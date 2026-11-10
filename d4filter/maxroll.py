"""Parser for maxroll.gg D4 build guides.

Maxroll serves its guides as a Remix app; the real data lives in the
``window.__remixContext`` JSON blob of the HTML shell, not in the static
markup. Within it, ``state.loaderData.<route>.post`` holds a gutenberg
block with an embedded ``plannerProfile`` containing:

- ``class`` / ``season`` / profile ``notes`` trees with ``d4-skill``,
  ``d4-affix``, and ``d4-tag`` embeds;
- plain-text notes sections such as "Important Stats";
- ``data.lootFilters`` — fully encoded import codes authored by the guide
  writers themselves.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

REMIX_CONTEXT_RE = re.compile(
    r"window\.__remixContext\s*=\s*(\{.*?\});?\s*</script>", re.DOTALL
)


@dataclass
class GuideSpec:
    source_url: str = ""
    title: str = ""
    site: str = "maxroll"
    game_class: str = ""
    season: int | None = None
    profile_names: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    skill_ids: list[str] = field(default_factory=list)
    affix_mentions: list[str] = field(default_factory=list)
    stat_lines: list[str] = field(default_factory=list)
    guide_filter_codes: list[tuple[str, str]] = field(default_factory=list)
    variants: dict = field(default_factory=dict)


def parse_remix_context(html: str) -> dict:
    match = REMIX_CONTEXT_RE.search(html)
    if not match:
        raise ValueError("no window.__remixContext found; page may not be a maxroll guide")
    return json.loads(match.group(1))


def _collect_embed_texts(node, embed_type: str, out: list[str]) -> None:
    if isinstance(node, dict):
        text = node.get("text")
        if node.get("embedType") == embed_type and isinstance(text, str):
            out.append(text)
        for value in node.values():
            _collect_embed_texts(value, embed_type, out)
    elif isinstance(node, list):
        for item in node:
            _collect_embed_texts(item, embed_type, out)


STAT_SECTION_HEADINGS = {"important stats", "stats", "stat priority", "stat priorities"}


def _find_important_stats(root) -> list[str]:
    """Extract bullet lines under any 'Important Stats' notes heading.

    Notes trees render the heading as one node and the bullet paragraphs as
    the following sibling node, so walk every children list and pair them.
    """
    lines: list[str] = []

    def join_parts(node) -> str:
        parts = []
        if isinstance(node, dict):
            if isinstance(node.get("text"), str):
                parts.append(node["text"])
            for value in node.values():
                parts.append(join_parts(value))
        elif isinstance(node, list):
            for item in node:
                parts.append(join_parts(item))
        return " ".join(p for p in parts if p).strip()

    def walk(node: object) -> None:
        if isinstance(node, dict):
            children = node.get("children")
            if isinstance(children, list):
                for index, child in enumerate(children):
                    texts = [
                        c.get("text", "")
                        for c in (child.get("children", []) if isinstance(child, dict) else [])
                        if isinstance(c, dict)
                    ]
                    if any(t.strip().lower() in STAT_SECTION_HEADINGS for t in texts):
                        payload = children[index + 1] if index + 1 < len(children) else None
                        bullets = payload.get("children", []) if isinstance(payload, dict) else []
                        for bullet in bullets:
                            line = join_parts(bullet)
                            if line:
                                lines.append(line)
                    walk(child)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(root)
    return lines


def parse_maxroll_guide(html: str, source_url: str = "") -> GuideSpec:
    context = parse_remix_context(html)
    loader = context["state"]["loaderData"]
    post = None
    for value in loader.values():
        if isinstance(value, dict) and isinstance(value.get("post"), dict):
            post = value["post"]
            break
    if post is None:
        raise ValueError("no post payload in maxroll remix context")

    spec = GuideSpec(source_url=source_url, title=post.get("title", ""))

    for block in post.get("gutenbergBlock", []):
        profile = block.get("plannerProfile")
        if not profile:
            continue
        data = profile.get("data", {})
        if not spec.game_class:
            spec.game_class = profile.get("class", "") or ""
            try:
                spec.season = int(data.get("season"))
            except (TypeError, ValueError):
                pass
        if spec.season is None:
            for tag in post.get("tags", []) or []:
                name = tag.get("name", "") if isinstance(tag, dict) else ""
                match = re.search(r"Season\s+(\d+)", name)
                if match:
                    spec.season = int(match.group(1))
                    break
        profiles = data.get("profiles", [])
        spec.profile_names = [p.get("name", "") for p in profiles]

        skills: list[str] = []
        affixes: list[str] = []
        variants: dict[str, dict] = {}
        for prof in profiles:
            notes = prof.get("widgetNotes", {})
            prof_skills: list[str] = []
            _collect_embed_texts(notes, "d4-skill", prof_skills)
            _collect_embed_texts(notes, "d4-affix", affixes)
            prof_stats = _find_important_stats(notes)
            skills.extend(prof_skills)
            spec.stat_lines.extend(prof_stats)
            variants[prof.get("name", "")] = {
                "stat_lines": prof_stats,
                "skills": prof_skills,
            }

        for prof in profiles:
            for line in prof.get("skillBar", []):
                if isinstance(line, str):
                    spec.skill_ids.append(line)

        seen: set[str] = set()
        spec.skills = [s for s in skills if not (s in seen or seen.add(s))]
        spec.affix_mentions = sorted(set(affixes))
        spec.stat_lines = list(dict.fromkeys(spec.stat_lines))
        spec.variants.update({
            name: {
                "stat_lines": list(dict.fromkeys(payload["stat_lines"])),
                "skills": list(dict.fromkeys(payload["skills"])),
            }
            for name, payload in variants.items()
        })

        for loot in data.get("lootFilters", []):
            name = loot.get("name", "")
            code = loot.get("code", "")
            if code:
                spec.guide_filter_codes.append((name, code))

    return spec
