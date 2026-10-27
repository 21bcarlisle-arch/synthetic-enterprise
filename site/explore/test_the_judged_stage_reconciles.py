"""The Judged stage's two columns reconcile: with the ledger for the household, and down the column for us.

Cold read O26 (2026-10-27): "Paid in total" equalled "Revenue billed" on every account, where stage 5's
ledger showed less collected (OCC-52fbc3104c5f: collected £4,747.99 against "paid" £5,062.23). The
ledger was right; the page summed each leg's `revenue_gbp`, the supplier's ex-VAT revenue, and called
it payment. O25: "Net after cost to serve" was not gross less cost to serve (OCC-f6813bf9f05e:
£4,776.92 - £477.25 is not £854.29), because gross was the household's two legs and the other two
figures were the electricity leg's, with no net row between them.

This drives the page's own `stageJudged()` over every household in the published book, in node, and
reads the rows a reader meets. Nothing is pinned to a figure. What is asserted is the property: paid is
what the ledger collected, billed foots to paid + credit + write-off + owed, each "less" row is the gap
between the rows around it, and the bottom line is the sum of the legs' own records.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SITE = HERE.parent
INDEX = HERE / "index.html"
BOOK = SITE / "data" / "customers.json"
LEGS = SITE / "data" / "customers"
PENNY = 0.011

_DRIVER = r"""
import fs from "node:fs";
import vm from "node:vm";
const html = fs.readFileSync(process.argv[2], "utf8");
const cases = JSON.parse(fs.readFileSync(0, "utf8"));
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
if (typeof sb.stageJudged !== "function") { console.error("stageJudged() is gone from the page"); process.exit(3); }
const out = cases.map((k) => {
  const d = k.fuels.electricity || k.fuels.gas;
  return { group: k.c.customer_group, html: sb.stageJudged(d, k.c, k.fuels) };
});
process.stdout.write(JSON.stringify(out));
"""

_ROW = re.compile(r"<tr><td>([^<]+)</td><td class=\"n\">([^<]*)</td></tr>")


def _gbp(text: str) -> float:
    return float(text.replace("£", "").replace(",", ""))


def _cases() -> list[dict]:
    cases = []
    for c in json.loads(BOOK.read_text())["customers"]:
        fuels = {}
        for fuel, leg in (c.get("legs") or {}).items():
            path = LEGS / (leg["cid"] + ".json")
            if path.is_file():
                fuels[fuel] = json.loads(path.read_text())
        if fuels and all((f.get("ledger") or {}).get("entries") is not None for f in fuels.values()):
            cases.append({"c": c, "fuels": fuels})
    return cases


@pytest.fixture(scope="module")
def judged(tmp_path_factory) -> list[tuple[dict, dict]]:
    if not BOOK.is_file():
        pytest.skip("no published book at site/data/customers.json")
    cases = _cases()
    driver = tmp_path_factory.mktemp("judged") / "driver.mjs"
    driver.write_text(_DRIVER)
    proc = subprocess.run(["node", str(driver), str(INDEX)], input=json.dumps(cases),
                          capture_output=True, text=True, timeout=300)
    assert proc.returncode == 0, proc.stderr[:800]
    rendered = json.loads(proc.stdout)
    return [(k, {lab: val for lab, val in _ROW.findall(r["html"])}) for k, r in zip(cases, rendered)]


def test_the_book_is_read(judged):
    # A driver that rendered nothing would pass every leg below over an empty list.
    assert len(judged) > 100


def test_paid_in_total_is_what_the_ledger_collected(judged):
    wrong = []
    for k, rows in judged:
        collected = sum(f["ledger"]["total_collected_gbp"] for f in k["fuels"].values())
        if abs(_gbp(rows["Paid in total"]) - collected) > PENNY:
            wrong.append((k["c"]["customer_group"], rows["Paid in total"], round(collected, 2)))
    assert not wrong, f"{len(wrong)} households print a paid figure the ledger did not collect: {wrong[:5]}"


def test_billed_foots_to_paid_credit_write_off_and_owed(judged):
    wrong = []
    for k, rows in judged:
        owed = next(v for lab, v in rows.items() if lab.startswith("Owed on "))
        parts = (_gbp(rows["Paid in total"]) + _gbp(rows.get("Government bill credit", "0"))
                 + _gbp(rows.get("Written off", "0")) + _gbp(owed))
        if abs(_gbp(rows["Billed, VAT included"]) - parts) > 4 * PENNY:
            wrong.append((k["c"]["customer_group"], rows["Billed, VAT included"], round(parts, 2)))
    assert not wrong, f"{len(wrong)} households' billed does not foot: {wrong[:5]}"


def test_the_column_for_us_foots_and_ends_on_the_legs_own_records(judged):
    steps = (("Revenue, before VAT", "less wholesale energy", "Gross margin"),
             ("Gross margin", "less network, policy and capital", "Net margin"),
             ("Net margin", "less cost to serve", "Net after cost to serve"))
    wrong = []
    for k, rows in judged:
        for top, less, result in steps:
            if abs(_gbp(rows[top]) - _gbp(rows[less]) - _gbp(rows[result])) > 2 * PENNY:
                wrong.append((k["c"]["customer_group"], top, less, result))
        record = sum(f["lifetime_net_after_cts_gbp"] for f in k["fuels"].values())
        if abs(_gbp(rows["Net after cost to serve"]) - record) > PENNY:
            wrong.append((k["c"]["customer_group"], "bottom line", rows["Net after cost to serve"], round(record, 2)))
    assert not wrong, f"{len(wrong)} breaks in the column for us: {wrong[:5]}"


def test_the_page_says_what_gross_and_net_count():
    page = INDEX.read_text()
    for words in ("<b>Gross margin</b> is revenue less the", "<b>Net margin</b> takes those out",
                  "<b>Cost to serve</b>"):
        assert words in page, words
