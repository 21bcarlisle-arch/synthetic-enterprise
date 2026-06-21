"""Company churn risk estimator -- observable-data only.

The company estimates churn probability from signals it can legitimately
observe: rate change percentage, customer tenure, and absolute bill burden.
It cannot read saas/customer_reaction.py parameters (alpha, beta,
bill-shock thresholds) or the SIM computed churn_probability.

Algorithm: base_rate + rate_sensitivity × rate_increase_pct
           - tenure_discount × min(tenure_years, 5)
           + bill_stress_sensitivity × max(0, prev_annual_bill / threshold - 1)
           clamped to [0.0, 0.95].

Gas fuel uses separate constants (Phase 14b):
  GAS_RATE_SENSITIVITY = 0.6: gas contracts have fewer alternative suppliers
    and are often bundled with electricity — customers are stickier on gas alone.
  GAS_BASE_CHURN_RATE = 0.08: dual-fuel gas legs almost never churn
    independently; base rate lower than electricity.
  Bill stress term is not applied to gas (pass annual_consumption_kwh=0).

The bill burden term captures what the rate-change-only model misses:
  - When rates fall from crisis peaks, rate_increase_pct turns negative
    and can push the estimate to 0 even for high-risk large customers
  - But a customer who spent £11,000/year last year at crisis prices is
    under more financial stress than rate % alone shows -- their budgets
    are stretched, they're shopping around
  - The company can observe this: it issued those bills and knows the
    customer's metered consumption (annual_consumption_kwh from meter reads)
  - bill_stress = (old_rate × annual_kwh / 1000) / THRESHOLD -- 1
    activates only when the PREVIOUS year's bill exceeded £3,000 GBP
    (the threshold where empirically customers start actively switching)
"""

BASE_CHURN_RATE = 0.10
RATE_SENSITIVITY = 0.8
GAS_BASE_CHURN_RATE = 0.08
GAS_RATE_SENSITIVITY = 0.6
TENURE_DISCOUNT_PER_YEAR = 0.01
MAX_TENURE_DISCOUNT_YEARS = 5
BILL_STRESS_SENSITIVITY = 0.25
BILL_STRESS_THRESHOLD_GBP = 3000.0
MAX_CHURN_PROBABILITY = 0.95


def estimate_churn_probability(
    old_rate_gbp_per_mwh: float,
    new_rate_gbp_per_mwh: float,
    tenure_years: float,
    annual_consumption_kwh: float = 0.0,
    fuel: str = "electricity",
) -> float:
    """Estimate churn probability from observable renewal signals.

    old_rate: unit rate (GBP/MWh) on the expiring contract
    new_rate: unit rate (GBP/MWh) on the renewal offer
    tenure_years: years since the customer original acquisition date
    annual_consumption_kwh: customer's estimated annual consumption (from
        meter reads). Used to compute prev-year bill burden. Defaults to 0
        (no bill stress term) for backwards compatibility.
    fuel: "electricity" (default) or "gas" — selects fuel-specific constants.
        Gas uses lower base rate (0.08) and lower rate sensitivity (0.6)
        to reflect stickier dual-fuel gas contracts with fewer alternatives.

    Returns: churn probability estimate in [0.0, 0.95]
    """
    base_rate = GAS_BASE_CHURN_RATE if fuel == "gas" else BASE_CHURN_RATE
    rate_sensitivity = GAS_RATE_SENSITIVITY if fuel == "gas" else RATE_SENSITIVITY

    if old_rate_gbp_per_mwh > 0:
        rate_increase_pct = (new_rate_gbp_per_mwh - old_rate_gbp_per_mwh) / old_rate_gbp_per_mwh
    else:
        rate_increase_pct = 0.0

    tenure_discount = TENURE_DISCOUNT_PER_YEAR * min(tenure_years, MAX_TENURE_DISCOUNT_YEARS)

    prev_annual_bill_gbp = old_rate_gbp_per_mwh * annual_consumption_kwh / 1000.0
    bill_stress = BILL_STRESS_SENSITIVITY * max(0.0, prev_annual_bill_gbp / BILL_STRESS_THRESHOLD_GBP - 1.0)

    p = base_rate + rate_sensitivity * rate_increase_pct - tenure_discount + bill_stress
    return max(0.0, min(MAX_CHURN_PROBABILITY, p))
