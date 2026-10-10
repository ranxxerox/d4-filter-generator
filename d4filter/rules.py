"""Richer filter tier design.

Improves on the web tool's 8-rule stack with an intermediate "near-BiS"
violet tier (N-1 core stats), a configurable gold threshold, and optional
class-aware hiding of dead-resource affixes. Rule semantics are identical
to the web format: first matching rule wins; visibility SHOW=0, RECOLOR=2,
HIDE_ALL=3, colors are packed little-endian ARGB.
"""

from __future__ import annotations

from . import data
from . import encoder as enc
from .data import DB

VIOLET = data.make_color(155, 89, 182)

CLASS_RESOURCE = {
    "Barbarian": "Fury",
    "Druid": "Spirit",
    "Necromancer": "Essence",
    "Rogue": "Energy",
    "Sorcerer": "Mana",
    "Warlock": "Wrath",
    "Spiritborn": "Vigor",
    "Paladin": "Faith",
}


def hide_dead_affixes(game_class: str) -> list[str]:
    """Affix names whose regen/on-kill resource belongs to another class."""
    own_resources = []
    for cls, resource in CLASS_RESOURCE.items():
        if cls == game_class:
            own_resources.append(resource)
    dead_prefixes = {
        resource
        for cls, resource in CLASS_RESOURCE.items()
        if resource not in own_resources
    }
    dead: list[str] = []
    for name in DB:
        if "Regeneration" in name or "On Kill" in name or "every 10 Kills" in name:
            if any(name.startswith(f"{prefix} ") for prefix in dead_prefixes):
                dead.append(name)
    return dead


def build_richer_filter(
    name: str,
    core: list[str],
    secondary: list[str],
    skills: list[str],
    gold_n: int = 2,
    game_class: str | None = None,
) -> str:
    """Rules pushed lowest-priority-first, mirroring the game's ordering."""
    core_ids = list(dict.fromkeys(DB[n] for n in core if n in DB))
    sec_ids = list(dict.fromkeys(DB[n] for n in secondary if n in DB))
    from .data import SKILLS

    skill_ids = []
    for skill in skills:
        entry = next(
            (s for s in SKILLS if s["name"] == skill and s["confirmed"]), None
        )
        if entry and entry["id"]:
            skill_ids.append(entry["id"])

    all_good = core_ids + sec_ids + skill_ids

    rules = [
        enc.make_rule("Legendary Talismans", data.SHOW, [
            enc.cond_rarity(data.LEG_PLUS),
            enc.cond_types([data.CHARM, data.SEAL]),
        ]),
        enc.make_rule("Hide Junk", data.HIDE_ALL, [
            enc.cond_rarity(data.COMMON | data.MAGIC | data.RARE),
        ]),
    ]

    if all_good:
        rules.append(enc.make_rule("Check Rare - Build Affix", data.RECOLOR,
                                   [enc.cond_rarity(data.RARE), enc.cond_affixes(all_good, 1)],
                                   data.C_ORANGE))

    if game_class and game_class in CLASS_RESOURCE:
        dead = hide_dead_affixes(game_class)
        if dead:
            rules.append(enc.make_rule("Hide Other-Class Resource", data.HIDE_ALL, [
                enc.cond_rarity(data.RARE), enc.cond_affixes([DB[d] for d in dead if d in DB], 1),
            ]))

    near_n = max(1, gold_n - 1)
    if len(core_ids) >= near_n:
        rules.append(enc.make_rule(f"Near BiS - {near_n}+ Core Stats", data.RECOLOR,
                                   [enc.cond_rarity(data.RARE), enc.cond_affixes(core_ids, near_n)],
                                   VIOLET))

    if len(core_ids) >= gold_n:
        rules.append(enc.make_rule(f"BiS Rare - {gold_n}+ Dmg Stats", data.RECOLOR,
                                   [enc.cond_rarity(data.RARE), enc.cond_affixes(core_ids, gold_n)],
                                   data.C_GOLD))

    rules.append(enc.make_rule("Codex Upgrade", data.RECOLOR, [enc.cond_codex()], data.C_GREEN))
    rules.append(enc.make_rule("Legendaries - Keep All", data.RECOLOR,
                               [enc.cond_rarity(data.LEG_PLUS)], data.C_GREEN))
    rules.append(enc.make_rule("Greater Affix - Loot", data.RECOLOR,
                               [enc.cond_greater_affix(1)], data.C_CYAN))
    rules.append(enc.make_rule("Show All - Catch All", data.SHOW, [enc.cond_rarity(data.ALL_RAR)]))

    return enc.to_base64(enc.make_filter(name, rules))
