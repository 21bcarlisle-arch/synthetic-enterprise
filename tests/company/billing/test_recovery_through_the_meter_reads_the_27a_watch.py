"""Recovery through the meter reads the 27A watch: a deduction from a household the watch has seen
go off supply is paused, through a world door, and the world takes no deduction after it (C37).

Knowledge: commons `psr_eligibility_and_disconnection_protection.md` s.5, "Recovery through the
meter, on the 27A watch" (27A.1(b) routes support through 27.8; 27.8A(d)(iv) names a pause).

Defect each leg names: a gate that pauses every meter, or none (the partition control); a pause the
desk records but the world ignores, so deductions go on; a pause that reaches back over deductions
already taken; a gate that reads an interruption dated after the day it is asked; a pause lodged
twice; a door that cannot pause and silently drops the cash the meter took; a missing watch read as
"no self-disconnection".
"""
from __future__ import annotations

import datetime as dt

from company.billing import winter_moratorium as gate
from company.billing.collections_journey import NO_PAUSE_DOOR, CollectionsJourneyDesk
from company.billing.winter_moratorium import (
    NO_SELF_DISCONNECTION_WATCH,
    SELF_DISCONNECTING,
    SELF_DISCONNECTION_WATCH,
    EnforcementAction,
    EnforcementCase,
    may_take,
)
from company.interfaces.sim_interface import LiveSimInterface, StubSimInterface
from company.regulatory.priority_services_register import ProtectionRecord
from simulation.payment_method_dynamics import meter_recoveries
from simulation.plan_offer_response import HouseholdPlanBook

MOVED = dt.date(2024, 1, 1)
DEBT = 300.0


class _Meter:
    """A world door on a meter changed on MOVED: it reports `interruptions` up to `through`, takes
    the published weekly deduction, and honours a pause."""

    def __init__(self, interruptions):
        self.interruptions, self.paused_after, self.pause_asks = interruptions, None, []

    def get_meter_supply_events(self, account_id, through):
        return {"interruptions": [{"on": d.isoformat()} for d in self.interruptions
                                  if d.isoformat() <= through],
                "top_ups": None, "top_ups_reason": "", "on_meter": True, "reason": ""}

    def get_meter_recoveries(self, account_id, moved_on, debt, through):
        return meter_recoveries(debt, dt.date.fromisoformat(moved_on),
                                dt.date.fromisoformat(through), suspended_after=self.paused_after)

    def suspend_deduction(self, account_id, after, reason):
        self.pause_asks.append((account_id, after, reason))
        self.paused_after = self.paused_after or dt.date.fromisoformat(after)
        return {"suspended": True, "reason": reason}


class _NoPauseMeter(_Meter):
    suspend_deduction = property()  # hasattr() is False: the door has no pause


def _desk(seam):
    posted = []
    desk = CollectionsJourneyDesk(view_at=lambda *a: {},
                                  refuse_dunning_of_cleared_debt=lambda *a: None,
                                  plan_offers=seam, post_cash=lambda *a: posted.append(a))
    desk._meters["C1"] = [MOVED, DEBT, 0]
    return desk, posted


def _read(desk, *days):
    from company.crm.account_hierarchy import Segment
    for d in days:
        desk._read_meter_recoveries("C1", d, Segment.RESIDENTIAL)


def test_the_pause_can_be_taken_and_can_be_withheld():
    """The whole partition first: a quiet meter is never paused, an interrupted one is."""
    quiet, quiet_cash = _desk(_Meter([]))
    off, off_cash = _desk(_Meter([dt.date(2024, 2, 5)]))
    for desk in (quiet, off):
        _read(desk, dt.date(2024, 1, 31), dt.date(2024, 2, 10), dt.date(2024, 6, 30))
    assert "C1" not in quiet.meter_recovery_paused and "C1" in off.meter_recovery_paused
    assert len(quiet_cash) == 25 and len(off_cash) < len(quiet_cash)


