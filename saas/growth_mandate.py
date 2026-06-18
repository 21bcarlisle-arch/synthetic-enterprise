"""Phase 8a — Growth Mandate & Acquisition Model.

Configuration, budget calculation, and deterministic acquisition rolls.
No simulation imports — pure business-rule module.
"""

import random

# "flat": replace each churn with an acquisition attempt.
# "grow": attempt additional proactive acquisitions (Phase 8b).
# "shrink": no acquisition attempts (wind down portfolio).
MANDATE: str = "flat"

# Cost to attempt a fresh market acquisition (spent whether won or not).
COST_PER_ACQUISITION: dict[str, float] = {
    "resi": 150.0,
    "SME": 400.0,
}

# Fixed operating overhead deducted monthly regardless of portfolio size.
# Covers: metering admin, licensing fees, basic IT/ops.
# Note: calibrated for a micro-supplier with <15 accounts.
FIXED_COST_MONTHLY: float = 50.0  # £50/month — calibrate to match overhead ratio

# Base probability of winning a cold fresh-market acquisition.
# Lower than home-move rates (55%/35%) because we're competing blind.
ACQUISITION_WIN_RATE: dict[str, float] = {
    "resi": 0.20,
    "SME": 0.12,
}


def forecast_churns_next_year(
    churn_risk: dict,
    from_period: str,
) -> dict[str, float]:
    """Return {billing_account_id: forecast_churn_probability} for accounts
    whose most recent churn entry falls within 12 months of `from_period`.

    Point-in-Time safe: uses only churn_risk already computed from
    records up to from_period. Expects churn_risk[cid] to be a list of
    dicts with 'event_date' and 'churn_probability' keys.
    """
    from datetime import date, timedelta

    try:
        window_start = date.fromisoformat(from_period[:10])
    except ValueError:
        return {}
    window_end = window_start + timedelta(days=365)

    result: dict[str, float] = {}
    for cid, entries in churn_risk.items():
        if not entries:
            continue
        relevant = [
            e for e in entries
            if window_start <= date.fromisoformat(e["event_date"][:10]) <= window_end
        ]
        if relevant:
            result[cid] = max(e["churn_probability"] for e in relevant)
    return result


def acquisition_budget_gbp(
    churn_forecast: dict[str, float],
    segment_by_account: dict[str, str],
) -> float:
    """Expected acquisition spend = sum(churn_probability * cost_per_acquisition).

    This is a budget estimate — actual spend may differ if fewer churns fire.
    Accounts not in segment_by_account default to 'resi' cost.
    """
    total = 0.0
    for cid, prob in churn_forecast.items():
        segment = segment_by_account.get(cid, "resi")
        cost = COST_PER_ACQUISITION.get(segment, COST_PER_ACQUISITION["resi"])
        total += prob * cost
    return total


def roll_acquisition(segment: str, rng_seed: str) -> bool:
    """Deterministic acquisition win roll.

    Uses ACQUISITION_WIN_RATE[segment] and a seeded random.Random.
    Same seed always produces the same result (deterministic run guarantee).
    """
    win_rate = ACQUISITION_WIN_RATE.get(segment, ACQUISITION_WIN_RATE["resi"])
    return random.Random(rng_seed).random() <= win_rate
