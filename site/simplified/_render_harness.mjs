// Render harness for the Simplified door (site/simplified/index.html).
// Extracts the inline <script>, runs it against a minimal DOM + inert fetch stub,
// invokes the page's own render helpers against the supplied simplified.json, and
// prints every captured element's contents as JSON so a test can assert on the
// RENDERED pixels (R11), not the source string.
//
// Usage: node _render_harness.mjs <index.html>   (simplified.json on stdin).
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

// The page's own fetch callback (not a standalone render fn) does exactly this;
// mirror it so the harness exercises the page's real renderLane() per lane.
document.getElementById("stats-line").innerHTML =
  "<strong>" + d.total_notes + "</strong> recorded simplification" + (d.total_notes === 1 ? "" : "s") +
  " across <strong>" + d.total_atoms_with_notes + "</strong> capabilit" + (d.total_atoms_with_notes === 1 ? "y" : "ies") +
  " in <strong>" + d.lanes.length + "</strong> lanes.";
const lanesOut = document.getElementById("lanes-out");
lanesOut.innerHTML = d.lanes.length ? d.lanes.map(sandbox.renderLane).join("") : '<div class="empty">No simplifications recorded.</div>';

const ids = ["stats-line", "lanes-out"];
const out = {};
for (const id of ids) {
  const e = elements[id];
  out[id] = e ? { innerHTML: e._inner, textContent: e._text } : null;
}
process.stdout.write(JSON.stringify(out));
