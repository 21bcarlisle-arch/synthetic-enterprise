// Render harness for the Evidence surface (site/evidence/index.html).
// Extracts the page's own inline <script>, runs it against a minimal DOM + inert fetch stub,
// invokes renderEvidence() against the supplied moap_evidence.json, and prints every captured
// container's contents as JSON -- so a test asserts the RENDERED value (R11), never the source
// string or the JSON it came from.
//
// Usage: node _render_harness.mjs <index.html>   (moap_evidence.json on stdin).
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
  JSON, Array, Set, isFinite, setTimeout() {} };
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(code, sandbox);

sandbox.renderEvidence(data);

// Every element the page's render actually touched -- the fixed containers (ev-summary,
// ev-provenance) plus one ev-node-<id> slot per node section, so a test can assert per-node
// rendered pixels without this harness carrying its own list of node ids.
const out = {};
for (const id of Object.keys(elements)) {
  const e = elements[id];
  out[id] = { innerHTML: e._inner, textContent: e._text };
}
// "ev-nodes" is the union of every node slot, for whole-surface assertions.
out["ev-nodes"] = {
  innerHTML: Object.keys(elements)
    .filter((k) => k.startsWith("ev-node-"))
    .map((k) => elements[k]._inner)
    .join(""),
  textContent: "",
};
process.stdout.write(JSON.stringify(out));
