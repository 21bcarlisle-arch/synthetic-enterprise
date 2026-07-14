// Render harness for the Director-door (site/director/index.html).
// Extracts the inline <script>, executes it against a minimal DOM + inert fetch
// stub, invokes renderAll(data), and prints every captured element's contents as
// JSON so a test can assert on the RENDERED pixels (R11), not the source string.
//
// Usage: node _render_harness.mjs <index.html>   (combined data JSON on stdin,
//        shape {twin, plan, sys}).
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
  const e = { id, _inner: "", _text: "" };
  Object.defineProperty(e, "innerHTML", { get() { return e._inner; }, set(v) { e._inner = String(v); } });
  Object.defineProperty(e, "textContent", { get() { return e._text; }, set(v) { e._text = String(v); } });
  return e;
}
const document = {
  getElementById(id) { return (elements[id] ||= stub(id)); },
};
// Inert fetch: the inline script ends with Promise.all([fetch...]) — we invoke
// renderAll directly instead, so the fetch chain must stay dormant.
const inert = { then() { return inert; }, catch() { return inert; } };
function fetch() { return inert; }
const Promise_ = { all() { return inert; } };

const sandbox = { document, fetch, console, Date, Number, String, Object, Math, JSON, Promise: Promise_ };
vm.createContext(sandbox);
vm.runInContext(code, sandbox);

sandbox.renderAll(data);

const ids = [
  "ro-banner",
  "twin-intro", "twin-kpis", "twin-passport",
  "queue-intro", "queue-kpis", "queue-body", "queue-passport",
  "qa-intro", "qa-body",
  "plan-intro", "plan-kpis", "plan-body", "plan-passport",
  "curriculum-note",
];
const out = {};
for (const id of ids) {
  const e = elements[id];
  out[id] = e ? { innerHTML: e._inner, textContent: e._text } : null;
}
process.stdout.write(JSON.stringify(out));
