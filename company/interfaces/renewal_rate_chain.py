"""Seam: the world reports the renewal; the supplier decides what it costs.

KNIFE pass 3, `A_composition_lift` step 24, disposition register §3s. Cuts three
crossings on `simulation/run_phase2b.py`:

  * `simulation.run_phase2b -> company.pricing.tariff_engine`
  * `simulation.run_phase2b -> company.pricing.margin_feedback`
  * `simulation.run_phase2b -> company.pricing.ofgem_price_cap`

Design, the group argument and the read-direction argument:
`company/pricing/renewal_rate_chain.py`.
Controls: `tests/company/interfaces/test_renewal_rate_chain_seam.py`.

ONE DOOR, NOT THREE, and §3q is the reason that has to be argued rather than
assumed. §3m's group test is "do they feed ONE total?" — step 22 applied it,
got NO, and landed two doors. Here the total is one number, the rate the
customer contracts at, and the writers form a CHAIN: the surcharge multiplies
what the premium left, the cap clamps what the uplift added. Three doors would
hand the ordering back to the world, which is the half of this crossing that
was never an import in the first place.

THE PREMIUM COEFFICIENTS ARE DELIBERATELY NOT RE-EXPORTED HERE. The lookback
depth, the target margin, the surcharge threshold and its ceiling are supplier
model parameters of ITS market — the portability law's rule 2
(`tests/architecture/test_market_at_the_seams.py`) refuses a per-market
quantity baked into a seam surface, and a second market sets every one of them
for itself. They stay inside `company/pricing/`, which is the point of the door.
"""

from __future__ import annotations

from company.pricing.renewal_rate_chain import RenewalRateChain

__all__ = ["RenewalRateChain", "decide_renewal_rate"]


def decide_renewal_rate(
    *,
    customer_id: str,
    billing_account: str,
    commodity: str,
    term_start: str,
    tariff_type: str | None,
    term_index: int,
    struck_unit_rate_gbp_per_mwh: float | None,
    portfolio_margin_rates: list[float],
    prior_term_margin_gbp: float | None,
    prior_term_revenue_gbp: float,
    is_domestic: bool,
    settled_records: list[dict],
) -> RenewalRateChain:
    """Ask the company what rate it is contracting this renewal at.

    Keyword-only on purpose: twelve positional arguments across a wall is how a
    caller ends up passing the wrong observable without either side noticing.
    Every parameter is a plain value, the supplier's own settled records, or the
    supplier's own realised margin history. There is deliberately no parameter
    through which a caller could supply, or reach, the tariff engine, the cap
    table or the surcharge function.
    """
    # Imported HERE, not at module level, and for a measured reason: a
    # module-level `from ... import decide_renewal_rate` puts the desk's own
    # entry point in this module's namespace, so a caller could import it from
    # the door and step straight past this signature — and the epistemic ratchet
    # would stay green, because the import still terminates on the exempt seam
    # package. The walker descends into function bodies (`ast.walk`), so nothing
    # about the wall measurement changes. Same device as
    # `company/interfaces/renewal_offer.py`.
    from company.pricing.renewal_rate_chain import decide_renewal_rate as _decide

    return _decide(
        customer_id=customer_id,
        billing_account=billing_account,
        commodity=commodity,
        term_start=term_start,
        tariff_type=tariff_type,
        term_index=term_index,
        struck_unit_rate_gbp_per_mwh=struck_unit_rate_gbp_per_mwh,
        portfolio_margin_rates=portfolio_margin_rates,
        prior_term_margin_gbp=prior_term_margin_gbp,
        prior_term_revenue_gbp=prior_term_revenue_gbp,
        is_domestic=is_domestic,
        settled_records=settled_records,
    )
