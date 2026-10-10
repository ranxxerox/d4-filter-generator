// Popup logic: asks the active tab for its guide payload, maps it, and
// renders the generated import code. Aliases and the gold threshold are
// persisted via chrome.storage.sync.
"use strict";

const statusEl = document.getElementById("status");
const summaryEl = document.getElementById("summary");
const codeEl = document.getElementById("code");
const copyEl = document.getElementById("copy");
const goldEl = document.getElementById("gold");

chrome.storage.sync.get(["aliases", "gold"], (data) => {
  if (data.gold) goldEl.value = String(data.gold);
});
goldEl.addEventListener("change", () => {
  chrome.storage.sync.set({ gold: parseInt(goldEl.value, 10) });
});

function parseGuideFromSource(source, url) {
  const parsers = globalThis.D4.parsers;
  if (source.remixContext) {
    const html = `<script>window.__remixContext = ${source.remixContext}</script>`;
    return parsers.parseMaxroll(html, url);
  }
  if (source.preloadedState) {
    const html = `<script>window.__PRELOADED_STATE__ = ${source.preloadedState}</script>`;
    return parsers.parseMobalytics(html, url);
  }
  throw new Error("this tab does not expose a known guide payload");
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
    const response = await chrome.tabs.sendMessage(tab.id, { type: "d4filter:get-guide" });
    if (!response || !response.ok || !response.source) {
      throw new Error("no guide payload returned from the tab");
    }
    const spec = parseGuideFromSource(response.source, response.url);
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
