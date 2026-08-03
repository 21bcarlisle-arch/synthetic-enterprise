// Harness for the cross-door GLOSSARY LAYER (site/assets/glossary-layer.js).
//
// The layer's whole job happens in a DOM: it finds [data-gloss] elements on a
// door and rewrites them into permalinks carrying the definition. Asserting on
// the source string would prove nothing, so this drives the REAL asset against a
// minimal DOM and reports what it actually did to the elements (R11 in the small).
//
// It also evaluates the slug function the GLOSSARY PAGE defines inline, so a test
// can compare the two implementations of the shared slug contract directly rather
// than trusting a comment that says they agree.
//
// Usage: node _layer_harness.mjs <layer.js> <glossary-index.html>
//   stdin:  {"feed": <glossary.json>, "marks": ["SSP", "Nonsense Term", ...]}
//   stdout: {"slugs": {...}, "pageSlugs": {...}, "elements": [...],
//            "resolved": [...], "unresolved": [...]}
import fs from "node:fs";
import vm from "node:vm";

const [layerPath, pagePath] = process.argv.slice(2);
const input = JSON.parse(fs.readFileSync(0, "utf8"));
const feed = input.feed;
const marks = input.marks || [];

// ---- a DOM small enough to read, real enough to be driven -------------------
function el(gloss) {
  const attrs = {};
  const classes = new Set();
  return {
    tagName: "SPAN",
    style: {},
    _attrs: attrs,
    textContent: gloss,
    getAttribute(k) { return k === "data-gloss" ? gloss : (attrs[k] ?? null); },
    setAttribute(k, v) { attrs[k] = String(v); },
    classList: { add(c) { classes.add(c); }, contains(c) { return classes.has(c); } },
    _report() {
      return { gloss, attrs: { ...attrs }, classes: [...classes] };
    },
  };
}

const nodes = marks.map(el);
const body = { querySelectorAll: (sel) => (sel === "[data-gloss]" ? nodes : []) };
const document = {
  body,
  querySelector: () => null,
  querySelectorAll: (sel) => (sel === "[data-gloss]" ? nodes : []),
  addEventListener() {},
};

// A location the layer can navigate, so the delegated click handler is exercised
// for real rather than assumed to work.
const location = { href: "https://poesys.net/proof/" };
const sandbox = {
  document, location, console: { warn() {}, log() {}, error() {} },
  String, Object, Array, JSON, Math, Number, RegExp, Boolean,
};
sandbox.globalThis = sandbox;
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(layerPath, "utf8"), sandbox);

const API = sandbox.PoesysGlossary;
const applied = API.apply(feed, body, "../glossary/");

// ---- the page's own inline slug implementation ------------------------------
const html = fs.readFileSync(pagePath, "utf8");
const m = html.match(/<script>([\s\S]*?)<\/script>/);
const pageBox = { String, Object, Array, JSON, Math, Number, RegExp, document: { addEventListener() {} } };
pageBox.window = pageBox;
vm.createContext(pageBox);
vm.runInContext(m[1], pageBox);

const slugs = {};
const pageSlugs = {};
for (const t of feed.terms) {
  slugs[t.term] = API.slug(t.term);
  pageSlugs[t.term] = pageBox.termSlug(t.term);
}

// Exercise the delegated click path on the first node, and report both what the
// handler returned and where `location` actually ended up.
const clickReturned = nodes.length ? API.handleClick(nodes[0]) : null;

process.stdout.write(JSON.stringify({
  slugs,
  pageSlugs,
  elements: nodes.map((n) => n._report()),
  resolved: applied.resolved,
  unresolved: applied.unresolved,
  ready: API.ready,
  clickReturned,
  locationAfterClick: location.href,
}));
