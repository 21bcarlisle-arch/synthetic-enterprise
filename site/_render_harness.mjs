// Render harness for the Home door (site/index.html).
// Mirrors site/world/_render_harness.mjs: extracts the page's first inline
// <script> (the CDN + director-comments tags carry src= so /<script>/ skips
// them), runs it against a minimal DOM + inert fetch stub + Chart stub, invokes
// the page's OWN render functions against the supplied live site/data JSON, and
// prints every captured element's contents as JSON so a test can assert on the
// RENDERED pixels (R11), not the source string.
//
// Usage: node _render_harness.mjs <index.html>
//   stdin: {"dashboard":..., "supplier":..., "method":..., "lastBill":...}
import fs from "node:fs";
import vm from "node:vm";

const htmlPath = process.argv[2];
const html = fs.readFileSync(htmlPath, "utf8");
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
// The thesis chart constructs `new Chart(...)` and later `.destroy()`s it; a
// no-op stub lets renderThesisChart run to the point where it sets the text
// pixels we assert on, without a real canvas.
function Chart() { return { destroy() {} }; }
const sandbox = { document, fetch, console, Date, Number, String, Object, Math,
  JSON, Array, Promise, Set, setTimeout() {}, encodeURIComponent, Chart };
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(code, sandbox);

// Drive the same render sequence the page's Promise.all(...).then does, with the
// supplied live data (lastBill is optional -- the pulse strip degrades gracefully).
sandbox.renderThesisChart(payload.dashboard);
sandbox.renderPulseStrip(payload.dashboard, payload.supplier, payload.method, payload.lastBill || null);

const ids = [
  "pulse-strip",
  "thesis-sentence", "thesis-caveat", "thesis-evidence",
];
const out = {};
for (const id of ids) {
  const e = elements[id];
  out[id] = e ? { innerHTML: e._inner, textContent: e._text } : null;
}
process.stdout.write(JSON.stringify(out));
