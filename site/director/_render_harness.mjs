// Render harness for the Director-door (site/director/index.html).
// Extracts the inline <script>, executes it against a minimal DOM + inert fetch
// stub, invokes renderAll(data), and prints every captured element's contents as
// JSON so a test can assert on the RENDERED pixels (R11), not the source string.
//
// Usage: node _render_harness.mjs <index.html>   (combined data JSON on stdin,
//        shape {twin, plan, sys, reserved, health, now}). `now` (ISO string) is
//        optional -- it pins the clock so time-relative renders (reserved item age,
//        daemon-heartbeat staleness) are deterministic under test.
import fs from "node:fs";
import vm from "node:vm";

const htmlPath = process.argv[2];
const html = fs.readFileSync(htmlPath, "utf8");

const m = html.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.error("no inline <script> found"); process.exit(2); }
const code = m[1];

const data = JSON.parse(fs.readFileSync(0, "utf8"));

const elements = {};
function stub(id) {
  // Enough of an Element to let the inline script's veil-init IIFE run without
  // throwing (addEventListener/style/classList are no-ops here) while still
  // capturing innerHTML/textContent for the render assertions.
  const e = { id, _inner: "", _text: "", value: "",
    addEventListener() {}, style: {},
    classList: { add() {}, remove() {}, toggle() {} } };
  Object.defineProperty(e, "innerHTML", { get() { return e._inner; }, set(v) { e._inner = String(v); } });
  Object.defineProperty(e, "textContent", { get() { return e._text; }, set(v) { e._text = String(v); } });
  return e;
}
const document = {
  getElementById(id) { return (elements[id] ||= stub(id)); },
};
// Inert fetch: the inline script ends with Promise.all([fetch...]) — we invoke
// renderAll directly instead, so the fetch chain must stay dormant.
const inert = { then() { return inert; }, catch() { return inert; } };
function fetch() { return inert; }
const Promise_ = { all() { return inert; } };
// Minimal window with an in-memory localStorage so the veil IIFE's PIN lookup
// is inert under test (no PIN saved -> it wires no-op listeners).
const window = { localStorage: { getItem() { return null; }, setItem() {} } };

const sandbox = { document, window, fetch, console, Date, Number, String, Object, Math, JSON, Promise: Promise_ };
vm.createContext(sandbox);
vm.runInContext(code, sandbox);

// `now` is passed through data.now (renderAll reads it); an explicit nowMs arg
// takes precedence when the test wants a hard pin.
const nowMs = data.now ? new Date(data.now).getTime() : undefined;
sandbox.renderAll(data, nowMs);

const ids = [
  "reserved-hyp", "reserved-intro", "reserved-kpis", "reserved-body", "reserved-passport",
  "health-hyp", "health-intro", "health-kpis", "health-body", "health-passport",
  "twin-intro", "twin-kpis", "twin-passport",
  "qa-intro", "qa-body",
  "plan-intro", "plan-kpis", "plan-body", "plan-passport",
  "curriculum-note",
];
const out = {};
for (const id of ids) {
  const e = elements[id];
  out[id] = e ? { innerHTML: e._inner, textContent: e._text } : null;
}
process.stdout.write(JSON.stringify(out));
