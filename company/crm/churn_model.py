"""Company churn risk estimator -- observable-data only.

The company estimates churn probability from signals it can legitimately
observe: rate change percentage and customer tenure. It cannot read
saas/customer_reaction.py parameters (alpha, beta, bill-shock thresholds)
or the SIM computed churn_probability.

Algorithm: base_rate + rate_sensitivity x rate_increase_pct
           - tenure_discount x min(tenure_years, 5), clamped to [0.0, 0.95].

This will systematically differ from the SIM bill-shock model:
  - SIM uses: actual bill amount relative to a personal threshold
  - Company uses: rate change % (observable) rather than absolute bill impact
  - For high-consumption customers in crisis years: company under-estimates
    churn vs SIM -- the same epistemic failure that surprised real suppliers.
"""

BASE_CHURN_RATE = 0.10
RATE_SENSITIVITY = 0.8
TENURE_DISCOUNT_PER_YEAR = 0.01
MAX_TENURE_DISCOUNT_YEARS = 5
MAX_CHURN_PROBABILITY = 0.95


def estimate_churn_probability(
    old_rate_gbp_per_mwh: float,
    new_rate_gbp_per_mwh: float,
    tenure_years: float,
) -> float:
    """Estimate churn probability from observable renewal signals.

    old_rate: unit rate (GBP/MWh) on the expiring contract
    new_rate: unit rate (GBP/MWh) on the renewal offer
    tenure_years: years since the customer original acquisition date

    Returns: churn probability estimate in [0.0, 0.95]
    """
    if old_rate_gbp_per_mwh > 0:
        rate_increase_pct = (new_rate_gbp_per_mwh - old_rate_gbp_per_mwh) / old_rate_gbp_per_mwh
    else:
        rate_increase_pct = 0.0

    tenure_discount = TENURE_DISCOUNT_PER_YEAR * min(tenure_years, MAX_TENURE_DISCOUNT_YEARS)
    p = BASE_CHURN_RATE + RATE_SENSITIVITY * rate_increase_pct - tenure_discount
    return max(0.0, min(MAX_CHURN_PROBABILITY, p))
