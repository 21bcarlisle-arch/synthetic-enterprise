"""SIM-side churn adjustment for satisfaction (Gap 3 Dim 4).

Satisfaction-based churn multiplier applied to the SIM ground-truth churn
probability before retention modifier. Analogous to switching_propensity.py
for income stress.

This operates at the SIM physics layer -- NOT visible to the company.
"""
from __future__ import annotations

from saas.churn_model import MAX_CHURN_PROBABILITY

_HIGH_SATISFACTION_THRESHOLD = 0.80
_LOW_SATISFACTION_THRESHOLD = 0.50

_HIGH_SATISFACTION_MULTIPLIER = 0.85
_LOW_SATISFACTION_MULTIPLIER = 1.30


def satisfaction_churn_multiplier(satisfaction_score: float) -> float:
    """Return churn probability multiplier based on SIM satisfaction score."""
    if satisfaction_score >= _HIGH_SATISFACTION_THRESHOLD:
        return _HIGH_SATISFACTION_MULTIPLIER
    if satisfaction_score < _LOW_SATISFACTION_THRESHOLD:
        return _LOW_SATISFACTION_MULTIPLIER
    return 1.0


def adjust_churn_for_satisfaction(
    base_churn_probability: float,
    satisfaction_score: float,
) -> float:
    """Return adjusted churn probability after applying satisfaction multiplier."""
    multiplier = satisfaction_churn_multiplier(satisfaction_score)
    return min(base_churn_probability * multiplier, MAX_CHURN_PROBABILITY)
