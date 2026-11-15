"""Each interruption the 27A watch sees on a meter the desk fitted is answered, and the world counts
the Consent offers made to PSR-type households that concealed (C36).

Defect each leg names: a watch that sees and does nothing (27A.1 met, 27A.5 not); an interruption
answered twice on a re-read, or answered on a meter the desk never fitted; an ASC offer carrying a
picked amount (E6 is a gap, so the amount must be None with its reason); "multiple attempts using
various channels" met by one; a 9.1(b) referral that cannot fire, or fires on the first event; a
move that leaves no 27A.2/27A.8 record; a concealment count that counts disclosers or households
with no PSR-type circumstance, or that loses the offers the world refused.
"""
from __future__ import annotations

import datetime as dt

from company.billing.collections_journey import (
    ARRANGEMENT_OFFERED,
    ASC_AMOUNT_GAP,
    EMERGENCY_CREDIT_AMOUNT_GAP,
    PREPAYMENT,
    REASSESS_ON_INTERRUPTION_COUNT,
    CollectionsJourneyDesk,
    _Journey,
)
from company.crm.account_hierarchy import Segment
from company.interfaces.sim_interface import LiveSimInterface
from simulation.household import household_of
from simulation.payment_method_dynamics import consent_offers_to_concealing_households
from simulation.plan_offer_response import HouseholdPlanBook
from simulation.vulnerability_state import vulnerability_state

SEED = 20240101
MOVED = dt.date(2024, 1, 1)
EVENTS = [dt.date(2024, 1, 8), dt.date(2024, 2, 5), dt.date(2024, 3, 4)]


class _Meter:
    """A world door that moves the meter on asking and reports `interruptions` up to `through`."""

    def __init__(self, interruptions):
        self.interruptions = interruptions

    def request_prepayment_move(self, account_id, requested_on, debt, months):
        return {"moved": True, "reason": "household agreed"}

    def get_meter_supply_events(self, account_id, through):
        return {"interruptions": [{"on": d.isoformat()} for d in self.interruptions
                                  if d.isoformat() <= through],
                "top_ups": None, "top_ups_reason": "", "on_meter": True, "reason": ""}

    def get_meter_recoveries(self, account_id, moved_on, debt, through):
        return []


def _desk(seam):
    desk = CollectionsJourneyDesk(view_at=lambda *a: {},
                                  refuse_dunning_of_cleared_debt=lambda *a: None,
                                  plan_offers=seam, post_cash=lambda *a: None)
    from company.billing.prepayment_suitability import (
        SuitabilityAnswers,
        assess_prepayment_suitability,
    )
    clear = SuitabilityAnswers(MOVED, **{f: False for f in SuitabilityAnswers.__dataclass_fields__
                                         if f != "asked_on"})
    desk.prepayment_suitability = lambda a, on: assess_prepayment_suitability(on, answers=clear)
    return desk


def _fit(desk, account_id="C1"):
    journey = _Journey(account_id, Segment.RESIDENTIAL)
    journey.stages.append({"stage": ARRANGEMENT_OFFERED, "on": MOVED.isoformat(),
                           "household_acceptance": False})  # declined: 27.8 answered
    desk._offer_prepayment(journey, MOVED, {"undisputed_overdue_gbp": 300.0, "max_days_overdue": 95})
    assert journey.exit == PREPAYMENT, journey.stages
    return journey


def test_each_interruption_on_a_fitted_meter_is_answered_once_with_asc_contact_and_referral():
    desk = _desk(_Meter(EVENTS))
    _fit(desk)
    fitted = desk.self_disconnection_support["C1"][0]
    assert fitted["kind"] == "credit_facilities_on_meter"
    assert fitted["emergency_credit"]["available"] and fitted["emergency_credit"]["amount_gbp"] is None
    assert fitted["emergency_credit"]["amount_gap"] == EMERGENCY_CREDIT_AMOUNT_GAP
    assert fitted["told"]["what_each_is_and_how_repaid"]

    desk._read_meter_recoveries("C1", dt.date(2024, 2, 10))
    desk._read_meter_recoveries("C1", dt.date(2024, 2, 10))  # a re-read answers nothing again
    desk._read_meter_recoveries("C1", dt.date(2024, 3, 31))
    answered = [r for r in desk.self_disconnection_support["C1"]
                if r["kind"] == "interruption_answered"]
    assert [r["interrupted_on"] for r in answered] == [d.isoformat() for d in EVENTS]
    assert [r["answered_on"] for r in answered] == ["2024-02-10", "2024-02-10", "2024-03-31"]
    for r in answered:
        asc = r["additional_support_credit"]
        assert asc["offered"] and asc["amount_gbp"] is None and asc["amount_gap"] == ASC_AMOUNT_GAP
        assert asc["instalment_gbp"] is None and "27.8" in asc["repayment"]
        assert len(set(r["contact"]["channels"])) >= 2
    # The whole partition: the referral can be taken, and is not taken on the first event.
    referred = [r["suitability_reassessment"] is not None for r in answered]
    assert any(referred) and not all(referred)
    assert referred == [n + 1 >= REASSESS_ON_INTERRUPTION_COUNT for n in range(len(EVENTS))]
    assert all(r["suitability_reassessment"]["decided"] is None for r in answered[1:])


def test_an_interruption_on_a_meter_this_desk_did_not_fit_is_not_answered_as_its_own():
    desk = _desk(_Meter(EVENTS))
    desk.watch_self_disconnection("C1", dt.date(2024, 3, 31))
    assert desk.self_disconnections("C1") == EVENTS
    assert "C1" not in desk.self_disconnection_support


def _households(seed, n=4000):
    concealing = disclosing = clear = None
    for i in range(n):
        a = f"SYN-2020-{i:04d}"
        st = vulnerability_state(household_of(a), seed)
        if st.psr_type_vulnerable and not st.discloses_psr and concealing is None:
            concealing = a
        elif st.discloses_psr and disclosing is None:
            disclosing = a
        elif not st.psr_type_vulnerable and clear is None:
            clear = a
        if concealing and disclosing and clear:
            return concealing, disclosing, clear
    raise AssertionError("the world drew no concealing, disclosing and clear household")


def test_the_world_counts_consent_offers_to_concealing_households_and_nothing_crosses():
    concealing, disclosing, clear = _households(SEED)
    book = HouseholdPlanBook()
    live = LiveSimInterface(household_plans=book)
    for a in (concealing, concealing, disclosing, clear):
        said = live.request_prepayment_move(a, "2024-01-01", 300.0, 3)
        assert set(said) == {"moved", "reason"}  # the company learns only the answer
    book.record_consent_offer(concealing, dt.date(2024, 6, 1), True)
    count = consent_offers_to_concealing_households(book.consent_offers, SEED)
    assert count["offers"] == 5 and count["households_offered"] == 3
    assert count["offers_to_concealing_psr_type"] == 3
    assert count["concealing_psr_type_households_offered"] == 1
    assert count["meters_moved_on_concealing_psr_type"] == 1
    assert consent_offers_to_concealing_households([], SEED)["offers_to_concealing_psr_type"] == 0
