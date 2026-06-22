"""Phase 2b — Gas Dual Fuel.

Adds gas supply to C1-C4 resi customers (dual fuel). Runs 2016-2025 with:
  - Electricity-only: C5, C6 (SME, PC3)
  - Dual fuel: C1-C4 (electricity PC1) + C1g-C4g (gas, daily, flat AQ/365)

Key differences from Phase 2a repriced:
  - Gas price feed: NBP SAP from sim/gas_data/nbp_sap.csv (FRED/IMF monthly)
  - Gas settlement: daily granularity, AQ/365 flat consumption
  - Gas forward curve: same generate_forward_price() logic on NBP records
  - Gas risk engine: assess_term_risk() with NBP records (same dual-window VaR)
  - Shared treasury: electricity + gas capital costs deducted from same pot
  - Starting treasury: scaled by total energy volume (elec + gas)

Delegation note: hand-written (orchestration-adjacent, per protocol).
"""

import statistics
from collections import defaultdict
from datetime import date, timedelta

import sim.risk_committee_agent as risk_committee_agent
from company.pricing.tariff_engine import (
    PORTFOLIO_PREMIUM_LOOKBACK,
    CompanyTariffEngine,
    compute_portfolio_premium,
)
from saas.customer_reaction import _billing_account_id
from saas.customers import (
    ACQUIRED_CUSTOMERS,
    CUSTOMERS,
    SUCCESSOR_CUSTOMERS,
    get_customer,
    make_acquired_customer,
)
from saas.growth_mandate import (
    COST_PER_ACQUISITION,
    FIXED_COST_MONTHLY,
    MANDATE,
    roll_acquisition,
)
from saas.ledger import (
    make_acquisition_spend_event,
    make_fixed_cost_event,
    make_retention_cost_event,
)
from saas.property_model import (
    DEFAULT_ASSETS,
    DEFAULT_HEATING_SYSTEM,
    DEFAULT_OCCUPANCY_PATTERN,
    build_properties,
)
from saas.tariff_pricing import TOU_OFFPEAK_MULTIPLIER, TOU_PEAK_MULTIPLIER, price_fixed_tariff
from sim.cache_store import get_cached_prices, log_cache_access
from sim.forward_curve import (
    SUMMER_MULTIPLIER,
    WINTER_MONTHS,
    WINTER_MULTIPLIER,
    generate_forward_price,
)
from sim.gas_prices_history import load_nbp_history
from company.pricing.margin_feedback import compute_margin_surcharge
from company.risk.hedge_policy import (
    COMPANY_MIN_HEDGE_FLOOR as MIN_HEDGE_FLOOR,
    company_evolve_hedge_fraction as evolve_hedge_fraction,
)
from sim.profile_class_1 import load_pc1_shape
from sim.profile_class_3 import load_pc3_shape
from sim.risk_committee import RiskCommitteeMonitor
from sim.risk_engine import assess_term_risk, is_administration_triggered
from sim.system_prices_history import get_system_prices_range
from sim.weather_price_sensitivity import weather_sensitivity_multiplier
from simulation.customer_events import roll_lifecycle_event
from simulation.demand_model import build_demand_shape
from simulation.gas_settlement import run_gas_term
from simulation.hedged_settlement import run_hedged_term
from simulation.policy_costs import (
    get_gas_ccl_per_mwh,
    get_gas_network_cost_per_mwh,
    get_ggl_per_mwh,
)
from simulation.volume_tolerance import compute_term_volume_tolerance
from simulation.triad import identify_triad_candidates, compute_triad_exposure, _triad_year
from simulation.hh_consumption import (
    estimate_annual_kwh,
    hh_shape_fn,
    is_hh_customer,
    load_hh_consumption,
)
from simulation.renewals import NOTICE_DAYS, build_renewal_schedule
from simulation.settlement import CONTRACT_LENGTH_DAYS
from simulation.weather_inputs import cloud_cover_for_customer, lookback_mean_temps, weather_means_for_customer

REPORT_START = "2016-01-01"
REPORT_END = "2025-06-07"
CRISIS_YEARS = {"2021", "2022"}

# Treasury scaled by total EAC across all commodities
# Base: £3,250 per 15,000 kWh of electricity EAC
ELEC_CUSTOMERS = [c for c in CUSTOMERS if c["commodity"] == "electricity"]
GAS_CUSTOMERS = [c for c in CUSTOMERS if c["commodity"] == "gas"]
# Phase 7e: successor electricity customers (activated on home-move win).
# Separate from ELEC_CUSTOMERS so they don't inflate the starting treasury.
SUCCESSOR_ELEC_CUSTOMERS = [c for c in SUCCESSOR_CUSTOMERS if c["commodity"] == "electricity"]
SUCCESSOR_MAP: dict[str, str] = {
    c["successor_of"]: c["customer_id"] for c in SUCCESSOR_ELEC_CUSTOMERS
}
_SUCCESSOR_ELEC_IDS: frozenset[str] = frozenset(c["customer_id"] for c in SUCCESSOR_ELEC_CUSTOMERS)
_ALL_KNOWN_CUSTOMERS = CUSTOMERS + SUCCESSOR_CUSTOMERS
ORIGINAL_4_CUSTOMER_EAC_KWH = 15_000

# Phase 6a: HH (smart meter) customers have eac_kwh=None — their effective
# EAC for hedging-volume sizing and treasury scaling is derived from real
# half-hourly consumption data (simulation/hh_consumption.py) instead.
EFFECTIVE_EAC_KWH: dict[str, float] = {
    c["customer_id"]: c["eac_kwh"] if c["eac_kwh"] is not None
    else estimate_annual_kwh(load_hh_consumption(c["customer_id"]))
    for c in ELEC_CUSTOMERS
}
# Successor customers share the same property EAC as their predecessor.
EFFECTIVE_EAC_KWH.update({
    c["customer_id"]: c["eac_kwh"]
    for c in SUCCESSOR_ELEC_CUSTOMERS
})

# Treasury sized on original customers only — successors don't exist yet at t=0.
TOTAL_ELEC_EAC = sum(
    EFFECTIVE_EAC_KWH[c["customer_id"]] for c in ELEC_CUSTOMERS
)
TOTAL_GAS_AQ = sum(c["aq_kwh"] for c in GAS_CUSTOMERS)
# Gas is priced ~10x cheaper per MWh than electricity; weight accordingly
# Treat 1 kWh gas ≈ 0.25 kWh electricity for treasury sizing (conservative)
GAS_ELEC_WEIGHT = 0.25
EFFECTIVE_EAC = TOTAL_ELEC_EAC + TOTAL_GAS_AQ * GAS_ELEC_WEIGHT
STARTING_TREASURY_GBP = 3250.0 * (EFFECTIVE_EAC / ORIGINAL_4_CUSTOMER_EAC_KWH)

# Phase 5c minimum hedge mandate: every term starts at the mandate floor
# (sim.hedging_strategy.MIN_HEDGE_FLOOR), not a neutral 50/50 guess.
RESET_HEDGE_FRACTION = MIN_HEDGE_FLOOR

RETENTION_THRESHOLD = 0.30
RETENTION_EFFECTIVENESS = 0.20

# Phase 14a: tiered discount — risk-proportional rather than flat 5%
# Higher churn risk warrants a larger offer; borderline cases get a lighter touch.
RETENTION_TIERS: list[tuple[float, float]] = [
    (0.75, 0.08),  # high risk (≥75%): 8% discount
    (0.50, 0.05),  # medium risk (50-75%): 5% discount
    (0.30, 0.03),  # low-risk-above-threshold (30-50%): 3% discount
]


def _retention_discount_for_risk(company_est: float) -> float:
    """Return the retention discount fraction appropriate for the churn estimate."""
    for threshold, discount in RETENTION_TIERS:
        if company_est >= threshold:
            return discount
    return 0.0

EARLIEST_SSP_DATE = "2015-11-07"
COMMITTEE_COOLDOWN_PERIODS = 1440

SHAPE_LOADERS = {1: load_pc1_shape, 3: load_pc3_shape}

