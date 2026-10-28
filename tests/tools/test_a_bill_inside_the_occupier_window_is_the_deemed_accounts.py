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


def test_a_part_window_bill_asks_the_payer_for_its_own_share_alone(tmp_path):
    """A bill partly inside the window: the engine asks the named payer for (1 - share) of it, so
    the payer pays that, and the page ledger takes the rest off as the deemed account's. The ledger
    collected the full printed total, so the payer paid the occupier's days, or a failed bill was
    written off at the payer's share and owed in full (OCC-87206d346f15g, GBP 19.16).
    Both outcomes are asserted reachable first, so a ledger that never collects cannot pass."""
    bills = [dict(_resi_bill("OCC-4", "2016-%02d-28" % m), occupier_share=0.4) for m in range(1, 13)]
    bills += [dict(_resi_bill("OCC-4", "2017-%02d-28" % m), occupier_share=0.4) for m in range(1, 13)]
    cust = _ledger(tmp_path, bills)["OCC-4"]
    pays = {p["invoice_number"]: p for p in cust["payments"]}
    outcomes = {p["outcome"] for p in pays.values()}
    assert "success" in outcomes, "no part-window bill was paid: the partition is not reached"
    for inv in cust["invoices"]:
        pay = pays[inv["invoice_number"]]
        if pay["outcome"] == "success":
            assert pay["amount_gbp"] == 90.0, f"the payer paid {pay['amount_gbp']} of a 90.00 share"
        assert inv.get("deemed_share_gbp") == 60.0 and inv["deemed_share_to"] == "occupier"
    # A date after every payment and case has landed, so the balance is what is still owed.
    led = build_account_ledger(cust, "2019-12-31")
    open_arrears = round(sum(i["outstanding_gbp"] for i in cust["invoices"]), 2)
    assert led["total_deemed_gbp"] == round(60.0 * len(bills), 2)
    assert led["current_balance_gbp"] == open_arrears


def test_an_ebss_credit_the_occupier_held_is_not_the_payers(tmp_path):
    """A part-window EBSS month whose credit the unnamed occupier's account held: the engine asks
    the payer for its share whole, so the payer pays it and the page posts no credit to the payer.
    The ledger netted GBP 67 from the payer and posted the month's credit on its page, leaving five
    payers in credit by 27 to 59 pounds on 5e3e9966a5 (OCC-25ff8966357a)."""
    months = ["2022-10-31", "2022-11-30", "2022-12-31", "2023-01-31", "2023-02-28", "2023-03-31"]
    bills = [dict(_resi_bill("OCC-5", pe), occupier_share=0.5, occupier_scheme_credit_gbp=67.0)
             for pe in months]
    cust = _ledger(tmp_path, bills)["OCC-5"]
    paid = [p for p in cust["payments"] if p["outcome"] == "success"]
    assert paid, "no part-window EBSS month was paid: the partition is not reached"
    assert all(p["amount_gbp"] == 75.0 and not p.get("scheme_credit_gbp") for p in paid), (
        [(p["amount_gbp"], p.get("scheme_credit_gbp")) for p in paid])
    led = build_account_ledger(cust, "2024-12-31")
    assert not [e for e in led["entries"] if e["type"] == "scheme_credit"]
    assert led["current_balance_gbp"] == round(sum(i["outstanding_gbp"] for i in cust["invoices"]), 2)


def test_a_window_month_the_ebss_credit_paid_leaves_the_payers_page_at_nothing(tmp_path):
    """A month wholly inside the window whose EBSS credit the deemed account held: the bill and the
    credit are both the deemed account's, so the payer's page nets to nothing. Once the window share
    counted the credit-paid days, the page still posted the month's GBP 67 to the payer, leaving it
    in credit by 67 a month (OCC-bec72a04dec8, Dec 2022 and Jan 2023)."""
    bills = [dict(_resi_bill("OCC-6", pe, 40.0), occupier_share=1.0, occupier_scheme_credit_gbp=40.0,
                  occupier_scheme_month_credit_gbp=67.0) for pe in ("2022-12-31", "2023-01-31")]
    cust = _ledger(tmp_path, bills)["OCC-6"]
    assert [i["billed_to"] for i in cust["invoices"]] == ["occupier", "occupier"]
    assert all(i.get("scheme_credit_month_gbp") == 67.0 for i in cust["invoices"]), (
        "the month credit is not on the deemed bill: the partition is not reached")
    led = build_account_ledger(cust, "2024-12-31")
    assert led["current_balance_gbp"] == 0.0, led["entries"]