def test_an_interruption_pauses_the_deduction_from_the_day_it_is_read_and_never_before():
    seam = _Meter([dt.date(2024, 2, 5)])
    desk, cash = _desk(seam)
    _read(desk, dt.date(2024, 1, 31), dt.date(2024, 2, 10), dt.date(2024, 6, 30))
    paused = desk.meter_recovery_paused["C1"]
    assert paused["on"] == "2024-02-10" and paused["suspended"] is True
    assert paused["grounds"] == ["slc_27a_self_disconnection"]
    assert SELF_DISCONNECTING in paused["reason"] and "2024-02-05" in paused["reason"]
    assert len(seam.pause_asks) == 1, "a pause was lodged more than once"
    # Taken before the desk could act (8, 15, 22, 29 Jan; 5 Feb) are posted; nothing after 10 Feb.
    days = [d for _a, _amt, d, _ref in cash]
    assert days == [MOVED + dt.timedelta(days=7 * n) for n in range(1, 6)]
    assert round(sum(a for _x, a, _d, _r in cash), 2) == round(5 * 6.01, 2)  # the rest stays owed


def test_a_door_that_cannot_pause_is_recorded_and_the_cash_taken_is_still_posted():
    desk, cash = _desk(_NoPauseMeter([dt.date(2024, 2, 5)]))
    _read(desk, dt.date(2024, 2, 10), dt.date(2024, 3, 31))
    paused = desk.meter_recovery_paused["C1"]
    assert paused["suspended"] is False and paused["door_reason"] == NO_PAUSE_DOOR
    assert len(cash) == 12  # every weekly deduction to 31 Mar, as the meter took them


def test_the_gate_on_recovery_reads_the_watch_and_cannot_see_the_future():
    on = dt.date(2024, 3, 1)

    def case(evidence=(), watch=True):
        record = (ProtectionRecord(SELF_DISCONNECTION_WATCH, on, on + dt.timedelta(days=1),
                                   met=True, evidence=tuple(evidence)) if watch else None)
        return EnforcementCase("C1", on, self_disconnection_watch=record)

    act = EnforcementAction.METER_RECOVERY
    assert act not in gate.UNROUTED_ACTIONS
    assert may_take(act, case()).permitted
    assert may_take(act, case([on + dt.timedelta(days=3)])).permitted, "read a future interruption"
    seen = may_take(act, case([dt.date(2024, 2, 5)]))
    assert not seen.permitted and SELF_DISCONNECTING in seen.reason
    blind = may_take(act, case(watch=False))
    assert not blind.permitted and NO_SELF_DISCONNECTION_WATCH in blind.reason
    # The Consent row is unchanged: a watch that has seen interruptions does not bar an offer.
    assert may_take(EnforcementAction.CONSENT_PPM_OFFER, case([dt.date(2024, 2, 5)])).refusals == \
        may_take(EnforcementAction.CONSENT_PPM_OFFER, case()).refusals


def test_the_world_honours_the_pause_and_refuses_one_with_no_meter():
    book = HouseholdPlanBook()
    book.record_meter("C1", MOVED, DEBT)
    live = LiveSimInterface(household_plans=book)
    before = live.get_meter_recoveries("C1", MOVED.isoformat(), DEBT, "2024-06-30")
    assert live.suspend_deduction("NOPE", "2024-02-10", "x")["suspended"] is False
    assert live.suspend_deduction("C1", "2024-02-10", "27A")["suspended"] is True
    assert live.suspend_deduction("C1", "2024-04-01", "later")["suspended"] is True
    after = live.get_meter_recoveries("C1", MOVED.isoformat(), DEBT, "2024-06-30")
    assert after == before[:len(after)] and [r["due"] for r in after][-1] == "2024-02-05"
    assert len(after) == 5 < len(before), "the first pause did not stand"
    assert StubSimInterface().suspend_deduction("C1", "2024-02-10", "x")["suspended"] is False
