"""Command-line interface.

``d4filter <url>``   fetch + parse a guide and summarize what was extracted
``--file PATH``      parse a saved HTML file instead of fetching
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .data import SKILLS
from .fetcher import fetch_cached
from .mapper import CORE_AFFIXES, map_curated_prose, map_guide_lines, map_rank_mentions, map_skills
from .mobalytics import parse_mobalytics_guide
from .maxroll import parse_maxroll_guide

SUPPORTED_HOSTS = ("maxroll.gg", "mobalytics.gg")


def _load_guide(
    url: str | None,
    file_path: str | None,
    use_cache: bool = True,
    cache_ttl: float | None = None,
):
    if file_path:
        path = Path(file_path)
        if not path.is_file():
            raise SystemExit(f"error: no such file: {file_path}")
        html = path.read_text(encoding="utf-8")
        source = file_path
    elif url:
        if not any(host in url for host in SUPPORTED_HOSTS):
            raise SystemExit(
                f"error: {url!r} is not a maxroll.gg or mobalytics.gg build guide URL"
            )
        try:
            html = fetch_cached(url, use_cache=use_cache, ttl_seconds=cache_ttl)
        except Exception as exc:  # urllib raises a family of errors
            raise SystemExit(f"error: could not fetch {url}: {exc}") from exc
        source = url
    else:
        raise SystemExit("error: provide a guide URL or --file PATH")
    parser = parse_maxroll_guide if "window.__remixContext" in html else parse_mobalytics_guide
    try:
        return parser(html, source_url=source)
    except ValueError as exc:
        raise SystemExit(f"error: no guide data in {source}: {exc}") from exc


def _skill_status(spec):
    confirmed, unconfirmed = [], []
    for name in spec.skills:
        entry = next((s for s in SKILLS if s["name"] == name), None)
        if entry is None:
            unconfirmed.append(name)
        elif entry["confirmed"]:
            confirmed.append(name)
        else:
            unconfirmed.append(name)
    return confirmed, unconfirmed


def describe(spec) -> str:
    lines = [
        f"Guide:    {spec.title or '(untitled)'}",
        f"URL:      {spec.source_url}",
        f"Class:    {spec.game_class or '(unknown)'} | Season {spec.season}",
        f"Profiles: {', '.join(spec.profile_names) or '(none)'}",
        f"Variants: {', '.join((spec.variants or {}).keys()) or '(single)'}",
        "",
    ]
    confirmed, unconfirmed = _skill_status(spec)
    lines.append(f"Skills ({len(confirmed)} mappable, {len(unconfirmed)} not in DB):")
    lines.append(f"  mappable: {', '.join(confirmed) or '-'}")
    lines.append(f"  other:    {', '.join(unconfirmed) or '-'}")
    lines.append("")
    lines.append(f"Stat lines ({len(spec.stat_lines)}):")
    for stat in spec.stat_lines:
        lines.append(f"  - {stat}")
    lines.append("")
    lines.append(f"Aspects mentioned: {', '.join(spec.affix_mentions) or '-'}")
    lines.append("")
    lines.append(f"Guide-authored filter codes: {len(spec.guide_filter_codes)}")
    for name, code in spec.guide_filter_codes:
        lines.append(f"  - {name} ({len(code)} chars)")
    return "\n".join(lines)


def _interactive_resolve(unmatched: list[str]) -> dict[str, str]:
    """Prompt the user for each unmatched stat line and persist the answer."""
    from .data import DB
    from . import aliases as alias_store
    from difflib import SequenceMatcher

    resolved: dict[str, str] = {}
    for line in unmatched:
        suggestions = sorted(
            DB,
            key=lambda name: SequenceMatcher(None, line.lower(), name.lower()).ratio(),
            reverse=True,
        )[:5]
        print(f"\nUnmapped: {line!r}")
        for index, name in enumerate(suggestions, start=1):
            print(f"  {index}. {name}")
        print("  0. skip")
        choice = input("Match (number or new name, empty=skip): ").strip()
        if not choice:
            continue
        if choice.isdigit() and 1 <= int(choice) <= len(suggestions):
            db_name = suggestions[int(choice) - 1]
        elif choice in DB:
            db_name = choice
        else:
            print(f"  '{choice}' is not in the DB; try again next run")
            continue
        resolved[line] = db_name
        alias_store.put(line.strip(), db_name)
    return resolved


def generate(spec, alias_table: dict[str, str], interactive: bool = False, gold_n: int = 2, mirror: bool = False, variant: str | None = None):
    """Combine guide extraction, mapping, and the rule builder.

    ``variant`` narrows extraction to one planner profile (e.g. "Bossing");
    the default merges all profiles.
    """
    stat_lines = spec.stat_lines
    skill_names = spec.skills
    if variant:
        payload = (spec.variants or {}).get(variant)
        if payload is None:
            available = ", ".join((spec.variants or {}).keys()) or "none"
            raise SystemExit(f"error: no variant named {variant!r}; available: {available}")
        stat_lines = payload.get("stat_lines", [])
        skill_names = payload.get("skills", [])

    stats = (
        map_guide_lines(stat_lines, alias_table)
        if spec.site == "maxroll"
        else map_curated_prose(stat_lines)
    )
    stats.skills.extend(map_skills(skill_names).skills)
    rank_mapping = map_rank_mentions(stat_lines)
    stats.skills.extend(rank_mapping.skills)
    if rank_mapping.skills:
        stats.unmatched = [line for line in stats.unmatched if not map_rank_mentions([line]).skills]
    if interactive and stats.unmatched:
        resolved = _interactive_resolve(stats.unmatched)
        for line, db_name in resolved.items():
            if db_name in CORE_AFFIXES:
                stats.core.append(db_name)
            else:
                stats.secondary.append(db_name)
        stats.unmatched = [line for line in stats.unmatched if line not in resolved]

    # Dedupe while preserving order (Set semantics of the web tool).
    core = list(dict.fromkeys(stats.core))
    secondary = list(dict.fromkeys(stats.secondary))
    skills_final = list(dict.fromkeys(stats.skills))

    name = spec.title or "My Loot Filter"
    if mirror:
        from .filter_mirror import build_mirror_filter

        code = build_mirror_filter(name, core, secondary, skills_final, gold_n)
    else:
        from .rules import build_richer_filter

        code = build_richer_filter(name, core, secondary, skills_final, gold_n, spec.game_class)
    summary = {
        "core": core,
        "secondary": secondary,
        "skills": skills_final,
        "unmatched": stats.unmatched,
        "code": code,
    }
    return summary


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="d4filter",
        description="Generate Diablo IV loot filter import codes from build guides.",
    )
    parser.add_argument("url", nargs="?", help="maxroll.gg or mobalytics.gg build-guide URL")
    parser.add_argument("--file", help="parse a saved guide HTML file instead of fetching")
    parser.add_argument("--no-cache", action="store_true", help="bypass the disk cache")
    parser.add_argument(
        "--cache-ttl",
        type=float,
        default=None,
        metavar="HOURS",
        help="hours a cached guide stays fresh (default 24)",
    )
    parser.add_argument("--interactive", action="store_true", help="prompt for unmatched stats")
    parser.add_argument("--gold", type=int, default=2, help="core stats required for gold tier (default 2)")
    parser.add_argument("--mirror", action="store_true", help="use the web tool's exact 8-rule stack instead of the richer tiers")
    parser.add_argument("--variant", help="restrict extraction to one planner profile (e.g. 'Bossing'); default merges all")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON instead of text")
    parser.add_argument(
        "--describe-only",
        action="store_true",
        help="print the extraction summary instead of generating a code",
    )
    parser.add_argument(
        "--print-guide-filter",
        help="print the guide's own loot filter code by name (e.g. 'Maxroll Light') instead of generating",
    )
    args = parser.parse_args(argv)

    cache_ttl = None if args.cache_ttl is None else args.cache_ttl * 3600
    spec = _load_guide(args.url, args.file, use_cache=not args.no_cache, cache_ttl=cache_ttl)

    if args.print_guide_filter:
        for name, code in spec.guide_filter_codes:
            if name.lower() == args.print_guide_filter.lower():
                print(code)
                return 0
        available = ", ".join(name for name, _ in spec.guide_filter_codes) or "none"
        raise SystemExit(f"error: no guide filter named {args.print_guide_filter!r}; available: {available}")

    if args.describe_only:
        if args.json:
            confirmed, unconfirmed = _skill_status(spec)
            print(json.dumps({
                "title": spec.title,
                "url": spec.source_url,
                "site": spec.site,
                "class": spec.game_class,
                "season": spec.season,
                "profiles": spec.profile_names,
                "variants": list((spec.variants or {}).keys()),
                "skills_confirmed": confirmed,
                "skills_unconfirmed": unconfirmed,
                "stat_lines": spec.stat_lines,
                "aspects": spec.affix_mentions,
                "guide_filters": [name for name, _ in spec.guide_filter_codes],
            }, indent=2))
        else:
            print(describe(spec))
        return 0

    result = generate(spec, {}, interactive=args.interactive, gold_n=args.gold, mirror=args.mirror, variant=args.variant)

    if args.json:
        print(json.dumps({
            "title": spec.title or "My Loot Filter",
            "url": spec.source_url,
            "site": spec.site,
            "class": spec.game_class,
            "season": spec.season,
            "profiles": spec.profile_names,
            "variants": list((spec.variants or {}).keys()),
            "variant": args.variant,
            "gold": args.gold,
            "mirror": args.mirror,
            "core": result["core"],
            "secondary": result["secondary"],
            "skills": result["skills"],
            "unmatched": result["unmatched"],
            "code": result["code"],
        }, indent=2))
        return 0

    print(f"Filter:   {spec.title or 'My Loot Filter'}")
    print(f"Class:    {spec.game_class or '(unknown)'} | Season {spec.season}")
    variant_names = list((spec.variants or {}).keys())
    if args.variant:
        others = ", ".join(n for n in variant_names if n != args.variant) or "-"
        print(f"Variant:  {args.variant} (other variants: {others})")
    elif variant_names:
        print(f"Variants: merged ({', '.join(variant_names)}); use --variant to narrow")
    print(f"Core:     {', '.join(result['core']) or '-'}")
    print(f"Second.:  {', '.join(result['secondary']) or '-'}")
    print(f"Skills:   {', '.join(result['skills']) or '-'}")
    if result["unmatched"]:
        print("Unmatched (skipped):")
        for line in result["unmatched"]:
            print(f"  - {line}")
    print()
    print("Import code:")
    print(result["code"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
