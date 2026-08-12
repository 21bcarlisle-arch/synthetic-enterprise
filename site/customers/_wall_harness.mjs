// Render harness for the WALL EXHIBIT drill-down (site/customers/index.html, atom SITE2).
//
// The operational-state panel at the top of the page has its own harness
// (_render_harness.mjs). This one drives the SECOND inline script -- the per-household
// drill-down -- so a test can assert on the RENDERED markup (R11) of every tab, in every
// wall view, plus the content injected into the tabs' placeholder elements afterwards.
//
// It deliberately calls layoutPanels(tabPanels()) rather than renderHousehold(): the
// structural guard's subject is the panel markup a tab actually produces, and driving the
// sole panel writer directly keeps the harness out of the login/nav chrome.
//
// Usage: node _wall_harness.mjs <index.html> <elec.json> [gas.json]
// Prints JSON: { views: {view: {tabKey: html}}, injected: {id: html}, probes: {...} }
import fs from "node:fs";
import vm from "node:vm";

const [, , htmlPath, elecPath, gasPath] = process.argv;
const html = fs.readFileSync(htmlPath, "utf8");
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
if (scripts.length < 2) { console.error("expected two inline <script> blocks"); process.exit(2); }
const code = scripts[1];

const elements = {};
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
const sandbox = {
  document, Chart, console, Date, Number, String, Object, Math, JSON, Array,
  fetch: () => inert, setTimeout() {}, alert() {},
  location: { search: "" },
  history: { replaceState() {} },
  URLSearchParams: globalThis.URLSearchParams,
  Promise,
};
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(code, sandbox);

sandbox.HH = {
  elec: JSON.parse(fs.readFileSync(elecPath, "utf8")),
  gas: gasPath ? JSON.parse(fs.readFileSync(gasPath, "utf8")) : null,
  base: null,
};
sandbox.HH.base = sandbox.HH.elec.base_account_id || sandbox.HH.elec.account_id;

const TAB_KEYS = [
  ["overview", null], ["accounts", null], ["consumption", null],
  ["billing", "bills"], ["billing", "statement"], ["billing", "cashflow"],
  ["timeline", null], ["risk", null],
];
const views = {};
for (const view of ["both", "customer", "behind"]) {
  sandbox.WALL_VIEW = view;
  const out = {};
  for (const [tab, billView] of TAB_KEYS) {
    sandbox.ACTIVE_TAB = tab;
    if (billView) sandbox.BILL_VIEW = billView;
    out[billView ? `${tab}:${billView}` : tab] = sandbox.layoutPanels(sandbox.tabPanels());
  }
  views[view] = out;
}

// Content injected AFTER layout into the tabs' placeholder elements. Each of these ids
// must itself sit inside a declared panel -- that is what the guard checks.
sandbox.WALL_VIEW = "both";
sandbox.ACTIVE_TAB = "billing";
sandbox.BILL_VIEW = "bills";
sandbox.layoutPanels(sandbox.tabPanels());
sandbox.renderBills(sandbox.HH.elec);
sandbox.BILL_VIEW = "cashflow";
sandbox.layoutPanels(sandbox.tabPanels());
sandbox.renderCashflow();
sandbox.renderForecastCashflow();
sandbox.ACTIVE_TAB = "consumption";
sandbox.layoutPanels(sandbox.tabPanels());
sandbox.renderUsage(sandbox.HH.elec);

const injected = {};
for (const id of ["bills-section", "usage-section", "cashflow-kpis", "cashflow-kpis-company", "forecast-cashflow-body"]) {
  injected[id] = elements[id] ? elements[id]._inner : null;
}

// R15 probes: the mechanism must REFUSE an undeclared side, both at panel() and at the
// layout boundary (a block hand-built around the helper).
const probes = {};
function probe(name, fn) {
  try { fn(); probes[name] = null; } catch (e) { probes[name] = String(e.message || e); }
}
probe("panel_with_no_side", () => sandbox.panel(undefined, "T", "<div class=\"card\">x</div>"));
probe("panel_with_unknown_side", () => sandbox.panel("marketing", "T", "<div class=\"card\">x</div>"));
probe("raw_block_reaches_layout", () => sandbox.layoutPanels([{ kind: "panel", side: "marketing", title: "T", body: "<div class=\"card\">x</div>" }]));
probe("undeclared_object_reaches_layout", () => sandbox.layoutPanels([{ html: "<div class=\"card\">x</div>" }]));
probe("declared_panel_is_accepted", () => sandbox.panel("customer", "T", "<div class=\"card\">x</div>"));

process.stdout.write(JSON.stringify({ views, injected, probes }));
