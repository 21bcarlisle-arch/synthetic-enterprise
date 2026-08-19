// LANDING-STATE harness for the wall exhibit (site/customers/index.html, atom SITE2).
//
// WHY THIS EXISTS, and it is the whole point of the file. _wall_harness.mjs drives the
// drill-down: it assigns a fully populated `sandbox.HH` BEFORE it ever calls setWallView,
// so its fixture can never occupy the state the page actually boots in. Cold-eyes
// 2026-08-17 found two live defects in exactly that gap, with the suite 97/97 green:
//
//   coldwalk:site2_wall_view_selector_throws_in_its_own_landing_state
//     every click of the three view buttons on the landing page raised
//     "Cannot read properties of null (reading 'segment')" -- setWallView called
//     renderHousehold() with HH={elec:null,gas:null,base:null}.
//   coldwalk:site2_case_study_cards_render_sim_truth_in_the_customer_view
//     the curated grid was appended to #app by a path no wall control could see, so
//     "sim 3.2% vs company 95.0%" and "True satisfaction fell 12.2 percentage points"
//     rendered under the customer view's own "if one appears, the page is broken".
//
// So this harness's SUBJECT is the rendered #app document in the boot state: HH left at
// its declared initial value, showLogin() then setWallView() driven through the page's own
// entry points, and the surviving markup captured per view. #app is modelled with real
// child nodes and real attributes (not the no-op stubs the drill-down harness uses),
// because "a block was REMOVED from the document" is the property being asserted.
//
// Usage: node _landing_harness.mjs <index.html> <case_studies.json> [roster]
//   roster: a path to a customers.json the page's ../data/customers.json fetch RESOLVES
//           with; the literal REJECT to model that artefact being unreadable; or omitted,
//           which keeps the original never-settling fetch (every pre-existing caller).
// Prints JSON: { views: {view: appHtml}, threw: {view: msg|null}, violations: {view: [...]},
//                drops: {view: [...]}, rosterHint: str|null, probes: {...} }
import fs from "node:fs";
import vm from "node:vm";

const [, , htmlPath, casesPath, rosterArg] = process.argv;
const html = fs.readFileSync(htmlPath, "utf8");
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
if (scripts.length < 2) { console.error("expected two inline <script> blocks"); process.exit(2); }
// Both scripts, document order -- see the same note in _wall_harness.mjs. The drill-down
// calls window.__accountStanding, which the first script defines.
const code = scripts[0];
const drillCode = scripts[1];

// A minimal element with REAL attributes, REAL children and a REAL innerHTML, so that
// removal from the document is observable rather than mocked away.
function el(tag) {
  const e = {
    tagName: tag, className: "", id: "", style: {}, dataset: {},
    _attrs: {}, _inner: "", children: [], parentNode: null,
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
    get() {
      // The rendered document is this node's own html plus every child appended to it --
      // which is what a reader sees, and what the customer view claims about.
      return e._inner + e.children.map((c) => c.outerHTML).join("");
    },
    set(v) {
      // Real innerHTML assignment detaches existing children. The cs-wrap cache depends
      // on that being true, so the harness models it rather than papering over it.
      e.children.forEach((c) => { c.parentNode = null; });
      e.children = [];
      e._inner = String(v);
    },
  });
  Object.defineProperty(e, "outerHTML", {
    get() {
      const attrs = Object.keys(e._attrs).map((k) => ` ${k}="${e._attrs[k]}"`).join("");
      return `<div class="${e.className}"${attrs}>${e.innerHTML}</div>`;
    },
  });
  Object.defineProperty(e, "textContent", { get() { return e._inner; }, set(v) { e._inner = String(v); } });
  return e;
}

const app = el("div");
app.id = "app";
const elements = { app };
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
// The ROSTER the landing card's account list is read from. Default is the original
// never-settling fetch, so every caller that passes two arguments sees the page in the
// state it has always been driven in; the two explicit modes are what the roster arms
// below need, and neither is reachable by accident.
const rosterBody = rosterArg && rosterArg !== "REJECT"
  ? JSON.parse(fs.readFileSync(rosterArg, "utf8"))
  : null;
