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


def adjust_churn_probability(base_prob: float, income_stress: IncomeStress | None) -> float:
    """Apply income stress modifier to a base churn probability.

    Result capped at 0.95; cannot go negative.
    """
    multiplier = stress_switching_multiplier(income_stress)
    return min(max(base_prob * multiplier, 0.0), _MAX_CHURN_PROBABILITY)
