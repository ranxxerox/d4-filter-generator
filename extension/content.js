// Content script: forwards the page's embedded guide payload to the popup.
// The embedded state objects live in the page's JS world, so an injected
// <script> posts them back via postMessage; this script relays to the
// extension runtime.
"use strict";

const PAGE_SOURCE_REQUEST = "d4filter:request-guide-source";
const PAGE_SOURCE_RESPONSE = "d4filter:guide-source";

function injectPageHook() {
  const script = document.createElement("script");
  script.textContent = `
    (function () {
      var send = function () {
        var payload = {};
        if (window.__remixContext) payload.remixContext = JSON.stringify(window.__remixContext);
        if (window.__PRELOADED_STATE__) payload.preloadedState = JSON.stringify(window.__PRELOADED_STATE__);
        window.postMessage({ type: "${PAGE_SOURCE_RESPONSE}", payload: payload }, window.location.origin);
      };
      window.addEventListener("message", function (event) {
        if (event.source === window && event.data && event.data.type === "${PAGE_SOURCE_REQUEST}") send();
      });
      send();
    })();
  `;
  (document.head || document.documentElement).appendChild(script);
  script.remove();
}

injectPageHook();

let latestSource = null;
window.addEventListener("message", (event) => {
  if (event.source !== window) return;
  if (event.data && event.data.type === PAGE_SOURCE_RESPONSE) {
    latestSource = event.data.payload || {};
  }
});

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message && message.type === "d4filter:get-guide") {
    // Re-request in case the SPA updated its state after load.
    window.postMessage({ type: PAGE_SOURCE_REQUEST }, window.location.origin);
    setTimeout(() => sendResponse({ ok: true, source: latestSource, url: location.href }), 150);
    return true;
  }
});
