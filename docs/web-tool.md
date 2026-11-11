# Web tool

The repository root holds two pages that share one reverse-engineered filter format. This document is for maintainers; install steps live in the root [README](../README.md#install-in-chrome).

## Shared data tables

`index.html` defines the tables everything else joins on:

- `DB`: affix display name to confirmed 32-bit affix ID.
- `SKILLS`: skill rank entries `{ name, id, class, confirmed }`.
- `CORE_CANDIDATES`: the UI grouping for the affix panels.
- `PRESETS`: the named selections, including the auto-loaded Warlock preset.

Display names are the join key between `DB`, `CORE_CANDIDATES`, `SKILLS`, the app state, and the presets. Renaming an affix means renaming it in every one of those places, or the lookup silently drops it.

`d4filter/data.py` mirrors `DB` and `SKILLS` for the CLI. Neither copy is generated, and `tests/test_data_parity.py` fails when the two drift.

IDs are reverse-engineered facts, not code. A guessed ID produces a broken rule in game, so an ID goes in only after a single-affix export confirms it. Entries with `confirmed: false` carry `id: null`, are greyed out in the UI, and are excluded from generation.

## Protobuf encoder

The encoder is handwritten in `index.html`: varint and field encoders (`efv`, `ef32`, `efb`, `efs`, `concat`), condition builders (`condRarity`, `condGreaterAffix`, `condCodex`, `condAffixes`, `condTypes`), and the rule and filter builders (`makeRule`, `makeFilter`). The output is the base64 of the binary protobuf.

Field numbers, nesting, and magic constants were reverse-engineered from live exports and are load-bearing. `d4filter/encoder.py` ports the same bytes. `tools/golden_harness.js` runs the page's own encoder under node, and `tests/test_golden.py` compares the two byte for byte.

Colours are packed ARGB uint32s: `makeColor(r, g, b, a = 255)` returns `((a << 24) | (b << 16) | (g << 8) | r) >>> 0`. `C_DEF` is `0xFFFF0000`, opaque red, not a palette default. The UI palette in `:root` is separate from these wire values.

## Rule order and visibility codes

`buildFilter` pushes rules lowest priority first: talismans, hide junk, orange build affix, gold core stats, codex, legendaries, greater affix, then the catch-all. The encoder reverses the list before writing it.

The preview shows the same rules highest priority first, so preview rule #1 is the catch-all and preview rule #8 is the lowest-priority talisman rule. The preview is not the push order.

The game applies the first matching rule. Visibility codes are `SHOW = 0`, `RECOLOR = 2`, and `HIDE_ALL = 3`. Reordering rules changes which one wins, so compare old and new output byte for byte when touching the stack.

## The two pages

- `index.html` is the manual picker. Data tables, encoder, and UI sit in one inline script, and it needs no network, so it also works from `file://`.
- `guide.html` is the hosted guide importer. It asks the extension for a guide tab's embedded payload and maps it through the same tables and encoder. It needs the published origin and the extension, so it does not work from disk.

## Generated extension data

`extension/lib/core.js` is generated from `index.html` by `tools/sync_extension_data.py`. The script copies the region from `const DB = {` to the filter-generation banner, so any encoder or data change in `index.html` must be followed by a rerun. `tests/test_extension.py` hashes that region and fails when the generated file is stale. Never edit `core.js` by hand.
