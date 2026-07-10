"""MARGIN_REALISM Step 3 -- the opex/cost-to-serve mechanism (Maturity Map B2).

Director amendment (docs/staging/done/MARGIN_REALISM_amended.md): do not charge the
company a fictional incumbent staff cost (hides the AI-native cost-advantage thesis),
but do not charge nothing either (unpriceable, too-easy game). Split into three parts:

(a) TRUE third-party & industry costs -- charged fully, per unit, anchored to real
    published rates. Only the DCC smart-meter comms charge is modelled here: the one
    line this session's research (docs/market_research/ASSUMPTIONS.md, "MARGIN_REALISM
    Step 3") found with a clean, current, unbundled, H-confidence per-meter-per-year
    rate. Payment processing, print/postage, credit-checks, debt-collection, and
    Elexon/Xoserve industry charges are real costs a supplier pays but were EXPLICITLY
    NOT FOUND as clean, unbundled, non-SME-scale figures this session -- per R12 (no
    fudge factors, ever), they are left at £0 here rather than estimated, and remain
    logged as open gaps in ASSUMPTIONS.md, not silently absorbed into this module.

(b) AI-compute + director-oversight hours at TRUE metered cost -- NOT YET POPULATED.
    Two real, unresolved design questions block this (registered in PRIORITIES.md, not
    silently defaulted): (i) `docs/observability/token-usage-log.jsonl` only covers
    2026-06-21 to 2026-06-25 and never captured interactive sessions -- not
    representative data; (ii) Anthropic's metered list-price-per-token vs the actual
    flat Max-subscription economics is a genuine costing-basis choice, and the
    director's own oversight-hours rate is his call, not the agent's to invent.
    `ai_compute_and_oversight_cost_gbp_per_year()` returns 0.0 until both are resolved.

(c) A DUAL ledger: the TRUE (a+b) ledger, and a BENCHMARK-loaded ledger additionally
    carrying a lower-quartile-incumbent-labour-cost proxy. The best available proxy
    found this session is Ofgem's own price-cap "Operating, debt and industry costs"
    allowance (per dual-fuel domestic customer per year, by payment method) -- but this
    figure BUNDLES opex + bad debt + industry charges together, so it is netted of this
    module's own true third-party cost (a) before being treated as the household's
    benchmark "labour" figure, per the research's own recommendation (avoids double-
    counting the DCC charge across both ledgers). This is a partial de-duplication, not
    a full reconciliation (bad debt and other industry costs remain bundled inside the
    Ofgem figure) -- a documented simplification, not claimed as exact.

R12 (anti-goal-seek) applies: these figures are a diagnostic of the true cost-advantage
gap, never tuned toward a target. R13 (baseline/curriculum split): these are real,
externally-anchored rates -- baseline-fidelity figures, not curriculum content.

Pure module: plain dicts/lists in, plain dicts out. No imports from `sim/` or `simulation/`.
"""
from __future__ import annotations

from typing import Any

# Smart DCC Ltd, "Charging Statement RY26/27 Issue 1.0", Tables 1 & 3 (docs/market_research/
# ASSUMPTIONS.md, "MARGIN_REALISM Step 3", fetched 2026-07-10). Same rate domestic/non-domestic.
DCC_COMMS_CHARGE_GBP_PER_YEAR: dict[str, float] = {
    "electricity": 19.01,
    "gas": 14.32,
}

# Ofgem "Summary of changes to the energy price cap 1 July to 30 September 2026", Annexes
# 1-2 -- "Operating, debt and industry costs" allowance, per DUAL-FUEL domestic customer
# per year, by payment method (docs/market_research/ASSUMPTIONS.md). Only Direct Debit and
# Standard Credit are modelled -- this codebase's PaymentChannel enum
# (simulation/household_segments.py) does not carry a Prepayment channel at all, so that
# real Ofgem figure (£308.04, Prepayment) has no population to apply to here.
OFGEM_BUNDLED_ALLOWANCE_GBP_PER_YEAR_DUAL_FUEL: dict[str, float] = {
    "direct_debit": 297.92,
    "standard_credit": 441.10,
}


def true_third_party_cost_gbp_per_year(customer: dict[str, Any]) -> float:
    """Part (a) for one billing account (one fuel, one customer_id). DCC comms charge
    only applies to smart-metered accounts (the charge is per DCC-enrolled smart meter,
    not per account) -- a non-smart or unknown-status account incurs £0 here (real
    unmodelled meter-service costs for those accounts are the MOP/DC/DA gap, distinct
    from DCC comms, see module docstring)."""
    if not customer.get("smart_meter"):
        return 0.0
    commodity = customer.get("commodity", "electricity")
    return DCC_COMMS_CHARGE_GBP_PER_YEAR.get(commodity, 0.0)


