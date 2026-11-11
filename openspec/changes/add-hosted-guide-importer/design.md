# Design

## Context

See `proposal.md` for motivation.

- `index.html` is self-contained. Its single inline script declares `DB`, `SKILLS`, `state`, and the protobuf encoder as top-level `const` bindings, and inline HTML attributes call the UI functions directly.
- `tools/golden_harness.js` extracts the first exact `<script>` block from `index.html` and appends code that references `buildFilter`, `DB`, `SKILLS`, and `state`. Those golden tests are the main correctness gate for the encoder.
- `tools/sync_extension_data.py` generates `extension/lib/core.js` from that same script block, and a pytest staleness guard fails when the two drift.
- `extension/lib/guide-spec.js`, `tiers.js`, and `mapper.js` are IIFE classic scripts. They attach to `globalThis.D4` and read `globalThis.D4.core` at load time.
- The extension is MV3 with a popup only. It uses `chrome.scripting.executeScript` in the `MAIN` world under the `activeTab` grant, so it works only while the popup is open.
- The published site is static. `maxroll.gg` sends no `Access-Control-Allow-Origin` header, and `mobalytics.gg` returns 403 without browser-like headers, so a `*.github.io` page cannot fetch either guide URL.

## Goals / Non-Goals

**Goals:**

- One hosted page that turns a guide into an import code, using the tested parser, mapper, tier builder, and encoder without copying them.
- Extension support for reading a guide tab while its popup is closed.
- A README that covers the hosted page, the extension, and the CLI.

**Non-Goals:**

- No server, proxy, or build step. The site stays static.
- No new affix or skill IDs.
- No change to the encoder, rule tiers, or CLI behavior.
- No paste-the-page-source fallback in this change.

## Decisions

### A separate `guide.html` instead of extending `index.html`

`index.html`'s inline script cannot also load `extension/lib/core.js`: both declare `DB`, `SKILLS`, and `state` as top-level `const`, and classic scripts share one global lexical scope, so the second declaration throws. Wrapping the inline script in an IIFE would fix the collision but break the golden harness, which appends `globalThis.__exports = { buildFilter, DB, SKILLS, state }` to the extracted script and relies on those bindings being in scope. Splitting the data tables out of `index.html` would move the golden source itself.

A separate page at the repo root loads `extension/lib/core.js`, `guide-spec.js`, `tiers.js`, and `mapper.js` with relative script tags. The whole repo root is published, so the same paths work from `file://` and from Pages. `guide.html` keeps its own script inside an IIFE and touches no globals.

Alternatives considered: inlining copies of the parser and mapper into `index.html` (duplicates code that the parity tests already guard), and making `core.js` the source of truth (large refactor of the golden source, unrelated to this change).

### Content-script bridge instead of `externally_connectable`

A page can call `chrome.runtime.sendMessage(extensionId, message)` only if the extension lists the page origin in `externally_connectable`, and the page must know the extension ID. Unpacked extension IDs vary by install, and Firefox does not support `externally_connectable`.

A content script that matches the published origin avoids both problems. It marks the page (`document.documentElement.dataset.d4filterExtension = version`), listens for `window.postMessage` requests, relays them to the service worker, and posts the reply back. The page never needs the extension ID, and detection is a DOM read.

Trade-off: the manifest carries a match pattern for the published origin. If the site moves to a custom domain or a different repository name, that one pattern changes. The README says so.

### Background service worker owns tab selection and extraction

Content scripts cannot query or script other tabs. A new `background.js` service worker handles `d4filter:read-guide` messages, picks a tab, and runs the same extraction function the popup uses:

- Prefer the active tab in the last focused window when its URL is on maxroll.gg or mobalytics.gg.
- Otherwise take the most recently accessed matching tab (`lastAccessed` when present, else the first result).
- Return `{ remix, preloaded, href, seen }`, matching the popup's shape.

