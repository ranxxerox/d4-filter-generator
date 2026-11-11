# Proposal

## Why

The fork's site is meant to publish from the `main` branch through a manual Pages setting. That setting lives outside the repository, can drift, and the publishing steps planned for the hosted guide importer assume branch publishing. A checked-in workflow makes every push to `main` publish automatically, keeps the configuration reviewable, and matches GitHub's current recommendation for Pages.

## What Changes

- Add `.github/workflows/pages.yml` from GitHub's official static Pages starter workflow: push to `main` and manual dispatch, least-privilege token permissions, one deployment at a time, then checkout, configure Pages, upload the repository root, and deploy.
- Switch the repository's Pages source from a branch to GitHub Actions. This is a one-time repository setting.
- Document the publishing behavior and the one-time setting in `README.md`.
- Supersede the branch-root publishing steps planned in `add-hosted-guide-importer`. When both changes land, the README describes Actions publishing only.

## Capabilities

### New Capabilities

- `pages-publishing`: the repository's static site publishes to GitHub Pages automatically when `main` changes, with a deployment that is safe to run repeatedly and leaves the last good site live on failure.

### Modified Capabilities

None.

## Impact

- `.github/workflows/pages.yml` (new)
- `README.md`
- GitHub repository Pages settings (source changes to GitHub Actions)
- No application code, encoder, CLI, extension, or test fixture changes
