// Render harness for the Customers door operational-state panel (site/customers/index.html).
// Extracts the FIRST inline <script> (the self-contained state panel, deliberately placed
// before the drill-down portal script), runs it against a minimal DOM + inert fetch stub,
// invokes the panel's own render functions against the supplied company.json, and prints every
// captured element's contents as JSON so a test can assert on the RENDERED pixels (R11), not the
// source string.
//
// Usage: node _render_harness.mjs <index.html> [leg.json ...]   (company.json on stdin).
//
// The optional leg files are the household's per-fuel records (site/data/customers/<id>.json),
// electricity leg FIRST -- what the page's own boot path fetches after company.json so the
// money panels can be the household's rather than one fuel leg's
// (coldwalk:site2_dual_fuel_household_shows_electricity_only_money). They are handed to the
// page's OWN __assembleLegs() rather than shaped here: the "how many legs should this
// household have" rule is the page's, and a harness that re-typed it would be grading its own
// copy of the logic (the tautology shape site/test_door_render_functions_are_wired.py exists
// for). Passing FEWER legs than the household has is a supported fixture -- it drives the
// leg-scoped fallback, which is the half of the control that can actually fail.
import fs from "node:fs";
import vm from "node:vm";

const htmlPath = process.argv[2];
const html = fs.readFileSync(htmlPath, "utf8");
// First attribute-less <script> block == the state panel (CDN tags carry src=, portal is later).
const m = html.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.error("no inline <script>"); process.exit(2); }
const code = m[1];
const company = JSON.parse(fs.readFileSync(0, "utf8"));

const elements = {};
function stub(id) {
  const e = { id, _inner: "", _text: "", style: {}, classList: { add() {}, remove() {} }, setAttribute() {}, appendChild() {} };
  Object.defineProperty(e, "innerHTML", { get() { return e._inner; }, set(v) { e._inner = String(v); } });
  Object.defineProperty(e, "textContent", { get() { return e._text; }, set(v) { e._text = String(v); } });
  return e;
}
const document = {
  readyState: "complete",
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
const legRecords = process.argv.slice(3).map((p) => JSON.parse(fs.readFileSync(p, "utf8")));
const legs = legRecords.length ? sandbox.__assembleLegs(legRecords) : null;
sandbox.renderCustomerState(company, legs);
sandbox.renderCustomerCarbon(company);

const ids = [
  "cust-stamp", "cust-intro", "cust-who", "cust-classify", "cust-money", "cust-value", "cust-sim",
  "cust-dd-cycle", "cust-arrears", "cust-money-basis", "cust-carbon",
];
const out = {};
for (const id of ids) {
  const e = elements[id];
  out[id] = e ? { innerHTML: e._inner, textContent: e._text } : null;
}
process.stdout.write(JSON.stringify(out));
