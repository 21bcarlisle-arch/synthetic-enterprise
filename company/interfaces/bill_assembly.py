"""Seam: the world asks the company to run its billing.

KNIFE pass 3, `A_composition_lift` step 11, 2026-08-10. Before this, the
simulated world assembled the supplier's bills itself, reaching directly into
`company/billing/back_billing.py`, `company/billing/account_adjustment_register.py`
and `saas/bill_generator.py` — three of `simulation/run_phase4c_on_phase2b.py`'s
thirteen wall crossings, and three modules whose internals a real supplier is
free to change without telling the world anything.

Now the world hands over settled records and its meter-read feed, and receives
bills. The back-billing cap, the write-off register and the bill generator are
unreachable from the SIM; what crosses is this one door.

WHY THE READ FEED GOES THE OTHER WAY. A supplier does not decide whether a meter
read arrives — it observes one. So the company cannot import the world's read
physics, and does not: `assemble_monthly_bills` takes a `ReadArrivalFeed` the
caller supplies (`simulation.meter_reads.SimulatedReadFeed` in the simulation, a
real D0010/DTC adapter at go-live). Moving the bill assembly with its
`simulation.meter_reads` imports intact would have traded three class-(b)
crossings for three class-(a) ones — the STRICTLY FORBIDDEN direction, which is
at zero and stays there. The inversion is the cut; the file move alone would
have been a laundering.

WHAT THIS UNBLOCKS, AND WHAT IT DOES NOT DO. `company/interfaces/collections_communication.py`
(B5) and `company/interfaces/dd_review_outcome.py` (B4) each recorded that they
could deliver a PULL and not the PUSH their design asks for, for one stated
structural reason: no company-side bill emitter existed to stamp an attribute
onto. It exists now. Neither push is built here — that is separate work, and
claiming it in this commit would be exactly the "shape of a push with the
substance of a pull" both modules refused.
"""

from __future__ import annotations

from company.billing.monthly_bill_assembly import (
    ReadArrival,
    ReadArrivalFeed,
)
from company.billing.monthly_bill_assembly import (
    build_monthly_bills as assemble_monthly_bills,
)

__all__ = ["ReadArrival", "ReadArrivalFeed", "assemble_monthly_bills"]
