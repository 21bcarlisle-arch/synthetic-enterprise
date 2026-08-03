// GENERIC live-door render harness (SITE1_expert_doors, R11 gate (b)).
//
// PURPOSE. Every existing harness in this repo (site/*/_render_harness.mjs,
// site/proof/_door_harness.mjs) is written PER DOOR: it imports the page's inline
// script and then calls that page's render functions BY NAME, in the page's own
// order. That is fine for a door-level unit test, but it cannot be pointed at the
// LIVE site, and it goes stale the moment a door renames a render function.
//
// This harness knows NO function names. It supplies the one thing the page
// actually boots from -- `fetch` -- and lets the door's OWN
// `fetch(...).then(...)` sequence drive itself to completion. Whatever the page
// renders, it renders; we report the resulting element contents.
//
// WHY THAT MATTERS (R11). "Done" for a user-visible surface means asserting the
// value RENDERED on the live surface, not the source string in the repo. Driving
// the LIVE html with the LIVE json reproduces exactly what a browser hitting
// poesys.net puts on screen, including the failure everyone actually ships: page
// deploys fine, its json 404s or drifts schema, and every panel sits on
// "Loading..." or "Could not load x.json" forever. A source-string test passes
// happily through that. This does not.
//
// FAIL-CLOSED (R15). A url the caller did not supply REJECTS, exactly as a 404
// would live -- it is never silently resolved to {} . That keeps the page's own
// `.catch()` branches on their real path, so a missing feed shows up as the
// door's rendered error text rather than as a vacuous pass.
//
// Usage: node _live_harness.mjs <door.html>
//   stdin:  {"../data/proof.json": <payload>, ...}   (url as written in the page)
//   stdout: {"<elementId>": {"innerHTML": "...", "textContent": "..."}, ...}
import fs from "node:fs";
import vm from "node:vm";

const htmlPath = process.argv[2];
if (!htmlPath) { console.error("usage: _live_harness.mjs <door.html>"); process.exit(2); }
const html = fs.readFileSync(htmlPath, "utf8");

// A door may carry several inline <script> blocks; concatenate them in document
// order so helpers defined in one are visible to the boot code in another.
const scripts = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)]
  .map((m) => m[1]).filter((s) => s.trim());

// A door with no inline script is not an error -- the Front Door and /privacy/ are
// deliberately static, server-rendered pages with nothing to drive. Report that fact
// and let the caller judge such a door on its SERVED markup instead of erroring out.
// (Treating "static" as "broken" here is what made the first live run report a false
// failure on the Front Door.)
if (!scripts.length) {
  process.stdout.write(JSON.stringify({
    _meta: { static: true, requested: [], unresolved: [], scriptError: null },
  }));
  process.exit(0);
}

const feeds = JSON.parse(fs.readFileSync(0, "utf8"));
// Pages cache-bust with `?t=`+Date.now(); match on the path, ignoring the query.
const bare = (u) => String(u).split("?")[0];
const table = new Map(Object.entries(feeds).map(([k, v]) => [bare(k), v]));

const requested = [];
const unresolved = [];
function fetch(url) {
  const key = bare(url);
  requested.push(key);
  if (!table.has(key)) {
    unresolved.push(key);
    // Reject, do NOT resolve-to-empty: a feed we could not fetch must drive the
    // page down its real error path, never a vacuous success.
    return Promise.reject(new Error("live harness: no payload supplied for " + key));
  }
  const payload = table.get(key);
  return Promise.resolve({
    ok: true, status: 200, url,
    json: () => Promise.resolve(payload),
    text: () => Promise.resolve(JSON.stringify(payload)),
  });
}

const elements = {};
const domReady = {};
function stub(id) {
  const e = {
    id, _inner: "", _text: "", style: {}, dataset: {}, children: [],
    classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
    setAttribute() {}, removeAttribute() {}, getAttribute() { return null; },
    appendChild(c) { e.children.push(c); return c; },
    addEventListener() {}, removeEventListener() {}, focus() {}, scrollIntoView() {},
    insertAdjacentHTML(_pos, h) { e._inner += String(h); },
    querySelector() { return stub(id + " >qs"); },
    querySelectorAll() { return []; },
  };
  Object.defineProperty(e, "innerHTML", { get() { return e._inner; }, set(v) { e._inner = String(v); } });
  Object.defineProperty(e, "textContent", { get() { return e._text; }, set(v) { e._text = String(v); } });
  Object.defineProperty(e, "innerText", { get() { return e._text; }, set(v) { e._text = String(v); } });
  return e;
}

const document = {
  getElementById(id) { return (elements[id] ||= stub(id)); },
  querySelector(sel) { return (elements["sel:" + sel] ||= stub("sel:" + sel)); },
  querySelectorAll() { return []; },
  createElement(tag) { return stub("new:" + tag); },
  createTextNode() { return stub("text"); },
  // Doors that boot on DOMContentLoaded (e.g. /glossary/) render NOTHING if this is a
  // no-op, and the verifier then reports a perfectly healthy door as blank. Capture the
  // listeners; they are fired below once every script block has been evaluated, which
  // is the order a real browser uses.
  addEventListener(type, fn) { if (typeof fn === "function") (domReady[type] ||= []).push(fn); },
  readyState: "loading",
  body: stub("body"),
  documentElement: stub("html"),
};

const sandbox = {
  document, fetch, console: { log() {}, warn() {}, error() {} },
  Date, Number, String, Object, Math, JSON, Array, Set, Map, Promise, Boolean,
  RegExp, Error, isNaN, isFinite, parseInt, parseFloat, encodeURIComponent, decodeURIComponent,
  URLSearchParams, URL, Intl, TextDecoder, TextEncoder, structuredClone,
  setTimeout(fn) { return setTimeout(fn, 0); }, clearTimeout,
  requestAnimationFrame(fn) { return setTimeout(fn, 0); },
  location: { hash: "", href: "https://poesys.net/", pathname: "/" },
  history: { replaceState() {}, pushState() {} },
  localStorage: { getItem() { return null; }, setItem() {}, removeItem() {} },
  navigator: { userAgent: "live-pixel-verify" },
};
sandbox.window = sandbox;
sandbox.globalThis = sandbox;
vm.createContext(sandbox);

let scriptError = null;
for (const code of scripts) {
  try {
    vm.runInContext(code, sandbox, { timeout: 20000 });
  } catch (e) {
    // Record and continue: one broken block should not hide what the others rendered.
    scriptError = scriptError || String(e && e.message || e);
  }
}

// Fire the deferred document-ready listeners, now that every inline block has been
// evaluated -- the same point a browser fires them.
document.readyState = "complete";
for (const type of ["DOMContentLoaded", "load", "readystatechange"]) {
  for (const fn of domReady[type] || []) {
    try { fn({ type }); } catch (e) { scriptError = scriptError || String(e && e.message || e); }
  }
}

// Let the page's own promise chains settle. Each pass drains the microtask queue
// AND one macrotask turn, so `.then` cascades and setTimeout-deferred renders both
// complete. Bounded, so a page that never settles cannot hang the verifier.
for (let i = 0; i < 40; i++) {
  await new Promise((r) => setTimeout(r, 0));
}

const out = { _meta: { requested, unresolved, scriptError } };
for (const [id, e] of Object.entries(elements)) {
  out[id] = { innerHTML: e._inner, textContent: e._text };
}
process.stdout.write(JSON.stringify(out));
