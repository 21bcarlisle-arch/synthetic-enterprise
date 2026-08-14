"""Seam: the supplier's monthly operating overhead is its own accrual.

KNIFE pass 3, `A_composition_lift` step 27, disposition register §3v. The
SECOND, narrower door of that step. The first —
`company/interfaces/growth_desk.py` — takes the acquire-or-retain economics off
`simulation/run_phase2b.py`; this one takes the monthly overhead accrual off the
same two crossings.

WHY TWO DOORS AND NOT ONE. §3m's group test is "do they feed ONE total?", and
here the honest answer is NO. The acquisition budget, the cap gate and the
retention guard are one decision seen from three sides — the guard's
`acq_cost_saved` term IS the acquisition cost the supplier avoids by retaining,
so they are arithmetically the same number. The monthly overhead is none of
that: it accrues on the calendar whether or not a single customer moved, it is
keyed by month rather than by account, and it lands in account 6200 rather than
against any supply point. Folding it into the growth door would hand the world
one surface that means two things, which is the re-export this pass exists to
avoid. §3t landed two doors for the same reason and this follows it.

WHAT THE WORLD WAS DOING THAT IS NOT THE WORLD'S. `run_phase2b` held
`FIXED_COST_MONTHLY` — £50/month of metering admin, licensing and basic IT/ops —
in its own namespace and passed it back into the supplier's own event
constructor. What a supplier's overhead COSTS is the supplier's own figure, and
one it is allowed to have wrong. The world's only legitimate input is the one it
already has: which month it has reached. So this door takes a month and nothing
else, and the amount never crosses.

That deletion is the point rather than a side effect: after this cut there is no
expression anywhere under `simulation/` from which the supplier's overhead can
be read, so the world cannot accrue it early, twice, or at a number of its own
choosing. The de-duplication by month stays on the world's side, because WHICH
months have been reached is the world's fact.

Controls: `tests/company/interfaces/test_growth_desk_seam.py`.
"""

from __future__ import annotations

from typing import Any

__all__ = ["book_monthly_overhead"]


def book_monthly_overhead(month: str) -> dict[str, Any]:
    """The supplier books one month of operating overhead.

    `month` is `YYYY-MM`. The AMOUNT is deliberately not a parameter and
    deliberately not re-exported — see the module docstring, and the portability
    law's rule 2, which refuses a per-market quantity on a seam surface.
    """
    from saas.growth_mandate import FIXED_COST_MONTHLY
    from saas.ledger import make_fixed_cost_event

    return make_fixed_cost_event(month, FIXED_COST_MONTHLY)
