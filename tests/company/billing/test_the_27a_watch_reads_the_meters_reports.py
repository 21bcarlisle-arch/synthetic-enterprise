"""The 27A watch reads what the prepayment meter reports, and its record lapses with its reads.

Defect each leg names: a watch with no door behind it returning a record (a watch that cannot see
what it watches); a record that outlives its last read; an interruption the meter reported that
the watch drops; a world whose meter never self-disconnects (a watch never tested), or reports a
week not yet lived; a seam that tells the company a meter it has not yet changed.
"""
from __future__ import annotations

import datetime as dt

from company.billing.collections_journey import (
    WATCH_READ_INTERVAL_DAYS,
    CollectionsJourneyDesk,
)
from company.billing.winter_moratorium import (
    NO_SELF_DISCONNECTION_WATCH,
    SELF_DISCONNECTION_WATCH,
    EnforcementAction,
    EnforcementCase,
    may_take,
)
from company.interfaces.sim_interface import LiveSimInterface, StubSimInterface
from simulation.payment_method_dynamics import TOP_UPS_NOT_DRAWN, meter_supply_events
from simulation.plan_offer_response import HouseholdPlanBook

SEED = 20240101
MOVED, ON = dt.date(2024, 1, 1), dt.date(2024, 3, 1)


def _desk(seam):
    return CollectionsJourneyDesk(view_at=lambda *a: {}, refuse_dunning_of_cleared_debt=lambda *a: None,
                                  plan_offers=seam, post_cash=lambda *a: None)


def test_the_meter_reports_interruptions_at_its_weekly_share_and_never_ahead():
    none = meter_supply_events("C1", None, ON, base_seed=SEED, weekly_share=1.0)
    assert none["interruptions"] == [] and not none["on_meter"]
    every = meter_supply_events("C1", MOVED, ON, base_seed=SEED, weekly_share=1.0)
    assert [e["on"] for e in every["interruptions"]] == [
        (MOVED + dt.timedelta(days=7 * n)).isoformat() for n in range(1, 9)]
    assert meter_supply_events("C1", MOVED, ON, base_seed=SEED, weekly_share=0.0)["interruptions"] == []
    assert every["top_ups"] is None and every["top_ups_reason"] == TOP_UPS_NOT_DRAWN
    # At the shipped share the world does self-disconnect, near the toggle's rate.
    through = MOVED + dt.timedelta(days=7 * 52)
    weeks = hits = 0
    for n in range(500):
        hits += len(meter_supply_events(f"C{n}", MOVED, through, base_seed=SEED)["interruptions"])
        weeks += 52
    assert 0.012 < hits / weeks < 0.027, hits / weeks


def test_the_live_seam_reports_only_a_meter_the_world_has_changed():
    book = HouseholdPlanBook()
    live = LiveSimInterface(household_plans=book)
    before = live.get_meter_supply_events("C1", ON.isoformat())
    assert before["interruptions"] == [] and not before["on_meter"]
    book.record_meter("C1", MOVED, 100.0)
    assert not live.get_meter_supply_events("C1", (MOVED - dt.timedelta(days=1)).isoformat())["on_meter"]
    assert live.get_meter_supply_events("C1", ON.isoformat())["on_meter"]
    assert LiveSimInterface().get_meter_supply_events("C1", ON.isoformat())["interruptions"] is None


class _Meter:
    def __init__(self, interruptions=None):
        self.interruptions = interruptions

    def get_meter_supply_events(self, account_id, through):
        rows = None if self.interruptions is None else [
            {"on": d.isoformat()} for d in self.interruptions if d.isoformat() <= through]
        return {"interruptions": rows, "top_ups": None, "top_ups_reason": "", "on_meter": True,
                "reason": ""}


def test_the_watch_is_dated_by_its_reads_and_keeps_every_interruption():
    # The permit leg first: a door that answers arms the watch from the day asked (27A.1).
    seen = [dt.date(2024, 1, 8), dt.date(2024, 2, 5)]
    desk = _desk(_Meter(seen))
    record = desk.watch_self_disconnection("C1", ON)
    assert record.kind == SELF_DISCONNECTION_WATCH and record.unusable_on(ON) is None
    assert record.learned_on == ON
    assert record.lapses_on == ON + dt.timedelta(days=WATCH_READ_INTERVAL_DAYS)
    assert record.evidence == tuple(seen) and desk.self_disconnections("C1") == seen
    # Unread, it lapses the next day: the record outlives no read.
    assert record.unusable_on(ON + dt.timedelta(days=1)) is not None
    # A read the door cannot answer does not refresh it.
    desk._plan_offers.interruptions = None
    later = desk.watch_self_disconnection("C1", ON + dt.timedelta(days=3))
    assert later.learned_on == ON and later.unusable_on(ON + dt.timedelta(days=3)) is not None
    # No door, or one that has never answered: no watch at all.
    assert _desk(_Meter(None)).watch_self_disconnection("C1", ON) is None
    assert _desk(StubSimInterface()).watch_self_disconnection("C1", ON) is None
    assert _desk(object()).watch_self_disconnection("C1", ON) is None


def test_the_consent_gate_takes_the_watch_and_refuses_without_it():
    # The desk wires its own watch to the gate wherever it has a world door, and none without one.
    desk = _desk(_Meter([]))
    assert desk.self_disconnection_watch == desk.watch_self_disconnection
    assert _desk(None).self_disconnection_watch is None
    watch = desk.self_disconnection_watch("C1", ON)
    case = dict(account_id="C1", as_of=ON, arrangement_offered=True, on_prepayment=False)
    from company.billing.prepayment_suitability import (
        SuitabilityAnswers,
        assess_prepayment_suitability,
    )
    clear = SuitabilityAnswers(ON, **{f: False for f in SuitabilityAnswers.__dataclass_fields__
                                      if f != "asked_on"})
    finding = assess_prepayment_suitability(ON, answers=clear)
    with_watch = may_take(EnforcementAction.CONSENT_PPM_OFFER, EnforcementCase(
        **case, suitability=finding, self_disconnection_watch=watch))
    assert with_watch.permitted, with_watch.reason
    without = may_take(EnforcementAction.CONSENT_PPM_OFFER, EnforcementCase(
        **case, suitability=finding))
    assert not without.permitted and NO_SELF_DISCONNECTION_WATCH in without.reason
