"""Inside one open arrears case the collections desk never walks back down its own ladder.

The 24 Oct finding (`docs/staging/SEAT_FINDING_THE_COLLECTIONS_DESK_WALKS_BACK_DOWN_ITS_OWN_LADDER_2026-10-24.md`):
a part-payment cleared the oldest bill (FIFO), the oldest bill left was younger, and the desk sent a
second reminder after a final notice, and re-made the plan offer each time an old bill re-crossed
day 28. Knowledge: `docs/market_research/company_debt_management.md`, "One case, one climb".

What each control names as its own defect:
  * `test_a_part_paid_case_holds_its_rung_and_offers_once_per_newly_missed_bill` -- the rung falls
    inside an open case; or a re-crossing of day 28 makes an offer; or a bill missed after the offer
    makes none. Its first assertion is that the hold-the-rung branch WAS taken, so a desk that never
    met a younger oldest-bill cannot pass it.
  * `test_the_order_check_refuses_a_walk_back` -- the order check accepts "final notice, then second
    reminder" on a balance-based segment.
  * `test_an_open_item_segment_is_not_made_to_climb` -- the climb is applied to every segment,
    including the invoice-by-invoice commercial ladder it was not examined for (GAP C2).
"""
from __future__ import annotations

import datetime as dt

import pytest

from company.billing.account_ledger import LedgerBook, LedgerEvent, LedgerEventType
from company.billing.arrears_engine import dunning_path
from company.billing.collections_journey import (
    ARRANGEMENT_OFFERED,
    PLAN_OFFER_STEP,
    PLAN_REOFFER_STEP,
    UnlawfulJourneyOrderError,
    assert_journey_order_lawful,
    climbs_per_case,
    ladder_actions,
)
from company.billing.payment_observation_consumer import PaymentObservationConsumer
from company.crm.account_hierarchy import Segment

START = dt.date(2016, 1, 1)
TERMS = 14


def _issued(n):
    return dt.date(START.year + (START.month - 1 + n) // 12, (START.month - 1 + n) % 12 + 1, 1)


def _event(account, kind, eid, amount, on):
    return LedgerEvent(event_id=eid, account_id=account, event_type=kind, amount_gbp=amount,
                       valid_time=on, transaction_time=dt.datetime.combine(on, dt.time(0, 0)),
                       invoice_ref=None)


def _part_paid_case(account="ACC-CLIMB"):
    """Nine £50 monthly bills, none paid on time. Mid-May a £150 lump clears the three oldest (FIFO),
    so the oldest bill left is from April and much younger than January's was."""
    consumer = PaymentObservationConsumer(ledger_book=LedgerBook())
    for n in range(9):
        consumer.ledger_book.post(_event(account, LedgerEventType.BILL_DEBIT, f"B:{n}", 50.0,
                                         _issued(n)))
    consumer.ledger_book.post(_event(account, LedgerEventType.PAYMENT_CREDIT, "P:lump", 150.0,
                                     dt.date(2016, 5, 16)))
    consumer.advance_collections_journey(account, dt.date(2016, 10, 31))
    journeys = consumer.collections_journeys.journeys()
    assert len(journeys) == 1 and journeys[0]["exit"] is None, journeys
    return journeys[0]


def test_a_part_paid_case_holds_its_rung_and_offers_once_per_newly_missed_bill():
    journey = _part_paid_case()
    assert_journey_order_lawful(journey, Segment.RESIDENTIAL)
    ladder = ladder_actions(Segment.RESIDENTIAL)
    trigger = {s.action: s.trigger_days_overdue for s in dunning_path(Segment.RESIDENTIAL)}
    rungs = [s for s in journey["stages"] if s["stage"] in ladder]

    # The rare branch CAN be taken: some rung was entered or held while the oldest bill was younger
    # than that rung's own trigger -- the date on which the old desk would have walked back down.
    held = [s for s in journey["stages"]
            if s["stage"] in ladder + (PLAN_REOFFER_STEP,)
            and s["days_overdue"] is not None
            and s["days_overdue"] < trigger[max(
                (r for r in rungs if r["on"] <= s["on"]), key=lambda r: ladder.index(r["stage"])
            )["stage"]]]
    assert held, "no date in this case met a younger oldest-bill, so the climb was never tested"

    indices = [ladder.index(s["stage"]) for s in rungs]
    assert indices == sorted(indices), [s["stage"] for s in rungs]

    first_offer = next(s["on"] for s in journey["stages"] if s["stage"] == PLAN_OFFER_STEP)
    missed_after = {(_issued(n) + dt.timedelta(days=TERMS + 1)).isoformat() for n in range(9)}
    missed_after = {d for d in missed_after if d > first_offer}
    reoffers = [s["on"] for s in journey["stages"] if s["stage"] == PLAN_REOFFER_STEP]
    plan_offers = [s for s in journey["stages"] if s["stage"] == PLAN_OFFER_STEP]
    assert len(plan_offers) == 1, "the plan-offer rung was re-entered: a re-crossing made an offer"
    assert set(reoffers) == missed_after, (sorted(reoffers), sorted(missed_after))
    offers = [s for s in journey["stages"] if s["stage"] == ARRANGEMENT_OFFERED]
    assert len(offers) == 1 + len(missed_after)


def test_the_order_check_refuses_a_walk_back():
    journey = _part_paid_case()
    stages = journey["stages"]
    top = max((s for s in stages if s["stage"] in ladder_actions(Segment.RESIDENTIAL)),
              key=lambda s: ladder_actions(Segment.RESIDENTIAL).index(s["stage"]))
    walked = dict(journey, stages=stages + [dict(top, stage="reminder_2", on=stages[-1]["on"])])
    with pytest.raises(UnlawfulJourneyOrderError, match="walks back down"):
        assert_journey_order_lawful(walked, Segment.RESIDENTIAL)


def test_an_open_item_segment_is_not_made_to_climb():
    assert climbs_per_case(Segment.RESIDENTIAL) and climbs_per_case(Segment.MICRO_SME)
    assert not climbs_per_case(Segment.SME) and not climbs_per_case(Segment.IC)
    on = "2016-03-01"
    falls = {"account_id": "ACC-IC", "exit": None, "stages": [
        {"stage": "missed_payment", "on": on}, {"stage": "final_demand", "on": on},
        {"stage": "interest_notice", "on": on}]}
    assert_journey_order_lawful(falls, Segment.IC)
