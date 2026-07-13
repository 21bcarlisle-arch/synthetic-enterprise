"""Phase MV: Economic Life Events tests.

Tests for IncomeStress enum, economic event types, probability constants,
apply_events handlers, generate_life_events integration, and
HouseholdDemandRegister.income_stress_at_date.
"""

import pytest

from simulation.household import (
    IncomeStress,
    make_household,
)
from simulation.life_events import (
    LifeEvent,
    _DIVORCE_ANNUAL_PROB,
    _ILLNESS_ANNUAL_PROB,
    _INCOME_RECOVERY_ANNUAL_PROB,
    _JOB_LOSS_ANNUAL_PROB,
    _NEW_BABY_ANNUAL_PROB,
    _RETIREMENT_PROB_BY_ERA,
    apply_events,
    generate_life_events,
)


def _resi_customer(cid="C1", era="suburban_semi"):
    return {"customer_id": cid, "home_type": era, "epc_rating": "C", "segment": "resi"}


def _make_hh(cid="C1"):
    return make_household(_resi_customer(cid))


# ── 1-4: IncomeStress enum values ────────────────────────────────────────────

def test_income_stress_low_value():
    assert IncomeStress.LOW.value == "low"


def test_income_stress_moderate_value():
    assert IncomeStress.MODERATE.value == "moderate"


def test_income_stress_high_value():
    assert IncomeStress.HIGH.value == "high"


def test_income_stress_enum_has_three_members():
    assert len(list(IncomeStress)) == 3


# ── 5: Household default ─────────────────────────────────────────────────────

def test_household_default_income_stress_is_low():
    hh = _make_hh()
    assert hh.income_stress == IncomeStress.LOW


# ── 6-9: EventType includes new types ────────────────────────────────────────

def test_can_create_job_loss_life_event():
    evt = LifeEvent("C1", "2021-06-01", "job_loss", {})
    assert evt.event_type == "job_loss"


def test_can_create_income_recovery_life_event():
    evt = LifeEvent("C1", "2022-03-01", "income_recovery", {})
    assert evt.event_type == "income_recovery"


def test_can_create_new_baby_life_event():
    evt = LifeEvent("C1", "2019-08-15", "new_baby", {})
    assert evt.event_type == "new_baby"


def test_can_create_retirement_starts_life_event():
    evt = LifeEvent("C1", "2020-01-01", "retirement_starts", {})
    assert evt.event_type == "retirement_starts"


# ── 10-15: apply_events handlers ─────────────────────────────────────────────

def test_job_loss_sets_high_stress():
    hh = _make_hh()
    evt = LifeEvent("C1", "2020-06-01", "job_loss", {})
    hh2 = apply_events(hh, [evt])
    assert hh2.income_stress == IncomeStress.HIGH


def test_income_recovery_clears_high_stress():
    hh = _make_hh()
    e1 = LifeEvent("C1", "2020-06-01", "job_loss", {})
    e2 = LifeEvent("C1", "2021-04-01", "income_recovery", {})
    hh2 = apply_events(hh, [e1, e2])
    assert hh2.income_stress == IncomeStress.LOW


def test_new_baby_raises_low_to_moderate():
    hh = _make_hh()
    evt = LifeEvent("C1", "2019-07-01", "new_baby", {})
    hh2 = apply_events(hh, [evt])
    assert hh2.income_stress == IncomeStress.MODERATE


def test_new_baby_does_not_lower_high_stress():
    hh = _make_hh()
    e1 = LifeEvent("C1", "2019-03-01", "job_loss", {})
    e2 = LifeEvent("C1", "2020-07-01", "new_baby", {})
    hh2 = apply_events(hh, [e1, e2])
    assert hh2.income_stress == IncomeStress.HIGH


def test_retirement_raises_low_to_moderate():
    hh = _make_hh()
    evt = LifeEvent("C1", "2018-09-01", "retirement_starts", {})
    hh2 = apply_events(hh, [evt])
    assert hh2.income_stress == IncomeStress.MODERATE


