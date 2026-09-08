"""Track cumulative rate shock count per customer from billing history.

Used by run_phase2b.py to pass bill_shock_count to enriched_churn_estimate.
The company knows rate histories because it set the rates on each contract.

A "bill shock" is defined as a term where the unit rate increased by more than
BILL_SHOCK_THRESHOLD vs the prior term. This is observable: the company issued
the bill at the new higher rate.

WHICH RATE THE HOUSEHOLD ACTUALLY SAW (2026-09-08). A shock is a thing that
happens to a household, so it is counted on what the household was CHARGED, not
on what the supplier was paid. Those are the same number on every day except
2022-10-01..2023-06-30, when the Energy Price Guarantee held a default-tariff
bill at 34.0p/kWh while the Ofgem cap the supplier was compensated to ran to
67.47p, HM Treasury paying the difference. Counted on the revenue rate, a
household that moved onto the default tariff in October 2022 registered a shock
in January 2023 that its bill never showed it — and then carried the churn uplift
for it, from `saas.churn_model`, in the quarter the whole record turns on.

So this reads `household_charged_unit_rate_gbp_per_mwh` where the record carries
it and `unit_rate_gbp_per_mwh` otherwise. The fallback is not a convenience: a
FIXED-TERM record has no charged leg because the household paid the rate the
company struck, and for it the two are the same question. `simulation/svt_product`
is what writes the split, and it is the only product where the two diverge.

Epistemic: both rate fields are observable (the company set the rate, and a
           supplier knew exactly what it billed a household under the EPG and
           what it reclaimed — that reclaim is the whole of the scheme).
           all_records contains only company-accessible billing data.
"""
from __future__ import annotations

BILL_SHOCK_THRESHOLD = 0.20  # rate increase > 20% triggers a shock count

#: Read in this order, first non-None wins. Not a `.get(a) or .get(b)`: a 0.0
#: rate is falsy and would silently fall through to the other leg, which is the
#: bug this ordering exists to not have.
_RATE_FIELDS = ("household_charged_unit_rate_gbp_per_mwh", "unit_rate_gbp_per_mwh")


def _household_charged_rate(record: dict) -> float | None:
    """What this record says the household paid per MWh, or None if it says nothing."""
    for field in _RATE_FIELDS:
        value = record.get(field)
        if value is not None:
            return value
    return None


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
        and _household_charged_rate(r) is not None
    ]
    cust_records.sort(key=lambda r: r.get("term_start", ""))
    shocks = 0
    for i in range(1, len(cust_records)):
        prev_rate = _household_charged_rate(cust_records[i - 1])
        curr_rate = _household_charged_rate(cust_records[i])
        if prev_rate is not None and prev_rate > 0 and curr_rate is not None:
            if (curr_rate - prev_rate) / prev_rate > shock_threshold:
                shocks += 1
    return shocks
