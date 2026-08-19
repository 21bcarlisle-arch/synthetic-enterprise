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

// ---------------------------------------------------------------------------
// THE BODY-LEVEL REGION LIST, and it is a SUBJECT this file did not have either.
//
// Every harness here -- this one included, until now -- modelled a `document` with no
// `body` at all. So the page's region list was in nobody's subject: measured in a real
// chromium on the served page, a block carrying "True satisfaction fell 12.2 percentage
// points" appended to document.body survived in the CUSTOMER's view with WALL_VIOLATIONS
// empty and 0 console errors, while 176+ tests were green. #op-state and #app were governed
// because two getElementById literals named them; the other five regions were governed by
// nothing, and a sixth added tomorrow would be too.
//
// So the region list is read off the page's own markup, in document order, exactly as
// opStateInner() reads the exhibit's children -- a hand-written list here would be this
// file's opinion of what the page contains, and what the page contains is the question.
// ---------------------------------------------------------------------------
function bodyRegions(src) {
  // Script and style BODIES are blanked (the element itself is kept, because it is a real
  // child of body and the governor has to decide about it). Comments go entirely: this page
  // carries long prose comments between regions, several of which mention tags by name.
  const flat = src
    .replace(/<!--[\s\S]*?-->/g, "")
    .replace(/<script\b([^>]*)>[\s\S]*?<\/script>/g, "<script$1></script>")
    .replace(/<style\b([^>]*)>[\s\S]*?<\/style>/g, "<style$1></style>");
  const open = flat.indexOf("<body");
  if (open < 0) throw new Error("no <body> in the page");
  const inner = flat.slice(flat.indexOf(">", open) + 1);
  const VOID = new Set(["BR", "HR", "IMG", "INPUT", "META", "LINK", "SOURCE", "AREA", "COL", "EMBED", "PARAM", "TRACK", "WBR"]);
  const out = [];
  const re = /<(\/?)([a-zA-Z][a-zA-Z0-9]*)\b([^>]*?)(\/?)>/g;
  let depth = 0, m;
  while ((m = re.exec(inner))) {
    const closing = m[1] === "/", tag = m[2].toUpperCase(), attrStr = m[3], selfClose = m[4] === "/";
    if (tag === "BODY" || tag === "HTML") break;
    if (VOID.has(tag) || selfClose) { if (depth === 0) out.push({ tag, attrStr }); continue; }
    if (!closing) { if (depth === 0) out.push({ tag, attrStr }); depth += 1; }
    else { depth -= 1; if (depth < 0) break; }
  }
  return out;
}
// One node per region, in document order. The four regions the rest of this harness already
// drives ARE those nodes -- not copies -- so a governor that removes #app from the body is
// removing the same object renderHousehold() writes into.
const body = el("body");
body.tagName = "BODY";
const REGION_IDS = [];
for (const { tag, attrStr } of bodyRegions(html)) {
  const attrs = {};
  for (const a of attrStr.matchAll(/([a-zA-Z-]+)="([^"]*)"/g)) attrs[a[1]] = a[2];
  const known = attrs.id && elements[attrs.id];
  const n = known || el(tag.toLowerCase());
  n.tagName = tag;
  if (attrs.id) n.id = attrs.id;
  if (attrs.class) n.className = attrs.class;
  for (const k of Object.keys(attrs)) if (k !== "id" && k !== "style") n.setAttribute(k, attrs[k]);
  body.appendChild(n);
  REGION_IDS.push(attrs.id || tag);
}
// ANTI-VACUITY, checked here rather than asserted in the test: a harness whose body came out
// empty would run every probe below against nothing and report them all as passing.
if (body.children.length < 5) { console.error("read " + body.children.length + " body regions"); process.exit(2); }

const document = {
  readyState: "complete",
  body,
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
    chrome: opStateHost.children.map((c) => c.getAttribute("data-wall-chrome")),
  };
}
sandbox.setWallView("both");
states.landing_per_view = perView;

