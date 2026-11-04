"""INV_BACK_BILLING_ON_RECEIPT_FROM_ISSUE (seventh cold read, N14): a catch-up on a bill paid on
receipt recovers only energy of the 12 months before the bill's ISSUE date.

Defects this catches: a catch-up billed on the deferred direct-debit basis, with nothing written off,
on a bill the household paid on receipt (0a6391d186: PROS-2018-0016, issued 13 Jun 2024, recovering
from 1 Feb 2022); and the 12 months measured back from the bill's period end, not its issue.
Mutations, each reds this file: the bar anchored on `period_end`; a DD-collected bill graded; the
rule's start date ignored; a partial bar read as a breach (the days share is not a bound); a bill with
no payment posted read as clean rather than unbounded; the window read in days, not calendar months.
"""
from __future__ import annotations

from tools import domain_invariant_runner as runner

ROW = "INV_BACK_BILLING_ON_RECEIPT_FROM_ISSUE"


def _account(*, issued="2020-06-05", start="2019-01-01", end="2020-04-30", written_off=0.0,
             method="standard_credit", segment="resi", period_end="2020-05-31", delta=100.0):
    """One electricity leg whose May 2020 bill carries a catch-up over `start`..`end`."""
    bill = {"invoice_number": 7, "document_type": "bill", "issue_date": issued, "due_date": "2020-06-19",
            "period_start": "2020-05-01", "period_end": period_end, "total_amount_gbp": 150.0,
            "catchup_adjustment_gbp": delta * 0.95, "catchup_raw_delta_gbp": delta,
            "catchup_written_off_gbp": written_off, "catchup_period_start": start, "catchup_period_end": end}
    payments = [] if method is None else [
        {"invoice_number": 7, "payment_date": "2020-06-19", "amount_gbp": 150.0, "method": method,
         "outcome": "success"}]
    return {"customer_id": "H", "segment": segment, "periods": [], "payments": [],
            "bill_record": {"invoices": [bill], "payments": payments}}


def _grade(**kw):
    t = runner.ev_back_billing_on_receipt(None, [runner.Account("H", _account(**kw))])
    return t.checked, t.unbounded, [b["side"] for b in t.breaches], [f["side"] for f in t.flags]


def test_every_leg_of_the_row_can_be_taken():
    """The partition, each branch reachable: breach, flag, clean, unbounded and ungraded."""
    # 155 of the window's 486 days fall before 5 Jun 2019: 31.89 of the 100.00 is barred by days.
    assert _grade() == (1, 0, ["nothing barred"], [])
    assert _grade(written_off=30.0) == (1, 0, [], ["barred less than the days share"])
    assert _grade(written_off=31.89) == (1, 0, [], [])
    assert _grade(method=None) == (0, 1, [], [])                         # how it was paid: not on record
    assert _grade(method="direct_debit") == (0, 0, [], [])               # Scenario B: not this row's


def test_the_twelve_months_run_back_from_the_issue_date_not_the_period_end():
    """Window from 1 Jun 2019, bill period ending 31 May 2020: exactly 12 months from the period end,
    but issued 15 Jun 2020, so 1-14 Jun 2019 lie outside. The 0a6391d186 SYN-2016-048 shape."""
    assert _grade(start="2019-06-01", issued="2020-06-15") == (1, 0, ["nothing barred"], [])
    # Twelve calendar months to the day are inside the window, as 21BA.1 words it.
    assert _grade(start="2019-06-05", issued="2020-06-05") == (1, 0, [], [])


def test_the_rule_starts_on_1_may_2018_and_on_1_november_2018_for_a_business():
    early = dict(issued="2018-04-30", start="2017-01-01", end="2018-03-31", period_end="2018-04-15")
    assert _grade(**early) == (0, 0, [], [])
    assert _grade(**dict(early, issued="2018-05-01")) == (1, 0, ["nothing barred"], [])
    assert _grade(**dict(early, issued="2018-08-01", segment="SME")) == (0, 0, [], [])
    assert _grade(**dict(early, issued="2018-11-01", segment="SME")) == (1, 0, ["nothing barred"], [])


def test_a_book_read_without_the_bill_record_is_never_clean():
    acct = _account()
    assert runner.run([{"id": ROW}], {"H": acct})[0]["status"] == "BREACHED"
    del acct["bill_record"]
    assert runner.run([{"id": ROW}], {"H": acct})[0]["status"] == "NOT_IN_EXPORT"
