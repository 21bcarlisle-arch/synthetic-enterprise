"""The Priced stage prints the price the tariff committed to, not the first bill's arithmetic.

Fourth cold read, N9 (2026-10-29): OCC-2f64fad94fe7, a gas-only standard variable account, printed
"Unit rate, all-in before VAT 0.00 p/kWh" under "What the supplier committed to", because
`stagePriced` read `d.invoices[0]` and that bill was the 22-29 Feb 2024 move-in stub: 0 kWh, no unit
rate. Its bills charge about 5p. 44 of the 1,293 rebuilt 209c3350ab pages did the same.

This drives the page's own `stagePriced()` in node, over the OCC-2f64fad94fe7 case and over every
page of a book, and grades what a reader meets against the bills on the same page, by the blind row
INV_COMMITTED_PRICE_IS_THE_TARIFFS_PRICE_PER_FUEL_AT_A_DATE, legs 1 to 4:
  1. a page whose bills charge a non-zero rate on kWh > 0 never prints 0.00 for the committed rate;
  2. the printed energy component equals the rate on the bill the panel says it is read from, and
     that bill charged energy (kWh > 0);
  3. the printed all-in rate is the sum of the printed components (no standing charge inside it);
  4. the printed standing charge is that bill's per-day standing charge.
Leg 5 (the cap) is the price rows' job over the bills. The book defaults to the published feed;
EXPLORE_PAGES_DIR grades another one (the 209c rebuild is /var/tmp/fourth-read/tree/site/data).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"
DATA = Path(os.environ.get("EXPLORE_PAGES_DIR") or HERE.parent / "data")

_DRIVER = r"""
import fs from "node:fs";
import vm from "node:vm";
const html = fs.readFileSync(process.argv[2], "utf8");
const pages = JSON.parse(fs.readFileSync(0, "utf8"));
const scripts = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)]
  .map((m) => m[1]).filter((s) => s.trim());
function stub(id) {
  const e = { id, _inner: "", style: {}, dataset: {}, classList: { add() {}, remove() {} },
    setAttribute() {}, appendChild() {}, scrollIntoView() {}, focus() {}, getContext() { return {}; } };
  Object.defineProperty(e, "innerHTML", { get() { return e._inner; }, set(v) { e._inner = String(v); } });
  Object.defineProperty(e, "textContent", { get() { return e._inner; }, set(v) { e._inner = String(v); } });
  return e;
}
const els = {};
const document = { readyState: "complete", getElementById(id) { return (els[id] ||= stub(id)); },
  querySelector() { return stub("qs"); }, querySelectorAll() { return []; },
  createElement() { return stub("ce"); }, addEventListener() {} };
const inert = { then() { return inert; }, catch() { return inert; } };
const sb = { document, console, Date, Number, String, Object, Math, JSON, Array, isNaN, isFinite,
  fetch: () => inert, setTimeout() {}, alert() {}, location: { search: "", hash: "" },
  history: { replaceState() {} }, URLSearchParams: globalThis.URLSearchParams, Promise };
sb.window = sb;
vm.createContext(sb);
for (const s of scripts) vm.runInContext(s, sb);
if (typeof sb.stagePriced !== "function") { console.error("stagePriced() is gone from the page"); process.exit(3); }
const out = pages.map((d) => ({ html: sb.stagePriced(d, {}),
  dates: (d.invoices || []).map((i) => sb.dt(i.date)) }));
