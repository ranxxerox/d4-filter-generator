# AGENTS.md

## Project Overview

Single-page, dependency-free web tool that generates Diablo IV loot filter import codes. The entire application is **one file: `index.html`** (~1300 lines) containing inline CSS, inline JS, and HTML markup. No frameworks, no build step, no package manager, no tests. Deployment is GitHub Pages from `main` (https://upsilon72.github.io/d4-filter-generator), so every commit to `main` ships immediately.

## Commands

There is no build, test, or lint tooling. The only useful commands are:

- **Run locally:** open `index.html` directly in a browser (e.g. `open index.html`) — everything works from `file://`; there is no server and no fetch/XHR logic.
- **Test changes:** manual verification in the browser. Click Generate and paste the output code into the in-game D4 filter import screen (or decode the base64 protobuf yourself to verify bytes).

## Architecture and Data Flow

Everything lives in `index.html`'s single `<script>` block, in this order:

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
