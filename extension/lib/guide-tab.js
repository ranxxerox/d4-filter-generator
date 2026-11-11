(function () {
// Reads a guide page's embedded payload from its main world. Shared by the
// popup and the background worker so both return the same shape.
// CommonJS-compatible for node tests.
"use strict";

function extract() {
  const remix = globalThis.__remixContext ?? null;
  const preloaded = globalThis.__PRELOADED_STATE__ ?? null;
  return {
    remix: remix ? JSON.parse(JSON.stringify(remix)) : null,
    preloaded: preloaded ? JSON.parse(JSON.stringify(preloaded)) : null,
    seen: {
      remixContext: typeof globalThis.__remixContext,
      preloadedState: typeof globalThis.__PRELOADED_STATE__,
    },
    href: (globalThis.location && globalThis.location.href) || "",
  };
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { extract };
}
if (typeof globalThis !== "undefined") {
  globalThis.D4 = globalThis.D4 || {};
  globalThis.D4.guideTab = { extract };
}
})();
