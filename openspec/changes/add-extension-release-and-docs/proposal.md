# Proposal

## Why

The guide importer only works with the browser extension installed, but the only install path is cloning the repository, enabling Chrome developer mode, and loading the folder unpacked. That is a developer workflow, and the README that explains it is written for people who already know the codebase. Someone who just wants a filter code has no obvious download and no plain-language instructions.

The repository also has no release at all: no tags, no packaged artifact, and no stable download URL. Every install instruction therefore depends on the reader being able to clone a git repository.

## What Changes

- Add a release workflow that packages the extension into a zip and attaches it to a GitHub Release whenever a `v*` tag is pushed, or when a maintainer runs it by hand.
- Publish the zip under a version-independent asset name so one stable URL always points at the newest extension build, and make the release notes say what the download is and how to install it.
- Validate that the tag matches `extension/manifest.json` so a release can never ship a version the extension does not report.
- Bump the extension to `1.0.0` for the first public downloadable release.
- Rewrite the root `README.md` for a non-technical reader: what the tool does, a single download link, numbered install steps for Chrome and Edge, how to import a code in game, and troubleshooting. Terminal commands and format internals move out of it.
- Add per-component technical documentation: an extension README, a tools README, a web-tool page document, a testing document, and a technical index under `docs/`. Refresh `d4filter/README.md` so it stands alone.
- Point the guide page's "Extension required" panel at the download instead of the repository, so the in-page recovery path matches the README.
- Add tests that guard the release workflow and the documentation set so both stay in the shape the specs require.

## Capabilities

### New Capabilities

- `extension-distribution`: the extension is packaged, versioned, and published as a downloadable artifact with a stable URL, and the release can never disagree with the manifest.
- `project-documentation`: the repository separates plain-language user documentation from per-component technical documentation, and each document has a defined audience and required content.

### Modified Capabilities

None. The project has no main specs yet.

## Impact

- `.github/workflows/release.yml` (new)
- `tests/test_release_workflow.py` (new)
- `tests/test_docs.py` (new)
- `README.md` (rewritten for end users)
- `extension/README.md` (new)
- `extension/manifest.json` (version bump)
- `tools/README.md` (new)
- `docs/README.md`, `docs/web-tool.md`, `docs/testing.md` (new)
- `d4filter/README.md` (refreshed)
- `guide.html` (install panel link)
- No encoder, parser, mapper, or rule-tier behavior changes; no test fixtures change.
- Release publishing needs `contents: write` on the repository token, which the default workflow token already has.
