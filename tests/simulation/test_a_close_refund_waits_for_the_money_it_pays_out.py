"""A closing refund is paid no earlier than the money its credit counts (home_moves.md s.8.8d).

The defect this file exists to catch: after s.8.8c, 12 of 176 closure refunds on the 068b5e3cc8 book
paid out money that reached the account after the refund, because the refund clock ran from the final
bill's issue whatever the balance was that day. SYN-2016-244 was refunded 42.14 on 15 Jan 2018 while its
77.82 final bill, raised 7 Jan, was paid on 21 Jan. The amount was right. The day was not: a credit is
payments in excess of the charges (SLC 27.16), so it exists once the money does.

One control over the partition: a refund rule that always waits, or never waits, fails here.
"""
from datetime import date, timedelta

from simulation.arrears_engine import balance_settlement_from_outcomes
from simulation.credit_refund_events import generate_credit_refund_log


def _row(cid, period_end, amount, outcome="success", method="direct_debit", days_late=0):
    return {"customer_id": cid, "period_end": period_end, "commodity": "electricity",
            "amount_gbp": amount, "due_date": date.fromisoformat(period_end) + timedelta(days=14),
            "method": method, "outcome": outcome, "days_late": days_late}


#: PAID_LATE: a level leg long off its schedule (its collections pair no bill), holding 40 a household
#:   overpaid, pays its 70 final bill whole 20 days late (SYN-2016-244's shape). Closing -40.
#: CREDIT_ROW: off level, its final bill is a -60 credit row falling due 18 days after it is issued. A
#:   credit posts when it is issued, so the refund does not wait for its due date. Its refund day must not
#:   move: counting it at its due date put 9 closed legs past reg 6D's clock on the page (PROS-2017-0351).
#: LEVEL_REPAID: a level leaver 30 in credit at its last level collection (19 Mar 2020), whose returned
#:   20 final bill the household repays on 10 May. The refund waits for the later of the two days.
#: EARLY_REPAID: the same, but the repayment row is dated before the return it settles (SYN-2016-139's
#:   11.52 is dated May 2021 and settles an Apr 2022 return). It reaches the account, and the page, when
#:   the walk sets it against the return on 30 Apr.
#: OVERPAID: off level, pays its final bill on time, then sends 25 nothing is owed against on 1 Mar 2021.
#:   That 25 is the whole credit, and it exists from 1 Mar.
#: PART_PAID: a level leaver 30 in credit whose 25 final bill comes back returned on 5 May, 15 of it
#:   part-paid that day (PROS-2019-0318's shape). The 10 left owed nets the credit to 20, which counts
#:   the 15, so the refund waits for 5 May.
#: COVERED: a level leaver whose credit meets its final bill whole (s.8.8c A), so the final bill carries
#:   no cash and the money was all in at its last level collection. Its refund day must not move.
_ROWS = ([_row("PAID_LATE", f"2017-{m:02d}-30", 50.0, method="standard_credit") for m in (9, 10, 11)]
         + [{**_row("PAID_LATE", "2017-08-01", 40.0, "repayment"), "settles_month": "2017-07"},
            _row("PAID_LATE", "2017-12-31", 70.0, method="standard_credit", days_late=20)]
         + [_row("CREDIT_ROW", f"2022-{m:02d}-30", 30.0, method="prepayment") for m in (10, 11)]
         + [{**_row("CREDIT_ROW", "2023-01-02", -60.0, "credit", method=None), "due_date": date(2023, 1, 20)}]
         + [_row("COVERED", f"2020-{m:02d}-28", 50.0) for m in (1, 2, 3)] + [_row("COVERED", "2020-04-05", 8.0)]
         + [_row("LEVEL_REPAID", f"2020-{m:02d}-28", 50.0) for m in (1, 2, 3)]
         + [_row("LEVEL_REPAID", "2020-04-05", 20.0, "failed"),
            {**_row("LEVEL_REPAID", "2020-04-26", 20.0, "repayment"), "settles_month": "2020-04"}]
         + [_row("EARLY_REPAID", f"2020-{m:02d}-28", 50.0) for m in (1, 2, 3)]
         + [{**_row("EARLY_REPAID", "2020-04-05", 20.0, "failed"), "due_date": date(2020, 4, 30)},
            {**_row("EARLY_REPAID", "2020-02-16", 20.0, "repayment"), "settles_month": "2020-02"}]
         + [_row("PART_PAID", f"2020-{m:02d}-28", 50.0) for m in (1, 2, 3)]
         + [{**_row("PART_PAID", "2020-04-05", 10.0, "failed"), "due_date": date(2020, 5, 5), "part_paid_gbp": 15.0}]
         + [_row("OVERPAID", f"2020-{m:02d}-31", 40.0, method="standard_credit") for m in (10, 12)]
         + [{**_row("OVERPAID", "2021-02-15", 25.0, "repayment"), "settles_month": "2020-12"}])
