"""Seam: the world hands over the book and the public prices, and takes back a position.

KNIFE pass 3, `A_composition_lift` step 19, 2026-08-12, disposition register
§3n. Before this, `simulation/run_phase2b.py::main()` ran the supplier's own
credit and collateral desk itself — marking the trading book at an observable
forward snapshot, building the wholesale credit register, sampling it
semi-annually for the peak, deriving the variation margin owed, and running the
MC-2 breaking-strain sweep. Three of that module's wall crossings
(`company.trading.wholesale_credit_exposure`, `company.finance.margin_call_book`,
`company.risk.collateral_death_test`), and one composition worth more than the
count says: the credit block's `peak_sample_date` was threaded back out through
`main()` and into the death test, so the world was carrying a company
intermediate between two company computations.

Now the world hands over what it holds — the company's own trading book, its
customer register's commodity column, and the two PUBLIC spot histories — and
receives a `CounterpartyCollateral`. Counterparty rating bands, credit limits,
the CSA margin rule, the facility sizing and the breaking-strain doses are
unreachable from the SIM; what crosses is this one door, in one direction, once.

THE READ DIRECTION IS WHY THIS IS A CUT AND NOT A FILE MOVE — the same test §3f
applied to bill assembly, §3i to the month-end close, §3l to the statutory
return and §3m to the flexibility book.
`company/risk/counterparty_collateral_desk.py` imports nothing from
`simulation/` or `sim/`: the book arrives as an object the world already holds
and the price history as plain records, both through this signature. Had the
composition been moved with a `simulation.*` import intact it would have traded
class-(b) crossings for class-(a) ones, the strictly forbidden direction, which
is at zero and stays there.

WHAT THIS DOES NOT DO. `run_phase2b` keeps `company.trading.forward_book` and
`company.trading.hedge_decision` and `company.risk.hedge_policy` — the desk that
OPENS the positions, which lives in the per-customer term loop and is a
different cut — along with the CRM builders, the pricing group and the `saas.*`
set. The two indirect edges are untouched for the fifth consecutive step. Stated
rather than left to be discovered from a count that stops at 3.
"""

from __future__ import annotations

from company.risk.counterparty_collateral_desk import (
    CounterpartyCollateral,
    build_counterparty_collateral,
)

__all__ = ["CounterpartyCollateral", "build_counterparty_collateral"]
