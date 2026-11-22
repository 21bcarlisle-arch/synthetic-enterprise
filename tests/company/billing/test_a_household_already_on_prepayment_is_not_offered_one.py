"""A Consent prepayment offer is refused to a household already on a prepayment meter (C32 tenth
pass, class 6).

Defect named: `EnforcementCase` carried no payment method, so the gate could not refuse a PPM
offer on the ground that the household already pays that way. On the desk, a second journey on an
account whose meter this desk had already moved asked the world to move it again, and the re-fit
reset the meter's debt record (`_meters`), dropping the deductions already posted.
"""
from __future__ import annotations

import dataclasses
import datetime as dt

from company.billing.collections_journey import (
    ARRANGEMENT_OFFERED,
    PREPAYMENT,
    PREPAYMENT_WITHHELD,
    CollectionsJourneyDesk,
    _Journey,
)
from company.billing.winter_moratorium import (
    ALREADY_ON_PREPAYMENT,
    PAYMENT_METHOD_NOT_HELD,
    EnforcementAction,
    may_take,
)
from company.crm.account_hierarchy import Segment
from tests.company.billing.test_the_enforcement_table import BASE

MOVED = dt.date(2024, 1, 1)
AGAIN = dt.date(2024, 6, 3)


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
    clear = SuitabilityAnswers(MOVED, **{f: False for f in SuitabilityAnswers.__dataclass_fields__
                                         if f != "asked_on"})
    desk.prepayment_suitability = lambda a, on: assess_prepayment_suitability(on, answers=clear)
    return desk


def _offer(desk, on):
    journey = _Journey("C1", Segment.RESIDENTIAL)
    journey.stages.append({"stage": ARRANGEMENT_OFFERED, "on": on.isoformat(),
                           "household_acceptance": False})  # declined: 27.8 answered
    desk._offer_prepayment(journey, on, {"undisputed_overdue_gbp": 300.0, "max_days_overdue": 95})
    return journey


def test_the_gate_refuses_each_ppm_move_on_a_household_already_on_one_and_permits_otherwise():
    moves = (EnforcementAction.CONSENT_PPM_OFFER, EnforcementAction.WARRANT_PPM_INSTALL,
             EnforcementAction.REMOTE_SWITCH_TO_PREPAY)
    for action in moves:  # the permit leg first: a gate that refuses everything passes the rest
        assert may_take(action, BASE).permitted, may_take(action, BASE).reason
        on_one = may_take(action, dataclasses.replace(BASE, on_prepayment=True))
        assert on_one.refusals == (("already_on_prepayment", ALREADY_ON_PREPAYMENT),), on_one
        unknown = may_take(action, dataclasses.replace(BASE, on_prepayment=None))
        assert unknown.refusals == (("already_on_prepayment", PAYMENT_METHOD_NOT_HELD),), unknown
    # A meter recovery needs the meter: the column does not bar it.
    assert may_take(EnforcementAction.METER_RECOVERY,
                    dataclasses.replace(BASE, on_prepayment=True)).permitted


def test_the_desk_does_not_offer_a_second_meter_to_a_household_on_the_one_it_fitted():
    seam = _Meter()
    desk = _desk(seam)
    assert _offer(desk, MOVED).exit == PREPAYMENT  # the first offer can be taken
    fitted = list(desk._meters["C1"])
    desk._meters["C1"][2] = 4  # deductions posted since the move
    again = _offer(desk, AGAIN)
    assert seam.moves == 1, "the world was asked to move a meter the desk had already moved"
    assert again.exit is None and again.stages[-1]["stage"] == PREPAYMENT_WITHHELD
    assert ALREADY_ON_PREPAYMENT in again.stages[-1]["decision"]
    assert desk._meters["C1"] == fitted[:2] + [4], "the re-fit reset the meter's debt record"
