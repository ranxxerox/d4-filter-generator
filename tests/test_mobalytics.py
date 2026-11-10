from pathlib import Path

import pytest

from d4filter.cli import generate
from d4filter.mobalytics import parse_mobalytics_guide, parse_preloaded_state
from d4filter.mapper import map_prose

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "mobalytics_blazing_scream_warlock.html"


@pytest.fixture(scope="module")
def spec():
    return parse_mobalytics_guide(FIXTURE.read_text(encoding="utf-8"), source_url="fixture.html")


def test_parses_title_class_season(spec):
    assert spec.title == "MrRonit's Blazing Scream Endgame PERFECTED"
    assert spec.game_class == "Warlock"
    assert spec.season == 15
    assert spec.site == "mobalytics"


def test_extracts_base_skill_labels(spec):
    assert "Blazing Scream" in spec.skills
    assert "Metamorphosis" in spec.skills
    # Variant labels collapse to their base skill name.
    assert "Blazing Scream: Orbital Scream" not in spec.skills


def test_prose_contains_stat_lines(spec):
    blob = " | ".join(spec.stat_lines)
    assert "Attack Speed" in blob or "crit" in blob.lower()


def test_map_prose_finds_db_names():
    mapped = map_prose("Stack Crit Chance, Crit Damage Multiplier and Ranks to skills. Temper for Max Life.")
    assert "Critical Strike Chance" in mapped.core
    assert "Critical Strike Damage Multiplier" in mapped.core
    assert "Maximum Life" in mapped.secondary


def test_map_prose_expands_abbreviations():
    mapped = map_prose("Temper for Lucky Hit for Resource.")
    assert "Lucky Hit Restore Primary Resource" in mapped.secondary


def test_stat_blocks_exclude_skill_descriptions(spec):
    blob = " | ".join(spec.stat_lines).lower()
    assert "stack crit chance" in blob
    assert "damage reduction and fortify" not in blob


def test_curated_prose_ignores_incidental_mentions():
    from d4filter.mapper import map_curated_prose

    mapped = map_curated_prose(
        [
            "Dark Prison provides damage reduction and fortify",
            "Blazing Scream has a 25% lucky hit chance",
            "Stack Crit Chance, Crit Damage Multiplier and Max Life",
        ]
    )
    assert "Damage Reduction" not in mapped.secondary
    assert "Lucky Hit Chance" not in mapped.secondary
    assert "Critical Strike Chance" in mapped.core
    assert "Maximum Life" in mapped.secondary


def test_generate_from_mobalytics_curates_false_positives(spec):
    result = generate(spec, {})
    assert "Resource Cost Reduction" in result["core"]
    assert "Fire Resistance" in result["secondary"]
    assert "Maximum Life" in result["secondary"]
    assert "Lucky Hit Restore Primary Resource" in result["secondary"]
    for false_positive in ("Armor", "Willpower", "Damage Reduction", "Lucky Hit Chance"):
        assert false_positive not in result["secondary"]


def test_generate_from_mobalytics(spec):
    result = generate(spec, {})
    assert "Blazing Scream" in result["skills"]
    assert result["code"]
    import base64

    raw = base64.b64decode(result["code"])
    assert "MrRonit's Blazing Scream Endgame PERFECTED".encode() in raw


def test_parse_requires_preloaded_state():
    with pytest.raises(ValueError):
        parse_preloaded_state("<html><body>nope</body></html>")


def test_skill_exclusion_not_needed_here():
    from d4filter.rules import hide_dead_affixes

    assert "Fury Regeneration" in hide_dead_affixes("Warlock")  # Fury is a Barbarian resource
    assert "Wrath Regeneration" not in hide_dead_affixes("Warlock")
    assert "Fury On Kill" in hide_dead_affixes("Necromancer")
    assert "Fury On Kill" not in hide_dead_affixes("Barbarian")
