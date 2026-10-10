// Popup logic: reads the active tab's embedded guide payload directly in
// the MAIN world (chrome.scripting), maps it, and renders the import code.
// No network requests are made; everything runs locally in the browser.
"use strict";

const statusEl = document.getElementById("status");
const summaryEl = document.getElementById("summary");
const codeEl = document.getElementById("code");
const copyEl = document.getElementById("copy");
const goldEl = document.getElementById("gold");

chrome.storage.sync.get(["gold"], (data) => {
  if (data.gold) goldEl.value = String(data.gold);
});
goldEl.addEventListener("change", () => {
  chrome.storage.sync.set({ gold: parseInt(goldEl.value, 10) });
});

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

function render(spec, result) {
  const lines = [
    `${spec.title || "(untitled)"} — ${spec.gameClass || "?"} S${spec.season ?? "?"}`,
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
    const aliases = (await chrome.storage.sync.get("aliases")).aliases || {};
    const goldN = parseInt(goldEl.value, 10);
    const result = globalThis.D4.mapper.generateFromSpec(spec, aliases, goldN);
    statusEl.textContent = "";
    render(spec, result);
  } catch (error) {
    statusEl.textContent = `Error: ${error.message}`;
  }
});

copyEl.addEventListener("click", async () => {
  await navigator.clipboard.writeText(copyEl.dataset.code);
  copyEl.textContent = "Copied!";
  setTimeout(() => { copyEl.textContent = "Copy Code"; }, 1500);
});
