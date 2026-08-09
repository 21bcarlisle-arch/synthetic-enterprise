"""Company/SIM seam — THE SUPPLY BOOK (which meter points this supplier has registered).

ADOPTION NOTE (provenance, not a reuse record)
RECORDED ON ADOPTION BY THE PW2 WORKER TICK (2026-08-09), NOT BY THIS MODULE'S AUTHOR —
    R9, so the provenance of this block is not mistaken for the author's own search. This file was
    found UNTRACKED in the working tree while its atom, KNIFE2_customer_straddle, already carried
    a landed level_current 0->2; committing the level without the code would claim a capability a
    fresh checkout cannot reproduce. Searched "supply book", "meter point registration", "sim
    company seam": the one existing crossing surface is
    `company/interfaces/sim_interface.py`, which this module sits alongside rather than duplicates
    — that seam exposes market observables to the company, this one publishes the registered book
    to the world, the opposite direction. Re-measured before adopting: 0 `saas.customers` tuples
    remain in LEGACY_SIM_READS_COMPANY, customer_straddle is 1 file / 0 edges (-16 vs baseline),
    KNIFE LEDGER OK, 22 tests green. The MEASUREMENT is verified; the owning lane should still
    confirm the seam DESIGN, which this tick did not review.

WHY THIS SEAM EXISTS
--------------------
The simulated world has to know which meter points are on this supplier's book.
That is not a leak in either direction and it is not an artefact of how this
repo is laid out: in GB, a supplier that takes on a meter point REGISTERS
against its MPAN in the central registration systems, and from that moment the
settlement systems, the DNO, the data collector and the agents all know the
point sits on that supplier's book. Registration is a company act that is
*published to the industry*, so the world reading the registered book is exactly
what happens in reality.

What does NOT happen in reality is the world reaching into the supplier's own
customer records to find that out. Before this seam, sixteen `simulation/`
modules did exactly that — `from saas.customers import CUSTOMERS` — sixteen
separate hands in the company's roster, none of them a declared crossing. This
module is the single published surface that replaces them: the SIM asks the
supply book, and the supply book is company-side code under
`company.interfaces`, the one sanctioned crossing surface in either direction
(`tests/architecture/test_epistemic_wall_ratchet.py`, `SEAM_PACKAGE`).

WHAT THIS SEAM IS NOT — read this before trusting it further than it goes
------------------------------------------------------------------------
It is a **routing** change, made under a behaviour-preserving wall (KNIFE pass
2, `docs/design/KNIFE_HOTSPOT_PASSES.md` §4). Sixteen scattered, undeclared
crossings became one declared, reviewable one. Three things it deliberately did
NOT do, recorded here rather than discovered later:

1. **It does not narrow the record to what industry can actually see.** A real
   MPAN registration publishes identity, supply start, address, profile class,
   metering arrangement and EAC — not the supplier's contract type or its
   internal segment label. The records handed back here are the full customer
   dicts, unchanged. Narrowing them is a behaviour change and therefore belongs
   to the boundary/adapter work (KNIFE pass 3 and the Epoch-3 adapter
   programme), not to a pass whose wall is "behaviour-preserving moves only".

2. **It does not move the ownership of dwelling truth.** `home_type`,
   `bedrooms` and `epc_rating` are facts about a physical property — world
   truth that happens to be stored company-side. Moving `saas/customers.py` to
   the SIM side would fix that and would re-open class (a) (company-side code
   reading SIM internals), which KNIFE pass 1 drove to zero. Strictly worse.
   The inversion is real and is owed forward, not fixed here.

3. **It does not decouple the two sides.** The same data crosses. What changed
   is that it crosses somewhere a reviewer can see it and a walker can name it.

IDENTITY IS PART OF THE CONTRACT, NOT AN ACCIDENT
-------------------------------------------------
`registered_supply_points()`, `successor_supply_points()` and
`acquired_supply_points()` return the LIVE list objects, never copies. That is
required, not lazy: `acquired_supply_points()` is a runtime accumulator that
`simulation.run_phase2b` appends to when a fresh-market acquisition wins, and
`saas.customers._clear_acquired_customers()` clears it in place between test
runs. A defensive copy here would silently sever both. Callers bind the result
once at import time — exactly the semantics `from saas.customers import
CUSTOMERS` had — so this pass changes no timing either.
"""

from __future__ import annotations

from typing import Any

from saas.customers import (
    ACQUIRED_CUSTOMERS,
    CUSTOMERS,
    SUCCESSOR_CUSTOMERS,
    customer_to_settlement_input,
    get_customer,
    make_acquired_customer,
)

SupplyPoint = dict[str, Any]


def registered_supply_points() -> list[SupplyPoint]:
    """The supplier's registered book: the original meter points on supply.

    Returns the live roster object (see IDENTITY above), not a copy.
    """
    return CUSTOMERS


def successor_supply_points() -> list[SupplyPoint]:
    """Points re-registered to this supplier after a home move was won.

    Same physical property as the predecessor; a fresh registration in the
    industry's eyes. Live object, not a copy.
    """
    return SUCCESSOR_CUSTOMERS


def acquired_supply_points() -> list[SupplyPoint]:
    """Points won in the open market during a run — the runtime accumulator.

    MUST be the live list: `simulation.run_phase2b` appends a registration to it
    as each acquisition lands, and test teardown clears it in place.
    """
    return ACQUIRED_CUSTOMERS


def registered_point(customer_id: str) -> SupplyPoint | None:
    """Look a point up by its identifier across all three registration books.

    Returns None when nothing on the book matches — the industry answer to
    "is this MPAN ours?" for a point that is not.
    """
    return get_customer(customer_id)


def settlement_input(point: SupplyPoint) -> dict[str, Any]:
    """Project a registered point down to what the settlement pipeline needs.

    Identity plus supply start — the only two fields settlement takes from
    registration.
    """
    return customer_to_settlement_input(point)


def register_acquired_point(
    customer_id: str,
    predecessor: SupplyPoint,
    acquisition_date: str,
) -> SupplyPoint:
    """Build the registration record for a point won in the open market.

    Cloned from the predecessor's property profile, because it IS the same
    property. Building the record does not add it to the book — the caller
    appends it to `acquired_supply_points()`, which is why that accessor must
    hand back the live list.
    """
    return make_acquired_customer(customer_id, predecessor, acquisition_date)
