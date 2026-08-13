"""Seam: the world reports the renewal; the supplier decides whether to reprice it.

KNIFE pass 3, `A_composition_lift` step 22, disposition register §3q. Cuts
`simulation.run_phase2b -> company.crm.customer_profitability`.

Design and the read-direction argument: the step-22 block at the foot of
`company/crm/customer_profitability.py`.
Controls: `tests/company/interfaces/test_customer_profitability_seam.py`.

TWO DOORS, NOT ONE, and this is the part worth reading before merging them.
Step 22 cuts the last two CRM crossings on `run_phase2b` in one change set, and
they are deliberately NOT behind a single object. §3m's test for a group — "do
they feed ONE total?" — fails here: an unprofitable-customer uplift changes a
unit rate inside the renewal loop, and broker commission is a channel cost
booked once at the end off the settled year. Naming a `CommercialDesk` over both
would invent an object the business does not have, and every later reader would
inherit it.
"""

from __future__ import annotations

from company.crm.customer_profitability import (
    MIN_TERM_INDEX_FOR_UPLIFT,
    UPLIFTABLE_COMMODITY,
    UPLIFTABLE_TARIFF_TYPES,
    renewal_unit_rate_uplift,
)

__all__ = [
    "MIN_TERM_INDEX_FOR_UPLIFT",
    "UPLIFTABLE_COMMODITY",
    "UPLIFTABLE_TARIFF_TYPES",
    "renewal_unit_rate_uplift",
]

# THE UPLIFT AMOUNT IS DELIBERATELY NOT RE-EXPORTED HERE, for the same reason
# the broker rate is not re-exported from `tpi_commission.py`: a per-market money
# quantity (£/MWh) on a seam surface is what the portability law's rule 2 refuses
# (`tests/architecture/test_market_at_the_seams.py`). How much a supplier adds to
# an unprofitable renewal is a model parameter of ITS market and stays inside
# `company/crm/customer_profitability.py`.
