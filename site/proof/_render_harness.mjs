// Render harness for the Proof-door coupled-triad gap panel.
// Extracts the inline <script> from index.html, executes it against a minimal
// DOM + fetch stub, invokes renderCoupledGaps(data), and prints the resulting
// element contents as JSON so a test can assert on the RENDERED pixels (R11).
//
// Usage: node _render_harness.mjs <index.html>   (data JSON on stdin)
import fs from "node:fs";
import vm from "node:vm";

const htmlPath = process.argv[2];
const html = fs.readFileSync(htmlPath, "utf8");

// Grab the inline script block (the one without a src=).
const m = html.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.error("no inline <script> found"); process.exit(2); }
const code = m[1];

// Read the render data from stdin.
const data = JSON.parse(fs.readFileSync(0, "utf8"));

// Minimal DOM: every element is a stub whose innerHTML/textContent we capture.
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
// fetch stub: the inline script ends with a top-level fetch(...).then().then().catch();
// return a self-chaining thenable that never invokes callbacks so eval stays inert.
const inert = { then() { return inert; }, catch() { return inert; } };
function fetch() { return inert; }

const sandbox = { document, fetch, console, Date, Number, String, Object, Math, JSON };
vm.createContext(sandbox);
vm.runInContext(code, sandbox);

// Invoke the panel render directly with the supplied data.
sandbox.renderCoupledGaps(data);

const out = {};
for (const id of ["gap-intro", "gap-kpis", "gap-alarms", "coupled-gaps"]) {
  const e = elements[id];
  out[id] = e ? { innerHTML: e._inner, textContent: e._text } : null;
}
process.stdout.write(JSON.stringify(out));
