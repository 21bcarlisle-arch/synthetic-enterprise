// Render harness for the PRINTED BILL (site/customers/index.html, atom D36).
//
// The wall exhibit has its own harness (_wall_harness.mjs) and the top-of-page
// operational panel has another (_render_harness.mjs). This one drives the BILL
// path -- billEquationHtml() on screen and downloadBillPdf() into a captured
// jsPDF -- so a test can assert on the RENDERED figures (R11) rather than on the
// JSON behind them.
//
// Why it runs the page's own code instead of re-implementing the renderer: the
// defect D36 closes was a RENDER defect. The record for bill C1g-INV141 was
// correct and passed BILL_FOOTS; the PAGE printed four of its five components,
// each rounded to whole pounds, above a total of -£2 that none of them explained.
// A checker that read the ledger and added it up would have passed while the
// page was unreadable. A checker that re-implemented the renderer would drift
// from the page and pass while the page failed -- the tautology shape R15 names.
//
// Usage: node _bill_render_harness.mjs <index.html> <customer.json> [customer.json ...]
// Prints JSON: { accounts: [{account, invoices: [{id, screen, pdf:[{text,x,y,right}]}]}] }
import fs from "node:fs";
import vm from "node:vm";

const [, , htmlPath, ...dataPaths] = process.argv;
const html = fs.readFileSync(htmlPath, "utf8");
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
if (scripts.length < 2) { console.error("expected two inline <script> blocks"); process.exit(2); }

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
function Chart() { return { destroy() {} }; }
const inert = { then() { return inert; }, catch() { return inert; } };

// The captured "printer". Every doc.text() call is recorded with its position, so
// the test can pair a label at the left margin with its right-aligned amount --
// i.e. read the PDF as a column of figures, which is what the customer does.
let PDF_CALLS = [];
function FakeJsPDF() {
  return {
    setFontSize() {}, setTextColor() {}, setDrawColor() {}, setFont() {},
    line() {}, save() {},
    text(t, x, y, opts) {
      PDF_CALLS.push({ text: String(t), x, y, right: !!(opts && opts.align === "right") });
    },
  };
}

const sandbox = {
  document, Chart, console, Date, Number, String, Object, Math, JSON, Array,
  fetch: () => inert, setTimeout() {}, alert() {},
  location: { search: "" },
  history: { replaceState() {} },
  URLSearchParams: globalThis.URLSearchParams,
  Promise,
  jspdf: { jsPDF: FakeJsPDF },
};
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(scripts[1], sandbox);

const accounts = [];
for (const p of dataPaths) {
  const d = JSON.parse(fs.readFileSync(p, "utf8"));
  if (!d || !Array.isArray(d.invoices)) continue;
  const account = d.account_id || d.base_account_id;
  sandbox.HH = { elec: d.commodity === "gas" ? null : d, gas: d.commodity === "gas" ? d : null, base: d.base_account_id || account };
  const invoices = [];
  for (const inv of d.invoices) {
    PDF_CALLS = [];
    sandbox.downloadBillPdf(inv);
    invoices.push({ id: inv.id, screen: sandbox.billEquationHtml(inv), pdf: PDF_CALLS });
  }
  accounts.push({ account, path: p, invoices });
}
process.stdout.write(JSON.stringify({ accounts }));
