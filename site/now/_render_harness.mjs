// Render harness for the Now door (site/now/index.html) -- the operational window.
// Extracts the inline <script>, runs it against a minimal DOM + inert fetch stub
// (so the page's own auto-boot Promise.all does NOT fire), then invokes the page's
// OWN render functions against the supplied JSON and prints every captured element's
// contents so a test can assert on the RENDERED pixels (R11), not the source string.
//
// Usage: node _render_harness.mjs <index.html> [weather.json] [market.json] [decisions.json]
//        company.json is read from stdin (the primary source).
import fs from "node:fs";
import vm from "node:vm";

const htmlPath = process.argv[2];
const html = fs.readFileSync(htmlPath, "utf8");
const m = html.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.error("no inline <script>"); process.exit(2); }
const code = m[1];

const company = JSON.parse(fs.readFileSync(0, "utf8"));
const weather = process.argv[3] ? JSON.parse(fs.readFileSync(process.argv[3], "utf8")) : null;
const market = process.argv[4] ? JSON.parse(fs.readFileSync(process.argv[4], "utf8")) : null;
const decisions = process.argv[5] ? JSON.parse(fs.readFileSync(process.argv[5], "utf8")) : null;

const elements = {};
function stub(id) {
  const e = { id, _inner: "", _text: "", className: "", style: {}, classList: { add() {}, remove() {} }, setAttribute() {}, appendChild() {} };
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
const sandbox = { document, fetch, console, Date, Number, String, Object, Math, JSON, Array, setTimeout() {} };
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(code, sandbox);

sandbox.renderStamp(company, weather, market);
sandbox.renderPanelWorld(weather, market);
sandbox.renderPanelSupplier(company, decisions);
sandbox.renderPanelCustomer(company);
sandbox.renderPanelCarbon(company);
sandbox.renderBuild(company);

const ids = [
  "stamp",
  "p1-pill", "p1-lag", "p1-metrics", "p1-sowhat",
  "p2-pill", "p2-metrics", "p2-decision", "p2-sowhat",
  "p3-pill", "p3-selector", "p3-metrics", "p3-chips", "p3-sowhat",
  "p4-body",
  "build-note",
];
const out = {};
for (const id of ids) {
  const e = elements[id];
  out[id] = e ? { innerHTML: e._inner, textContent: e._text } : null;
}
process.stdout.write(JSON.stringify(out));
