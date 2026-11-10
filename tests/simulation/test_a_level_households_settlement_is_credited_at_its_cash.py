"""A level household's settlement of a returned collection is credited at the cash that crossed.

The walk priced every settlement at `min(asked, open)`, both in the bill's face. A level household is
asked its level amount, and `level_collection_difference` leaves failed months out, so the walk adds
up only if it credits the cash. On book 78f82e4242, 130 settlements were credited above the cash
(OCC-1bb3be076448: 27.00 sent, 49.38 credited) and 149 below it (OCC-3c914ee8cef5g: 39.55 sent against
a 23.00 summer bill, 23.00 credited, the rest gone). The cash above what is open waits as credit, and
a later paid level collection does not use it: the household paid that collection in full, so the
excess is refunded at close (OCC-3c914ee8cef5g's 16.55 was drawn by a paid bill and never refunded).

The control in each test is the same rows off the level schedule, where the old pricing stands: the
branch is the level leg's alone, so the fix cannot pass by changing every leg.
"""
import datetime as dt

from simulation.arrears_engine import balance_settlement_from_outcomes

LEG = "L1"


def _row(outcome, due, amount, period_end, **extra):
    return {"customer_id": LEG, "period_end": period_end, "commodity": "electricity",
            "amount_gbp": amount, "due_date": due, "outcome": outcome, "days_late": 0,
            "method": "direct_debit" if outcome in ("success", "failed") else None, **extra}


def _level(*months):
    return {LEG: [{"month": m, "collection_date": "%s-10" % m, "amount_gbp": 30.0} for m in months]}


def _settles(on, cash, month):
    return _row("repayment", on, cash, on.isoformat(), settles_month=month)


def _repaid(credited):
    return round(sum(c["amount_gbp"] for cs in credited.values() for c in cs
                     if c["kind"] == "repayment"), 2)


def test_a_settlement_below_the_face_is_credited_at_its_cash():
    rows = [_row("failed", dt.date(2019, 3, 14), 49.38, "2019-02-28"),
            _settles(dt.date(2019, 3, 28), 27.00, "2019-02")]
    _, level = balance_settlement_from_outcomes(rows, set(), level_dd_collections=_level("2019-02"))
    assert _repaid(level) == 27.00
    # Off the level schedule the household was asked the face, and the walk prices it there.
    _, flat = balance_settlement_from_outcomes(rows, set())
    assert _repaid(flat) == 49.38


def test_cash_above_the_face_waits_and_a_paid_level_collection_does_not_use_it():
    rows = [_row("failed", dt.date(2018, 8, 14), 23.00, "2018-07-31"),
            _settles(dt.date(2018, 8, 31), 39.55, "2018-07"),
            _row("success", dt.date(2018, 9, 14), 30.00, "2018-08-31")]
    closing = {}
    _, level = balance_settlement_from_outcomes(rows, {LEG}, closing,
                                                level_dd_collections=_level("2018-07", "2018-08"))
    assert level[(LEG, "2018-07-31", "electricity")] == [
        {"date": dt.date(2018, 8, 31), "amount_gbp": 23.00, "credit_period_end": "2018-08-31",
         "kind": "repayment"}]
    assert (LEG, "2018-08-31", "electricity") not in level
    # The leaver closes 16.55 in credit: the cash over the bill, which the refund pays back.
    assert closing[LEG] == -16.55
    # Off the level schedule the old pricing stands: the face, no excess, nothing waiting.
    flat_closing = {}
    _, flat = balance_settlement_from_outcomes(rows, {LEG}, flat_closing)
    assert _repaid(flat) == 23.00 and flat_closing[LEG] == 0.0
