"""A level direct-debit leaver closes on its one balance (home_moves.md s.8.8b).

The walk takes a paid DD bill as paid at its face. A household on a level amount paid that amount
instead, so the walk alone closed 420 of the 421 stranded legs on af31e73fa7 at the wrong balance:
no refund of a level credit, and write-offs of bills an over-collection had already paid. Defect
this file exists to catch: the close reading the walk's paid-at-face bills instead of the level
collections, on the refund side or the write-off side.
"""
from datetime import date, timedelta

from simulation.arrears_engine import (
    LEG_CLOSE,
    arrears_stages,
    balance_settlement_from_outcomes,
    level_collection_difference,
)
from simulation.credit_refund_events import generate_credit_refund_log


def _row(cid, period_end, outcome, amount=50.0):
    return {"customer_id": cid, "period_end": period_end, "commodity": "electricity",
            "amount_gbp": amount, "due_date": date.fromisoformat(period_end) + timedelta(days=14),
            "method": "direct_debit", "outcome": outcome, "days_late": 0}


def _leg(cid, outcomes):
    return [_row(cid, f"2020-{m:02d}-28", o) for m, o in enumerate(outcomes, start=1)]


def _level(cid, amount, months, last_collected="2020-{m:02d}-19"):
    return {cid: [{"month": f"2020-{m:02d}", "collection_date": last_collected.format(m=m),
                   "amount_gbp": amount} for m in range(1, months + 1)]}


#: OVER: paid 60 a month against three 50 bills -> 30 in credit.
#: PART: one 50 bill failed, two paid at 70 against 50 -> 40 over, so 10 is owed, not 50.
#: SHORT: paid 40 against two 50 bills and one failed -> 50 failed + 20 short = 70 owed.
#: PLAIN: not on a level amount -> the failed bill is written off whole, as it always was.
_ROWS = (_leg("OVER", ["success"] * 3) + _leg("PART", ["failed", "success", "success"])
         + _leg("SHORT", ["success", "success", "failed"]) + _leg("PLAIN", ["failed", "success"]))
_LEVEL = {**_level("OVER", 60.0, 3), **_level("PART", 70.0, 3), **_level("SHORT", 40.0, 3)}
_LEAVERS = {"OVER", "PART", "SHORT", "PLAIN"}


def _close():
    closing, last = {}, {}
    written, _ = balance_settlement_from_outcomes(
        _ROWS, _LEAVERS, closing, level_dd_collections=_LEVEL, last_collection_out=last)
    by_leg = {}
    for (cid, _pe, _c), wo in written.items():
        by_leg[cid] = round(by_leg.get(cid, 0.0) + wo["amount_gbp"], 2)
        assert wo["leg"] == LEG_CLOSE
    return closing, by_leg, last


def test_every_fate_of_a_level_leaver_is_reached_refund_partial_write_off_and_standing_debt():
    """One control over the partition: a close that refunds nothing, or writes everything off,
    fails here before any leg's value is read."""
    closing, written, _ = _close()
    fates = {
        "refund": closing["OVER"] < 0 and "OVER" not in written,
        "trimmed_write_off": 0 < written.get("PART", 0) < 50,
        "standing_debt": closing["SHORT"] > written.get("SHORT", 0) > 0,
        "plain_unchanged": written.get("PLAIN") == 50.0,
    }
    assert all(fates.values()), fates


def test_the_closing_balance_is_what_was_billed_less_what_the_bank_paid():
    closing, written, last = _close()
    assert closing["OVER"] == -30.0
    assert closing["PART"] == 10.0 and written["PART"] == 10.0
    assert closing["SHORT"] == 70.0 and written["SHORT"] == 50.0
    assert closing["PLAIN"] == 50.0
    assert last["OVER"] == date(2020, 3, 19)
    assert "PLAIN" not in last


def test_a_returned_month_takes_its_level_slot_and_pays_nothing():
    """The failed bill still consumes its month's collection, exactly as the page matches them:
    otherwise the next bill would take the returned month's level amount."""
    diff = level_collection_difference(_leg("X", ["failed", "success"]),
                                       {"X": [{"month": "2020-01", "collection_date": "2020-01-19",
                                               "amount_gbp": 10.0},
                                              {"month": "2020-02", "collection_date": "2020-02-19",
                                               "amount_gbp": 80.0}]})
    assert diff == {"X": (-30.0, date(2020, 2, 19))}


def test_the_refund_clock_runs_from_a_collection_taken_after_the_final_bill():
    rows = _leg("OVER", ["success"] * 3)
    late = {"OVER": [{"month": f"2020-{m:02d}", "collection_date": "2020-04-20" if m == 3
                      else f"2020-{m:02d}-19", "amount_gbp": 60.0} for m in (1, 2, 3)]}
    closing, last = {}, {}
    balance_settlement_from_outcomes(rows, {"OVER"}, closing, level_dd_collections=late,
                                     last_collection_out=last)
    bills = [{"customer_id": "OVER", "period_end": r["period_end"]} for r in rows]
    log = generate_credit_refund_log(bills, {"OVER": "resi"}, closing, last_collection=last)
    assert len(log) == 1 and log[0]["credit_amount_gbp"] == 30.0
    assert log[0]["request_date"] == "2020-04-20"
    assert date.fromisoformat(log[0]["paid_date"]) >= date(2020, 4, 20)


def test_the_page_writes_off_what_the_walk_wrote_off_not_the_case():
    stages = arrears_stages(50.0, date(2020, 2, 11), False, method="direct_debit",
                            write_off_date=date(2021, 3, 31), write_off_gbp=10.0)
    written = [s for s in stages if s["stage"] == "WRITTEN_OFF"]
    assert written and written[0]["amount_gbp"] == 10.0


def test_the_page_ledger_posts_the_walks_write_off():
    from tools.generate_payment_ledger_data import build_account_ledger
    stages = arrears_stages(50.0, date(2020, 2, 11), False, method="direct_debit",
                            write_off_date=date(2021, 3, 31), write_off_gbp=10.0)
    cust = {"invoices": [{"invoice_number": 1, "issue_date": "2020-01-28", "due_date": "2020-02-11",
                          "total_amount_gbp": 50.0}],
            "payments": [], "arrears_history": [{"invoice_number": 1, "arrears_gbp": 50.0,
                                                 "stages": stages}]}
    entries = build_account_ledger(cust, as_of="2025-01-01")["entries"]
    assert [e["amount_gbp"] for e in entries if e["type"] == "write_off"] == [-10.0]
