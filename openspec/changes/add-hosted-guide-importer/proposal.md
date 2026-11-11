# Proposal

## Why

The fork's GitHub Pages site currently publishes only the manual affix picker. The CLI and the extension already turn a build guide into a filter, but neither runs from a web page. Anyone who wants the guide-driven flow has to install an extension or a Python environment first. Hosting the fork's own site with a guide importer gives those people a single link, and gives the fork one place to document all three tools.

## What Changes

- Add a hosted guide importer page to the Pages site. It reuses the generated `extension/lib/core.js` data and encoder, plus the existing parser, tier, and mapper modules, so no game data or encoder logic is copied.
- The importer reads a guide payload from the extension, shows the detected guide title, class, season, and variant, and renders an import code with copy and download controls. It keeps the variant selector and the gold core-stat threshold from the extension popup.
- Extend the MV3 extension with a background service worker and a content script that runs on the Pages origin, so the hosted page can ask for the active guide tab's payload. Add host permissions for maxroll.gg and mobalytics.gg so the extension can read those tabs without the popup being open.
- Show a clear message on the hosted page when the extension is missing, out of date, or has no guide tab available.
- Add navigation between the manual picker and the guide importer.
- Rewrite `README.md` around the three ways to produce a filter (hosted page, extension, CLI), including the publishing setup from `add-pages-publish-workflow` and how to import the code in game.

## Capabilities

### New Capabilities

- `hosted-guide-import`: the published page turns a guide into a filter import code, including guide summary, variant selection, gold threshold, and output controls.
- `extension-page-bridge`: the extension answers guide-payload requests from the published page and reports when it cannot.

### Modified Capabilities

None. The encoder, affix IDs, and CLI behavior do not change.

## Impact

- `guide.html` (new), plus small link changes in `index.html`
- `extension/manifest.json`, `extension/background.js` (new), `extension/content-pages.js` (new)
- `README.md`
- Tests: wiring checks for the new page and manifest; the existing extension parity tests stay the correctness gate for parsing and mapping
- GitHub Pages publishing through the workflow added by `add-pages-publish-workflow`
- No changes to `d4filter/`, the protobuf encoder, or the reverse-engineered ID tables
