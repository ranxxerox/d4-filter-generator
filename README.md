# D4 Loot Filter Generator

Turns a Diablo IV build guide or a hand-picked stat list into a loot filter import code. It runs in the browser or on your machine, with no server and no account.

There are three ways to use it. The guide importer reads a maxroll.gg or mobalytics.gg guide tab and needs the browser extension. The manual picker lets you choose affixes and skill ranks by hand. The CLI fetches a guide URL, or a saved page, and prints the code.

## Live site

- Manual picker: https://ranxxerox.github.io/d4-filter-generator/
- Guide importer: https://ranxxerox.github.io/d4-filter-generator/guide.html

The manual picker also works from `file://`. The guide importer needs the extension running on the published origin, so it stays offline when opened as a local file.

## Import a code in game

1. Open the character menu, then Loot Filter.
2. Click New Filter.
3. Click Import.
4. Paste the code and confirm.

## Guide importer and extension

The page cannot fetch either guide site itself: maxroll.gg sends no CORS header and mobalytics.gg rejects plain requests. A content script on the published site asks the extension for the payload from a guide tab you already have open, and the extension answers through the page's message channel.

You need Chrome or Edge, the extension installed, and a maxroll.gg or mobalytics.gg guide tab open.

Install the extension from source:

1. Clone or download the repository.
2. Open `chrome://extensions` and turn on Developer mode.
3. Click "Load unpacked" and select the `extension/` folder.
4. Reload the guide importer page.

Open a guide tab, open the guide importer, and press "Read guide tab". The page shows the guide title, class, and season, along with the matched core stats, secondary stats, and skills. Lines that matched no verified affix or skill are listed at the bottom. If the guide has several planner profiles, pick one or merge them all. The gold tier setting controls how many core stats it requires. Copy or download the finished code.

If the page says the extension is missing, install it and reload the page. If it says no guide tab is open, open one. If it says the guide tab has no payload, reload that guide page once.

The extension popup does the same job from a guide tab, with the variant and gold settings it remembers between uses.

The bridge works in Chrome and Edge only. The published origin appears in one place, `extension/manifest.json`:

```json
"matches": ["https://ranxxerox.github.io/d4-filter-generator/*"]
```

If you publish the site somewhere else, change that line and reload the extension. The service worker reads the allowed page URL from the manifest, so no other file hardcodes it.

## Manual picker

Open `index.html` or the live page, pick a class, select core stats, secondary stats, and skill ranks, then press Generate. Presets include the Hell Fracture Warlock build.

## CLI

```sh
python3 -m venv .venv
.venv/bin/pip install -e .[dev]

# summarize a guide and print an import code
.venv/bin/d4filter https://maxroll.gg/d4/build-guides/hell-fracture-warlock-guide

# read a saved page instead of fetching
.venv/bin/d4filter --file tests/fixtures/maxroll_hell_fracture_warlock_guide.html

# narrow to one planner profile, or raise the gold threshold
.venv/bin/d4filter https://maxroll.gg/d4/build-guides/hell-fracture-warlock-guide --variant Endgame
.venv/bin/d4filter https://maxroll.gg/d4/build-guides/hell-fracture-warlock-guide --gold 3

# machine-readable output for scripting
.venv/bin/d4filter https://maxroll.gg/d4/build-guides/hell-fracture-warlock-guide --json
```

`d4filter/README.md` covers the remaining flags, the response cache, and the alias file.

## Publishing

Every push to `main` publishes the site. The workflow in `.github/workflows/pages.yml` uploads the repository root, and you can start a deploy by hand from the Actions tab.

The first deploy needs one repository setting:

1. Open Settings, then Pages.
2. Set Source to GitHub Actions.

The fork publishes at https://ranxxerox.github.io/d4-filter-generator/. Actions must be enabled on the repository.

The whole root is published, so `tests/`, `docs/`, and `openspec/` are readable as well. The repository holds no secrets.

## Contributing

The outstanding task is confirming skill rank IDs for the classes other than Warlock: Barbarian, Druid, Necromancer, Rogue, Sorcerer, Spiritborn, and Paladin. Build a filter in game with one skill per rule, export it, and decode it. Unconfirmed skills stay unselectable in the UI and are left out of generated filters.

Affix IDs are confirmed facts. A guessed ID silently produces a broken rule in game, so add one only after the single-affix export procedure confirms it.

Run the tests before sending a change:

```sh
.venv/bin/python -m pytest
```

The suite runs the JavaScript encoder from `index.html` under node and compares it with the Python port byte for byte. It also checks the extension parsers, mapper, and tier builder against the CLI on the saved guide pages.

## Technical notes

The filter format is Protocol Buffers, base64-encoded, reverse-engineered from live D4 exports. Field numbers, nesting, and colour packing are load-bearing, so compare old and new output byte for byte when changing the encoder.

Rules are pushed lowest priority first and the encoder reverses them. The game applies the first matching rule, with visibility codes for show, recolour, and hide.

`extension/lib/core.js` is generated from `index.html` by `tools/sync_extension_data.py`, and a test fails when the two drift. Do not edit it by hand.

`d4filter/filter_mirror.py` reproduces the web tool's rule stack for parity tests. The product rule tiers live in `d4filter/rules.py`.

Guide parsing reads the JSON each site embeds, not the visible HTML. The saved pages in `tests/fixtures/` guard the current shapes, and a site redesign means refreshing them.

## Credits

Research and reverse-engineering by Upsilon72 (https://github.com/Upsilon72/d4-filter-generator), with Claude. This fork adds the hosted guide importer, the extension bridge, and the CLI.

Season 13 for the manual picker. The guide importer reports whatever season the guide itself declares.
