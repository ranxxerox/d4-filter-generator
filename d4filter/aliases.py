"""Persistent stat-name aliases.

Recorded interactively when a guide stat line cannot be resolved, so the
same guide parses cleanly on the next run. Stored as JSON at
``~/.config/d4filter/aliases.json`` mapping guide phrasing → DB name.
"""

from __future__ import annotations

import json
from pathlib import Path


def config_path() -> Path:
    return Path.home() / ".config" / "d4filter" / "aliases.json"


def load() -> dict[str, str]:
    path = config_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}
    return {str(k): str(v) for k, v in data.items()}


def save(aliases: dict[str, str]) -> None:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(aliases, indent=2, sort_keys=True))


def put(guide_text: str, db_name: str) -> dict[str, str]:
    aliases = load()
    aliases[guide_text] = db_name
    save(aliases)
    return aliases
