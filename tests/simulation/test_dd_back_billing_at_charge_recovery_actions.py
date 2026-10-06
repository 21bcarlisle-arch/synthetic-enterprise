"""SLC 21BA for direct debit is taken where the debit asks for money, not where a statement is sent.

A direct-debit statement is not a charge recovery action; the debit is, and so is the final bill
that asks for the closing balance (Energy Ombudsman). `simulation/dd_balance_book.py` therefore
bars each account's old collection shortfall at those actions. Whether the annual review also seeks
the balance is the director's assumption toggle (`seek_balance_at_review`); both arms are held here.
"""
from __future__ import annotations

import datetime as dt

from company.billing.back_billing import RecoveryPeriod, barred_unrecovered_gbp
from company.interfaces.accounting_close import close_the_books
from simulation.arrears_engine import payment_method
from simulation.dd_balance_book import build_dd_balance_book


def _dd_id() -> str:
    for i in range(5000):
        if payment_method("resi", 90.0, f"C{i}", "electricity") == "direct_debit":
            return f"C{i}"
    raise AssertionError("no direct-debit id in range")


DD = _dd_id()


def _bills(amounts, true=None, start=(2020, 1)):
    y, m = start
    out = []
    for i, amt in enumerate(amounts):
        b = {
            "customer_id": DD, "segment": "resi", "commodity": "electricity",
            "period_start": f"{y:04d}-{m:02d}-01", "period_end": f"{y:04d}-{m:02d}-28",
            "total_amount_gbp": amt,
        }
        if true is not None:
            b["true_total_amount_gbp"] = true[i]
        out.append(b)
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


# Accurate bills on a debit opened short: £60 against £100 of use, then use doubles in year two.
SHORT = _bills([100.0] * 12 + [200.0] * 18)
OPENING = {DD: 60.0}


def test_a_review_that_never_seeks_the_balance_bars_at_the_final_bill_and_one_that_does_bars_at_the_review():
    never = build_dd_balance_book(SHORT, OPENING, {DD}, seek_balance_at_review=False)
    seeks = build_dd_balance_book(SHORT, OPENING, {DD}, seek_balance_at_review=True)
    # Both arms of the toggle can be taken, and each takes the bar at its own action.
    assert (never.barred_at_reviews_gbp == 0 and never.barred_at_final_bills_gbp > 0
            and seeks.barred_at_reviews_gbp > 0), (never.summary(), seeks.summary())
    # Year one's £480 shortfall is still open at the second review, when it is more than a year old.
    assert seeks.barred_at_reviews_gbp >= 480.0
    # Never asked for, the shortfall ages into the final bill, and more of it is lost.
    assert never.barred_at_final_bills_gbp > seeks.barred_at_reviews_gbp + seeks.barred_at_final_bills_gbp


def test_an_open_accounts_bar_is_an_exposure_not_a_loss():
    book = build_dd_balance_book(SHORT, OPENING, closed_ids=set())
    assert book.barred_at_final_bills_gbp == 0
    assert book.barred_if_sought_at_run_end_gbp > 0


def test_a_debit_that_covered_the_use_bars_nothing_however_wrong_the_bills_were():
    # Ombudsman Scenario B, on the book: estimates billed half the use; the £100 debit paid all of it.
    bills = _bills([50.0] * 17, true=[100.0] * 17)
    book = build_dd_balance_book(bills, {DD: 100.0}, {DD})
    assert book.barred_at_final_bills_gbp == 0


def test_the_bar_never_exceeds_the_debit_the_action_seeks():
    # The debit covers what was billed but not what was used: the statement shows a credit, so the
    # final bill asks for nothing, and nothing can be barred from it.
    bills = _bills([80.0] * 24, true=[100.0] * 24)
    book = build_dd_balance_book(bills, {DD: 90.0}, {DD})
    assert book.trajectories[DD][-1].balance_gbp > 0
    assert book.barred_at_final_bills_gbp == 0


def test_the_review_as_it_was_leaves_every_trajectory_byte_identical():
    plain = build_dd_balance_book(SHORT, OPENING).serialise()
    closed = build_dd_balance_book(SHORT, OPENING, {DD}).serialise()
    for key in ("monthly_held_credit_series", "sample_trajectories"):
        assert plain[key] == closed[key]


def test_a_debt_recovered_and_re_accrued_is_not_read_as_old():
    """The raised debit pays the OLDEST shortfall. 2022's £120 is repaid by a 2023 surplus; the
    £120 open at the demand is the second half of 2023's, inside the window, so nothing is barred.
    Netting the surplus only against the total read £80 of 2022 as still owed."""
    def month(y, m):
        return dt.date(y, m, 1), dt.date(y + (m == 12), m % 12 + 1, 1)

    periods = [RecoveryPeriod(*month(2022, m), 110.0, 100.0) for m in range(1, 13)]
    periods += [RecoveryPeriod(*month(2023, m), 80.0, 100.0) for m in range(1, 7)]
    periods += [RecoveryPeriod(*month(2023, m), 120.0, 100.0) for m in range(7, 13)]
    assert barred_unrecovered_gbp(periods, dt.date(2024, 3, 1)) == 0.0


def test_the_true_charge_is_the_suppliers_own_and_never_the_worlds():
    """The defect: an estimated period's true charge was read off the world's
    `true_total_amount_gbp`, and the bar is now booked. The supplier's own is the estimate plus a
    share of the catch-up the next read billed, pro rata to the estimates."""
    est = _bills([50.0] * 14 + [10.0])
    catchup = est[-1]
    catchup.update({
        "catchup_applied": True, "catchup_period_start": est[0]["period_start"],
        "catchup_period_end": est[-2]["period_end"], "catchup_raw_delta_gbp": 700.0,
        "catchup_adjustment_gbp": 700.0, "total_amount_gbp": 710.0,
    })
    book = build_dd_balance_book(est, {DD: 50.0}, {DD})
    truths = [p.true_charge_gbp for p in book.trajectories[DD]]
    assert truths == [100.0] * 14 + [10.0]
    # A world figure on the bills moves nothing.
    lied = [{**b, "true_total_amount_gbp": 9999.0} for b in est]
    assert build_dd_balance_book(lied, {DD: 50.0}, {DD}).summary() == book.summary()
    # Fourteen months of £50 short, collected at the 15th: the oldest are barred.
    assert book.barred_at_final_bills_gbp > 0


def test_each_bar_taken_is_written_off_on_the_ledger_and_an_exposure_is_not():
    book = build_dd_balance_book(SHORT, OPENING, {DD})
    assert [a["action"] for a in book.bar_actions] == ["final_bill"]
    assert sum(a["amount_gbp"] for a in book.bar_actions) == round(book.barred_at_final_bills_gbp, 2)
    seeks = build_dd_balance_book(SHORT, OPENING, {DD}, seek_balance_at_review=True)
    assert {a["action"] for a in seeks.bar_actions} >= {"review"}
    assert build_dd_balance_book(SHORT, OPENING, closed_ids=set()).bar_actions == []

    records: list[dict] = []
    bills = [{**b, "total_consumption_kwh": 100.0} for b in SHORT]
    plain = close_the_books(records, bills)
    booked = close_the_books(records, bills, back_billing_bars=book.bar_actions)
    bar = book.bar_actions[0]["amount_gbp"]
    assert round(plain.pnl["revenue_gbp"] - booked.pnl["revenue_gbp"], 2) == bar
    assert booked.pnl["back_billing_write_off_gbp"] == bar
    # What was billed is unchanged, so the billed clock still reconciles.
    assert booked.pnl.get("total_billed_gbp") == plain.pnl.get("total_billed_gbp")
