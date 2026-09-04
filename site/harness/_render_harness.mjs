// Render harness for the harness page.
// Extracts the inline <script>, runs it against a minimal DOM + inert fetch stub, invokes the
// page's own render function named in argv[3] against the JSON on stdin, and prints the captured
// element contents so a test can assert on the RENDERED pixels (R11), not on the source string.
//
// A grep of index.html cannot see this section: `renderDeployment` composes its sentence at
// RUNTIME from the feed, so the words a reader meets exist nowhere in the markup.
//
// Usage: node _render_harness.mjs <index.html> <renderFn> <elementId>   (feed JSON on stdin).
import fs from "node:fs";
import vm from "node:vm";

const htmlPath = process.argv[2];
const fnName = process.argv[3];
const elementId = process.argv[4];
const html = fs.readFileSync(htmlPath, "utf8");
const m = html.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.error("no inline <script>"); process.exit(2); }
const code = m[1];
const d = JSON.parse(fs.readFileSync(0, "utf8"));

const elements = {};
function stub(id) {
  const e = {
    id, _inner: "", _text: "", style: {},
    classList: { add() {}, remove() {} },
    setAttribute() {}, getAttribute() { return ""; },
    addEventListener() {}, appendChild() {}, closest() { return null; },
  };
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
const sandbox = { document, fetch, console, Date, Number, String, Object, Math, JSON, Array, isNaN, setTimeout() {} };
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(code, sandbox);
if (typeof sandbox[fnName] !== "function") { console.error("no such render fn: " + fnName); process.exit(3); }
sandbox[fnName](d);

const e = elements[elementId];
process.stdout.write(JSON.stringify(e ? { innerHTML: e._inner, textContent: e._text } : null));
