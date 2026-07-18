// Render harness for the Journey door (site/project/index.html).
// Mirrors site/world/_render_harness.mjs: extracts the page's inline <script>,
// runs it against a minimal DOM + inert fetch stub + Chart stub, sets the page's
// own module-level data globals (D/PH/MM/TM/PP/DT), invokes the page's own render
// functions, and prints every captured element's contents as JSON so a test can
// assert on the RENDERED pixels (R11), not the source string.
//
// The page's render functions read module-level globals (renderKpis() etc. take
// no argument and read D, PH, ...), unlike the World door's argument-passing
// functions -- so the harness sets those globals directly on the sandbox.
//
// Usage: node _render_harness.mjs <index.html>
//   stdin: {"dashboard":..., "phases":..., "maturity_map":..., "test_mix":...,
//           "provisional_plan":..., "director_twin":...}
import fs from "node:fs";
import vm from "node:vm";

const htmlPath = process.argv[2];
const html = fs.readFileSync(htmlPath, "utf8");
// The first bare <script> (no attributes) is the page's inline code; the CDN and
// director-comments tags carry a src= attribute so they are skipped by /<script>/.
const m = html.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.error("no inline <script>"); process.exit(2); }
const code = m[1];
const payload = JSON.parse(fs.readFileSync(0, "utf8"));

const elements = {};
function stub(id) {
  const e = { id, _inner: "", _text: "", style: {}, dataset: {},
    classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
    setAttribute() {}, appendChild() {}, options: [], querySelectorAll() { return []; } };
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
// Chart.js is loaded from a CDN on the live page; the render functions that draw
// canvases construct `new Chart(...)`. A no-op stub lets those functions run to
// the point where they set the text pixels we assert on, without a real canvas.
function Chart() { return { destroy() {} }; }
const sandbox = { document, fetch, console, Date, Number, String, Object, Math,
  JSON, Array, Promise, Set, setTimeout() {}, Chart };
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(code, sandbox);

// The page declares `var D=null,PH=null,...` -- set them to the supplied live data,
// then drive the same render sequence the page's Promise.all(...).then does.
sandbox.D = payload.dashboard;
sandbox.PH = payload.phases;
sandbox.MM = payload.maturity_map;
sandbox.TM = payload.test_mix;
sandbox.PP = payload.provisional_plan;
sandbox.DT = payload.director_twin;

sandbox.renderKpis();
sandbox.renderTestMix();
if (sandbox.MM) { sandbox.renderEpoch2Strip(); sandbox.renderMMView(); }
if (sandbox.PP) sandbox.renderProvisionalPlan();
if (sandbox.DT) sandbox.renderDirectorTwin();

const ids = [
  "inv-kpis", "be-domain-count", "epoch2-strip",
  "mm-view-body", "pp-body", "dt-body",
];
const out = {};
for (const id of ids) {
  const e = elements[id];
  out[id] = e ? { innerHTML: e._inner, textContent: e._text } : null;
}
process.stdout.write(JSON.stringify(out));
