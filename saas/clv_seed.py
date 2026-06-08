"""Customer Lifetime Value (CLV) Seed Calculation.

A CLV seed is a running total of the per-period margin for each customer,
computed as the difference between contract value billed and actual cost of
supply. This module processes settlement records to maintain this running total
in chronological order, ensuring that data arrives through the `interface/`
seam without direct imports from `sim/`.

This module is pure: it takes plain dicts as input and returns a dict structure.
It operates solely on the data provided, adhering to the Point-in-Time Blindfold
structural rules already established in other modules like saas/tariff_pricing.py
and saas/customer_reaction.py.
"""

def build_clv_seed(settlement_records):
    # Sort records by settlement_date and then by settlement_period
    sorted_records = sorted(
        settlement_records,
        key=lambda x: (x["settlement_date"], x["settlement_period"])
    )

    clv_seed = {}

    for record in sorted_records:
        customer_id = record["customer_id"]
        period_value_gbp = record["revenue_gbp"] - record["wholesale_cost_gbp"]

        if customer_id not in clv_seed:
            clv_seed[customer_id] = {
                "running_total_gbp": 0.0,
                "periods_counted": 0,
                "history": []
            }

        # Update the running total and count of periods
        clv_seed[customer_id]["running_total_gbp"] += period_value_gbp
        clv_seed[customer_id]["periods_counted"] += 1

        # Append the current period's data to the history
        clv_seed[customer_id]["history"].append({
            "settlement_date": record["settlement_date"],
            "settlement_period": record["settlement_period"],
            "period_value_gbp": period_value_gbp,
            "running_total_gbp": clv_seed[customer_id]["running_total_gbp"]
        })

    return clv_seed
