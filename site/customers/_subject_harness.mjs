// SUBJECT-SEPARATION harness for the wall exhibit (site/customers/index.html, atom SITE2).
//
// WHY THIS EXISTS. The other three harnesses each have a subject that structurally cannot
// see the defect this one is for:
//   _render_harness.mjs   drives the pinned exhibit ALONE (script 1, no drill-down).
//   _wall_harness.mjs     drives layoutPanels(tabPanels()) -- the drill-down's panels, with
//                         #op-state modelled only as a filterable child list.
//   _landing_harness.mjs  drives the BOOT state, where no household is open at all.
// None of them ever occupies the state a reader complained about:
//
//   coldwalk:site2_c1_pinned_exhibit_reads_as_the_open_households (MAJOR, 3 of 3 blind
//   personas) -- the exhibit is pinned to ONE account and re-renders ~2,000px above
//   WHICHEVER household is open, on all six tabs, with nothing between them. All three
//   readers attributed C1's GBP6,560.17 and "two person / urban flat" to C6 (an SME with no
//   gas) and to C_IC1 (I&C). The data is right, the heading does name C1, and the page still
//   misinforms -- because two accounts render at once.
//
// So THIS harness's subject is the document with BOTH regions live: a real #op-state built
// from the page's own markup and filled by the page's own renderCustomerState(), and a real
// #app driven through the page's own renderHousehold() against real per-customer JSON. It
// then walks four states in the order a visitor does -- land, open another household, close,
// open the exhibit's OWN household -- and reports what is in the rendered document.
//
// The last of those is the NULL CONTROL and it is the reason this file is not just a
// one-sided assertion: opening C1 moves the SAMPLE (which household is open) without moving
// the LAW (two subjects must not co-render). If the exhibit vanished there too, the mechanism
// would be "hide the exhibit whenever anything is open" dressed up as a subject rule.
//
// Usage: node _subject_harness.mjs <index.html> <company.json> <exhibit-elec.json>
//                                  <other-elec.json> [exhibit-gas.json]
// Prints JSON: { states: {name: {...}}, exhibitAccount, otherAccount }
import fs from "node:fs";
import vm from "node:vm";

const [, , htmlPath, companyPath, exhibitPath, otherPath, exhibitGasPath] = process.argv;
const html = fs.readFileSync(htmlPath, "utf8");
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
if (scripts.length < 2) { console.error("expected two inline <script> blocks"); process.exit(2); }
const code = scripts[0];
const drillCode = scripts[1];

// ---------------------------------------------------------------------------
// The #op-state children come from the PAGE'S OWN markup, not from a fixture written here.
// A hand-written child list would be this harness's opinion of what the exhibit contains;
// the misread was about what the exhibit actually contains, so the block is read off the
// file and split at depth 0.
// ---------------------------------------------------------------------------
function opStateInner(src) {
  const open = src.indexOf('<div id="op-state"');
  if (open < 0) throw new Error("no #op-state block in the page");
  const bodyStart = src.indexOf(">", open) + 1;
  let depth = 1, i = bodyStart;
  const tag = /<\/?(div|section)\b/g;
  tag.lastIndex = bodyStart;
  let m;
  while ((m = tag.exec(src))) {
    // A self-closing or void form does not occur for div/section in this page.
    depth += m[0][1] === "/" ? -1 : 1;
    if (depth === 0) { i = m.index; break; }
  }
  return src.slice(bodyStart, i);
}
function topLevelChildren(inner) {
  const out = [];
  const tag = /<\/?(div|section)\b[^>]*>/g;
  let depth = 0, start = -1, m;
  while ((m = tag.exec(inner))) {
    const closing = m[0][1] === "/";
    if (!closing) { if (depth === 0) start = m.index; depth += 1; }
    else {
      depth -= 1;
      if (depth === 0 && start >= 0) { out.push(inner.slice(start, m.index + m[0].length)); start = -1; }
    }
  }
  return out;
}

