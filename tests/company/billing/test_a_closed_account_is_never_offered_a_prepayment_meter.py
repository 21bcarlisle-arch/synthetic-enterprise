"""No step at a premise this company no longer supplies (2026-11-23).

Defect named: nothing on the Consent path asked whether the account was still supplied. On the 2016
run with 7527a2e36's closing collection forced off, ACC-SYN-2016-005 closed in June 2016, its journey
opened on 29 Jul, the desk offered an arrangement on 25 Aug, and on 26 Oct `_offer_prepayment` asked
the world to fit a prepayment meter by Consent at a premise the company had left.
`docs/staging/SEAT_FINDING_THE_DESK_OFFERS_A_PREPAYMENT_METER_TO_A_HOUSEHOLD_THAT_HAS_LEFT_2026-11-23.md`.

The closure the gate reads is the company's own record (`note_supply_ended`, told as the run closes
the account), never the world's `churned_billing_accounts`.
"""
from __future__ import annotations

import dataclasses
import datetime as dt

import pytest

from company.billing.collections_journey import (
    ARRANGEMENT_OFFERED,
    MISSED_PAYMENT,
    PREPAYMENT,
    PREPAYMENT_OFFERED,
    PREPAYMENT_WITHHELD,
    CollectionsJourneyDesk,
    _Journey,
)
from company.billing.winter_moratorium import (
    COVERED,
    ENFORCEMENT_TABLE,
    SUPPLY_ENDED,
    EnforcementAction,
    may_take,
)
from company.compliance.domain_invariants import (
    ALL_INVARIANTS,
    NO_PREMISE_STEP_AFTER_SUPPLY_ENDED,
    PremiseStepAfterSupplyEndedError,
    premise_steps_after_supply_ended,
)
from company.crm.account_hierarchy import Segment
from tests.company.billing.test_the_enforcement_table import BASE

ACCOUNT = "ACC-SYN-2016-005"
LAST_SUPPLIED = dt.date(2016, 6, 30)
OPENED, ARRANGED, CONSENT = dt.date(2016, 7, 29), dt.date(2016, 8, 25), dt.date(2016, 10, 26)


class _Meter:
    def __init__(self):
        self.moves = 0

    def request_prepayment_move(self, account_id, requested_on, debt, months):
        self.moves += 1
        return {"moved": True, "reason": "household agreed"}

    def get_meter_supply_events(self, account_id, through):
        return {"interruptions": [], "top_ups": None, "top_ups_reason": "", "on_meter": True,
                "reason": ""}

    def get_meter_recoveries(self, account_id, moved_on, debt, through):
        return []


def _desk(seam):
    from company.billing.prepayment_suitability import (
        SuitabilityAnswers,
        assess_prepayment_suitability,
    )
    desk = CollectionsJourneyDesk(view_at=lambda *a: {},
                                  refuse_dunning_of_cleared_debt=lambda *a: None,
                                  plan_offers=seam, post_cash=lambda *a: None)
    clear = SuitabilityAnswers(OPENED, **{f: False for f in SuitabilityAnswers.__dataclass_fields__
                                          if f != "asked_on"})
    desk.prepayment_suitability = lambda a, on: assess_prepayment_suitability(on, answers=clear)
    return desk


def _the_2016_005_journey(desk):
    """ACC-SYN-2016-005's journey to the Consent rung: opened after it left, arrangement declined."""
    journey = _Journey(ACCOUNT, Segment.RESIDENTIAL)
    journey.stages.append({"stage": MISSED_PAYMENT, "on": OPENED.isoformat()})
    journey.stages.append({"stage": ARRANGEMENT_OFFERED, "on": ARRANGED.isoformat(),
                           "household_acceptance": False})  # declined: 27.8 answered
    desk._offer_prepayment(journey, CONSENT, {"undisputed_overdue_gbp": 300.0,
                                              "max_days_overdue": 95})
    return journey


