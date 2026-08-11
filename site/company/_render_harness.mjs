// Render harness for the Company door (site/company/index.html).
// Extracts the inline <script>, runs it against a minimal DOM + inert fetch stub,
// invokes the page's own render functions against the supplied company.json, and
// prints every captured element's contents as JSON so a test can assert on the
// RENDERED pixels (R11), not the source string.
//
// Usage: node _render_harness.mjs <index.html>   (stdin: EITHER a bare company.json,
//   back-compat, OR a wrapper {company, capabilities, coverage, world} to inject
//   mutated capability/coverage/world payloads for R15 independence tests). When
//   not injected, capabilities.json / saas_coverage.json / decisions.json /
//   world.json are read from ../data/ on disk.
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
const decs = raw && raw.company && "decisions" in raw ? raw.decisions : loadDisk("decisions.json");
const world = raw && raw.company && "world" in raw ? raw.world : loadDisk("world.json");

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
// THE HARNESS MAY NOT SUPPLY A CALL THE PAGE DOES NOT MAKE (R15, 2026-08-11).
// This list was hand-typed and included `renderBookMix(d)` while the page itself never
// called it -- so three door tests asserted rendered pixels for a panel that served
// "Loading..." on the live site for 8 days. The control was a producer of the very
// evidence it graded. Now the ARGUMENTS stay declared here (the harness is the only
// thing that knows which payload each function eats) but the CALL SET is derived from
// the page's own boot path, and a mismatch in either direction is fatal.
const ARGS = {
  renderCapabilities: () => [caps],
  renderCoverage: () => [cov],
  renderDecisions: () => [decs],
  renderBookMix: () => [d],
  renderState: () => [d],
  renderFinance: () => [d, world],
  renderTrading: () => [d],
  renderWholesale: () => [d],
  renderHousehold: () => [d],
  renderCompliance: () => [d],
  renderBuild: () => [d],
};
const defined = [...code.matchAll(/^\s*function\s+(render[A-Za-z0-9_]*)\s*\(/gm)].map((m) => m[1]);
const invoked = defined.filter((fn) => {
  const direct = [...code.matchAll(new RegExp(`\\b${fn}\\s*\\(`, "g"))]
    .some((m) => !code.slice(0, m.index).trimEnd().endsWith("function"));
  const byRef = new RegExp(`[=,(\\[]\\s*${fn}\\s*[,)\\]]`).test(code);
  return direct || byRef;
});
const orphans = defined.filter((fn) => !invoked.includes(fn));
if (orphans.length) {
  console.error(`page defines but never invokes: ${orphans.join(", ")}`);
  process.exit(3);
}
const unfed = invoked.filter((fn) => !(fn in ARGS));
if (unfed.length) {
  console.error(`page invokes render fns this harness cannot feed: ${unfed.join(", ")}`);
  process.exit(4);
}
for (const fn of invoked) sandbox[fn](...ARGS[fn]());

const ids = [
  "mix-intro", "mix-kpis", "mix-note",
  "cap-grid", "cap-passport",
  "cov-intro", "cov-kpis", "cov-body", "cov-passport",
  "state-kpis", "state-decisions",
  "finance-intro", "finance-kpis", "finance-unit-note", "cost-to-serve-dist", "arrears-dist", "credit-cycle", "bridge-intro", "bridge-body", "finance-passport",
  "trading-intro", "trading-kpis", "hedge-body", "trading-passport",
  "wholesale-intro", "wholesale-kpis", "wholesale-cp-body", "wholesale-passport",
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
