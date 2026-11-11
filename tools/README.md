# Tools

The scripts in this folder keep the extension and the Python port honest against `index.html`. Install steps for the extension live in the root [README](../README.md#install-in-chrome); this document is for maintainers.

## sync_extension_data.py

```sh
python3 tools/sync_extension_data.py
```

Regenerates `extension/lib/core.js` from `index.html`. The script reads the page's single `<script>` block and copies the region from `const DB = {` to the `// FILTER GENERATION` banner, which holds the data tables, the protobuf encoder, the condition builders, and the colour constants. It writes a header that marks the file generated and a footer that exports the symbols through CommonJS and `globalThis.D4.core`, so node tests can `require()` it and the extension can load it as a classic script.

Rerun it after any data or encoder change in `index.html`, then commit both files together.

The staleness guard lives in `tests/test_extension.py::test_generated_core_matches_index_html`. It hashes the same region of `index.html` and the generated body and fails with "extension/lib/core.js is stale; run tools/sync_extension_data.py" when they differ. That guard is why `core.js` is never edited by hand.

## golden_harness.js

```sh
node tools/golden_harness.js index.html '{"name":"Check","norm":2,"core":[],"sec":[],"skills":[]}'
```

Loads the page's actual script block in a node VM with minimal DOM stubs, sets the app state from the JSON argument, and prints the page's base64 filter code. `tests/test_golden.py` feeds the same inputs to the Python encoder and asserts the strings match byte for byte.

The harness is the correctness gate for any encoder change: if the Python port and the page disagree, the harness shows which side moved.
