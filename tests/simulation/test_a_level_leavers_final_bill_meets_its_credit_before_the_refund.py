"""A level leaver's final bill meets the credit before the refund, and a level month draws no credit
(home_moves.md s.8.8c).

Defects this file exists to catch, both read off the 068b5e3cc8 pages:
A. the final bill, off the level schedule, collected at its face beside the level credit, and the close
   refunding that credit whole (SYN-2016-369: 303.65 refunded, 8.95 collected the next day);
B. a credit bill drawn against a level-paid month at the bill's face while the bank paid the level
   amount, so the close refunded less than the account held (SYN-2016-493: 12.90 of 55.46).
"""
from datetime import date, timedelta

from simulation.arrears_engine import balance_settlement_from_outcomes


def _row(cid, period_end, amount, outcome="success"):
    return {"customer_id": cid, "period_end": period_end, "commodity": "electricity",
            "amount_gbp": amount, "due_date": date.fromisoformat(period_end) + timedelta(days=14),
            "method": "direct_debit", "outcome": outcome, "days_late": 0}


def _level(cid, amount, months):
    return {cid: [{"month": f"2020-{m:02d}", "collection_date": f"2020-{m:02d}-19",
                   "amount_gbp": amount} for m in months]}


#: COVERED: 60 a month on three 50 bills -> 30 credit; final bill 8 -> refund 22, final DD nothing.
#: SHORT: same 30 credit; final bill 45 -> refund nothing, final DD 15.
#: CREDITED: 30 a month on three 30 bills, the second month's bill a -20 credit -> 20 credit, plus the
#:   level month after it, which the bank paid at 30 and must not eat the credit; final bill 5 -> 15.
_ROWS = ([_row("COVERED", f"2020-{m:02d}-28", 50.0) for m in (1, 2, 3)] + [_row("COVERED", "2020-04-05", 8.0)]
         + [_row("SHORT", f"2020-{m:02d}-28", 50.0) for m in (1, 2, 3)] + [_row("SHORT", "2020-04-05", 45.0)]
         + [_row("CREDITED", "2020-01-28", 30.0), _row("CREDITED", "2020-02-28", -20.0, "credit"),
            _row("CREDITED", "2020-03-28", 30.0), _row("CREDITED", "2020-04-05", 5.0)])
_LEVEL = {**_level("COVERED", 60.0, (1, 2, 3)), **_level("SHORT", 60.0, (1, 2, 3)),
          **_level("CREDITED", 30.0, (1, 3))}
_LEAVERS = {"COVERED", "SHORT", "CREDITED"}


def _close():
    closing, last = {}, {}
    _, credited = balance_settlement_from_outcomes(
        _ROWS, _LEAVERS, closing, level_dd_collections=_LEVEL, last_collection_out=last)
    final = {cid: round(sum(c["amount_gbp"] for c in credited.get((cid, "2020-04-05", "electricity"), ())
                            if c["kind"] == "credit"), 2) for cid in _LEAVERS}
    return closing, final, credited


def test_the_final_bill_takes_the_credit_whole_in_part_or_not_at_all():
    """One control over the partition: a walk that nets nothing, or nets everything, fails here."""
    closing, final, _ = _close()
    assert closing["COVERED"] == -22.0 and final["COVERED"] == 8.0      # refund the rest, collect 0
    assert closing["SHORT"] == 0.0 and final["SHORT"] == 30.0          # refund 0, collect 15


def test_a_level_month_draws_no_credit_so_the_credit_waits_for_the_final_bill():
    closing, final, credited = _close()
    assert not credited.get(("CREDITED", "2020-03-28", "electricity")), credited
    assert final["CREDITED"] == 5.0 and closing["CREDITED"] == -15.0


def test_a_stayer_is_not_netted_by_the_close():
    """Named limit (s.8.8c choice 17): only a leaver's final bills meet the level credit here."""
    closing = {}
    _, credited = balance_settlement_from_outcomes(_ROWS, set(), closing, level_dd_collections=_LEVEL)
    assert not credited.get(("COVERED", "2020-04-05", "electricity"))
