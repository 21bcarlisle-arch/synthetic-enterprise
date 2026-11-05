"""A household's later settlement carries no more than is still open on its contract, and pooled
credit keeps each sum's own kind.

On the fd91027799 book, 25 settlements carried GBP 1,497.46 more than was still open on their fuel.
SYN-2016-380 paid its Sep 2019 bill's 84.32 in Sep 2021, after a 2020 credit had cleared it, so the
account ran into credit. The household is told its balance. A bill other money has cleared has
nothing left to settle (debt_and_collections.md s.7.3). On three legs that excess then landed on a
credit bill's remainder, and the one pooled figure took the latest kind. The page nets only
"credit", so it lost the remainder (PROS-2017-0351, PROS-2020-0126g, SYN-2016-380: GBP 299.35).
"""
import datetime as dt

from simulation.arrears_engine import balance_settlement_from_outcomes, open_on_contract_gbp


def _row(outcome, due, amount, period_end, **extra):
    return {"customer_id": "L1", "period_end": period_end, "commodity": "electricity",
            "amount_gbp": amount, "due_date": due, "outcome": outcome, "days_late": 0,
            "method": None, **extra}


FAILED_FEB = _row("failed", dt.date(2018, 3, 14), 100.0, "2018-02-28")
PAID_MAY = _row("success", dt.date(2018, 6, 14), 100.0, "2018-05-31")


def _settles_feb(on):
    return _row("repayment", on, 100.0, on.isoformat(), settles_month="2018-02")


def test_a_settlement_after_a_credit_carries_only_the_rest_and_leaves_no_excess():
    credit = _row("credit", dt.date(2018, 3, 20), -30.0, "2018-03-31")
    rows = [FAILED_FEB, credit, _settles_feb(dt.date(2018, 3, 28)), PAID_MAY]
    _, credited = balance_settlement_from_outcomes(rows, set())
    on_feb = credited[("L1", "2018-02-28", "electricity")]
    assert [(c["amount_gbp"], c["kind"]) for c in on_feb] == [(30.0, "credit"), (70.0, "repayment")]
    # Nothing was paid in excess, so nothing waits to come off May's bill.
    assert ("L1", "2018-05-31", "electricity") not in credited
    # The control: the same settlement with no credit before it carries the whole bill. The cap
    # binds only where other money got there first.
    _, uncapped = balance_settlement_from_outcomes(
        [FAILED_FEB, _settles_feb(dt.date(2018, 3, 28)), PAID_MAY], set())
    assert [c["amount_gbp"] for c in uncapped[("L1", "2018-02-28", "electricity")]] == [100.0]


def test_the_triads_sizing_reads_the_same_walk():
    credit = _row("credit", dt.date(2018, 3, 20), -30.0, "2018-03-31")
    assert open_on_contract_gbp([FAILED_FEB, credit], dt.date(2018, 3, 28)) == 70.0
    # A credit dated after the settlement does not reach back before it.
    assert open_on_contract_gbp([FAILED_FEB, credit], dt.date(2018, 3, 19)) == 100.0
    # A contract in credit owes nothing.
    big = _row("credit", dt.date(2018, 3, 20), -130.0, "2018-03-31")
    assert open_on_contract_gbp([FAILED_FEB, big], dt.date(2018, 3, 28)) == 0.0


def test_pooled_credit_keeps_each_sums_own_kind():
    # A credit bill waits (nothing open). A repayment for no issued bill then lands as excess beside
    # it, and May's paid bill takes both. The page nets only the credit bill's sum.
    rows = [_row("credit", dt.date(2018, 1, 20), -50.0, "2018-01-31"),
            _row("repayment", dt.date(2018, 2, 1), 20.0, "2018-02-01"),
            PAID_MAY]
    _, credited = balance_settlement_from_outcomes(rows, set())
    on_may = credited[("L1", "2018-05-31", "electricity")]
    assert [(c["amount_gbp"], c["kind"], c["credit_period_end"]) for c in on_may] == [
        (50.0, "credit", "2018-01-31"), (20.0, "repayment", "2018-02-01")]
