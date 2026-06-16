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
from saas.customers import CUSTOMERS, get_customer
from saas.property_model import (
    DEFAULT_ASSETS,
    DEFAULT_HEATING_SYSTEM,
    DEFAULT_OCCUPANCY_PATTERN,
    build_properties,
)
from saas.tariff_pricing import price_fixed_tariff
from sim.cache_store import get_cached_prices, log_cache_access
from sim.forward_curve import (
    SUMMER_MULTIPLIER,
    WINTER_MONTHS,
    WINTER_MULTIPLIER,
    generate_forward_price,
)
from sim.gas_prices_history import load_nbp_history
from sim.hedging_strategy import MIN_HEDGE_FLOOR, evolve_hedge_fraction
from sim.profile_class_1 import load_pc1_shape
from sim.profile_class_3 import load_pc3_shape
from sim.risk_committee import RiskCommitteeMonitor
from sim.risk_engine import assess_term_risk, is_administration_triggered
from sim.system_prices_history import get_system_prices_range
from sim.weather_price_sensitivity import weather_sensitivity_multiplier
from simulation.demand_model import build_demand_shape
from simulation.gas_settlement import run_gas_term
from simulation.hedged_settlement import run_hedged_term
from simulation.hh_consumption import (
    estimate_annual_kwh,
    hh_shape_fn,
    is_hh_customer,
    load_hh_consumption,
)
from simulation.renewals import build_renewal_schedule
from simulation.settlement import CONTRACT_LENGTH_DAYS
from simulation.weather_inputs import lookback_mean_temps, weather_means_for_customer

REPORT_START = "2016-01-01"
REPORT_END = "2025-06-07"
CRISIS_YEARS = {"2021", "2022"}

# Treasury scaled by total EAC across all commodities
# Base: £3,250 per 15,000 kWh of electricity EAC
ELEC_CUSTOMERS = [c for c in CUSTOMERS if c["commodity"] == "electricity"]
GAS_CUSTOMERS = [c for c in CUSTOMERS if c["commodity"] == "gas"]
ORIGINAL_4_CUSTOMER_EAC_KWH = 15_000

# Phase 6a: HH (smart meter) customers have eac_kwh=None — their effective
# EAC for hedging-volume sizing and treasury scaling is derived from real
# half-hourly consumption data (simulation/hh_consumption.py) instead.
EFFECTIVE_EAC_KWH: dict[str, float] = {
    c["customer_id"]: c["eac_kwh"] if c["eac_kwh"] is not None
    else estimate_annual_kwh(load_hh_consumption(c["customer_id"]))
    for c in ELEC_CUSTOMERS
}

TOTAL_ELEC_EAC = sum(EFFECTIVE_EAC_KWH.values())
TOTAL_GAS_AQ = sum(c["aq_kwh"] for c in GAS_CUSTOMERS)
# Gas is priced ~10x cheaper per MWh than electricity; weight accordingly
# Treat 1 kWh gas ≈ 0.25 kWh electricity for treasury sizing (conservative)
GAS_ELEC_WEIGHT = 0.25
EFFECTIVE_EAC = TOTAL_ELEC_EAC + TOTAL_GAS_AQ * GAS_ELEC_WEIGHT
STARTING_TREASURY_GBP = 3250.0 * (EFFECTIVE_EAC / ORIGINAL_4_CUSTOMER_EAC_KWH)

# Phase 5c minimum hedge mandate: every term starts at the mandate floor
# (sim.hedging_strategy.MIN_HEDGE_FLOOR), not a neutral 50/50 guess.
RESET_HEDGE_FRACTION = MIN_HEDGE_FLOOR
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


