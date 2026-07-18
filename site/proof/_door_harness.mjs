// Full-door render harness for the Proof door (site/proof/index.html).
// The panel harness (_render_harness.mjs) drives only renderCoupledGaps; this one
// drives the page's WHOLE render sequence (the same order the page's fetch(...)
// .then(d => ...) runs it) against the supplied live proof.json, so a door-level
// test can assert on the RENDERED pixels (R11) across the door, not one panel.
//
// Usage: node _door_harness.mjs <index.html>   (proof.json on stdin)
import fs from "node:fs";
import vm from "node:vm";

const htmlPath = process.argv[2];
const html = fs.readFileSync(htmlPath, "utf8");
const m = html.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.error("no inline <script> found"); process.exit(2); }
const code = m[1];
const data = JSON.parse(fs.readFileSync(0, "utf8"));

const elements = {};
function stub(id) {
  const e = { id, _inner: "", _text: "", style: {}, dataset: {},
    classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
    setAttribute() {}, appendChild() {} };
  Object.defineProperty(e, "innerHTML", { get() { return e._inner; }, set(v) { e._inner = String(v); } });
  Object.defineProperty(e, "textContent", { get() { return e._text; }, set(v) { e._text = String(v); } });
  return e;
}
const document = {
  getElementById(id) { return (elements[id] ||= stub(id)); },
  querySelector() { return stub("qs"); },
  querySelectorAll() { return []; },
  createElement() { return stub("ce"); },
  addEventListener() {},
};
const inert = { then() { return inert; }, catch() { return inert; } };
function fetch() { return inert; }
const sandbox = { document, fetch, console, Date, Number, String, Object, Math,
  JSON, Array, Set, setTimeout() {} };
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(code, sandbox);

// Same sequence as the page's own fetch(...).then(d => ...).
sandbox.renderPrinciples(data);
sandbox.renderCoupledGaps(data);
sandbox.renderKilllist(data);
sandbox.renderTimeline(data);
sandbox.renderVerification(data);
sandbox.renderOpenWork(data);
sandbox.renderPredictions(data);
sandbox.renderRetros(data);
sandbox.renderBuild(data);

const ids = [
  "timeline-intro", "verify-kpis", "banked-note",
  "openwork-intro", "gap-intro", "gap-kpis",
  "pred-intro", "pred-kpis", "build-note",
];
const out = {};
for (const id of ids) {
  const e = elements[id];
  out[id] = e ? { innerHTML: e._inner, textContent: e._text } : null;
}
process.stdout.write(JSON.stringify(out));
