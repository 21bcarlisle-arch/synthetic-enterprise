"""N29: a closing dual-fuel household's credit on one fuel pays its closing debt on the other before
anything is refunded (home_moves.md s.8.8e, choices 21-24).

The defect this catches: the close refund read each fuel alone, so on the 6fe7827ab2 run 42
households were refunded a credit on one fuel (GBP 1,339.69 of it settable) while the other fuel
closed owing, and that debt was then written off. A first build posted the set-off beside the debt
leg's arrears case, which still wrote its whole amount off, so 4 legs closed below zero on the page.
The set-off now enters the debt leg's own walk, and the write-off falls by it.
"""
from __future__ import annotations

import datetime as dt

from simulation.arrears_engine import (
    LEG_CLOSE,
    balance_settlement_from_outcomes,
    with_credits_applied,
)
from simulation.credit_refund_events import (
    generate_credit_refund_log,
    set_offs_from_refund_log,
)
from tools.generate_payment_ledger_data import build_account_ledger


def _bills(*cids: str, period_end: str = "2023-06-10") -> list[dict]:
    return [{"customer_id": c, "period_end": period_end} for c in cids]


def _log(closing: dict[str, float], period_end: str = "2023-06-10") -> dict[str, dict]:
    log = generate_credit_refund_log(_bills(*closing, period_end=period_end), {}, closing)
    return {e["customer_id"]: e for e in log}


def test_the_set_off_can_be_taken_and_refunds_only_the_rest():
    """The partition first: the set-off branch is taken, and the refund is what is left."""
    log = _log({"H1": -100.0, "H1g": 60.0})
    event = log["H1"]
    assert event["set_off_gbp"] == 60.0 and event["set_off_against"] == "H1g"
    assert event["credit_amount_gbp"] == 40.0
    assert "H1g" not in log, "a leg that closes owing is not refunded"


def test_a_debt_larger_than_the_credit_takes_all_of_it_and_nothing_is_refunded():
    event = _log({"PROS-2019-0318": -111.33, "PROS-2019-0318g": 1047.61})["PROS-2019-0318"]
    assert event["set_off_gbp"] == 111.33
    assert event["credit_amount_gbp"] == 0.0


def test_no_set_off_without_a_closing_debt_on_the_same_household():
    log = _log({"H2": -50.0, "H2g": -20.0, "H3": -30.0, "H4g": 80.0})
    assert all(e["set_off_gbp"] == 0.0 and "set_off_against" not in e for e in log.values())
    assert {c: e["credit_amount_gbp"] for c, e in log.items()} == {"H2": 50.0, "H2g": 20.0, "H3": 30.0}


def test_it_applies_before_slc_27_8d_too():
    """Choice 22: the whole window, not only from 22 Jan 2021."""
    event = _log({"H5": -40.0, "H5g": 25.0}, period_end="2018-03-01")["H5"]
    assert event["set_off_gbp"] == 25.0 and event["credit_amount_gbp"] == 15.0


def _bill(cid: str, period_end: str, outcome: str, amount: float) -> dict:
    return {"customer_id": cid, "period_end": period_end, "commodity": "gas",
            "due_date": dt.date.fromisoformat(period_end) + dt.timedelta(days=14),
            "outcome": outcome, "amount_gbp": amount, "days_late": 0, "method": "cash_cheque"}


_DEBT_LEG = [_bill("H1g", "2023-04-10", "failed", 25.0), _bill("H1g", "2023-05-10", "failed", 35.0),
             _bill("H1g", "2023-06-10", "success", 20.0)]


def _walk(set_off: float | None):
    closing: dict[str, float] = {}
    log = [{"customer_id": "H1", "paid_date": "2023-07-03", "set_off_gbp": set_off,
            "set_off_against": "H1g"}] if set_off is not None else []
    written, credited = balance_settlement_from_outcomes(
        _DEBT_LEG, {"H1g"}, closing, set_offs=set_offs_from_refund_log(log))
    return written, credited, closing


def test_the_set_off_nets_the_debt_legs_cases_oldest_first_before_the_close_write_off():
    """The partition over the debt leg: without a set-off both cases are written off whole; with
    one, the oldest is met first and only what is left is written off; a set-off as large as the
    debt leaves nothing to write off."""
    whole, _, closing = _walk(None)
    assert closing["H1g"] == 60.0
    assert {k[1]: (w["amount_gbp"], w["leg"]) for k, w in whole.items()} == {
        "2023-04-10": (25.0, LEG_CLOSE), "2023-05-10": (35.0, LEG_CLOSE)}

    part, credited, closing = _walk(40.0)
    assert closing["H1g"] == 60.0, "closing_out is the balance at close, before the set-off"
    assert {k[1]: w["amount_gbp"] for k, w in part.items()} == {"2023-05-10": 20.0}
    met = {k[1]: [(c["amount_gbp"], c["kind"], c["credit_period_end"]) for c in v]
           for k, v in credited.items()}
    assert met == {"2023-04-10": [(25.0, "set_off", "H1")], "2023-05-10": [(15.0, "set_off", "H1")]}

    full, _, _ = _walk(60.0)
    assert full == {}, "a set-off of the whole debt leaves nothing to write off"