function node(htmlStr) {
  const attrs = {};
  const head = htmlStr.slice(0, htmlStr.indexOf(">"));
  for (const a of head.matchAll(/([a-z-]+)="([^"]*)"/g)) attrs[a[1]] = a[2];
  const n = {
    _html: htmlStr, _attrs: attrs, parentNode: null, id: attrs.id || "",
    getAttribute(k) { return Object.prototype.hasOwnProperty.call(attrs, k) ? attrs[k] : null; },
    setAttribute(k, v) { attrs[k] = String(v); },
    querySelector() { return null; },
    get outerHTML() { return n._html; },
  };
  return n;
}

// A real element: real attributes, real children, real innerHTML. Removal from the document
// has to be OBSERVABLE, because "the reader cannot see the other household's money" is a
// claim about the DOM and not about a stylesheet.
function el(tag) {
  const e = {
    tagName: tag, className: "", id: "", style: {}, dataset: {},
    _attrs: {}, _inner: "", _text: "", children: [], parentNode: null,
    classList: { add() {}, remove() {} },
    setAttribute(n, v) { e._attrs[n] = String(v); },
    getAttribute(n) { return Object.prototype.hasOwnProperty.call(e._attrs, n) ? e._attrs[n] : null; },
    appendChild(c) {
      const i = e.children.indexOf(c);
      if (i >= 0) e.children.splice(i, 1);
      e.children.push(c); c.parentNode = e; return c;
    },
    removeChild(c) {
      const i = e.children.indexOf(c);
      if (i >= 0) e.children.splice(i, 1);
      c.parentNode = null; return c;
    },
    querySelector() { return null; },
    scrollIntoView() {}, focus() {}, getContext() { return {}; },
  };
  Object.defineProperty(e, "innerHTML", {
    get() { return e._inner + e.children.map((c) => c.outerHTML).join(""); },
    set(v) { e.children.forEach((c) => { c.parentNode = null; }); e.children = []; e._inner = String(v); },
  });
  Object.defineProperty(e, "outerHTML", {
    get() {
      const attrs = Object.keys(e._attrs).map((k) => ` ${k}="${e._attrs[k]}"`).join("");
      return `<div id="${e.id}" class="${e.className}"${attrs}>${e.innerHTML}</div>`;
    },
  });
  Object.defineProperty(e, "textContent", { get() { return e._text; }, set(v) { e._text = String(v); } });
  return e;
}

const opStateHost = el("div");
opStateHost.id = "op-state";
// The host's OWN declared subject comes from the page markup, so a page that ships without
// the attribute is a page this harness runs unchanged -- which is what makes the R15
// stripped-attribute mutation a real experiment rather than a harness edit.
{
  const head = html.slice(html.indexOf('<div id="op-state"'));
  for (const a of head.slice(0, head.indexOf(">")).matchAll(/([a-z-]+)="([^"]*)"/g)) {
    if (a[1] !== "id" && a[1] !== "style") opStateHost.setAttribute(a[1], a[2]);
  }
}
topLevelChildren(opStateInner(html)).forEach((h) => opStateHost.appendChild(node(h)));
const OP_STATE_CHILD_COUNT = opStateHost.children.length;
if (!OP_STATE_CHILD_COUNT) { console.error("read zero #op-state children"); process.exit(2); }

const app = el("div"); app.id = "app";
const boundary = el("div"); boundary.id = "subject-boundary";
const doorWallView = el("div"); doorWallView.id = "door-wall-view";
const elements = { app, "op-state": opStateHost, "subject-boundary": boundary, "door-wall-view": doorWallView };

