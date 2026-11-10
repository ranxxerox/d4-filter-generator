"""Extension parity tests.

The extension's JS modules (generated core + ported parsers/mappers) must
produce output identical to the Python CLI. Node runs the JS side; pytest
compares.
"""

import json
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
EXT = REPO_ROOT / "extension"
MAXROLL_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "maxroll_hell_fracture_warlock_guide.html"
MOBALYTICS_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "mobalytics_blazing_scream_warlock.html"
ROGUE_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "maxroll_dance_of_knives_rogue_guide.html"

NODE_SCRIPT = """
const path = require("path");
const ext = process.argv[1];
const fixtures = JSON.parse(process.argv[2]);
const fs = require("fs");

global.globalThis.D4 = global.globalThis.D4 || {};
const core = require(path.join(ext, "lib", "core.js"));
const parsers = require(path.join(ext, "lib", "guide-spec.js"));
const mapper = require(path.join(ext, "lib", "mapper.js"));

const out = {};
for (const [key, [file, site, variant]] of Object.entries(fixtures)) {
  const html = fs.readFileSync(file, "utf8");
  const spec = site === "maxroll" ? parsers.parseMaxroll(html, "test") : parsers.parseMobalytics(html, "test");
  const result = mapper.generateFromSpec(spec, {}, 2, variant || null);
  out[key] = {
    site: spec.site,
    gameClass: spec.gameClass,
    season: spec.season,
    title: spec.title,
    skills: spec.skills,
    nStats: spec.statLines.length,
    core: result.core,
    secondary: result.secondary,
    skillsMapped: result.skills,
    code: result.code,
  };
}
process.stdout.write(JSON.stringify(out));
"""

PY_PARITY_CASES = [
    ("Parity Rogue", ["Critical Strike Chance", "Attack Speed"], ["Maximum Life"], ["Core Skills"], 2, "Rogue"),
    ("Parity Necro", ["Critical Strike Damage Multiplier"], ["Maximum Life", "Armor"], [], 3, "Necromancer"),
    ("Parity NoClass", ["Attack Speed"], [], ["All Skills"], 1, None),
]


def run_js(fixtures: dict) -> dict:
    proc = subprocess.run(
        ["node", "-e", NODE_SCRIPT, str(EXT), json.dumps(fixtures)],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)


@pytest.fixture(scope="module")
def js_results():
    return run_js(
        {
            "maxroll": [str(MAXROLL_FIXTURE), "maxroll"],
            "mobalytics": [str(MOBALYTICS_FIXTURE), "mobalytics"],
            "rogue": [str(ROGUE_FIXTURE), "maxroll", "Bossing"],
            "rogue_merged": [str(ROGUE_FIXTURE), "maxroll"],
        }
    )


def test_extension_core_loads():
    out = subprocess.run(
        ["node", "-e", "const c = require(process.argv[1]); console.log(Object.keys(c.DB).length)", str(EXT / "lib" / "core.js")],
        capture_output=True,
        text=True,
        check=True,
    )
    assert int(out.stdout.strip()) > 50


def test_js_maxroll_parse_matches_python_shape(js_results):
    mx = js_results["maxroll"]
    assert mx["site"] == "maxroll"
    assert mx["gameClass"] == "Warlock"
    assert mx["season"] == 15
    assert "Hell Fracture" in mx["skills"]
    assert mx["nStats"] == 7


def test_js_mobalytics_parse_matches_python_shape(js_results):
    mb = js_results["mobalytics"]
    assert mb["site"] == "mobalytics"
    assert mb["gameClass"] == "Warlock"
    assert mb["season"] == 15
    assert "Blazing Scream" in mb["skills"]


def test_js_rogue_parse_matches_python_shape(js_results):
    rg = js_results["rogue"]
    assert rg["site"] == "maxroll"
    assert rg["gameClass"] == "Rogue"
    assert rg["season"] == 15
    assert "Dance of Knives" in rg["skills"]
    assert "Shadow Step" in js_results["rogue_merged"]["skills"]


def test_extension_pipeline_matches_python_cli(js_results):
    from d4filter.cli import generate
    from d4filter.maxroll import parse_maxroll_guide
    from d4filter.mobalytics import parse_mobalytics_guide

    py_specs = {
        "maxroll": (parse_maxroll_guide(MAXROLL_FIXTURE.read_text(encoding="utf-8"), "test"), None),
        "mobalytics": (parse_mobalytics_guide(MOBALYTICS_FIXTURE.read_text(encoding="utf-8"), "test"), None),
        "rogue": (parse_maxroll_guide(ROGUE_FIXTURE.read_text(encoding="utf-8"), "test"), "Bossing"),
        "rogue_merged": (parse_maxroll_guide(ROGUE_FIXTURE.read_text(encoding="utf-8"), "test"), None),
    }
    for key, (spec, variant) in py_specs.items():
        py = generate(spec, {}, variant=variant)
        js = js_results[key]
        assert sorted(js["core"]) == sorted(py["core"]), key
        assert sorted(js["secondary"]) == sorted(py["secondary"]), key
        assert sorted(js["skillsMapped"]) == sorted(py["skills"]), key
        assert js["code"] == py["code"], f"{key}: base64 mismatch"


