(function () {
// Content script for the published site: marks the page so it can detect the
// extension, then relays guide-read requests from the page to the service
// worker and posts the answer back. Requests from other origins, other
// sources, or other channels are ignored.
"use strict";

const CHANNEL_PAGE = "d4filter-page";
const CHANNEL_EXTENSION = "d4filter-extension";
const REQUEST_TYPE = "read-guide";
const REPLY_TYPE = "guide";

function isGuideRequest(event, expectedOrigin, expectedSource) {
  if (!event || event.origin !== expectedOrigin) return false;
  if (event.source !== expectedSource) return false;
  const data = event.data;
  return (
    !!data &&
    typeof data === "object" &&
    data.source === CHANNEL_PAGE &&
    data.type === REQUEST_TYPE
  );
}

function reply(payload) {
  try {
    window.postMessage(
      Object.assign({ source: CHANNEL_EXTENSION, type: REPLY_TYPE }, payload),
      location.origin
    );
  } catch (error) {
    // A page that navigated away mid-request has nothing to receive it.
  }
}

function handleMessage(event) {
  if (!isGuideRequest(event, location.origin, window)) return;
  let pending;
  try {
    pending = chrome.runtime.sendMessage({ type: "d4filter:read-guide" });
  } catch (error) {
    reply({
      ok: false,
      payload: null,
      error: "The extension was reloaded. Reload this page, then try again.",
    });
    return;
  }
  pending.then(
    (answer) => {
      reply({
        ok: !!(answer && answer.ok),
        payload: (answer && answer.payload) || null,
        error: (answer && answer.error) || (answer ? "" : "The extension did not answer."),
      });
    },
    (error) => {
      reply({ ok: false, payload: null, error: (error && error.message) || String(error) });
    }
  );
}

function announce() {
  document.documentElement.dataset.d4filterExtension = chrome.runtime.getManifest().version;
}

const api = { CHANNEL_PAGE, CHANNEL_EXTENSION, REQUEST_TYPE, isGuideRequest, announce };

if (typeof module !== "undefined" && module.exports) {
  module.exports = api;
}
if (typeof globalThis !== "undefined") {
  globalThis.D4 = globalThis.D4 || {};
  globalThis.D4.contentPages = api;
}

if (
  typeof document !== "undefined" &&
  typeof window !== "undefined" &&
  typeof chrome !== "undefined" &&
  chrome.runtime
) {
  announce();
  window.addEventListener("message", handleMessage);
}
})();