function harnessFetch(url) {
  if (rosterArg && String(url).includes("customers.json")) {
    return rosterArg === "REJECT"
      ? Promise.reject(new Error("roster unavailable"))
      : Promise.resolve({ ok: true, json: () => Promise.resolve(rosterBody) });
  }
  return inert;
}
const sandbox = {
  document, Chart, Date, Number, String, Object, Math, JSON, Array,
  console: { log() {}, warn() {}, error(m) { consoleErrs.push(String(m)); } },
  fetch: harnessFetch, setTimeout() {}, alert() {},
  location: { search: "" },
  history: { replaceState() {} },
  URLSearchParams: globalThis.URLSearchParams,
  Promise,
};
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(code, sandbox);
vm.runInContext(drillCode, sandbox);

// HH is NOT assigned. The page's own `var HH={elec:null,gas:null,base:null}` is the state
// under test; assigning a household here would reproduce the blindness this file exists
// to remove.
sandbox.CASE_STUDIES = JSON.parse(fs.readFileSync(casesPath, "utf8"));

// The harness must also RUN against a page that has none of this mechanism -- that is how
// the control is proven to fire on the unfixed document (R15) rather than only on the
// fixed one. So every hook below is read defensively.
const viol = () => (sandbox.WALL_VIOLATIONS || []).slice();
const clearViol = () => { if (sandbox.WALL_VIOLATIONS) sandbox.WALL_VIOLATIONS.length = 0; };

// The roster fill is a PROMISE chain on the host queue, so the rendered value only exists
// once the microtask queue has drained. A harness that read the slot synchronously would
// only ever see the pending text -- and would report a page that never resolves as green.
const flush = async () => { for (let i = 0; i < 20; i += 1) await Promise.resolve(); };

const views = {}, threw = {}, violations = {}, drops = {};
for (const view of ["both", "customer", "behind"]) {
  clearViol();
  sandbox.showLogin(null);
  await flush();
  try { sandbox.setWallView(view); threw[view] = null; }
  catch (e) { threw[view] = String((e && e.message) || e); }
  views[view] = app.innerHTML;
  violations[view] = viol();
  drops[view] = (sandbox.CASE_STUDY_DROPS || []).slice();
}

// THE RENDERED ACCOUNT LIST. Read off the slot the page filled, from a FRESH element --
// the stub registry outlives a showLogin(), so a slot left over from the loop above would
// let a page that never writes the list at all report the previous run's answer.
delete elements["roster-hint"];
sandbox.CUSTOMER_GROUPS = null;   // the page caches the roster; each mode must re-fetch
sandbox.showLogin(null);
await flush();
const rosterHint = elements["roster-hint"] ? elements["roster-hint"].innerHTML : null;
const rosterSlotInDocument = app.innerHTML.includes('id="roster-hint"');

// R15 probes, driven through the same entry points.
const probes = {};
// 1. An undeclared block bolted onto #app -- the shape of the defect -- must not survive.
sandbox.showLogin(null);
try { sandbox.setWallView("customer"); } catch (e) { /* pre-fix */ }
const rogue = el("div");
rogue.className = "bolted-on";
rogue._inner = "<div>sim 99.9% vs company 1.0%</div>";
app.appendChild(rogue);
clearViol();
try { sandbox.setWallView("customer"); } catch (e) { /* pre-fix pages throw here; the leak below is the finding */ }
probes.undeclared_block_withheld = app.innerHTML.indexOf("bolted-on") === -1;
probes.undeclared_block_recorded = viol();
// 2. A block declaring a side the wall does not know cannot be filtered, so it must throw.
sandbox.showLogin(null);
const badside = el("div");
badside.className = "mystery";
badside.setAttribute("data-wall-side", "marketing");
app.appendChild(badside);
try { sandbox.setWallView("customer"); probes.unknown_side_block = null; }
catch (e) { probes.unknown_side_block = String((e && e.message) || e); }
// 3. A case with no declared side is dropped rather than published.
sandbox.showLogin(null);
const cases = JSON.parse(fs.readFileSync(casesPath, "utf8"));
sandbox.CASE_STUDIES = { cases: cases.cases.map((c) => ({ ...c, wall_side: undefined })) };
// Driven in EVERY view: a case with no declared side must be publishable in none of
// them. Checking only "behind" would pass a mutant that defaults the missing side to
// "customer", which is precisely the fail-open shape.
probes.undeclared_case_html = "";
for (const view of ["both", "customer", "behind"]) {
  try { sandbox.setWallView(view); } catch (e) { /* pre-fix */ }
  probes.undeclared_case_html += app.innerHTML;
}
probes.undeclared_case_drops = (sandbox.CASE_STUDY_DROPS || []).slice();

process.stdout.write(JSON.stringify({
  views, threw, violations, drops, probes, consoleErrs, rosterHint, rosterSlotInDocument,
}));
