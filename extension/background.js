(function () {
// Service worker: answers guide-read requests from the published page's
// content script. It picks a supported guide tab, runs the shared extractor
// in that tab's MAIN world, and returns the payload the page parses.
"use strict";

const REQUEST_TYPE = "d4filter:read-guide";
const GUIDE_MATCHES = ["https://maxroll.gg/*", "https://mobalytics.gg/*"];
const GUIDE_HOSTS = ["maxroll.gg", "mobalytics.gg"];
const NO_TAB_MESSAGE =
  "No maxroll.gg or mobalytics.gg guide tab is open. Open a guide, then try again.";
const NO_PAYLOAD_MESSAGE =
  "That guide tab has no embedded payload. Reload the guide page once, then try again.";

function isGuideUrl(url) {
  let parsed;
  try {
    parsed = new URL(url);
  } catch (error) {
    return false;
  }
  if (parsed.protocol !== "https:" && parsed.protocol !== "http:") return false;
  return GUIDE_HOSTS.some(
    (host) => parsed.hostname === host || parsed.hostname.endsWith("." + host)
  );
}

// The published page is whatever the content script matches, so the manifest
// stays the only place the site URL lives.
function pagePrefix() {
  try {
    const scripts = chrome.runtime.getManifest().content_scripts || [];
    for (const script of scripts) {
      for (const match of script.matches || []) {
        if (match.endsWith("/*")) return match.slice(0, -1);
      }
    }
  } catch (error) {
    return "";
  }
  return "";
}

function isPageSender(sender) {
  const prefix = pagePrefix();
  const url = sender && sender.url;
  return !!prefix && typeof url === "string" && url.startsWith(prefix);
}

function pickMostRecentGuide(tabs) {
  const usable = (tabs || []).filter((tab) => tab && tab.id && isGuideUrl(tab.url));
  if (!usable.length) return null;
  const timed = usable.filter((tab) => typeof tab.lastAccessed === "number");
  if (!timed.length) return usable[0];
  return timed.reduce((best, tab) => (tab.lastAccessed > best.lastAccessed ? tab : best));
}

async function pickGuideTab() {
  const [active] = await chrome.tabs.query({ active: true, lastFocusedWindow: true });
  if (active && isGuideUrl(active.url)) return active;
  const tabs = await chrome.tabs.query({ url: GUIDE_MATCHES });
  return pickMostRecentGuide(tabs);
}

async function readGuide() {
  const tab = await pickGuideTab();
  if (!tab || !tab.id) return { ok: false, error: NO_TAB_MESSAGE };
  await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    world: "MAIN",
    files: ["lib/guide-tab.js"],
  });
  const [injection] = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    world: "MAIN",
    func: () => globalThis.D4.guideTab.extract(),
  });
  const payload = injection && injection.result;
  if (!payload || (!payload.remix && !payload.preloaded)) {
    const seen = (payload && payload.seen) || {};
    const detail =
      Object.entries(seen)
        .map(([key, value]) => key + "=" + value)
        .join(", ") || "page not inspected";
    return { ok: false, error: NO_PAYLOAD_MESSAGE + " (" + detail + ")" };
  }
  return { ok: true, payload };
}

const api = {
  REQUEST_TYPE,
  GUIDE_MATCHES,
  NO_TAB_MESSAGE,
  NO_PAYLOAD_MESSAGE,
  isGuideUrl,
  pagePrefix,
  isPageSender,
  pickMostRecentGuide,
  pickGuideTab,
  readGuide,
};

if (typeof module !== "undefined" && module.exports) {
  module.exports = api;
}
if (typeof globalThis !== "undefined") {
  globalThis.D4 = globalThis.D4 || {};
  globalThis.D4.guideWorker = api;
}

if (typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.onMessage) {
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (!message || message.type !== REQUEST_TYPE) return undefined;
    if (!isPageSender(sender)) {
      sendResponse({ ok: false, error: "This request did not come from the published page." });
      return undefined;
    }
    readGuide().then(sendResponse, (error) => {
      sendResponse({ ok: false, error: (error && error.message) || String(error) });
    });
    return true;
  });
}
})();