// ---------------------------------------------------------------------------
// 7. THE FAIL-OPEN HALF of this region's governor, which is the one the 2026-08-17 walk
//    named and the 08-17 fix closed only on #app. applyWallViewToOpState kept
//    `!side||wallViewShows(side)`, so an #op-state block declaring NOTHING was appended in
//    every view -- the customer's included. These probes bolt a block onto the LIVE region
//    (the same path a new panel would arrive by) and report what the document then holds.
//
//    Read defensively and driven through the page's own setWallView, so this file runs
//    unchanged against a page with none of the mechanism -- which is what makes the
//    mutations experiments rather than harness edits.
// ---------------------------------------------------------------------------
const wallViol = () => (sandbox.WALL_VIOLATIONS || []).slice();
const clearWallViol = () => { if (sandbox.WALL_VIOLATIONS) sandbox.WALL_VIOLATIONS.length = 0; };
function bolt(attrs, inner) {
  const n = node(`<div class="card"${Object.keys(attrs).map((k) => ` ${k}="${attrs[k]}"`).join("")}>${inner}</div>`);
  opStateHost.appendChild(n);
  return n;
}
// Bolting a block on makes it a member of the page's own subject list, which is the point.
// Each probe must therefore take its own block back OUT of that list, or probe (b) would be
// measuring the block probe (a) left behind.
function unbolt(n) {
  if (n.parentNode === opStateHost) opStateHost.removeChild(n);
  const cache = sandbox.OP_STATE_BLOCKS;
  if (Array.isArray(cache)) { const i = cache.indexOf(n); if (i >= 0) cache.splice(i, 1); }
}
function driveAllViews() {
  const seen = { html: "", threw: null };
  for (const view of ["both", "customer", "behind"]) {
    try { sandbox.showLogin(null); sandbox.setWallView(view); }
    catch (e) { seen.threw = String((e && e.message) || e); }
    seen.html += opStateHost.children.map((c) => c.outerHTML).join("");
  }
  return seen;
}
const opProbes = {};
// (a) THE DEFECT'S OWN SHAPE: undeclared, carrying a SIM-only headline. Driven in all three
//     views because a probe that only checks "behind" passes a mutant defaulting the
//     missing side to the customer's -- precisely the fail-open being guarded.
clearWallViol();
const rogue = bolt({}, "True satisfaction fell 12.2 percentage points");
let seen = driveAllViews();
opProbes.undeclared_op_state_html = seen.html;
opProbes.undeclared_op_state_threw = seen.threw;
opProbes.undeclared_op_state_recorded = wallViol();
unbolt(rogue);
// (b) NULL CONTROL A -- same block, DECLARED chrome. Moves the declaration, not the law:
//     if this one also vanished, the "fix" would be "hide anything appended late".
clearWallViol();
const chromeBlock = bolt({ "data-wall-chrome": "1" }, "CHROME-SENTINEL");
seen = driveAllViews();
opProbes.chrome_op_state_html = seen.html;
opProbes.chrome_op_state_recorded = wallViol();
unbolt(chromeBlock);
// (c) NULL CONTROL B -- same block, DECLARED company. Must be governed by the VIEW, not
//     withheld outright: present behind the wall, absent from the customer's side.
clearWallViol();
const sided = bolt({ "data-wall-side": "company" }, "SIDED-SENTINEL");
const sidedPerView = {};
for (const view of ["both", "customer", "behind"]) {
  try { sandbox.showLogin(null); sandbox.setWallView(view); } catch (e) { /* pre-fix */ }
  sidedPerView[view] = opStateHost.children.map((c) => c.outerHTML).join("").indexOf("SIDED-SENTINEL") !== -1;
}
opProbes.sided_op_state_per_view = sidedPerView;
opProbes.sided_op_state_recorded = wallViol();
unbolt(sided);
sandbox.setWallView("both");
states.op_state_declaration_probes = opProbes;

