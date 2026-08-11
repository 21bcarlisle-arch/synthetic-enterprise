"""The supplier's own billing-experience view of its book — who pays late, who complains.

WHY THIS LIVES COMPANY-SIDE (KNIFE pass 3, `A_composition_lift`, step 16,
2026-08-11, disposition register §3k). Two builders sat inlined in
`simulation/run_phase4c_on_phase2b.py`'s `main()`, and neither is world physics:

  1. `saas.payment_behaviour.build_payment_behaviour` — the supplier's credit-risk
     SEGMENTATION of its own customers, the bad-debt provision rate it books
     against each segment, and the payment date it EXPECTS from each.
  2. `saas.contact_model.build_contact_model` — the supplier's ESTIMATE of how
     likely a bill is to generate a contact, how many of those escalate to a
     complaint, and the service-quality score it reports off them.

EVERY NUMBER IN BOTH IS A BELIEF, NOT A FACT, and that is the argument for the
cut. A real supplier decides for itself which of its customers it calls "high
risk", what provision rate it books, and how it models complaint escalation; it
changes all three without telling anyone and gets them wrong routinely. Leaving
the composition world-side made the WORLD the thing that decides how the
supplier segments its own customers.

WHY THIS IS A GROUP, and the argument is NOT §3j's — stated because copying that
section's reasoning here would be false. The customer-value four were a group
because of a dependency CHAIN inside them (enterprise value needs churn needs
cost to serve), so cutting one at a time would have left the world holding an
intermediate. These two are INDEPENDENT of each other: either could be cut
alone without stranding a value world-side. They travel together for a different
and weaker reason, and the weaker reason is the true one — one input (`bills`,
and nothing else), and one question ("what does this supplier expect its book to
do when the bills land?"). Two doors onto the same argument list, differing only
in which belief comes back, would be two doors for no gain.

THE READ DIRECTION IS THE TEST OF THE CUT, the same one §3f, §3i and §3j applied.
This module imports nothing from `simulation/` or `sim/`: the bills arrive as
plain dicts through `build_billing_experience_view`'s signature. Had the
composition moved with a `simulation.*` import intact it would have traded
class-(b) crossings for class-(a) ones — the strictly forbidden direction, which
is at zero and stays there.

BEHAVIOUR IS UNCHANGED BY CONSTRUCTION. Nothing is reimplemented: the same two
functions are called with the same argument, in the same relative order, at the
same point in `main()`. Neither reads anything the other writes, so the order is
not load-bearing and this docstring does not claim it is.

THE BILL LIST IS THE FULL, UNFILTERED ONE, and that is a real decision rather
than an omission. Four hundred lines away in the same run, `close_the_books`
partitions these same bills through the Tier-1 issuance gate and recognises
revenue only against the ISSUED half (§3i, `BILL_TO_LEDGER_LINKAGE.md`). The
temptation when recomposing here is to apply the same filter for symmetry. It
would be wrong in both directions: a HELD bill is one the supplier has NOT sent,
so it can generate no contact and no complaint — but the provision the supplier
books against the customer's credit risk does not vanish because a bill was held
in the exception queue, and the pre-cut code provisioned against every bill.
Symmetry with the close would silently move the bad-debt figure. The seam test
performs exactly that filter as a mutation and asserts the view moves, so the
choice is pinned by a control rather than by this paragraph.

THE LEAK THIS CUT DOES NOT REPAIR, named rather than left to look sanctioned by
the new door. `simulation/contact_centre.py::generate_contact_centre_log(bills,
contact_model)` draws the world's ACTUAL contact events off
`contact_probability` — a number this module computes as the supplier's
estimate. The company's belief about how often it will be contacted therefore
CONSTITUTES how often it is contacted: the B2/B3 inversion, the same shape as
`simulation/satisfaction_churn.py` clamping the world's churn at the company's
`MAX_CHURN_PROBABILITY` before §3g cut it. That leak pre-dates this cut and is
untouched by it — the crossing being paid down here is the run module's IMPORT,
not the world's use of the returned dict. It is filed as a finding rather than
fixed on sight (SELF_INTERRUPT_DISCIPLINE: the repair is a world-side contact
physics module, a B3-shaped atom, not a line in this one). Recording it here
matters because after the cut the flow reads as a sanctioned seam hand-back, and
a reader could take the door as evidence that the direction was examined and
found clean. It was examined and found DIRTY, in a dimension this pass does not
own.

POINT-IN-TIME NOTE. Neither builder carries an `as_of` bound and neither needs
one: both are per-bill functions of fields the bill already carries
(`clarity_score`, `bill_shock_pct`, `total_amount_gbp`, `period_end`), with no
cross-bill or forward-looking term. `build_payment_behaviour`'s expected payment
date is derived from the bill's own period end plus a segment constant, not from
anything the world knows later. If a future caller routes a point-in-time
DECISION through this output, that caller needs the bound; this module does not.
"""

from __future__ import annotations

from dataclasses import dataclass

from saas.contact_model import build_contact_model
from saas.payment_behaviour import build_payment_behaviour

__all__ = ["BillingExperienceView", "build_billing_experience_view"]


@dataclass(frozen=True)
class BillingExperienceView:
    """What the supplier expects its book to do when the bills land.

    `payment_behaviour` — `{customer_id: [per-bill record, ...]}` carrying the
    credit-risk segment, the bad-debt provision, the expected payment date and
    the vulnerability flag.

    `contact_model` — `{"by_customer": {...}, "portfolio": {...}}` carrying the
    per-bill contact and complaint probabilities and the portfolio-level
    service-quality score.

    Both are plain dicts, in the shape their builders have always returned. The
    view does not reshape them: a seam that re-keys its payload gives every
    downstream consumer a second thing to be wrong about, and the point of this
    cut is WHERE the composition happens, not what it produces.
    """

    payment_behaviour: dict
    contact_model: dict


def build_billing_experience_view(bills: list[dict]) -> BillingExperienceView:
    """Build the supplier's billing-experience view over its own bills.

    `bills` is DATA the world hands over — the bills this supplier assembled,
    in the FULL unfiltered form every other consumer sees (see the module
    docstring on why the close's issuance filter is deliberately not applied
    here). Everything derived from them is the supplier's own belief.
    """
    return BillingExperienceView(
        payment_behaviour=build_payment_behaviour(bills),
        contact_model=build_contact_model(bills),
    )
