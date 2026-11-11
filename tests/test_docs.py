"""Guards for the user and technical documentation.

The root README is the only install guide, so these checks keep its
download link, install labels, and troubleshooting table in place and in
step with the guide page.

Every component document is indexed from `docs/README.md`, and technical
documents link to the README install section instead of restating the
browser steps.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
README = REPO_ROOT / "README.md"
GUIDE = REPO_ROOT / "guide.html"
DOCS = REPO_ROOT / "docs"

DOWNLOAD_URL = (
    "https://github.com/ranxxerox/d4-filter-generator/"
    "releases/latest/download/d4-filter-generator-extension.zip"
)

ACTION_WORDS = ("Install", "Open", "Reload", "Select", "Use", "Press", "Pick")


def readme_text() -> str:
    return README.read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    start = text.index(heading)
    rest = text[start + len(heading) :]
    end = re.search(r"\n#{2,3} ", rest)
    return rest[: end.start()] if end else rest


def test_readme_says_what_the_tool_does():
    text = readme_text()
    assert "loot filter import code" in text


def test_readme_names_the_three_ways_to_use_it():
    text = readme_text()
    for way in ("Guide importer", "Manual picker", "Command line"):
        assert way in text


def test_readme_has_the_stable_download_link():
    assert DOWNLOAD_URL in readme_text()


def test_readme_links_the_technical_index():
    assert "docs/README.md" in readme_text()


def test_readme_contains_no_terminal_install_commands():
    text = readme_text()
    for command in ("pip install", "python3 -m venv", "git clone"):
        assert command not in text


def test_chrome_install_names_every_label():
    install = section(readme_text(), "### Install in Chrome")
    for label in ("chrome://extensions", "Developer mode", "Load unpacked", "`extension` folder"):
        assert label in install
    assert "Success:" in install


def test_edge_install_names_every_label():
    install = section(readme_text(), "### Install in Edge")
    for label in ("edge://extensions", "Developer mode", "Load unpacked", "`extension` folder"):
        assert label in install
    assert "Success:" in install


def test_install_states_what_success_looks_like():
    text = readme_text()
    assert "no error banner" in section(text, "### Install in Chrome")
    assert "no error banner" in section(text, "### Install in Edge")


def test_in_game_import_steps():
    steps = section(readme_text(), "## Import a code in game")
    for label in ("Loot Filter", "New Filter", "Import", "Paste"):
        assert label in steps


def test_troubleshooting_covers_common_failures():
    text = readme_text()
    table = section(text, "## Troubleshooting")
    lowered = table.lower()
    for phrase in ("extension required", "no guide tab is open", "no payload", "reload"):
        assert phrase in lowered, phrase

    rows = [line for line in table.splitlines() if line.startswith("|") and "---" not in line]
    actions = [row.split("|")[2].strip() for row in rows[1:]]
    assert len(actions) >= 4
    for action in actions:
        assert any(word in action for word in ACTION_WORDS), action


def test_guide_page_links_the_same_download():
    guide = GUIDE.read_text(encoding="utf-8")
    assert DOWNLOAD_URL in guide
    assert DOWNLOAD_URL in readme_text()
