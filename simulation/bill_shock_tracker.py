"""Track cumulative rate shock count per customer from billing history.

Used by run_phase2b.py to pass bill_shock_count to enriched_churn_estimate.
The company knows rate histories because it set the rates on each contract.

A "bill shock" is defined as a term where the unit rate increased by more than
BILL_SHOCK_THRESHOLD vs the prior term. This is observable: the company issued
the bill at the new higher rate.

Epistemic: unit_rate_gbp_per_mwh is observable (company set the rate).
           all_records contains only company-accessible billing data.
"""
from __future__ import annotations

BILL_SHOCK_THRESHOLD = 0.20  # rate increase > 20% triggers a shock count


def count_rate_shocks(
    customer_id: str,
    commodity: str,
    all_records: list[dict],
    shock_threshold: float = BILL_SHOCK_THRESHOLD,
) -> int:
    """Count the number of prior terms where the unit rate increased > shock_threshold.

    Filters all_records for the given customer_id and commodity, sorts by term_start,
    and counts transitions where (new_rate - old_rate) / old_rate > shock_threshold.

    Returns 0 if fewer than 2 matching records or if no shocks found.
    """
    cust_records = [
        r for r in all_records
        if r.get("customer_id") == customer_id
        and r.get("commodity") == commodity
        and r.get("unit_rate_gbp_per_mwh") is not None
    ]
    cust_records.sort(key=lambda r: r.get("term_start", ""))
    shocks = 0
    for i in range(1, len(cust_records)):
        prev_rate = cust_records[i - 1]["unit_rate_gbp_per_mwh"]
        curr_rate = cust_records[i]["unit_rate_gbp_per_mwh"]
        if prev_rate is not None and prev_rate > 0 and curr_rate is not None:
            if (curr_rate - prev_rate) / prev_rate > shock_threshold:
                shocks += 1
    return shocks
