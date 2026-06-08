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