# Phase 4c-1 property records only cover resi electricity customers (C1-C4).
# SME customers (C5, C6) get this default property for 4c-2's demand-shape
# adjustment — no occupancy/asset seed data exists for them.
DEFAULT_PROPERTY = {
    "heating_system": DEFAULT_HEATING_SYSTEM,
    "occupancy_pattern": DEFAULT_OCCUPANCY_PATTERN,
    "assets": dict(DEFAULT_ASSETS),
}


def _weather_adjusted_shape_fn(
    base_shape_fn,
    weather_means: dict[str, float],
    property_record: dict,
    cloud_cover_means: dict[str, float] | None = None,
    latitude_deg: float | None = None,
):
    """Wrap a SHAPE_LOADERS[...] base-shape function with 4c-2's
    weather/occupancy/asset demand adjustment (`build_demand_shape`).

    Falls back to the unadjusted base shape on dates with no weather data
    (e.g. outside sim/weather_data's 2016-01-01..2025-06-07 coverage).

    Phase 25a: cloud_cover_means + latitude_deg enable solar irradiance
    reduction for customers with assets.solar=True (currently C4).
    """
    from datetime import date as _date
    from sim.weather_engine import half_hourly_solar_irradiance

    def shape_fn(date_str):
        base_shape = base_shape_fn(date_str)
        mean_temp = weather_means.get(date_str)
        if mean_temp is None:
            return base_shape
        irradiance = None
        if cloud_cover_means is not None and latitude_deg is not None:
            cloud_pct = cloud_cover_means.get(date_str)
            if cloud_pct is not None:
                day_of_year = _date.fromisoformat(date_str).timetuple().tm_yday
                irradiance = [
                    half_hourly_solar_irradiance(day_of_year, p, latitude_deg, cloud_pct)
                    for p in range(1, 49)
                ]
        return build_demand_shape(base_shape, mean_temp, "electricity", property_record, irradiance)

    return shape_fn


def _clamp_term_end(term_start: str, end_date: str = REPORT_END) -> str:
    natural = (date.fromisoformat(term_start) + timedelta(days=CONTRACT_LENGTH_DAYS)).isoformat()
    if natural > end_date:
        return (date.fromisoformat(end_date) + timedelta(days=1)).isoformat()
    return natural


def _bootstrap_first_term_forward_price(
    term_start: str, gas_records: list[dict],
    contract_length_months: int = 12, lookback_days: int = 90, risk_factor: float = 1.2,
    lookback_daily_mean_temps_c: list[float] | None = None,
) -> float:
    """Forward price for a customer's first gas term when NBP history begins
    on (not before) term_start — the standard 90-day-prior lookback in
    generate_forward_price() finds nothing and raises ValueError.

    Mirrors generate_forward_price()'s base + volatility-premium + seasonal
    formula exactly, but draws its window from the first lookback_days of
    *available* records starting at term_start, since no prior data exists.
    This is a one-time bootstrap for the very first term only — every
    subsequent renewal has a full prior-history window and uses
    generate_forward_price() unchanged.
    """
    start_date = date.fromisoformat(term_start)
    window_end = start_date + timedelta(days=lookback_days - 1)

    filtered_records = [
        record for record in gas_records
        if start_date <= date.fromisoformat(record["settlementDate"]) <= window_end
    ]

    base_price = statistics.mean(record["systemSellPrice"] for record in filtered_records)
    volatility_premium = statistics.pstdev(
        record["systemSellPrice"] for record in filtered_records
    ) * risk_factor
    forward_base = base_price + volatility_premium

    start_month = start_date.month
    seasonal_multipliers = [
        WINTER_MULTIPLIER if ((start_month - 1 + offset) % 12 + 1) in WINTER_MONTHS else SUMMER_MULTIPLIER
        for offset in range(contract_length_months)
    ]
    seasonal_multiplier = statistics.mean(seasonal_multipliers)
    forward_price = forward_base * seasonal_multiplier

    if lookback_daily_mean_temps_c is not None:
        forward_price *= weather_sensitivity_multiplier(lookback_daily_mean_temps_c)

    return forward_price


def _build_gas_renewal_schedule(
    customer: dict, gas_records: list[dict], lookback_temps_fn=None,
    report_end: str = REPORT_END,
) -> list[dict]:
    """Build renewal schedule for a gas customer using NBP forward prices.

    lookback_temps_fn (Phase 4c-3, optional): see
    `simulation.renewals.build_renewal_schedule` — same callable, threaded
    through to `generate_forward_price`'s `lookback_daily_mean_temps_c`.
    Phase 30b: gas CCL + GGL (policy) and gas network cost passed through in unit rate.
    """
    aq_kwh = customer["aq_kwh"]
    acq_date = customer["acquisition_date"]
    cust_segment = customer.get("segment", "resi")
    schedule = []
    term_start = acq_date

    _company_engine = CompanyTariffEngine()
    while term_start <= report_end:
        term_end = _clamp_term_end(term_start, end_date=report_end)
        lookback_temps = lookback_temps_fn(term_start) if lookback_temps_fn else None
        try:
            sim_fwd = generate_forward_price(term_start, gas_records, lookback_daily_mean_temps_c=lookback_temps)
        except ValueError:
            if not schedule:
                sim_fwd = _bootstrap_first_term_forward_price(
                    term_start, gas_records, lookback_daily_mean_temps_c=lookback_temps
                )
            else:
                break
        # Phase 34a: gas tariffs also priced NOTICE_DAYS before term start.
        gas_notice_date = (date.fromisoformat(term_start) - timedelta(days=NOTICE_DAYS)).isoformat()
        try:
            company_fwd = _company_engine.get_forward_price("gas", gas_notice_date, gas_records)
        except ValueError:
            company_fwd = sim_fwd  # fallback: insufficient prior data for first term
        # Phase 30b: gas policy cost (CCL + GGL) and network charges pass-through.
        # CCL: domestic gas exempt; GGL applies from Nov 2021.
        gas_policy = (
            get_gas_ccl_per_mwh(term_start, cust_segment)
            + get_ggl_per_mwh(term_start, aq_kwh)
        )
        gas_network = get_gas_network_cost_per_mwh(term_start)
        unit_rate = price_fixed_tariff(
            company_fwd, aq_kwh, term_start,
            naked_fraction=1 - MIN_HEDGE_FLOOR,
            policy_cost_per_mwh=gas_policy,
            network_cost_per_mwh=gas_network,
        )
        schedule.append({
            "acquisition_date": term_start,
            "notice_date": gas_notice_date,
            "term_end": term_end,
            "forward_price_gbp_per_mwh": sim_fwd,
            "company_forward_price_gbp_per_mwh": company_fwd,
            "unit_rate_gbp_per_mwh": unit_rate,
        })
        term_start = term_end  # next term starts where this ends

    return schedule


def _build_churn_basis_risk(customer_events_log: list) -> list[dict]:
    """Phase 11b + 39a: Build churn basis risk records with SVT comparison."""
    from simulation.svt_rates import get_svt_elec_rate_gbp_per_mwh

    records = []
    for e in customer_events_log:
        if e.get("company_churn_estimate") is None:
            continue
        unit_rate = e.get("unit_rate_gbp_per_mwh")
        term_start = e["event_date"]
        svt_rate = get_svt_elec_rate_gbp_per_mwh(term_start)
        rate_vs_svt_pct = None
        if unit_rate is not None and svt_rate is not None and svt_rate > 0:
            rate_vs_svt_pct = round((unit_rate - svt_rate) / svt_rate * 100.0, 2)
        records.append({
            "customer_id": e["customer_id"],
            "term_start": term_start,
            "sim_churn_probability": e["churn_probability"],
            "company_churn_estimate": e["company_churn_estimate"],
            "churn_estimate_error_pct": e["churn_estimate_error_pct"],
            "is_active_renewal": e.get("is_active_renewal", True),
            "unit_rate_gbp_per_mwh": unit_rate,
            "svt_rate_gbp_per_mwh": svt_rate,
            "rate_vs_svt_pct": rate_vs_svt_pct,
        })
    return records


