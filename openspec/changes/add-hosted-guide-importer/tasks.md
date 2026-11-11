# Tasks

## 1. Shared guide-source extraction

- [x] 1.1 Add `extension/lib/guide-tab.js` exposing `globalThis.D4.guideTab.extract()` (plus a CommonJS export) that returns `{ remix, preloaded, href, seen }` from the page globals; verify with `node -e "require('./extension/lib/guide-tab.js')"` that the function loads and is callable with stubbed globals.
- [x] 1.2 Load `guide-tab.js` in `extension/popup.html` and replace the inline extraction function in `popup.js` with the shared helper; verify `.venv/bin/python -m pytest tests/test_extension.py` passes and the popup still generates a code from a live guide tab.

## 2. Extension bridge

- [x] 2.1 Update `extension/manifest.json` with the background service worker, host permissions for maxroll.gg and mobalytics.gg, and a content script matching the published origin; verify with a new `tests/test_pages_bridge.py` that asserts each entry and keeps the existing permissions.
- [x] 2.2 Add `extension/background.js` that handles `d4filter:read-guide`, selects the active or most recently used guide tab, and runs the shared extractor in the `MAIN` world; verify by loading the unpacked extension and generating from the hosted page with the popup closed.
- [x] 2.3 Add `extension/content-pages.js` that sets the version marker on the document, relays `window.postMessage` requests to the worker, and ignores other origins and sources; verify the marker appears in the page DOM and a request returns a payload.
- [x] 2.4 Extract the content script's message check into a pure helper and cover it in `tests/test_pages_bridge.py` with allowed and rejected origin/source cases; verify the new test fails when the origin check is removed.

## 3. Hosted guide page

- [x] 3.1 Create `guide.html` at the repo root with `core.js`, `guide-spec.js`, `tiers.js`, and `mapper.js` script tags in that order and an IIFE UI script; verify a `tests/test_pages_bridge.py` case asserts the order and that the page contains no copied affix table.
- [x] 3.2 Implement extension detection with a short wait, the read request, and the three failure messages (not installed, no guide tab, page needs a reload); verify each path by hand with the extension installed, disabled, and with no guide tab open.
- [x] 3.3 Render the guide summary, variant selector defaulting to Endgame, gold threshold, matched core/secondary/skills, unmatched lines, and the code with copy and download controls; verify by generating from a live maxroll guide and comparing the code to the popup's output for the same variant.
- [x] 3.4 Add a parity case that feeds the parsers a payload object instead of raw HTML, the way the hosted page does; verify the generated code matches the existing HTML-based case for the same fixture.

## 4. Site navigation

- [x] 4.1 Add links between `index.html` and `guide.html` and point the footer at the fork; verify both pages open from `file://` and each link reaches the other page.

## 5. README

- [x] 5.1 Rewrite `README.md` around the hosted page, the extension, and the CLI, with the in-game import steps, the publishing section from `add-pages-publish-workflow`, contributing notes, technical notes, and upstream credit; run the humanizer pass on the prose, then verify every command runs as written and every URL resolves.
- [x] 5.2 Note the Chrome/Edge requirement and the one manifest line to change if the published origin moves; verify the path and origin match the files on disk.

## 6. Integration

- [x] 6.1 Run the full suite with `.venv/bin/python -m pytest` and confirm the golden and extension parity tests pass.
- [ ] 6.2 Generate from one maxroll guide and one mobalytics guide on the hosted page and confirm each code matches the popup and the CLI for the same variant.
- [x] 6.3 Confirm the Pages publish workflow from `add-pages-publish-workflow` is enabled and the published URL serves `guide.html`, `index.html`, and `extension/lib/core.js`.

## Workflow follow-up

- Archive the change after the project's review requirements are satisfied.
- Verify the archived specs and tasks.
