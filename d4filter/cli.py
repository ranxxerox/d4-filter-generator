"""Command-line interface.

``d4filter <url>``   fetch + parse a guide and summarize what was extracted
``--file PATH``      parse a saved HTML file instead of fetching
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .data import SKILLS
from .fetcher import fetch_cached
from .maxroll import parse_maxroll_guide


def _load_guide(url: str | None, file_path: str | None, use_cache: bool = True):
    if file_path:
        return parse_maxroll_guide(Path(file_path).read_text(encoding="utf-8"), source_url=file_path)
    if not url:
        raise SystemExit("error: provide a guide URL or --file PATH")
    html = fetch_cached(url, use_cache=use_cache)
    return parse_maxroll_guide(html, source_url=url)


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


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="d4filter",
        description="Generate Diablo IV loot filter import codes from build guides.",
    )
    parser.add_argument("url", nargs="?", help="maxroll.gg build-guide URL")
    parser.add_argument("--file", help="parse a saved guide HTML file instead of fetching")
    parser.add_argument("--no-cache", action="store_true", help="bypass the disk cache")
    parser.add_argument(
        "--print-guide-filter",
        help="print the guide's own loot filter code by name (e.g. 'Maxroll Light') instead of summarizing",
    )
    args = parser.parse_args(argv)

    spec = _load_guide(args.url, args.file, use_cache=not args.no_cache)

    if args.print_guide_filter:
        for name, code in spec.guide_filter_codes:
            if name.lower() == args.print_guide_filter.lower():
                print(code)
                return 0
        available = ", ".join(name for name, _ in spec.guide_filter_codes) or "none"
        raise SystemExit(f"error: no guide filter named {args.print_guide_filter!r}; available: {available}")

    print(describe(spec))
    return 0


if __name__ == "__main__":
    sys.exit(main())
