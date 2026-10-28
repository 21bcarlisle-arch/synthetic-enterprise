"""A bill wholly inside the change-of-tenancy window or the void is the deemed account's, and the
ledger reads that from the run instead of drawing a payer of its own.

The run books such a bill as the unnamed occupier's debt or the owner's charge, billed and never
collected (B7 slices 4 and 6; `docs/market_research/back_billing_and_liability.md` s.13), and the
arrears engine never asks the named payer for it. `generate_billing_ledger` drew a method and an
outcome for it anyway, so the named household showed DD collections and failed DDs for money nobody
asked it for. Two of those failed DDs (OCC-3c914ee8cef5g, Mar 2016; OCC-561d240ea21a, Oct 2017) stood
`BALANCE_OPEN` and never chased on the 13a6e5e71d book (cold read O27).
"""
import json

from tests.tools.test_generate_billing_ledger_pw import _resi_bill
from tools.generate_billing_ledger import generate
from tools.generate_payment_ledger_data import build_account_ledger


def _ledger(tmp_path, bills):
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps({"bills": bills, "per_customer_behavioral": {},
                              "churned_billing_accounts": []}))
    return generate(rj, tmp_path / "ledger.json")["customers"]


def test_a_window_bill_has_no_payment_and_a_named_bill_still_has_one(tmp_path):
    """Partition control: the occupier's month, the owner's void month and the named payer's month
    are each taken. MUTATIONS: draw an outcome on the no-row branch again and the window months
    carry payments; send every bill to the deemed account and the named month loses its payment."""
    bills = [dict(_resi_bill("OCC-1", "2017-01-31"), void_owner_share=1.0),
             dict(_resi_bill("OCC-1", "2017-02-28"), occupier_share=1.0),
             _resi_bill("OCC-1", "2017-03-31")]
    cust = _ledger(tmp_path, bills)["OCC-1"]
    by_end = {inv["period_end"]: inv for inv in cust["invoices"]}
    paid_for = {p["invoice_number"] for p in cust["payments"]}
    void, window, named = by_end["2017-01-31"], by_end["2017-02-28"], by_end["2017-03-31"]
    assert void["billed_to"] == "owner" and void["payment_status"] == "billed_to_the_owner"
    assert window["billed_to"] == "occupier" and window["payment_status"] == "billed_to_the_occupier"
    assert void["invoice_number"] not in paid_for and window["invoice_number"] not in paid_for
    assert named["invoice_number"] in paid_for and "billed_to" not in named
    assert all(a["invoice_number"] == named["invoice_number"] for a in cust["arrears_history"])


def test_the_deemed_bill_leaves_the_named_payers_balance(tmp_path):
    """The page ledger raises the deemed bill and takes it straight off: the named payer's balance
    is what its own bills leave, and billed foots with the deemed bucket beside the others."""
    cust = _ledger(tmp_path, [dict(_resi_bill("OCC-2", "2017-02-28"), occupier_share=1.0)])["OCC-2"]
    led = build_account_ledger(cust, cust["invoices"][-1]["issue_date"])
    assert led["current_balance_gbp"] == 0.0
    assert led["total_deemed_gbp"] == led["total_billed_gbp"] == 150.0
    assert led["total_collected_gbp"] == 0.0
    assert [e["type"] for e in led["entries"]] == ["invoice_raised", "deemed_account"]


def test_a_catch_up_credit_inside_the_window_is_the_deemed_accounts_too(tmp_path):
    """The window's estimates corrected inside the window are the occupier's credit, not the named
    payer's: left on the payer, nothing drew it and the leaver closed in credit with no refund
    (OCC-2e29bf263cb4, -£15.33). MUTATIONS: test the window after the credit branch and this fails."""
    credit = dict(_resi_bill("OCC-3", "2017-03-31", -15.0), occupier_share=1.0,
                  catchup_applied=True, catchup_direction="overcharge")
    cust = _ledger(tmp_path, [dict(_resi_bill("OCC-3", "2017-02-28"), occupier_share=1.0),
                              credit])["OCC-3"]
    assert [i["billed_to"] for i in cust["invoices"]] == ["occupier", "occupier"]
    led = build_account_ledger(cust, cust["invoices"][-1]["issue_date"])
    assert led["current_balance_gbp"] == 0.0