// ---------------------------------------------------------------------------
// 8. THE REGION LIST ITSELF. Same three probes as (7), one level up: the subject is now
//    document.body's children rather than #op-state's. Driven through the page's own
//    setWallView, and each probe takes its own block back out so the next one is not
//    measuring the last one's residue.
//
//    Read defensively throughout -- this file must run unchanged against a page with none
//    of the mechanism, or the mutations in the test module would be proving nothing.
// ---------------------------------------------------------------------------
function boltBody(attrs, inner) {
  const n = el("div");
  n.className = "bolted-at-body";
  n._inner = inner;
  for (const k of Object.keys(attrs)) n.setAttribute(k, attrs[k]);
  body.appendChild(n);
  return n;
}
function unboltBody(n) { if (n.parentNode === body) body.removeChild(n); }
function driveBodyAllViews() {
  const seen = { ids: {}, threw: null };
  for (const view of ["both", "customer", "behind"]) {
    try { sandbox.showLogin(null); sandbox.setWallView(view); }
    catch (e) { seen.threw = String((e && e.message) || e); }
    seen.ids[view] = body.children.map(regionKey);
  }
  return seen;
}
// ONE identity for a region, used by the census and by every survival probe. Two different
// keying rules is how "the guard removed NAV" came out of a run in which nothing was removed.
function regionKey(c) { return c.id || c.className || c.tagName; }
const docProbes = {};
docProbes.declared_regions = body.children.map((c) => ({
  key: regionKey(c),
  id: c.id || null,
  tag: c.tagName,
  cls: c.className || null,
  chrome: c.getAttribute("data-wall-chrome"),
  governed: c.getAttribute("data-wall-governed"),
}));
// The page's OWN exclusion set, reported rather than applied here, so the test can check it
// against a list written independently of the page. A governor that may edit its own
// exemption list has no subject.
docProbes.page_nonrendering = (() => {
  const m = /var DOC_NONRENDERING=\{([^}]*)\}/.exec(html);
  return m ? m[1].split(",").map((s) => s.split(":")[0].trim()).filter(Boolean) : null;
})();
// (a) THE MEASURED DEFECT: undeclared, at body level, carrying the SIM-only headline the
//     page's own WALL_VIEW_NOTE names as proof the page is broken.
clearWallViol();
const bodyRogue = boltBody({}, "True satisfaction fell 12.2 percentage points");
let bseen = driveBodyAllViews();
docProbes.undeclared_region_ids = bseen.ids;
docProbes.undeclared_region_threw = bseen.threw;
docProbes.undeclared_region_recorded = wallViol();
unboltBody(bodyRogue);
// (b) NULL CONTROL A -- the same block, DECLARED chrome, must SURVIVE. Without this the
//     mechanism could be "remove anything appended after boot" wearing a declaration rule's
//     clothes, and probe (a) would pass for the wrong reason.
clearWallViol();
const bodyChrome = boltBody({ "data-wall-chrome": "BODY-CHROME-SENTINEL" }, "chrome");
bseen = driveBodyAllViews();
docProbes.chrome_region_ids = bseen.ids;
docProbes.chrome_region_recorded = wallViol();
unboltBody(bodyChrome);
// (c) THE CLAIM THAT IS NOT CHECKABLE. A region declaring governance by a function that does
//     not exist is ungoverned however loudly it says otherwise, so it must be treated exactly
//     as an undeclared one. This is the arm that stops the new attribute becoming decoration.
clearWallViol();
const bodyFake = boltBody({ "data-wall-governed": "applyWallViewToNothing" }, "x");
bseen = driveBodyAllViews();
docProbes.fake_governor_ids = bseen.ids;
docProbes.fake_governor_recorded = wallViol();
unboltBody(bodyFake);
// (e) THE CLAIM THAT IS CHECKABLE AND STILL FALSE, which is the half (c) does not reach.
//     (c) asks whether the named governor EXISTS. Both of this page's governors resolve
//     their host by a hardcoded id -- applyWallViewToApp walks getElementById("app") and
//     applyWallViewToOpState walks getElementById("op-state") -- so a region naming one of
//     them passes the existence arm while that function never looks at it. The declaration
//     is true of the FUNCTION and false of the REGION. Carries the same SIM-only headline
//     as (a) so a survival here is the identical leak, reached through a real governor's
//     name instead of through no name at all.
clearWallViol();
const bodyBorrowed = boltBody({ "data-wall-governed": "applyWallViewToApp" },
  "True satisfaction fell 12.2 percentage points");
bodyBorrowed.className = "bolted-borrowed-governor";
bseen = driveBodyAllViews();
docProbes.borrowed_governor_ids = bseen.ids;
docProbes.borrowed_governor_recorded = wallViol();
unboltBody(bodyBorrowed);
// (d) THE RELEASE, and R11 forbids an orphan transition: after all that removal the page's
//     own seven regions must still be in the document, in every view.
clearWallViol();
docProbes.surviving_regions = driveBodyAllViews().ids;
docProbes.surviving_recorded = wallViol();
sandbox.setWallView("both");
states.document_region_probes = docProbes;

process.stdout.write(JSON.stringify({
  states, exhibitAccount, otherAccount, consoleErrs,
  op_state_child_count: OP_STATE_CHILD_COUNT,
  region_ids: REGION_IDS,
}));
