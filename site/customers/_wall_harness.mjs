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
// It ALSO drives the page's own setWallView() over the static #op-state region, because
// the view selector's subject is the WHOLE page, not the drill-down (cold-eyes 2026-08-12:
// the original filtered only layoutPanels(), so the customer view still rendered the
// company-only and SIM-only exhibit panels above it, and every test was green because no
// fixture's subject was the whole document). The caller passes the op-state region's
// top-level children as [{side, html}]; this harness builds them into a DOM host the page's
// own applyWallViewToOpState() manipulates, then reports what SURVIVES per view.
//
// Usage: node _wall_harness.mjs <index.html> <elec.json> [gas.json] [opstate-children.json]
// Prints JSON: { views: {...}, injected: {...}, probes: {...}, opState: {view: html},
//               opStateProbes: {...} }
import fs from "node:fs";
import vm from "node:vm";

const [, , htmlPath, elecPath, gasPath, opStatePath] = process.argv;
const html = fs.readFileSync(htmlPath, "utf8");
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
if (scripts.length < 2) { console.error("expected two inline <script> blocks"); process.exit(2); }
// BOTH inline scripts, in document order -- the browser runs both, and since
// coldwalk:site2_closed_account_settled_to_zero_and_in_credit the drill-down deliberately
// has NO local copy of the account-standing writer: it calls window.__accountStanding,
// which the first script defines. A harness that ran only the second script would be
// asserting against a page shape no reader is served, and would make the "one writer, not
// four" property untestable -- the same wrong-subject class this module has paid for
// twice (sections 9 and 17).
const code = scripts[0];
const drillCode = scripts[1];

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
// The #op-state region, modelled as real child nodes so the page's own
// applyWallViewToOpState() can append/remove them. `children` is the live document
// order; a node removed from it is GONE from the rendered document, which is the
// property the customer view claims ("if one appears, the page is broken").
const opStateSpec = opStatePath ? JSON.parse(fs.readFileSync(opStatePath, "utf8")) : null;
function opStateNode(spec) {
  const n = {
    _side: spec.side === undefined ? null : spec.side,
    _html: spec.html,
    parentNode: null,
    getAttribute(name) { return name === "data-wall-side" ? n._side : null; },
  };
  return n;
}
const opStateHost = opStateSpec
  ? (() => {
      const host = { children: opStateSpec.map(opStateNode) };
      host.children.forEach((c) => { c.parentNode = host; });
      host.appendChild = (el) => {
        const i = host.children.indexOf(el);
        if (i >= 0) host.children.splice(i, 1);
        host.children.push(el);
        el.parentNode = host;
        return el;
      };
      host.removeChild = (el) => {
        const i = host.children.indexOf(el);
        if (i >= 0) host.children.splice(i, 1);
        el.parentNode = null;
        return el;
      };
      return host;
    })()
  : null;

const document = {
  readyState: "complete",
  getElementById(id) {
    if (id === "op-state" && opStateHost) return opStateHost;
    return (elements[id] ||= stub(id));
  },
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
vm.runInContext(drillCode, sandbox);

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

// THE BILLING TAB, PER FUEL LEG. `injected` above captures the electricity leg only,
// because that is the tab's default. The closed-account settlement claim is rendered from
// the LEG's own ledger (closedAccountNotice(d, invoices)), and C1's credit balance sits
// entirely on the GAS leg -- so a fixture that only ever drives electricity structurally
// cannot see "Account settled to zero" published over a -£24.37 ledger, which is the
// defect coldwalk:site2_closed_account_settled_to_zero_and_in_credit names. Captured as
// its own key rather than folded into `injected`, whose every entry is required non-empty
// by a named test and which single-fuel households would otherwise fail.
const billsByFuel = {};
for (const [fuel, rec] of [["elec", sandbox.HH.elec], ["gas", sandbox.HH.gas]]) {
  if (!rec) { billsByFuel[fuel] = null; continue; }
  sandbox.ACTIVE_TAB = "billing";
  sandbox.BILL_VIEW = "bills";
  sandbox.BILL_FUEL = fuel;
  sandbox.layoutPanels(sandbox.tabPanels());
  sandbox.renderBills(rec);
  billsByFuel[fuel] = elements["bills-section"] ? elements["bills-section"]._inner : null;
}
sandbox.BILL_FUEL = "elec";

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

// The op-state pass, LAST so it cannot disturb the fixtures above. Each view is driven
// through the page's own setWallView() -- the real entry point the button calls -- and the
// surviving children are serialised in document order. If the view switch does not govern
// this region, every view returns the same html and the union tests below fail.
const opState = {};
const opStateProbes = {};
// The DOOR's own copy of the view selector. The page header tells a reader at the canonical
// door that choosing "The customer's side" below renders that view on its own; cold-eyes
// 2026-08-12 found the control only existed inside renderHousehold(), i.e. only after a
// household was opened. Captured here so the test's subject is the RENDERED control coming
// out of the page's own setWallView(), not a string grep of the file.
const doorWallView = {};
if (opStateHost) {
  for (const view of ["both", "customer", "behind"]) {
    sandbox.setWallView(view);
    opState[view] = opStateHost.children.map((c) => c._html).join("");
    doorWallView[view] = elements["door-wall-view"] ? elements["door-wall-view"]._inner : null;
  }
  sandbox.setWallView("both");
  // R15: a block declaring a side the wall does not know cannot be filtered, so
  // applyWallViewToOpState must REFUSE it rather than silently render it everywhere.
  const rogue = opStateNode({ side: "marketing", html: "<div class=\"card\">x</div>" });
  rogue.parentNode = opStateHost;
  opStateHost.children.push(rogue);
  try {
    sandbox.OP_STATE_BLOCKS = null;
    sandbox.setWallView("customer");
    opStateProbes.unknown_side_block = null;
  } catch (e) {
    opStateProbes.unknown_side_block = String(e.message || e);
  }
  opStateHost.removeChild(rogue);
  sandbox.OP_STATE_BLOCKS = null;
  sandbox.setWallView("both");
}

process.stdout.write(JSON.stringify({ views, injected, billsByFuel, probes, opState, opStateProbes, doorWallView }));
