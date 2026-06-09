"""Phase 2a re-run with activity-based pricing fix.

Identical to simulation/run_phase2a.py except that build_renewal_schedule()
now receives eac_kwh so the new price_fixed_tariff(forward_price, eac_kwh,
term_start) signature is satisfied.  The simulation logic, treasury physics,
Context Handshake wiring, and evolution rule are completely unchanged — this
is a pure pricing-formula comparison run.

Key differences from Phase 2a:
  - unit_rate loaded per-customer via activity-based tariff (covers capital cost)
  - C6 expected to flip net-positive — gross margin should now cover capital costs
  - Context Handshake and VaR trigger use recalibrated thresholds
    (VAR_BREACH_MULTIPLIER=2.50, treasury health gate)

The original run_phase2a.py is preserved as a historical artefact.
"""

from collections import defaultdict
from datetime import date, timedelta

from saas.customers import CUSTOMERS, get_customer
from sim.cache_store import get_cached_prices, log_cache_access
from sim.hedging_strategy import evolve_hedge_fraction
from sim.profile_class_1 import load_pc1_shape
from sim.profile_class_3 import load_pc3_shape
from sim.risk_committee import RiskCommitteeMonitor
from sim.risk_engine import assess_term_risk
from sim.system_prices_history import get_system_prices_range
from simulation.hedged_settlement import run_hedged_term
from simulation.portfolio_pnl import build_portfolio_pnl
from simulation.renewals import build_renewal_schedule
from simulation.settlement import CONTRACT_LENGTH_DAYS
import sim.risk_committee_agent as risk_committee_agent

REPORT_START = "2016-01-01"
REPORT_END = "2025-06-07"
CRISIS_YEARS = {"2021", "2022"}

ORIGINAL_4_CUSTOMER_EAC_KWH = 15_000
STARTING_TREASURY_GBP = 3250.0 * (sum(c["eac_kwh"] for c in CUSTOMERS) / ORIGINAL_4_CUSTOMER_EAC_KWH)

RESET_HEDGE_FRACTION = 0.50
EARLIEST_SSP_DATE = "2015-11-07"

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
    print("=== Phase 2a REPRICED — Activity-Based Pricing Fix + Recalibrated Risk Committee ===")
    print(f"Pricing: forward + capital_cost_per_mwh + £2/MWh flat margin")
    print(f"Risk committee: VAR_BREACH_MULTIPLIER=2.50 + treasury health gate (< 1.5x starting)")
    print(f"Customers: {[c['customer_id'] for c in CUSTOMERS]}")
    print(f"Portfolio EAC: {total_eac:,} kWh")
    print(f"Starting treasury: £{STARTING_TREASURY_GBP:.2f}\n")

    earliest_acquisition = min(date.fromisoformat(c["acquisition_date"]) for c in CUSTOMERS)
    fetch_start_natural = (earliest_acquisition - timedelta(days=365)).isoformat()
    fetch_start = max(fetch_start_natural, EARLIEST_SSP_DATE)
    cached = get_cached_prices(fetch_start, REPORT_END)
    if cached is not None:
        price_records = cached
        print(f"Cache hit: {len(price_records):,} SSP records ({fetch_start} to {REPORT_END}).")
        log_cache_access("elexon_ssp_full.json", hit=True, phase="2a_repriced", task_name="pre-fetch-elexon-full")
    else:
        price_records = get_system_prices_range(fetch_start, REPORT_END)
        log_cache_access("elexon_ssp_full.json", hit=False, phase="2a_repriced")
    print(f"Retrieved {len(price_records):,} SSP records ({fetch_start} to {REPORT_END}).\n")

    price_lookup = {
        (r["settlementDate"], r["settlementPeriod"]): r["systemSellPrice"]
        for r in price_records
    }

    schedules = {}
    for customer in CUSTOMERS:
        cid = customer["customer_id"]
        schedules[cid] = build_renewal_schedule(
            cid, customer["acquisition_date"], REPORT_END, price_records, customer["eac_kwh"]
        )

    all_terms = []
    for cid, schedule in schedules.items():
        for term in schedule:
            all_terms.append((term["acquisition_date"], cid, term))
    all_terms.sort(key=lambda x: (x[0], x[1]))

    treasury = STARTING_TREASURY_GBP
    monitor = RiskCommitteeMonitor(treasury)

    next_hf = {c["customer_id"]: RESET_HEDGE_FRACTION for c in CUSTOMERS}
    pending_committee_overrides: dict[str, float] = {}
    current_risk: dict[str, dict] = {}
    current_hf: dict[str, float] = {c["customer_id"]: RESET_HEDGE_FRACTION for c in CUSTOMERS}

    all_records: list[dict] = []
    customer_evolution_logs: dict[str, list] = {c["customer_id"]: [] for c in CUSTOMERS}
    customer_risk_logs: dict[str, list] = {c["customer_id"]: [] for c in CUSTOMERS}
    customer_term_indices: dict[str, int] = {c["customer_id"]: 0 for c in CUSTOMERS}
    committee_wake_ups: list[dict] = []
    administration_event = None

    periods_since_committee = COMMITTEE_COOLDOWN_PERIODS

    current_year_str = REPORT_START[:4]
    ytd_gross = ytd_net = ytd_capital = 0.0

    print("=== Processing terms in chronological order ===\n")

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

        if cid in pending_committee_overrides:
            hf = pending_committee_overrides.pop(cid)
        else:
            hf = next_hf[cid]
        current_hf[cid] = hf

        actual_naked_kwh = eac_kwh * (1.0 - hf)
        actual_risk = assess_term_risk(term_start_str, actual_naked_kwh, forward_price, price_records)
        counterfactual_risk = assess_term_risk(term_start_str, float(eac_kwh), forward_price, price_records)
        current_risk[cid] = actual_risk

        term_records = run_hedged_term(
            cid, term_start_str, term_end_str,
            term["unit_rate_gbp_per_mwh"], forward_price, hf,
            actual_risk["monthly_cost_of_capital_gbp"],
            shape_fn, price_records,
        )

        for rec in term_records:
            rec["data_regime"] = "historical"

        settled_this_term: list[dict] = []
        for record in term_records:
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

            if treasury <= 0 and administration_event is None:
                administration_event = {
                    "date": record["settlement_date"],
                    "period": record["settlement_period"],
                    "customer_id": record["customer_id"],
                    "treasury_balance_gbp": treasury,
                    "proximate_cause": classify_administration_cause(record),
                }
                break

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

        print(
            f"  {cid} term {term_index:2d} ({term_start_str}→{term_end_str[:10]}): "
            f"PC{profile_class} hf={hf:.2f} → next={new_hf:.2f} "
            f"unit_rate=£{term['unit_rate_gbp_per_mwh']:.2f}/MWh "
            f"actual_net=£{actual_term_net:8.2f} naked_net=£{naked_term_net:8.2f}"
        )

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

    print("\n=== Per-customer lifetime value (REPRICED) ===")
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

    print(f"\n=== Context Handshake wake-ups: {len(committee_wake_ups)} total ===")
    if committee_wake_ups:
        for wu in committee_wake_ups:
            adjs = ", ".join(f"{k}→{v:.2f}" for k, v in wu["adjustments"].items()) or "(no adjustments)"
            print(f"  {wu['settlement_date']} p{wu['settlement_period']}: treasury=£{wu['treasury_gbp']:.2f}  {adjs}")
    else:
        print("  (no wake-ups — thresholds not breached)")

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

    print("\nPer-customer breakdown (REPRICED):")
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
