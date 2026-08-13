"""The company's TIME-OF-USE OFFER surface — the one place the world may ask whether
this customer is being offered a ToU tariff this term, and at what pair.

WHY THIS MODULE EXISTS (KNIFE pass 3, `A_composition_lift` step 25, register §3t)
---------------------------------------------------------------------------------
`simulation/run_phase2b.py` held the supplier's eligibility rule and the supplier's
peak/off-peak split, and composed them. Two crossings --
`saas.smart_meter_rollout` and `saas.tariff_pricing` -- and the composition was the
worse half: WHETHER to offer a ToU product to everyone whose meter permits it is a
commercial decision, not a consequence of the meter.

The decision lives at `company/pricing/tou_desk.py`. This module is the DOOR to it,
a separate file for the same reason `renewal_offer.py` is: the seam package is meant
to read as a list of doors, so what crosses the wall stays reviewable at a glance.

WHAT CROSSES, PRECISELY
-----------------------
In: the customer record (read for metering facts the supplier genuinely observes)
and the flat rate this term is contracted at.

Out: a `TouOffer` -- two numbers -- or `None` when no ToU offer is made. No
eligibility predicate, no multipliers, no rollout model. The world cannot ask "would
this customer be eligible" separately from "what are you offering them", because
that separation is what let it own the composition in the first place.

`tests/company/interfaces/test_tou_offer_seam.py` keeps that true and is
mutation-proven.
"""

from __future__ import annotations

from company.pricing.tou_desk import TouOffer

__all__ = ("TouOffer", "request_tou_offer")


def request_tou_offer(
    *,
    customer: dict,
    flat_unit_rate_gbp_per_mwh: float,
) -> TouOffer | None:
    """Ask the company what ToU pair, if any, it is offering this customer.

    Keyword-only on purpose: a customer record and a rate are both "the obvious
    first argument", and swapping them is the kind of error that would show up as
    a plausible number rather than a crash.
    """
    from company.pricing.tou_desk import decide_tou_offer

    return decide_tou_offer(
        customer=customer,
        flat_unit_rate_gbp_per_mwh=flat_unit_rate_gbp_per_mwh,
    )