def test_a_supplied_account_in_the_same_state_is_offered_the_meter():
    """The permit leg: without it a desk that refuses every Consent offer passes the test below."""
    seam = _Meter()
    desk = _desk(seam)
    journey = _the_2016_005_journey(desk)
    assert seam.moves == 1, [s.get("decision") for s in journey.stages]
    assert [s["stage"] for s in journey.stages[-2:]] == [PREPAYMENT_OFFERED, PREPAYMENT]


def test_the_desk_refuses_a_meter_at_a_premise_its_own_record_says_it_left():
    seam = _Meter()
    desk = _desk(seam)
    desk.note_supply_ended(ACCOUNT, LAST_SUPPLIED)
    journey = _the_2016_005_journey(desk)
    assert seam.moves == 0, "the world was asked to fit a meter at a premise the company had left"
    last = journey.stages[-1]
    assert last["stage"] == PREPAYMENT_WITHHELD and journey.exit is None
    assert SUPPLY_ENDED.format(last=LAST_SUPPLIED.isoformat()) in last["decision"]


def test_a_closure_told_after_the_step_date_does_not_reach_back():
    """The column reads the date: a step on or before the last day supplied is a supplied step."""
    seam = _Meter()
    desk = _desk(seam)
    desk.note_supply_ended(ACCOUNT, CONSENT)
    _the_2016_005_journey(desk)
    assert seam.moves == 1


def test_every_premise_action_reads_the_column_and_no_other_does():
    premise = {EnforcementAction.DISCONNECTION, EnforcementAction.WARRANT_PPM_INSTALL,
               EnforcementAction.REMOTE_SWITCH_TO_PREPAY, EnforcementAction.CONSENT_PPM_OFFER}
    reads = {a for a, row in ENFORCEMENT_TABLE.items() if row["account_still_supplied"] == COVERED}
    assert reads == premise
    left = dataclasses.replace(BASE, supply_ended_on=BASE.as_of - dt.timedelta(days=1))
    for action in EnforcementAction:
        assert may_take(action, BASE).permitted, may_take(action, BASE).reason
        refused = dict(may_take(action, left).refusals)
        assert ("account_still_supplied" in refused) == (action in premise), action


def test_the_invariant_finds_a_premise_step_after_supply_ended_and_the_desk_raises_on_it():
    record = {"account_id": ACCOUNT, "stages": [
        {"stage": MISSED_PAYMENT, "on": OPENED.isoformat()},
        {"stage": PREPAYMENT_OFFERED, "on": CONSENT.isoformat()}]}
    assert NO_PREMISE_STEP_AFTER_SUPPLY_ENDED in ALL_INVARIANTS
    found = premise_steps_after_supply_ended(record, LAST_SUPPLIED)
    assert [f["stage"] for f in found] == [PREPAYMENT_OFFERED]
    assert premise_steps_after_supply_ended(record, None) == []
    assert premise_steps_after_supply_ended(record, CONSENT) == []
    # A route that skips the gate is caught by the desk's own refusal over what it issued.
    desk = _desk(_Meter())
    desk.note_supply_ended(ACCOUNT, LAST_SUPPLIED)
    journey = _Journey(ACCOUNT, Segment.RESIDENTIAL)
    journey.enter(PREPAYMENT_OFFERED, CONSENT, "a route that never asked the gate", {})
    with pytest.raises(PremiseStepAfterSupplyEndedError, match=ACCOUNT):
        desk._refuse_issued(journey, 0, ACCOUNT, None)


def test_the_run_tells_the_desk_the_last_day_supplied_at_each_closure():
    """Reachability: both in-run closures hand the desk a date, so the column is not dead in a run."""
    import inspect

    import simulation.run_phase2b as run
    src = inspect.getsource(run._main)
    calls = [src[i:src.index(")\n", src.index("_final_bill_due(", i)) + 80]
             for i in range(len(src)) if src.startswith("_payment_triad.close_account(", i)]
    assert len(calls) == 2 and all("last_supplied=" in c for c in calls), calls
