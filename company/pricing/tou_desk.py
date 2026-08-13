"""The company's TIME-OF-USE OFFER decision — who gets a ToU tariff, and at what pair.

WHY THIS MODULE EXISTS (KNIFE pass 3, `A_composition_lift` step 25, register §3t)
---------------------------------------------------------------------------------
`simulation/run_phase2b.py` composed this itself: it asked
`saas.smart_meter_rollout.is_tou_eligible` whether the supplier would offer this
customer a ToU tariff, then built the peak/off-peak pair inline as
`(unit_rate * TOU_PEAK_MULTIPLIER, unit_rate * TOU_OFFPEAK_MULTIPLIER)` from the
supplier's own multipliers -- the SECOND site applying that split, the first being
`saas.tariff_pricing.price_tou_tariff`. The world could not have called that one: it
strikes its own flat rate from a forward price, and the world holds the rate the
customer is actually CONTRACTED at, after the renewal rate chain has moved it. So
this is not a company constant read by accident; it is the supplier's product shape
implemented twice, once on each side of the wall. Step 25 makes it one
(`saas.tariff_pricing.split_flat_rate_to_tou`) and puts the decision behind a door.

WHAT IS THE COMPANY'S HERE, AND WHAT IS NOT
-------------------------------------------
NOT the company's, and deliberately left in the world: whether a customer HAS a
smart meter or an HH meter. That is a physical fact about the estate -- the rollout
happened, the world stamps it on the customer -- and the supplier observes it. It
still arrives here on the customer record.

The company's: what it DOES with that fact. Offering a ToU product to everyone the
meter allows is a commercial choice a supplier makes and can get wrong (offer ToU to
a flat-shape customer and revenue is neutral at the assumed split but not at theirs).
So is the shape of the pair: peak at 1.5x, off-peak set so that a 30/70 consumption
split is revenue-neutral against the flat rate. Both are the supplier's, both are
allowed to be wrong, and the gap between the assumed 30/70 split and the customer's
actual half-hourly shape is exactly the quantity the COUPLED TRIAD scores.

ORDER IS THE SIGNATURE: the pair is struck off the FINAL flat rate. Ask for the ToU
offer before the rate chain has finished moving it and the peak rate is a multiple of
a number the customer was never contracted at.
"""

from __future__ import annotations

from dataclasses import dataclass

from saas.smart_meter_rollout import is_tou_eligible
from saas.tariff_pricing import split_flat_rate_to_tou

__all__ = ("TouOffer", "decide_tou_offer")


@dataclass(frozen=True)
class TouOffer:
    """The peak/off-peak pair the company is offering for one term.

    Two numbers and nothing else -- no eligibility predicate, no multipliers, no
    rollout model. A term with no ToU offer is represented by `None` at the call
    site rather than by a `TouOffer` with null rates, so a caller cannot bill
    against an offer that was never made.
    """

    peak_rate_gbp_per_mwh: float
    offpeak_rate_gbp_per_mwh: float


def decide_tou_offer(
    *,
    customer: dict,
    flat_unit_rate_gbp_per_mwh: float,
) -> TouOffer | None:
    """Decide whether this customer is offered ToU this term, and at what pair.

    customer: the customer record as the world holds it. Read for METERING FACTS
        only (`metering`, `smart_meter`) -- what the supplier can see about the
        physical meter.
    flat_unit_rate_gbp_per_mwh: the rate this term is actually contracted at,
        AFTER every writer that moves it (see `company/pricing/renewal_rate_chain.py`).

    Returns None when the company is not offering ToU for this term.
    """
    if not is_tou_eligible(customer):
        return None

    peak, offpeak = split_flat_rate_to_tou(flat_unit_rate_gbp_per_mwh)
    return TouOffer(peak, offpeak)
