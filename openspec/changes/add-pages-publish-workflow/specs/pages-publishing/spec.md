# Spec Delta

## Purpose

Publishes the repository's static site to GitHub Pages automatically whenever `main` changes, using GitHub's official Pages deployment actions.

## ADDED Requirements

### Requirement: Deploy on main

The repository SHALL deploy the current `main` branch to GitHub Pages whenever a commit lands on `main`, and SHALL allow the same deployment to be started by hand.

#### Scenario: Push to main

- **WHEN** a commit is pushed to `main`
- **THEN** a workflow run uploads the current `main` and deploys it to Pages

#### Scenario: Manual run

- **WHEN** a maintainer starts the workflow from the Actions tab
- **THEN** the run deploys the current `main`

### Requirement: Least-privilege token

The workflow SHALL request only `contents: read`, `pages: write`, and `id-token: write`.

#### Scenario: Token scopes

- **WHEN** the workflow runs
- **THEN** the job token has read access to the repository and write access to Pages, and no other write scope

### Requirement: One deployment at a time

The workflow SHALL use a single concurrency group for Pages and SHALL NOT cancel a deployment that is already running.

#### Scenario: Queued run

- **WHEN** a second run starts while a deployment is in progress
- **THEN** the second run waits, and the running deployment finishes instead of being cancelled

### Requirement: Published paths

The deployment SHALL publish the repository root so the site root serves `index.html` and the guide page and shared library scripts keep the same relative paths they have locally.

#### Scenario: Site root

- **WHEN** a deployment completes
- **THEN** the published site root serves `index.html`

#### Scenario: Shared assets

- **WHEN** the guide page requests a script from `extension/lib/`
- **THEN** the published site returns that script at the same path

### Requirement: Failed runs keep the live site

A run that fails before the deploy step SHALL leave the last successful deployment serving traffic.

#### Scenario: Failure before deploy

- **WHEN** checkout, configuration, or upload fails
- **THEN** the previously published site stays live

### Requirement: Deployment visibility

The deploy job SHALL expose the published URL through a `github-pages` environment.

#### Scenario: Run summary

- **WHEN** a deployment succeeds
- **THEN** the run shows the published URL for the `github-pages` environment

### Requirement: Pages source is Actions

The repository SHALL publish through GitHub Actions rather than a branch.

#### Scenario: Repository setting

- **WHEN** the repository's Pages configuration is read
- **THEN** its build type is the workflow build type, not a branch source
