"""Phase 2a: Six-customer portfolio with SME segment and Context Handshake.

SUPERSEDED by simulation/run_phase2a_repriced.py (activity-based pricing +
recalibrated risk committee). Preserved as a historical artefact only — do
not run as part of the live pipeline. As of the Phase 2b gas dual-fuel WIP,
this script is also broken (`saas.customers.CUSTOMERS` now includes gas
records without `eac_kwh`, and this script iterates CUSTOMERS unfiltered
unlike the repriced version's electricity-only filter).

Two new things vs Phase 1e:

  1. SME customers C5 (25,000 kWh, PC3, London small office) and C6
     (45,000 kWh, PC3, Manchester warehouse) join the portfolio from
     2016-01-01 and 2016-04-01 respectively. Profile Class 3 (non-domestic
     unrestricted) replaces PC1 for these customers — same settlement
     mechanics, different half-hourly shape loaded from
     sim/data/profile_class_3_gad.csv.

  2. Context Handshake: the risk committee agent wakes and adjusts
     hedge_fractions when either hard threshold is breached:
       - Treasury drawdown > 10% from rolling 12-month peak
       - VaR_current > VaR_stressed × 1.20
     The wake-up sets a pending hedge_fraction override for the flagged
     customer(s), applied at their NEXT term start. The evolution rule
     continues to run at every term boundary independently; the committee's
     override takes priority at the term start where it lands.

Architecture change vs Phase 1e:
  Phase 1e generated all customer books independently (per-customer, term-
  by-term) then merged into a chronological treasury walk. Phase 2a must
  interleave term processing in true chronological order so the Context
  Handshake can fire mid-term and set a pending hedge_fraction override for
  ANY customer's next term start — not just the one whose records are
  currently being walked. Each term is settled and walked to exhaustion
  before the next chronological term starts.

Starting treasury:
  Scaled from Phase 1e's £3,250 by the ratio of new total portfolio EAC to
  the original four-customer EAC: £3,250 × (85,000 / 15,000) = £18,416.67.
"""

from collections import defaultdict
from datetime import date, timedelta

import sim.risk_committee_agent as risk_committee_agent
from saas.customers import CUSTOMERS, get_customer
from sim.cache_store import get_cached_prices, log_cache_access
from sim.hedging_strategy import evolve_hedge_fraction
from sim.profile_class_1 import load_pc1_shape
from sim.profile_class_3 import load_pc3_shape
from sim.risk_committee import RiskCommitteeMonitor
from sim.risk_engine import assess_term_risk, is_administration_triggered
from sim.system_prices_history import get_system_prices_range
from simulation.hedged_settlement import run_hedged_term
from simulation.portfolio_pnl import build_portfolio_pnl
from simulation.renewals import build_renewal_schedule
from simulation.settlement import CONTRACT_LENGTH_DAYS

REPORT_START = "2016-01-01"
REPORT_END = "2025-06-07"
CRISIS_YEARS = {"2021", "2022"}

ORIGINAL_4_CUSTOMER_EAC_KWH = 15_000   # C1+C2+C3+C4 EAC from Phase 1e
STARTING_TREASURY_GBP = 3250.0 * (sum(c["eac_kwh"] for c in CUSTOMERS) / ORIGINAL_4_CUSTOMER_EAC_KWH)

RESET_HEDGE_FRACTION = 0.50
EARLIEST_SSP_DATE = "2015-11-07"

# After a committee wake-up, do not fire again for ~30 days of half-hourly periods
COMMITTEE_COOLDOWN_PERIODS = 1440

SHAPE_LOADERS = {
    1: load_pc1_shape,
    3: load_pc3_shape,
}


def _clamp_term_end(term_start: str) -> str:
    natural = (date.fromisoformat(term_start) + timedelta(days=CONTRACT_LENGTH_DAYS)).isoformat()
    if natural > REPORT_END:
        return (date.fromisoformat(REPORT_END) + timedelta(days=1)).isoformat()
    return natural


def classify_administration_cause(record: dict) -> str:
    if record["margin_gbp"] < 0 and abs(record["margin_gbp"]) > record["capital_cost_gbp"]:
        return (
            f"margin call — trading loss £{record['margin_gbp']:.4f} dominated; "
            f"capital cost that period £{record['capital_cost_gbp']:.4f}"
        )
    return (
        f"accumulated CoC drain — capital charge exhausted treasury; "
        f"triggering period gross margin £{record['margin_gbp']:.4f}, "
        f"capital deduction £{record['capital_cost_gbp']:.4f}"
    )


