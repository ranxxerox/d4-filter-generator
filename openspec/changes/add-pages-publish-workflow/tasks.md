# Tasks

## 1. Workflow and its guard

- [x] 1.1 Add `.github/workflows/pages.yml` with the starter flow, `branches: [main]`, the three token permissions, the `pages` concurrency group, and `upload-pages-artifact@v5` at `path: '.'`; verify `ruby -ryaml -e 'YAML.load_file(".github/workflows/pages.yml")'` exits 0.
- [x] 1.2 Add `tests/test_pages_workflow.py` covering the trigger, permissions, concurrency, step order, root path, and environment URL; verify the test fails when `branches: [main]` is changed to `[dev]`.

## 2. README

- [x] 2.1 Add a Publishing section with the automatic behavior, manual run, one-time Pages source step, fork URL, and Actions requirement; run the humanizer pass on the prose, then verify the settings path and URL match the workflow and the repository.
- [ ] 2.2 Point the Live tool line at the fork's Pages URL; verify the URL resolves after the first deploy.

## 3. Repository setup

- [x] 3.1 Set the Pages source to GitHub Actions, through settings or `gh api`; verify `gh api repos/ranxxerox/d4-filter-generator/pages --jq .build_type` returns `workflow`.
- [ ] 3.2 After the workflow reaches `main`, watch a run and verify the deployment URL serves `index.html` and `extension/lib/core.js`.

## 4. Plan coherence

- [x] 4.1 Update `add-hosted-guide-importer`'s design and tasks to reference this workflow instead of branch publishing; verify `openspec validate add-hosted-guide-importer --strict` still passes.

## 5. Integration

- [x] 5.1 Run `.venv/bin/python -m pytest` and confirm the new workflow guard and the existing golden and extension tests pass.

## Workflow follow-up

- Commit and push the workflow to `main` when the user asks.
- Archive the change after the project's review requirements are satisfied.