_LEVEL = {"PAID_LATE": [{"month": "2016-05", "collection_date": "2016-05-31", "amount_gbp": 44.92}],
          **{cid: [{"month": f"2020-{m:02d}", "collection_date": f"2020-{m:02d}-19", "amount_gbp": 60.0}
                   for m in (1, 2, 3)] for cid in ("COVERED", "LEVEL_REPAID", "EARLY_REPAID", "PART_PAID")}}
_LEAVERS = {"PAID_LATE", "CREDIT_ROW", "COVERED", "LEVEL_REPAID", "EARLY_REPAID", "OVERPAID", "PART_PAID"}
#: The day the money each leg's credit counts reaches the account.
_MONEY_IN = {"PAID_LATE": date(2018, 1, 14) + timedelta(days=20), "LEVEL_REPAID": date(2020, 5, 10),
             "EARLY_REPAID": date(2020, 4, 30), "OVERPAID": date(2021, 3, 1),
             "PART_PAID": date(2020, 5, 5)}


def _refunds(with_money_in: bool) -> tuple[dict, dict, dict]:
    closing, last, money_in = {}, {}, {}
    balance_settlement_from_outcomes(_ROWS, _LEAVERS, closing, level_dd_collections=_LEVEL,
                                     last_collection_out=last, money_in_out=money_in)
    bills = [{"customer_id": r["customer_id"], "period_end": r["period_end"]} for r in _ROWS
             if r["outcome"] != "repayment"]
    log = generate_credit_refund_log(bills, {cid: "resi" for cid in _LEAVERS}, closing, last_collection=last,
                                     money_in=money_in if with_money_in else None)
    return closing, money_in, {r["customer_id"]: r for r in log}


def test_every_refund_waits_for_its_money_and_only_a_late_one_moves():
    closing, money_in, log = _refunds(True)
    _, _, unmoved = _refunds(False)
    assert closing == {"PAID_LATE": -40.0, "CREDIT_ROW": -60.0, "COVERED": -22.0, "LEVEL_REPAID": -30.0,
                       "EARLY_REPAID": -30.0, "OVERPAID": -25.0, "PART_PAID": -20.0}
    # Both sides of the partition are taken: five refunds move, two do not.
    moved = {cid for cid in log if log[cid]["paid_date"] != unmoved[cid]["paid_date"]}
    assert moved == {"PAID_LATE", "LEVEL_REPAID", "EARLY_REPAID", "OVERPAID", "PART_PAID"}, (log, unmoved)
    for cid, arrived in _MONEY_IN.items():
        assert money_in[cid] == arrived
        assert unmoved[cid]["paid_date"] < arrived.isoformat() <= log[cid]["paid_date"]
    # The amount never moves: only the day does.
    assert {c: r["credit_amount_gbp"] for c, r in log.items()} == {c: -v for c, v in closing.items()}


def test_a_final_bill_its_credit_covers_carries_no_cash_to_wait_for():
    _, money_in, _ = _refunds(True)
    assert "COVERED" not in money_in