def ai_compute_and_oversight_cost_gbp_per_year(customer: dict[str, Any]) -> float:
    """Part (b) -- see module docstring. Always 0.0 until both open design questions
    (token-usage-log representativeness + costing-basis choice; director's own
    oversight rate) are resolved. `customer` is accepted for call-site symmetry with
    the other two functions even though it is currently unused."""
    return 0.0


def true_opex_cost_gbp_per_year(customer: dict[str, Any]) -> float:
    """The TRUE (a+b) ledger for one billing account/year."""
    return (
        true_third_party_cost_gbp_per_year(customer)
        + ai_compute_and_oversight_cost_gbp_per_year(customer)
    )


def _household_base_id(customer_id: str) -> str:
    """Strips the 'g' gas-leg suffix (e.g. 'C1g' -> 'C1') so a dual-fuel household's two
    billing accounts are recognised as ONE household for the benchmark ledger -- the
    Ofgem allowance is a per-DUAL-FUEL-HOUSEHOLD figure, not per fuel account, so it
    must not be counted twice for a household with both an electricity and a gas
    account."""
    return customer_id[:-1] if customer_id.endswith("g") else customer_id


def build_opex_ledger(
    customers: list[dict[str, Any]],
    payment_channel_by_household: dict[str, str],
) -> dict[str, Any]:
    """Portfolio-level dual opex ledger for one year (or the whole active book).

    customers: plain dicts, each with at least customer_id/segment/commodity/smart_meter
        (saas.customers.CUSTOMERS shape).
    payment_channel_by_household: {household_base_id: "direct_debit" | "standard_credit"}
        -- the CALLER resolves this (e.g. via
        simulation.household_segments.payment_channel_for_customer()), kept out of this
        module to preserve its "no imports from sim/simulation" purity.

    Returns:
      true_third_party_cost_gbp, true_ai_compute_cost_gbp, true_opex_total_gbp,
      benchmark_labour_cost_gbp (Ofgem allowance per distinct household, netted of that
        household's own true_third_party_cost_gbp -- see module docstring),
      benchmark_opex_total_gbp (== benchmark_labour_cost_gbp; already bundles bad debt/
        industry costs per Ofgem, so true_ai_compute is NOT added again here -- a real
        incumbent's cost-to-serve wouldn't carry an AI-compute line either),
      investor_thesis_gap_gbp (benchmark_opex_total_gbp - true_opex_total_gbp -- the
        gap the director's amendment names as "the investor thesis, quantified"),
      household_count (resi households resolved to a known payment channel -- households
        with no resolvable channel are excluded from the benchmark side only, not the
        true side, and logged via unresolved_household_count).
    """
    true_third_party_total = 0.0
    true_ai_compute_total = 0.0
    third_party_by_household: dict[str, float] = {}

    for customer in customers:
        cid = customer.get("customer_id", "")
        base_id = _household_base_id(cid)
        a_cost = true_third_party_cost_gbp_per_year(customer)
        true_third_party_total += a_cost
        true_ai_compute_total += ai_compute_and_oversight_cost_gbp_per_year(customer)
        third_party_by_household[base_id] = third_party_by_household.get(base_id, 0.0) + a_cost

    benchmark_labour_total = 0.0
    resolved_household_count = 0
    unresolved_household_count = 0
    for base_id, channel in payment_channel_by_household.items():
        allowance = OFGEM_BUNDLED_ALLOWANCE_GBP_PER_YEAR_DUAL_FUEL.get(channel)
        if allowance is None:
            unresolved_household_count += 1
            continue
        net_of_a = max(0.0, allowance - third_party_by_household.get(base_id, 0.0))
        benchmark_labour_total += net_of_a
        resolved_household_count += 1

    true_opex_total = true_third_party_total + true_ai_compute_total
    benchmark_opex_total = benchmark_labour_total

    return {
        "true_third_party_cost_gbp": round(true_third_party_total, 2),
        "true_ai_compute_cost_gbp": round(true_ai_compute_total, 2),
        "true_opex_total_gbp": round(true_opex_total, 2),
        "benchmark_labour_cost_gbp": round(benchmark_labour_total, 2),
        "benchmark_opex_total_gbp": round(benchmark_opex_total, 2),
        "investor_thesis_gap_gbp": round(benchmark_opex_total - true_opex_total, 2),
        "household_count": resolved_household_count,
        "unresolved_household_count": unresolved_household_count,
    }