def test_retirement_does_not_lower_high_stress():
    hh = _make_hh()
    e1 = LifeEvent("C1", "2017-05-01", "job_loss", {})
    e2 = LifeEvent("C1", "2019-04-01", "retirement_starts", {})
    hh2 = apply_events(hh, [e1, e2])
    assert hh2.income_stress == IncomeStress.HIGH


# ── 16-18: Probability constants ─────────────────────────────────────────────

def test_job_loss_prob_is_positive():
    assert 0 < _JOB_LOSS_ANNUAL_PROB < 0.1


def test_income_recovery_prob_is_plausible():
    assert 0.2 <= _INCOME_RECOVERY_ANNUAL_PROB <= 0.8


def test_retirement_prob_highest_for_1945_1964_era():
    era = "1945_1964"
    assert _RETIREMENT_PROB_BY_ERA[era] > _RETIREMENT_PROB_BY_ERA.get("post_2000", 0.0)


# ── 19-27: illness / divorce (W2_5_life_event_stream, 2026-07-13) ───────────

def test_can_create_illness_life_event():
    evt = LifeEvent("C1", "2021-02-01", "illness", {})
    assert evt.event_type == "illness"


def test_can_create_divorce_life_event():
    evt = LifeEvent("C1", "2022-09-01", "divorce", {})
    assert evt.event_type == "divorce"


def test_illness_sets_high_stress():
    hh = _make_hh()
    evt = LifeEvent("C1", "2020-06-01", "illness", {})
    hh2 = apply_events(hh, [evt])
    assert hh2.income_stress == IncomeStress.HIGH


def test_income_recovery_clears_illness_high_stress():
    hh = _make_hh()
    e1 = LifeEvent("C1", "2020-06-01", "illness", {})
    e2 = LifeEvent("C1", "2021-04-01", "income_recovery", {})
    hh2 = apply_events(hh, [e1, e2])
    assert hh2.income_stress == IncomeStress.LOW


def test_divorce_raises_low_to_moderate():
    hh = _make_hh()
    evt = LifeEvent("C1", "2019-07-01", "divorce", {})
    hh2 = apply_events(hh, [evt])
    assert hh2.income_stress == IncomeStress.MODERATE


def test_divorce_does_not_lower_high_stress():
    hh = _make_hh()
    e1 = LifeEvent("C1", "2019-03-01", "job_loss", {})
    e2 = LifeEvent("C1", "2020-07-01", "divorce", {})
    hh2 = apply_events(hh, [e1, e2])
    assert hh2.income_stress == IncomeStress.HIGH


def test_illness_prob_is_positive():
    assert 0 < _ILLNESS_ANNUAL_PROB < 0.1


def test_divorce_prob_is_positive():
    assert 0 < _DIVORCE_ANNUAL_PROB < 0.1


def test_generate_life_events_can_produce_illness_and_divorce():
    # Deterministic seed sweep: with enough households (varying seeds via
    # customer_id hash), at least one should draw an illness event and at
    # least one a divorce event over a 10-year window -- proves the new
    # branches are genuinely reachable from generate_life_events(), not
    # just from apply_events() in isolation.
    found_illness = False
    found_divorce = False
    for i in range(200):
        hh = _make_hh(cid=f"C{i}")
        events = generate_life_events(hh, 2016, 2025)
        types = {e.event_type for e in events}
        if "illness" in types:
            found_illness = True
        if "divorce" in types:
            found_divorce = True
        if found_illness and found_divorce:
            break
    assert found_illness, "expected at least one illness event across 200 seeded households"
    assert found_divorce, "expected at least one divorce event across 200 seeded households"


# ── 19-20: generate_life_events and household_demand integration ──────────────

def test_generate_life_events_returns_list_for_resi():
    hh = _make_hh()
    events = generate_life_events(hh, 2016, 2025, seed=42)
    assert isinstance(events, list)


def test_make_household_has_income_stress_attribute():
    hh = make_household({"customer_id": "C99", "home_type": "urban_flat", "epc_rating": "D", "segment": "resi"})
    assert hasattr(hh, "income_stress")
    assert hh.income_stress in list(IncomeStress)
