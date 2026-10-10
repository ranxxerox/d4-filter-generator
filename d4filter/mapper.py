"""Map guide stat/skill wording to DB entries.

Resolution order per stat line: exact DB name → persisted alias →
normalized substring match → fuzzy match above threshold. Anything
unresolved is surfaced (and can be resolved interactively and persisted).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher

from . import aliases
from .data import DB, SKILLS

FUZZY_THRESHOLD = 0.72

_NUMBER_RE = re.compile(r"[\d.]+")
_NOISE_CHARS = re.compile(r"[~+%+.!,></:;()\"'\u2018\u2019]")


def _normalize(text: str) -> str:
    text = _NOISE_CHARS.sub(" ", text)
    text = _NUMBER_RE.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip().lower()


_ABBREVIATIONS = {
    "crd": "critical strike damage multiplier",
    "chd": "critical strike damage multiplier",
    "crit dmg": "critical strike damage multiplier",
    "crit di": "critical strike damage multiplier",
    "crit chance": "critical strike chance",
    "crit damage": "critical strike damage multiplier",
    "crit strike damage": "critical strike damage multiplier",
    "cs": "critical strike chance",
    "cc": "critical strike chance",
    "ldk": "lucky hit chance",
    "imp ldk": "lucky hit restore primary resource",
    "lucky hit for resource": "lucky hit restore primary resource",
    "lucky hit restore resource": "lucky hit restore primary resource",
    "max life": "maximum life",
}


@dataclass
class Mapping:
    core: list[str] = field(default_factory=list)
    secondary: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    unmatched: list[str] = field(default_factory=list)


CORE_AFFIXES = {
    "All Damage Multiplier", "Critical Strike Chance", "Critical Strike Damage Multiplier",
    "Attack Speed", "Vulnerable Damage Multiplier", "Fire Damage Multiplier",
    "Shadow Damage Multiplier", "Cold Damage Multiplier", "Lightning Damage Multiplier",
    "Physical Damage Multiplier", "Poison Damage Multiplier", "Holy Damage Multiplier",
    "Damage Over Time Multiplier", "Weapon Damage", "Wrath Regeneration",
    "Mana Regeneration", "Fury Regeneration", "Energy Regeneration", "Essence Regeneration",
    "Spirit Regeneration", "Vigor Regeneration", "Faith Regeneration",
    "Resource Cost Reduction", "Resource Generation",
}


def _classify(db_name: str) -> tuple[str, str]:
    if db_name in CORE_AFFIXES:
        return "core", db_name
    return "secondary", db_name


def _best_db_match(cleaned: str) -> str | None:
    exact = [name for name in DB if name.lower() == cleaned]
    if exact:
        return exact[0]

    substring = [name for name in DB if name.lower() in cleaned]
    if substring:
        return max(substring, key=len)

    reversed_substring = [name for name in DB if cleaned in name.lower()]
    if len(cleaned) >= 4 and reversed_substring:
        return max(reversed_substring, key=len)

    best, best_ratio = None, 0.0
    for name in DB:
        ratio = SequenceMatcher(None, cleaned, name.lower()).ratio()
        if ratio > best_ratio:
            best, best_ratio = name, ratio
    return best if best_ratio >= FUZZY_THRESHOLD else None


def resolve_stat_line(line: str, alias_table: dict[str, str]) -> tuple[str | None, str | None]:
    """Return (db_name|None, debug_info|None) for one guide stat line."""
    cleaned = _normalize(line)

    for phrase, target in _ABBREVIATIONS.items():
        if phrase in cleaned and target in DB:
            return target, "abbreviation"

    exact = next((name for name in DB if name.lower() == cleaned), None)
    if exact:
        return exact, "exact"

    alias_name = aliases.load().get(line.strip()) or alias_table.get(line.strip())
    if alias_name and alias_name in DB:
        return alias_name, "user alias"

    if cleaned and len(cleaned) >= 3:
        return _best_db_match(cleaned), "normalized"
    return None, None


def resolve_skill(name: str) -> tuple[str | None, bool]:
    """Return (db_skill_name|None, confirmed)."""
    entry = next((s for s in SKILLS if s["name"].lower() == name.lower().strip()), None)
    if entry:
        return entry["name"], bool(entry["confirmed"])
    if not name.strip():
        return None, False
    best, best_ratio = None, 0.0
    for skill in SKILLS:
        ratio = SequenceMatcher(None, name.lower().strip(), skill["name"].lower()).ratio()
        if ratio > best_ratio:
            best, best_ratio = skill, ratio
    if best_ratio >= FUZZY_THRESHOLD:
        return best["name"], bool(best["confirmed"])
    return None, False


def map_stat_lines(
    stat_lines: list[str],
    alias_table: dict[str, str],
    resolver=None,
) -> Mapping:
    """Resolver hook lets the CLI inject interactive prompting; the default
    resolver returns fuzzy results or None."""
    mapping = Mapping()
    auto_resolver = resolver or (lambda text: resolve_stat_line(text, alias_table))

    for line in stat_lines:
        db_name, method = auto_resolver(line)
        if db_name:
            role, db_name = _classify(db_name)
            (mapping.core if role == "core" else mapping.secondary).append(db_name)
        else:
            mapping.unmatched.append(line)
    return mapping


def map_skills(skill_names: list[str]) -> Mapping:
    mapping = Mapping()
    for name in skill_names:
        db_name, confirmed = resolve_skill(name)
        if db_name and confirmed:
            mapping.skills.append(db_name)
        elif not db_name:
            mapping.unmatched.append(name)
    return mapping


def map_prose(blob: str) -> Mapping:
    """Affix hunting for site prose (mobalytics): a match is official if a
    DB name (or its alias expansion) appears verbatim in the text."""
    mapping = Mapping()
    text = blob.lower()
    for phrase, target in _ABBREVIATIONS.items():
        text = re.sub(rf"{re.escape(phrase)}\b", target, text)
    for name in DB:
        if name.lower() in text:
            role, db_name = _classify(name)
            (mapping.core if role == "core" else mapping.secondary).append(db_name)
    return mapping
