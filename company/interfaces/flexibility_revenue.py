"""Seam: the world hands over its asset snapshot and takes back the flex book.

KNIFE pass 3, `A_composition_lift` step 18, 2026-08-11, disposition register
§3m. Before this, `simulation/run_phase2b.py::main()` drove the domestic and
I&C flexibility revenue books itself — two of that module's wall crossings
(`company.market.flexibility_revenue_book`,
`company.market.ic_flexibility_revenue`) — and, worse than the imports, it
handed its own `HouseholdDemandRegister` to a company module which then pulled
customer asset flags out of it at will.

Now the world hands over what it owns — a per-year-end asset snapshot and its
own I&C electricity roster, both as DATA — and receives a `FlexibilityRevenue`.
The Capacity Market clearing prices, the DFS rates, the aggregator's cut, the
eligibility floor and the flex-kW estimates are unreachable from the SIM; what
crosses is this one door, in one direction, once.

THE READ DIRECTION IS WHY THIS IS A CUT AND NOT A FILE MOVE — the same test
§3f applied to bill assembly, §3i to the month-end close and §3l to the
statutory return. `company/market/flexibility_revenue.py` imports nothing from
`simulation/` or `sim/`: the snapshot arrives as plain nested mappings through
this signature. Had the composition been moved with a `simulation.*` import
intact it would have traded class-(b) crossings for class-(a) ones, the strictly
forbidden direction, which is at zero and stays there.

WHAT THIS DOES NOT DO. `run_phase2b` keeps its other crossings — the trading
desk, the CRM builders, the pricing group and the `saas.*` set — and the two
indirect edges are untouched. Stated rather than left to be discovered from a
count that stops at 2.
"""

from __future__ import annotations

from company.market.flexibility_revenue import (
    FlexibilityRevenue,
    build_flexibility_revenue,
)

__all__ = ["FlexibilityRevenue", "build_flexibility_revenue"]
