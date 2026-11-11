"""Guards for the extension release workflow.

The workflow is the only path that publishes a downloadable extension, so
these checks keep its triggers, permissions, packaging, and release notes
from drifting.
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "release.yml"
NOTES = REPO_ROOT / ".github" / "release-notes.md"
MANIFEST = REPO_ROOT / "extension" / "manifest.json"
PATH_SUFFIXES = (".js", ".html", ".css", ".json")


def workflow_text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def notes_text() -> str:
    return NOTES.read_text(encoding="utf-8")


def test_workflow_exists():
    assert WORKFLOW.is_file()


def test_triggers_on_version_tag_and_manual_dispatch():
    text = workflow_text()
    assert 'tags: ["v*"]' in text
    assert "workflow_dispatch:" in text


def test_token_permissions_are_least_privilege():
    text = workflow_text()
    permissions = text[text.index("permissions:") : text.index("jobs:")]
    writes = [line for line in permissions.splitlines() if line.strip().endswith("write")]
    assert writes == ["  contents: write"]


def test_packages_one_stable_asset():
    text = workflow_text()
    assert "zip -r d4-filter-generator-extension.zip extension" in text
    assert "-x 'extension/*.md'" in text


def test_publishes_with_gh_and_checked_in_notes():
    text = workflow_text()
    assert "gh release create" in text
    assert "d4-filter-generator-extension.zip" in text
    assert "--title" in text
    assert "--notes-file .github/release-notes.md" in text


def test_hyphenated_versions_publish_as_prereleases():
    text = workflow_text()
    assert "*-*" in text
    assert 'prerelease="--prerelease"' in text


def test_notes_say_what_the_archive_is():
    text = notes_text()
    assert "browser extension" in text
    assert "Chrome" in text
    assert "Edge" in text


def test_notes_give_extract_and_load_steps():
    text = notes_text()
    assert "unzip" in text
    assert "Load unpacked" in text
    assert "extension` folder" in text


def test_notes_link_to_readme_troubleshooting():
    text = notes_text()
    assert "#troubleshooting" in text
    assert "README" in text


def manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def referenced_paths(node):
    if isinstance(node, dict):
        for value in node.values():
            yield from referenced_paths(value)
    elif isinstance(node, list):
        for value in node:
            yield from referenced_paths(value)
    elif isinstance(node, str) and node.endswith(PATH_SUFFIXES) and "://" not in node:
        yield node


def test_every_manifest_path_exists_in_the_folder():
    missing = [path for path in referenced_paths(manifest()) if not (MANIFEST.parent / path).is_file()]
    assert missing == []
