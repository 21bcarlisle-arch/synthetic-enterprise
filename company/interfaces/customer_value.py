"""Seam: the world hands over settled records and takes back the supplier's view of its book.

KNIFE pass 3, `A_composition_lift` step 15, 2026-08-11, disposition register
§3j. Before this, `simulation/run_phase4c_on_phase2b.py::main()` composed the
supplier's customer-value layer itself — cost to serve, churn risk, home-move
win rates, enterprise value, and the account-6100 posting schedule that falls
out of the first. That was four of that module's seven remaining wall crossings
(`saas.cost_to_serve`, `saas.churn_model`, `saas.home_move_win_rate`,
`saas.enterprise_value`).

Now the world hands over what it owns — the settled records and the customer
book, as DATA — and receives a `CustomerValueView`. How the supplier costs a
customer, what it believes about churn, and what it thinks its book is worth are
unreachable from the SIM; what crosses is this one door.

WHY THIS IS A GROUP AND NOT FOUR ITEMS, which is §3i's own instruction and the
reason the cut is shaped this way. The four builders are one process with a
dependency chain inside it: `home_move_win_rates` needs `churn_risk`, and
`enterprise_value` needs both `churn_risk` and `cost_to_serve`. Cutting them
one at a time would have left the world holding the intermediate values and
threading them back in — a seam that publishes a PULL is half a cut. Taking the
group means the chain is internal and the door carries only what the world
actually owns.

WHAT THIS DOES NOT DO. The billing-experience group (`saas.contact_model`,
`saas.payment_behaviour`) and `company.billing.dd_review_runner` remain live
crossings of the run module. They are a different process on a different input
(`bills`, not settled records) and §3h already ruled the third a routing
residual. Stated rather than left to be discovered from a count that stops at 4.
"""

from __future__ import annotations

from company.analytics.customer_value_view import (
    CustomerValueView,
    build_customer_value_view,
)

__all__ = ["CustomerValueView", "build_customer_value_view"]
