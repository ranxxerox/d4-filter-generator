# d4filter

Command-line tool that turns maxroll.gg and mobalytics.gg Diablo IV build guides into loot filter import codes, using the same reverse-engineered protobuf format as the web tool in `index.html`.

## Install

The package needs Python 3.11 or newer.

```sh
python3 -m venv .venv
.venv/bin/pip install -e .[dev]
```

This installs the `d4filter` console entry point and the test dependencies. Every command below uses `.venv/bin/d4filter`, which avoids activating the environment.

## Usage

```sh
# summarize a guide and print an import code
.venv/bin/d4filter https://maxroll.gg/d4/build-guides/hell-fracture-warlock-guide

# read a saved page instead of fetching
.venv/bin/d4filter --file tests/fixtures/maxroll_hell_fracture_warlock_guide.html
```

### Flags

| Flag | Effect |
| --- | --- |
| `url` | maxroll.gg or mobalytics.gg build-guide URL. Omit it when using `--file`. |
| `-h`, `--help` | Print the flag list and exit. |
| `--file FILE` | Parse a saved guide HTML file instead of fetching. |
| `--no-cache` | Bypass the disk cache and fetch again. |
| `--cache-ttl HOURS` | Hours a cached guide stays fresh (default 24). |
| `--interactive` | Prompt for unmatched stats and save the answers as aliases. |
| `--gold GOLD` | Core stats required for the gold tier (default 2). |
| `--mirror` | Use the web tool's exact 8-rule stack instead of the richer tiers. |
| `--variant VARIANT` | Restrict extraction to one planner profile (e.g. `Bossing`); the default merges every profile. |
| `--json` | Emit machine-readable JSON instead of text. Also works with `--describe-only`. |
| `--describe-only` | Print the extraction summary instead of generating a code. |
| `--print-guide-filter NAME` | Print one of the guide's own loot filter codes by name (e.g. `Maxroll Light`) instead of generating. |

## Response cache

Fetched guides are cached on disk under `~/.cache/d4filter`, so repeated runs do not refetch the same page. A cached page is reused for 24 hours by default. `--cache-ttl HOURS` changes that window, and `--no-cache` ignores the cache for one run.

## Alias file

`--interactive` prompts for each stat the mapper could not match and writes the chosen mapping to `~/.config/d4filter/aliases.json`. Later runs read that file before falling back to fuzzy matching, so a guide phrasing is answered once.

## How it works

1. **Fetch** the guide HTML, using the cache unless told otherwise.
2. **Parse** the payload each site embeds, not the visible HTML:
   - maxroll: `window.__remixContext` (planner profiles, skill embeds, "Important Stats" notes, and the author's own filter codes).
   - mobalytics: `window.__PRELOADED_STATE__` to `diablo4State.apollo.graphqlV2.queries` (Lexical rich text, skill labels, class and season tags).
3. **Map** stats and skills onto the verified affix database in `d4filter/data.py`: exact match, then alias, then normalized, then fuzzy. Skills require a confirmed ID.
4. **Encode** the protobuf filter in `d4filter/encoder.py` and print it base64-encoded.

### Variants and paragraph rules

Maxroll guides expose one or more planner profiles as `GuideSpec.variants`. `--variant` narrows extraction to a single profile by name; without it, the CLI merges the stats and skills of every profile.

Both mappers also scan prose paragraphs for verbatim DB names, because newer guides put stat advice in sentences instead of bullets. A paragraph counts only when it contains a recommendation cue such as "stack", "temper", "look for", or "affix", so skill, gem, and item descriptions that merely mention a stat do not become filter rules. Mobalytics applies the same cue test to its Lexical text. Skill-rank goals in the same notes ("+15 Ranks to Abyss Skills", "Ranks to Hellfire/Demonology Skills") map to confirmed skills.

Rule-tier design in `d4filter/rules.py`: cyan greater-affix, gold N or more core stats, violet near-BiS (N-1), orange any build affix, green codex and legendaries, class-aware hiding of other-class resource affixes, plus talismans and a show-all catch-all. The first matching rule wins, matching the game's interpreter. `--mirror` reproduces the web tool's 8-rule stack instead; `d4filter/filter_mirror.py` exists only for the parity tests.

## Tests

```sh
.venv/bin/python -m pytest
```

Golden tests run the JavaScript encoder from `index.html` under node (`tools/golden_harness.js`) and assert the Python port emits byte-identical base64. [docs/testing.md](../docs/testing.md) covers the rest of the suite.
