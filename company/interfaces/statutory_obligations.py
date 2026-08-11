"""Seam: the world hands over settled volumes and takes back the statutory position.

KNIFE pass 3, `A_composition_lift` step 17, 2026-08-11, disposition register
§3l. Before this, `simulation/run_phase2b.py::main()` computed the supplier's
Renewables Obligation, FiT levelisation levy and Climate Change Levy itself —
three of that module's wall crossings (`company.regulatory.roc_ledger`,
`company.regulatory.fit_book`, `company.regulatory.ccl_ledger`), and it read
three PRIVATE rate tables across the wall to do it.

Now the world hands over what it owns — the settled records and its own I&C
book, as DATA — and receives a `StatutoryObligations`. The obligation levels,
the buy-out prices, the levy rates and which customers are CCL-liable are
unreachable from the SIM; what crosses is this one door.

THE READ DIRECTION IS WHY THIS IS A CUT AND NOT A FILE MOVE — the same test
§3f applied to bill assembly and §3i to the month-end close.
`company/regulatory/statutory_obligations.py` imports nothing from `simulation/`
or `sim/`: the records arrive as plain dicts through this signature. Had the
computation been moved with a `simulation.*` import intact it would have traded
class-(b) crossings for class-(a) ones, the strictly forbidden direction, which
is at zero and stays there.

WHAT THIS DOES NOT DO. `run_phase2b` keeps its other crossings — the trading
desk, the CRM builders, the pricing group and the `saas.*` set are separate
processes on separate inputs, and the two indirect edges are untouched. This
door carries the annual statutory return and nothing else. Stated rather than
left to be discovered from a count that stops at 3.
"""

from __future__ import annotations

from company.regulatory.statutory_obligations import (
    StatutoryObligations,
    build_statutory_obligations,
)

__all__ = ["StatutoryObligations", "build_statutory_obligations"]