process.stdout.write(JSON.stringify(out));
"""

_TEXT = re.compile(r"<[^>]+>")
ALL_IN = re.compile(r"Unit rate, all-in before VAT\s*([\d.]+)\s*p/kWh")
ENERGY = re.compile(r"Energy component of the unit rate\s*([\d.]+)\s*p/kWh")
STACK = re.compile(r"Energy\s+([\d.]+)p.*?Network, policy and levies\s+([\d.]+)p", re.S)
STANDING = re.compile(r"<td>Standing charge</td><td class=\"n\">£([\d.]+)/day")
#: The bill the panel says its price is read from, in either wording the page has used.
FROM = re.compile(r"From (?:this account's first issued bill|the first bill that charged energy under this "
                  r"tariff), (\d{1,2} \w{3,4} \d{4})")
#: Half a unit of the last printed digit (2 dp on the rates, 4 dp on the standing charge).
HALF_P, HALF_SC = 0.0051, 0.00006

#: OCC-2f64fad94fe7 on the 209c3350ab book, its first two bills as the page held them.
OCC_2F64 = {
    "account_id": "OCC-2f64fad94fe7", "commodity": "gas", "tariff_name": "Standard Variable (Gas)",
    "avg_hedge_fraction": 0.85, "annual_pnl": [],
    "invoices": [
        {"id": "OCC-2f64fad94fe7-INV1731", "date": "2024-02-29", "period_start": "2024-02-22",
         "period_end": "2024-02-29", "consumption_kwh": 0, "unit_rate_p_per_kwh": None,
         "standing_charge_gbp": 2.26, "days_in_period": 8, "standing_charge_gbp_per_day": 0.283,
         "non_commodity_amount_gbp": 0.0},
        {"id": "OCC-2f64fad94fe7-INV1732", "date": "2024-03-31", "period_start": "2024-03-01",
         "period_end": "2024-03-31", "consumption_kwh": 636.7, "unit_rate_p_per_kwh": 5.667,
         "standing_charge_gbp": 8.74, "days_in_period": 31, "standing_charge_gbp_per_day": 0.282,
         "non_commodity_amount_gbp": 8.91},
    ],
}


def _render(pages: list[dict], tmp: Path) -> list[dict]:
    driver = tmp / "driver.mjs"
    driver.write_text(_DRIVER)
    proc = subprocess.run(["node", str(driver), str(INDEX)], input=json.dumps(pages),
                          capture_output=True, text=True, timeout=300)
    assert proc.returncode == 0, proc.stderr[:800]
    return json.loads(proc.stdout)


def _charged(i: dict) -> bool:
    return (i.get("consumption_kwh") or 0) > 0 and i.get("unit_rate_p_per_kwh") is not None


def grade(page: dict, rendered: dict) -> tuple[str, str]:
    """('pass' | 'breach' | 'ungraded', why) for one page's Priced panel, by legs 1 to 4."""
    charged = [i for i in page.get("invoices") or () if _charged(i)]
    html = rendered["html"]
    text = _TEXT.sub(" ", html)
    all_in, energy = ALL_IN.search(text), ENERGY.search(text)
    if not charged:
        # Not yet graded: no bill carries a rate, so leg 2 has nothing to compare. Leg 1 still
        # holds -- a page that prints a committed rate here invented it.
        return ("breach", "prints a rate no bill charged") if all_in else ("ungraded", "no bill charged energy")
    if not all_in or float(all_in.group(1)) <= 0:
        return "breach", "leg 1: the committed rate is 0.00 or missing while the bills charge one"
    src = FROM.search(text)
    if not src:
        return "breach", "leg 2: the panel does not name the bill its rate is read from"
    named = [i for i, d in zip(page["invoices"], rendered["dates"]) if d == src.group(1).strip()]
    bill = next((i for i in named if _charged(i)), None)
    if bill is None:
        return "breach", f"leg 2: the bill it names ({src.group(1)}) charged no energy"
    if not energy or abs(float(energy.group(1)) - bill["unit_rate_p_per_kwh"]) > HALF_P:
        return "breach", f"leg 2: energy {energy and energy.group(1)} against the bill's {bill['unit_rate_p_per_kwh']}"
    stack = STACK.search(text)
    if not stack or abs(float(stack.group(1)) + float(stack.group(2)) - float(all_in.group(1))) > 2 * HALF_P:
        return "breach", "leg 3: the printed components do not add up to the all-in rate"
    sc = STANDING.search(html)
    if not sc or abs(float(sc.group(1)) - bill["standing_charge_gbp_per_day"]) > HALF_SC:
        return "breach", "leg 4: the standing charge is not the bill's per-day figure"
    return "pass", ""


def test_a_zero_use_first_bill_does_not_set_the_committed_price(tmp_path):
    # Red on 58abe075eb: the stub's 0 kWh and null rate printed "0.00 p/kWh".
    [rendered] = _render([OCC_2F64], tmp_path)
    verdict, why = grade(OCC_2F64, rendered)
    assert verdict == "pass", why
    text = _TEXT.sub(" ", rendered["html"])
    assert "5.67 p/kWh" in text and "£0.2820/day" in rendered["html"]


def test_the_grader_reaches_every_outcome(tmp_path):
    # A grader that passes everything passes every page below; show each outcome is reachable.
    broken = {"html": "<tr><td>Unit rate, all-in before VAT</td><td class=\"n\">0.00 p/kWh</td></tr>",
              "dates": ["", ""]}
    assert grade(OCC_2F64, broken)[0] == "breach"
    unbilled = dict(OCC_2F64, invoices=OCC_2F64["invoices"][:1])
    [r] = _render([unbilled], tmp_path)
    assert grade(unbilled, r)[0] == "ungraded"
    [r] = _render([OCC_2F64], tmp_path)
    assert grade(OCC_2F64, r)[0] == "pass"


def test_every_page_in_the_book_prints_the_tariffs_price(tmp_path):
    pages_dir = DATA / "customers"
    if not pages_dir.is_dir():
        pytest.skip(f"no per-customer pages at {pages_dir}")
    pages = []
    for f in sorted(pages_dir.glob("*.json")):
        d = json.loads(f.read_text())
        if isinstance(d, dict) and d.get("invoices"):
            pages.append(d)
    assert len(pages) > 100, "the book read is too small to say anything"
    verdicts = [(p["account_id"], *grade(p, r)) for p, r in zip(pages, _render(pages, tmp_path))]
    breaches = [v for v in verdicts if v[1] == "breach"]
    print(f"INV_COMMITTED_PRICE pages={len(verdicts)} pass={sum(v[1] == 'pass' for v in verdicts)} "
          f"breach={len(breaches)} ungraded={sum(v[1] == 'ungraded' for v in verdicts)}")
    assert not breaches, f"{len(breaches)} of {len(verdicts)} pages: {breaches[:5]}"
