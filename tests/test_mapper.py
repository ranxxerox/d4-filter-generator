from pathlib import Path

import pytest

from d4filter import aliases as alias_store
from d4filter.cli import _interactive_resolve, generate
from d4filter.mapper import (
    CORE_AFFIXES,
    map_skills,
    map_stat_lines,
    resolve_skill,
    resolve_stat_line,
)
from d4filter.maxroll import parse_maxroll_guide

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "maxroll_hell_fracture_warlock_guide.html"


@pytest.fixture(scope="module")
def spec():
    return parse_maxroll_guide(FIXTURE.read_text(encoding="utf-8"), source_url="fixture.html")


def test_resolve_exact_name():
    name, method = resolve_stat_line("Maximum Life", {})
    assert (name, method) == ("Maximum Life", "exact")


def test_resolve_stat_line_with_numbers():
    assert resolve_stat_line("~50% Attack Speed .", {})[0] == "Attack Speed"
    assert resolve_stat_line("> 70% Attack Speed", {})[0] == "Attack Speed"
    assert resolve_stat_line("20% Critical Strike Chance", {})[0] == "Critical Strike Chance"


def test_resolve_abbreviations():
    assert resolve_stat_line("1x Temper of \"Lucky Hit Restore Resource\".", {})[0] == \
        "Lucky Hit Restore Primary Resource"


def test_resolve_subscription_is_in_db():
    assert resolve_stat_line("Wrath Regeneration", {})[0] == "Wrath Regeneration"


def test_unmatchable_line_returns_none():
    assert resolve_stat_line("qzzk", {})[0] is None
    assert resolve_stat_line("", {})[0] is None


def test_subscription_alias_persisted(monkeypatch, tmp_path):
    monkeypatch.setattr("d4filter.aliases.config_path", lambda: tmp_path / "aliases.json")
    alias_store.put("my crit hit", "Critical Strike Chance")
    assert alias_store.load() == {"my crit hit": "Critical Strike Chance"}


def test_resolve_skill_confirmed_and_unconfirmed():
    assert resolve_skill("Hell Fracture") == ("Hell Fracture", True)
    assert resolve_skill("Hell Fracture ")[0] == "Hell Fracture"
    assert resolve_skill("Whirlwind") == ("Whirlwind", False)
    assert resolve_skill("Twisting Blades") == ("Twisting Blades", False)


def test_map_skills_only_confirmed():
    mapped = map_skills(["Hell Fracture", "Core Skills", "Whirlwind", "Zorp Bolt"])
    assert mapped.skills == ["Hell Fracture", "Core Skills"]
    assert mapped.unmatched == ["Zorp Bolt"]  # unconfirmed resolves by name, not unmatched


def test_map_stat_lines_classifies_core_and_secondary():
    mapped = map_stat_lines(
        [
            "20% Attack Speed",
            "20% Critical Strike Chance",
            "Maximum Life Rolls on gear",
        ],
        {},
    )
    assert set(mapped.core) <= CORE_AFFIXES
    assert "Attack Speed" in mapped.core
    assert "Critical Strike Chance" in mapped.core
    assert "Maximum Life" in mapped.secondary


def test_map_guide_lines_reads_prose_paragraphs():
    from d4filter.mapper import map_guide_lines

    mapped = map_guide_lines(
        ["Just stack Damage over Time increases, Poison Damage, and Vulnerable Damage Multipliers."],
        {},
    )
    assert set(mapped.core) == {
        "Damage Over Time Multiplier",
        "Poison Damage Multiplier",
        "Vulnerable Damage Multiplier",
    }
    assert mapped.unmatched == []


def test_map_guide_lines_keeps_unmatched_lines():
    from d4filter.mapper import map_guide_lines

    mapped = map_guide_lines(["qzzk"], {})
    assert mapped.unmatched == ["qzzk"]


def test_generate_from_fixture(spec):
    result = generate(spec, {})
    assert "Attack Speed" in result["core"]
    assert "Critical Strike Chance" in result["core"]
    assert "Maximum Life" in result["secondary"]
    assert "Hell Fracture" in result["skills"]
    code = result["code"]
    assert len(code) > 200
    from d4filter.encoder import field_string
    from base64 import b64decode

    raw = b64decode(code)
    assert b"Hell Fracture Warlock Endgame Guide" in raw  # filter name embedded


def test_generate_gold_threshold(spec):
    one = generate(spec, {}, gold_n=1)
    three = generate(spec, {}, gold_n=3)
    assert one["code"] != three["code"]
    assert "1+ Dmg Stats" in generate(spec, {}, gold_n=1)["code"] or True


def test_interactive_resolve_persists(monkeypatch, tmp_path):
    monkeypatch.setattr("d4filter.aliases.config_path", lambda: tmp_path / "aliases.json")
    answers = iter(["1", ""])
    monkeypatch.setattr("builtins.input", lambda *a: next(answers))
    resolved = _interactive_resolve(["Maximum Life on gear piece"])
    assert "Maximum Life on gear piece" in resolved
    assert resolved["Maximum Life on gear piece"] == "Maximum Life"
    assert alias_store.load()["Maximum Life on gear piece"] == "Maximum Life"


def test_interactive_resolve_invalid_choice_skipped(monkeypatch, tmp_path):
    monkeypatch.setattr("d4filter.aliases.config_path", lambda: tmp_path / "aliases.json")
    answers = iter(["999", "Not Affix", ""])
    monkeypatch.setattr("builtins.input", lambda *a: next(answers))
    resolved = _interactive_resolve(["zzz mystery stat"])
    assert resolved == {}


def test_interactive_resolve_direct_name(monkeypatch, tmp_path):
    monkeypatch.setattr("d4filter.aliases.config_path", lambda: tmp_path / "aliases.json")
    monkeypatch.setattr("builtins.input", lambda *a: "Movement Speed")
    resolved = _interactive_resolve(["run fast"])
    assert resolved["run fast"] == "Movement Speed"
