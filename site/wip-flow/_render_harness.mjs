// Render harness for the WIP + Flow door (site/wip-flow/index.html).
// Extracts the inline <script>, runs it against a minimal DOM + inert fetch stub,
// invokes the render functions against the supplied wip_flow.json, and prints
// every captured element's contents as JSON so a test can assert on the RENDERED
// pixels (R11), not just the source data.
//
// Usage: node _render_harness.mjs <index.html>   (wip_flow.json on stdin).
import fs from "node:fs";
import vm from "node:vm";

const htmlPath = process.argv[2];
const html = fs.readFileSync(htmlPath, "utf8");
const m = html.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.error("no inline <script>"); process.exit(2); }
const code = m[1];
const d = JSON.parse(fs.readFileSync(0, "utf8"));

const elements = {};
function stub(id) {
  const e = { id, _inner: "", _text: "", style: {}, classList: { add() {}, remove() {} }, setAttribute() {}, appendChild() {} };
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
sandbox.DATA = d;
sandbox.renderWip(d);
sandbox.renderBuild(d);

const ids = [
  "hero-framing", "kpis", "wip-stages", "wip-lanes",
  "cycle-basis", "cycle-lanes", "throughput-intro", "throughput-summary",
  "throughput-windows", "principle-headline", "principle-body", "dial-note", "build-note",
];
const out = {};
for (const id of ids) {
  const e = elements[id];
  out[id] = e ? { innerHTML: e._inner, textContent: e._text } : null;
}
process.stdout.write(JSON.stringify(out));