def _build_company_event_log(
    customer_events_log: list,
    won_successor_activations: dict,
    fresh_acquisitions: list,
    successor_map: dict,
) -> list:
    """Build the company CRM event log from simulation outputs — Phase 12a.

    Returns a list of dicts (one per event) that the company CRM knows about.
    Churn events come from customer_events_log; acquisition events come from
    won_successor_activations (home-move wins) and fresh_acquisitions (market wins).
    """
    result = []
    for evt in customer_events_log:
        if evt["event_type"] == "churned":
            result.append({
                "event_type": "churn",
                "customer_id": evt["customer_id"],
                "event_date": evt["event_date"],
                "reason": "non-renewal",
                "sim_churn_probability": evt.get("churn_probability"),
                "company_churn_estimate": evt.get("company_churn_estimate"),
            })
    for successor_id, activation_date in won_successor_activations.items():
        predecessor = next(
            (p for p, s in successor_map.items() if s == successor_id), None
        )
        result.append({
            "event_type": "acquisition",
            "customer_id": successor_id,
            "event_date": activation_date,
            "channel": "home-move-win",
            "predecessor_id": predecessor,
        })
    for acq in fresh_acquisitions:
        result.append({
            "event_type": "acquisition",
            "customer_id": acq["customer_id"],
            "event_date": acq["event_date"],
            "channel": "market-acquisition",
            "predecessor_id": acq.get("predecessor_id"),
        })
    return sorted(result, key=lambda e: e["event_date"])


def _compute_company_divergence(
    basis_risk_terms: list[dict],
    churn_basis_risk: list[dict],
    demand_estimation_log: list[dict] | None = None,
) -> dict:
    """Aggregate company-model divergence from SIM ground truth, by year -- Phase 12e/23a.

    basis_risk_terms: per-term tariff pricing error (tariff_error_pct = signed)
    churn_basis_risk: per-renewal churn estimate error (churn_estimate_error_pct = signed, may be None)
    demand_estimation_log: per-renewal EAC estimation error (Phase 23a)
    Returns: {tariff_error_by_year, churn_error_by_year, demand_error_by_year}
    """
    by_year_tariff: dict[str, list[float]] = defaultdict(list)
    for b in basis_risk_terms:
        by_year_tariff[b["term_start"][:4]].append(abs(b["tariff_error_pct"]))

    by_year_churn: dict[str, list[float]] = defaultdict(list)
    for c in churn_basis_risk:
        if c.get("churn_estimate_error_pct") is not None:
            by_year_churn[c["term_start"][:4]].append(abs(c["churn_estimate_error_pct"]))

    by_year_demand: dict[str, list[float]] = defaultdict(list)
    for d in (demand_estimation_log or []):
        by_year_demand[d["term_start"][:4]].append(abs(d["error_pct"]))

    def _summarize(by_year: dict) -> dict:
        return {
            yr: {
                "n": len(errs),
                "mean_abs_error_pct": round(sum(errs) / len(errs), 4),
                "max_abs_error_pct": round(max(errs), 4),
            }
            for yr, errs in sorted(by_year.items())
        }

    return {
        "tariff_error_by_year": _summarize(by_year_tariff),
        "churn_error_by_year": _summarize(by_year_churn),
        "demand_error_by_year": _summarize(by_year_demand),
    }




def _derive_eac_from_settlement(cid: str, all_records: list[dict]) -> float:
    """Mean actual annual consumption from all available settlement records.

    Phase 25a: used as SIM oracle for the demand_estimation_log, replacing
    the declared EAC (EFFECTIVE_EAC_KWH) which mismatches actual consumption
    for EV customers (C2/C4: declared 3500/5500 kWh, actual ~6820 kWh with EV).
    Falls back to EFFECTIVE_EAC_KWH when fewer than 180 days of records exist.
    """
    from datetime import date as _date
    recs = [
        r for r in all_records
        if r.get("customer_id") == cid and r.get("consumption_kwh") is not None
    ]
    if not recs:
        return EFFECTIVE_EAC_KWH.get(cid, 0.0)
    dates = [r["settlement_date"] for r in recs]
    total_days = (_date.fromisoformat(max(dates)) - _date.fromisoformat(min(dates))).days + 1
    if total_days < 180:
        return EFFECTIVE_EAC_KWH.get(cid, 0.0)
    return sum(r["consumption_kwh"] for r in recs) / total_days * 365.25


def _company_eac_estimate(cid: str, term_start_str: str, all_records: list[dict]) -> float:
    """Estimate customer annual consumption from observable prior-year billing records.

    Phase 23a: replaces SIM-internal EFFECTIVE_EAC_KWH lookup in company-layer decisions.
    The company observes kWh billed in the 12 months before the renewal date.
    Falls back to EFFECTIVE_EAC_KWH on the first term (no prior billing yet).
    """
    from datetime import date as _date
    term_start = _date.fromisoformat(term_start_str)
    year_ago = term_start.replace(year=term_start.year - 1)
    estimated = sum(
        r["consumption_kwh"]
        for r in all_records
        if r.get("customer_id") == cid
        and r.get("consumption_kwh") is not None
        and year_ago <= _date.fromisoformat(r["settlement_date"]) < term_start
    )
    return estimated if estimated > 0 else EFFECTIVE_EAC_KWH.get(cid, 0.0)


