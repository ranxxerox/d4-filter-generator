# Spec Delta

## Purpose

Turns a maxroll.gg or mobalytics.gg build guide into a Diablo IV loot filter import code from the published static site, using the same verified affix data and encoder as the manual picker.

## ADDED Requirements

### Requirement: Guide content comes from the extension

The published guide importer SHALL obtain guide content through the installed browser extension and SHALL NOT make cross-origin requests for guide pages.

#### Scenario: Extension present with a guide tab open

- **WHEN** the user opens the guide importer with the extension installed and a supported guide tab open
- **THEN** the page requests that tab's embedded guide payload

#### Scenario: Extension missing

- **WHEN** the extension is not installed or does not answer
- **THEN** the page shows an install or enable message and leaves the generate action unavailable

#### Scenario: No guide tab open

- **WHEN** the extension answers but no maxroll.gg or mobalytics.gg tab is open
- **THEN** the page tells the user to open a guide tab and try again

### Requirement: Guide summary

After a guide payload is parsed, the page SHALL show the guide title, game class, season, and either the selected variant or the merged label.

#### Scenario: Maxroll guide summary

- **WHEN** a maxroll guide payload is parsed
- **THEN** the page shows its title, class, season, and the merged variant label until the user picks a variant

#### Scenario: Mobalytics guide summary

- **WHEN** a mobalytics guide payload is parsed
- **THEN** the page shows its title, class, and season

### Requirement: Variant selection

When a parsed guide exposes more than one planner profile, the page SHALL let the user pick one profile or merge all profiles, and SHALL regenerate the code when the selection changes.

#### Scenario: Multiple variants

- **WHEN** the guide exposes two or more variants
- **THEN** the page lists each variant plus a merge-all option and defaults to the Endgame profile when one exists

#### Scenario: Variant change

- **WHEN** the user changes the variant
- **THEN** the page regenerates the import code from that profile without rereading the guide

#### Scenario: Single variant

- **WHEN** the guide exposes one or no variants
- **THEN** the page hides the variant control

### Requirement: Gold core-stat threshold

The page SHALL let the user set how many core stats the gold tier requires, SHALL default to 2, and SHALL regenerate the code when the value changes.

#### Scenario: Threshold change

- **WHEN** the user changes the gold threshold
- **THEN** the page regenerates the code with that threshold and the current variant

### Requirement: Import code output

The page SHALL show the generated import code and SHALL offer copy and download actions.

#### Scenario: Code rendered

- **WHEN** a code is generated
- **THEN** the page shows it in a selectable field with copy and download controls

#### Scenario: Copy

- **WHEN** the user copies the code
- **THEN** the clipboard holds the full code and the page confirms the copy

#### Scenario: Download

- **WHEN** the user downloads the code
- **THEN** the page saves a text file containing the code

### Requirement: Mapping feedback

The page SHALL list the matched core stats, secondary stats, and skills, and SHALL report guide lines that did not match a verified affix or skill.

#### Scenario: Matches shown

- **WHEN** guide lines map to verified entries
- **THEN** the page lists the matched core stats, secondary stats, and skills

#### Scenario: Unmatched lines

- **WHEN** some guide lines match nothing
- **THEN** the page shows how many were skipped and lists their text

### Requirement: Manual picker stays available

The published site SHALL keep the manual affix picker at the site root and SHALL link between the picker and the guide importer.

#### Scenario: Site root

- **WHEN** the user opens the site root
- **THEN** the manual picker loads with the same behavior as before

#### Scenario: Cross links

- **WHEN** the user follows the link on either page
- **THEN** the other page opens
