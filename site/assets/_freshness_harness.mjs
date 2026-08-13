// Harness for the FRESHNESS BANNER layer (site/assets/freshness-banner.js).
//
// Same reasoning as glossary/_layer_harness.mjs: the banner's whole job happens in a DOM and in a
// pair of fetches, so a source-string assertion proves nothing about what a visitor sees. This
// drives the REAL asset against a minimal DOM with controlled feeds and reports the element it
// actually produced -- its state attribute and its rendered text.
//
// FAIL-CLOSED (R15): a url the caller did not supply REJECTS, exactly as a 404 would live. That
// keeps the layer's own .catch() branches on their real path, so a missing feed shows up as the
// rendered UNKNOWN banner rather than as a vacuous pass.
//
// Usage: node _freshness_harness.mjs <freshness-banner.js>
//   stdin:  {"/data/publish_provenance.json": <payload|null>,
//            "/data/tick_heartbeat.json": <payload|null>}     (null = 404)
//   stdout: {"state": "...", "text": "...", "html": "...", "error": null|"..."}
import fs from "node:fs";
import vm from "node:vm";

const assetPath = process.argv[2];
if (!assetPath) { console.error("usage: _freshness_harness.mjs <freshness-banner.js>"); process.exit(2); }
const feeds = JSON.parse(fs.readFileSync(0, "utf8"));

function textOf(html) {
  return String(html).replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim();
}

const created = [];
function makeElement(tag) {
  return {
    tagName: String(tag).toUpperCase(),
    _attrs: {},
    className: "",
    innerHTML: "",
    textContent: "",
    setAttribute(k, v) { this._attrs[k] = String(v); },
    getAttribute(k) { return this._attrs[k] ?? null; },
    appendChild() {},
  };
}

const head = { appendChild() {} };
const body = { firstChild: null, insertBefore(node) { created.push(node); } };
const document = {
  head,
  body,
  readyState: "complete",
  createElement: makeElement,
  addEventListener(_, fn) { fn(); },
};

// The layer resolves both feeds with `new URL(path, window.location.origin)`, so key the fixture
// by pathname -- the caller supplies paths, never fully-qualified urls.
function fetchImpl(url) {
  const path = new URL(url).pathname;
  if (!(path in feeds)) {
    return Promise.reject(new Error("no fixture for " + path));
  }
  const payload = feeds[path];
  if (payload === null) {
    return Promise.resolve({ ok: false, status: 404, json: () => Promise.reject(new Error("404")) });
  }
  return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve(payload) });
}

const sandbox = {
  document,
  fetch: fetchImpl,
  URL,
  Promise,
  console: { warn() {}, log() {}, error() {} },
  String, Object, Array, JSON, Math, Number, Boolean, Error,
  location: { origin: "https://poesys.net" },
};
sandbox.window = sandbox;
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(assetPath, "utf8"), sandbox);

// The layer boots through two chained promises; let the microtask queue drain before reporting.
await new Promise((r) => setTimeout(r, 0));
await new Promise((r) => setTimeout(r, 0));

const bar = created[0];
process.stdout.write(JSON.stringify({
  state: bar ? bar.getAttribute("data-freshness-state") : null,
  html: bar ? bar.innerHTML : null,
  text: bar ? textOf(bar.innerHTML) : null,
  error: sandbox.PoesysFreshness ? sandbox.PoesysFreshness.error : "layer did not install",
}));
