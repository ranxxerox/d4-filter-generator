#!/usr/bin/env node
// Golden harness: loads the actual <script> block from index.html with DOM
// stubs, mutates its state, and prints the web tool's base64 output. The
// Python port must produce identical strings for identical inputs.
"use strict";
const fs = require("fs");
const vm = require("vm");

const htmlPath = process.argv[2];
const input = JSON.parse(process.argv[3]); // {name, norm:2, core:[], sec:[], skills:[]}

const html = fs.readFileSync(htmlPath, "utf8");
const match = html.match(/<script>([\s\S]*?)<\/script>/);
if (!match) {
  console.error("no script block found");
  process.exit(1);
}
const script =
  match[1] +
  `
globalThis.__exports = { buildFilter, DB, SKILLS, state };
`;

const elementStub = (id) => ({
  id,
  value: id === "filterName" ? input.name : id === "goldThreshold" ? String(input.norm) : "",
});
const documentStub = {
  getElementById: (id) => elementStub(id),
  addEventListener: () => {},
  querySelectorAll: () => [],
};

const sandbox = {
  document: documentStub,
  console,
  setTimeout: () => {},
  TextEncoder,
  Uint8Array,
  DataView,
  btoa: (s) => Buffer.from(s, "binary").toString("base64"),
};
vm.createContext(sandbox);
vm.runInContext(script, sandbox, { filename: "index.html.script" });

const state = sandbox.__exports.state;
state.coreStats = new Set(input.core);
state.secondaryStats = new Set(input.sec);
state.skills = new Set(input.skills);

process.stdout.write(sandbox.__exports.buildFilter());
