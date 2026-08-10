"""The day of the month a household's Direct Debit collects on — a CUSTOMER
attribute, held by the world.

WHY THIS MODULE EXISTS (KNIFE pass 3, design B4_billing_mechanics_reached_directly)
-----------------------------------------------------------------------------------
`staggered_payment_day` used to live in `company/billing/direct_debit.py`, and two
SIM modules imported it across the wall to find out when their own customers pay.
That is the same class of misfiling `§2a` of
`docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md` found for the reputation index,
the resentment ledger and activation energy, and it is cut by the same B1 template:
the module was world physics filed on the company side, so the crossing died with
the move rather than with a new door.

The fidelity argument, which is the whole of the ruling:

  * A household PICKS its collection day (or is assigned one at sign-up) and that
    choice is a fact about the customer, not a decision the supplier makes about
    them. Across a supplier's book those days spread through the month, which is
    why collections stagger rather than all landing on the same offset from the
    bill date.
  * The supplier then OBSERVES the day — it is written on the mandate. That is a
    real company-observable, and nothing here takes it away: the world hands the
    day over when it sets a mandate up (`payment_day=` on
    `company.billing.direct_debit.DirectDebitMandate`), exactly as a customer
    tells their supplier which day suits them.

Before the move the arrow pointed the wrong way — the world asked the company to
invent its own customers' habits. After it, the world holds the habit and the
company receives it.

THE 1–28 RANGE IS THE PAYMENT RAILS, NOT EITHER LANE'S PRIVATE CHOICE
----------------------------------------------------------------------
`company/billing/direct_debit.py` keeps its own `_MIN_PAYMENT_DAY`/`_MAX_PAYMENT_DAY`
and VALIDATES the day it is told. The bounds are stated twice on purpose, and the
duplication is not the `one name, two numbers` defect, for a reason that had to be
made true rather than asserted:

  * The range is a published UK Bacs convention (days are capped at 28 so the date
    exists in every month), which the regulation-commons doctrine treats as readable
    by every lane — like the law, it is published in reality.
  * A test pinning the two constants EQUAL would restore in the suite exactly the
    coupling this cut removes from the code. So the control instead pins the
    RELATIONSHIP that matters: every day this module can emit is a day the company's
    mandate register accepts. If either side drifts, mandate setup raises — a loud
    failure at the seam, not a silent divergence. See
    `tests/simulation/test_dd_payment_day.py`.

Deterministic, and drawing from nothing shared (C-S2): the day is a pure digest of the
customer id, so it consumes no RNG and can never shift another subsystem's stream.
Same customer id -> same day, every replay.
"""
from __future__ import annotations

import hashlib

# The world assigns collection days in the published UK Bacs range. Kept as this
# side's OWN reading of that convention -- see the module docstring on why this is
# deliberately not shared with the company's validation bounds.
_MIN_PAYMENT_DAY = 1
_MAX_PAYMENT_DAY = 28


def staggered_payment_day(customer_id: str) -> int:
    """The fixed day-of-month (1-28) this customer's level DD collects on.

    DD1 (2026-07-27, DD_seasonal_cashflow_physics): real households pick (or are
    assigned) a collection day, and across a supplier's book those days are spread
    through the month -- so collections STAGGER rather than every mandate landing on
    the same relative offset from its bill date.

    Derived DETERMINISTICALLY from the customer id via a stable digest -- no RNG draw
    is consumed, so this can never shift another subsystem's random stream (C-S2:
    deterministic, idempotent replay; a pure per-customer function is the strongest
    form of the named-substream discipline -- it draws from nothing shared at all).
    """
    digest = hashlib.sha256(customer_id.encode("utf-8")).hexdigest()
    span = _MAX_PAYMENT_DAY - _MIN_PAYMENT_DAY + 1
    return _MIN_PAYMENT_DAY + (int(digest[:8], 16) % span)
