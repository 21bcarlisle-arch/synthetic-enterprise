// Render harness for the Company door (site/company/index.html).
// Extracts the inline <script>, runs it against a minimal DOM + inert fetch stub,
// invokes the page's own render functions against the supplied company.json, and
// prints every captured element's contents as JSON so a test can assert on the
// RENDERED pixels (R11), not the source string.
//
// Usage: node _render_harness.mjs <index.html>   (stdin: EITHER a bare company.json,
//   back-compat, OR a wrapper {company, capabilities, coverage} to inject mutated
//   capability/coverage payloads for R15 independence tests). When not injected,
//   capabilities.json and saas_coverage.json are read from ../data/ on disk.
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";

const htmlPath = process.argv[2];
const html = fs.readFileSync(htmlPath, "utf8");
const m = html.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.error("no inline <script>"); process.exit(2); }
const code = m[1];
const raw = JSON.parse(fs.readFileSync(0, "utf8"));
const d = raw && raw.company ? raw.company : raw;
const dataDir = path.join(path.dirname(htmlPath), "..", "data");
function loadDisk(name) { try { return JSON.parse(fs.readFileSync(path.join(dataDir, name), "utf8")); } catch { return null; } }
const caps = raw && raw.company && "capabilities" in raw ? raw.capabilities : loadDisk("capabilities.json");
const cov = raw && raw.company && "coverage" in raw ? raw.coverage : loadDisk("saas_coverage.json");

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
sandbox.renderCapabilities(caps);
sandbox.renderCoverage(cov);
sandbox.renderState(d);
sandbox.renderFinance(d);
sandbox.renderTrading(d);
sandbox.renderHousehold(d);
sandbox.renderCompliance(d);
sandbox.renderBuild(d);

const ids = [
  "cap-grid", "cap-passport",
  "cov-intro", "cov-kpis", "cov-body", "cov-passport",
  "state-kpis",
  "finance-intro", "finance-kpis", "bridge-intro", "bridge-body", "finance-passport",
  "trading-intro", "trading-kpis", "hedge-body", "trading-passport",
  "hh-intro", "hh-attrs", "hh-kpis", "hh-detail", "hh-passport",
  "oblig-intro", "oblig-kpis", "oblig-body", "tiered-block", "oblig-passport",
  "build-note",
];
const out = {};
for (const id of ids) {
  const e = elements[id];
  out[id] = e ? { innerHTML: e._inner, textContent: e._text } : null;
}
process.stdout.write(JSON.stringify(out));
