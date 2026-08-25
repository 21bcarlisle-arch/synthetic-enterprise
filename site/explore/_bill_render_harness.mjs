// Render harness for the PRINTED BILL (site/explore/index.html, atom D36).
//
// This page has a GENERIC live harness already (site/_live_harness.mjs), which boots the door
// against real feeds and reports what each element rendered. That one answers "does the page
// come up and show the right thing for the household it opened on". It cannot answer D36's
// question, which is about a POPULATION: every bill on every account must add up as printed,
// and the stage renders one bill per household. So this harness drives the page's own
// `billEquationHtml()` across all of them -- 10,239 bills at the time of writing, of which 796
// carry a catch-up adjustment.
//
// Why it runs the page's own code instead of re-implementing the renderer: the defect D36
// closes is a RENDER defect. The record for bill C1g-INV141 was correct and passed BILL_FOOTS;
// the PAGE printed four of its five components, each rounded to whole pounds, above a total of
// -£2.43 that none of them explained. A checker that read the ledger and added it up would have
// passed while the page was unreadable. A checker that re-implemented the renderer would drift
// from the page and pass while the page failed -- the tautology shape R15 names.
//
// RE-HOMED 2026-08-25 from site/customers/_bill_render_harness.mjs. That file, the page it
// drove, and therefore this whole control were deleted together on 2026-08-20 when eleven pages
// became five tabs; D36's nineteen assertions errored at fixture setup for five days while the
// bill Explore inherited quietly went back to printing four lines above a total they did not sum
// to. The PDF half of the old harness is NOT restored, because /explore/ has no PDF download to
// drive -- see test_the_pdf_half_of_this_control_is_withdrawn_not_passing, which fails if a PDF
// path returns to the page without a control coming back with it.
//
// Usage: node _bill_render_harness.mjs <index.html> <customer.json> [customer.json ...]
// Prints JSON: { accounts: [{account, path, invoices: [{id, screen}]}] }
import fs from "node:fs";
import vm from "node:vm";

const [, , htmlPath, ...dataPaths] = process.argv;
const html = fs.readFileSync(htmlPath, "utf8");
const scripts = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)]
  .map((m) => m[1]).filter((s) => s.trim());
if (!scripts.length) { console.error("no inline <script> block to drive"); process.exit(2); }

function stub(id) {
  const e = {
    id, _inner: "", _text: "", style: {}, dataset: {},
    classList: { add() {}, remove() {} },
    setAttribute() {}, appendChild() {}, scrollIntoView() {}, focus() {},
    getContext() { return {}; },
  };
  Object.defineProperty(e, "innerHTML", { get() { return e._inner; }, set(v) { e._inner = String(v); } });
  Object.defineProperty(e, "textContent", { get() { return e._text; }, set(v) { e._text = String(v); } });
  return e;
}
const elements = {};
const document = {
  readyState: "complete",
  getElementById(id) { return (elements[id] ||= stub(id)); },
  querySelector() { return stub("qs"); },
  querySelectorAll() { return []; },
  createElement() { return stub("ce"); },
  addEventListener() {},
};
// The page's boot code is a chain of top-level `fetch(...).then(...)`. An inert thenable lets
// the script DEFINE its render functions without any of its feeds having to exist -- the feeds
// are the generic live harness's job, not this one's.
const inert = { then() { return inert; }, catch() { return inert; } };

const sandbox = {
  document, console, Date, Number, String, Object, Math, JSON, Array, isNaN, isFinite,
  fetch: () => inert, setTimeout() {}, alert() {},
  location: { search: "", hash: "" },
  history: { replaceState() {} },
  URLSearchParams: globalThis.URLSearchParams,
  Promise,
};
sandbox.window = sandbox;
vm.createContext(sandbox);
for (const s of scripts) vm.runInContext(s, sandbox);

if (typeof sandbox.billEquationHtml !== "function") {
  // FAIL-CLOSED (R15). If the bill renderer is renamed or deleted again, this harness must say
  // so loudly rather than emit an empty population that every assertion passes over.
  console.error("billEquationHtml() is not defined by the page -- the bill renderer is gone");
  process.exit(3);
}

const accounts = [];
for (const p of dataPaths) {
  const d = JSON.parse(fs.readFileSync(p, "utf8"));
  if (!d || !Array.isArray(d.invoices)) continue;
  const account = d.account_id || d.base_account_id;
  const invoices = [];
  for (const inv of d.invoices) invoices.push({ id: inv.id, screen: sandbox.billEquationHtml(inv) });
  accounts.push({ account, path: p, invoices });
}
process.stdout.write(JSON.stringify({ accounts }));
