"""Customer dissatisfaction scoring — a deliberately simple "seed" reaction model.

Key Domain Insight (CLAUDE.md): customer reaction to bills is non-rational —
arithmetically correct bills frequently produce complaints. This module scores
one crude proxy for that: a per-customer running counter that increments every
settlement period where the actual cost of supplying that period ran more than
`threshold` (default 20%) hotter than what the customer is billed for it under
their fixed tariff. The customer never sees wholesale costs directly — this is
a seed signal for the Experience observability surface, not a claim that real
customers perceive or react to supplier-side costs.

This module is pure: it takes settlement records as plain dicts and returns a
dict of per-customer scores. It does not import from `sim/` — those records
arrive across the `interface/` seam, keeping the Point-in-Time Blindfold
structural (the same pattern as saas/tariff_pricing.py).
"""


def score_experience_signals(settlement_records, bill_shock_threshold=0.15, rolling_window=6):
    """Phase 3a — richer per-billing-period experience signals.

    A "billing period" is one calendar month (settlement_date[:7]) for one
    customer_id. Within each billing period, `actual_bill_gbp` sums
    `revenue_gbp` (what the customer is billed) and `actual_cost_gbp` sums
    `wholesale_cost_gbp` (what it actually cost to supply them) across every
    settlement record in that month.

    Three signals are computed per customer per billing period, each
    point-in-time safe (using only that period and earlier):

    - `bill_shock_score`: abs(actual_bill_gbp - rolling_avg_gbp) / rolling_avg_gbp,
      where rolling_avg_gbp is the average actual_bill_gbp over up to the
      previous `rolling_window` billing periods (strictly before this one).
      `None` (and `bill_shock_triggered=False`) until at least one prior
      period exists. Triggers (`bill_shock_triggered=True`) when the score
      exceeds `bill_shock_threshold`.
    - `cumulative_exposure_gbp`: running sum, across all billing periods to
      date, of (actual_cost_gbp - actual_bill_gbp) — positive means the
      supplier has under-recovered cost from this customer over their
      tenure so far.
    - `expectation_gap_gbp`: actual_bill_gbp - expected_bill_gbp, where
      expected_bill_gbp is the previous billing period's actual_bill_gbp
      x 1.02 (the customer's naive "a bit more than last time" expectation).
      `None` until a previous period exists.

    Returns a dict keyed by customer_id, each value a chronologically
    ordered list of per-billing-period dicts:
      {billing_period, actual_bill_gbp, actual_cost_gbp,
       rolling_avg_gbp, bill_shock_score, bill_shock_triggered,
       cumulative_exposure_gbp, expected_bill_gbp, expectation_gap_gbp}
    """
    by_customer_period: dict[str, dict[str, dict]] = {}
    for record in settlement_records:
        customer_id = record["customer_id"]
        billing_period = record["settlement_date"][:7]
        periods = by_customer_period.setdefault(customer_id, {})
        bucket = periods.setdefault(
            billing_period,
            {"actual_bill_gbp": 0.0, "actual_cost_gbp": 0.0},
        )
        bucket["actual_bill_gbp"] += record["revenue_gbp"]
        bucket["actual_cost_gbp"] += record["wholesale_cost_gbp"]

    signals: dict[str, list[dict]] = {}
    for customer_id, periods in by_customer_period.items():
        ordered_periods = sorted(periods.items())

        history: list[float] = []
        cumulative_exposure_gbp = 0.0
        previous_bill_gbp = None
        customer_signals = []

        for billing_period, totals in ordered_periods:
            actual_bill_gbp = totals["actual_bill_gbp"]
            actual_cost_gbp = totals["actual_cost_gbp"]

            if history:
                rolling_avg_gbp = sum(history[-rolling_window:]) / len(history[-rolling_window:])
                bill_shock_score = abs(actual_bill_gbp - rolling_avg_gbp) / rolling_avg_gbp
                bill_shock_triggered = bill_shock_score > bill_shock_threshold
            else:
                rolling_avg_gbp = None
                bill_shock_score = None
                bill_shock_triggered = False

            cumulative_exposure_gbp += actual_cost_gbp - actual_bill_gbp

            if previous_bill_gbp is not None:
                expected_bill_gbp = previous_bill_gbp * 1.02
                expectation_gap_gbp = actual_bill_gbp - expected_bill_gbp
            else:
                expected_bill_gbp = None
                expectation_gap_gbp = None

            customer_signals.append({
                "billing_period": billing_period,
                "actual_bill_gbp": actual_bill_gbp,
                "actual_cost_gbp": actual_cost_gbp,
                "rolling_avg_gbp": rolling_avg_gbp,
                "bill_shock_score": bill_shock_score,
                "bill_shock_triggered": bill_shock_triggered,
                "cumulative_exposure_gbp": cumulative_exposure_gbp,
                "expected_bill_gbp": expected_bill_gbp,
                "expectation_gap_gbp": expectation_gap_gbp,
            })

            history.append(actual_bill_gbp)
            previous_bill_gbp = actual_bill_gbp

        signals[customer_id] = customer_signals

    return signals


def score_dissatisfaction(settlement_records, threshold=0.20):
    # Initialize a dictionary to store customer data
    customer_data = {}

    # Sort globally by time so each customer's history is chronological AND
    # customers appear in the output in order of their earliest settlement —
    # not by customer_id string ordering, which need not coincide with it.
    sorted_records = sorted(
        settlement_records,
        key=lambda x: (x["settlement_date"], x["settlement_period"])
    )

    # Process each record
    for record in sorted_records:
        customer_id = record["customer_id"]
        if customer_id not in customer_data:
            customer_data[customer_id] = {
                "dissatisfaction_count": 0,
                "periods_scored": 0,
                "history": []
            }

        # Check if the condition is met
        triggered = record["wholesale_cost_gbp"] > record["revenue_gbp"] * (1 + threshold)
        if triggered:
            customer_data[customer_id]["dissatisfaction_count"] += 1

        # Update the history and periods scored
        customer_data[customer_id]["history"].append({
            "settlement_date": record["settlement_date"],
            "settlement_period": record["settlement_period"],
            "triggered": triggered,
            "running_total": customer_data[customer_id]["dissatisfaction_count"]
        })
        customer_data[customer_id]["periods_scored"] += 1

    return customer_data
