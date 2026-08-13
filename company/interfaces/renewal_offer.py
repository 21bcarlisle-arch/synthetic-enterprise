"""The company's RENEWAL-OFFER surface — the one place the world may ask what the
company is quoting a customer for their next term.

WHY THIS MODULE EXISTS (KNIFE pass 3, design B7_renewal_is_a_company_decision)
-------------------------------------------------------------------------------
`simulation/renewals.py` used to import the company's tariff engine, its pricing
function, its approval interface and its decision-rights table, and run the renewal
pricing decision — including the company's own internal governance escalation — from
inside the simulated world. Four crossings, and the worst of them was governance: a
real customer does not read their supplier's approval workflow.

The decision itself now lives at `company/pricing/renewal_desk.py`. This module is
the DOOR to it, and it is deliberately a separate file: the seam package is meant to
read as a list of doors, so that what crosses the wall stays reviewable at a glance.
Letting the desk live here would make `company/interfaces/` the second place company
decisions are made, which is how a chokepoint stops being one.

WHAT CROSSES, PRECISELY
-----------------------
In: what a supplier genuinely has about a renewal — the customer, the term and notice
dates, the product and segment, the EAC on record, the published spot history any
market participant can look up, the published levy/network schedules for that term,
and the rate the customer is on today.

Out: a `RenewalOffer` — four numbers. No engine, no pricing function, no decision
class, no decision log, no approval queue. `tests/company/interfaces/
test_renewal_offer_seam.py` exists to keep that true and is mutation-proven: a
`desk=`/`engine=` convenience argument or a widened `__all__` would restore the
removed dependency WITHOUT creating a single wall edge, because the import would
still terminate on the exempt seam package and the ratchet is blind to it by
construction.

**This is a cut, not laundering.** `company/interfaces/` and `company/pricing/` are
both WALKED by `tools/epistemic_wall.py` byte for byte. Nothing moved out of the
instrument's reach; the edge is exempt because it terminates on the sanctioned
crossing surface — the ratchet's own published `SEAM_PACKAGE` remedy — and not
because the measurement stopped looking. Contrast
`docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md` §2b, where relocating a
composition root to `tools/` was REFUSED for the reason that does not apply here:
`tools/` is outside `WALL_DIRS` and the walker never looks there.

THE HONEST LIMIT — this is a PULL, and it is the right shape here
------------------------------------------------------------------
B7 as written says the world "keeps the renewal EVENT ... and receives the resulting
offer through the seam", so a request answered at the door is the design, not half of
it — unlike B5, whose design asked for a stamped event and got a pull. What this door
does NOT yet buy is the cold-start forward price: `fallback_forward_price_gbp_per_mwh`
is the world's own estimate, handed to the company for the case where the company's
notice-date lookback window is empty. That leak is named rather than smoothed over,
preserved because repairing it would move priced rates inside a wall pass, and
recorded as owed in the register's §3a.
"""

from __future__ import annotations

from datetime import date

from company.pricing.renewal_desk import RenewalOffer

__all__ = ("RenewalOffer", "request_company_forward_estimate", "request_renewal_offer")


def request_company_forward_estimate(
    *,
    commodity: str,
    notice_date: str,
    observable_price_records: list[dict],
    fallback_gbp_per_mwh: float,
) -> float:
    """Ask the company what forward price it is pricing this term off.

    KNIFE step 24 (register §3s), and a NARROWER door than
    `request_renewal_offer` on purpose. The gas renewal schedule in
    `simulation/run_phase2b.py` builds the term itself -- the calendar, the
    published levy and network schedules, the deemed gaps -- and needs only the
    one number that is the company's: its own view of the forward. Routing it
    through `request_renewal_offer` would have made the world accept an
    electricity-shaped offer object it does not use, which is how a door starts
    lying about what crosses it.
    """
    from company.pricing.renewal_desk import estimate_forward_price

    return estimate_forward_price(
        commodity=commodity,
        notice_date=notice_date,
        observable_price_records=observable_price_records,
        fallback_gbp_per_mwh=fallback_gbp_per_mwh,
    )


def request_renewal_offer(
    *,
    customer_id: str,
    term_start: date,
    notice_date: date,
    tariff_type: str,
    segment: str,
    eac_kwh: int,
    observable_price_records: list[dict],
    published_policy_cost_per_mwh: float,
    published_network_cost_per_mwh: float,
    prior_fixed_unit_rate: float | None,
    fallback_forward_price_gbp_per_mwh: float,
) -> RenewalOffer:
    """Ask the company what it will quote this customer for this term.

    Keyword-only on purpose: eleven positional arguments across a wall is how a
    caller ends up passing the wrong observable without either side noticing.

    Every parameter is a plain value or a list of published market records. There is
    deliberately no parameter through which a caller could supply, or reach, the
    company's pricing engine, its decision policy or its decision log.
    """
    # Imported HERE, not at module level, and for a measured reason: a module-level
    # `from ... import quote_renewal` puts the desk's own entry point in this
    # module's namespace, so `from company.interfaces.renewal_offer import
    # quote_renewal` would let a caller step straight past this door's deliberately
    # narrow signature — and the epistemic ratchet would stay green, because the
    # import still terminates on the exempt seam package. The walker descends into
    # function bodies (`ast.walk`), so nothing about the wall measurement changes.
    from company.pricing.renewal_desk import quote_renewal

    return quote_renewal(
        customer_id=customer_id,
        term_start=term_start,
        notice_date=notice_date,
        tariff_type=tariff_type,
        segment=segment,
        eac_kwh=eac_kwh,
        observable_price_records=observable_price_records,
        published_policy_cost_per_mwh=published_policy_cost_per_mwh,
        published_network_cost_per_mwh=published_network_cost_per_mwh,
        prior_fixed_unit_rate=prior_fixed_unit_rate,
        fallback_forward_price_gbp_per_mwh=fallback_forward_price_gbp_per_mwh,
    )
