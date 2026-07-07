"""Solicited feedback survey engine (Phase RU, FEEDBACK_AND_REPUTATION.md Layer 1).

SIM-side: dispatches CSAT/NPS surveys and complaint-resolution outcomes off
the true satisfaction score (simulation/sim_satisfaction.py) and models
realistic response/occurrence behaviour rather than an oracle read:

- Survey response propensity is U-shaped (very satisfied and very
  dissatisfied customers respond; the silent middle mostly doesn\'t), a low
  base rate, further suppressed under income stress (the overwhelmed don\'t
  answer surveys). A real respondent reports a noisy, rounded version of
  their true state, not a clean read.
- Complaints occur probabilistically off the same bill-shock signal
  saas/contact_model.py already uses (a confusing/shocking bill drives
  contact), then resolve on a randomised timer against the real 56-day
  Ombudsman SLC window (company/crm/complaints.py OMBUDSMAN_ESCALATION_DAYS).

The company only ever observes the response/outcome -- never
sim_satisfaction_score itself. That measurement gap is the point (Phase RU
basis-risk display).

All dispatch is deterministic: `random.Random(f"{kind}_{customer_id}_{date}")`,
matching the existing convention in simulation/customer_events.py.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

from company.core.reputation_index import ReputationEventType
from simulation.household import IncomeStress

# --- Survey response propensity -------------------------------------------

BASE_RESPONSE_RATE = 0.08
HIGH_SATISFACTION_THRESHOLD = 0.80
LOW_SATISFACTION_THRESHOLD = 0.35
EXTREME_RESPONSE_BONUS = 0.12
RESPONSE_NOISE_STD = 0.08

_INCOME_STRESS_RESPONSE_MULTIPLIER: dict[IncomeStress, float] = {
    IncomeStress.LOW: 1.0,
    IncomeStress.MODERATE: 0.8,
    IncomeStress.HIGH: 0.55,
}


def response_propensity(
    true_satisfaction: float, income_stress: Optional[IncomeStress] = None
) -> float:
    """U-shaped survey response rate: the silent middle mostly doesn\'t answer."""
    rate = BASE_RESPONSE_RATE
    if (
        true_satisfaction >= HIGH_SATISFACTION_THRESHOLD
        or true_satisfaction <= LOW_SATISFACTION_THRESHOLD
    ):
        rate += EXTREME_RESPONSE_BONUS
    if income_stress is not None:
        rate *= _INCOME_STRESS_RESPONSE_MULTIPLIER.get(income_stress, 1.0)
    return max(0.0, min(1.0, rate))


def _noisy_reported_fraction(true_satisfaction: float, rng: random.Random) -> float:
    """A real respondent reports a noisy, rounded version of their true state."""
    noisy = true_satisfaction + rng.gauss(0.0, RESPONSE_NOISE_STD)
    return max(0.0, min(1.0, noisy))


@dataclass(frozen=True)
class CSATDispatchResult:
    customer_id: str
    surveyed_date: str
    responded: bool
    score_0_10: Optional[float] = None


@dataclass(frozen=True)
class NPSDispatchResult:
    customer_id: str
    surveyed_date: str
    responded: bool
    score_0_10: Optional[int] = None


def dispatch_csat_survey(
    customer_id: str,
    event_date: str,
    true_satisfaction: float,
    income_stress: Optional[IncomeStress] = None,
) -> CSATDispatchResult:
    """Post-event CSAT dispatch. Score is 0-10 (matches company/crm/css_tracker.py scale)."""
    rng = random.Random(f"csat_{customer_id}_{event_date}")
    propensity = response_propensity(true_satisfaction, income_stress)
    if rng.random() >= propensity:
        return CSATDispatchResult(customer_id, event_date, responded=False)
    score = round(_noisy_reported_fraction(true_satisfaction, rng) * 10.0, 1)
    return CSATDispatchResult(customer_id, event_date, responded=True, score_0_10=score)


def dispatch_nps_survey(
    customer_id: str,
    event_date: str,
    true_satisfaction: float,
    income_stress: Optional[IncomeStress] = None,
) -> NPSDispatchResult:
    """Renewal-cadence NPS dispatch (company/crm/nps_tracker.py\'s real data source)."""
    rng = random.Random(f"nps_{customer_id}_{event_date}")
    propensity = response_propensity(true_satisfaction, income_stress)
    if rng.random() >= propensity:
        return NPSDispatchResult(customer_id, event_date, responded=False)
    score = round(_noisy_reported_fraction(true_satisfaction, rng) * 10.0)
    score = max(0, min(10, score))
    return NPSDispatchResult(customer_id, event_date, responded=True, score_0_10=score)


# --- Complaint occurrence + resolution timing ------------------------------

COMPLAINT_BASE_PROBABILITY = 0.03
BILL_SHOCK_COMPLAINT_PENALTY = 0.35

# Resolution-outcome bands, evaluated against company/crm/complaints.py\'s real
# OMBUDSMAN_ESCALATION_DAYS (56) SLC window:
ON_TIME_DAYS_MAX = 10
OMBUDSMAN_ESCALATION_PROBABILITY = 0.08
OMBUDSMAN_UPHELD_PROBABILITY = 0.5
LATE_BUT_WITHIN_SLC_PROBABILITY = 0.25


@dataclass(frozen=True)
class ComplaintResolutionOutcome:
    customer_id: str
    event_date: str
    occurred: bool
    reputation_event_type: Optional[ReputationEventType] = None
    days_to_resolve: Optional[int] = None


def dispatch_complaint_and_resolution(
    customer_id: str, event_date: str, bill_shock_occurred: bool
) -> ComplaintResolutionOutcome:
    """Roll whether a complaint occurs this term, and if so how it resolves.

    Reuses saas/contact_model.py\'s insight (a confusing/shocking bill drives
    contact) at this loop\'s native per-renewal-term granularity rather than
    the monthly-bill granularity contact_model.py itself operates at --
    GRI must be fed causally, in-order, inside the same loop that reads
    activation_energy_multiplier() for that customer\'s later renewals, so
    the dispatch has to live here rather than in a downstream billing pass.
    """
    rng = random.Random(f"complaint_{customer_id}_{event_date}")
    probability = COMPLAINT_BASE_PROBABILITY + (
        BILL_SHOCK_COMPLAINT_PENALTY if bill_shock_occurred else 0.0
    )
    if rng.random() >= probability:
        return ComplaintResolutionOutcome(customer_id, event_date, occurred=False)

    outcome_roll = rng.random()
    if outcome_roll < OMBUDSMAN_ESCALATION_PROBABILITY:
        days = rng.randint(57, 120)
        upheld = rng.random() < OMBUDSMAN_UPHELD_PROBABILITY
        event_type = (
            ReputationEventType.COMPLAINT_UPHELD_AT_OMBUDSMAN
            if upheld
            else ReputationEventType.COMPLAINT_RESOLVED_LATE
        )
        return ComplaintResolutionOutcome(customer_id, event_date, True, event_type, days)
    if outcome_roll < OMBUDSMAN_ESCALATION_PROBABILITY + LATE_BUT_WITHIN_SLC_PROBABILITY:
        days = rng.randint(ON_TIME_DAYS_MAX + 1, 56)
        return ComplaintResolutionOutcome(
            customer_id, event_date, True, ReputationEventType.COMPLAINT_RESOLVED_LATE, days
        )
    days = rng.randint(1, ON_TIME_DAYS_MAX)
    return ComplaintResolutionOutcome(
        customer_id, event_date, True, ReputationEventType.COMPLAINT_RESOLVED_ON_TIME, days
    )
