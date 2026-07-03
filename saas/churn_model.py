"""Churn risk model — Phase 4b-2 (customer value layer).

`simulation/renewals.py` assumes a 100% renewal rate — "no churn modelled
yet — that is a later phase's concern" (its words). This module is that
later phase: it estimates a churn (non-renewal) probability for each
billing account at each annual renewal point, driven by the bill-shock
history (`saas/customer_reaction.py`'s `score_experience_signals`) in the
12 months leading up to that renewal.

Key Domain Insight (CLAUDE.md): customer reaction to bills is non-rational.
This model encodes that directly — churn risk is driven purely by how often
a customer experienced a bill shock (`bill_shock_triggered`), not by whether
the underlying prices were fair or the supplier's margin was thin.

Model: `churn_probability = BASE_ANNUAL_CHURN_PROBABILITY +
bill_shock_count * CHURN_UPLIFT_PER_BILL_SHOCK`, capped at
`MAX_CHURN_PROBABILITY`. `BASE_ANNUAL_CHURN_PROBABILITY` (5%) reflects the
UK domestic switching rate baseline even for customers with no bill shocks
at all; each triggered bill shock in the preceding contract year adds
`CHURN_UPLIFT_PER_BILL_SHOCK` (3 percentage points).

This module is pure: it takes settlement records and the CUSTOMERS roster
as plain lists of dicts and returns a plain dict. It does not import from
`sim/` — settlement records arrive across the `interface/` seam, keeping
the Point-in-Time Blindfold structural (same pattern as
`saas/customer_reaction.py` and `saas/cost_to_serve.py`).
"""

from datetime import date, timedelta

from saas.customer_reaction import score_experience_signals

CONTRACT_LENGTH_DAYS = 365  # matches simulation/settlement.py

BASE_ANNUAL_CHURN_PROBABILITY = 0.05
CHURN_UPLIFT_PER_BILL_SHOCK = 0.03
MAX_CHURN_PROBABILITY = 0.95


def churn_probability(bill_shock_count: int) -> float:
    """Return the churn (non-renewal) probability for a renewal point that
    had `bill_shock_count` triggered bill shocks in the preceding contract
    year, capped at MAX_CHURN_PROBABILITY.
    """
    return min(
        BASE_ANNUAL_CHURN_PROBABILITY + bill_shock_count * CHURN_UPLIFT_PER_BILL_SHOCK,
        MAX_CHURN_PROBABILITY,
    )


def _shift_month(period: str, months: int) -> str:
    """Shift a "YYYY-MM" string by `months` (positive or negative)."""
    year, month = (int(part) for part in period.split("-"))
    total = year * 12 + (month - 1) + months
    return f"{total // 12:04d}-{total % 12 + 1:02d}"


def _renewal_periods(acquisition_date: str, last_period: str) -> list[str]:
    """Annual renewal points (as "YYYY-MM" strings) for a contract that
    started on `acquisition_date`, up to and including the first renewal
    whose month is <= `last_period`.
    """
    acquired = date.fromisoformat(acquisition_date)
    periods = []
    renewal_number = 1
    while True:
        renewal_date = acquired + timedelta(days=CONTRACT_LENGTH_DAYS * renewal_number)
        renewal_period = renewal_date.isoformat()[:7]
        if renewal_period > last_period:
            break
        periods.append(renewal_period)
        renewal_number += 1
    return periods


def build_churn_risk(settlement_records: list[dict], customers: list[dict]) -> dict:
    """Estimate churn risk at each annual renewal point for every billing
    account present in `settlement_records`.

    Returns a dict keyed by billing-account id (e.g. "C1", not "C1g" — see
    `saas.customer_reaction._billing_account_id`), each value a
    chronologically ordered list of:
      {renewal_period, bill_shock_count, churn_probability}

    `renewal_period` is a "YYYY-MM" string for the annual anniversary of the
    account's `acquisition_date` (from `customers`). `bill_shock_count` is
    the number of `bill_shock_triggered` billing periods in the 12 months
    immediately preceding `renewal_period`. An account with no renewal
    point within the data's coverage (e.g. less than a year of history)
    returns an empty list.

    Raises KeyError if a billing account has no matching entry in
    `customers` (looked up by `customer_id`).
    """
    signals = score_experience_signals(settlement_records, comparison_mode="yoy")
    acquisition_by_account = {c["customer_id"]: c["acquisition_date"] for c in customers}

    churn_risk: dict[str, list[dict]] = {}
    for account_id, periods in signals.items():
        acquisition_date = acquisition_by_account[account_id]
        shocks_by_period = {p["billing_period"]: p["bill_shock_triggered"] for p in periods}
        last_period = periods[-1]["billing_period"]

        account_risk = []
        for renewal_period in _renewal_periods(acquisition_date, last_period):
            window_start = _shift_month(renewal_period, -12)
            window_end = _shift_month(renewal_period, -1)
            bill_shock_count = sum(
                1
                for billing_period, triggered in shocks_by_period.items()
                if window_start <= billing_period <= window_end and triggered
            )
            account_risk.append({
                "renewal_period": renewal_period,
                "bill_shock_count": bill_shock_count,
                "churn_probability": churn_probability(bill_shock_count),
            })

        churn_risk[account_id] = account_risk

    return churn_risk
