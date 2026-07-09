"""SIM-side income stress -> switching propensity (Dim 3 behavioural).

Encodes the UK energy market vulnerability trap: financially stressed customers
tend NOT to switch suppliers even when unhappy. Friction costs (deposit requirements,
direct debit setup, mental load) suppress switching more for HIGH-stress households.

LOW-stress customers are slightly MORE likely to shop around when they experience
price pain -- they have the cognitive bandwidth and financial flexibility to compare.

This is SIM ground truth applied to ACTUAL churn outcomes. The company does not
read income_stress directly -- it uses observable payment behaviour (Phases MX/MY).
"""
from __future__ import annotations

from simulation.household import IncomeStress

_MAX_CHURN_PROBABILITY = 0.95

STRESS_SWITCHING_MULTIPLIER: dict[IncomeStress, float] = {
    IncomeStress.LOW:      1.10,
    IncomeStress.MODERATE: 0.85,
    IncomeStress.HIGH:     0.65,
}


def stress_switching_multiplier(income_stress: IncomeStress | None) -> float:
    """Return the switching-propensity multiplier for a given income stress level.

    None maps to LOW (baseline -- no stress data available).
    """
    if income_stress is None:
        return STRESS_SWITCHING_MULTIPLIER[IncomeStress.LOW]
    return STRESS_SWITCHING_MULTIPLIER[income_stress]


# Layer 2 dimension 3 (tenure, 2026-07-09): real suppliers see lower
# switching among renters -- private renters often can't freely switch
# (landlord-controlled accounts in some tenancies, more transient outlook,
# less incentive to invest effort in a home they don't own); social
# renters similarly. EHS anchors the population SHARE of each tenure type
# (household_segments.py::TENURE_POPULATION_SHARE) but does NOT publish a
# switching-suppression magnitude -- these multipliers are a calibration
# CHOICE (NOT independently sourced), kept modest, per the Anchored-noise
# law. Owner-occupier is the baseline (1.0, no suppression).
TENURE_SWITCHING_MULTIPLIER: dict[str, float] = {
    "owner_occupier": 1.0,
    "private_renter": 0.80,
    "social_renter": 0.75,
}


def tenure_switching_multiplier(tenure: str | None) -> float:
    """Return the switching-propensity multiplier for a given tenure
    archetype. None maps to owner_occupier (baseline -- no tenure data
    available), matching stress_switching_multiplier's None convention."""
    if tenure is None:
        return TENURE_SWITCHING_MULTIPLIER["owner_occupier"]
    return TENURE_SWITCHING_MULTIPLIER.get(tenure, TENURE_SWITCHING_MULTIPLIER["owner_occupier"])


def adjust_churn_probability(base_prob: float, income_stress: IncomeStress | None,
                              tenure: str | None = None) -> float:
    """Apply income stress (and optionally tenure) modifiers to a base
    churn probability.

    `tenure` is optional -- default None preserves the exact original
    behaviour (income-stress-only). Result capped at 0.95; cannot go
    negative.
    """
    multiplier = stress_switching_multiplier(income_stress) * tenure_switching_multiplier(tenure)
    return min(max(base_prob * multiplier, 0.0), _MAX_CHURN_PROBABILITY)
