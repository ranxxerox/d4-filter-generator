# Testing

The suite is pytest only; there is no build or lint step. Install steps for the extension live in the root [README](../README.md#install-in-chrome).

## Commands

```sh
# everything
.venv/bin/python -m pytest

# one file, while working on it
.venv/bin/python -m pytest tests/test_golden.py

# quiet output
.venv/bin/python -m pytest -q
```

`node` must be on `PATH`: the golden and extension parity tests run JavaScript from `index.html` and the extension under node.

## What each suite guards

| File | Guards |
| --- | --- |
| `tests/test_golden.py` | Byte-for-byte parity between the page's encoder and the Python port. |
| `tests/test_data_parity.py` | `DB` and `SKILLS` stay identical between `index.html` and `d4filter/data.py`. |
| `tests/test_extension.py` | Extension parsers, mapper, and tiers match the CLI, the popup flow works, and `extension/lib/core.js` is not stale. |
| `tests/test_mapper.py` | Stat and skill mapping, aliases, prose cues, and unmatched handling. |
| `tests/test_maxroll.py` | maxroll payload parsing against the saved fixtures, including variants and prose notes. |
| `tests/test_mobalytics.py` | mobalytics payload parsing against the saved fixtures. |
| `tests/test_pages_bridge.py` | The guide page's message bridge and its error paths. |
| `tests/test_pages_workflow.py` | The Pages workflow's triggers, permissions, and deploy steps. |
| `tests/test_release_workflow.py` | The release workflow's triggers, version check, packaging, asset name, notes, and manifest paths. |
| `tests/test_docs.py` | The root README install guide, the download link, the component documents, and the docs index. |

## Golden harness

`tools/golden_harness.js` loads the real `<script>` block from `index.html` in a node VM with DOM stubs, sets the app state from a JSON argument, and prints the page's base64 output. `tests/test_golden.py` runs the Python encoder on the same inputs and asserts the strings match byte for byte.

A mismatch means one side moved without the other. Decide which side is correct, change the other, and keep the old output around for comparison: field numbers and nesting are load-bearing, so a plausible refactor that shifts one byte is a bug.

## Saved guide fixtures

`tests/fixtures/` holds saved maxroll and mobalytics pages. The parsers read the JSON each site embeds (`window.__remixContext` and `window.__PRELOADED_STATE__`), not the visible HTML, so the fixtures pin the shapes the parsers depend on. `.gitattributes` marks them vendored because they are third-party HTML.

Refresh a fixture when a site redesigns the page or when a parser change needs a shape the saved pages do not contain. Save the page exactly as served, then update any expectations that legitimately changed. Do not edit a fixture by hand to make a parser pass: that hides the real page shape.

## Workflow and docs guards

`tests/test_pages_workflow.py` and `tests/test_release_workflow.py` read the workflow files as text and assert their triggers, permissions, and steps. They catch a workflow edit that would stop publishing the site or ship an archive the manifest does not describe.

`tests/test_docs.py` asserts the root README's download link, install labels, in-game steps, and troubleshooting actions; that the guide page and release notes carry the same link; that every component document exists and is indexed; and that technical documents link to the README install section instead of repeating the browser steps.
