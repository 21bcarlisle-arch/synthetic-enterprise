"""MARGIN_REALISM Step 3 -- the opex/cost-to-serve mechanism (Maturity Map B2).

B2_OPEX_TAXONOMY_EXPANSION.md (2026-07-10, director-direct NTFY): expanded the
original three-part split below with categories (4)/(5)/(6) -- see
INFRASTRUCTURE_COST_LINES, GOVERNANCE_COST_LINES, CAC_ONE_OFF_GBP_PER_*_CUSTOMER/
BROKER_COMMISSION_GBP_PER_KWH, and the fixed_cost_floor_gbp_per_year()/
break_even_analysis() functions further down. Anchors from
docs/market_research/B2_CATEGORY{4,5,6}_*.md (2026-07-10 research passes) --
none had a single clean public figure; every line is tagged is_estimate/source/
classification (fixed/stepped/variable) honestly rather than collapsed to a
fake-precise constant.

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


# ---------------------------------------------------------------------------
# Category (4): INFRASTRUCTURE AT COMMERCIAL RATES
# Research: docs/market_research/B2_CATEGORY4_INFRASTRUCTURE_ANCHORS.md (2026-07-10).
# None of these five candidate lines had a single clean public "£X/year" figure --
# each is a reasoned range (source cited where real, None where genuinely
# uncited/quote-only), midpoint used as the point estimate, is_estimate flagged
# honestly rather than collapsed to a fake-precise constant (same discipline as
# part (a) above). DCC connection/enrolment is deliberately NOT a line here:
# SECAS confirms the entry process itself carries no direct fee, and the real
# recurring DCC cost is already modelled via DCC_COMMS_CHARGE_GBP_PER_YEAR above --
# a new line here would double-count.
# ---------------------------------------------------------------------------
INFRASTRUCTURE_COST_LINES: dict[str, dict[str, Any]] = {
    "cloud_hosting_commercial_resilience": {
        "annual_gbp": 80_000.0,
        "range_gbp": (40_000.0, 120_000.0),
        "is_estimate": True,
        "classification": "fixed",
        "source": None,
        "note": (
            "No published energy-supplier cloud-cost figure exists; reasoned "
            "build-up from DRaaS + platform-hosting benchmarks (AWS DR pricing, "
            "n2ws 2025). Real cost likely steps with book size/transaction "
            "volume but no anchored curve found -- treated as fixed at current "
            "scale, not extrapolated."
        ),
    },
    "market_data_licence": {
        "annual_gbp": 27_500.0,
        "range_gbp": (15_000.0, 40_000.0),
        "is_estimate": True,
        "classification": "fixed",
        "source": None,
        "note": (
            "ICIS/Argus/Montel/Platts are quote-only (no public price list, "
            "confirmed). Industry-common estimate, not citable to one source. "
            "Real cost likely steps with seat/market count."
        ),
    },
    "bsc_rec_sec_membership": {
        "annual_gbp": 20_000.0,
        "range_gbp": (10_000.0, 30_000.0),
        "is_estimate": True,
        "classification": "stepped",
        "source": "https://bscdocs.elexon.co.uk/bsc/bsc-section-d-bsc-cost-recovery-and-participation-charges",
        "note": (
            "Real mechanism (BSC Section D) genuinely scales via a Funding "
            "Share proportional to market share -- a real stepped/variable "
            "cost, not fixed in principle -- but no exact small-supplier "
            "formula/rate is published. Flat estimate used at current book "
            "scale; do not extrapolate to a materially larger book without "
            "re-anchoring against Elexon's actual cost-recovery statement."
        ),
    },
    "bacs_sponsorship_bureau": {
        "annual_gbp": 6_500.0,
        "range_gbp": (3_000.0, 10_000.0),
        "is_estimate": True,
        "classification": "fixed",
        "source": "https://www.londonandzurich.co.uk/guides/guide-direct-debit-uk-businesses/",
        "note": (
            "Fixed bureau/sponsorship relationship fee. The separate real "
            "per-transaction Bacs rate (<£0.25/txn, sourced) is a variable "
            "payment-processing cost -- already a known unmodelled gap noted "
            "in part (a)'s docstring above, not duplicated here."
        ),
    },
}

# ---------------------------------------------------------------------------
# Category (5): FIXED GOVERNANCE & PROFESSIONAL -- the "AI-irreducible floor".
# Research: docs/market_research/B2_CATEGORY5_GOVERNANCE_ANCHORS.md (2026-07-10).
# Own P&L line -- NEVER blended into the per-customer true/benchmark ledger
# above. golive_conditional=True lines only apply once the company holds a real
# Ofgem licence / has real insurable exposure -- excluded from the floor during a
# pure backtest/simulation (this project's current status), per the research's
# own recommendation. Tagged here as the simplifications-register entry for
# each such line, per the B2_OPEX_TAXONOMY_EXPANSION.md instruction.
# ---------------------------------------------------------------------------
GOVERNANCE_COST_LINES: dict[str, dict[str, Any]] = {
    "statutory_audit": {
        "annual_gbp": 8_500.0,
        "range_gbp": (6_000.0, 12_000.0),
        "is_estimate": True,
        "classification": "stepped",
        "source": "https://auditgroup.co.uk/statutory-audit-costs/",
        "golive_conditional": False,
        "note": (
            "Real UK audit-fee-as-%-of-revenue bands exist above the £5m "
            "turnover threshold (see audit_fee_gbp() for the anchored scaling "
            "version); this flat figure is the small-book/voluntary-audit "
            "default below that threshold."
        ),
    },
    "legal_retainer": {
        "annual_gbp": 12_000.0,
        "range_gbp": (5_340.0, 9_300.0),
        "is_estimate": True,
        "classification": "fixed",
        "source": "https://complianceconsultant.org/compliance-retainer-services/",
        "golive_conditional": False,
        "note": (
            "Midpoint judgement between a general UK commercial retainer "
            "(~£9.3k/yr) and a compliance-specific retainer (~£5.3k-£12k/yr) "
            "-- no supplier-specific figure was found."
        ),
    },
    "ofgem_licence_fee": {
        "annual_gbp": 500.0,
        "range_gbp": (500.0, 500.0),
        "is_estimate": False,
        "classification": "fixed",
        "source": "https://www.ofgem.gov.uk/sites/default/files/2024-05/Licence%20fee%20cost%20recovery%20principles%20May%202024.pdf",
        "golive_conditional": True,
        "note": (
            "Real, sourced published minimum (Ofgem Licence Fee Cost Recovery "
            "Principles, May 2024). A larger supplier pays more via a "
            "market-share-weighted formula; this book's scale sits at the "
            "minimum. Only payable once actually holding a live Ofgem licence."
        ),
    },
    "insurance_pi_cyber_dando": {
        "annual_gbp": 4_100.0,
        "range_gbp": (630.0, 7_500.0),
        "is_estimate": True,
        "classification": "fixed",
        "source": "https://getindemnity.co.uk/business-insurance/cyber/how-much-does-cyber-insurance-cost",
        "golive_conditional": True,
        "note": (
            "Combined PI (~£1,500) + Cyber (~£2,000) + D&O (~£600) estimate. "
            "No real insurable exposure exists pre-golive (no real customers "
            "or board liability in a pure backtest/simulation)."
        ),
    },
    "company_secretarial": {
        "annual_gbp": 600.0,
        "range_gbp": (100.0, 800.0),
        "is_estimate": True,
        "classification": "stepped",
        "source": "https://www.companyservicesuk.co.uk/secretarial-services/full-company-secretarial-support/",
        "golive_conditional": False,
        "note": (
            "Real bands exist by number of directors/shareholders (e.g. up to "
            "5 vs up to 10) -- too small a cost line to warrant a full curve; "
            "comprehensive-package estimate used."
        ),
    },
}


def audit_fee_gbp(annual_revenue_gbp: float) -> float:
    """Real anchored scaling (docs/market_research/B2_CATEGORY5_GOVERNANCE_ANCHORS.md):
    0.25% of revenue for £5m-£10m turnover, 0.19% for £10m-£25m (auditgroup.co.uk /
    teamed.global benchmarks). Below £5m turnover -- this book's real current scale --
    the %-of-revenue band isn't anchored, so this falls back to
    GOVERNANCE_COST_LINES['statutory_audit']'s flat voluntary-audit estimate rather
    than extrapolating a real band below the range it was benchmarked against."""
    if annual_revenue_gbp >= 10_000_000:
        return round(annual_revenue_gbp * 0.0019, 2)
    if annual_revenue_gbp >= 5_000_000:
        return round(annual_revenue_gbp * 0.0025, 2)
    return GOVERNANCE_COST_LINES["statutory_audit"]["annual_gbp"]


def infrastructure_floor_gbp_per_year() -> float:
    """Category (4) total -- portfolio-level, not per-customer."""
    return sum(line["annual_gbp"] for line in INFRASTRUCTURE_COST_LINES.values())


def governance_floor_gbp_per_year(annual_revenue_gbp: float = 0.0, golive: bool = False) -> float:
    """Category (5) total. golive=False (this project's current status) excludes
    golive-conditional lines (Ofgem licence fee, insurance) -- no real regulatory/
    insurable exposure exists yet in a pure backtest/simulation."""
    audit = audit_fee_gbp(annual_revenue_gbp) if annual_revenue_gbp else GOVERNANCE_COST_LINES["statutory_audit"]["annual_gbp"]
    total = 0.0
    for name, line in GOVERNANCE_COST_LINES.items():
        if line.get("golive_conditional", False) and not golive:
            continue
        total += audit if name == "statutory_audit" else line["annual_gbp"]
    return total


def fixed_cost_floor_gbp_per_year(annual_revenue_gbp: float = 0.0, golive: bool = False) -> dict[str, Any]:
    """Categories (4)+(5) combined -- the 'AI-irreducible floor'. Its own P&L
    line, portfolio-level, NEVER blended into the per-customer true/benchmark
    ledger (build_opex_ledger() above) -- this is a company-level fixed cost, not
    a cost-to-serve-per-customer figure."""
    infra = infrastructure_floor_gbp_per_year()
    governance = governance_floor_gbp_per_year(annual_revenue_gbp, golive)
    return {
        "infrastructure_gbp": round(infra, 2),
        "governance_gbp": round(governance, 2),
        "total_floor_gbp": round(infra + governance, 2),
        "golive": golive,
    }


# ---------------------------------------------------------------------------
# Category (6): SCALE STRUCTURE -- fixed / stepped / variable classification,
# and customer-acquisition cost (CAC) per channel per segment as a real cost
# line. Research: docs/market_research/B2_CATEGORY6_CAC_ANCHORS.md (2026-07-10).
#
# Residential/SME acquisition via a price-comparison site (PCS) is a real,
# one-off, per-customer cost. I&C acquisition via a broker is a real, ONGOING
# per-kWh commission -- a structurally DIFFERENT cost shape (a trail commission
# embedded in the unit rate for the life of the contract, not a one-off spend
# at signup) -- applied at billing time via broker_commission_gbp(), not at
# acquisition time via acquisition_cost_gbp().
# ---------------------------------------------------------------------------
CAC_ONE_OFF_GBP_PER_DUAL_FUEL_CUSTOMER: dict[str, float] = {
    # Midpoint of £50-£60 dual-fuel PCS commission -- real, sourced (CMA-era
    # rate, corroborated via The Conversation / CMA Energy market investigation
    # Appendix 8.3).
    "pcs_aggregator": 55.0,
}
CAC_ONE_OFF_GBP_PER_SINGLE_FUEL_CUSTOMER: dict[str, float] = {
    "pcs_aggregator": 27.5,
}

# Ongoing broker commission, GBP per kWh billed (NOT one-off) -- real,
# UK-specific, sourced (Connection Technologies, "Business Energy Broker Fees
# 2026"). Midpoints of the cited bands.
BROKER_COMMISSION_GBP_PER_KWH: dict[str, float] = {
    "sme": 0.0125,             # midpoint 0.5-2.0p/kWh, small business band
    "ic_mid_market": 0.0075,   # midpoint 0.3-1.2p/kWh
    "ic_half_hourly": 0.005,   # midpoint 0.2-0.8p/kWh
}


def acquisition_cost_gbp(channel: str = "pcs_aggregator", is_dual_fuel: bool = False) -> float:
    """One-off residential/SME acquisition cost via a PCS channel. I&C broker
    commission is deliberately NOT modelled here -- it's an ongoing per-kWh
    cost, see broker_commission_gbp(). Unknown channels return 0.0 (e.g. direct/
    brand marketing -- no energy-specific anchor was found, only a low-confidence
    cross-industry estimate the research explicitly flagged as too weak to build
    on; left at 0.0 rather than invented, per R12)."""
    table = (
        CAC_ONE_OFF_GBP_PER_DUAL_FUEL_CUSTOMER if is_dual_fuel
        else CAC_ONE_OFF_GBP_PER_SINGLE_FUEL_CUSTOMER
    )
    return table.get(channel, 0.0)


def broker_commission_gbp(kwh: float, segment: str) -> float:
    """Ongoing I&C/SME broker commission, applied per kWh billed (not per
    acquisition event). segment: 'sme' | 'ic_mid_market' | 'ic_half_hourly'."""
    rate = BROKER_COMMISSION_GBP_PER_KWH.get(segment)
    if rate is None:
        return 0.0
    return round(kwh * rate, 2)


def cost_lines_by_classification() -> dict[str, list[str]]:
    """Every cost line in this module, classified fixed / stepped / variable,
    per B2_OPEX_TAXONOMY_EXPANSION.md category (6). See each line's own 'note'
    for whether the classification is genuinely anchored to a real scale curve
    or a documented simplification (no curve data found -- treated as fixed at
    current scale, not extrapolated)."""
    result: dict[str, list[str]] = {"fixed": [], "stepped": [], "variable": []}
    for name, line in {**INFRASTRUCTURE_COST_LINES, **GOVERNANCE_COST_LINES}.items():
        result[line["classification"]].append(name)
    result["variable"].append("dcc_comms_charge")  # part (a) above, genuinely per-meter
    result["variable"].append("cac_pcs_aggregator")  # per acquired customer
    result["variable"].append("broker_commission")  # per kWh billed
    return result


def break_even_customer_count(
    fixed_floor_gbp: float, avg_gross_margin_gbp_per_customer: float
) -> float | None:
    """Emergent break-even: customer count (at a given average gross margin per
    customer) needed for gross margin to cover the fixed floor. None if average
    margin <= 0 -- break-even is genuinely undefined/unreachable at that mix, a
    real diagnostic finding (R12: report it, never hide or fudge it)."""
    if avg_gross_margin_gbp_per_customer <= 0:
        return None
    return round(fixed_floor_gbp / avg_gross_margin_gbp_per_customer, 1)


def break_even_analysis(
    segment_avg_gross_margin_gbp: dict[str, float],
    current_mix_counts: dict[str, int],
    fixed_floor_gbp: float,
) -> dict[str, Any]:
    """The named 'investor thesis, quantified' output: book size + mix at which
    gross margin covers the fixed (4)+(5) floor. Two views: (a) at the CURRENT
    observed segment mix, book size needed to break even; (b) per-segment
    sensitivity -- book size needed if the book were 100% one segment. This is
    purely descriptive of the current run's real segment economics -- R12
    (anti-goal-seek) applies in full: never tuned toward a target, recomputed
    fresh each run."""
    total_customers = sum(current_mix_counts.values())
    if total_customers == 0:
        weighted_avg_margin = 0.0
    else:
        weighted_avg_margin = sum(
            segment_avg_gross_margin_gbp.get(seg, 0.0) * count
            for seg, count in current_mix_counts.items()
        ) / total_customers

    at_current_mix = break_even_customer_count(fixed_floor_gbp, weighted_avg_margin)
    per_segment = {
        seg: break_even_customer_count(fixed_floor_gbp, avg_margin)
        for seg, avg_margin in segment_avg_gross_margin_gbp.items()
    }

    return {
        "fixed_floor_gbp": round(fixed_floor_gbp, 2),
        "weighted_avg_gross_margin_gbp_per_customer": round(weighted_avg_margin, 2),
        "break_even_customers_at_current_mix": at_current_mix,
        "break_even_customers_per_segment_if_pure": per_segment,
        "current_book_size": total_customers,
        "covers_floor_at_current_mix": (
            total_customers >= at_current_mix if at_current_mix else False
        ),
    }
