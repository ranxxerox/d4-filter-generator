# Design

## Context

See `proposal.md` for motivation.

- The repository has no tags and no releases. `extension/manifest.json` reports version `0.3.0`; `pyproject.toml` reports `0.1.0` and is not part of this change.
- `.github/workflows/pages.yml` already establishes the workflow conventions this repository uses: official `actions/*` steps pinned by major, least-privilege `permissions`, a concurrency group, and a pytest guard in `tests/test_pages_workflow.py` that asserts the file's shape.
- The extension folder holds runtime files only today: `manifest.json`, `background.js`, `content-pages.js`, `popup.html`, `popup.js`, and `lib/*.js`. It has no README, so adding one changes what a naive "zip the folder" would ship.
- The manifest's content script matches `https://ranxxerox.github.io/d4-filter-generator/*`, so the published site and the extension are released from the same repository and must stay in step.
- `guide.html` shows an "Extension required" panel linking to the repository landing page. That is the in-page recovery path for a missing extension.
- Chrome and Edge refuse to install an extension archive from outside their stores on managed platforms; the supported path for a self-distributed extension is extract, then "Load unpacked" with developer mode on.

## Goals / Non-Goals

**Goals:**

- One documented URL that always downloads the newest extension, and a release page a non-technical reader can follow without opening the source tree.
- A release that cannot disagree with the version the browser reports.
- A root README a first-time user can follow with no terminal, and per-component technical documents a maintainer can rely on.

**Non-Goals:**

- No Chrome Web Store or Edge Add-ons submission. That needs a developer account, a review cycle, and a listing, and is a separate change. The release archive is the interim distribution channel.
- No `.crx` artifact. Browsers block side-loaded `.crx` files, so a zip plus "Load unpacked" is the only self-distributed path that works.
- No automated changelog generation, no release cadence policy, and no version bump automation.
- No change to encoder, parser, mapper, rule tiers, or saved fixtures.
- No relocation of existing files. The pages stay at the repository root so published URLs do not change.

## Decisions

### Publish a zip of `extension/` as the release asset

