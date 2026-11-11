# Design

## Context

See `proposal.md` for motivation.

- The repository has no `.github` directory today.
- Upstream publishes from `main` at the repository root through a Pages setting. The hosted guide importer change planned the same branch-root setup.
- GitHub's official static Pages starter (`actions/starter-workflows/pages/static.yml`) defines the flow: `checkout@v4`, `configure-pages@v5`, `upload-pages-artifact@v3`, `deploy-pages@v5`, with `contents: read`, `pages: write`, `id-token: write`, and a `pages` concurrency group.
- `upload-pages-artifact@v3` excludes only `.git` and `.github`. It has no hidden-file exclusion. `v5` excludes hidden files by default.
- Actions-based Pages requires the repository source to be set to GitHub Actions. `configure-pages` can enable Pages only with a token other than `GITHUB_TOKEN`.

## Goals / Non-Goals

**Goals:**

- Publish `main` automatically with a checked-in, reviewable workflow.
- Keep token permissions minimal and deployments serialized.
- Keep published paths identical to local paths so `index.html` and `extension/lib/*.js` resolve without rewriting links.

**Non-Goals:**

- No test gate in the workflow, no custom domain, and no minimal `_site` staging.
- No change to site content, the encoder, the CLI, or the extension.

## Decisions

### Adopt the official starter workflow

The checked-in `pages.yml` follows `actions/starter-workflows/pages/static.yml`. Alternatives considered: `peaceiris/actions-gh-pages` pushing a `gh-pages` branch (needs a token and a second branch) and branch publishing in repository settings (invisible in the repo, and the step the fork wants to replace). The official actions use OIDC, need no personal access token, and keep the deployment visible in the run.

### Trigger on `main` literally

The starter writes `branches: [$default-branch]`, a token the GitHub UI replaces. In a checked-in file it stays literal, so the workflow names `main`. If the fork's default branch changes, the branch list changes with it.

### Upload the repository root

`path: '.'` keeps `index.html` at the site root and `extension/lib/*.js` at the same relative paths used locally. New assets publish without editing the workflow. Alternative: stage a `_site` directory with an explicit copy list. That hides internal docs and test fixtures, but adds a list to maintain and fails when a planned page is not present yet. Root publishing matches upstream and the earlier design.

### Bump `upload-pages-artifact` to v5

The starter pins v3, which includes hidden files. The repository tracks `.crush/`, so v3 would publish agent configuration. v5 excludes hidden files by default. The other actions stay at the starter's majors: `checkout@v4`, `configure-pages@v5`, `deploy-pages@v5`.

### Deploy only, no test job

The workflow runs the deploy job alone, as the starter does. Tests stay a pre-merge step. Alternative: a pytest job before deploy. That gates publishing but adds setup time and a second failure surface. It can be added later without changing the specs.

### Serialized deployments with minimal permissions

One `pages` concurrency group with `cancel-in-progress: false`, so a production deploy finishes and a queued run waits. Permissions are the three the Pages actions need. No `contents: write`.

### Pages source is a one-time setting

The workflow cannot switch the source with `GITHUB_TOKEN`; the `enablement` input on `configure-pages` needs a personal access token. The README documents Settings, Pages, Source: GitHub Actions. Until that is set, `configure-pages` fails and the previous site stays live.

### Supersede the branch publishing steps

`add-hosted-guide-importer` planned Settings, Pages, Deploy from a branch. When both changes land, the README describes Actions publishing only. This change updates that change's design and tasks so the two plans agree.

## Risks / Trade-offs

| Risk | Mitigation |
| --- | --- |
| Pages source is still a branch | `configure-pages` fails, the run fails, and the old site stays live. The README gives the one-time step, and the Pages API reports the build type. |
| Actions are disabled on the fork | The workflow never runs. The README says to enable Actions. |
| Publishing the repository root exposes internal docs, tests, and planning artifacts | Accepted for now. Staging a `_site` directory is a later option. |
| A broken `main` deploys | Tests stay a pre-merge gate. A test job can be added later. |
| Action majors age | Majors are pinned. Bumping them is a separate change. |
| The fork's default branch is not `main` | The trigger names `main`; update the branch list if that changes. |

## Migration Plan

1. Add the workflow, its test, and the README section.
2. Commit and push to `main`.
3. Set Settings, Pages, Source: GitHub Actions.
4. Watch the run and confirm the published URL.

Rollback: disable the workflow and set Pages back to the branch source, or revert the commit. The last deployed artifact stays live.

## Verification

- `tests/test_pages_workflow.py` checks the trigger, permissions, concurrency, step order, root path, and environment URL.
- The full pytest suite passes.
- `gh api repos/ranxxerox/d4-filter-generator/pages --jq .build_type` returns `workflow`.
- The published URL serves `index.html` and `extension/lib/core.js`.