@pytest.mark.parametrize("name,core,sec,skills,gold,cls", PY_PARITY_CASES)
def test_js_richer_tiers_match_python(name, core, sec, skills, gold, cls):
    from d4filter.rules import build_richer_filter

    py = build_richer_filter(name, core, sec, skills, gold, cls)
    proc = subprocess.run(
        ["node", "-e", (
            "const t = require(process.argv[1]);"
            "const s = JSON.parse(process.argv[2]);"
            "process.stdout.write(t.buildRicherFilter(s.name, s.core, s.sec, s.skills, s.gold, s.cls));"
        ), str(EXT / "lib" / "tiers.js"),
           json.dumps({"name": name, "core": core, "sec": sec, "skills": skills, "gold": gold, "cls": cls})],
        capture_output=True,
        text=True,
        check=True,
    )
    assert proc.stdout == py


@pytest.mark.parametrize(
    "fixture,variant,expected_core",
    [
        (MAXROLL_FIXTURE, None, "Attack Speed"),
        (ROGUE_FIXTURE, "Bossing", "Damage Over Time Multiplier"),
        (MOBALYTICS_FIXTURE, None, "Resource Cost Reduction"),
    ],
)
def test_popup_classic_script_flow(fixture, variant, expected_core):
    """Simulate the popup: load libs as classic scripts in one shared scope
    and generate through globalThis.D4, including the variant selector path."""
    NODE_POPUP = """
const fs = require("fs"), vm = require("vm");
const ctx = {
  fs, TextEncoder,
  btoa: (s) => Buffer.from(s, "binary").toString("base64"),
  fixture: process.argv[2], ext: process.argv[1], variant: process.argv[3] || null,
};
vm.createContext(ctx);
for (const f of ["lib/core.js", "lib/tiers.js", "lib/guide-spec.js", "lib/mapper.js"]) {
  vm.runInContext(fs.readFileSync(ctx.ext + "/" + f, "utf8"), ctx, { filename: f });
}
const out = vm.runInContext(`
  const html = fs.readFileSync(globalThis.fixture, "utf8");
  const parsers = globalThis.D4.parsers;
  const spec = html.includes("window.__remixContext")
    ? parsers.parseMaxroll(html, "t")
    : parsers.parseMobalytics(JSON.parse(
        /window.__PRELOADED_STATE__\\\\s*=\\\\s*(\\\\{[\\\\s\\\\S]*?\\\\});?\\\\s*<\\\\/script>/.exec(html)[1]
      ), "t");
  globalThis.D4.mapper.generateFromSpec(spec, {}, 2, globalThis.variant)
`, ctx);
process.stdout.write(JSON.stringify({ code: out.code, core: out.core, skills: out.skills }));
"""
    proc = subprocess.run(
        ["node", "-e", NODE_POPUP, str(EXT), str(fixture), variant or ""],
        capture_output=True,
        text=True,
        check=True,
    )
    out = json.loads(proc.stdout)
    assert expected_core in out["core"]
    assert len(out["code"]) > 500


def test_popup_defaults_to_endgame_variant():
    """The popup should start on the guide's endgame profile, not merge-all."""
    NODE_POPUP = """
const fs = require("fs"), vm = require("vm");
function element() {
  return {
    value: "", innerHTML: "", textContent: "", dataset: {}, style: {}, children: [],
    addEventListener() {},
    closest() { return element(); },
    appendChild(child) { this.children.push(child); },
  };
}
const elements = {};
const ctx = {
  console, setTimeout,
  document: {
    getElementById(id) { return (elements[id] = elements[id] || element()); },
    createElement() { return element(); },
  },
  chrome: {
    storage: { sync: { get(keys, cb) { cb({}); }, set() {} } },
    scripting: { executeScript() {} },
    tabs: { query() {} },
  },
  navigator: { clipboard: { writeText() {} } },
};
ctx.globalThis = ctx;
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[1], "utf8"), ctx, { filename: "popup.js" });
const out = {
  endgame: vm.runInContext('pickDefaultVariant(["Starter","Endgame","Bossing"])', ctx),
  noEndgame: vm.runInContext('pickDefaultVariant(["Starter","Midgame"])', ctx),
  preferred: vm.runInContext('preferredVariant = "Bossing"; pickDefaultVariant(["Starter","Endgame","Bossing"])', ctx),
  stalePreferred: vm.runInContext('preferredVariant = "Nope"; pickDefaultVariant(["Starter","Endgame"])', ctx),
};
process.stdout.write(JSON.stringify(out));
"""
    proc = subprocess.run(
        ["node", "-e", NODE_POPUP, str(EXT / "popup.js")],
        capture_output=True,
        text=True,
        check=True,
    )
    out = json.loads(proc.stdout)
    assert out["endgame"] == "Endgame"
    assert out["noEndgame"] == ""
    assert out["preferred"] == "Bossing"
    assert out["stalePreferred"] == "Endgame"


def test_generated_core_matches_index_html():
    """The generated core.js must be regenerated when index.html changes."""
    import hashlib
    import re

    html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")
    script = re.search(r"<script>([\s\S]*?)</script>", html).group(1)
    start = script.find("const DB = {")
    end = script.find("// ════════════════════════════════════════════════════════════\n// FILTER GENERATION")
    source_hash = hashlib.sha256(script[start:end].strip().encode()).hexdigest()

    core_js = (EXT / "lib" / "core.js").read_text(encoding="utf-8")
    body = core_js[core_js.find("const DB = {"):]
    body = body[: body.find("if (typeof module")]
    generated_hash = hashlib.sha256(body.strip().encode()).hexdigest()
    assert source_hash == generated_hash, "extension/lib/core.js is stale; run tools/sync_extension_data.py"