def main(report_end: str | None = None, sim_interface=None):
    """Run the full Phase 2b + 4c settlement simulation.

    report_end: ISO date string (e.g. "2022-12-31") to truncate the
        simulation window for faster iteration. Defaults to REPORT_END
        (the full 2016-2025 window). Use --end-year on the annual_report
        CLI or pass directly for experiment runs.
    """
    effective_end = report_end or REPORT_END
    print("=== Phase 2b — Gas Dual Fuel ===")
    print(f"Electricity customers: {[c['customer_id'] for c in ELEC_CUSTOMERS]}")
    print(f"Gas customers:         {[c['customer_id'] for c in GAS_CUSTOMERS]}")
    print(f"Elec EAC: {TOTAL_ELEC_EAC:,.0f} kWh  Gas AQ: {TOTAL_GAS_AQ:,} kWh")
    print(f"Starting treasury: £{STARTING_TREASURY_GBP:.2f}")
    if effective_end != REPORT_END:
        print(f"[Truncated window: {REPORT_START} to {effective_end}]\n")
    else:
        print()

    # ---- Load price feeds ----
    earliest_acq = min(
        date.fromisoformat(c["acquisition_date"])
        for c in ELEC_CUSTOMERS + GAS_CUSTOMERS
    )
    fetch_start_natural = (earliest_acq - timedelta(days=365)).isoformat()
    fetch_start = max(fetch_start_natural, EARLIEST_SSP_DATE)

    cached = get_cached_prices(fetch_start, effective_end)
    if cached is not None:
        elec_records = cached
        print(f"Cache hit: {len(elec_records):,} SSP records.")
        log_cache_access("elexon_ssp_full.json", hit=True, phase="2b")
    else:
        elec_records = get_system_prices_range(fetch_start, effective_end)
        log_cache_access("elexon_ssp_full.json", hit=False, phase="2b")
    print(f"Electricity: {len(elec_records):,} SSP records ({fetch_start} to {effective_end}).")

    gas_records = load_nbp_history()
    print(f"Gas: {len(gas_records):,} NBP daily records.\n")

    elec_price_lookup = {
        (r["settlementDate"], r["settlementPeriod"]): r["systemSellPrice"]
        for r in elec_records
    }

    # ---- Phase 4c-1/4c-2/4c-3 inputs: per-customer weather + property records ----
    properties = build_properties(CUSTOMERS)
    weather_by_customer = {
        c["customer_id"]: weather_means_for_customer(c)
        for c in ELEC_CUSTOMERS + GAS_CUSTOMERS + SUCCESSOR_ELEC_CUSTOMERS
    }
    # Phase 25a: cloud cover for solar customers (C4 has assets.solar=True).
    cloud_cover_by_customer = {
        c["customer_id"]: cloud_cover_for_customer(c)
        for c in ELEC_CUSTOMERS + SUCCESSOR_ELEC_CUSTOMERS
        if properties.get(c["customer_id"], {}).get("assets", {}).get("solar")
    }

    # Phase 6a: per-customer HH consumption for HH (smart meter) customers.
    hh_consumption_by_customer = {
        c["customer_id"]: load_hh_consumption(c["customer_id"])
        for c in ELEC_CUSTOMERS if is_hh_customer(c)
    }

    def _lookback_temps_fn(cid):
        weather_means = weather_by_customer[cid]
        return lambda term_start: lookback_mean_temps(weather_means, term_start)

    # ---- Build electricity schedules ----
    elec_schedules = {}
    for c in ELEC_CUSTOMERS:
        elec_schedules[c["customer_id"]] = build_renewal_schedule(
            c["customer_id"], c["acquisition_date"], effective_end,
            elec_records, EFFECTIVE_EAC_KWH[c["customer_id"]],
            lookback_temps_fn=_lookback_temps_fn(c["customer_id"]),
            segment=c.get("segment", "resi"),
        )

    # Phase 7e: pre-generate successor schedules (gated until activation).
    # Successors use the same acquisition_date as their predecessor so the
    # term schedule aligns — actual settlement only starts at the churn date.
    for c in SUCCESSOR_ELEC_CUSTOMERS:
        elec_schedules[c["customer_id"]] = build_renewal_schedule(
            c["customer_id"], c["acquisition_date"], effective_end,
            elec_records, EFFECTIVE_EAC_KWH[c["customer_id"]],
            lookback_temps_fn=_lookback_temps_fn(c["customer_id"]),
            segment=c.get("segment", "resi"),
        )

    # ---- Build gas schedules ----
    gas_schedules = {}
    for c in GAS_CUSTOMERS:
        gas_schedules[c["customer_id"]] = _build_gas_renewal_schedule(
            c, gas_records, lookback_temps_fn=_lookback_temps_fn(c["customer_id"]),
            report_end=effective_end,
        )

    # ---- Interleave all terms chronologically ----
    all_terms = []
    for cid, schedule in elec_schedules.items():
        for term in schedule:
            all_terms.append((term["acquisition_date"], cid, "electricity", term))
    for cid, schedule in gas_schedules.items():
        for term in schedule:
            all_terms.append((term["acquisition_date"], cid, "gas", term))
    all_terms.sort(key=lambda x: (x[0], x[1]))

    # ---- Simulation state ----
    treasury = STARTING_TREASURY_GBP
    monitor = RiskCommitteeMonitor(treasury)

    all_customers_ids = (
        [c["customer_id"] for c in ELEC_CUSTOMERS]
        + [c["customer_id"] for c in GAS_CUSTOMERS]
        + [c["customer_id"] for c in SUCCESSOR_ELEC_CUSTOMERS]
    )
    # Phase 7e: successor_id → activation_date (set when home-move is won).
    # Gate: successor terms are skipped until their activation date.
    won_successor_activations: dict[str, str] = {}
    next_hf = {cid: RESET_HEDGE_FRACTION for cid in all_customers_ids}
    pending_committee_overrides: dict[str, float] = {}
    current_risk: dict[str, dict] = {}
    current_hf: dict[str, float] = {cid: RESET_HEDGE_FRACTION for cid in all_customers_ids}

    # Phase 16c + 19a: track prior-term realized margin + revenue per customer (all commodities)
    # Gas customers use separate CIDs (C1g, C2g, etc.) so this dict works for both.
    prev_term_margin: dict[str, float] = {}
    prev_term_revenue: dict[str, float] = {}
    margin_feedback_log: list[dict] = []
    # Phase 22a: post-crisis hangover — how many more renewals get the +12% churn uplift
    hangover_remaining: dict[str, int] = {}
    CRISIS_HANGOVER_LOSS_THRESHOLD = 0.20  # trigger: net loss > 20% of term revenue

    # Phase 17a + 19a: rolling portfolio-wide margin rates for learning premium
    portfolio_elec_margin_rates: list[float] = []
    portfolio_gas_margin_rates: list[float] = []  # Phase 19a: separate gas tracking
    dynamic_pricing_log: list[dict] = []

    all_records: list[dict] = []
    evolution_logs: dict[str, list] = {cid: [] for cid in all_customers_ids}
    term_indices: dict[str, int] = {cid: 0 for cid in all_customers_ids}
    committee_wake_ups: list[dict] = []
    customer_events_log: list[dict] = []
    churned_billing_accounts: set[str] = set()
    administration_event = None
    periods_since_committee = COMMITTEE_COOLDOWN_PERIODS
    total_periods_processed = 0
    PROGRESS_EVERY_PERIODS = 100

    # Phase 23a: demand estimation divergence tracking
    demand_estimation_log: list[dict] = []

    # Phase 8a: growth mandate tracking
    acquisition_spend_events: list[dict] = []
    fixed_cost_events: list[dict] = []
    _acquisition_counter: dict[str, int] = {}  # base_id -> next fresh-acquisition suffix
    _fixed_cost_emitted: set[str] = set()  # months already charged (dedup across customers)

    # Phase 11a: basis risk tracking — company_fwd vs sim_fwd per term
    basis_risk_terms: list[dict] = []
    # Phase 11b: track previous electricity unit rate per customer for churn estimate
    prev_elec_unit_rates: dict[str, float] = {}
    # Phase 14b: track previous gas unit rate for gas company churn estimate
    prev_gas_unit_rates: dict[str, float] = {}
    # Phase 12a: fresh acquisition wins for company_event_log
    fresh_acquisitions: list[dict] = []
    # Phase 12b: retention cost events and log
    retention_cost_events: list[dict] = []
    retention_log: list[dict] = []
    # Phase 12c: churns where no offer was made (missed opportunities)
    no_offer_churn_log: list[dict] = []
    # Phase 14b: gas renewal rate pressure log for dual-fuel monitoring
    company_gas_churn_log: list[dict] = []
    # Phase 27c: volume tolerance tracking for I&C customers
    volume_tolerance_log: list[dict] = []

    current_year_str = REPORT_START[:4]
    ytd_gross = ytd_net = ytd_capital = 0.0

    print("=== Processing terms chronologically ===\n")

    for term_start_str, cid, commodity, term in all_terms:
        if administration_event:
            break

        # Phase 6b: skip churned accounts (billing-account level — covers both elec + gas legs)
        billing_account = _billing_account_id(cid)
        if billing_account in churned_billing_accounts:
            term_indices[cid] += 1
            continue

        # Phase 7e: gate successor terms until activated by a home-move win.
        # Do NOT increment term_indices here — we want term_index=0 on first real term
        # so the churn roll doesn't fire prematurely.
        if cid in _SUCCESSOR_ELEC_IDS:
            activation_date = won_successor_activations.get(cid)
            if not activation_date or term_start_str < activation_date:
                continue

        term_end_str = term.get("term_end") or _clamp_term_end(term_start_str, end_date=effective_end)
        forward_price = term["forward_price_gbp_per_mwh"]        # sim's sophisticated estimate
        company_fwd = term.get("company_forward_price_gbp_per_mwh", forward_price)
        unit_rate = term["unit_rate_gbp_per_mwh"]
        term_index = term_indices[cid]
        term_indices[cid] += 1

        # Phase 17a + 19a: portfolio learning premium (electricity and gas)
        _portfolio_rates = (
            portfolio_elec_margin_rates if commodity == "electricity" else portfolio_gas_margin_rates
        )
        if term_index >= 1 and len(_portfolio_rates) >= 1:
            lookback = _portfolio_rates[-PORTFOLIO_PREMIUM_LOOKBACK:]
            portfolio_prem = compute_portfolio_premium(lookback)
            if abs(portfolio_prem) > 1e-6:
                rate_before = unit_rate
                unit_rate *= (1.0 + portfolio_prem)
                dynamic_pricing_log.append({
                    "customer_id": cid,
                    "commodity": commodity,
                    "term_start": term_start_str,
                    "recent_margin_rates": [round(r, 4) for r in lookback],
                    "mean_recent_margin_rate": round(sum(lookback) / len(lookback), 4),
                    "portfolio_premium_pct": round(portfolio_prem * 100, 2),
                    "unit_rate_before": round(rate_before, 4),
                    "unit_rate_after": round(unit_rate, 4),
                })

        # Phase 16c + 19a: apply realized-margin recovery surcharge at renewal (all commodities)
        if term_index >= 1 and cid in prev_term_margin:
            surcharge = compute_margin_surcharge(prev_term_margin[cid], prev_term_revenue.get(cid, 0.0))
            if surcharge > 0:
                unit_rate *= (1.0 + surcharge)
                margin_feedback_log.append({
                    "customer_id": cid,
                    "commodity": commodity,
                    "term_start": term_start_str,
                    "prev_margin_gbp": round(prev_term_margin[cid], 4),
                    "prev_revenue_gbp": round(prev_term_revenue.get(cid, 0.0), 4),
                    "surcharge_pct": round(surcharge * 100, 2),
                    "unit_rate_before": round(term["unit_rate_gbp_per_mwh"], 4),
                    "unit_rate_after": round(unit_rate, 4),
                })

        # Phase 11a: record basis risk (company estimate vs sim ground truth)
        basis_risk_terms.append({
            "customer_id": cid,
            "commodity": commodity,
            "term_start": term_start_str,
            "company_fwd_gbp_per_mwh": company_fwd,
            "sim_fwd_gbp_per_mwh": forward_price,
            "tariff_error_pct": (company_fwd - forward_price) / forward_price if forward_price else 0.0,
        })

        # Phase 11b + 14b: capture previous rates before updating
        old_elec_rate = prev_elec_unit_rates.get(cid) if commodity == "electricity" else None
        old_gas_rate = prev_gas_unit_rates.get(cid) if commodity == "gas" else None
        if commodity == "electricity":
            prev_elec_unit_rates[cid] = unit_rate
        elif commodity == "gas":
            prev_gas_unit_rates[cid] = unit_rate

        if term_index >= 1 and commodity == "electricity":
            company_est_pre = None
            retention_modifier_val = None
            _no_offer_reason = "below_threshold"
            # Phase 33: active/passive renewal split. Default True until we know the rate.
            active_renewal = True
            passive_cap = None
            if old_elec_rate is not None:
                from company.crm.churn_model import (
                    estimate_churn_probability as _est_churn,
                    is_active_renewal as _is_active_renewal,
                    estimate_passive_churn_probability as _est_passive_churn,
                    PASSIVE_CHURN_CAP as _PASSIVE_CHURN_CAP,
                )
                active_renewal = _is_active_renewal(term_start_str, f"{billing_account}_{term_index}")
                passive_cap = None if active_renewal else _PASSIVE_CHURN_CAP
                acq_date_for_est = next(
                    (c["acquisition_date"] for c in _ALL_KNOWN_CUSTOMERS if c["customer_id"] == billing_account),
                    term_start_str,
                )
                tenure_for_est = (date.fromisoformat(term_start_str) - date.fromisoformat(acq_date_for_est)).days / 365.25
                # Phase 15d: pass previous-term hedge fraction — well-hedged customers
                # experienced stable prices, making them less rate-sensitive at renewal.
                prev_hf = current_hf.get(cid, 0.0)
                hangover_periods = hangover_remaining.get(cid, 0)
                # Phase 23a: company estimates EAC from observable prior-year billing
                company_eac = _company_eac_estimate(cid, term_start_str, all_records)
                # Phase 25a: true_eac is mean annual settled consumption (actual, not declared).
                # Fixes misleading ~100% error for EV customers (C2/C4 declared 3500/5500
                # kWh but actually consume ~6820 kWh/year with EV charging).
                true_eac = _derive_eac_from_settlement(cid, all_records) or EFFECTIVE_EAC_KWH.get(cid, 0.0)
                if true_eac > 0:
                    eac_err_pct = (company_eac - true_eac) / true_eac * 100.0
                    demand_estimation_log.append({
                        "customer_id": cid,
                        "term_start": term_start_str,
                        "company_eac_kwh": round(company_eac),
                        "true_eac_kwh": round(true_eac),
                        "error_pct": round(eac_err_pct, 2),
                        "source": "prior_billing" if company_eac != true_eac else "fallback",
                    })
                # Phase 27e: I&C segment uses broker-driven churn model
                cust_for_churn = next(
                    (c for c in _ALL_KNOWN_CUSTOMERS if c["customer_id"] == billing_account), None
                )
                segment_for_churn = cust_for_churn.get("segment", "resi") if cust_for_churn else "resi"
                # Phase 33: passive renewers use SVT-inertia constants; active use full model.
                # I&C customers are always active (brokers shop every renewal — no passive roll).
                if not active_renewal and segment_for_churn != "I&C":
                    company_est_pre = round(_est_passive_churn(
                        old_elec_rate, unit_rate, tenure_for_est,
                    ), 4)
                else:
                    company_est_pre = round(_est_churn(
                        old_elec_rate, unit_rate, tenure_for_est,
                        company_eac,
                        hedge_fraction=prev_hf,
                        hangover_periods_remaining=hangover_periods,
                        segment=segment_for_churn,
                    ), 4)
                if hangover_periods > 0:
                    hangover_remaining[cid] = hangover_periods - 1
                if company_est_pre > RETENTION_THRESHOLD:
                    eac_for_ret = company_eac  # Phase 23a: use company estimate
                    discount_pct = _retention_discount_for_risk(company_est_pre)
                    ret_cost = unit_rate * discount_pct * eac_for_ret / 1000.0
                    expected_margin = (unit_rate - company_fwd) * eac_for_ret / 1000.0
                    # Phase 15b: include acquisition cost savings in the offer guard.
                    # If the customer churns, the company spends acq_cost on a replacement
                    # attempt (whether it wins or not). So the true value protected by
                    # retaining = expected_margin + acq_cost_saved.
                    cust_data_ret = get_customer(billing_account)
                    seg_ret = cust_data_ret["segment"] if cust_data_ret else "resi"
                    acq_cost_saved = COST_PER_ACQUISITION.get(seg_ret, 150.0)
                    if expected_margin + acq_cost_saved > ret_cost:
                        retention_modifier_val = RETENTION_EFFECTIVENESS
                        retention_cost_events.append(
                            make_retention_cost_event(billing_account, term_start_str, ret_cost, company_est_pre)
                        )
                        retention_log.append({
                            "customer_id": billing_account,
                            "event_date": term_start_str,
                            "company_churn_estimate": company_est_pre,
                            "discount_pct": discount_pct,
                            "retention_cost_gbp": ret_cost,
                            "expected_term_margin_gbp": expected_margin,
                            "acq_cost_saved_gbp": round(acq_cost_saved, 2),
                            "outcome": "pending",
                        })
                    else:
                        _no_offer_reason = "uneconomical"
            event = roll_lifecycle_event(
                cid, term_start_str, commodity, list(all_records), _ALL_KNOWN_CUSTOMERS,
                old_rate_gbp_per_mwh=old_elec_rate,
                new_rate_gbp_per_mwh=unit_rate,
                retention_modifier=retention_modifier_val,
                precomputed_company_estimate=company_est_pre,
                passive_churn_cap=passive_cap,
            )
            if event is not None:
                event["is_active_renewal"] = active_renewal
                event["unit_rate_gbp_per_mwh"] = unit_rate
                customer_events_log.append(event)
                if retention_modifier_val is not None and retention_log:
                    outcome_str = "churned_despite_offer" if event["event_type"] == "churned" else "retained"
                    retention_log[-1]["outcome"] = outcome_str
                    if sim_interface is not None:
                        sim_interface.notify_retention_attempt(
                            billing_account, term_start_str, company_est_pre,
                            discount_pct, outcome=outcome_str
                        )
                if event["event_type"] == "churned":
                    if retention_modifier_val is None:
                        # No offer was made — record as missed retention opportunity
                        eac_missed = company_eac  # Phase 23a: use company estimate
                        no_offer_churn_log.append({
                            "customer_id": billing_account,
                            "event_date": term_start_str,
                            "company_churn_estimate": company_est_pre,
                            "expected_term_margin_gbp": (unit_rate - company_fwd) * eac_missed / 1000.0,
                            "no_offer_reason": _no_offer_reason,
                        })
                    churned_billing_accounts.add(billing_account)
                    print(
                        f"  [CHURN] {billing_account} at {term_start_str} — "
                        f"p_retain={event['effective_retention_probability']:.4f}  "
                        f"roll={event['random_roll']:.4f}"
                    )
                    if sim_interface is not None:
                        sim_interface.notify_churn(
                            billing_account,
                            term_start_str,
                            reason="non-renewal",
                            sim_churn_probability=event.get("churn_probability"),
                            company_churn_estimate=event.get("company_churn_estimate"),
                        )
                    if event.get("home_move_won"):
                        successor_id = SUCCESSOR_MAP.get(billing_account)
                        if successor_id:
                            won_successor_activations[successor_id] = term_start_str
                            print(f"  [WIN] Home-mover won: {successor_id} activates at {term_start_str}")
                            if sim_interface is not None:
                                sim_interface.notify_acquisition(
                                    successor_id,
                                    term_start_str,
                                    channel="home-move-win",
                                    predecessor_id=billing_account,
                                )
                    elif MANDATE != "shrink":
                        customer_data = get_customer(billing_account)
                        segment = customer_data["segment"] if customer_data else "resi"
                        acq_cost = COST_PER_ACQUISITION.get(segment, 150.0)
                        acq_seed = f"acquire_{billing_account}_{term_start_str}"
                        acq_won = roll_acquisition(segment, acq_seed)

                        acquisition_spend_events.append(
                            make_acquisition_spend_event(
                                billing_account, term_start_str, acq_cost, acq_won, segment
                            )
                        )

                        if acq_won:
                            suffix = _acquisition_counter.get(billing_account, 3)
                            _acquisition_counter[billing_account] = suffix + 1
                            new_cid = f"{billing_account}_{suffix}"
                            new_customer = make_acquired_customer(new_cid, customer_data, term_start_str)
                            ACQUIRED_CUSTOMERS.append(new_customer)
                            fresh_acquisitions.append({
                                "customer_id": new_cid,
                                "event_date": term_start_str,
                                "predecessor_id": billing_account,
                            })
                            if sim_interface is not None:
                                sim_interface.notify_acquisition(
                                    new_cid,
                                    term_start_str,
                                    channel="market-acquisition",
                                    predecessor_id=billing_account,
                                )
                            print(
                                f"  [ACQUIRE] Fresh acquisition won: {new_cid} at {term_start_str} "
                                f"(£{acq_cost:.0f}, {segment})"
                            )
                        else:
                            print(
                                f"  [ACQUIRE] Fresh acquisition failed: {billing_account} at {term_start_str} "
                                f"(£{acq_cost:.0f}, {segment})"
                            )
                    continue
            elif retention_modifier_val is not None and retention_log:
                # No lifecycle event — offer made, customer just renewed normally
                retention_log[-1]["outcome"] = "retained"
                if sim_interface is not None:
                    sim_interface.notify_retention_attempt(
                        billing_account, term_start_str, company_est_pre,
                        retention_log[-1]["discount_pct"], outcome="retained"
                    )

        # Phase 14b: compute gas company churn estimate for dual-fuel monitoring.
        # Gas legs don't drive churn decisions (those live at electricity billing-account
        # level), but the company tracks gas renewal rate changes separately to spot
        # early-warning pressure on dual-fuel portfolios.
        if term_index >= 1 and commodity == "gas" and old_gas_rate is not None:
            from company.crm.churn_model import estimate_churn_probability as _est_churn
            gas_customer_data = next(
                (c for c in _ALL_KNOWN_CUSTOMERS if c["customer_id"] == billing_account),
                None,
            )
            if gas_customer_data is not None:
                acq_date_gas = gas_customer_data.get("acquisition_date", term_start_str)
                tenure_gas = (date.fromisoformat(term_start_str) - date.fromisoformat(acq_date_gas)).days / 365.25
                gas_company_est = round(_est_churn(old_gas_rate, unit_rate, tenure_gas, fuel="gas"), 4)
                company_gas_churn_log.append({
                    "customer_id": cid,
                    "billing_account": billing_account,
                    "term_start": term_start_str,
                    "old_gas_rate": round(old_gas_rate, 4),
                    "new_gas_rate": round(unit_rate, 4),
                    "company_gas_churn_estimate": gas_company_est,
                })

        if cid in pending_committee_overrides:
            hf = pending_committee_overrides.pop(cid)
        else:
            hf = next_hf[cid]
        current_hf[cid] = hf

        if commodity == "electricity":
            customer = get_customer(cid)
            # Phase 25a: use calibrated EAC from prior billing records; falls back
            # to declared EAC on first term (no billing history yet).
            eac_kwh = _company_eac_estimate(cid, term_start_str, all_records)
            if is_hh_customer(customer):
                shape_fn = hh_shape_fn(hh_consumption_by_customer[cid])
            else:
                profile_class = customer.get("profile_class", 1)
                property_record = properties.get(cid, DEFAULT_PROPERTY)
                # Phase 25a: pass cloud cover + latitude for solar customers (C4).
                has_solar = property_record.get("assets", {}).get("solar", False)
                cloud_cover = cloud_cover_by_customer.get(cid) if has_solar else None
                latitude = customer.get("location", {}).get("lat") if has_solar else None
                shape_fn = _weather_adjusted_shape_fn(
                    SHAPE_LOADERS[profile_class], weather_by_customer[cid], property_record,
                    cloud_cover_means=cloud_cover, latitude_deg=latitude,
                )

            naked_kwh = eac_kwh * (1.0 - hf)
            risk = assess_term_risk(term_start_str, naked_kwh, forward_price, elec_records)
            counterfactual_risk = assess_term_risk(term_start_str, float(eac_kwh), forward_price, elec_records)
            current_risk[cid] = risk

            # HH (smart meter) customers get ToU pricing — flat unit_rate is the
            # base; peak/off-peak rates are derived from it via the ToU multipliers.
            tou_rates = None
            if is_hh_customer(customer):
                tou_rates = (unit_rate * TOU_PEAK_MULTIPLIER, unit_rate * TOU_OFFPEAK_MULTIPLIER)

            cust_segment = customer.get("segment", "resi") if customer else "resi"
            term_records = run_hedged_term(
                cid, term_start_str, term_end_str, unit_rate, forward_price, hf,
                risk["monthly_cost_of_capital_gbp"], shape_fn, elec_records,
                tou_rates=tou_rates, segment=cust_segment,
            )
            for rec in term_records:
                rec["data_regime"] = "historical"
                rec["commodity"] = "electricity"

            # Phase 27c: volume tolerance for I&C customers.
            if cust_segment == "I&C" and term_records:
                term_days = (
                    date.fromisoformat(term_end_str) - date.fromisoformat(term_start_str)
                ).days
                contracted_term_kwh = eac_kwh * term_days / 365.25
                actual_term_kwh = sum(r["consumption_kwh"] for r in term_records)
                avg_spot = (
                    sum(r.get("wholesale_cost_gbp", 0) for r in term_records)
                    / (sum(r["consumption_kwh"] for r in term_records) / 1000.0)
                    if actual_term_kwh > 0 else 0.0
                )
                vt = compute_term_volume_tolerance(
                    actual_term_kwh, contracted_term_kwh, avg_spot, forward_price, hf
                )
                volume_tolerance_log.append({
                    "customer_id": cid,
                    "term_start": term_start_str,
                    "term_end": term_end_str,
                    **vt,
                })

        else:  # gas
            gas_customer = get_customer(cid)
            aq_kwh = gas_customer["aq_kwh"]

            naked_kwh = aq_kwh * (1.0 - hf)
            risk = assess_term_risk(term_start_str, naked_kwh, forward_price, gas_records)
            counterfactual_risk = assess_term_risk(term_start_str, float(aq_kwh), forward_price, gas_records)
            current_risk[cid] = risk

            term_records = run_gas_term(
                cid, term_start_str, term_end_str, aq_kwh,
                unit_rate, hf, forward_price,
                risk["monthly_cost_of_capital_gbp"], gas_records,
                segment=cust_segment,
            )
            for rec in term_records:
                rec["data_regime"] = "historical"

        settled_this_term: list[dict] = []
        for rec in term_records:
            rec_year = rec["settlement_date"][:4]
            if rec_year != current_year_str:
                ytd_gross = ytd_net = ytd_capital = 0.0
                current_year_str = rec_year

            # Phase 8a: emit one fixed_cost_event per calendar month.
            # Use a seen-set to deduplicate across customers (multiple customers'
            # terms interleave, so naive current_month_str comparison double-counts).
            # Fixed costs flow through the ledger only — not deducted from the
            # energy trading treasury (trading vs. ops architectural separation).
            rec_month = rec["settlement_date"][:7]
            if rec_month not in _fixed_cost_emitted:
                fixed_cost_events.append(make_fixed_cost_event(rec_month, FIXED_COST_MONTHLY))
                _fixed_cost_emitted.add(rec_month)

            treasury += rec["net_margin_gbp"]
            rec["treasury_cash_balance_gbp"] = treasury
            ytd_gross += rec["margin_gbp"]
            ytd_net += rec["net_margin_gbp"]
            ytd_capital += rec["capital_cost_gbp"]
            settled_this_term.append(rec)

            total_periods_processed += 1
            if total_periods_processed % PROGRESS_EVERY_PERIODS == 0:
                print(
                    f"  ... progress: {total_periods_processed:,} settlement periods "
                    f"processed (latest: {rec['settlement_date']} period "
                    f"{rec.get('settlement_period', '-')}, treasury £{treasury:.2f})"
                )

            if is_administration_triggered(treasury) and administration_event is None:
                administration_event = {
                    "date": rec["settlement_date"],
                    "customer_id": rec["customer_id"],
                    "treasury_balance_gbp": treasury,
                    "commodity": commodity,
                }
                break

            periods_since_committee += 1
            if periods_since_committee < COMMITTEE_COOLDOWN_PERIODS:
                continue

            # Risk committee check (electricity customers only for VaR aggregation)
            active_elec = [c for c in ELEC_CUSTOMERS if c["customer_id"] in current_risk]
            if not active_elec:
                continue

            portfolio_var_current = sum(
                current_risk[c["customer_id"]]["var_current_gbp"] for c in active_elec
            )
            portfolio_var_stressed = sum(
                current_risk[c["customer_id"]]["var_stressed_gbp"] for c in active_elec
            )
            _eac = {c["customer_id"]: _company_eac_estimate(c["customer_id"], rec["settlement_date"], all_records) for c in active_elec}
            total_eac_active = sum(_eac.values())
            sigma_weighted = sum(
                current_risk[c["customer_id"]]["sigma_recent"] * _eac[c["customer_id"]] / total_eac_active
                for c in active_elec
            )

            portfolio_state = {
                "customers": [
                    {
                        "customer_id": c["customer_id"],
                        "hedge_fraction": current_hf[c["customer_id"]],
                        "eac_kwh": _eac[c["customer_id"]],
                        "active_collateral_gbp": current_risk[c["customer_id"]]["active_collateral_gbp"],
                        "monthly_cost_of_capital_gbp": current_risk[c["customer_id"]]["monthly_cost_of_capital_gbp"],
                        "var_current_gbp": current_risk[c["customer_id"]]["var_current_gbp"],
                        "var_stressed_gbp": current_risk[c["customer_id"]]["var_stressed_gbp"],
                    }
                    for c in active_elec
                ],
                "gross_margin_ytd_gbp": ytd_gross,
                "net_margin_ytd_gbp": ytd_net,
                "capital_costs_ytd_gbp": ytd_capital,
                "sigma_recent": sigma_weighted,
                "forward_price_gbp_per_mwh": forward_price if commodity == "electricity" else 0.0,
            }

            settlement_period = rec.get("settlement_period", 1)
            triggered = monitor.update(
                treasury, rec["settlement_date"], settlement_period,
                portfolio_var_current, portfolio_var_stressed,
                portfolio_state, elec_records,
            )
            if triggered:
                periods_since_committee = 0
                print(
                    f"\n  [RISK COMMITTEE] Woken at {rec['settlement_date']} — "
                    f"treasury £{treasury:.2f}"
                )
                try:
                    adjustments = risk_committee_agent.invoke(
                        rec["settlement_date"], settlement_period, dict(current_hf),
                    )
                    for adj_cid, new_hf_val in adjustments.items():
                        pending_committee_overrides[adj_cid] = new_hf_val
                        print(f"    {adj_cid}: hf override → {new_hf_val:.2f}")
                    committee_wake_ups.append({
                        "settlement_date": rec["settlement_date"],
                        "treasury_gbp": treasury,
                        "adjustments": adjustments,
                        "portfolio_var_current_gbp": portfolio_var_current,
                        "portfolio_var_stressed_gbp": portfolio_var_stressed,
                    })
                except Exception as exc:
                    print(f"    [ERROR] Committee invocation failed: {exc}")

        all_records.extend(settled_this_term)
        if administration_event:
            break

        # Evolution (use actual vs naked net margin)
        actual_net = sum(r["net_margin_gbp"] for r in settled_this_term)
        if commodity == "electricity":
            months = len({r["settlement_date"][:7] for r in settled_this_term})
            naked_capital = counterfactual_risk["monthly_cost_of_capital_gbp"] * months
            naked_gross = sum(
                r["revenue_gbp"]
                - (r["consumption_kwh"] / 1000)
                * elec_price_lookup.get((r["settlement_date"], r["settlement_period"]), 0.0)
                for r in settled_this_term
            )
            naked_net = naked_gross - naked_capital
        else:
            months = len({r["settlement_date"][:7] for r in settled_this_term})
            naked_capital = counterfactual_risk["monthly_cost_of_capital_gbp"] * months
            gas_spot_lookup = {r["settlementDate"]: r["systemSellPrice"] for r in gas_records}
            aq_kwh = get_customer(cid)["aq_kwh"]
            daily_kwh = aq_kwh / 365.0
            naked_gross = sum(
                r["revenue_gbp"]
                - (daily_kwh / 1000.0) * gas_spot_lookup.get(r["settlement_date"], 0.0)
                for r in settled_this_term
            )
            naked_net = naked_gross - naked_capital

        # Phase 16c + 17a + 19a: record term margin + revenue for all commodities
        prev_term_margin[cid] = actual_net
        term_revenue = sum(r["revenue_gbp"] for r in settled_this_term)
        prev_term_revenue[cid] = term_revenue
        # Phase 22a: trigger post-crisis hangover when electricity term suffers >20% net loss.
        # Company observes this from its own P&L — customers scarred by crisis prices stay anxious
        # even when rates improve, so churn stays elevated for 2 renewal periods.
        if commodity == "electricity" and term_revenue > 0 and actual_net / term_revenue < -CRISIS_HANGOVER_LOSS_THRESHOLD:
            from company.crm.churn_model import CRISIS_HANGOVER_WINDOW_PERIODS
            hangover_remaining[cid] = CRISIS_HANGOVER_WINDOW_PERIODS
        if term_revenue > 0:
            if commodity == "electricity":
                portfolio_elec_margin_rates.append(actual_net / term_revenue)
            else:
                portfolio_gas_margin_rates.append(actual_net / term_revenue)  # Phase 19a

        new_hf, reason = evolve_hedge_fraction(hf, naked_net, actual_net)
        next_hf[cid] = new_hf
        evolution_logs[cid].append({
            "term_index": term_index, "term_start": term_start_str,
            "commodity": commodity, "hf_used": hf, "actual_net": actual_net,
            "naked_net": naked_net, "next_hf": new_hf,
        })

        print(
            f"  {cid} ({commodity[:4]}) term {term_index:2d} ({term_start_str}→{term_end_str[:10]}): "
            f"hf={hf:.2f}→{new_hf:.2f}  "
            f"unit_rate=£{unit_rate:.2f}/MWh  "
            f"actual_net=£{actual_net:8.2f}  naked_net=£{naked_net:8.2f}"
        )

    # =================== REPORTING ===================

    if administration_event:
        print(f"\n!!! ADMINISTRATION EVENT on {administration_event['date']} !!!")
        print(f"    Customer: {administration_event['customer_id']} ({administration_event['commodity']})")
        print(f"    Treasury: £{administration_event['treasury_balance_gbp']:.4f}")
    else:
        final_t = all_records[-1]["treasury_cash_balance_gbp"] if all_records else STARTING_TREASURY_GBP
        print(f"\n=== SURVIVED full window. Final treasury: £{final_t:.2f} ===")

    yearly_records: dict[str, list] = defaultdict(list)
    for rec in all_records:
        yearly_records[rec["settlement_date"][:4]].append(rec)

    print("\n=== Portfolio P&L by calendar year (all commodities) ===")
    print(f"{'Year':<6} {'Gross £':>9} {'Cap £':>9} {'Net £':>9} {'Treasury £':>12} {'Flag':>8}")
    for year in sorted(yearly_records.keys()):
        yr = yearly_records[year]
        gross = sum(r["margin_gbp"] for r in yr)
        capital = sum(r["capital_cost_gbp"] for r in yr)
        net = sum(r["net_margin_gbp"] for r in yr)
        treas = yr[-1]["treasury_cash_balance_gbp"]
        flag = "CRISIS" if year in CRISIS_YEARS else ""
        print(f"{year:<6} {gross:>9.2f} {capital:>9.2f} {net:>9.2f} {treas:>12.2f} {flag:>8}")

    print("\n=== Commodity exposure split ===")
    for commodity in ["electricity", "gas"]:
        recs = [r for r in all_records if r.get("commodity") == commodity]
        gross = sum(r["margin_gbp"] for r in recs)
        cap = sum(r["capital_cost_gbp"] for r in recs)
        net = sum(r["net_margin_gbp"] for r in recs)
        print(f"  {commodity:12s}: gross=£{gross:.2f}  capital=£{cap:.2f}  net=£{net:.2f}")

    print("\n=== Per-customer lifetime P&L ===")
    for c in ELEC_CUSTOMERS + GAS_CUSTOMERS:
        cid = c["customer_id"]
        recs = [r for r in all_records if r["customer_id"] == cid]
        gross = sum(r["margin_gbp"] for r in recs)
        cap = sum(r["capital_cost_gbp"] for r in recs)
        net = sum(r["net_margin_gbp"] for r in recs)
        kwh = EFFECTIVE_EAC_KWH.get(cid) or c.get("aq_kwh")
        comm = c["commodity"]
        print(
            f"  {cid} ({comm[:4]}, {kwh:,.0f} kWh): "
            f"gross=£{gross:.2f}  capital=£{cap:.2f}  net=£{net:.2f}"
        )

    print(f"\n=== Customer lifecycle events: {len(customer_events_log)} ===")
    renewals_by_type: dict[str, int] = {}
    for evt in customer_events_log:
        renewals_by_type[evt["event_type"]] = renewals_by_type.get(evt["event_type"], 0) + 1
    print(f"  Renewed: {renewals_by_type.get('renewed', 0)}  Churned: {renewals_by_type.get('churned', 0)}")
    for evt in customer_events_log:
        flag = " *** CHURNED ***" if evt["event_type"] == "churned" else ""
        print(
            f"  {evt['customer_id']} {evt['event_date']}: "
            f"p_churn={evt['churn_probability']:.4f}  "
            f"p_win={evt['win_probability']:.4f}  "
            f"p_retain={evt['effective_retention_probability']:.4f}  "
            f"roll={evt['random_roll']:.4f}{flag}"
        )

    print(f"\n=== Context Handshake wake-ups: {len(committee_wake_ups)} ===")
    if committee_wake_ups:
        for wu in committee_wake_ups:
            adjs = ", ".join(f"{k}→{v:.2f}" for k, v in wu["adjustments"].items()) or "(none)"
            print(f"  {wu['settlement_date']}: treasury=£{wu['treasury_gbp']:.2f}  {adjs}")
    else:
        print("  (no wake-ups — thresholds not breached)")

    total_gross = sum(r["margin_gbp"] for r in all_records)
    total_capital = sum(r["capital_cost_gbp"] for r in all_records)
    total_net = sum(r["net_margin_gbp"] for r in all_records)
    final_treasury = all_records[-1]["treasury_cash_balance_gbp"] if all_records else STARTING_TREASURY_GBP

    # Phase 27d: Triad risk for I&C customers.
    # Identify Triad periods for each winter in the run window, then compute
    # each I&C customer's TNUoS exposure. Uses SSP as a demand proxy.
    ic_customer_ids = [
        c["customer_id"]
        for c in _ALL_KNOWN_CUSTOMERS
        if c.get("segment") == "I&C"
    ]
    triad_log: list[dict] = []
    if ic_customer_ids:
        triad_winters = set()
        for rec in elec_records:
            d = date.fromisoformat(rec["settlementDate"])
            if d.month in {11, 12, 1, 2}:
                triad_winters.add(_triad_year(rec["settlementDate"]))
        for winter_year in sorted(triad_winters):
            triad_periods = identify_triad_candidates(elec_records, winter_year)
            if not triad_periods:
                continue
            for cid in ic_customer_ids:
                cid_records = [r for r in all_records if r.get("customer_id") == cid]
                if not cid_records:
                    continue
                exposure = compute_triad_exposure(cid, triad_periods, cid_records, winter_year)
                triad_log.append(exposure)

    print("\n=== Full-window portfolio summary ===")
    print(f"Gross margin:      £{total_gross:>12.2f}")
    print(f"Capital costs:     £{total_capital:>12.2f}")
    print(f"Net margin:        £{total_net:>12.2f}")
    print(f"Starting treasury: £{STARTING_TREASURY_GBP:>12.2f}")
    print(f"Final treasury:    £{final_treasury:>12.2f}")
    print(f"Treasury change:   £{final_treasury - STARTING_TREASURY_GBP:>+12.2f}")
    print(f"Capital cost ratio: {total_capital/total_gross*100:.1f}% of gross")
    if administration_event:
        print(f"OUTCOME: ADMINISTRATION on {administration_event['date']}")
    else:
        print("OUTCOME: SURVIVED — full window completed")

    return {
        "all_records": all_records,
        "administration_event": administration_event,
        "committee_wake_ups": committee_wake_ups,
        "customer_events": customer_events_log,
        "churned_billing_accounts": sorted(churned_billing_accounts),
        "won_successor_activations": won_successor_activations,
        "hedge_evolution": evolution_logs,
        "total_gross": total_gross,
        "total_capital": total_capital,
        "total_net": total_net,
        "final_treasury": final_treasury,
        "starting_treasury": STARTING_TREASURY_GBP,
        # Phase 8a: growth mandate outputs
        "acquisition_spend_events": acquisition_spend_events,
        "fixed_cost_events": fixed_cost_events,
        "acquired_customers": [c["customer_id"] for c in ACQUIRED_CUSTOMERS],
        "growth_mandate": MANDATE,
        # Phase 11a: basis risk — company estimate vs sim ground truth per term
        "basis_risk_terms": basis_risk_terms,
        # Phase 11b: churn basis risk — company churn estimate vs sim ground truth per renewal
        # Phase 39a: extended with SVT comparison fields
        "churn_basis_risk": _build_churn_basis_risk(customer_events_log),
        # Phase 12a: company CRM event log — dated artefacts of churn and acquisition
        "company_event_log": _build_company_event_log(
            customer_events_log, won_successor_activations, fresh_acquisitions, SUCCESSOR_MAP
        ),
        "retention_log": retention_log,
        "retention_cost_events": retention_cost_events,
        "no_offer_churn_log": no_offer_churn_log,
        "company_gas_churn_log": company_gas_churn_log,
        "volume_tolerance_log": volume_tolerance_log,
        "triad_log": triad_log,
        "margin_feedback_log": margin_feedback_log,
        "dynamic_pricing_log": dynamic_pricing_log,
        # Phase 12e: aggregated company-model divergence by year
        "company_divergence": _compute_company_divergence(
            basis_risk_terms,
            [
                {
                    "term_start": e["event_date"],
                    "churn_estimate_error_pct": e["churn_estimate_error_pct"],
                }
                for e in customer_events_log
                if e.get("company_churn_estimate") is not None
            ],
            demand_estimation_log=demand_estimation_log,  # Phase 23a
        ),
        "demand_estimation_log": demand_estimation_log,  # Phase 23a: full log for report
    }


if __name__ == "__main__":
    main()
