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
// Usage: node _freshness_harness.mjs <freshness-banner.js> [data-figures]
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
// THE INCLUDING SCRIPT TAG. The layer reads `document.currentScript` at load so a REFERENCE
// page can declare `data-figures="none"` and opt out of a freshness claim about figures it does
// not have. Supplying it here is supplying an input the asset already reads -- the same shape as
// the feeds above -- and without it that branch is untestable and would ship unexercised.
const currentScript = {
  getAttribute(name) {
    return name === "data-figures" ? (process.argv[3] || null) : null;
  },
};

const document = {
  head,
  body,
  readyState: "complete",
  currentScript,
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

// THE READER'S CLOCK IS AN INPUT, SO IT HAS TO BE SUPPLIABLE.
//
// The layer's frozen-feed check is the one verdict it does NOT read out of the feed: it asks the
// clock in front of the reader how long ago the feed was written. A control for it that used the
// real `Date.now()` would be keyed to today's answer -- green today, and quietly meaningless the
// day the fixture dates fall out of range. `POESYS_FRESHNESS_NOW` makes that clock a fixture like
// the feeds themselves.
//
// UNSET IS THE INTRINSIC DATE, deliberately: `vm.createContext` gives the context its own real
// `Date`, so every test written before this one keeps the clock it already had and this shim is
// invisible to them.
const NOW_OVERRIDE = process.env.POESYS_FRESHNESS_NOW || null;

const sandbox = {
  document,
  fetch: fetchImpl,
  URL,
  Promise,
  console: { warn() {}, log() {}, error() {} },
  String, Object, Array, JSON, Math, Number, Boolean, Error,
  location: { origin: "https://poesys.net" },
};
if (NOW_OVERRIDE !== null) {
  const fixed = Date.parse(NOW_OVERRIDE);
  if (Number.isNaN(fixed)) {
    console.error("POESYS_FRESHNESS_NOW is not a parseable instant: " + NOW_OVERRIDE);
    process.exit(2);
  }
  // `parse` stays the real one -- only NOW is under the fixture's control. Substituting the whole
  // of Date would make the layer's date ARITHMETIC a property of this harness, which is the
  // opposite of what a control wants to establish.
  sandbox.Date = { now: () => fixed, parse: (s) => Date.parse(s), UTC: Date.UTC };
}

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
