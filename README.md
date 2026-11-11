# D4 Loot Filter Generator

Turns a Diablo IV build guide or a hand-picked stat list into a loot filter import code. It runs in your browser or on your own machine, with no server and no account.

## Three ways to use it

- **Guide importer**: open a maxroll.gg or mobalytics.gg build guide in one tab and the importer in another, then press "Read guide tab". This one needs the browser extension.
- **Manual picker**: choose your class, core stats, secondary stats, and skill ranks by hand.
- **Command line**: fetch a guide or read a saved page and print the code. The CLI has its own document at [d4filter/README.md](d4filter/README.md).

## Get the extension

The guide importer cannot fetch either guide site itself, so it reads the guide through the D4 Filter Generator browser extension. Download the newest build:

**[Download d4-filter-generator-extension.zip](https://github.com/ranxxerox/d4-filter-generator/releases/latest/download/d4-filter-generator-extension.zip)**

That link always serves the newest release, so it is safe to bookmark.

## Live site

- Manual picker: https://ranxxerox.github.io/d4-filter-generator/
- Guide importer: https://ranxxerox.github.io/d4-filter-generator/guide.html

The manual picker also works from a local file. The guide importer needs the extension running on the published site, so it stays offline when opened from disk.

## Technical documentation

[docs/README.md](docs/README.md) indexes the technical documents for the extension, the web pages, the CLI, the tooling scripts, and the test suite. Each document names its audience.

## Contributing

The outstanding task is confirming skill rank IDs for the classes other than Warlock: Barbarian, Druid, Necromancer, Rogue, Sorcerer, Spiritborn, and Paladin. Build a filter in game with one skill per rule, export it, and decode it. Unconfirmed skills stay unselectable in the UI and are left out of generated filters.

Affix IDs are confirmed facts. A guessed ID silently produces a broken rule in game, so add one only after the single-affix export procedure confirms it.

[docs/testing.md](docs/testing.md) covers the test commands and what each suite guards.

## Credits

Research and reverse-engineering by Upsilon72 (https://github.com/Upsilon72/d4-filter-generator), with Claude. This fork adds the hosted guide importer, the extension bridge, and the CLI.

Season 13 for the manual picker. The guide importer reports whatever season the guide itself declares.
