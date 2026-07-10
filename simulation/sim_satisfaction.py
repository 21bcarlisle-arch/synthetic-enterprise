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

import hashlib

from simulation.household import IncomeStress
from simulation.household_segments import PaymentChannel

BASELINE_SATISFACTION = 0.70
_BILL_SHOCK_DELTA = -0.10

_INCOME_STRESS_DELTA: dict[IncomeStress, float] = {
    IncomeStress.LOW: 0.0,
    IncomeStress.MODERATE: -0.05,
    IncomeStress.HIGH: -0.15,
}

_TENURE_BONUS_PER_YEAR = 0.02
_MAX_TENURE_BONUS = 0.10

# Ofgem/Citizens Advice "Energy Consumer Satisfaction Survey" Wave 20 (BMG
# Research, published May 2025, fieldwork Jan 2025, n=3,854): Direct Debit
# 82% satisfied, Standard Credit 76% -- a persistent ~6pt gap, present in
# every wave since tracking began (docs/market_research/ASSUMPTIONS.md,
# "Customer Satisfaction Population Distribution", 2026-07-10). Closes a
# previously-flagged gap: payment_channel_for_customer() already existed as
# an archetype but was never consumed by this model.
_PAYMENT_CHANNEL_DELTA: dict[PaymentChannel, float] = {
    PaymentChannel.DIRECT_DEBIT: 0.0,
    PaymentChannel.STANDARD_CREDIT: -0.06,
}

# Same source: even respondents who share the SAME coarse "satisfied"
# classification split materially further underneath it (very satisfied 38%
# vs satisfied 42%, ~47/53 within one band) -- real per-customer
# heterogeneity exists even within one shared circumstance cohort, which this
# model previously had none of at all (every customer with the same
# bill-shock count and income-stress tier got the IDENTICAL score -- measured
# live: 67%/28% of all datapoints sitting at exactly one of two values).
# +/-0.04 is an honestly-flagged CALIBRATION CHOICE, not a directly published
# per-customer standard deviation (no source publishes individual-level
# variance within a single cohort) -- the direction and existence of
# heterogeneity is anchored, the exact magnitude is not.
_INDIVIDUAL_VARIATION_RANGE = 0.08


def _individual_variation(customer_id: str) -> float:
    """Deterministic per-customer heterogeneity term in [-range/2, +range/2]."""
    digest = hashlib.sha256(f"satisfaction_variation_{customer_id}".encode()).hexdigest()
    frac = int(digest[:8], 16) / 0xFFFFFFFF
    return (frac - 0.5) * _INDIVIDUAL_VARIATION_RANGE


def sim_satisfaction_score(
    bill_shock_count: int,
    tenure_years: float = 0.0,
    income_stress: IncomeStress | None = None,
    payment_channel: PaymentChannel | None = None,
    customer_id: str | None = None,
) -> float:
    """Compute SIM-side ground-truth satisfaction score in [0.0, 1.0].

    Degrades with each rate shock and income stress; partially buffered by
    long tenure (loyal customers tolerate the same shock better than new
    ones); a real payment-method gap and per-customer heterogeneity term
    apply when the corresponding optional args are supplied (both
    backward-compatible -- omitting them reproduces the prior behaviour).
    """
    score = BASELINE_SATISFACTION
    score += bill_shock_count * _BILL_SHOCK_DELTA
    if income_stress is not None:
        score += _INCOME_STRESS_DELTA.get(income_stress, 0.0)
    tenure_bonus = min(tenure_years * _TENURE_BONUS_PER_YEAR, _MAX_TENURE_BONUS)
    score += tenure_bonus
    if payment_channel is not None:
        score += _PAYMENT_CHANNEL_DELTA.get(payment_channel, 0.0)
    if customer_id is not None:
        score += _individual_variation(customer_id)
    return max(0.0, min(1.0, score))
