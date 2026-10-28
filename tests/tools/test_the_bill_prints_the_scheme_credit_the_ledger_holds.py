"""The bill prints the Energy Bills Support Scheme credit the ledger holds (N1 of the second cold read).

The defect: PROS-2019-0246's ledger held all six EBSS credits (GBP 400), and its portal invoices
carried none, so the page printed "The electricity bill for December 2022 was GBP 598.04" with no
credit line. `tools/generate_invoice_data._real_invoice` mapped `credit_applied_gbp` (account
credit) and dropped `scheme_credit_month_gbp` / `scheme_credit_gbp`, and the suite's EBSS row read
the ledger, so it passed. Each test here is red on the code before the fix.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from tools import generate_explore_cast as cast
from tools.generate_invoice_data import _real_invoice

PROJECT = Path(__file__).resolve().parents[2]
PAGE = PROJECT / "site" / "explore" / "index.html"
HARNESS = PROJECT / "site" / "explore" / "_bill_render_harness.mjs"
NODE = shutil.which("node")


def _ledger_invoice(**over):
    """PROS-2019-0246's December 2022 electricity bill as the ledger holds it."""
    inv = dict(customer_id="PROS-2019-0246", invoice_number=15881, period_start="2022-12-01",
               period_end="2022-12-31", commodity="electricity", consumption_kwh=1500.0,
               commodity_amount_gbp=520.00, standing_charge_gbp=14.57, non_commodity_amount_gbp=35.00,
               vat_gbp=28.47, total_amount_gbp=598.04, payment_status="paid", outstanding_gbp=0.0,
               scheme_credit_gbp=67.0, scheme_credit_month_gbp=67.0)
    inv.update(over)
    return inv


def test_the_portal_invoice_carries_the_months_credit_and_the_part_this_bill_used():
    out = _real_invoice(_ledger_invoice())
    assert (out["scheme_credit_gbp"], out["scheme_credit_applied_gbp"]) == (67.0, 67.0), out
    # A bill smaller than the month's credit: the bill shows the month, and used only its own size.
    small = _real_invoice(_ledger_invoice(commodity_amount_gbp=20.0, standing_charge_gbp=8.0,
                                          non_commodity_amount_gbp=10.0, vat_gbp=1.9,
                                          total_amount_gbp=39.9, scheme_credit_gbp=39.9))
    assert (small["scheme_credit_gbp"], small["scheme_credit_applied_gbp"]) == (67.0, 39.9), small
    # A month with no credit stays None, never a printed zero.
    none = _real_invoice(_ledger_invoice(scheme_credit_gbp=None, scheme_credit_month_gbp=None))
    assert none["scheme_credit_gbp"] is None, none


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_the_page_prints_the_credit_below_the_total_and_what_the_household_paid(tmp_path):
    dec = _real_invoice(_ledger_invoice())
    plain = _real_invoice(_ledger_invoice(invoice_number=15870, period_start="2021-12-01",
                                          period_end="2021-12-31", scheme_credit_gbp=None,
                                          scheme_credit_month_gbp=None))
    f = tmp_path / "PROS-2019-0246.json"
    f.write_text(json.dumps({"account_id": "PROS-2019-0246", "invoices": [dec, plain]}))
    proc = subprocess.run([NODE, str(HARNESS), str(PAGE), str(f)], capture_output=True, text=True,
                          timeout=120)
    assert proc.returncode == 0, proc.stderr[-2000:]
    screens = {i["id"]: i["screen"] for a in json.loads(proc.stdout)["accounts"] for i in a["invoices"]}
    s = screens[dec["id"]]
    assert "Energy Bills Support Scheme credit" in s and "£67.00" in s, s
    assert "To pay</span><span>£531.04" in s, s
    # The credit sits below the total: the charges above it still add to £598.04.
    assert s.index("= Total") < s.index("Energy Bills Support Scheme"), s
    assert "Energy Bills Support Scheme" not in screens[plain["id"]]


def test_the_2022_shock_sentence_names_the_credit_the_bill_showed():
    rec = {"fuel": "electricity", "month": "December 2022", "now": 598.04, "before": 311.08,
           "scheme_credit": 67.0}
    words = cast._template({"legs": {"electricity": {}}}, {}, "2022-12-31", "shock_2022", rec)[1]
    assert words == ("The electricity bill for December 2022 was £598.04 before its £67.00 Energy "
                     "Bills Support Scheme credit, against £311.08 a year earlier."), words
    words = cast._template({"legs": {"electricity": {}}}, {}, "2022-12-31", "shock_2022", dict(rec, scheme_credit=0.0))[1]
    assert "Scheme" not in words, words