const document = {
  readyState: "complete",
  getElementById(id) { return (elements[id] ||= el("div")); },
  querySelector() { return null; },
  querySelectorAll() { return []; },
  createElement(tag) { return el(tag); },
  addEventListener() {},
};
function Chart() { return { destroy() {} }; }
const inert = { then() { return inert; }, catch() { return inert; } };
const consoleErrs = [];
const sandbox = {
  document, Chart, Date, Number, String, Object, Math, JSON, Array,
  console: { log() {}, warn() {}, error(m) { consoleErrs.push(String(m)); } },
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

const company = JSON.parse(fs.readFileSync(companyPath, "utf8"));
const exhibitElec = JSON.parse(fs.readFileSync(exhibitPath, "utf8"));
const exhibitGas = exhibitGasPath ? JSON.parse(fs.readFileSync(exhibitGasPath, "utf8")) : null;
const otherElec = JSON.parse(fs.readFileSync(otherPath, "utf8"));

const exhibitAccount = (company.household || {}).id || null;
const otherAccount = otherElec.base_account_id || otherElec.account_id;

// Read defensively throughout: this harness must also run against a page that has NONE of
// the mechanism, or the R15 mutations below would be proving nothing (a harness that throws
// on the unfixed page reports "control fired" for the wrong reason).
const violations = () => {
  if (typeof sandbox.__subjectViolations !== "function") return null;
  try { return sandbox.__subjectViolations(); } catch (e) { return ["THREW: " + String(e.message || e)]; }
};
const openHousehold = (elec, gas) => {
  sandbox.HH = { elec, gas: gas || null, base: elec.base_account_id || elec.account_id };
  sandbox.ACTIVE_TAB = "overview";
  sandbox.BILL_FUEL = elec ? "elec" : "gas";
  sandbox.CONS_FUEL = sandbox.BILL_FUEL;
  sandbox.BILL_VIEW = "bills";
  sandbox.CASH_SCOPE = gas ? "combined" : sandbox.BILL_FUEL;
};

function capture(name, threw) {
  const kids = opStateHost.children;
  return [name, {
    threw: threw || null,
    // What is ACTUALLY in the document, in document order.
    op_state_children: kids.length,
    op_state_children_expected: OP_STATE_CHILD_COUNT,
    op_state_html: kids.map((c) => c.outerHTML).join(""),
    op_state_subject: opStateHost.getAttribute("data-account-subject"),
    boundary_html: boundary.innerHTML,
    app_html: app.innerHTML,
    violations: violations(),
  }];
}

const states = {};
function step(name, fn) {
  let threw = null;
  try { fn(); } catch (e) { threw = String((e && e.message) || e); }
  const [k, v] = capture(name, threw);
  states[k] = v;
}

// 1. THE DOOR. showLogin() first (the real boot path for a visitor with no ?acc=), then the
//    page's own renderCustomerState against real company.json -- which is what teaches the
//    exhibit region whose account it is.
step("landing", () => {
  sandbox.showLogin(null);
  const legs = sandbox.__assembleLegs([exhibitElec, ...(exhibitGas ? [exhibitGas] : [])]);
  sandbox.renderCustomerState(company, legs);
  if (sandbox.applyWallViewToOpState) sandbox.applyWallViewToOpState();
});

// 2. THE DEFECT'S OWN STATE: a DIFFERENT household open beneath the pinned exhibit.
step("other_household_open", () => {
  openHousehold(otherElec, null);
  sandbox.renderHousehold();
});

// 3. Every tab -- the walk measured ~2,000px of exhibit above SIX of them, so one tab is not
//    the population. switchTab() is the real entry point a reader clicks.
const perTab = {};
for (const [tab] of sandbox.TABS || [["overview"]]) {
  let threw = null;
  try { sandbox.switchTab(tab); } catch (e) { threw = String((e && e.message) || e); }
  perTab[tab] = {
    threw,
    op_state_children: opStateHost.children.length,
    boundary_html: boundary.innerHTML,
    violations: violations(),
  };
}
states.other_household_open_per_tab = perTab;

// 4. THE RELEASE. R11 forbids an orphan transition: a removal whose restore is untested is
//    half a mechanism.
step("closed_again", () => { sandbox.doLogout(); });

// 5. THE NULL CONTROL. The exhibit's OWN household open. Same law, different sample.
step("exhibit_household_open", () => {
  openHousehold(exhibitElec, exhibitGas);
  sandbox.renderHousehold();
});

// 6. The view selector must still govern the region it governed before -- this change adds a
//    second reason to withhold a block and must not have eaten the first.
const perView = {};
for (const view of ["both", "customer", "behind"]) {
  let threw = null;
  try { sandbox.showLogin(null); sandbox.setWallView(view); } catch (e) { threw = String((e && e.message) || e); }
  perView[view] = {
    threw,
    op_state_children: opStateHost.children.length,
    sides: opStateHost.children.map((c) => c.getAttribute("data-wall-side")),
  };
}
sandbox.setWallView("both");
states.landing_per_view = perView;

process.stdout.write(JSON.stringify({
  states, exhibitAccount, otherAccount, consoleErrs,
  op_state_child_count: OP_STATE_CHILD_COUNT,
}));
