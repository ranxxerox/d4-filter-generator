# Extension

The MV3 extension that lets the published guide importer read a maxroll.gg or mobalytics.gg guide tab. Install steps live in the root README only: [Install in Chrome](../README.md#install-in-chrome) and [Install in Edge](../README.md#install-in-edge). This document is for maintainers.

## Manifest and permissions

`manifest.json` is the only place the published origin appears. The content script matches `https://ranxxerox.github.io/d4-filter-generator/*`, and `background.js` reads that prefix back from the manifest, so moving the site means editing one line and no other file.

- `activeTab` and `scripting`: inject `lib/guide-tab.js` into the guide tab and run the extractor in the page's MAIN world.
- `storage`: remember the gold threshold, the preferred variant, and stat aliases in `chrome.storage.sync`.
- `host_permissions` for `maxroll.gg` and `mobalytics.gg`: find guide tabs and inject the extractor into them.

`manifest_version` is 3, the service worker is `background.js`, and the action popup is `popup.html`. The manifest version is the single source of truth for releases.

## The page bridge

The importer page cannot fetch either guide site itself, so it asks the extension through the page's message channel:

1. `content-pages.js` runs at `document_start` on the published site and sets `document.documentElement.dataset.d4filterExtension` to the manifest version. The page reads that attribute to detect the extension.
2. The page posts `{ source: "d4filter-page", type: "read-guide" }` to its own window.
3. The content script accepts the message only when the origin, `event.source`, channel, and type all match, then sends `{ type: "d4filter:read-guide" }` with `chrome.runtime.sendMessage`.
4. `background.js` answers only senders whose URL starts with the manifest's content-script prefix. It picks the active guide tab when there is one, otherwise the most recently accessed guide tab, injects `lib/guide-tab.js`, and calls `D4.guideTab.extract()` in the MAIN world.
5. The content script posts the answer back as `{ source: "d4filter-extension", type: "guide", ok, payload, error }`.

Message names: page channels `d4filter-page` and `d4filter-extension`, page request `read-guide`, page reply `guide`, worker request `d4filter:read-guide`, DOM marker `d4filterExtension`.

`extract()` returns `{ remix, preloaded, seen, href }`. `remix` is maxroll's `window.__remixContext`, `preloaded` is mobalytics' `window.__PRELOADED_STATE__`, and `seen` records which globals existed so the "no payload" error can say what the page actually held.

## Popup flow

`popup.js` reads the active tab directly, without the service worker:

1. `chrome.scripting.executeScript` injects `lib/guide-tab.js` into the active tab's MAIN world and calls `extract()`.
2. `lib/guide-spec.js` parses the payload into a guide spec.
3. `lib/mapper.js` maps the spec onto the verified data and `lib/tiers.js` generates the code.
4. The popup renders the title, class, season, matched core stats, secondary stats, and skills, then shows the code with a Copy Code button.

Stored settings are `gold` (core stats required by the gold tier), `variant` (the last chosen planner profile), and `aliases` (stat-name overrides). The variant selector starts on `Endgame` when the guide has one, otherwise it merges every profile. Changes to the gold threshold and the variant regenerate the code immediately.

## Generated core

`lib/core.js` is generated from `index.html` by `tools/sync_extension_data.py`. It holds the `DB` and `SKILLS` tables, the protobuf encoder, the condition builders, and the colour constants. Do not edit it by hand: rerun the script after any encoder or data change. `tests/test_extension.py` hashes the source region and fails when the generated file is stale.

The other `lib/` modules are IIFE-wrapped because they load as classic scripts and share one global `D4` namespace. `popup.html` loads them in dependency order: `core`, `tiers`, `guide-spec`, `mapper`, `guide-tab`, then `popup.js`.

## Producing a release

`.github/workflows/release.yml` runs on a `v*` tag or by hand. It reads `version` from `manifest.json`, fails when the pushed tag is not `v<version>`, zips `extension/` excluding markdown to `d4-filter-generator-extension.zip`, and publishes it with `gh release create` using `.github/release-notes.md`. Versions containing a hyphen publish as pre-releases, so `releases/latest` keeps pointing at a stable build.

To cut a release: bump `version` in `manifest.json`, commit, tag that commit `v<version>`, and push the tag. The asset name never changes, so the download link in the root README stays valid across versions.
