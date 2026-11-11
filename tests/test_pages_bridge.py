"""Wiring tests for the hosted guide page and the extension page bridge.

These cover the pieces that carry a guide payload from a guide tab to the
published page: the manifest, the content script's message gate, the worker's
tab selection and extraction, and the hosted page's behavior with a simulated
bridge. Parsing and encoding stay covered by the parity tests in
test_extension.py.
"""

import json
import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
EXT = REPO_ROOT / "extension"
GUIDE_PAGE = REPO_ROOT / "guide.html"
MANIFEST = EXT / "manifest.json"
PUBLISHED_ORIGIN = "https://ranxxerox.github.io"
PUBLISHED_MATCH = "https://ranxxerox.github.io/d4-filter-generator/*"

MAXROLL_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "maxroll_hell_fracture_warlock_guide.html"
ROGUE_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "maxroll_dance_of_knives_rogue_guide.html"
MOBALYTICS_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "mobalytics_blazing_scream_warlock.html"


def run_node(script: str, *args: str) -> dict:
    proc = subprocess.run(
        ["node", "-e", script, *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)


# ── manifest ────────────────────────────────────────────────────


def test_manifest_declares_the_bridge():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert manifest["manifest_version"] == 3
    assert manifest["action"]["default_popup"] == "popup.html"
    assert manifest["background"]["service_worker"] == "background.js"
    assert {"activeTab", "scripting", "storage"}.issubset(set(manifest["permissions"]))

    hosts = manifest["host_permissions"]
    assert "https://maxroll.gg/*" in hosts
    assert "https://mobalytics.gg/*" in hosts

    scripts = manifest["content_scripts"]
    assert len(scripts) == 1
    assert scripts[0]["matches"] == [PUBLISHED_MATCH]
    assert scripts[0]["js"] == ["content-pages.js"]


def test_manifest_files_exist():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert (EXT / manifest["background"]["service_worker"]).is_file()
    for script in manifest["content_scripts"]:
        for name in script["js"]:
            assert (EXT / name).is_file()
        for match in script["matches"]:
            assert match.startswith(PUBLISHED_ORIGIN + "/d4-filter-generator/")


# ── content script gate ─────────────────────────────────────────

CONTENT_SCRIPT_GATE = r"""
const mod = require(process.argv[1]);
const pageWindow = {};
const origin = "https://ranxxerox.github.io";
const request = { origin, source: pageWindow, data: { source: "d4filter-page", type: "read-guide" } };
process.stdout.write(JSON.stringify({
  accepted: mod.isGuideRequest(request, origin, pageWindow),
  otherOrigin: mod.isGuideRequest({ ...request, origin: "https://example.com" }, origin, pageWindow),
  missingOrigin: mod.isGuideRequest({ ...request, origin: undefined }, origin, pageWindow),
  otherSource: mod.isGuideRequest({ ...request, source: {} }, origin, pageWindow),
  otherChannel: mod.isGuideRequest(
    { ...request, data: { source: "d4filter-extension", type: "read-guide" } }, origin, pageWindow
  ),
  otherType: mod.isGuideRequest(
    { ...request, data: { source: "d4filter-page", type: "read-other" } }, origin, pageWindow
  ),
  noData: mod.isGuideRequest({ ...request, data: null }, origin, pageWindow),
}));
"""


def test_content_script_only_accepts_page_requests():
    out = run_node(CONTENT_SCRIPT_GATE, str(EXT / "content-pages.js"))

    assert out["accepted"] is True
    assert out["otherOrigin"] is False
    assert out["missingOrigin"] is False
    assert out["otherSource"] is False
    assert out["otherChannel"] is False
    assert out["otherType"] is False
    assert out["noData"] is False


CONTENT_SCRIPT_RELAY = r"""
const fs = require("fs");
const vm = require("vm");

const script = fs.readFileSync(process.argv[1], "utf8");
const posted = [];
const sent = [];
const listeners = [];
const documentElement = { dataset: {} };
const window = {
  addEventListener(type, fn) { if (type === "message") listeners.push(fn); },
  postMessage(data, targetOrigin) { posted.push({ data, targetOrigin }); },
};
const ctx = {
  console, setImmediate, Promise, Object,
  document: { documentElement },
  window,
  location: { origin: "https://ranxxerox.github.io" },
  chrome: {
    runtime: {
      getManifest: () => ({ version: "0.3.0" }),
      sendMessage(message) {
        if (ctx.staleContext) throw new Error("Extension context invalidated.");
        sent.push(message);
        return Promise.resolve({
          ok: true,
          payload: { remix: { state: {} }, preloaded: null, href: "https://maxroll.gg/x", seen: {} },
        });
      },
    },
  },
};
ctx.globalThis = ctx;
vm.createContext(ctx);
vm.runInContext(script, ctx, { filename: "content-pages.js" });

const message = { source: "d4filter-page", type: "read-guide" };
const pageEvent = (origin) => ({ origin, source: window, data: message });
listeners[0](pageEvent("https://ranxxerox.github.io"));
listeners[0](pageEvent("https://example.com"));
ctx.staleContext = true;
listeners[0](pageEvent("https://ranxxerox.github.io"));

setImmediate(() => {
  process.stdout.write(JSON.stringify({
    marker: documentElement.dataset.d4filterExtension,
    sent,
    posted,
  }));
});
"""


def test_content_script_announces_and_relays():
    out = run_node(CONTENT_SCRIPT_RELAY, str(EXT / "content-pages.js"))

    assert out["marker"] == "0.3.0"
    assert out["sent"] == [{"type": "d4filter:read-guide"}]
    assert len(out["posted"]) == 2
    assert all(reply["targetOrigin"] == PUBLISHED_ORIGIN for reply in out["posted"])

    ok_reply = next(reply for reply in out["posted"] if reply["data"]["ok"])
    assert ok_reply["data"]["source"] == "d4filter-extension"
    assert ok_reply["data"]["type"] == "guide"
    assert ok_reply["data"]["payload"]["remix"] == {"state": {}}

    stale = next(reply for reply in out["posted"] if not reply["data"]["ok"])
    assert "Reload this page" in stale["data"]["error"]


# ── worker tab selection ────────────────────────────────────────

WORKER_TAB_PICK = r"""
const mod = require(process.argv[1]);
const tabs = [
  { id: 1, url: "https://maxroll.gg/d4/build-guides/old", lastAccessed: 100 },
  { id: 2, url: "https://mobalytics.gg/diablo-4/profile/new", lastAccessed: 900 },
  { id: 3, url: "https://example.com/guide", lastAccessed: 5000 },
];
const untimed = [
  { id: 7, url: "https://maxroll.gg/d4/build-guides/a" },
  { id: 8, url: "https://maxroll.gg/d4/build-guides/b" },
];
const recent = mod.pickMostRecentGuide(tabs);
globalThis.chrome = {
  runtime: {
    getManifest: () => ({
      content_scripts: [{ matches: ["https://ranxxerox.github.io/d4-filter-generator/*"] }],
    }),
  },
};
process.stdout.write(JSON.stringify({
  guideHost: mod.isGuideUrl("https://maxroll.gg/d4/build-guides/x"),
  guideSubdomain: mod.isGuideUrl("https://planners.maxroll.gg/x"),
  mobalytics: mod.isGuideUrl("https://mobalytics.gg/diablo-4/profile/x"),
  lookalike: mod.isGuideUrl("https://notmaxroll.gg/x"),
  notAUrl: mod.isGuideUrl("chrome://extensions"),
  noUrl: mod.isGuideUrl(undefined),
  mostRecent: recent && recent.id,
  fallback: (mod.pickMostRecentGuide(untimed) || {}).id,
  none: mod.pickMostRecentGuide([{ id: 4, url: "https://example.com" }]),
  pagePrefix: mod.pagePrefix(),
  pageSender: mod.isPageSender({ url: "https://ranxxerox.github.io/d4-filter-generator/guide.html" }),
  otherSender: mod.isPageSender({ url: "https://ranxxerox.github.io/other/guide.html" }),
  noSenderUrl: mod.isPageSender({}),
}));
"""


def test_worker_picks_the_most_recent_guide_tab():
    out = run_node(WORKER_TAB_PICK, str(EXT / "background.js"))

    assert out["guideHost"] is True
    assert out["guideSubdomain"] is True
    assert out["mobalytics"] is True
    assert out["lookalike"] is False
    assert out["notAUrl"] is False
    assert out["noUrl"] is False
    assert out["mostRecent"] == 2
    assert out["fallback"] == 7
    assert out["none"] is None
    assert out["pagePrefix"] == PUBLISHED_ORIGIN + "/d4-filter-generator/"
    assert out["pageSender"] is True
    assert out["otherSender"] is False
    assert out["noSenderUrl"] is False


# ── worker extraction ───────────────────────────────────────────

WORKER_READ_GUIDE = r"""
const path = require("path");
const fs = require("fs");
const ext = process.argv[1];
const fixture = process.argv[2];
const mode = process.argv[3];

const html = fs.readFileSync(fixture, "utf8");
const payload = JSON.parse(
  /window\.__remixContext\s*=\s*(\{[\s\S]*?\});?\s*<\/script>/.exec(html)[1]
);
globalThis.location = { href: "https://maxroll.gg/d4/build-guides/x" };
if (mode !== "no-payload") globalThis.__remixContext = payload;

const worker = require(path.join(ext, "background.js"));
const tab = { id: 9, url: "https://maxroll.gg/d4/build-guides/x", lastAccessed: 10 };
globalThis.chrome = {
  tabs: { query: async () => (mode === "no-tab" ? [] : [tab]) },
  scripting: {
    executeScript: async (options) =>
      options.files
        ? []
        : [{ result: require(path.join(ext, "lib", "guide-tab.js")).extract() }],
  },
};

worker.readGuide().then((out) =>
  process.stdout.write(
    JSON.stringify({ ok: out.ok, error: out.error || "", payload: out.payload || null })
  )
);
"""


def test_worker_reads_a_guide_tab_without_the_popup():
    out = run_node(WORKER_READ_GUIDE, str(EXT), str(MAXROLL_FIXTURE), "success")

    assert out["ok"] is True
    assert out["payload"]["href"] == "https://maxroll.gg/d4/build-guides/x"
    assert out["payload"]["seen"] == {"remixContext": "object", "preloadedState": "undefined"}
    assert out["payload"]["remix"]["state"]["loaderData"]


@pytest.mark.parametrize(
    "mode,expected",
    [
        ("no-tab", "maxroll.gg or mobalytics.gg"),
        ("no-payload", "Reload the guide page"),
    ],
)
def test_worker_reports_unreadable_guides(mode, expected):
    out = run_node(WORKER_READ_GUIDE, str(EXT), str(MAXROLL_FIXTURE), mode)

    assert out["ok"] is False
    assert expected in out["error"]
    assert out["payload"] is None
    if mode == "no-payload":
        assert "remixContext=undefined" in out["error"]
        assert "preloadedState=undefined" in out["error"]


# ── hosted page wiring ──────────────────────────────────────────


def test_guide_page_loads_the_shared_libraries_in_order():
    html = GUIDE_PAGE.read_text(encoding="utf-8")

    sources = re.findall(r'<script src="([^"]+)"></script>', html)
    assert sources == [
        "extension/lib/core.js",
        "extension/lib/guide-spec.js",
        "extension/lib/tiers.js",
        "extension/lib/mapper.js",
    ]
    for source in sources:
        assert (REPO_ROOT / source).is_file()


def test_guide_page_holds_no_affix_data():
    html = GUIDE_PAGE.read_text(encoding="utf-8")

    assert "const DB" not in html
    assert "const SKILLS" not in html
    assert not re.search(r"0x[0-9A-Fa-f]{6,}", html)


def test_site_pages_link_to_each_other():
    picker = (REPO_ROOT / "index.html").read_text(encoding="utf-8")
    guide = GUIDE_PAGE.read_text(encoding="utf-8")

    assert 'href="guide.html"' in picker
    assert 'href="index.html"' in guide
    assert "https://github.com/ranxxerox/d4-filter-generator" in picker
    assert "https://github.com/ranxxerox/d4-filter-generator" in guide


def test_readme_documents_the_published_origin_once():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    match = manifest["content_scripts"][0]["matches"][0]
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert match in readme
    assert "Chrome or Edge" in readme

    for path in [EXT / "background.js", EXT / "content-pages.js", EXT / "popup.js", GUIDE_PAGE]:
        assert "ranxxerox.github.io" not in path.read_text(encoding="utf-8"), path


# ── hosted page behavior ────────────────────────────────────────

GUIDE_PAGE_HARNESS = r"""
const fs = require("fs");
const vm = require("vm");
const path = require("path");

const repo = process.argv[1];
const fixture = process.argv[2];
const mode = process.argv[3];
const site = process.argv[4];
const altVariant = process.argv[5] || "";

const html = fs.readFileSync(path.join(repo, "guide.html"), "utf8");
const inline = /<script>\n([\s\S]*?)\n<\/script>/.exec(html)[1];
const fixtureHtml = fs.readFileSync(fixture, "utf8");
const payloadPattern = site === "maxroll"
  ? /window\.__remixContext\s*=\s*(\{[\s\S]*?\});?\s*<\/script>/
  : /window\.__PRELOADED_STATE__\s*=\s*(\{[\s\S]*?\});?\s*<\/script>/;
const payload = JSON.parse(payloadPattern.exec(fixtureHtml)[1].replace(/;\s*$/, ""));

function makeElement(id) {
  return {
    id, textContent: "", innerHTML: "", hidden: false, disabled: false,
    value: "", download: "", dataset: {}, children: [], handlers: {},
    addEventListener(type, fn) { this.handlers[type] = fn; },
    appendChild(child) { this.children.push(child); },
    click() { return this.handlers.click ? this.handlers.click() : undefined; },
  };
}

const elements = {};
const created = [];
const documentElement = {
  dataset: mode === "no-extension" ? {} : { d4filterExtension: "0.3.0" },
};
const document = {
  documentElement,
  getElementById(id) { return (elements[id] = elements[id] || makeElement(id)); },
  createElement() { const element = makeElement(""); created.push(element); return element; },
  createRange() { return { selectNodeContents() {} }; },
  execCommand() { return true; },
};
elements.gold = makeElement("gold");
elements.gold.value = "2";

const listeners = [];
const window = {
  addEventListener(type, fn) { if (type === "message") listeners.push(fn); },
  removeEventListener(type, fn) {
    const index = listeners.indexOf(fn);
    if (index >= 0) listeners.splice(index, 1);
  },
  postMessage(data) {
    if (!data || data.source !== "d4filter-page") return;
    let reply = null;
    if (mode === "success") {
      reply = {
        source: "d4filter-extension",
        type: "guide",
        ok: true,
        payload: {
          remix: site === "maxroll" ? payload : null,
          preloaded: site === "mobalytics" ? payload : null,
          href: "https://example.test/guide",
          seen: { remixContext: "undefined", preloadedState: "undefined" },
        },
      };
    } else if (mode === "no-tab") {
      reply = { source: "d4filter-extension", type: "guide", ok: false, payload: null,
                error: "No maxroll.gg or mobalytics.gg guide tab is open. Open a guide, then try again." };
    } else if (mode === "no-payload") {
      reply = { source: "d4filter-extension", type: "guide", ok: false, payload: null,
                error: "That guide tab has no embedded payload. Reload the guide page once, then try again." };
    }
    if (!reply) return;
    setImmediate(() => {
      for (const listener of [...listeners]) {
        listener({ source: window, origin: "https://ranxxerox.github.io", data: reply });
      }
    });
  },
  getSelection() { return { removeAllRanges() {}, addRange() {} }; },
};

let clipboard = "";
const ctx = {
  console, setTimeout, clearTimeout, setImmediate, TextEncoder,
  btoa: (value) => Buffer.from(value, "binary").toString("base64"),
  document, window,
  location: {
    origin: "https://ranxxerox.github.io",
    href: "https://ranxxerox.github.io/d4-filter-generator/guide.html",
  },
  navigator: { clipboard: { writeText: async (text) => { clipboard = text; } } },
  Blob: class { constructor(parts) { this.parts = parts; } },
  URL: { createObjectURL: () => "blob:test", revokeObjectURL() {} },
};
ctx.globalThis = ctx;
vm.createContext(ctx);
for (const file of ["extension/lib/core.js", "extension/lib/guide-spec.js",
                    "extension/lib/tiers.js", "extension/lib/mapper.js"]) {
  vm.runInContext(fs.readFileSync(path.join(repo, file), "utf8"), ctx, { filename: file });
}
vm.runInContext(inline, ctx, { filename: "guide.html" });

ctx.__payload = payload;
ctx.__site = site;
ctx.__alt = altVariant;
const expected = vm.runInContext(`
  (() => {
    const parse = globalThis.__site === "maxroll"
      ? globalThis.D4.parsers.parseMaxroll
      : globalThis.D4.parsers.parseMobalytics;
    const spec = parse(globalThis.__payload, "test");
    const names = Object.keys(spec.variants || {});
    const fallback = names.find((name) => /^endgame$/i.test(name)) || null;
    const code = (variant, gold) => globalThis.D4.mapper.generateFromSpec(spec, {}, gold, variant).code;
    return {
      title: spec.title,
      gameClass: spec.gameClass,
      season: spec.season,
      variants: names,
      defaultVariant: fallback,
      defaultCode: code(fallback, 2),
      goldCode: code(fallback, 3),
      altCode: globalThis.__alt ? code(globalThis.__alt, 2) : null,
    };
  })()
`, ctx);

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

(async () => {
  await wait(mode === "no-extension" ? 1100 : 60);
  const out = {
    mode,
    installHidden: elements.install.hidden,
    generateDisabled: elements.generate.disabled,
    status: elements.status.textContent,
    statusKind: elements.status.dataset.kind,
    expected,
  };

  if (mode !== "no-extension") {
    await elements.generate.click();
    await wait(60);
    out.statusAfter = elements.status.textContent;
    out.statusKindAfter = elements.status.dataset.kind;
    out.generateDisabledAfter = elements.generate.disabled;
    out.outputHidden = elements.output.hidden;
    out.summaryHidden = elements.summary.hidden;
    out.variantHiddenAfter = elements.variantRow.hidden;
    if (mode !== "success") {
      elements.gold.value = "3";
      elements.gold.handlers.change();
      out.outputHiddenAfterChange = elements.output.hidden;
    }
  }

  if (mode === "success") {
    out.title = elements.guideTitle.textContent;
    out.gameClass = elements.guideClass.textContent;
    out.season = elements.guideSeason.textContent;
    out.variantLabel = elements.guideVariant.textContent;
    out.variantHidden = elements.variantRow.hidden;
    out.variantValue = elements.variant.value;
    out.variantOptions = elements.variant.children.map((option) => [option.value, option.textContent]);
    out.code = elements.code.textContent;
    out.core = elements.coreList.textContent;
    out.secondary = elements.secondaryList.textContent;
    out.skills = elements.skillList.textContent;
    out.unmatchedHidden = elements.unmatched.hidden;
    out.unmatchedCount = elements.unmatchedCount.textContent;
    out.unmatchedItems = elements.unmatchedList.children.map((item) => item.textContent);

    elements.gold.value = "3";
    elements.gold.handlers.change();
    out.goldCode = elements.code.textContent;

    if (altVariant) {
      elements.gold.value = "2";
      elements.variant.value = altVariant;
      elements.variant.handlers.change();
      out.altCode = elements.code.textContent;
      out.altLabel = elements.guideVariant.textContent;
    }

    await elements.copy.handlers.click();
    out.clipboardMatches = clipboard === elements.code.textContent && clipboard.length > 500;
    out.copyLabel = elements.copy.textContent;

    elements.download.handlers.click();
    const lastLink = created[created.length - 1];
    out.downloadName = lastLink && lastLink.download;
  }

  process.stdout.write(JSON.stringify(out));
})();
"""


@pytest.mark.parametrize(
    "fixture,site,alt_variant",
    [
        (MAXROLL_FIXTURE, "maxroll", "Speedfarm"),
        (MOBALYTICS_FIXTURE, "mobalytics", ""),
        (ROGUE_FIXTURE, "maxroll", "Bossing"),
    ],
)
def test_guide_page_generates_from_a_guide(fixture, site, alt_variant):
    out = run_node(
        GUIDE_PAGE_HARNESS,
        str(REPO_ROOT),
        str(fixture),
        "success",
        site,
        alt_variant,
    )
    expected = out["expected"]

    assert out["installHidden"] is True
    assert out["generateDisabled"] is False
    assert out["status"] == ""
    assert out["outputHidden"] is False
    assert out["statusAfter"] == ""
    assert out["generateDisabledAfter"] is False

    assert out["title"] == expected["title"]
    assert out["gameClass"] == expected["gameClass"]
    assert out["season"] == "Season " + str(expected["season"])
    assert out["variantLabel"] == (expected["defaultVariant"] or "All profiles merged")

    variants = expected["variants"]
    assert out["variantHidden"] is (len(variants) <= 1)
    if len(variants) > 1:
        assert out["variantOptions"] == [["", "(merge all)"]] + [[name, name] for name in variants]
        assert out["variantValue"] == (expected["defaultVariant"] or "")
        assert expected["defaultVariant"] == "Endgame"

    assert out["code"] == expected["defaultCode"]
    assert out["goldCode"] == expected["goldCode"]
    if alt_variant:
        assert out["altCode"] == expected["altCode"]
        assert out["altLabel"] == alt_variant

    assert out["unmatchedHidden"] is (out["unmatchedItems"] == [])
    assert out["unmatchedCount"] == str(len(out["unmatchedItems"]))
    assert out["clipboardMatches"] is True
    assert out["copyLabel"] == "Copied!"
    assert out["downloadName"].endswith("-filter.txt")

    from d4filter.cli import generate
    from d4filter.mobalytics import parse_mobalytics_guide
    from d4filter.maxroll import parse_maxroll_guide

    text = Path(fixture).read_text(encoding="utf-8")
    parse = parse_maxroll_guide if site == "maxroll" else parse_mobalytics_guide
    spec = parse(text, "test")
    default_variant = expected["defaultVariant"]
    assert out["code"] == generate(spec, {}, variant=default_variant)["code"]
    assert out["goldCode"] == generate(spec, {}, gold_n=3, variant=default_variant)["code"]
    if alt_variant:
        assert out["altCode"] == generate(spec, {}, variant=alt_variant)["code"]


@pytest.mark.parametrize(
    "mode,message",
    [
        ("no-tab", "No maxroll.gg or mobalytics.gg guide tab is open."),
        ("no-payload", "Reload the guide page once, then try again."),
    ],
)
def test_guide_page_reports_unreadable_guides(mode, message):
    out = run_node(GUIDE_PAGE_HARNESS, str(REPO_ROOT), str(MAXROLL_FIXTURE), mode, "maxroll")

    assert message in out["statusAfter"]
    assert out["statusKindAfter"] == "error"
    assert out["outputHidden"] is True
    assert out["generateDisabledAfter"] is False
    assert out["summaryHidden"] is True
    assert out["variantHiddenAfter"] is True
    assert out["outputHiddenAfterChange"] is True


def test_guide_page_asks_for_the_extension_when_it_is_missing():
    out = run_node(
        GUIDE_PAGE_HARNESS, str(REPO_ROOT), str(MAXROLL_FIXTURE), "no-extension", "maxroll"
    )

    assert out["installHidden"] is False
    assert out["generateDisabled"] is True
    assert out["statusKind"] == "error"
    assert "needs the D4 Filter Generator extension" in out["status"]


# ── payload object parity ───────────────────────────────────────

PAYLOAD_OBJECT_PARITY = r"""
const fs = require("fs");
const path = require("path");
const ext = process.argv[1];
const cases = JSON.parse(process.argv[2]);

require(path.join(ext, "lib", "core.js"));
const parsers = require(path.join(ext, "lib", "guide-spec.js"));
const mapper = require(path.join(ext, "lib", "mapper.js"));

const out = {};
for (const [key, spec] of Object.entries(cases)) {
  const html = fs.readFileSync(spec.file, "utf8");
  const pattern = spec.site === "maxroll"
    ? /window\.__remixContext\s*=\s*(\{[\s\S]*?\});?\s*<\/script>/
    : /window\.__PRELOADED_STATE__\s*=\s*(\{[\s\S]*?\});?\s*<\/script>/;
  const payload = JSON.parse(pattern.exec(html)[1].replace(/;\s*$/, ""));
  const parse = spec.site === "maxroll" ? parsers.parseMaxroll : parsers.parseMobalytics;
  const fromHtml = parse(html, "test");
  const fromObject = parse(payload, "test");
  const htmlResult = mapper.generateFromSpec(fromHtml, {}, 2, spec.variant || null);
  const objectResult = mapper.generateFromSpec(fromObject, {}, 2, spec.variant || null);
  out[key] = {
    sameCode: htmlResult.code === objectResult.code,
    sameCore: JSON.stringify(htmlResult.core) === JSON.stringify(objectResult.core),
    sameSecondary: JSON.stringify(htmlResult.secondary) === JSON.stringify(objectResult.secondary),
    sameSkills: JSON.stringify(htmlResult.skills) === JSON.stringify(objectResult.skills),
    sameTitle: fromHtml.title === fromObject.title,
    sameClass: fromHtml.gameClass === fromObject.gameClass,
    sameSeason: fromHtml.season === fromObject.season,
  };
}
process.stdout.write(JSON.stringify(out));
"""


def test_payload_object_matches_the_html_path():
    cases = {
        "maxroll": {"file": str(MAXROLL_FIXTURE), "site": "maxroll", "variant": "Endgame"},
        "mobalytics": {"file": str(MOBALYTICS_FIXTURE), "site": "mobalytics"},
        "rogue": {"file": str(ROGUE_FIXTURE), "site": "maxroll", "variant": "Bossing"},
    }
    out = run_node(PAYLOAD_OBJECT_PARITY, str(EXT), json.dumps(cases))

    for key, result in out.items():
        assert result["sameCode"] is True, key
        assert result["sameCore"] is True, key
        assert result["sameSecondary"] is True, key
        assert result["sameSkills"] is True, key
        assert result["sameTitle"] is True, key
        assert result["sameClass"] is True, key
        assert result["sameSeason"] is True, key