The release attaches a single archive containing the `extension/` directory. Alternatives: a `.crx` (browsers block side-loading it), a full repository zipball (the user then has to find the folder, and the archive is much larger), or nothing but a documented clone (today's state). A zip keeps the "Load unpacked" flow intact and is small.

### One stable asset name, version in the tag

The asset is always named `d4-filter-generator-extension.zip`. GitHub's `releases/latest/download/<asset>` redirect then yields a permanent URL that serves the newest build:

`https://github.com/ranxxerox/d4-filter-generator/releases/latest/download/d4-filter-generator-extension.zip`

Alternatives: embed the version in the asset name (every document's link breaks each release), or link to `releases/latest` and make the reader pick the asset (one more decision for a non-technical user). The unversioned name costs the ability to tell archives apart once downloaded; the version is still visible in the release title and inside `manifest.json`.

### Archive everything in `extension/` except markdown

The packaging step zips `extension/` and excludes `*.md`. Including everything else means a newly added runtime file ships without editing the workflow, which is the failure mode that matters: an archive missing a script breaks the extension silently. Markdown is the only category of file the folder will hold that is not runtime. Alternatives: an explicit file list (misses new files), or zipping the folder with nothing excluded (ships the extension README to end users, harmless but noisy). A test asserts every path `manifest.json` references exists in the folder, so a rename cannot produce a broken archive.

### Tag push, plus manual dispatch

The workflow triggers on tags matching `v*` and on `workflow_dispatch`. Tag push is the normal path and ties the artifact to an immutable commit. Manual dispatch lets a maintainer re-publish after a failed run or publish from an existing commit without creating a second tag by hand.

### The tag must equal the manifest version

Before packaging, the workflow reads `version` from `extension/manifest.json` and compares `v$version` with the pushed tag. A mismatch fails the job before anything is uploaded. Alternatives: trust the tag (a release can then advertise a version the browser does not report, which breaks every "update the extension" instruction), or generate the tag from the manifest (a workflow cannot create the tag that triggered it, so this only works for dispatch). On manual dispatch there is no tag to compare, so the workflow creates `v$version` from the checked-out commit.

### `gh` CLI instead of a third-party release action

The workflow uses `gh release create` with the runner's token, the same way `tests/test_pages_workflow.py` guards a checked-in workflow. Alternatives: `softprops/action-gh-release` (widely used, but adds a third-party action and its own release semantics), or the REST API through `actions/github-script` (more code for the same result). `gh` is preinstalled on GitHub runners and needs no extra dependency.

### Notes come from a checked-in template

The release body is a checked-in `.github/release-notes.md` with the version substituted, passed through `--notes-file`. It states what the archive is, the supported browsers, the install steps, and where to get help. Alternatives: `--generate-notes` (lists commits, which means nothing to an end user, and cannot carry install steps), or no notes (the release page then repeats the gap this change exists to close). Generated notes are deliberately dropped rather than concatenated, so the body stays deterministic and a test can assert its sections.

### Hyphenated versions publish as pre-releases

If the manifest version contains a hyphen (for example `1.1.0-beta.1`), the release is created with `--prerelease`. GitHub's `releases/latest` skips pre-releases, so a beta never becomes the documented download. One conditional, and it protects the stable URL from a mistake.

### Bump the extension to `1.0.0`

This is the first release anyone can download. `1.0.0` signals a supported build rather than a development snapshot, and it gives the tag something meaningful to match. The version stays in `extension/manifest.json` as the single source; `pyproject.toml` keeps its own version because the CLI has an independent release story.

### The root README becomes the only install guide

The root README keeps the download link, the numbered install steps, the in-game import steps, and a troubleshooting list. Every other document links to its install section by anchor instead of restating the browser steps. Alternatives: keep install steps in the extension README and have the root README link down (a new user lands on the technical document first), or duplicate the steps (two places to drift). A test asserts the technical documents do not contain the browser step text.

### Technical documents sit next to their component, with one index

`extension/README.md`, `tools/README.md`, and the existing `d4filter/README.md` live beside their code. The two pages at the repository root have no folder of their own, so their document is `docs/web-tool.md`, and the suite gets `docs/testing.md`. `docs/README.md` indexes all of them with the audience for each. Alternatives: everything under `docs/` (separates a component's document from the component) or no index (a maintainer has to guess which document covers the encoder).

## Risks / Trade-offs

| Risk | Mitigation |
| --- | --- |
| A non-technical reader still cannot install, because browsers require developer mode for unpacked extensions | The steps name every label and screen, state what success looks like, and the troubleshooting list covers the common failures. Store distribution is the follow-up change that removes developer mode entirely. |
| A new runtime file is added to `extension/` but the archive is built from a stale list | The archive includes every file in the folder except markdown, and a test checks that every manifest-referenced path exists. |
| The tag and the manifest disagree | The workflow fails before uploading; nothing is published. |
| Re-running a release for an existing tag fails because the release exists | Accepted. Silently overwriting a published release is worse; the maintainer deletes the release or publishes a new version. |
| `releases/latest` hides pre-releases, so a beta is not the download | Intended. Stable versions must not be pre-release tagged, which the workflow derives from the version string rather than a manual choice. |
| The extension README ends up inside the archive | The packaging step excludes markdown, and the release test asserts the exclusion. |
| Documentation drifts from the code | Tests assert the root README's required sections, the stable download URL, the absence of terminal commands in user sections, and that every index link resolves. |
| Publishing the release needs a write token | The job requests `contents: write` only, which the repository's default token already grants. |
| A fork with a different repository name gets a wrong download URL in the docs | The URL appears in the README, the notes template, and `guide.html`; the release test asserts they agree, so one edit cannot leave a stale link behind. |

## Migration Plan

1. Add the workflow, notes template, tests, and documents; bump `extension/manifest.json` to `1.0.0`; repoint `guide.html`.
2. Merge to `main`. The pages workflow republishes the site, and the new install panel link goes live.
3. Tag the release commit: `git tag v1.0.0 && git push origin v1.0.0`.
4. Watch the release run, then open the release page and download the archive to confirm it extracts and loads unpacked.
5. Confirm the stable URL redirects to the new asset.

Rollback: delete the release and the tag with `gh release delete v1.0.0 --yes --cleanup-tag`, or revert the commit. The published site keeps serving the previous content, and no installed extension breaks because the archive is additive.

## Verification

- `tests/test_release_workflow.py` checks the triggers, permissions, version comparison, packaging exclusions, asset name, notes file, and pre-release condition.
- `tests/test_docs.py` checks the root README's required sections, the stable download URL appearing identically in the README, notes template, and guide page, the absence of clone or pip steps in user sections, the existence of every component document, and that each index link resolves.
- `.venv/bin/python -m pytest` passes.
- A pushed `v1.0.0` tag produces a release whose archive extracts to a loadable extension.
- `curl -sI https://github.com/ranxxerox/d4-filter-generator/releases/latest/download/d4-filter-generator-extension.zip` returns a redirect to the release asset.
