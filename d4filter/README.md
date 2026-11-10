# d4filter

Command-line tool that turns maxroll.gg and mobalytics.gg Diablo IV build
guides into loot filter import codes, using the same reverse-engineered
protobuf format as the bundled web tool in `index.html`.

## Usage

```sh
# create/activate the venv used for development
python3 -m venv .venv
.venv/bin/pip install -e .[dev]

# summarize a guide and print an import code
.venv/bin/d4filter https://maxroll.gg/d4/build-guides/hell-fracture-warlock-guide

# read a locally saved guide page instead of fetching
.venv/bin/d4filter --file saved-guide.html

# interactive resolution of unmatched stats (choices persist to
# ~/.config/d4filter/aliases.json)
.venv/bin/d4filter <url> --interactive

# adjust the gold-tier core-stat threshold, or match the web tool exactly
.venv/bin/d4filter <url> --gold 3
.venv/bin/d4filter <url> --mirror

# narrow to one planner profile instead of merging every profile's stats
.venv/bin/d4filter <url> --variant Bossing

# print one of the guide's own filter codes instead of generating
.venv/bin/d4filter <url> --print-guide-filter "Maxroll Light"
```

## How it works

1. **Fetch** guide HTML with a disk cache (`~/.cache/d4filter`).
2. **Parse** the structured payload both sites embed:
   - maxroll: `window.__remixContext` (planner profiles, skill embeds,
     "Important Stats" notes, plus the author's own filter codes).
   - mobalytics: `window.__PRELOADED_STATE__` →
     `diablo4State.apollo.graphqlV2.queries` (Lexical rich text, skill
     labels, class/season tags).
3. **Map** statistics and skills onto the verified affix database in
   `d4filter/data.py` (exact → alias → normalized → fuzzy, plus a verbatim
   DB-name scan for prose paragraphs; skills require confirmed IDs only).
   Prose only counts when it reads like advice ("stack", "temper", "look
   for", "affix"), so skill, gem, and item descriptions that merely mention
   a stat do not become filter rules.
4. **Encode** the protobuf filter (varint/field encoders in
   `d4filter/encoder.py`) and print it base64-encoded.

Rule-tier design (`d4filter/rules.py`): cyan greater-affix, gold ≥N core
stats, violet near-BiS (N-1), orange any build affix, green codex and
legendaries, class-aware hiding of other-class resource affixes, plus
talismans and a show-all catch-all. First matching rule wins, matching
the game's interpreter.

## Tests

```sh
.venv/bin/python -m pytest
```

Golden tests run the actual JavaScript encoder from `index.html` under
node (`tools/golden_harness.js`) and assert the Python port emits
byte-identical base64 for the same rule inputs.
