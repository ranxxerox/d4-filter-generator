# Spec Delta

## Purpose

Makes the browser extension installable by someone who does not clone the repository, by publishing a packaged download that always matches the extension's reported version.

## ADDED Requirements

### Requirement: Packaged download

The repository SHALL publish a zip archive of the browser extension for every release, containing the extension's runtime files under a single top-level directory.

#### Scenario: Archive contents

- **WHEN** a release archive is downloaded and extracted
- **THEN** it contains one directory holding `manifest.json`, the popup files, the service worker, the content script, and the shared library scripts, and nothing else

#### Scenario: Load unpacked

- **WHEN** the extracted directory is selected with the browser's "Load unpacked" action
- **THEN** the browser accepts it as a valid extension without further edits

### Requirement: Stable download location

Each release SHALL attach the archive under an asset name that does not contain the version, and the newest release SHALL be reachable at a URL that stays valid across versions.

#### Scenario: Newest release URL

- **WHEN** a newer release is published
- **THEN** the previously documented download URL serves the newer archive without any document being edited

#### Scenario: Archive name

- **WHEN** a release is published
- **THEN** its attached archive keeps the same file name as the previous release

### Requirement: Version agreement

A release SHALL NOT publish an archive whose extension version differs from the release tag, and the check SHALL fail the release instead of publishing a mismatched build.

#### Scenario: Matching version

- **WHEN** the tag is `v1.0.0` and the extension manifest reports `1.0.0`
- **THEN** the release publishes the archive

#### Scenario: Mismatched version

- **WHEN** the tag and the extension manifest report different versions
- **THEN** the release fails and no archive is published

### Requirement: Release trigger

The release SHALL be published by pushing a version tag and SHALL also be startable by hand without a new commit.

#### Scenario: Tag push

- **WHEN** a maintainer pushes a tag matching the version pattern
- **THEN** the release workflow packages the extension and publishes the release

#### Scenario: Manual run

- **WHEN** a maintainer starts the release workflow from the Actions tab
- **THEN** the workflow publishes a release for the version the extension manifest reports

### Requirement: Release notes explain the download

Each release SHALL describe what the attached archive is, the browser versions it supports, and the steps to install it, without requiring the reader to open the repository.

#### Scenario: Reader arrives from the download link

- **WHEN** someone opens the release page
- **THEN** the notes state that the archive is the browser extension, name the supported browsers, and give the install steps

### Requirement: Install guidance points at the download

Every user-facing install instruction, including the guide page's extension-required panel, SHALL direct the reader to the downloadable release rather than to a source checkout.

#### Scenario: Guide page without the extension

- **WHEN** the guide page cannot reach the extension
- **THEN** the panel it shows links to the release download, not to the repository landing page

#### Scenario: Root README install section

- **WHEN** a reader follows the install section of the root README
- **THEN** they download an archive from the release, with no repository clone required