`host_permissions` for `https://maxroll.gg/*` and `https://mobalytics.gg/*` let `chrome.scripting.executeScript` run in those tabs without an `activeTab` grant. The popup keeps its current flow; the extraction function moves to a shared helper or is duplicated verbatim so both paths return the same object.

### Message protocol

| Direction | Shape |
| --- | --- |
| Page to content script | `window.postMessage({ source: "d4filter-page", type: "read-guide" }, location.origin)` |
| Content script to worker | `chrome.runtime.sendMessage({ type: "d4filter:read-guide" })` |
| Content script to page | `window.postMessage({ source: "d4filter-extension", type: "guide", ok, source, error }, location.origin)` |

The content script ignores messages whose `event.source` is not `window` or whose origin is not the page origin. The page ignores replies that do not carry the `d4filter-extension` source. No `externally_connectable` entry is needed because the page never talks to the extension directly.

### Guide page behavior

- Parse with `parseMaxroll(payload, href)` or `parseMobalytics(payload, href)`. Both already accept an object or raw HTML.
- Generate with `generateFromSpec(spec, {}, goldN, variant)`. Aliases are empty because the page has no persistence; unmatched lines are shown instead.
- Variant options match the popup: merge-all plus each profile, defaulting to the profile named Endgame when present, otherwise merge-all.
- Gold threshold defaults to 2 and is not persisted.
- The page waits briefly for the extension marker before showing the install message, so a slow content script does not produce a false negative.
- The page loads `core.js` before `tiers.js` and `mapper.js`, since those read `globalThis.D4.core` at load time.

### Publishing

GitHub Pages deploys the fork from `main` at the repository root. That keeps `guide.html` and `extension/lib/*` at paths that work locally and online. The deploy itself comes from the `add-pages-publish-workflow` change, which adds a GitHub Actions workflow and sets the Pages source to Actions. This change adds no deployment configuration of its own.

See `add-pages-publish-workflow` for the workflow triggers, permissions, and the one-time Pages setting.

## Risks / Trade-offs

| Risk | Mitigation |
| --- | --- |
| Guide payloads can be several MB, and the page relays them through two message hops | Read once per generate, keep no copy in storage, and show a busy state while reading. The popup already returns the same payload from `executeScript`. |
| The content-script match pattern is tied to `https://ranxxerox.github.io/d4-filter-generator/*` | Document the one manifest line to change if the site moves. The manual picker and popup keep working regardless. |
| Users with an older unpacked extension build see the install message | The marker includes the manifest version; the message tells them to reload the extension. |
| `lastAccessed` may be unavailable without the `tabs` permission | Host permissions expose the URL for matching tabs; if `lastAccessed` is missing, fall back to the first matching tab. |
| No extension means no guide import at all | The page explains the requirement and links to the extension install steps. A paste fallback can be added later without changing the specs. |
| Publishing the repo root exposes `tests/`, `docs/`, and `openspec/` | Already true upstream; the repository holds no secrets. |
| Firefox and Safari cannot use the bridge | The README states Chrome and Edge. The page still serves the manual tool everywhere. |

## Migration Plan

1. Merge to `main`. The Pages workflow from `add-pages-publish-workflow` deploys the repository root.
2. Confirm the Pages source is set to GitHub Actions, as that change documents.
3. Reload the unpacked extension so the new manifest, worker, and content script load.
4. Open a maxroll or mobalytics guide tab, open the hosted guide page, and confirm the code matches the popup's output for the same guide and variant.

Rollback is a revert commit. Pages serves the previous build after it redeploys, and the extension returns to the popup-only flow after a reload.

## Verification

- Existing pytest suite, including the extension parity and golden encoder tests.
- New wiring tests: `guide.html` loads the four lib scripts in order and contains no copied affix tables; the manifest declares the worker, host permissions, and the published-origin content script.
- Manual check of the three failure paths: extension missing, no guide tab, and guide page needing a reload.
