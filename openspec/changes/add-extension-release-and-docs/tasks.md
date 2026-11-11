# Tasks

## 1. Release pipeline

- [x] 1.1 Add `.github/workflows/release.yml` with a `v*` tag trigger and `workflow_dispatch`, `permissions: contents: write`, and a checkout step; verify the file exists and `tests/test_release_workflow.py` asserts both triggers and the single write permission
- [x] 1.2 Add the version-agreement step that reads `version` from `extension/manifest.json` and fails when the pushed tag is not `v<version>`; verify by running the same shell comparison locally with a matching tag (`v0.3.0`) and a mismatching one (`v9.9.9`) and confirming the first succeeds and the second exits non-zero
- [x] 1.3 Add the packaging step that zips `extension/` to `d4-filter-generator-extension.zip` excluding markdown; verify locally with `zip -r /tmp/ext.zip extension -x 'extension/*.md'` and `unzip -l /tmp/ext.zip` showing the runtime files under one `extension/` directory and no `.md` entry
- [x] 1.4 Add the publication step using `gh release create` with the stable asset name, `--title`, `--notes-file .github/release-notes.md`, and `--prerelease` when the version contains a hyphen; verify `tests/test_release_workflow.py` asserts the asset name, notes file, and pre-release condition
- [ ] 1.5 Add `.github/release-notes.md` stating that the archive is the browser extension, naming Chrome and Edge, giving the extract-and-load steps, and linking to the README troubleshooting section; verify the notes test asserts each of those four sections
- [ ] 1.6 Bump `extension/manifest.json` to `1.0.0`; verify `python3 -c "import json; print(json.load(open('extension/manifest.json'))['version'])"` prints `1.0.0` and the existing suite still passes
- [ ] 1.7 Extend `tests/test_release_workflow.py` to assert that every path `extension/manifest.json` references exists in the folder, so a renamed script cannot produce a broken archive; verify the test passes and fails when a referenced file is temporarily renamed

## 2. Root README for end users

- [ ] 2.1 Rewrite `README.md` around a non-technical reader: what the tool does, the three ways to use it, the stable download link, and a pointer to `docs/README.md` for technical detail; verify `tests/test_docs.py` asserts the download URL, the technical-index link, and the absence of `pip install`, `python3 -m venv`, and `git clone` anywhere in the file
- [ ] 2.2 Add numbered extension install steps for Chrome and Edge that name `chrome://extensions` or `edge://extensions`, Developer mode, "Load unpacked", the folder to select, and what success looks like; verify the docs test asserts each label appears in the install section
- [ ] 2.3 Add the in-game import steps and a troubleshooting list covering missing extension, no guide tab, no payload, and a reload; verify the docs test asserts the troubleshooting entries exist and each names an action
- [ ] 2.4 Repoint the "Extension required" panel in `guide.html` at the stable release download URL; verify the docs test asserts the URL in `guide.html` equals the URL in `README.md`
- [ ] 2.5 Add `tests/test_docs.py` with the root README assertions from 2.1 to 2.4; verify `.venv/bin/python -m pytest tests/test_docs.py` passes

## 3. Component technical documents

- [ ] 3.1 Add `docs/README.md` indexing every component document with its audience and what it covers; verify the docs test asserts each index link resolves to an existing file
- [ ] 3.2 Add `extension/README.md` covering the manifest and permissions, the content-script-to-service-worker-to-page bridge and its message names, the popup flow and stored settings, the generated `lib/core.js`, and how a release is produced; verify the docs test asserts the manifest, bridge, popup, and release sections exist and that the document links to the README install section instead of restating it
- [ ] 3.3 Add `docs/web-tool.md` covering the shared data tables and their parity constraint, the protobuf encoder and colour packing, rule push order versus preview order and the visibility codes, the two pages and their different data sources, and the `tools/sync_extension_data.py` generation rule; verify the docs test asserts each topic heading exists
- [ ] 3.4 Add `tools/README.md` covering `sync_extension_data.py` and the staleness guard plus `golden_harness.js`; verify the docs test asserts both script names appear
- [ ] 3.5 Refresh `d4filter/README.md` so it stands alone: installation, every flag from the CLI help, the response cache, the alias file, and the mapper's variant and paragraph rules; verify `openspec`-independent check that `.venv/bin/d4filter --help` flags all appear in the document
- [ ] 3.6 Add `docs/testing.md` covering the pytest commands, the golden byte-for-byte harness, the saved guide fixtures and when to refresh them, and the workflow and docs guards; verify the docs test asserts the pytest command and fixture directory appear
- [ ] 3.7 Extend `tests/test_docs.py` with the component-document assertions from 3.1 to 3.6 and a check that no technical document repeats the browser install steps; verify the full file passes

## 4. Integration checks

- [ ] 4.1 Run `.venv/bin/python -m pytest` and confirm every test passes, including the pre-existing golden and parity guards
- [ ] 4.2 Build the archive locally, extract it to a temporary directory, and confirm the extracted folder contains `manifest.json` with version `1.0.0` and loads as an unpacked extension in a Chromium browser
- [ ] 4.3 Confirm the stable download URL appears identically in `README.md`, `.github/release-notes.md`, and `guide.html`, and that `tests/test_docs.py` fails if any one of them is changed alone

## Workflow follow-up

- Merge the change, then push the `v1.0.0` tag and watch the release run finish.
- Open the release page, download the archive, and confirm the notes and asset name match what the README documents.
- Confirm `releases/latest/download/d4-filter-generator-extension.zip` redirects to the new asset.
- Archive the change once the release is verified.