def test_the_case_on_the_page_prints_the_set_off_and_ends_at_what_is_left():
    _, credited, _ = _walk(40.0)
    stages = [{"stage": "OPEN", "date": "2023-06-08"}, {"stage": "WRITTEN_OFF", "date": "2024-06-10"}]
    walked = with_credits_applied(stages, 35.0, credited[("H1g", "2023-05-10", "gas")])
    applied = [st for st in walked if st["stage"] == "CREDIT_APPLIED"]
    assert [st["amount_gbp"] for st in applied] == [15.0]
    assert "set against this bill" in applied[0]["note"] and "GBP20.00 left owed" in applied[0]["note"]


def test_a_set_off_on_a_leg_that_did_not_close_is_not_netted():
    """Choice 24: only where both legs close. The walk nets a set-off on a leaver only."""
    log = [{"customer_id": "H1", "paid_date": "2023-07-03", "set_off_gbp": 40.0,
            "set_off_against": "H1g"}]
    _, credited = balance_settlement_from_outcomes(_DEBT_LEG, set(),
                                                   set_offs=set_offs_from_refund_log(log))
    assert not any(c["kind"] == "set_off" for v in credited.values() for c in v)


def _leg(cid: str, billed: float, paid: float, set_off: float, refund: float, other: str) -> dict:
    day = "2023-06-26"
    return {
        "invoices": [{"invoice_number": 1 if cid == "H1" else 2, "issue_date": "2023-06-10",
                      "total_amount_gbp": billed}],
        "payments": ([{"invoice_number": 1, "outcome": "success", "payment_date": "2023-06-12",
                       "amount_gbp": paid, "method": "direct_debit"}] if paid else []),
        "arrears_history": [],
        "set_offs": [{"date": day, "amount_gbp": set_off, "other_leg": other}],
        "refunds": [{"paid_date": day, "amount_gbp": refund}] if refund else [],
    }


def test_the_page_prints_the_set_off_on_both_legs_and_each_leg_still_foots():
    credit_leg = _leg("H1", billed=50.0, paid=150.0, set_off=60.0, refund=40.0, other="H1g")
    debt_leg = _leg("H1g", billed=60.0, paid=0.0, set_off=-60.0, refund=0.0, other="H1")
    as_of = dt.date(2025, 7, 4).isoformat()
    for leg in (credit_leg, debt_leg):
        walk = build_account_ledger(leg, as_of)
        assert any(e["type"] == "set_off" for e in walk["entries"])
        assert walk["current_balance_gbp"] == 0.0
        assert round(walk["total_collected_gbp"] + walk["current_balance_gbp"]
                     + walk["total_written_off_gross_gbp"], 2) == walk["total_billed_gbp"]
    entries = build_account_ledger(credit_leg, as_of)["entries"]
    order = [e["type"] for e in entries if e["date"] == "2023-06-26"]
    assert order == ["set_off", "refund_debit"], "the refund pays only what the set-off left"


def test_the_ledger_posts_each_legs_side_and_no_empty_refund():
    from tools.generate_billing_ledger import post_refunds_and_set_offs

    customers = {"H1": {}, "H1g": {}, "H2": {}}
    post_refunds_and_set_offs(customers, [
        {"customer_id": "H1", "paid_date": "2023-06-26", "credit_amount_gbp": 0.0,
         "set_off_gbp": 111.33, "set_off_against": "H1g"},
        {"customer_id": "H2", "paid_date": "2023-07-01", "credit_amount_gbp": 12.5, "set_off_gbp": 0.0},
    ])
    assert "refunds" not in customers["H1"], "a credit the set-off took whole prints no refund line"
    assert customers["H1"]["set_offs"] == [{"date": "2023-06-26", "amount_gbp": 111.33, "other_leg": "H1g"}]
    assert customers["H1g"]["set_offs"] == [{"date": "2023-06-26", "amount_gbp": -111.33, "other_leg": "H1"}]
    assert customers["H2"] == {"refunds": [{"paid_date": "2023-07-01", "amount_gbp": 12.5}]}


def test_a_level_debt_legs_one_balance_falls_by_the_set_off():
    """A level leg is written off no further than its one balance (s.8.8b choice 4), so the set-off
    must come off that balance too, not only off the bills: PART paid 70 a month against a failed
    50 and two paid 50s, so it owes 10; 6 set off leaves 4 to write off, not 10."""
    rows = [{"customer_id": "PART", "period_end": f"2020-{m:02d}-28", "commodity": "electricity",
             "amount_gbp": 50.0, "due_date": dt.date(2020, m, 28) + dt.timedelta(days=14),
             "method": "direct_debit", "outcome": o, "days_late": 0}
            for m, o in enumerate(["failed", "success", "success"], start=1)]
    level = {"PART": [{"month": f"2020-{m:02d}", "collection_date": f"2020-{m:02d}-19",
                       "amount_gbp": 70.0} for m in range(1, 4)]}
    log = [{"customer_id": "PARTg", "paid_date": "2020-04-20", "set_off_gbp": 6.0,
            "set_off_against": "PART"}]
    before, _ = balance_settlement_from_outcomes(rows, {"PART"}, level_dd_collections=level)
    after, _ = balance_settlement_from_outcomes(rows, {"PART"}, level_dd_collections=level,
                                                set_offs=set_offs_from_refund_log(log))
    assert sum(w["amount_gbp"] for w in before.values()) == 10.0
    assert sum(w["amount_gbp"] for w in after.values()) == 4.0
