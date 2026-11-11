# Spec Delta

## Purpose

Keeps the front page readable by someone who only wants a filter code, while giving each part of the repository its own place to document how it works.

## ADDED Requirements

### Requirement: Root README serves end users

The root `README.md` SHALL explain the product in plain language and SHALL NOT require a terminal to follow its main paths.

#### Scenario: Reader with no development background

- **WHEN** someone reads the root README top to bottom
- **THEN** they learn what the tool does, how to get the extension, how to use the live site, and how to import a code in game

#### Scenario: No install prerequisites

- **WHEN** the root README's extension and live-site sections are read
- **THEN** they contain no package installation, virtual environment, or git commands

#### Scenario: Entry to technical detail

- **WHEN** a reader wants implementation detail
- **THEN** the root README links to the technical documentation index instead of containing the detail itself

### Requirement: Install steps are written for non-technical readers

The root README SHALL give numbered install steps for the extension that assume no prior knowledge of browser extension development.

#### Scenario: Install section

- **WHEN** a reader follows the install steps
- **THEN** every step names the exact screen, button, or menu label to use, and states what a successful result looks like

#### Scenario: Unpacking the download

- **WHEN** the reader has downloaded the archive
- **THEN** the instructions say where to extract it and which folder to select in the browser

#### Scenario: Troubleshooting

- **WHEN** the extension appears to be missing or the guide page cannot read a tab
- **THEN** the README lists the common causes and the action for each

### Requirement: Per-component technical documentation

Each sub-component of the repository SHALL have its own document describing its structure, responsibilities, and the constraints a maintainer must preserve.

#### Scenario: Component coverage

- **WHEN** the technical documentation is listed
- **THEN** the browser extension, the web pages, the Python CLI, the tooling scripts, and the test suite each have a document

#### Scenario: Extension document

- **WHEN** the extension document is read
- **THEN** it covers the manifest, permissions, the page bridge message protocol, the popup flow, and how a release is produced

#### Scenario: Web tool document

- **WHEN** the web pages document is read
- **THEN** it covers the shared data tables, the protobuf encoder, rule ordering and visibility codes, and the generated `extension/lib/core.js`

#### Scenario: CLI document

- **WHEN** the CLI document is read
- **THEN** it covers installation, every flag, the response cache, and the alias file

#### Scenario: Tooling and test documents

- **WHEN** the tooling and test documents are read
- **THEN** they cover the extension data sync script, the golden harness, the saved guide fixtures, and the commands that run each check

### Requirement: Technical documentation index

A technical documentation index SHALL link every component document and SHALL state which audience each one serves.

#### Scenario: Navigating from the index

- **WHEN** a maintainer opens the index
- **THEN** every component document is reachable by link from it

#### Scenario: Stale links

- **WHEN** a component document is renamed or removed
- **THEN** a test fails until the index is updated

### Requirement: Single source for install steps

Install instructions SHALL live in the root README, and technical documents SHALL link to it instead of repeating the steps.

#### Scenario: Technical document mentions installing the extension

- **WHEN** a technical document needs to refer to installation
- **THEN** it links to the root README section rather than restating the browser steps
