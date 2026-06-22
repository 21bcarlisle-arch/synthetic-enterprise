"""Phase 10a — Segment customer model simulation.

Replaces run_phase2b.py's 9 named individual customers with 5 population
segments (resi_standard, resi_smart, sme_standard, sme_smart, gas_resi).

Key differences from run_phase2b:
  - Volume = headcount × avg_kwh_per_customer × profile-class shape scale
  - Headcount evolves annually: churn, smart-meter upgrades, acquisition
  - Unit rate re-priced at each annual renewal using current headcount EAC
  - No successor/home-mover mechanics — headcount handles attrition organically
  - Risk committee and hedge evolution unchanged (same physics, bigger book)
"""

import statistics
from collections import defaultdict
from datetime import date, timedelta

import sim.risk_committee_agent as risk_committee_agent
from saas.growth_mandate import FIXED_COST_MONTHLY, MANDATE
from saas.ledger import make_fixed_cost_event
from saas.property_model import DEFAULT_ASSETS, DEFAULT_HEATING_SYSTEM, DEFAULT_OCCUPANCY_PATTERN
from saas.tariff_pricing import price_fixed_tariff
from sim.cache_store import get_cached_prices, log_cache_access
from sim.forward_curve import (
    BASE_TERM_PREMIUM,
    DEFAULT_RISK_FACTOR,
    EWMA_HALF_LIFE_DAYS,
    SUMMER_MULTIPLIER,
    WINTER_MONTHS,
    WINTER_MULTIPLIER,
    _ewma,
    _seasonal_shape,
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
from simulation.segments import (
    ELEC_SEGMENTS,
    GAS_SEGMENTS,
    SEGMENT_BY_ID,
    SEGMENTS,
    CustomerSegment,
    apply_annual_headcount_changes,
)
from simulation.settlement import CONTRACT_LENGTH_DAYS
from simulation.weather_inputs import lookback_mean_temps, weather_means_for_customer

REPORT_START = "2016-01-01"
REPORT_END = "2025-06-07"
CRISIS_YEARS = {"2021", "2022"}
EARLIEST_SSP_DATE = "2015-11-07"
COMMITTEE_COOLDOWN_PERIODS = 1440
PROGRESS_EVERY_PERIODS = 500
GAS_ELEC_WEIGHT = 0.25
ORIGINAL_SCALE_EAC_KWH = 15_000  # treasury sizing reference (same as run_phase2b)
RESET_HEDGE_FRACTION = MIN_HEDGE_FLOOR

SHAPE_LOADERS = {1: load_pc1_shape, 3: load_pc3_shape}

DEFAULT_PROPERTY = {
    "heating_system": DEFAULT_HEATING_SYSTEM,
    "occupancy_pattern": DEFAULT_OCCUPANCY_PATTERN,
    "assets": dict(DEFAULT_ASSETS),
}


def _clamp_term_end(term_start: str, end_date: str = REPORT_END) -> str:
    natural = (date.fromisoformat(term_start) + timedelta(days=CONTRACT_LENGTH_DAYS)).isoformat()
    if natural > end_date:
        return (date.fromisoformat(end_date) + timedelta(days=1)).isoformat()
    return natural


def _bootstrap_gas_price(
    term_start: str,
    gas_records: list[dict],
    lookback_days: int = 90,
    risk_factor: float = 1.2,
    lookback_daily_mean_temps_c: list[float] | None = None,
) -> float:
    """Bootstrap forward gas price when no prior history exists (first term only)."""
    start_date = date.fromisoformat(term_start)
    window_end = start_date + timedelta(days=lookback_days - 1)
    filtered = [
        r for r in gas_records
        if start_date <= date.fromisoformat(r["settlementDate"]) <= window_end
    ]
    daily_buckets: dict[str, list[float]] = {}
    for r in filtered:
        daily_buckets.setdefault(r["settlementDate"], []).append(r["systemSellPrice"])
    daily_means = [statistics.mean(v) for _, v in sorted(daily_buckets.items())]
    effective_hl = min(EWMA_HALF_LIFE_DAYS, len(daily_means)) if daily_means else 1
    spot_ewma = _ewma(daily_means, effective_hl) if daily_means else 0.0
    seasonal = _seasonal_shape(start_date.month, 12)
    tenor_years = 12 / 12.0
    term_premium = BASE_TERM_PREMIUM * (tenor_years ** 0.5) * (risk_factor / DEFAULT_RISK_FACTOR)
    fwd = spot_ewma * seasonal * (1.0 + term_premium)
    if lookback_daily_mean_temps_c:
        fwd *= weather_sensitivity_multiplier(lookback_daily_mean_temps_c)
    return fwd


def _segment_shape_fn(
    seg: CustomerSegment,
    headcount: int,
    weather_means: dict[str, float],
) -> callable:
    """Return a shape function for a segment: base PC shape × headcount × scale."""
    base_loader = SHAPE_LOADERS[seg.profile_class]
    scale = seg.shape_scale  # calibrates per-customer PC kWh to avg_kwh_per_customer

    def shape_fn(date_str: str) -> list[float]:
        base = base_loader(date_str)
        mean_temp = weather_means.get(date_str)
        if mean_temp is not None:
            base = build_demand_shape(base, mean_temp, "electricity", DEFAULT_PROPERTY)
        return [v * scale * headcount for v in base]

    return shape_fn


def _build_elec_term_data(
    seg: CustomerSegment,
    term_start: str,
    effective_end: str,
    elec_records: list[dict],
    headcount: int,
    lookback_temps: list[float] | None,
) -> dict | None:
    """Build one electricity term for a segment. Returns None if beyond simulation window."""
    if term_start > effective_end:
        return None
    term_end = _clamp_term_end(term_start, effective_end)
    current_eac = headcount * seg.avg_kwh_per_customer
    try:
        fwd = generate_forward_price(
            term_start, elec_records, lookback_daily_mean_temps_c=lookback_temps
        )
    except ValueError:
        return None  # no forward price — skip this term
    unit_rate = price_fixed_tariff(
        fwd, current_eac, term_start, naked_fraction=1 - MIN_HEDGE_FLOOR
    )
    return {
        "term_start": term_start,
        "term_end": term_end,
        "forward_price_gbp_per_mwh": fwd,
        "unit_rate_gbp_per_mwh": unit_rate,
        "eac_kwh": current_eac,
    }


def _build_gas_term_data(
    seg: CustomerSegment,
    term_start: str,
    effective_end: str,
    gas_records: list[dict],
    headcount: int,
    lookback_temps: list[float] | None,
) -> dict | None:
    """Build one gas term for a segment. Returns None if beyond simulation window."""
    if term_start > effective_end:
        return None
    term_end = _clamp_term_end(term_start, effective_end)
    current_aq = int(headcount * seg.avg_kwh_per_customer)
    try:
        fwd = generate_forward_price(
            term_start, gas_records, lookback_daily_mean_temps_c=lookback_temps
        )
    except ValueError:
        if term_start == seg.acquisition_date:
            fwd = _bootstrap_gas_price(term_start, gas_records, lookback_daily_mean_temps_c=lookback_temps)
        else:
            return None
    unit_rate = price_fixed_tariff(
        fwd, current_aq, term_start, naked_fraction=1 - MIN_HEDGE_FLOOR
    )
    return {
        "term_start": term_start,
        "term_end": term_end,
        "forward_price_gbp_per_mwh": fwd,
        "unit_rate_gbp_per_mwh": unit_rate,
        "aq_kwh": current_aq,
    }


def main(report_end: str | None = None) -> dict:
    """Run the Phase 10a segment simulation.

    Returns the same dict schema as run_phase2b.main() for compatibility
    with annual_report.py (plus segment-specific keys).
    """
    effective_end = report_end or REPORT_END

    print("=== Phase 10a — Segment Customer Model ===")
    initial_headcounts = {s.segment_id: s.headcount for s in SEGMENTS}
    total_initial_elec = sum(
        s.avg_kwh_per_customer * s.headcount for s in ELEC_SEGMENTS
    )
    total_initial_gas = sum(
        s.avg_kwh_per_customer * s.headcount for s in GAS_SEGMENTS
    )
    effective_eac = total_initial_elec + total_initial_gas * GAS_ELEC_WEIGHT
    starting_treasury = 3_250.0 * (effective_eac / ORIGINAL_SCALE_EAC_KWH)
    print(f"Segments:        {[s.segment_id for s in SEGMENTS]}")
    print(f"Total elec EAC:  {total_initial_elec:,.0f} kWh")
    print(f"Total gas AQ:    {total_initial_gas:,.0f} kWh")
    print(f"Starting treasury: £{starting_treasury:,.2f}")
    print()

    # ---- Load price feeds ----
    fetch_start = max(
        (date.fromisoformat(REPORT_START) - timedelta(days=365)).isoformat(),
        EARLIEST_SSP_DATE,
    )
    cached = get_cached_prices(fetch_start, effective_end)
    if cached is not None:
        elec_records = cached
        print(f"Cache hit: {len(elec_records):,} SSP records.")
        log_cache_access("elexon_ssp_full.json", hit=True, phase="10a")
    else:
        elec_records = get_system_prices_range(fetch_start, effective_end)
        log_cache_access("elexon_ssp_full.json", hit=False, phase="10a")
    print(f"Electricity: {len(elec_records):,} SSP records ({fetch_start} to {effective_end}).")

    gas_records = load_nbp_history()
    print(f"Gas: {len(gas_records):,} NBP daily records.\n")

    elec_price_lookup = {
        (r["settlementDate"], r["settlementPeriod"]): r["systemSellPrice"]
        for r in elec_records
    }
    gas_spot_lookup = {r["settlementDate"]: r["systemSellPrice"] for r in gas_records}

    # ---- Weather means per segment (representative location) ----
    weather_by_segment = {
        seg.segment_id: weather_means_for_customer(seg.as_weather_customer())
        for seg in SEGMENTS
        if seg.commodity == "electricity"
    }

    def _lookback_temps_fn(sid: str, commodity: str = "electricity"):
        if commodity != "electricity":
            return lambda term_start: None
        weather_means = weather_by_segment.get(sid, {})
        return lambda term_start: lookback_mean_temps(weather_means, term_start)

    # ---- Simulation state ----
    treasury = starting_treasury
    monitor = RiskCommitteeMonitor(treasury)
    headcounts: dict[str, int] = dict(initial_headcounts)
    next_hf: dict[str, float] = {s.segment_id: RESET_HEDGE_FRACTION for s in SEGMENTS}
    pending_committee_overrides: dict[str, float] = {}
    current_hf: dict[str, float] = {s.segment_id: RESET_HEDGE_FRACTION for s in SEGMENTS}
    current_risk: dict[str, dict] = {}
    term_indices: dict[str, int] = {s.segment_id: 0 for s in SEGMENTS}
    evolution_logs: dict[str, list] = {s.segment_id: [] for s in SEGMENTS}

    all_records: list[dict] = []
    committee_wake_ups: list[dict] = []
    fixed_cost_events: list[dict] = []
    headcount_history: list[dict] = []  # snapshot headcounts at each year
    administration_event = None
    periods_since_committee = COMMITTEE_COOLDOWN_PERIODS
    total_periods_processed = 0
    _fixed_cost_emitted: set[str] = set()

    current_year_str = REPORT_START[:4]
    ytd_gross = ytd_net = ytd_capital = 0.0

    # ---- Build initial terms for all segments ----
    # Terms are built dynamically: at each term_start, compute term using current headcount.
    # Pre-compute all term_start dates for each segment (annual, from acquisition_date).
    def _term_starts(seg: CustomerSegment) -> list[str]:
        starts = []
        ts = seg.acquisition_date
        while ts <= effective_end:
            starts.append(ts)
            ts = _clamp_term_end(ts, effective_end)
        return starts

    # Build ordered list of (term_start, segment_id, commodity) entries
    all_term_keys: list[tuple[str, str, str]] = []
    for seg in SEGMENTS:
        for ts in _term_starts(seg):
            all_term_keys.append((ts, seg.segment_id, seg.commodity))
    all_term_keys.sort(key=lambda x: (x[0], x[1]))

    # Track which year headcounts were last updated (so we update once per year boundary)
    last_headcount_update_year: str = REPORT_START[:4]
    headcount_history.append({
        "year": REPORT_START[:4],
        "headcounts": dict(headcounts),
    })

    print("=== Processing segment terms chronologically ===\n")

    for term_start_str, sid, commodity in all_term_keys:
        if administration_event:
            break

        seg = SEGMENT_BY_ID[sid]
        term_year = term_start_str[:4]
        term_index = term_indices[sid]
        term_indices[sid] += 1

        # Apply annual headcount changes at the start of each new year
        if term_year > last_headcount_update_year and term_index >= 1:
            headcounts = apply_annual_headcount_changes(headcounts, last_headcount_update_year)
            last_headcount_update_year = term_year
            headcount_history.append({"year": term_year, "headcounts": dict(headcounts)})
            print(
                f"  [HEADCOUNT] Year {term_year}: "
                + "  ".join(f"{k}={v}" for k, v in headcounts.items())
            )

        headcount = headcounts[sid]
        if headcount <= 0:
            continue

        hf = pending_committee_overrides.pop(sid, next_hf[sid])
        current_hf[sid] = hf

        if commodity == "electricity":
            term_data = _build_elec_term_data(
                seg, term_start_str, effective_end, elec_records, headcount,
                _lookback_temps_fn(sid)(term_start_str),
            )
            if term_data is None:
                continue
            term_end_str = term_data["term_end"]
            forward_price = term_data["forward_price_gbp_per_mwh"]
            unit_rate = term_data["unit_rate_gbp_per_mwh"]
            current_eac = term_data["eac_kwh"]

            naked_kwh = current_eac * (1.0 - hf)
            risk = assess_term_risk(term_start_str, naked_kwh, forward_price, elec_records)
            counterfactual_risk = assess_term_risk(
                term_start_str, float(current_eac), forward_price, elec_records
            )
            current_risk[sid] = risk

            shape_fn = _segment_shape_fn(seg, headcount, weather_by_segment.get(sid, {}))
            term_records = run_hedged_term(
                sid, term_start_str, term_end_str,
                unit_rate, forward_price, hf,
                risk["monthly_cost_of_capital_gbp"],
                shape_fn, elec_records,
            )
            for rec in term_records:
                rec["data_regime"] = "historical"
                rec["commodity"] = "electricity"
                rec["segment_headcount"] = headcount

        else:  # gas
            term_data = _build_gas_term_data(
                seg, term_start_str, effective_end, gas_records, headcount,
                _lookback_temps_fn(sid, "gas")(term_start_str),
            )
            if term_data is None:
                continue
            term_end_str = term_data["term_end"]
            forward_price = term_data["forward_price_gbp_per_mwh"]
            unit_rate = term_data["unit_rate_gbp_per_mwh"]
            current_aq = term_data["aq_kwh"]

            naked_kwh = current_aq * (1.0 - hf)
            risk = assess_term_risk(term_start_str, naked_kwh, forward_price, gas_records)
            counterfactual_risk = assess_term_risk(
                term_start_str, float(current_aq), forward_price, gas_records
            )
            current_risk[sid] = risk

            term_records = run_gas_term(
                sid, term_start_str, term_end_str, current_aq,
                unit_rate, hf, forward_price,
                risk["monthly_cost_of_capital_gbp"], gas_records,
            )
            for rec in term_records:
                rec["data_regime"] = "historical"
                rec["segment_headcount"] = headcount

        settled_this_term: list[dict] = []
        for rec in term_records:
            rec_year = rec["settlement_date"][:4]
            if rec_year != current_year_str:
                ytd_gross = ytd_net = ytd_capital = 0.0
                current_year_str = rec_year

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
                    f"  ... {total_periods_processed:,} periods "
                    f"(latest: {rec['settlement_date']}, treasury £{treasury:,.2f})"
                )

            if is_administration_triggered(treasury) and administration_event is None:
                administration_event = {
                    "date": rec["settlement_date"],
                    "segment_id": rec["customer_id"],
                    "treasury_balance_gbp": treasury,
                    "commodity": commodity,
                }
                break

            periods_since_committee += 1
            if periods_since_committee < COMMITTEE_COOLDOWN_PERIODS:
                continue

            # Risk committee — electricity segments only
            active_elec_sids = [s.segment_id for s in ELEC_SEGMENTS if s.segment_id in current_risk]
            if not active_elec_sids:
                continue

            portfolio_var_current = sum(current_risk[s]["var_current_gbp"] for s in active_elec_sids)
            portfolio_var_stressed = sum(current_risk[s]["var_stressed_gbp"] for s in active_elec_sids)
            total_eac_active = sum(
                headcounts[s] * SEGMENT_BY_ID[s].avg_kwh_per_customer for s in active_elec_sids
            )
            sigma_weighted = sum(
                current_risk[s]["sigma_recent"]
                * headcounts[s] * SEGMENT_BY_ID[s].avg_kwh_per_customer
                / total_eac_active
                for s in active_elec_sids
            )

            portfolio_state = {
                "customers": [
                    {
                        "customer_id": s,
                        "hedge_fraction": current_hf[s],
                        "eac_kwh": headcounts[s] * SEGMENT_BY_ID[s].avg_kwh_per_customer,
                        "active_collateral_gbp": current_risk[s]["active_collateral_gbp"],
                        "monthly_cost_of_capital_gbp": current_risk[s]["monthly_cost_of_capital_gbp"],
                        "var_current_gbp": current_risk[s]["var_current_gbp"],
                        "var_stressed_gbp": current_risk[s]["var_stressed_gbp"],
                    }
                    for s in active_elec_sids
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
                    f"treasury £{treasury:,.2f}"
                )
                try:
                    adjustments = risk_committee_agent.invoke(
                        rec["settlement_date"], settlement_period, dict(current_hf),
                    )
                    for adj_sid, new_hf_val in adjustments.items():
                        pending_committee_overrides[adj_sid] = new_hf_val
                        print(f"    {adj_sid}: hf override → {new_hf_val:.2f}")
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

        # Hedge fraction evolution
        actual_net = sum(r["net_margin_gbp"] for r in settled_this_term)
        if commodity == "electricity":
            months = len({r["settlement_date"][:7] for r in settled_this_term})
            naked_capital = counterfactual_risk["monthly_cost_of_capital_gbp"] * months
            naked_gross = sum(
                r["revenue_gbp"]
                - (r["consumption_kwh"] / 1000)
                * elec_price_lookup.get((r["settlement_date"], r.get("settlement_period", 1)), 0.0)
                for r in settled_this_term
            )
            naked_net = naked_gross - naked_capital
        else:
            months = len({r["settlement_date"][:7] for r in settled_this_term})
            naked_capital = counterfactual_risk["monthly_cost_of_capital_gbp"] * months
            daily_kwh = current_aq / 365.0
            naked_gross = sum(
                r["revenue_gbp"]
                - (daily_kwh / 1000.0) * gas_spot_lookup.get(r["settlement_date"], 0.0)
                for r in settled_this_term
            )
            naked_net = naked_gross - naked_capital

        new_hf, reason = evolve_hedge_fraction(hf, naked_net, actual_net)
        next_hf[sid] = new_hf
        evolution_logs[sid].append({
            "term_index": term_index,
            "term_start": term_start_str,
            "commodity": commodity,
            "hf_used": hf,
            "actual_net": actual_net,
            "naked_net": naked_net,
            "next_hf": new_hf,
            "headcount": headcount,
        })

        print(
            f"  {sid} ({commodity[:4]}) term {term_index:2d} ({term_start_str}→{term_end_str[:10]}): "
            f"hc={headcount}  hf={hf:.2f}→{new_hf:.2f}  "
            f"unit_rate=£{unit_rate:.2f}/MWh  "
            f"actual_net=£{actual_net:8.2f}  naked_net=£{naked_net:8.2f}"
        )

    # =================== REPORTING ===================

    if administration_event:
        print(f"\n!!! ADMINISTRATION EVENT on {administration_event['date']} !!!")
        print(f"    Segment: {administration_event['segment_id']} ({administration_event['commodity']})")
        print(f"    Treasury: £{administration_event['treasury_balance_gbp']:.4f}")
    else:
        final_t = all_records[-1]["treasury_cash_balance_gbp"] if all_records else starting_treasury
        print(f"\n=== SURVIVED full window. Final treasury: £{final_t:,.2f} ===")

    yearly_records: dict[str, list] = defaultdict(list)
    for rec in all_records:
        yearly_records[rec["settlement_date"][:4]].append(rec)

    print("\n=== Portfolio P&L by calendar year ===")
    print(f"{'Year':<6} {'Gross £':>12} {'Cap £':>10} {'Net £':>10} {'Treasury £':>14} {'Flag':>8}")
    for year in sorted(yearly_records.keys()):
        yr = yearly_records[year]
        gross = sum(r["margin_gbp"] for r in yr)
        capital = sum(r["capital_cost_gbp"] for r in yr)
        net = sum(r["net_margin_gbp"] for r in yr)
        treas = yr[-1]["treasury_cash_balance_gbp"]
        flag = "CRISIS" if year in CRISIS_YEARS else ""
        print(f"{year:<6} {gross:>12.2f} {capital:>10.2f} {net:>10.2f} {treas:>14.2f} {flag:>8}")

    print("\n=== Per-segment lifetime P&L ===")
    for seg in SEGMENTS:
        sid = seg.segment_id
        recs = [r for r in all_records if r["customer_id"] == sid]
        if not recs:
            continue
        gross = sum(r["margin_gbp"] for r in recs)
        cap = sum(r["capital_cost_gbp"] for r in recs)
        net = sum(r["net_margin_gbp"] for r in recs)
        final_hc = headcounts[sid]
        print(
            f"  {sid} ({seg.commodity[:4]}, initial hc={seg.headcount}, final hc={final_hc}): "
            f"gross=£{gross:,.2f}  cap=£{cap:,.2f}  net=£{net:,.2f}"
        )

    print("\n=== Headcount history ===")
    for snapshot in headcount_history:
        print(f"  {snapshot['year']}: " + "  ".join(
            f"{k}={v}" for k, v in snapshot["headcounts"].items()
        ))

    print(f"\n=== Context Handshake wake-ups: {len(committee_wake_ups)} ===")

    total_gross = sum(r["margin_gbp"] for r in all_records)
    total_capital = sum(r["capital_cost_gbp"] for r in all_records)
    total_net = sum(r["net_margin_gbp"] for r in all_records)
    final_treasury = all_records[-1]["treasury_cash_balance_gbp"] if all_records else starting_treasury

    print("\n=== Full-window portfolio summary ===")
    print(f"Gross margin:      £{total_gross:>14,.2f}")
    print(f"Capital costs:     £{total_capital:>14,.2f}")
    print(f"Net margin:        £{total_net:>14,.2f}")
    print(f"Starting treasury: £{starting_treasury:>14,.2f}")
    print(f"Final treasury:    £{final_treasury:>14,.2f}")
    print(f"Treasury change:   £{final_treasury - starting_treasury:>+14,.2f}")
    if total_gross > 0:
        print(f"Capital cost ratio: {total_capital / total_gross * 100:.1f}% of gross")
    print("OUTCOME:", "ADMINISTRATION" if administration_event else "SURVIVED — full window completed")

    return {
        "all_records": all_records,
        "administration_event": administration_event,
        "committee_wake_ups": committee_wake_ups,
        "fixed_cost_events": fixed_cost_events,
        "hedge_evolution": evolution_logs,
        "total_gross": total_gross,
        "total_capital": total_capital,
        "total_net": total_net,
        "final_treasury": final_treasury,
        "starting_treasury": starting_treasury,
        "headcount_history": headcount_history,
        "final_headcounts": dict(headcounts),
        "growth_mandate": MANDATE,
        # Compatibility with annual_report.py schema
        "customer_events": [],
        "churned_billing_accounts": [],
        "won_successor_activations": {},
        "acquired_customers": [],
        "acquisition_spend_events": [],
    }


if __name__ == "__main__":
    main()