def main():
    total_eac = sum(c["eac_kwh"] for c in CUSTOMERS)
    print("=== Phase 2a — Six-Customer Portfolio with SME Segment and Context Handshake ===")
    print(f"Customers: {[c['customer_id'] for c in CUSTOMERS]}")
    print(f"Portfolio EAC: {total_eac:,} kWh  (original 4-customer: {ORIGINAL_4_CUSTOMER_EAC_KWH:,} kWh)")
    print(f"Starting treasury: £{STARTING_TREASURY_GBP:.2f}  (scaled from £3,250 × {total_eac}/{ORIGINAL_4_CUSTOMER_EAC_KWH})")
    print(f"Reset hedge_fraction: {RESET_HEDGE_FRACTION:.2f}  |  Committee cooldown: {COMMITTEE_COOLDOWN_PERIODS} periods\n")

    # --- Price data: wide fetch covering 365-day sigma_recent lookback ---
    earliest_acquisition = min(date.fromisoformat(c["acquisition_date"]) for c in CUSTOMERS)
    fetch_start_natural = (earliest_acquisition - timedelta(days=365)).isoformat()
    fetch_start = max(fetch_start_natural, EARLIEST_SSP_DATE)
    cached = get_cached_prices(fetch_start, REPORT_END)
    if cached is not None:
        price_records = cached
        print(f"Cache hit: {len(price_records):,} SSP records from sim/cache/elexon_ssp_full.json ({fetch_start} to {REPORT_END}).")
        log_cache_access("elexon_ssp_full.json", hit=True, phase="2a", task_name="pre-fetch-elexon-full")
    else:
        price_records = get_system_prices_range(fetch_start, REPORT_END)
        log_cache_access("elexon_ssp_full.json", hit=False, phase="2a")
    print(f"Retrieved {len(price_records):,} SSP records ({fetch_start} to {REPORT_END}).\n")

    # Flat lookup for spot price by (date, period) — used in naked counterfactual calculation
    price_lookup = {
        (r["settlementDate"], r["settlementPeriod"]): r["systemSellPrice"]
        for r in price_records
    }

    # --- Renewal schedules (build up front; no settlement yet) ---
    schedules = {}
    for customer in CUSTOMERS:
        cid = customer["customer_id"]
        schedules[cid] = build_renewal_schedule(
            cid, customer["acquisition_date"], REPORT_END, price_records
        )

    # --- Chronological term queue: all 6 customers' terms, sorted by start date ---
    all_terms = []
    for cid, schedule in schedules.items():
        for term in schedule:
            all_terms.append((term["acquisition_date"], cid, term))
    all_terms.sort(key=lambda x: (x[0], x[1]))

    # --- Simulation state ---
    treasury = STARTING_TREASURY_GBP
    monitor = RiskCommitteeMonitor(treasury)

    # Hedge fractions: evolution rule output for next term start
    next_hf = {c["customer_id"]: RESET_HEDGE_FRACTION for c in CUSTOMERS}
    # Committee overrides: applied at next term start, then cleared
    pending_committee_overrides: dict[str, float] = {}
    # Current-term risk assessments (kept for portfolio_state computation)
    current_risk: dict[str, dict] = {}
    # Current hedge fractions (for portfolio_state and committee context)
    current_hf: dict[str, float] = {c["customer_id"]: RESET_HEDGE_FRACTION for c in CUSTOMERS}

    all_records: list[dict] = []
    customer_evolution_logs: dict[str, list] = {c["customer_id"]: [] for c in CUSTOMERS}
    customer_risk_logs: dict[str, list] = {c["customer_id"]: [] for c in CUSTOMERS}
    customer_term_indices: dict[str, int] = {c["customer_id"]: 0 for c in CUSTOMERS}
    committee_wake_ups: list[dict] = []
    administration_event = None

    # Period-level cooldown counter: starts "ready" so the committee can fire from period 1
    periods_since_committee = COMMITTEE_COOLDOWN_PERIODS

    # YTD accumulators — reset when settlement_date crosses a year boundary
    current_year_str = REPORT_START[:4]
    ytd_gross = ytd_net = ytd_capital = 0.0

    print("=== Processing terms in chronological order ===\n")

    # --- Main loop: one term at a time, interleaved across all 6 customers ---
    for term_start_str, cid, term in all_terms:
        if administration_event:
            break

        customer = get_customer(cid)
        eac_kwh = customer["eac_kwh"]
        profile_class = customer.get("profile_class", 1)
        shape_fn = SHAPE_LOADERS[profile_class]
        forward_price = term["forward_price_gbp_per_mwh"]

        term_index = customer_term_indices[cid]
        customer_term_indices[cid] += 1
        term_end_str = _clamp_term_end(term_start_str)

        # Hedge fraction for this term: committee override takes priority over evolution
        if cid in pending_committee_overrides:
            hf = pending_committee_overrides.pop(cid)
        else:
            hf = next_hf[cid]
        current_hf[cid] = hf

        # --- Risk assessment: actual position and fully-naked counterfactual ---
        actual_naked_kwh = eac_kwh * (1.0 - hf)
        actual_risk = assess_term_risk(term_start_str, actual_naked_kwh, forward_price, price_records)
        counterfactual_risk = assess_term_risk(term_start_str, float(eac_kwh), forward_price, price_records)
        current_risk[cid] = actual_risk

        # --- Settle the term ---
        term_records = run_hedged_term(
            cid, term_start_str, term_end_str,
            term["unit_rate_gbp_per_mwh"], forward_price, hf,
            actual_risk["monthly_cost_of_capital_gbp"],
            shape_fn, price_records,
        )

        # Tag every record with the data lineage regime
        for rec in term_records:
            rec["data_regime"] = "historical"

        # --- Walk this term's records: treasury update + Context Handshake check ---
        settled_this_term: list[dict] = []
        for record in term_records:
            # Reset YTD accumulators at year boundary
            rec_year = record["settlement_date"][:4]
            if rec_year != current_year_str:
                ytd_gross = ytd_net = ytd_capital = 0.0
                current_year_str = rec_year

            treasury += record["net_margin_gbp"]
            record["treasury_cash_balance_gbp"] = treasury
            ytd_gross += record["margin_gbp"]
            ytd_net += record["net_margin_gbp"]
            ytd_capital += record["capital_cost_gbp"]
            settled_this_term.append(record)

            if is_administration_triggered(treasury) and administration_event is None:
                administration_event = {
                    "date": record["settlement_date"],
                    "period": record["settlement_period"],
                    "customer_id": record["customer_id"],
                    "treasury_balance_gbp": treasury,
                    "proximate_cause": classify_administration_cause(record),
                }
                break

            # Context Handshake: compute portfolio-level VaR across all active customers
            periods_since_committee += 1
            if periods_since_committee < COMMITTEE_COOLDOWN_PERIODS:
                continue

            active_customers = [c for c in CUSTOMERS if c["customer_id"] in current_risk]
            if not active_customers:
                continue

            portfolio_var_current = sum(
                current_risk[ac["customer_id"]]["var_current_gbp"] for ac in active_customers
            )
            portfolio_var_stressed = sum(
                current_risk[ac["customer_id"]]["var_stressed_gbp"] for ac in active_customers
            )

            total_eac_active = sum(ac["eac_kwh"] for ac in active_customers)
            sigma_weighted = sum(
                current_risk[ac["customer_id"]]["sigma_recent"] * ac["eac_kwh"] / total_eac_active
                for ac in active_customers
            )

            portfolio_state = {
                "customers": [
                    {
                        "customer_id": ac["customer_id"],
                        "hedge_fraction": current_hf[ac["customer_id"]],
                        "eac_kwh": ac["eac_kwh"],
                        "active_collateral_gbp": current_risk[ac["customer_id"]]["active_collateral_gbp"],
                        "monthly_cost_of_capital_gbp": current_risk[ac["customer_id"]]["monthly_cost_of_capital_gbp"],
                        "var_current_gbp": current_risk[ac["customer_id"]]["var_current_gbp"],
                        "var_stressed_gbp": current_risk[ac["customer_id"]]["var_stressed_gbp"],
                    }
                    for ac in active_customers
                ],
                "gross_margin_ytd_gbp": ytd_gross,
                "net_margin_ytd_gbp": ytd_net,
                "capital_costs_ytd_gbp": ytd_capital,
                "sigma_recent": sigma_weighted,
                "forward_price_gbp_per_mwh": forward_price,
            }

            triggered = monitor.update(
                treasury,
                record["settlement_date"], record["settlement_period"],
                portfolio_var_current, portfolio_var_stressed,
                portfolio_state, price_records,
            )

            if triggered:
                periods_since_committee = 0
                print(
                    f"\n  [RISK COMMITTEE] Woken at {record['settlement_date']} "
                    f"period {record['settlement_period']} — treasury £{treasury:.2f}"
                )
                try:
                    adjustments = risk_committee_agent.invoke(
                        record["settlement_date"],
                        record["settlement_period"],
                        dict(current_hf),
                    )
                    for adj_cid, new_hf_val in adjustments.items():
                        pending_committee_overrides[adj_cid] = new_hf_val
                        print(f"    {adj_cid}: hf override → {new_hf_val:.2f} (next term start)")
                    committee_wake_ups.append({
                        "settlement_date": record["settlement_date"],
                        "settlement_period": record["settlement_period"],
                        "treasury_gbp": treasury,
                        "adjustments": adjustments,
                    })
                except Exception as exc:
                    print(f"    [ERROR] Risk committee invocation failed: {exc}")

        all_records.extend(settled_this_term)

        if administration_event:
            break

        # --- Evolution rule at term end (unchanged from Phase 1e) ---
        actual_term_net = sum(r["net_margin_gbp"] for r in settled_this_term)
        naked_term_gross = sum(
            r["revenue_gbp"] - (r["consumption_kwh"] / 1000)
            * price_lookup.get((r["settlement_date"], r["settlement_period"]), 0.0)
            for r in settled_this_term
        )
        distinct_months = len({r["settlement_date"][:7] for r in settled_this_term})
        naked_capital = counterfactual_risk["monthly_cost_of_capital_gbp"] * distinct_months
        naked_term_net = naked_term_gross - naked_capital

        new_hf, evolution_reasoning = evolve_hedge_fraction(hf, naked_term_net, actual_term_net)
        next_hf[cid] = new_hf

        customer_risk_logs[cid].append({
            "term_index": term_index,
            "term_start": term_start_str,
            "hedge_fraction_used": hf,
            "actual_naked_volume_kwh": actual_naked_kwh,
            "sigma_recent": actual_risk["sigma_recent"],
            "sigma_stressed": actual_risk["sigma_stressed"],
            "var_current_gbp": actual_risk["var_current_gbp"],
            "var_stressed_gbp": actual_risk["var_stressed_gbp"],
            "active_collateral_gbp": actual_risk["active_collateral_gbp"],
            "monthly_cost_of_capital_gbp": actual_risk["monthly_cost_of_capital_gbp"],
            "counterfactual_active_collateral_gbp": counterfactual_risk["active_collateral_gbp"],
            "counterfactual_monthly_cost_of_capital_gbp": counterfactual_risk["monthly_cost_of_capital_gbp"],
        })
        customer_evolution_logs[cid].append({
            "term_index": term_index,
            "term_start": term_start_str,
            "hedge_price_gbp_per_mwh": forward_price,
            "hedge_fraction_used": hf,
            "actual_margin_net_gbp": actual_term_net,
            "naked_margin_net_gbp": naked_term_net,
            "evolution_reasoning": evolution_reasoning,
            "next_hedge_fraction": new_hf,
        })

        override_note = ""
        if pending_committee_overrides.get(cid):
            override_note = f" [committee override pending → {pending_committee_overrides[cid]:.2f}]"
        print(
            f"  {cid} term {term_index:2d} ({term_start_str}→{term_end_str[:10]}): "
            f"PC{profile_class} hf={hf:.2f} → next={new_hf:.2f} "
            f"actual_net=£{actual_term_net:8.2f} naked_net=£{naked_term_net:8.2f}"
            f"{override_note}"
        )

    # --- Post-run: add naked_margin_gbp to every record for hedge-effectiveness comparison ---
    for record in all_records:
        spot = price_lookup.get((record["settlement_date"], record["settlement_period"]))
        if spot is not None:
            record["naked_margin_gbp"] = record["revenue_gbp"] - (record["consumption_kwh"] / 1000) * spot

    # =================== REPORTING ===================

    if administration_event:
        print(f"\n!!! ADMINISTRATION EVENT on {administration_event['date']} "
              f"(period {administration_event['period']}) !!!")
        print(f"    Treasury: £{administration_event['treasury_balance_gbp']:.4f}")
        print(f"    Customer: {administration_event['customer_id']}")
        print(f"    Cause: {administration_event['proximate_cause']}")
    else:
        final_treasury = all_records[-1]["treasury_cash_balance_gbp"] if all_records else STARTING_TREASURY_GBP
        print(f"\n=== Company SURVIVED the full window. Final treasury: £{final_treasury:.2f} ===")

    # --- Portfolio P&L by calendar year ---
    yearly_records: dict[str, list] = defaultdict(list)
    for record in all_records:
        yearly_records[record["settlement_date"][:4]].append(record)

    print("\n=== Portfolio P&L by calendar year ===")
    print(f"{'Year':<6} {'Gross £':>9} {'Cap £':>9} {'Net £':>9} {'Treasury £':>12} {'σ_stressed':>10} {'Flag':>10}")
    for year in sorted(yearly_records.keys()):
        yr = yearly_records[year]
        gross = sum(r["margin_gbp"] for r in yr)
        capital = sum(r["capital_cost_gbp"] for r in yr)
        net = sum(r["net_margin_gbp"] for r in yr)
        treasury_end = yr[-1]["treasury_cash_balance_gbp"]
        sigma_stressed = 0.50 if year < "2023" else 1.50
        flag = "CRISIS" if year in CRISIS_YEARS else ""
        if administration_event and year == administration_event["date"][:4]:
            flag = "ADMIN"
        print(f"{year:<6} {gross:>9.2f} {capital:>9.2f} {net:>9.2f} {treasury_end:>12.2f} {sigma_stressed:>10.2f} {flag:>10}")

    # --- Per-customer CLV (net margin total over simulation window) ---
    print("\n=== Per-customer lifetime value (total net margin, £) ===")
    for customer in CUSTOMERS:
        cid = customer["customer_id"]
        c_records = [r for r in all_records if r["customer_id"] == cid]
        gross = sum(r["margin_gbp"] for r in c_records)
        capital = sum(r["capital_cost_gbp"] for r in c_records)
        net = sum(r["net_margin_gbp"] for r in c_records)
        seg = customer["segment"]
        pc = customer.get("profile_class", 1)
        print(f"  {cid} ({seg}, PC{pc}, {customer['eac_kwh']:,} kWh): "
              f"gross=£{gross:.2f} capital=£{capital:.2f} net=£{net:.2f}")

    # --- Per-customer year-by-year hedge_fraction evolution ---
    print("\n=== Per-customer hedge_fraction evolution by year ===")
    for customer in CUSTOMERS:
        cid = customer["customer_id"]
        pc = customer.get("profile_class", 1)
        print(f"\n{cid} (PC{pc}, {customer['eac_kwh']:,} kWh, {customer['segment']}):")
        elog_by_year = {e["term_start"][:4]: e for e in customer_evolution_logs[cid]}
        rlog_by_year = {r["term_start"][:4]: r for r in customer_risk_logs[cid]}
        for year in sorted(set(list(elog_by_year) + list(rlog_by_year))):
            if year not in elog_by_year:
                continue
            if administration_event and year > administration_event["date"][:4]:
                print(f"  {year}: NOT REACHED (administration)")
                continue
            elog = elog_by_year[year]
            rlog = rlog_by_year[year]
            print(
                f"  {year}: hf={elog['hedge_fraction_used']:.2f} "
                f"VaR_curr=£{rlog['var_current_gbp']:.2f} VaR_str=£{rlog['var_stressed_gbp']:.2f} "
                f"collateral=£{rlog['active_collateral_gbp']:.2f} "
                f"actual_net=£{elog['actual_margin_net_gbp']:.2f} "
                f"naked_net=£{elog['naked_margin_net_gbp']:.2f} → "
                f"next={elog['next_hedge_fraction']:.2f}"
            )

    # --- Context Handshake wake-up log ---
    print(f"\n=== Context Handshake wake-ups: {len(committee_wake_ups)} total ===")
    if committee_wake_ups:
        for wu in committee_wake_ups:
            adjs = ", ".join(f"{k}→{v:.2f}" for k, v in wu["adjustments"].items()) or "(no adjustments)"
            print(f"  {wu['settlement_date']} p{wu['settlement_period']}: treasury=£{wu['treasury_gbp']:.2f}  {adjs}")
    else:
        print("  (no wake-ups — thresholds never breached)")

    # --- Hedge effectiveness: agent net vs naked net by year ---
    print("\n=== Hedge effectiveness (agent net margin vs naked-counterfactual gross, by year) ===")
    crisis_agent = crisis_naked = stable_agent = stable_naked = 0.0
    for year in sorted(yearly_records.keys()):
        yr = yearly_records[year]
        agent_net = sum(r["net_margin_gbp"] for r in yr)
        naked_gross = sum(r.get("naked_margin_gbp", 0.0) for r in yr)
        diff = agent_net - naked_gross
        verdict = "agent beat naked" if diff > 0 else ("naked would have won" if diff < 0 else "tied")
        flag = "  <- CRISIS" if year in CRISIS_YEARS else ""
        print(f"  {year}: agent_net=£{agent_net:.2f}  naked_gross=£{naked_gross:.2f}  diff=£{diff:+.2f}  ({verdict}){flag}")
        if year in CRISIS_YEARS:
            crisis_agent += agent_net
            crisis_naked += naked_gross
        else:
            stable_agent += agent_net
            stable_naked += naked_gross
    print(f"\n  Crisis combined: agent=£{crisis_agent:.2f} naked=£{crisis_naked:.2f} diff=£{crisis_agent - crisis_naked:+.2f}")
    print(f"  Stable combined: agent=£{stable_agent:.2f} naked=£{stable_naked:.2f} diff=£{stable_agent - stable_naked:+.2f}")

    # --- Full-window portfolio summary ---
    pnl = build_portfolio_pnl(all_records)
    total_capital = sum(r["capital_cost_gbp"] for r in all_records)
    total_net = sum(r["net_margin_gbp"] for r in all_records)
    final_treasury = all_records[-1]["treasury_cash_balance_gbp"] if all_records else STARTING_TREASURY_GBP
    end_date = administration_event["date"] if administration_event else REPORT_END

    print(f"\n=== Full-window portfolio summary ({REPORT_START} to {end_date}) ===")
    print(f"Gross margin:      £{pnl['portfolio']['margin_gbp']:>12.2f}")
    print(f"Capital costs:     £{total_capital:>12.2f}")
    print(f"Net margin:        £{total_net:>12.2f}")
    print(f"Starting treasury: £{STARTING_TREASURY_GBP:>12.2f}")
    print(f"Final treasury:    £{final_treasury:>12.2f}")
    print(f"Treasury change:   £{final_treasury - STARTING_TREASURY_GBP:>+12.2f}")
    if administration_event:
        print(f"OUTCOME: ADMINISTRATION on {administration_event['date']}")
    else:
        print("OUTCOME: SURVIVED — full window completed")

    print("\nPer-customer breakdown:")
    for customer in CUSTOMERS:
        cid = customer["customer_id"]
        cdata = pnl["by_customer"].get(cid, {})
        c_cap = sum(r["capital_cost_gbp"] for r in all_records if r["customer_id"] == cid)
        c_net = sum(r["net_margin_gbp"] for r in all_records if r["customer_id"] == cid)
        periods = cdata.get("settlement_period_count", 0)
        print(
            f"  {cid} ({customer['segment']}, PC{customer.get('profile_class', 1)}, "
            f"{customer['eac_kwh']:,} kWh): "
            f"gross=£{cdata.get('margin_gbp', 0):.2f}  capital=£{c_cap:.2f}  "
            f"net=£{c_net:.2f}  periods={periods}"
        )

    return {
        "all_records": all_records,
        "pnl": pnl,
        "administration_event": administration_event,
        "customer_evolution_logs": customer_evolution_logs,
        "customer_risk_logs": customer_risk_logs,
        "committee_wake_ups": committee_wake_ups,
        "total_capital_costs_gbp": total_capital,
        "total_net_margin_gbp": total_net,
        "final_treasury_gbp": final_treasury,
        "starting_treasury_gbp": STARTING_TREASURY_GBP,
    }


if __name__ == "__main__":
    main()
