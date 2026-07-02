"""SIM-side customer satisfaction model (Gap 3 Dim 4 ground truth).

Satisfaction is a latent construct computed from SIM-internal signals
(rate history, income stress, tenure). This is the ground truth the SIM
uses to adjust actual churn probability.

The company approximates satisfaction via company/crm/satisfaction_accumulator.py
using only company observables (billing records, CSS surveys, complaints).
That approximation differs from this ground truth -- creating a realistic
prediction gap between what the company forecasts and what actually happens.
"""
from __future__ import annotations

from simulation.household import IncomeStress

BASELINE_SATISFACTION = 0.70
_BILL_SHOCK_DELTA = -0.10

_INCOME_STRESS_DELTA: dict[IncomeStress, float] = {
    IncomeStress.LOW: 0.0,
    IncomeStress.MODERATE: -0.05,
    IncomeStress.HIGH: -0.15,
}

_TENURE_BONUS_PER_YEAR = 0.02
_MAX_TENURE_BONUS = 0.10


def sim_satisfaction_score(
    bill_shock_count: int,
    tenure_years: float = 0.0,
    income_stress: IncomeStress | None = None,
) -> float:
    """Compute SIM-side ground-truth satisfaction score in [0.0, 1.0].

    Degrades with each rate shock and income stress; partially buffered by
    long tenure (loyal customers tolerate the same shock better than new ones).
    """
    score = BASELINE_SATISFACTION
    score += bill_shock_count * _BILL_SHOCK_DELTA
    if income_stress is not None:
        score += _INCOME_STRESS_DELTA.get(income_stress, 0.0)
    tenure_bonus = min(tenure_years * _TENURE_BONUS_PER_YEAR, _MAX_TENURE_BONUS)
    score += tenure_bonus
    return max(0.0, min(1.0, score))
