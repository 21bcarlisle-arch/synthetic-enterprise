/* R11 for D_printed_figure_rederivation: assert the RENDERED bill line, not
   the JSON behind it.
 *
 * The defect this atom closes was a RENDER defect -- the JSON carried a rate
 * with enough precision, and `toFixed(2)` in the portal threw it away before
 * the customer saw it. So a check that reads site/state/billing_ledger.json
 * and multiplies the numbers would have passed while the page still showed
 * `317.9 kWh x 11.90p = GBP 37.82`. This runs the portal's OWN render
 * functions, lifted verbatim out of site/customers/index.html, and parses the
 * arithmetic back out of the emitted HTML text.
 *
 * Lifting the functions by source extraction (rather than reimplementing them)
 * is the point: a reimplementation would drift from the page and pass while
 * the page failed, which is the same tautology shape R15 names.
 *
 * Usage: node tools/verify_printed_bill_render.mjs
 */
import { readFileSync } from "node:fs";

const HTML = readFileSync("site/customers/index.html", "utf8");
const LEDGER = JSON.parse(readFileSync("site/state/billing_ledger.json", "utf8"));

function lift(name) {
  const start = HTML.indexOf("function " + name + "(");
  if (start < 0) throw new Error("render function not found in page: " + name);
  let depth = 0, i = HTML.indexOf("{", start);
  const from = i;
  for (; i < HTML.length; i++) {
    if (HTML[i] === "{") depth++;
    else if (HTML[i] === "}" && --depth === 0) break;
  }
  return "function " + name + HTML.slice(start + ("function " + name).length, from) + HTML.slice(from, i + 1);
}

// The page's own helpers these two depend on.
// D36 (2026-08-12) moved the bill path onto its own pence-precision formatter,
// billGbp(). This harness plays the external auditor, so it keeps its OWN
// 2dp implementation rather than lifting the page's -- an auditor that borrows
// the printer's arithmetic cannot fail (R15 TAUTOLOGY). Both names are bound
// because the lifted functions call billGbp and the page's other code calls gbp.
const PRELUDE = `
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c];});}
  function gbp(v){return "£"+Number(v).toFixed(2);}
  function billGbp(v){return (Number(v)<0?"-":"")+"£"+Math.abs(Number(v)).toFixed(2);}
`;

const src = PRELUDE + lift("rateStr") + "\n" + lift("billUsageLinesHtml") + "\n" +
  "return {billUsageLinesHtml: billUsageLinesHtml, rateStr: rateStr};";
const api = new Function(src)();

const money = (s) => Number(s.replace(/[£,]/g, ""));
let checked = 0, withRate = 0;
const failures = [];

for (const [cid, entry] of Object.entries(LEDGER.customers)) {
  for (const inv of entry.invoices) {
    const html = api.billUsageLinesHtml(inv);
    checked++;
    // Parse the rendered text back: "<qty> kWh &times; <rate>p/kWh (elec) = £<amt>"
    const m = html.match(/([\d.,]+) kWh &times; ([\d.]+)p\/kWh[^=]*= £([\d.,-]+)/);
    if (!m) continue; // a line rendered without a rate claims no arithmetic
    withRate++;
    const qty = money(m[1]), rate = Number(m[2]), amt = money(m[3]);
    const product = Math.round(qty * rate) / 100;
    if (Math.abs(product - amt) > 0.0049) {
      failures.push(`${cid} ${inv.period_end}: rendered "${qty} kWh x ${rate}p = £${amt}" but the product is £${product.toFixed(2)}`);
    }
  }
}

console.log(`rendered usage lines checked : ${checked}`);
console.log(`  of which printed a rate    : ${withRate}`);
console.log(`  arithmetic does not hold   : ${failures.length}`);
for (const f of failures.slice(0, 5)) console.log("    " + f);

if (withRate < 0.9 * checked) {
  console.log("FAIL: too few lines carry a rendered rate -- this check would pass vacuously.");
  process.exit(1);
}
if (failures.length) process.exit(1);
console.log("PASS: every rendered usage line reproduces its own printed amount.");
