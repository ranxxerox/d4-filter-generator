// Popup logic: reads the active tab's embedded guide payload directly in
// the MAIN world (chrome.scripting), maps it, and renders the import code.
// No network requests are made; everything runs locally in the browser.
"use strict";

const statusEl = document.getElementById("status");
const summaryEl = document.getElementById("summary");
const codeEl = document.getElementById("code");
const copyEl = document.getElementById("copy");
const goldEl = document.getElementById("gold");
const variantEl = document.getElementById("variant");

let preferredVariant = "";

chrome.storage.sync.get(["gold", "variant"], (data) => {
  if (data.gold) goldEl.value = String(data.gold);
  if (data.variant) preferredVariant = data.variant;
});
goldEl.addEventListener("change", () => {
  chrome.storage.sync.set({ gold: parseInt(goldEl.value, 10) });
});

let lastSpec = null;
let lastAliases = {};

function readGuideSource(tabId) {
  return chrome.scripting.executeScript({
    target: { tabId },
    world: "MAIN",
    func: () => {
      const remix = window.__remixContext ?? null;
      const preloaded = window.__PRELOADED_STATE__ ?? null;
      return {
        remix: remix ? JSON.parse(JSON.stringify(remix)) : null,
        preloaded: preloaded ? JSON.parse(JSON.stringify(preloaded)) : null,
        seen: {
          remixContext: typeof window.__remixContext,
          preloadedState: typeof window.__PRELOADED_STATE__,
        },
        href: window.location.href,
      };
    },
  });
}

function parseGuideFromSource(source, url) {
  const parsers = globalThis.D4.parsers;
  if (source.remix) return parsers.parseMaxroll(source.remix, url);
  if (source.preloaded) return parsers.parseMobalytics(source.preloaded, url);
  return null;
}

function pickDefaultVariant(names) {
  if (preferredVariant && names.includes(preferredVariant)) return preferredVariant;
  return names.find((name) => /^endgame$/i.test(name)) || "";
}

function renderVariantOptions(spec) {
  const names = Object.keys(spec.variants || {});
  variantEl.innerHTML = "";
  if (names.length <= 1) {
    variantEl.closest("label").style.display = "none";
    variantEl.value = "";
    return;
  }
  variantEl.closest("label").style.display = "flex";
  for (const name of ["(merge all)", ...names]) {
    const option = document.createElement("option");
    option.value = name === "(merge all)" ? "" : name;
    option.textContent = name;
    variantEl.appendChild(option);
  }
  variantEl.value = pickDefaultVariant(names);
}

function regenerate() {
  if (!lastSpec) return;
  const goldN = parseInt(goldEl.value, 10);
  const variant = variantEl.value || null;
  const result = globalThis.D4.mapper.generateFromSpec(lastSpec, lastAliases, goldN, variant);
  render(lastSpec, result, variant);
}

variantEl.addEventListener("change", () => {
  preferredVariant = variantEl.value;
  chrome.storage.sync.set({ variant: preferredVariant });
  regenerate();
});
goldEl.addEventListener("change", regenerate);

function render(spec, result, variant) {
  const lines = [
    `${spec.title || "(untitled)"} — ${spec.gameClass || "?"} S${spec.season ?? "?"}`,
    `Variant: ${variant || "all profiles merged"}`,
    `Core: ${result.core.join(", ") || "-"}`,
    `Secondary: ${result.secondary.join(", ") || "-"}`,
    `Skills: ${result.skills.join(", ") || "-"}`,
  ];
  if (result.unmatched.length) {
    lines.push(`Unmatched: ${result.unmatched.length}`);
  }
  summaryEl.textContent = lines.join("\n");
  codeEl.textContent = result.code;
  codeEl.style.display = "block";
  copyEl.style.display = "block";
  copyEl.dataset.code = result.code;
}

document.getElementById("generate").addEventListener("click", async () => {
  statusEl.textContent = "Reading guide…";
  summaryEl.textContent = "";
  codeEl.style.display = "none";
  copyEl.style.display = "none";
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab || !tab.id || !/^https?:/.test(tab.url || "")) {
      throw new Error("open a maxroll.gg or mobalytics.gg guide tab first");
    }
    const [injection] = await readGuideSource(tab.id);
    const source = injection && injection.result;
    const spec = source ? parseGuideFromSource(source, source.href) : null;
    if (!spec) {
      const seen = source ? source.seen : {};
      const detail = Object.entries(seen)
        .map(([key, type]) => `${key}=${type}`)
        .join(", ") || "page not inspected";
      throw new Error(
        `no guide payload on this tab (${detail}). Reload the guide page once, then click Generate again.`
      );
    }
    lastSpec = spec;
    lastAliases = (await chrome.storage.sync.get("aliases")).aliases || {};
    renderVariantOptions(spec);
    regenerate();
    statusEl.textContent = "";
  } catch (error) {
    statusEl.textContent = `Error: ${error.message}`;
  }
});

copyEl.addEventListener("click", async () => {
  await navigator.clipboard.writeText(copyEl.dataset.code);
  copyEl.textContent = "Copied!";
  setTimeout(() => { copyEl.textContent = "Copy Code"; }, 1500);
});
