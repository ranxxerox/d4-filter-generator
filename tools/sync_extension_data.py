#!/usr/bin/env python
"""Generate extension/lib/core.js from index.html.

Extracts the data tables (DB, SKILLS, constants) and the handwritten
protobuf encoder straight out of the web tool's script block so the
extension can never drift from the tested source. Rerun after any
encoder/data change in index.html.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
OUT = ROOT / "extension" / "lib" / "core.js"

HEADER = """\
// GENERATED FILE - do not edit by hand.
// Regenerate with: python3 tools/sync_extension_data.py
// Source: index.html script block (data tables + protobuf encoder).
// CommonJS-compatible so node tests can require() it and the extension
// can load it via a classic <script> tag.
"""

FOOTER = """
if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    DB, SKILLS, state, PRESETS,
    encodeVarint, efv, ef32, efb, efs, concat,
    condRarity, condGreaterAffix, condCodex, condAffixes, condTypes,
    SHOW, RECOLOR, HIDE_ALL, COMMON, MAGIC, RARE, LEGENDARY, UNIQUE,
    MYTHIC, TALISMAN, LEG_PLUS, ALL_RAR, makeColor,
    C_CYAN, C_GREEN, C_ORANGE, C_GOLD, C_DEF, CHARM, SEAL,
    makeRule, makeFilter, toBase64,
  };
}
if (typeof globalThis !== "undefined") {
  globalThis.D4 = globalThis.D4 || {};
  globalThis.D4.core = {
    DB, SKILLS, state, PRESETS,
    encodeVarint, efv, ef32, efb, efs, concat,
    condRarity, condGreaterAffix, condCodex, condAffixes, condTypes,
    SHOW, RECOLOR, HIDE_ALL, COMMON, MAGIC, RARE, LEGENDARY, UNIQUE,
    MYTHIC, TALISMAN, LEG_PLUS, ALL_RAR, makeColor,
    C_CYAN, C_GREEN, C_ORANGE, C_GOLD, C_DEF, CHARM, SEAL,
    makeRule, makeFilter, toBase64,
  };
}
"""


def main() -> None:
    html = INDEX.read_text(encoding="utf-8")
    match = re.search(r"<script>([\s\S]*?)</script>", html)
    if not match:
        raise SystemExit("no script block in index.html")
    script = match.group(1)

    start = script.find("const DB = {")
    end_marker = "// ════════════════════════════════════════════════════════════\n// FILTER GENERATION"
    end = script.find(end_marker)
    if start == -1 or end == -1:
        raise SystemExit("expected data/encoder region markers not found in index.html")

    core = script[start:end].rstrip()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(HEADER + "\n" + core + "\n" + FOOTER, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(core)} bytes of script)")


if __name__ == "__main__":
    main()
