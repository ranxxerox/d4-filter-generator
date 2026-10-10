"""Byte-faithful mirror of buildFilter() in index.html.

Replicates the web tool's fixed 8-rule stack in lowest-priority-first push
order so golden tests can compare Python output against the live JS encoder
run under node. The richer tier design lands in a later baton.
"""

from __future__ import annotations

from . import data
from . import encoder as enc
from .data import SKILLS, DB


def build_mirror_filter(
    name: str,
    core_stats: list[str],
    secondary_stats: list[str],
    skills: list[str],
    gold_n: int,
) -> str:
    name = name or "My Loot Filter"
    # JS input path uses Sets, which preserve insertion order and dedupe.
    core_stats = list(dict.fromkeys(core_stats))
    secondary_stats = list(dict.fromkeys(secondary_stats))
    skills = list(dict.fromkeys(skills))
    core_ids = [DB[n] for n in core_stats if n in DB]
    sec_ids = [DB[n] for n in secondary_stats if n in DB]
    skill_ids = [
        sk["id"]
        for n in skills
        if (sk := next((s for s in SKILLS if s["name"] == n and s["confirmed"]), None))
        is not None
    ]

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