def _weather_adjusted_shape_fn(base_shape_fn, weather_means: dict[str, float], property_record: dict):
    """Wrap a SHAPE_LOADERS[...] base-shape function with 4c-2's
    weather/occupancy/asset demand adjustment (`build_demand_shape`).

    Falls back to the unadjusted base shape on dates with no weather data
    (e.g. outside sim/weather_data's 2016-01-01..2025-06-07 coverage)."""

    def shape_fn(date_str):
        base_shape = base_shape_fn(date_str)
        mean_temp = weather_means.get(date_str)
        if mean_temp is None:
            return base_shape
        return build_demand_shape(base_shape, mean_temp, "electricity", property_record)

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
    """
    aq_kwh = customer["aq_kwh"]
    acq_date = customer["acquisition_date"]
    schedule = []
    term_start = acq_date

    while term_start <= report_end:
        term_end = _clamp_term_end(term_start, end_date=report_end)
        lookback_temps = lookback_temps_fn(term_start) if lookback_temps_fn else None
        try:
            fwd = generate_forward_price(term_start, gas_records, lookback_daily_mean_temps_c=lookback_temps)
        except ValueError:
            if not schedule:
                fwd = _bootstrap_first_term_forward_price(
                    term_start, gas_records, lookback_daily_mean_temps_c=lookback_temps
                )
            else:
                break
        unit_rate = price_fixed_tariff(fwd, aq_kwh, term_start, naked_fraction=1 - MIN_HEDGE_FLOOR)
        schedule.append({
            "acquisition_date": term_start,
            "term_end": term_end,
            "forward_price_gbp_per_mwh": fwd,
            "unit_rate_gbp_per_mwh": unit_rate,
        })
        term_start = term_end  # next term starts where this ends

    return schedule


def main(report_end: str | None = None):
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
        c["customer_id"]: weather_means_for_customer(c) for c in ELEC_CUSTOMERS + GAS_CUSTOMERS
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
            elec_records, EFFECTIVE_EAC_KWH[c["customer_id"]], lookback_temps_fn=_lookback_temps_fn(c["customer_id"]),
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
    )
    next_hf = {cid: RESET_HEDGE_FRACTION for cid in all_customers_ids}
    pending_committee_overrides: dict[str, float] = {}
    current_risk: dict[str, dict] = {}
    current_hf: dict[str, float] = {cid: RESET_HEDGE_FRACTION for cid in all_customers_ids}

    all_records: list[dict] = []
    evolution_logs: dict[str, list] = {cid: [] for cid in all_customers_ids}
    term_indices: dict[str, int] = {cid: 0 for cid in all_customers_ids}
    committee_wake_ups: list[dict] = []
    administration_event = None
    periods_since_committee = COMMITTEE_COOLDOWN_PERIODS
    total_periods_processed = 0
    PROGRESS_EVERY_PERIODS = 100

    current_year_str = REPORT_START[:4]
    ytd_gross = ytd_net = ytd_capital = 0.0

    print("=== Processing terms chronologically ===\n")

    for term_start_str, cid, commodity, term in all_terms:
        if administration_event:
            break

        term_end_str = term.get("term_end") or _clamp_term_end(term_start_str, end_date=effective_end)
        forward_price = term["forward_price_gbp_per_mwh"]
        unit_rate = term["unit_rate_gbp_per_mwh"]
        term_index = term_indices[cid]
        term_indices[cid] += 1

        if cid in pending_committee_overrides:
            hf = pending_committee_overrides.pop(cid)
        else:
            hf = next_hf[cid]
        current_hf[cid] = hf

        if commodity == "electricity":
            customer = get_customer(cid)
            eac_kwh = EFFECTIVE_EAC_KWH[cid]
            if is_hh_customer(customer):
                shape_fn = hh_shape_fn(hh_consumption_by_customer[cid])
            else:
                profile_class = customer.get("profile_class", 1)
                property_record = properties.get(cid, DEFAULT_PROPERTY)
                shape_fn = _weather_adjusted_shape_fn(
                    SHAPE_LOADERS[profile_class], weather_by_customer[cid], property_record
                )

            naked_kwh = eac_kwh * (1.0 - hf)
            risk = assess_term_risk(term_start_str, naked_kwh, forward_price, elec_records)
            counterfactual_risk = assess_term_risk(term_start_str, float(eac_kwh), forward_price, elec_records)
            current_risk[cid] = risk

            term_records = run_hedged_term(
                cid, term_start_str, term_end_str, unit_rate, forward_price, hf,
                risk["monthly_cost_of_capital_gbp"], shape_fn, elec_records,
            )
            for rec in term_records:
                rec["data_regime"] = "historical"
                rec["commodity"] = "electricity"

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
            )
            for rec in term_records:
                rec["data_regime"] = "historical"

        settled_this_term: list[dict] = []
        for rec in term_records:
            rec_year = rec["settlement_date"][:4]
            if rec_year != current_year_str:
                ytd_gross = ytd_net = ytd_capital = 0.0
                current_year_str = rec_year

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
            total_eac_active = sum(EFFECTIVE_EAC_KWH[c["customer_id"]] for c in active_elec)
            sigma_weighted = sum(
                current_risk[c["customer_id"]]["sigma_recent"] * EFFECTIVE_EAC_KWH[c["customer_id"]] / total_eac_active
                for c in active_elec
            )

            portfolio_state = {
                "customers": [
                    {
                        "customer_id": c["customer_id"],
                        "hedge_fraction": current_hf[c["customer_id"]],
                        "eac_kwh": EFFECTIVE_EAC_KWH[c["customer_id"]],
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
        "hedge_evolution": evolution_logs,
        "total_gross": total_gross,
        "total_capital": total_capital,
        "total_net": total_net,
        "final_treasury": final_treasury,
        "starting_treasury": STARTING_TREASURY_GBP,
    }


if __name__ == "__main__":
    main()
