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


def build_churn_risk(settlement_records: list[dict], customers: list[dict],
                     comparison_mode: str = "yoy", through_period: str | None = None) -> dict:
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
    signals = score_experience_signals(settlement_records, comparison_mode=comparison_mode)
    acquisition_by_account = {c["customer_id"]: c["acquisition_date"] for c in customers}

    churn_risk: dict[str, list[dict]] = {}
    for account_id, periods in signals.items():
        acquisition_date = acquisition_by_account[account_id]
        shocks_by_period = {p["billing_period"]: p["bill_shock_triggered"] for p in periods}
        last_period = periods[-1]["billing_period"]
        # THE RENEWAL BEING ASKED ABOUT IS ALWAYS BEYOND THE SETTLED WINDOW (2026-08-27).
        #
        # `last_period` is the final period in the records handed in, and the caller that
        # matters -- `simulation.customer_events.roll_lifecycle_event` -- is handed records up
        # to but NOT INCLUDING the term it is pricing. So the renewal it is asking about lies
        # one period past the horizon BY CONSTRUCTION, and excluding it for that is circular.
        #
        # MEASURED, and it silenced churn rather than mislabelling it. A term ENDING 2016-12-31
        # has renewal month 2016-12, which the settled records still cover, so the roll happened.
        # A term STARTING 2017-04-01 has month 2017-04 while the records stop at 2017-03, so
        # `roll_lifecycle_event` found no entry and RETURNED NONE -- no churn decision at all.
        # Six of the nine residential seed accounts (C2, C3, C4, C6, C8, C9) were priced at 18
        # renewals across 2017-2019 and produced not one lifecycle event, while the three whose
        # anniversary happened to land on a month END churned normally. Whether a customer could
        # leave depended on which side of a month boundary their anniversary sat.
        #
        # NO FUTURE DATA IS READ, which is what makes this safe rather than a Point-in-Time
        # breach. The bill-shock window for a renewal is the TWELVE MONTHS BEFORE it
        # (`_shift_month(renewal_period, -12)` to `-1`), so for a 2017-04 renewal it is
        # 2016-04..2017-03 -- entirely inside records that stop at 2017-03. The data was always
        # there; only the horizon check kept it out. And `_renewal_periods` still returns
        # nothing beyond `horizon`, so raising it to the asked-about month admits that renewal
        # and no later one.
        horizon = max(last_period, through_period) if through_period else last_period

        account_risk = []
        for renewal_period in _renewal_periods(acquisition_date, horizon):
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
