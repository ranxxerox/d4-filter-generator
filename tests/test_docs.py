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

COMPONENT_DOCS = {
    "extension": REPO_ROOT / "extension" / "README.md",
    "web tool": DOCS / "web-tool.md",
    "CLI": REPO_ROOT / "d4filter" / "README.md",
    "tooling": REPO_ROOT / "tools" / "README.md",
    "tests": DOCS / "testing.md",
}

TECHNICAL_DOCS = [
    REPO_ROOT / "extension" / "README.md",
    REPO_ROOT / "d4filter" / "README.md",
    REPO_ROOT / "tools" / "README.md",
    DOCS / "README.md",
    DOCS / "web-tool.md",
    DOCS / "testing.md",
]

CLI_FLAGS = (
    "--help",
    "--file",
    "--no-cache",
    "--cache-ttl",
    "--interactive",
    "--gold",
    "--mirror",
    "--variant",
    "--json",
    "--describe-only",
    "--print-guide-filter",
)


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


def test_download_url_matches_every_document():
    documents = (README, GUIDE, REPO_ROOT / ".github" / "release-notes.md")
    for path in documents:
        assert DOWNLOAD_URL in path.read_text(encoding="utf-8"), path


def test_every_component_document_exists():
    missing = [name for name, path in COMPONENT_DOCS.items() if not path.is_file()]
    assert missing == []


def test_index_links_every_component_and_they_resolve():
    index = DOCS / "README.md"
    text = index.read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^)]+)\)", text):
        path = target.split("#")[0]
        assert (index.parent / path).is_file(), target

    for name, path in COMPONENT_DOCS.items():
        relative = path.relative_to(DOCS) if DOCS in path.parents else Path("..") / path.relative_to(REPO_ROOT)
        assert relative.as_posix() in text, name


def test_extension_document_covers_its_constraints():
    text = COMPONENT_DOCS["extension"].read_text(encoding="utf-8")
    for heading in (
        "## Manifest and permissions",
        "## The page bridge",
        "## Popup flow",
        "## Generated core",
        "## Producing a release",
    ):
        assert heading in text
    for name in ("d4filter-page", "d4filter-extension", "d4filter:read-guide", "d4filterExtension"):
        assert name in text
    assert "../README.md#install-in-chrome" in text


def test_web_tool_document_covers_its_topics():
    text = COMPONENT_DOCS["web tool"].read_text(encoding="utf-8")
    for heading in (
        "## Shared data tables",
        "## Protobuf encoder",
        "## Rule order and visibility codes",
        "## The two pages",
        "## Generated extension data",
    ):
        assert heading in text
    assert "sync_extension_data.py" in text


def test_tooling_document_names_both_scripts():
    text = COMPONENT_DOCS["tooling"].read_text(encoding="utf-8")
    assert "sync_extension_data.py" in text
    assert "golden_harness.js" in text
    assert "stale" in text


def test_cli_document_covers_every_flag():
    text = COMPONENT_DOCS["CLI"].read_text(encoding="utf-8")
    for flag in CLI_FLAGS:
        assert flag in text, flag
    assert "~/.cache/d4filter" in text
    assert "aliases.json" in text
    assert "--variant" in text and "paragraph" in text.lower()


def test_testing_document_names_the_commands_and_fixtures():
    text = COMPONENT_DOCS["tests"].read_text(encoding="utf-8")
    assert ".venv/bin/python -m pytest" in text
    assert "tests/fixtures/" in text
    assert "golden_harness.js" in text


def test_technical_documents_do_not_restate_browser_install_steps():
    for path in TECHNICAL_DOCS:
        text = path.read_text(encoding="utf-8")
        for label in ("Load unpacked", "Developer mode", "chrome://extensions", "edge://extensions"):
            assert label not in text, f"{path.relative_to(REPO_ROOT)} repeats {label}"
