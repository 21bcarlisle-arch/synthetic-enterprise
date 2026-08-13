"""Seam: the world hands over settled volume and its I&C roster; the supplier books the commission.

KNIFE pass 3, `A_composition_lift` step 22, disposition register §3q. Cuts
`simulation.run_phase2b -> company.crm.tpi_book`.

Design and the read-direction argument: `company/crm/tpi_commission_desk.py`.
Controls: `tests/company/interfaces/test_tpi_commission_seam.py`.
"""

from __future__ import annotations

from company.crm.tpi_commission_desk import TPICommissionResult, build_tpi_commission

__all__ = [
    "TPICommissionResult",
    "build_tpi_commission",
]

# THE COMMISSION RATE IS DELIBERATELY NOT RE-EXPORTED HERE. It is a per-market
# money quantity (£/MWh) and the portability law's rule 2 —
# `tests/architecture/test_market_at_the_seams.py` — refuses one baked into a
# seam surface; a second market renegotiates broker terms in its own currency
# and on its own basis. It stays a supplier model parameter inside
# `company/crm/tpi_commission_desk.py`, which is where the door's whole point is
# that it lives.
