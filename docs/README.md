# Technical documentation

The root [README](../README.md) covers what the tool does, how to install the extension, and how to import a code. This index is for people changing the code.

| Document | Audience | Covers |
| --- | --- | --- |
| [Extension](../extension/README.md) | Extension maintainers | The manifest and its permissions, the page bridge message protocol, the popup flow and stored settings, the generated `lib/core.js`, and how a release is produced. |
| [Web tool](web-tool.md) | Web page maintainers | The shared data tables and their parity constraint, the protobuf encoder and colour packing, rule ordering and visibility codes, the two pages and their data sources, and the generated extension data. |
| [CLI](../d4filter/README.md) | CLI users and maintainers | Installation, every flag, the response cache, the alias file, and the mapper's variant and paragraph rules. |
| [Tooling](../tools/README.md) | Tooling maintainers | `sync_extension_data.py` and its staleness guard, plus `golden_harness.js`. |
| [Testing](testing.md) | Anyone running the suite | The pytest commands, the golden byte-for-byte harness, the saved guide fixtures, and the workflow and docs guards. |

## Install steps

Browser install steps live in the root README only: [Install in Chrome](../README.md#install-in-chrome) and [Install in Edge](../README.md#install-in-edge). Component documents link there instead of repeating them.
