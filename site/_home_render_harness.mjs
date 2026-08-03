// Render harness for the Home door (site/index.html) -- SITE_EH1_segment_disclosure.
// Mirrors site/company/_render_harness.mjs's pattern (Node/vm, run the page's own
// inline <script> against real JSON, capture the rendered element) but scoped to the
// ONE dynamic render this door carries: the composition-disclosure sentence
// (renderComposition -> #composition-note). Everything else on this door is static
// prose (test_home_door.py's structural scans cover that), so this harness only needs
// to prove the ONE new fetch-and-render is real (R11), not a hardcoded string.
//
// Usage: node _home_render_harness.mjs <index.html>   (stdin: company.json, EITHER the
//   real file or a mutated payload for R15 independence tests).
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
  const e = { id, _inner: "" };
  Object.defineProperty(e, "innerHTML", { get() { return e._inner; }, set(v) { e._inner = String(v); } });
  return e;
}
const document = { getElementById(id) { return (elements[id] ||= stub(id)); } };
const inert = { then() { return inert; }, catch() { return inert; } };
function fetch() { return inert; }
const sandbox = { document, fetch, console, Date, Number, String, Object, Math, JSON, Array };
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(code, sandbox);
sandbox.renderComposition(d);

const out = {};
for (const id of ["composition-note"]) {
  const e = elements[id];
  out[id] = e ? { innerHTML: e._inner } : null;
}
process.stdout.write(JSON.stringify(out));
