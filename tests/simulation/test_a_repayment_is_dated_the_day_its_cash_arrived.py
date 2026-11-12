"""A household repayment is money in on the day it arrived, not on the day the walk met it with a bill.

A level household repays a returned collection before the bill that collection paid for falls due. The walk
(`balance_settlement_from_outcomes`) opens that bill at its due date, so it holds the cash as waiting credit until
then and lists the netting under the due date. The page posts an ARREARS_REPAID stage as `payment_received` on the
stage's date, so it booked PROS-2016-0098's GBP 75.33 of 29 Nov 2018 on 16 Dec. On the 29 Nov cure day the page
then printed GBP 29.29 owed while the desk, which saw the cash, cured. That is 56 of the 113 holds on the 6fe7827ab2
book (docs/design/LEVEL_DD_AREA_MAP_2026-11-11.md s.6).
"""
import datetime as dt

from simulation.arrears_engine import ARREARS_REPAID, CREDIT_APPLIED, with_credits_applied

OPENED = "2018-11-16"
STAGES = [{"stage": "DD_FAILED", "date": OPENED, "note": "Direct debit returned"},
          {"stage": "FIRST_NOTICE", "date": "2018-11-23", "note": "x"},
          {"stage": "SECOND_NOTICE", "date": "2018-12-14", "note": "x"}]


def _repaid(stages):
    return [(s["date"], s["amount_gbp"]) for s in stages if s["stage"] == ARREARS_REPAID]


def test_cash_that_arrived_before_the_walk_met_it_is_dated_on_its_own_day_and_cash_before_the_case_is_credit():
    credits = [
        # Arrived 29 Nov, after the case opened; the walk met it with the bill on 16 Dec.
        {"date": dt.date(2018, 12, 16), "amount_gbp": 75.11, "credit_period_end": "2018-11-29",
         "kind": "repayment"},
        # Arrived 31 Dec and met that day.
        {"date": dt.date(2018, 12, 31), "amount_gbp": 14.04, "credit_period_end": "2018-12-31",
         "kind": "repayment"},
    ]
    early = [{"date": dt.date(2018, 12, 16), "amount_gbp": 10.0, "credit_period_end": "2018-10-02",
              "kind": "repayment"}]
    credit_bill = [{"date": dt.date(2018, 12, 16), "amount_gbp": 5.0, "credit_period_end": "2018-11-30",
                    "kind": "credit"}]
    on_its_day = _repaid(with_credits_applied(STAGES, 89.15, credits))
    early_stages = with_credits_applied(STAGES, 89.15, early)
    before_the_case = [(s["date"], s["amount_gbp"]) for s in early_stages if s["stage"] == CREDIT_APPLIED]
    credit_stage = [s["date"] for s in with_credits_applied(STAGES, 89.15, credit_bill)
                    if s["stage"] == CREDIT_APPLIED]
    # The partition: repayments dated on their own day; cash from before the case opened is credit already
    # on the account, noted at the opening and not this case's money in (LEVEL_DD map s.9 fix 2); and a
    # credit bill (not money in) left on the day it was netted.
    assert on_its_day == [("2018-11-29", 75.11), ("2018-12-31", 14.04)]
    assert before_the_case == [(OPENED, 10.0)] and not _repaid(early_stages)
    assert "payment of 2018-10-02" in next(s["note"] for s in early_stages if s["stage"] == CREDIT_APPLIED)
    assert credit_stage == ["2018-12-16"]


def test_the_stages_stay_in_date_order_and_each_note_states_what_was_left_on_its_day():
    credits = [
        {"date": dt.date(2018, 12, 31), "amount_gbp": 14.04, "credit_period_end": "2018-12-31",
         "kind": "repayment"},
        {"date": dt.date(2018, 12, 16), "amount_gbp": 75.11, "credit_period_end": "2018-11-29",
         "kind": "repayment"},
    ]
    stages = with_credits_applied(STAGES, 89.15, credits)
    dates = [s["date"] for s in stages]
    assert dates == sorted(dates)
    first = next(s for s in stages if s["stage"] == ARREARS_REPAID)
    assert first["date"] == "2018-11-29" and "GBP14.04 left owed" in first["note"]


def test_a_credit_bill_netted_after_the_cash_arrived_is_counted_after_it_in_the_notes():
    # The walk met both on 16 Dec. The cash arrived on 29 Nov, so it came first; the credit bill is not money
    # in and keeps the day it was netted, whatever period it covered.
    credits = [
        {"date": dt.date(2018, 12, 16), "amount_gbp": 5.0, "credit_period_end": "2018-11-20", "kind": "credit"},
        {"date": dt.date(2018, 12, 16), "amount_gbp": 75.11, "credit_period_end": "2018-11-29",
         "kind": "repayment"},
    ]
    stages = with_credits_applied(STAGES, 89.15, credits)
    repaid = next(s for s in stages if s["stage"] == ARREARS_REPAID)
    applied = next(s for s in stages if s["stage"] == CREDIT_APPLIED)
    assert "GBP14.04 left owed" in repaid["note"]
    assert applied["date"] == "2018-12-16" and "GBP9.04 left owed" in applied["note"]
