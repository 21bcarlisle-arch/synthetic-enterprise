"""A level direct debit is collected in a credit bill's month too (payments_and_direct_debit_2026-10-25.md,
"What a level direct debit must be"), and the world walk counts that cash.

Defect this file exists to catch: the walk pairing a level collection only with a DD bill, so a
credit bill's month (a read catch-up refunding an overcharge) drops the cash the household's bank
paid. On 78f82e4242 that was 15 of 17 unshown collections on desk-written-off accounts; SYN-2016-218g
closed at 73.44 with its 19.63 of 13 Mar 2017 missing. The closing balance sizes refunds and bad debt.
"""
from datetime import date, timedelta

from simulation.arrears_engine import balance_settlement_from_outcomes, level_collection_difference


def _row(month, amount, outcome, collection_result=None):
    period_end = f"2017-{month:02d}-28"
    row = {"customer_id": "L", "period_end": period_end, "commodity": "electricity",
           "amount_gbp": amount, "due_date": date.fromisoformat(period_end) + timedelta(days=14),
           "method": None if outcome == "credit" else "direct_debit", "outcome": outcome,
           "days_late": 0}
    if outcome == "credit":
        row["collection_result"] = collection_result
    return row


_LEVEL = {"L": [{"month": f"2017-{m:02d}", "collection_date": f"2017-{m:02d}-13",
                 "amount_gbp": 20.0} for m in (1, 2, 3)]}


def _close(credit_result):
    # The credit is the last month, so no later paid bill draws it (that draw is its own question).
    rows = [_row(1, 20.0, "success"), _row(2, 20.0, "success"),
            _row(3, -11.30, "credit", credit_result)]
    closing, last = {}, {}
    balance_settlement_from_outcomes(rows, {"L"}, closing, level_dd_collections=_LEVEL,
                                     last_collection_out=last)
    return closing["L"], last.get("L"), level_collection_difference(rows, _LEVEL)


def test_a_paid_collection_in_a_credit_month_is_money_in_and_a_returned_one_is_not():
    """Both branches over the partition first: a walk that ignored the credit month, or counted
    every presented collection whatever its result, fails one of the two."""
    paid, last_paid, _ = _close("success")
    returned, last_returned, _ = _close("failed")
    assert paid == round(returned - 20.0, 2), (paid, returned)
    # Two bills paid at face 20 and one credit: the walk holds 11.30 in credit. The bank paid 60 in
    # three collections against bills of 40 less 11.30, so the household is 31.30 in credit.
    assert paid == -31.30
    assert returned == -11.30
    assert last_paid == date(2017, 3, 13)


def test_the_credit_month_takes_its_own_slot_so_later_months_keep_theirs():
    """Popping the credit month's collection must not shift March's onto February's slot."""
    rows = [_row(1, 20.0, "success"), _row(2, -11.30, "credit", "success"),
            _row(3, 25.0, "success")]
    # Feb's 20 is all difference; Mar's 25 bill paid by Mar's 20 collection leaves 5 owed.
    assert level_collection_difference(rows, _LEVEL)["L"] == (-15.0, date(2017, 3, 13))


def test_a_credit_bill_with_no_presented_collection_moves_nothing():
    rows = [_row(1, 20.0, "success"), _row(2, -11.30, "credit", None), _row(3, 20.0, "success")]
    assert level_collection_difference(rows, _LEVEL) == {"L": (0.0, date(2017, 3, 13))}
