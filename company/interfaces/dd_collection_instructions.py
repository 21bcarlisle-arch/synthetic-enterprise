"""The company's DD-COLLECTIONS surface — the one place the world may receive the
supplier's collection instructions and report back what happened to the money.

WHY THIS MODULE EXISTS (KNIFE pass 3, design `B4_billing_mechanics_reached_directly`)
-------------------------------------------------------------------------------------
This is the LAST of B4's four edges and the one its block called the hard one, because
`simulation/dd_collection_book.py` did not merely consult the company's billing module
— it BUILT the company's artefact, opening a `DirectDebitBook`, creating mandates on
it and appending `DDPaymentAttempt`s. The world was operating the supplier's
collection register.

The desk that operates it now is `company/billing/dd_collections_desk.py`, and that
module's docstring carries the full design. This module is the door: it publishes the
desk and its three instruction types, and nothing else.

WHAT IS DELIBERATELY NOT RE-EXPORTED
-------------------------------------
`DirectDebitBook`, `DirectDebitMandate`, `DDPaymentAttempt`, `next_collection_on_day`,
`AMENDMENT_MATERIALITY_THRESHOLD_GBP`, `AMENDMENT_WINDOW_BILLS`. Any one of them
re-exported here would hand the register's construction, its outcome vocabulary or the
supplier's re-estimation routine straight back to the world **with the epistemic
ratchet still green**, because an import that terminates on this package is exempt by
construction and the ratchet is blind to what the package chooses to name. That is the
exposure `company/interfaces/dd_review_outcome.py` recorded when it refused to
re-export `_recommended_monthly`, and it is why
`tests/company/interfaces/test_dd_collection_instructions_seam.py` mutation-proves the
narrowness of `__all__` rather than trusting it.

**This is a cut, not laundering.** `company/interfaces/` and `company/billing/` are
both WALKED byte for byte by `tools/epistemic_wall.py`. Nothing moved out of the
instrument's reach; the edge is exempt because it terminates on the sanctioned
crossing surface — the ratchet's own published `SEAM_PACKAGE` remedy — not because the
measurement stopped looking. Contrast §2b of the register, where relocating a
composition root to `tools/` was REFUSED, for the reason that does not apply here:
`tools/` is outside `WALL_DIRS` and the walker never looks there.

THE HONEST RESIDUAL
--------------------
`collection_register()` returns the desk's own `DirectDebitBook` so the run's report
serialiser can read it. The world holds that object briefly and passes it on; it
cannot name the type, construct one, or write to it through any exported name, so the
property B4 asked for holds. What remains owed is one layer up and belongs to
`A_composition_lift`: the run's composition root
(`simulation/run_phase4c_on_phase2b.py::main`) is what threads the register into the
report, and until that composition sits company-side the register makes its last hop
through the world. That is a routing residual, not a decision the world takes.

REUSE: company/interfaces/dd_collection_instructions.py
CLASS: CUSTOM
INDEX: searched "dd collection instructions", "collection", "instruction" -- 33 and 25
rows. The three neighbouring doors this pass already built are the right comparison and
none of them covers this: `company.interfaces.dd_review_outcome` publishes ONE number
(the standing monthly amount on the customer's letter),
`company.interfaces.collections_communication` publishes ONE string (a dunning letter's
tone), and `company.interfaces.credit_refund_requests` takes an SLC 14 closure and
returns a refund record. Widening any of them to also carry mandate setup, ADDACS
amendment and collection instructions would make a single door the union of four
unrelated surfaces -- the opposite of the narrowness each of those modules'
mutation-proven `__all__` exists to hold, and the reason `tests/company/interfaces/
test_dd_collection_instructions_seam.py` pins this door's `__all__` too. One seam per
surface is the design; a per-surface door is what makes a widening legible.
"""

from __future__ import annotations

from company.billing.dd_collections_desk import (
    AmendmentInstruction,
    CollectionInstruction,
    DirectDebitCollectionsDesk,
    MandateSetupInstruction,
)

__all__ = [
    "AmendmentInstruction",
    "CollectionInstruction",
    "DirectDebitCollectionsDesk",
    "MandateSetupInstruction",
    "open_collections_desk",
]


def open_collections_desk() -> DirectDebitCollectionsDesk:
    """Open a fresh collections desk for a run."""
    return DirectDebitCollectionsDesk()
