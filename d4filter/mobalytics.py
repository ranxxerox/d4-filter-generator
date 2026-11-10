"""Parser for mobalytics.gg Diablo 4 build guides.

Mobalytics preloads each guide as a structured document in
``window.__PRELOADED_STATE__`` → ``diablo4State.apollo.graphqlV2.queries``.
The build document carries tagged class/season metadata, Lexical-editor
rich-text widgets (equipment notes, uniques, aspects) where stat advice is
written in prose, skill widgets keyed with ``static-data-widget`` labels,
and a per-widget loot filter container that is usually null.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from . import data  # noqa: F401  (kept for parity with maxroll parser import shape)
from .maxroll import GuideSpec, _collect_embed_texts  # noqa: F401

PRELOADED_STATE_RE = re.compile(r"window\.__PRELOADED_STATE__\s*=\s*(\{.*?\});?\s*</script>", re.DOTALL)


def parse_preloaded_state(html: str) -> dict:
    match = PRELOADED_STATE_RE.search(html)
    if not match:
        raise ValueError("no window.__PRELOADED_STATE__ found; page may not be a mobalytics guide")
    return json.loads(match.group(1).rstrip().rstrip(";"))


def _find_build_document(state: dict) -> dict | None:
    for model in state.get("diablo4State", {}).get("apollo", {}).get("graphqlV2", {}).get("queries", []):
        state_payload = model.get("state") or {}
        data = state_payload.get("data")
        if not isinstance(data, list):
            continue
        for entry in data:
            if not isinstance(entry, dict):
                continue
            game = entry.get("game") or {}
            docs = (game.get("documents") or {})
            build = docs.get("userGeneratedDocumentBySlug")
            if isinstance(build, dict) and isinstance(build.get("data"), dict):
                doc = build["data"]
                if doc.get("content"):
                    return doc
    return None


def _tag_value(doc: dict, group_slug: str) -> str | None:
    tags = ((doc.get("tags") or {}).get("data") or [])
    for tag in tags:
        if isinstance(tag, dict) and tag.get("groupSlug") == group_slug:
            return tag.get("name")
    return None


def _blob_from_lexical(node) -> str:
    """Flatten lexically-typed rich text, folding embedded widget labels in."""
    parts: list[str] = []
    if isinstance(node, dict):
        if node.get("type") == "static-data-widget":
            parts.append(node.get("label") or node.get("text") or "")
        elif isinstance(node.get("text"), str):
            parts.append(node["text"])
        for value in node.values():
            parts.append(_blob_from_lexical(value))
    elif isinstance(node, list):
        for item in node:
            parts.append(_blob_from_lexical(item))
    return " ".join(p for p in parts if p)


def _skill_labels(doc: dict) -> list[str]:
    labels: list[str] = []

    def walk(node) -> None:
        if isinstance(node, dict):
            if (
                node.get("type") == "static-data-widget"
                and node.get("groupId") == "skills"
                and isinstance(node.get("label"), str)
            ):
                base = node["label"].split(":")[0].strip()
                labels.append(base)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(doc)
    seen: set[str] = set()
    return [s for s in labels if not (s in seen or seen.add(s))]


def _block_texts(root) -> list[str]:
    """Split a Lexical root into paragraph/list-item sized blocks.

    Flattening a whole section loses the boundaries between headings and
    paragraphs, which makes it impossible to tell stat advice from a skill
    or gem description. Blocks keep that structure.
    """
    blocks: list[str] = []

    def collect(node) -> None:
        if isinstance(node, dict):
            kind = node.get("type")
            if kind in ("paragraph", "listitem"):
                text = " ".join(
                    part for part in (_blob_from_lexical(child) for child in node.get("children") or []) if part
                )
                text = " ".join(text.split())
                if text:
                    blocks.append(text)
                return
            if kind == "list":
                for child in node.get("children") or []:
                    collect(child)
                return
            for value in node.values():
                collect(value)
        elif isinstance(node, list):
            for item in node:
                collect(item)

    collect(root)
    return blocks


def _stat_prose(doc: dict) -> list[str]:
    paragraphs: list[str] = []

    for node in doc.get("content", []):
        content = node.get("data") or {}
        if not isinstance(content, dict):
            continue
        simplified = (content.get("simplifiedContent") or {})
        value = (simplified.get("value") or {})
        root = value.get("root")
        if isinstance(root, dict):
            paragraphs.extend(_block_texts(root))

    return list(dict.fromkeys(p for p in paragraphs if p.strip()))


def parse_mobalytics_guide(html: str, source_url: str = "") -> GuideSpec:
    state = parse_preloaded_state(html)
    doc = _find_build_document(state)
    if doc is None:
        raise ValueError("no build document in mobalytics preloaded state")

    title = (doc.get("data") or {}).get("name") or doc.get("slugifiedName") or ""
    spec = GuideSpec(
        source_url=source_url,
        title=title,
        site="mobalytics",
        game_class=_tag_value(doc, "class") or "",
    )
    season_name = _tag_value(doc, "season")
    if season_name:
        try:
            spec.season = int(str(season_name).replace("Season", "").strip())
        except ValueError:
            spec.season = None

    spec.skills = _skill_labels(doc)
    spec.skill_ids = []
    spec.stat_lines = _stat_prose(doc)
    return spec
