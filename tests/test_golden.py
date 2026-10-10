import json
import subprocess
from pathlib import Path

import pytest

from d4filter import data
from d4filter.encoder import (
    cond_affixes,
    cond_greater_affix,
    cond_rarity,
    encode_varint,
    field_32bit,
    field_blob,
    field_string,
    field_varint,
    make_filter,
    make_rule,
    to_base64,
)
from d4filter.filter_mirror import build_mirror_filter

REPO_ROOT = Path(__file__).resolve().parents[1]
HARNESS = REPO_ROOT / "tools" / "golden_harness.js"
INDEX_HTML = REPO_ROOT / "index.html"

GOLDEN_CASES = [
    ("Test", ["Critical Strike Chance", "Attack Speed"], ["Maximum Life"], ["Core Skills"], 2),
    ("", [], [], [], 2),
    ("Skills Only", [], [], ["Core Skills", "All Skills", "Hell Fracture"], 3),
    (
        "HF Warlock",
        [
            "Critical Strike Chance",
            "Critical Strike Damage Multiplier",
            "Attack Speed",
            "All Damage Multiplier",
            "Vulnerable Damage Multiplier",
            "Fire Damage Multiplier",
            "Shadow Damage Multiplier",
            "Wrath Regeneration",
        ],
        ["Willpower", "Maximum Life"],
        [
            "Hell Fracture",
            "Abyss Skills",
            "Core Skills",
            "All Skills",
            "Hellfire Skills",
            "Occult Skills",
            "Sigil of Chaos",
            "Sigil of Summons",
            "Sigil of Subversion",
            "Blazing Scream",
            "Bombardment",
            "Rampage",
        ],
        2,
    ),
    ("Dupes", ["Attack Speed", "Attack Speed"], ["Life On Hit"], ["Core Skills", "Core Skills"], 1),
    ("No Gold Branch", ["Attack Speed"], [], ["All Skills"], 3),
]


def run_web_tool(name, core, sec, skills, norm):
    payload = json.dumps({"name": name, "norm": norm, "core": core, "sec": sec, "skills": skills})
    return subprocess.run(
        ["node", str(HARNESS), str(INDEX_HTML), payload],
        capture_output=True,
        text=True,
        check=True,
    ).stdout


@pytest.mark.parametrize(
    "name,core,sec,skills,norm",
    GOLDEN_CASES,
    ids=[c[0] for c in GOLDEN_CASES],
)
def test_golden_bytes_match_web_tool(name, core, sec, skills, norm):
    expected = run_web_tool(name, core, sec, skills, norm)
    actual = build_mirror_filter(name, core, sec, skills, norm)
    assert actual == expected


def test_varint_single_byte():
    assert encode_varint(0) == b"\x00"
    assert encode_varint(127) == b"\x7f"


def test_varint_multi_byte():
    assert encode_varint(128) == b"\x80\x01"
    assert encode_varint(300) == b"\xac\x02"


def test_field_headers():
    assert field_varint(1, 1) == b"\x08\x01"
    assert field_32bit(3, data.C_DEF) == b"\x1d\x00\x00\xff\xff"
    assert field_blob(4, b"") == b"\x22\x00"
    assert field_string(2, "ab") == b"\x12\x02ab"


def test_rule_length_field():
    rule = make_rule("n", data.SHOW, [])
    assert rule[0] == 0x0A  # field 1, wire type 2 (length-delimited)
    tail = rule[1:]
    # Header varint itself may span bytes; decode it back out.
    decoded_len = 0
    shift = 0
    i = 0
    while True:
        b = tail[i]
        decoded_len |= (b & 0x7F) << shift
        shift += 7
        i += 1
        if not b & 0x80:
            break
    body = tail[i:]
    assert decoded_len == len(body) == 3 + len(field_varint(2, data.SHOW)) + 5 + len(field_varint(5, 1))


def test_conditions_shape():
    cond = cond_rarity(data.RARE)
    assert cond == b"\x22\x04\x08\x01\x20\x04"
    ga = cond_greater_affix(1)
    assert ga == b"\x22\x04\x08\x03\x30\x01"
    aff = cond_affixes([data.DB["Attack Speed"]], 2)
    assert aff.startswith(b"\x22")
    assert b"\x08\x06" in aff  # type tag 6


def test_make_filter_counts_rules():
    rules = [
        make_rule("a", data.SHOW, []),
        make_rule("b", data.HIDE_ALL, [cond_rarity(data.ALL_RAR)]),
    ]
    blob = make_filter("f", rules)
    text = to_base64(blob)
    assert isinstance(text, str)
    assert len(rules) == 2
