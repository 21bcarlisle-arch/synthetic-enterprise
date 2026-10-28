"""The customer page prints the Energy Price Guarantee as its own line, and the revenue row grades it.

Residual R2 of docs/staging/SEAT_FINDING_THE_SECOND_COLD_READS_ROWS_FIND_A_LATE_DIRECT_DEBIT_AN_
UNSHOWN_PRICE_GUARANTEE_AND_ESTIMATES_TOO_CLOSE_TO_THE_MONTH_2026-10-28.md. "Revenue, before VAT"
carries what the government paid the supplier in Oct 2022 - Jun 2023, and the page printed it
nowhere: `generate_invoice_data._real_invoice` dropped the ledger's EPG fields, so 266 accounts on
the 1a02c46116 book read revenue above what was billed with no line to say why. Knowledge page:
docs/market_research/default_tariff_cap_and_epg_on_the_bill.md.

Mutations, each reds this file:
  * `_real_invoice` stops carrying `epg_discount_gbp` or `epg_support_gbp`.
  * `generate_payment_ledger_data` drops `total_epg_support_gbp`.
  * the page drops the bill's discount line, or the Judged panel's EPG row.
  * `ev_billed_ex_vat_reconciles` stops adding E to B -> a crisis account breaches below.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from tools.generate_invoice_data import _real_invoice
from tools.generate_payment_ledger_data import build_account_ledger

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "site" / "explore" / "index.html"


def _ledger_invoice(**kw):
    inv = dict(customer_id="C-EPG", invoice_number=1, period_start="2023-01-01", period_end="2023-01-31",
               commodity="electricity", consumption_kwh=300.0, commodity_amount_gbp=70.0,
               standing_charge_gbp=15.0, non_commodity_amount_gbp=20.0, vat_gbp=5.25,
               total_amount_gbp=110.25, payment_status="paid", read_type="A",
               issue_date="2023-02-01")
    inv.update(kw)
    return inv


def test_the_page_invoice_carries_both_epg_figures_and_an_unsupported_bill_carries_neither():
    crisis = _real_invoice(_ledger_invoice(hmt_epg_receipt_gbp=96.0, epg_support_gbp=90.0))
    assert (crisis["epg_discount_gbp"], crisis["epg_support_gbp"]) == (96.0, 90.0)
    plain = _real_invoice(_ledger_invoice())
    assert (plain["epg_discount_gbp"], plain["epg_support_gbp"]) == (None, None)


def test_the_page_ledger_totals_the_support_outside_its_footing():
    cust = {"invoices": [_ledger_invoice(epg_support_gbp=90.0),
                         _ledger_invoice(invoice_number=2, period_start="2023-02-01",
                                         period_end="2023-02-28", epg_support_gbp=60.5),
                         _ledger_invoice(invoice_number=3, period_start="2023-07-01", period_end="2023-07-31")],
            "payments": []}
    led = build_account_ledger(cust, "2023-12-31")
    assert led["total_epg_support_gbp"] == 150.5
    assert led["total_billed_gbp"] == pytest.approx(3 * 110.25)


_DRIVER = r"""
import fs from "node:fs"; import vm from "node:vm";
const html = fs.readFileSync(process.argv[2], "utf8");
const scripts = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]).filter(s => s.trim());
function stub(id){const e={id,_inner:"",style:{},dataset:{},classList:{add(){},remove(){}},setAttribute(){},appendChild(){},scrollIntoView(){},focus(){},getContext(){return {};}};
  Object.defineProperty(e,"innerHTML",{get(){return e._inner;},set(v){e._inner=String(v);}});
  Object.defineProperty(e,"textContent",{get(){return e._inner;},set(v){e._inner=String(v);}});return e;}
const els={}; const inert={then(){return inert;},catch(){return inert;}};
const sb={document:{readyState:"complete",getElementById(id){return (els[id] ||= stub(id));},querySelector(){return stub("q");},querySelectorAll(){return [];},createElement(){return stub("c");},addEventListener(){}},
  console,Date,Number,String,Object,Math,JSON,Array,isNaN,isFinite,fetch:()=>inert,setTimeout(){},alert(){},location:{search:"",hash:""},history:{replaceState(){}},URLSearchParams:globalThis.URLSearchParams,Promise};
sb.window=sb; vm.createContext(sb); for (const s of scripts) vm.runInContext(s, sb);
const a = JSON.parse(process.argv[3]);
const fuels = {electricity: a.fuel};
process.stdout.write(JSON.stringify({bill: sb.billEquationHtml(a.bill), judged: sb.stageJudged({reaction_chain: []}, {legs: {}}, fuels)}));
"""


def _render(tmp_path, bill, fuel):
    node = shutil.which("node")
    if node is None:
        pytest.fail("node is not installed, so the page's own render cannot be driven")
    drv = tmp_path / "drive.mjs"
    drv.write_text(_DRIVER)
    out = subprocess.run([node, str(drv), str(PAGE), json.dumps({"bill": bill, "fuel": fuel})],
                         capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def _page_bill(**kw):
    b = dict(id="C-EPG-INV1", period_start="2023-01-01", period_end="2023-01-31", consumption_kwh=300.0,
             unit_rate_p_per_kwh=23.33, commodity_amount_gbp=70.0, standing_charge_gbp=15.0,
             days_in_period=31, standing_charge_gbp_per_day=0.4839, non_commodity_amount_gbp=20.0,
             vat_gbp=5.25, amount_gbp=110.25, registers=None)
    b.update(kw)
    return b


def test_the_bill_and_the_judged_panel_print_the_guarantee_only_where_it_was_paid(tmp_path):
    crisis = _render(tmp_path, _page_bill(epg_discount_gbp=96.0),
                     {"lifetime_revenue_gbp": 190.0, "ledger": {"total_epg_support_gbp": 90.0}})
    assert "Energy Price Guarantee discount" in crisis["bill"] and "96.00" in crisis["bill"]
    assert "of which Energy Price Guarantee, paid by the government" in crisis["judged"]
    assert "90.00" in crisis["judged"]
    plain = _render(tmp_path, _page_bill(), {"lifetime_revenue_gbp": 105.0, "ledger": {}})
    assert "Energy Price Guarantee" not in plain["bill"] + plain["judged"]
