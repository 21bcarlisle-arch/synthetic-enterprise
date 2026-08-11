"""Seam: the world hands over settled records and takes back closed books.

KNIFE pass 3, `A_composition_lift` step 14, 2026-08-11. Before this,
`simulation/run_phase4c_on_phase2b.py::main()` ran the supplier's month-end
itself — partitioning bills through the Tier-1 issuance gate, shaping the
cost-to-serve schedule into account-6100 events, posting the double-entry
ledger, deriving the P&L, and then checking the supplier's own billed-clock
invariant against the result. That was three of that module's ten remaining wall
crossings (`company.billing.pre_bill_validation`, `saas.ledger`,
`company.compliance.domain_invariants`).

Now the world hands over what it owns — the settled records, plus the spend and
cost-to-serve schedules as DATA — and receives an `AccountingClose`. The
issuance gate, the chart of accounts, the revenue-recognition policy and the
month-end reconciliation are unreachable from the SIM; what crosses is this one
door.

THE READ DIRECTION IS WHY THIS IS A CUT AND NOT A FILE MOVE — the same test §3f
applied to bill assembly. `company/finance/accounting_close.py` imports nothing
from `simulation/` or `sim/`: the settled records arrive as plain dicts through
this signature. Had the close been moved with a `simulation.*` import intact it
would have traded class-(b) crossings for class-(a) ones, the strictly forbidden
direction, which is at zero and stays there.

WHAT THIS DOES NOT DO. `saas.payment_behaviour` remains a live crossing of the
run module, because `build_payment_behaviour(bills)` is still called world-side
for the billing-experience output — the close's own use of that model no longer
goes through the world, but the edge does not fall until the billing-experience
group is cut too. Stated rather than left to be discovered from a count that
did not move as far as the reader might expect.
"""

from __future__ import annotations

from company.finance.accounting_close import AccountingClose, close_the_books

__all__ = ["AccountingClose", "close_the_books"]
