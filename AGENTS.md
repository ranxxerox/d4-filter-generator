# AGENTS.md

## Project Overview

Diablo IV loot filter tooling. Two artifacts share one reverse-engineered format:

1. **`index.html`** (~1300 lines) — the original single-page web tool, inline CSS/JS, no dependencies. Deployed by GitHub Pages from `main` (https://upsilon72.github.io/d4-filter-generator), so every commit to `main` ships immediately.
2. **`d4filter/`** — a Python CLI package (same repository) that fetches maxroll.gg and mobalytics.gg build guides and emits filter import codes. Installed via `pip install -e .[dev]`; console entry point `d4filter`. Its own docs live in `d4filter/README.md`; the ported data/encoder modules document the shared format invariants.
3. **`extension/`** — an MV3 Chrome extension with the same goal: a content script forwards each guide page's embedded JSON (`window.__remixContext` / `__PRELOADED_STATE__`) to a popup that maps stats and emits an import code. `extension/lib/core.js` is **generated** from `index.html` by `tools/sync_extension_data.py` — never edit it by hand; rerun the script after encoder/data changes (a pytest staleness guard enforces this). The other lib modules are IIFE-wrapped because they load as classic scripts sharing one global scope.

No frameworks, no build step, no lint tooling. Tests are pytest (`.venv/bin/python -m pytest`); golden tests require `node` on PATH.

## Commands

There is no build or lint tooling. The useful commands are:

- **Run the web tool locally:** open `index.html` directly in a browser (e.g. `open index.html`) — everything works from `file://`.
- **Run the CLI:** `.venv/bin/d4filter <guide-url>` (see `d4filter/README.md` for flags).
- **Test changes:** `.venv/bin/python -m pytest`. Golden tests execute the JavaScript encoder extracted from `index.html` under node (`tools/golden_harness.js`) and compare output byte-for-byte with the Python port — they are the main correctness gate for any encoder/data change.
- **Test the web tool manually:** generate a code in the browser, paste into the in-game D4 filter import screen.

## Architecture and Data Flow

The web tool lives in `index.html`'s single `<script>` block, in this order:

1. **Data tables** (lines ~718–913):
   - `DB` — map of affix display name → confirmed 32-bit affix ID (hex). Currently 77 entries.
   - `SKILLS` — array of skill-rank entries `{ name, id, class, confirmed }`. Only Warlock + two generic entries are confirmed; entries with `confirmed: false` have `id: null` and are intentionally **not selectable** in the UI.
   - `CORE_CANDIDATES` — UI grouping for the affix panels.
   - `state` — the single mutable app state ({Sets} of core stats, secondary stats, skills, last generated code).
   - `PRESETS` — keyed presets incl. `hf-warlock` (auto-loaded on DOMContentLoaded) and `clear`.

2. **Protobuf encoder** (~line 918): handwritten varint/field encoders (`efv`, `ef32`, `efb`, `efs`, `concat`) and condition builders (`condRarity`, `condGreaterAffix`, `condCodex`, `condAffixes`, `condTypes`). Output is base64 (`toBase64`) of the binary protobuf filter.

3. **Filter generation** (`buildFilter`, ~line 1002): emits the fixed 8-rule stack in **lowest-priority-first order** (the encoder reverses it) — Legendary Talismans, Hide Junk, orange build-affix recolor, gold 2+-core-stats recolor (only if enough core stats selected), Codex, Legendaries, Greater Affix, and a final Show-All catch-all.

4. **UI functions**: `renderCoreStats`, `filterSkills`, `toggleAffix`, `toggleSkill`, `updatePreview`, `generate`, `copyCode`, `downloadCode`, `loadPreset`, `showToast`. Wire-up happens via inline `onclick` / `onchange` / `oninput` attributes in the HTML — not addEventListener (except for the DOMContentLoaded init block).

## Critical Domain Knowledge (the actual risk areas)

- **Affix/skill IDs are reverse-engineered facts, not code.** Every ID in `DB` and `SKILLS` was confirmed only through tedious in-game work: build a filter with one affix per rule in D4, export, and decode. There is no API. **Never invent, guess, or "fix" an ID** — an unverified ID silently produces broken rules in-game. New IDs go in only after the single-affix export procedure confirms them.
- **Non-Warlock skill IDs are placeholders:** `{ name, id: null, confirmed: false }`. The code consistently treats `confirmed: false` as unselectable and excluded from generation (`buildFilter` at index.html:1008 filters on `confirmed`; the UI greys them out). Keep this gating intact when adding class support; the outstanding contribution task is confirming IDs for Barbarian, Druid, Necromancer, Rogue, Sorcerer, Spiritborn, Paladin.
- **Rule order is inverted:** rules are pushed lowest-priority-first in `buildFilter` and displayed highest-first in `updatePreview`. The preview (rule #1 = catch-all) is *not* the push order. If you reorder rules, defeat/enable semantics must match the game's interpreter: first matching rule wins (`SHOW=0`, `RECOLOR=2`, `HIDE_ALL=3` visibility codes).
- **The protobuf format is undocumented externally:** it was reverse-engineered from live D4 exports. Field numbers, nesting (`efb` wraps length-delimited submessages), and magic constants (rarity bitmask, `CHARM`/`SEAL` item type IDs, color packing as `makeColor` little-endian ARGB) are load-bearing. Don't refactor structure without byte-comparing old vs. new output.
- **Colors are packed ARGB uint32s** (`makeColor(r,g,b)` → `(a<<24)|(b<<16)|(g<<8)|r`); `C_DEF` is `0xFFFF0000` (red, alpha255) not a "default red color" of the app's palette.

## Conventions within the file

- Section banners use `// ════` for major areas and `// ──` for minor ones; CSS uses `/* ── name ── */` comments. The CSS custom-property palette (`--bg`, `--gold`, `--cyan`, ...) in `:root` is the only color source for the UI theme.
- Data lives in plain `const` objects/arrays keyed by human-readable display names; display name strings are used as the join key between `DB`, `CORE_CANDIDATES`, `SKILLS`, `state`, and `PRESETS`. If you rename an affix string, you must rename it in **all** of those places plus presets, or the mapping breaks silently (`filter(Boolean)` drops misses).
- No minification requirements, no external JS deps. Inline everything.

## Python package specifics

- `d4filter/data.py` mirrors `DB`/`SKILLS`/constants from `index.html` and is **not** the source of truth; verify ID changes in the game first, and keep both copies identical (open decision D-001 in `docs/build_ledger.md`).
- Guide parsing is against each site's embedded JSON payload, not visible HTML (maxroll: `window.__remixContext`; mobalytics: `window.__PRELOADED_STATE__`). Site redesigns break parsers — saved HTML fixtures under `tests/fixtures/` guard the current shapes; refresh them from live pages when formats change.
- Maxroll planner profiles are exposed as `GuideSpec.variants` (per-profile stat lines and skills). The CLI `--variant` flag and the popup's Variant selector narrow extraction to one profile; the default merges all profiles. Both mappers also scan prose paragraphs for verbatim DB names, since newer guides put stat advice in sentences instead of bullets; mobalytics paragraphs only count when they contain a recommendation cue, so skill and gem descriptions do not become filter rules.
- Mobalytics plain fetches get 403; the fetcher sends full browser-like headers to succeed. Don't simplify them back to a minimal UA.
- `d4filter/filter_mirror.py` replicates the web tool's exact rule stack and is only for golden parity tests; product rule tiers live in `d4filter/rules.py`. Change behavior there, not in the mirror.
- Factory process docs (`docs/factory_config.md`, `docs/build_ledger.md`) track batons, acceptance evidence, and open decisions for ongoing work.
