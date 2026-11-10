"""index.html is the source of truth for reverse-engineered game data.

`d4filter/data.py` and the generated `extension/lib/core.js` are copies.
These tests fail loudly when the copies drift, so a new in-game-confirmed ID
only ever needs to be added to index.html and then mirrored.
"""

import re
from pathlib import Path

import pytest

from d4filter import data

REPO_ROOT = Path(__file__).resolve().parents[1]


def _script() -> str:
    html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")
    return re.search(r"<script>([\s\S]*?)</script>", html).group(1)


@pytest.fixture(scope="module")
def script():
    return _script()


def _js_db(script: str) -> list[tuple[str, int]]:
    block = re.search(r"const DB = \{([\s\S]*?)\n\};", script).group(1)
    return [(name, int(value, 16)) for name, value in re.findall(r'"([^"]+)":\s*(0x[0-9A-Fa-f]+)', block)]


def _js_skills(script: str) -> list[dict]:
    block = re.search(r"const SKILLS = \[([\s\S]*?)\n\];", script).group(1)
    rows = re.findall(
        r'\{ name: "([^"]+)",\s*id: (null|0x[0-9A-Fa-f]+),\s*class: "([^"]+)",\s*confirmed: (true|false) \}',
        block,
    )
    return [
        {
            "name": name,
            "id": None if raw_id == "null" else int(raw_id, 16),
            "class": game_class,
            "confirmed": confirmed == "true",
        }
        for name, raw_id, game_class, confirmed in rows
    ]


def test_affix_ids_match_index_html(script):
    js_db = _js_db(script)
    names = [name for name, _ in js_db]
    assert len(names) == len(set(names)), "duplicate affix name in index.html DB"
    assert js_db == list(data.DB.items())


def test_skills_match_index_html(script):
    assert _js_skills(script) == data.SKILLS


def test_confirmed_skills_have_ids(script):
    for entry in _js_skills(script):
        if entry["confirmed"]:
            assert entry["id"] is not None, entry["name"]
        else:
            assert entry["id"] is None, entry["name"]


def test_visibility_and_rarity_constants_match(script):
    assert f"const SHOW={data.SHOW}, RECOLOR={data.RECOLOR}, HIDE_ALL={data.HIDE_ALL};" in script

    rarity = re.search(
        r"const COMMON=(0x[0-9A-Fa-f]+),MAGIC=(0x[0-9A-Fa-f]+),RARE=(0x[0-9A-Fa-f]+),"
        r"LEGENDARY=(0x[0-9A-Fa-f]+),UNIQUE=(0x[0-9A-Fa-f]+),MYTHIC=(0x[0-9A-Fa-f]+),"
        r"TALISMAN=(0x[0-9A-Fa-f]+);",
        script,
    )
    values = [int(value, 16) for value in rarity.groups()]
    assert values == [
        data.COMMON,
        data.MAGIC,
        data.RARE,
        data.LEGENDARY,
        data.UNIQUE,
        data.MYTHIC,
        data.TALISMAN,
    ]
    assert data.LEG_PLUS == data.LEGENDARY | data.UNIQUE | data.MYTHIC | data.TALISMAN
    assert f"ALL_RAR  = 0x{data.ALL_RAR:X};" in script


def test_item_type_ids_and_colors_match(script):
    assert re.search(rf"CHARM\s*=\s*0x{data.CHARM:08x};", script, re.IGNORECASE)
    assert re.search(rf"SEAL\s*=\s*0x{data.SEAL:08x};", script, re.IGNORECASE)
    assert re.search(rf"C_DEF\s*=\s*0x{data.C_DEF:08x};", script, re.IGNORECASE)

    def html_color(name: str) -> int:
        match = re.search(rf"const {name}\s*=\s*makeColor\((\d+),(\d+),(\d+)\);", script)
        assert match, name
        return data.make_color(*(int(channel) for channel in match.groups()))

    assert html_color("C_CYAN") == data.C_CYAN
    assert html_color("C_GREEN") == data.C_GREEN
    assert html_color("C_ORANGE") == data.C_ORANGE
    assert html_color("C_GOLD") == data.C_GOLD
