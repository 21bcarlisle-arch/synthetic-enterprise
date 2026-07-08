"""Company churn risk estimator -- observable-data only.

The company estimates churn probability from signals it can legitimately
observe: rate change percentage, customer tenure, absolute bill burden,
and hedge fraction from the company's own hedging records.

Algorithm: base_rate
           + effective_rate_sensitivity × rate_increase_pct
           - tenure_discount × min(tenure_years, 5)
           + bill_stress_sensitivity × max(0, prev_annual_bill / threshold - 1)
           clamped to [0.0, 0.95].

Where effective_rate_sensitivity = rate_sensitivity × (1 - hedge_fraction × HEDGE_SENSITIVITY_REDUCTION)

Hedge fraction signal (Phase 15d):
  The company knows the hedge fraction it applied to each customer contract.
  A fully hedged customer (hf=1.0) experienced near-fixed prices regardless
  of market moves; they are less sensitive to the headline rate increase at
  renewal because their last contract felt stable. HEDGE_SENSITIVITY_REDUCTION=0.4:
  hf=1.0 → 40% rate sensitivity reduction; hf=0.5 → 20% reduction; hf=0.0 → no change.
  This reduces the structural over-estimation of churn in crisis years (2021-22)
  where rate increases were extreme but hedged customers had stable bills.

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
from __future__ import annotations

import math

from company.crm.market_conditions import market_conditions_multiplier

BASE_CHURN_RATE = 0.10
RATE_SENSITIVITY = 0.8
GAS_BASE_CHURN_RATE = 0.08
GAS_RATE_SENSITIVITY = 0.6
TENURE_DISCOUNT_PER_YEAR = 0.01
MAX_TENURE_DISCOUNT_YEARS = 5
BILL_STRESS_SENSITIVITY = 0.25
BILL_STRESS_THRESHOLD_GBP = 3000.0
HEDGE_SENSITIVITY_REDUCTION = 0.4
MAX_CHURN_PROBABILITY = 0.95
# Phase QP+1 (0.95-ceiling calibration fix, PRIORITIES.md P1, flagged since Phase QB):
# a hard clamp at MAX_CHURN_PROBABILITY collapsed every sufficiently large single-renewal
# rate rise into an indistinguishable 95% -- most visibly in the Decision Event Ledger's
# C_IC1 case (Phase QP), where a 95% company estimate sized a real retention discount
# against a SIM truth of 4%. Above CHURN_SATURATION_ELBOW the raw linear score is passed
# through an asymptotic curve instead of a hard clamp, so genuinely different elevated
# risk levels (e.g. a 50% vs a 150% I&C rate rise) stay distinguishable below the ceiling;
# only truly extreme spikes (300%+) still read as ~95%. Below the elbow, behaviour is
# byte-for-byte unchanged (identity) -- this only touches the region that used to clamp.
CHURN_SATURATION_ELBOW = 0.90
CHURN_SATURATION_SCALE = 0.30
# Phase 27e: I&C-specific churn constants.
# I&C customers shop via brokers at every renewal — base churn is higher and
# rate sensitivity is stronger than residential/SME. Tenure loyalty is lower
# (brokers switch regardless of relationship).
# Bill stress sensitivity is 0 for I&C: large industrial sites have large
# bills by nature (4 GWh at £54/MWh = £216k/yr) but are not "financially
# stressed" by bill size. I&C churn is driven by rate comparison via brokers
# (captured by IC_RATE_SENSITIVITY=1.5x), not absolute bill magnitude.
# Setting sensitivity=0 fixes systematic 95% overestimate for mid-size I&C.
IC_BASE_CHURN_RATE = 0.20       # brokers shop every renewal regardless
IC_RATE_SENSITIVITY = 1.5       # highly price-sensitive -- 10% rate rise -> +15% churn
IC_TENURE_DISCOUNT_PER_YEAR = 0.005  # less loyalty benefit per year
IC_BILL_STRESS_THRESHOLD_GBP = 50_000.0  # retained for backward-compat; unused when sensitivity=0
IC_BILL_STRESS_SENSITIVITY = 0.0    # I&C: rate-driven churn, not bill-size-driven
# Phase 22a: post-crisis churn hangover. When the company observes that a
# customer's prior term had a large net loss (>20% of revenue), customers
# who survived crisis prices remain financially anxious even after rates fall.
# The rate-change signal collapses to near-zero when rates improve (negative
# rate_increase_pct), but actual churn stays elevated for 2 renewal periods.
CRISIS_HANGOVER_BASE_UPLIFT = 0.12   # added to churn probability during hangover
CRISIS_HANGOVER_WINDOW_PERIODS = 2   # hangover persists for this many renewals
# Phase 33: active/passive renewal split.
# ~65% of domestic/SME customers roll to SVT by inaction at term end (passive).
# Passive rollers are inert: low base churn, very low rate sensitivity.
# Active renewers (35%) explicitly choose a new fixed deal — full churn model applies.
# SVT inertia data: Ofgem Consumer Engagement Surveys 2018-2019; CMA 2016 investigation.
PASSIVE_RENEWAL_RATE = 0.35         # probability a renewal is "active" (picks a new fix)
PASSIVE_BASE_CHURN_RATE = 0.05      # ~10%/year; SVT leavers are the most inert segment
PASSIVE_RATE_SENSITIVITY = 0.1      # rate changes don't drive passive customers to switch
PASSIVE_CHURN_CAP = 0.10            # SIM ground-truth cap for passive churn rolls
# Crisis years (2022 in UK): no fixed deals available — ALL renewals are forced passive.
CRISIS_PASSIVE_YEARS = frozenset({"2022"})


def _saturate_churn_probability(raw: float) -> float:
    """Asymptotically approach MAX_CHURN_PROBABILITY above CHURN_SATURATION_ELBOW instead
    of hard-clamping. Identity below the elbow -- unchanged behaviour for every estimate
    that was not previously being clamped."""
    if raw <= 0.0:
        return 0.0
    if raw <= CHURN_SATURATION_ELBOW:
        return raw
    x = (raw - CHURN_SATURATION_ELBOW) / CHURN_SATURATION_SCALE
    headroom = MAX_CHURN_PROBABILITY - CHURN_SATURATION_ELBOW
    saturated = CHURN_SATURATION_ELBOW + headroom * (1.0 - math.exp(-x))
    return min(MAX_CHURN_PROBABILITY, saturated)


def is_active_renewal(term_start_str: str, seed: str, active_probability: float | None = None) -> bool:
    """Return True if this renewal is an 'active' choice, False if passive SVT roll.

    `active_probability` defaults to the flat population-wide PASSIVE_RENEWAL_RATE
    (35%) when not supplied -- unchanged behaviour for any caller that doesn't pass
    it. Phase 2 (CORE_FIDELITY_PHASES.md, household engagement archetype) threads a
    per-customer probability here instead, so a household's active/passive/
    disengaged trait is persistent across its whole tenure rather than a fresh
    coin-flip every renewal. This module stays free of any `simulation.*` import
    (epistemic wall) -- the caller (simulation/run_phase2b.py) resolves the
    customer's archetype via simulation/household_segments.py and passes the
    plain float in.

    Crisis years (CRISIS_PASSIVE_YEARS) force all renewals passive — no fixed deals were
    available to switch to (UK 2022: suppliers withdrew fixed tariffs as wholesale costs
    exceeded the Ofgem price cap).
    """
    import random as _rnd
    year = term_start_str[:4]
    if year in CRISIS_PASSIVE_YEARS:
        return False
    threshold = PASSIVE_RENEWAL_RATE if active_probability is None else active_probability
    return _rnd.Random(f"active_renewal_{seed}").random() < threshold


def estimate_passive_churn_probability(
    old_rate_gbp_per_mwh: float,
    new_rate_gbp_per_mwh: float,
    tenure_years: float,
    renewal_year: int | None = None,
) -> float:
    """Churn estimate for a passive SVT-roller.

    Uses SVT-inertia constants: low base rate, very low rate sensitivity.
    These customers don't actively respond to rate changes — their churn
    is driven mainly by life events (house moves), not price signals.

    renewal_year: if given, scales the estimate by the published market
        switching multiplier (`company.crm.market_conditions`) — even inert
        SVT-rollers are more/less likely to move when competitor deals are
        more/less attractive that year. Defaults to None (multiplier 1.0,
        unchanged behaviour) for backward compatibility.
    """
    if old_rate_gbp_per_mwh > 0:
        rate_increase_pct = (new_rate_gbp_per_mwh - old_rate_gbp_per_mwh) / old_rate_gbp_per_mwh
    else:
        rate_increase_pct = 0.0
    tenure_discount = TENURE_DISCOUNT_PER_YEAR * min(tenure_years, MAX_TENURE_DISCOUNT_YEARS)
    p = PASSIVE_BASE_CHURN_RATE + PASSIVE_RATE_SENSITIVITY * rate_increase_pct - tenure_discount
    p = max(PASSIVE_BASE_CHURN_RATE, min(PASSIVE_CHURN_CAP, p))
    p *= market_conditions_multiplier(renewal_year)
    return max(0.0, min(MAX_CHURN_PROBABILITY, p))


def estimate_churn_probability(
    old_rate_gbp_per_mwh: float,
    new_rate_gbp_per_mwh: float,
    tenure_years: float,
    annual_consumption_kwh: float = 0.0,
    fuel: str = "electricity",
    hedge_fraction: float = 0.0,
    hangover_periods_remaining: int = 0,
    segment: str = "resi",
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
    hedge_fraction: fraction of the previous term that was hedged (0.0-1.0).
        The company knows this from its own hedging records. A well-hedged
        customer experienced stable prices; their rate sensitivity is reduced
        by HEDGE_SENSITIVITY_REDUCTION proportionally to the hedge fraction.
        Defaults to 0.0 (no hedge adjustment) for backwards compatibility.
    segment: "resi" (default), "SME", or "I&C". I&C uses broker-driven
        constants (higher base churn, higher rate sensitivity, less tenure
        loyalty) reflecting that sophisticated buyers shop at every renewal.

    Returns: churn probability estimate in [0.0, 0.95]
    """
    if segment == "I&C":
        base_rate = IC_BASE_CHURN_RATE
        rate_sensitivity = IC_RATE_SENSITIVITY
        tenure_discount_per_year = IC_TENURE_DISCOUNT_PER_YEAR
        bill_stress_threshold = IC_BILL_STRESS_THRESHOLD_GBP
        bill_stress_sens = IC_BILL_STRESS_SENSITIVITY
    elif fuel == "gas":
        base_rate = GAS_BASE_CHURN_RATE
        rate_sensitivity = GAS_RATE_SENSITIVITY
        tenure_discount_per_year = TENURE_DISCOUNT_PER_YEAR
        bill_stress_threshold = BILL_STRESS_THRESHOLD_GBP
        bill_stress_sens = BILL_STRESS_SENSITIVITY
    else:
        base_rate = BASE_CHURN_RATE
        rate_sensitivity = RATE_SENSITIVITY
        tenure_discount_per_year = TENURE_DISCOUNT_PER_YEAR
        bill_stress_threshold = BILL_STRESS_THRESHOLD_GBP
        bill_stress_sens = BILL_STRESS_SENSITIVITY

    # Phase 15d: hedge-adjusted rate sensitivity. Well-hedged customers experienced
    # stable prices during their last contract → less reactive to headline rate changes.
    effective_rate_sensitivity = rate_sensitivity * (1.0 - hedge_fraction * HEDGE_SENSITIVITY_REDUCTION)

    if old_rate_gbp_per_mwh > 0:
        rate_increase_pct = (new_rate_gbp_per_mwh - old_rate_gbp_per_mwh) / old_rate_gbp_per_mwh
    else:
        rate_increase_pct = 0.0

    tenure_discount = tenure_discount_per_year * min(tenure_years, MAX_TENURE_DISCOUNT_YEARS)

    prev_annual_bill_gbp = old_rate_gbp_per_mwh * annual_consumption_kwh / 1000.0
    bill_stress = bill_stress_sens * max(0.0, prev_annual_bill_gbp / bill_stress_threshold - 1.0)

    hangover_uplift = CRISIS_HANGOVER_BASE_UPLIFT if hangover_periods_remaining > 0 else 0.0
    p = base_rate + effective_rate_sensitivity * rate_increase_pct - tenure_discount + bill_stress + hangover_uplift
    return _saturate_churn_probability(p)
