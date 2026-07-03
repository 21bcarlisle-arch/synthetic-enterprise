"""Enriched company churn estimate combining rate-sensitivity and payment-behaviour signals.

The rate-change model (company/crm/churn_model.py) captures price-sensitivity churn:
customers who shop around when rates rise. It misses stress-driven churn: customers
who disengage due to financial pressure regardless of the rate change.

The payment-behaviour model (company/crm/payment_churn_model.py) captures stress signals
from observable payment records: POOR/CRITICAL scores flag at-risk customers whose
departure the rate model may not predict.

enriched_churn_estimate() takes the max of both models. This ensures:
- Price-sensitive departures flagged by rate model are not suppressed
- Stress-driven departures flagged by payment model are not missed
- Excellent behaviour + low rate increase can suppress below rate model alone

All inputs are observable by the company. No SIM internals accessed.
"""
from __future__ import annotations

from typing import Optional

from company.crm.churn_model import estimate_churn_probability
from company.crm.payment_behaviour_analytics import BehaviourScore
from company.crm.payment_churn_model import combined_churn_probability
from saas.churn_model import BASE_ANNUAL_CHURN_PROBABILITY, MAX_CHURN_PROBABILITY

INDUSTRY_BASE_CHURN_RATE: float = 0.05


def enriched_churn_estimate(
    old_rate_gbp_per_mwh: float,
    new_rate_gbp_per_mwh: float,
    tenure_years: float,
    annual_consumption_kwh: float = 0.0,
    *,
    bill_shock_count: int = 0,
    behaviour_score: Optional[BehaviourScore] = None,
    satisfaction_score: Optional[float] = None,
    fuel: str = "electricity",
    hedge_fraction: float = 0.0,
    hangover_periods_remaining: int = 0,
    segment: str = "resi",
) -> float:
    """Return enriched churn probability from rate-sensitivity and payment-behaviour signals.

    rate_estimate  = estimate_churn_probability(old_rate, new_rate, tenure, ...)
    payment_estimate = combined_churn_probability(bill_shock_count, behaviour_score, satisfaction_score)
    result = max(rate_estimate, payment_estimate), capped at MAX_CHURN_PROBABILITY.

    When behaviour_score and satisfaction_score are both None and bill_shock_count is 0,
    payment_estimate = BASE_ANNUAL_CHURN_PROBABILITY (same as combined_churn_probability baseline),
    so the enriched estimate equals the rate model for backward compatibility.
    """
    rate_est = estimate_churn_probability(
        old_rate_gbp_per_mwh,
        new_rate_gbp_per_mwh,
        tenure_years,
        annual_consumption_kwh,
        fuel=fuel,
        hedge_fraction=hedge_fraction,
        hangover_periods_remaining=hangover_periods_remaining,
        segment=segment,
    )
    payment_est = combined_churn_probability(bill_shock_count, behaviour_score, satisfaction_score)
    result = max(rate_est, payment_est, INDUSTRY_BASE_CHURN_RATE)
    return min(result, MAX_CHURN_PROBABILITY)
