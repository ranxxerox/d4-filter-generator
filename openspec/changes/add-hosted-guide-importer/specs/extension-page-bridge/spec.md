# Spec Delta

## Purpose

Lets the published guide importer read a guide tab's embedded payload through the installed extension, without the user opening the extension popup.

## ADDED Requirements

### Requirement: Page origin allowlist

The extension SHALL serve guide requests only from the published site origin.

#### Scenario: Published origin

- **WHEN** a page on the published site origin sends a guide request
- **THEN** the extension handles it

#### Scenario: Any other origin

- **WHEN** a page on any other origin sends a guide request
- **THEN** the extension ignores it

### Requirement: Guide tab selection

On request, the extension SHALL read the embedded guide payload from a maxroll.gg or mobalytics.gg tab, preferring the active tab when it is a guide and otherwise the most recently used guide tab.

#### Scenario: Active tab is a guide

- **WHEN** the active tab is a supported guide page
- **THEN** the extension returns that tab's payload and URL

#### Scenario: Active tab is not a guide

- **WHEN** the active tab is not a guide but another supported guide tab is open
- **THEN** the extension returns the most recently used guide tab's payload

#### Scenario: No guide tab

- **WHEN** no supported guide tab is open
- **THEN** the extension returns an error that names the supported sites

### Requirement: Payload extraction

The extension SHALL read `window.__remixContext` for maxroll guides and `window.__PRELOADED_STATE__` for mobalytics guides from the page's main world.

#### Scenario: Maxroll payload

- **WHEN** the tab exposes `window.__remixContext`
- **THEN** the extension returns it as a serializable value

#### Scenario: Mobalytics payload

- **WHEN** the tab exposes `window.__PRELOADED_STATE__`
- **THEN** the extension returns it as a serializable value

#### Scenario: No payload

- **WHEN** neither global is present
- **THEN** the extension returns the detected types so the page can ask the user to reload the guide page

### Requirement: Page handshake and availability

The extension SHALL announce its presence on the published page and SHALL answer requests through that page's message channel.

#### Scenario: Detection

- **WHEN** the published page loads with the extension installed
- **THEN** the page can detect the extension and its version

#### Scenario: Answer

- **WHEN** the page sends a guide request and the extension is installed
- **THEN** the extension replies with either the payload or a readable error

#### Scenario: Not installed

- **WHEN** the extension is not installed
- **THEN** the page gets no reply and shows the install message

### Requirement: Host access

The extension SHALL declare host access to maxroll.gg and mobalytics.gg so it can read guide tabs while the popup is closed, and SHALL keep the existing popup flow working.

#### Scenario: Popup closed

- **WHEN** the extension is installed and the user has not opened the popup
- **THEN** the extension can still read a guide tab on request from the published page

#### Scenario: Popup flow unchanged

- **WHEN** the user opens the popup on a guide tab
- **THEN** the popup produces the same code as before this change
