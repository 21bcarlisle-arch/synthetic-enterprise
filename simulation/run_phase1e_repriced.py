"""Phase 1e re-run with activity-based pricing fix.

Identical to simulation/run_phase1e.py except that build_renewal_schedule()
now receives eac_kwh so the new price_fixed_tariff(forward_price, eac_kwh,
term_start) signature is satisfied.  The simulation logic, treasury physics,
and evolution rule are completely unchanged — this is a pure pricing-formula
comparison run, not a new phase.

The original run_phase1e.py is preserved as a historical artefact.  Do not
overwrite it.  The per-customer net margins produced here are the "new tariff"
column of the pricing-fix comparison table.
"""

from collections import defaultdict
from datetime import date, timedelta

from saas.customers import CUSTOMERS, customer_to_settlement_input, get_customer
from sim.hedging_strategy import evolve_hedge_fraction
from sim.profile_class_1 import load_pc1_shape
from sim.risk_engine import assess_term_risk, is_administration_triggered
from sim.system_prices_history import get_system_prices_range
from simulation.hedged_settlement import run_hedged_term
from simulation.portfolio_pnl import build_portfolio_pnl
from simulation.renewals import build_renewal_schedule
from simulation.settlement import CONTRACT_LENGTH_DAYS

REPORT_START = "2016-01-01"
REPORT_END = "2025-06-07"
CRISIS_YEARS = {"2021", "2022"}

STARTING_TREASURY_GBP = 3250.0
RESET_HEDGE_FRACTION = 0.50
RESET_REASONING = (
    "Phase 1d's agent converged to 0.00 (fully naked), but that was the right "
    "answer for the wrong reason — recency bias from a calm 2016-2020 formative "
    "period. Phase 1e tests whether real capital physics change the equilibrium, "
    "so we reset to the neutral 0.50 prior rather than inheriting a position that "
    "was learned under a cost structure that didn't reflect reality."
)

EARLIEST_SSP_DATE = "2015-11-07"


def _clamp_term_end(term_start: str) -> str:
    natural = (date.fromisoformat(term_start) + timedelta(days=CONTRACT_LENGTH_DAYS)).isoformat()
    if natural > REPORT_END:
        return (date.fromisoformat(REPORT_END) + timedelta(days=1)).isoformat()
    return natural


def run_customer_book(customer_id: str, eac_kwh: int, schedule: list[dict], price_lookup: dict, price_records: list[dict]):
    hedge_fraction = RESET_HEDGE_FRACTION
    all_records = []
    evolution_log = []
    risk_log = []

    for term_index, term in enumerate(schedule):
        term_start = term["acquisition_date"]
        term_end = _clamp_term_end(term_start)
        forward_price = term["forward_price_gbp_per_mwh"]

        actual_naked_volume_kwh = eac_kwh * (1 - hedge_fraction)
        actual_risk = assess_term_risk(term_start, actual_naked_volume_kwh, forward_price, price_records)

        counterfactual_naked_volume_kwh = float(eac_kwh)
        counterfactual_risk = assess_term_risk(term_start, counterfactual_naked_volume_kwh, forward_price, price_records)

        term_records = run_hedged_term(
            customer_id, term_start, term_end,
            term["unit_rate_gbp_per_mwh"], forward_price, hedge_fraction,
            actual_risk["monthly_cost_of_capital_gbp"],
            load_pc1_shape, price_records,
        )
        all_records.extend(term_records)

        actual_term_margin_net_gbp = sum(r["net_margin_gbp"] for r in term_records)

        naked_term_margin_gross_gbp = sum(
            r["revenue_gbp"] - (r["consumption_kwh"] / 1000) * price_lookup[(r["settlement_date"], r["settlement_period"])]
            for r in term_records
        )
        distinct_months_in_term = len({r["settlement_date"][:7] for r in term_records})
        naked_capital_cost_total_gbp = counterfactual_risk["monthly_cost_of_capital_gbp"] * distinct_months_in_term
        naked_term_margin_net_gbp = naked_term_margin_gross_gbp - naked_capital_cost_total_gbp

        new_hedge_fraction, evolution_reasoning = evolve_hedge_fraction(
            hedge_fraction, naked_term_margin_net_gbp, actual_term_margin_net_gbp
        )

        risk_log.append({
            "term_index": term_index,
            "term_start": term_start,
            "hedge_fraction_used": hedge_fraction,
            "actual_naked_volume_kwh": actual_naked_volume_kwh,
            "sigma_recent": actual_risk["sigma_recent"],
            "sigma_stressed": actual_risk["sigma_stressed"],
            "var_current_gbp": actual_risk["var_current_gbp"],
            "var_stressed_gbp": actual_risk["var_stressed_gbp"],
            "active_collateral_gbp": actual_risk["active_collateral_gbp"],
            "monthly_cost_of_capital_gbp": actual_risk["monthly_cost_of_capital_gbp"],
            "counterfactual_active_collateral_gbp": counterfactual_risk["active_collateral_gbp"],
            "counterfactual_monthly_cost_of_capital_gbp": counterfactual_risk["monthly_cost_of_capital_gbp"],
        })

        evolution_log.append({
            "term_index": term_index,
            "term_start": term_start,
            "hedge_price_gbp_per_mwh": forward_price,
            "hedge_fraction_used": hedge_fraction,
            "actual_margin_net_gbp": actual_term_margin_net_gbp,
            "naked_margin_net_gbp": naked_term_margin_net_gbp,
            "evolution_reasoning": evolution_reasoning,
            "next_hedge_fraction": new_hedge_fraction,
        })

        hedge_fraction = new_hedge_fraction

    return all_records, evolution_log, risk_log


def classify_administration_cause(record: dict) -> str:
    if record["margin_gbp"] < 0 and abs(record["margin_gbp"]) > record["capital_cost_gbp"]:
        return (
            f"margin call — a sharp trading loss (gross margin £{record['margin_gbp']:.4f} "
            f"in a single period) was the dominant driver that tipped the balance under, "
            f"capital cost deduction that period was £{record['capital_cost_gbp']:.4f}"
        )
    return (
        f"accumulated cost-of-capital drain — the steady capital charge, not a single "
        f"bad trading outcome, finally exhausted the treasury; triggering period gross "
        f"margin was £{record['margin_gbp']:.4f}, capital cost deduction £{record['capital_cost_gbp']:.4f}"
    )


def main():
    print("=== Phase 1e REPRICED — Nine-Year Portfolio Run with Activity-Based Pricing ===")
    print("Pricing: activity-based (forward + capital_cost_per_mwh + £2/MWh flat margin)")
    print(f"Treasury: £{STARTING_TREASURY_GBP:.2f} | Hedge reset: {RESET_HEDGE_FRACTION:.2f}\n")

    earliest_acquisition = min(date.fromisoformat(c["acquisition_date"]) for c in CUSTOMERS)
    fetch_start_natural = (earliest_acquisition - timedelta(days=365)).isoformat()
    fetch_start = max(fetch_start_natural, EARLIEST_SSP_DATE)
    price_records = get_system_prices_range(fetch_start, REPORT_END)
    print(f"Retrieved {len(price_records)} SSP records ({fetch_start} to {REPORT_END}).")

    price_lookup = {
        (r["settlementDate"], r["settlementPeriod"]): r["systemSellPrice"]
        for r in price_records
    }

    customer_books = {}

    print("\n=== Per-customer agent decisions, term by term (Phase 1e repriced) ===")
    for customer in CUSTOMERS:
        settlement_input = customer_to_settlement_input(customer)
        customer_id = settlement_input["customer_id"]
        eac_kwh = get_customer(customer_id)["eac_kwh"]
        schedule = build_renewal_schedule(customer_id, settlement_input["acquisition_date"], REPORT_END, price_records, eac_kwh)

        customer_records, evolution_log, risk_log = run_customer_book(
            customer_id, eac_kwh, schedule, price_lookup, price_records
        )
        customer_books[customer_id] = {
            "records": customer_records,
            "evolution_log": evolution_log,
            "risk_log": risk_log,
            "eac_kwh": eac_kwh,
        }

        print(f"\n{customer_id} (EAC {eac_kwh} kWh) — reset hf={RESET_HEDGE_FRACTION:.2f}")
        for rlog, elog in zip(risk_log, evolution_log):
            print(
                f"  term {rlog['term_index']} ({rlog['term_start']}): "
                f"hf={rlog['hedge_fraction_used']:.2f} "
                f"unit_rate=£{schedule[rlog['term_index']]['unit_rate_gbp_per_mwh']:.2f}/MWh "
                f"actual_net=£{elog['actual_margin_net_gbp']:.2f} "
                f"naked_net=£{elog['naked_margin_net_gbp']:.2f} → "
                f"next_hf={elog['next_hedge_fraction']:.2f}"
            )

    all_records = []
    for book in customer_books.values():
        all_records.extend(book["records"])
    all_records.sort(key=lambda r: (r["settlement_date"], r["settlement_period"], r["customer_id"]))

    treasury_cash_balance = STARTING_TREASURY_GBP
    administration_event = None
    settled_records = []

    for record in all_records:
        treasury_cash_balance += record["net_margin_gbp"]
        record["treasury_cash_balance_gbp"] = treasury_cash_balance
        settled_records.append(record)

        if is_administration_triggered(treasury_cash_balance) and administration_event is None:
            administration_event = {
                "date": record["settlement_date"],
                "period": record["settlement_period"],
                "customer_id": record["customer_id"],
                "treasury_balance_gbp": treasury_cash_balance,
                "proximate_cause": classify_administration_cause(record),
            }
            break

    all_records = settled_records

    if administration_event:
        admin_date = administration_event["date"]
        print(f"\n!!! ADMINISTRATION EVENT on {admin_date} (period {administration_event['period']}) !!!")
        print(f"    Treasury balance: £{administration_event['treasury_balance_gbp']:.4f}")
        print(f"    Proximate cause: {administration_event['proximate_cause']}")
    else:
        final_balance = all_records[-1]["treasury_cash_balance_gbp"] if all_records else STARTING_TREASURY_GBP
        print(f"\n=== Company survived the full window. Final treasury balance: £{final_balance:.2f} ===")

    for record in all_records:
        spot_price = price_lookup.get((record["settlement_date"], record["settlement_period"]))
        if spot_price is not None:
            record["naked_margin_gbp"] = record["revenue_gbp"] - (record["consumption_kwh"] / 1000) * spot_price

    yearly_records = defaultdict(list)
    for record in all_records:
        yearly_records[record["settlement_date"][:4]].append(record)

    print("\n=== Portfolio P&L by calendar year (gross / capital / net / treasury) ===")
    print(f"{'Year':<6} {'Gross £':>9} {'Cap £':>9} {'Net £':>9} {'Treasury £':>12} {'σ_stressed':>12} {'Crisis':>7}")
    for year in sorted(yearly_records.keys()):
        yr = yearly_records[year]
        gross_margin = sum(r["margin_gbp"] for r in yr)
        capital_costs = sum(r["capital_cost_gbp"] for r in yr)
        net_margin = sum(r["net_margin_gbp"] for r in yr)
        treasury_end = yr[-1]["treasury_cash_balance_gbp"]
        sigma_stressed = 0.50 if year < "2023" else 1.50
        crisis = "<- CRISIS" if year in CRISIS_YEARS else ""
        print(f"{year:<6} {gross_margin:>9.2f} {capital_costs:>9.2f} {net_margin:>9.2f} {treasury_end:>12.2f} {sigma_stressed:>12.2f} {crisis:>7}")

    pnl = build_portfolio_pnl(all_records)
    total_capital_costs = sum(r["capital_cost_gbp"] for r in all_records)
    total_net_margin = sum(r["net_margin_gbp"] for r in all_records)
    final_treasury = all_records[-1]["treasury_cash_balance_gbp"] if all_records else STARTING_TREASURY_GBP

    print(f"\n=== Full-window portfolio P&L ({REPORT_START} to {REPORT_END if not administration_event else administration_event['date']}) ===")
    print(f"Gross margin:   £{pnl['portfolio']['margin_gbp']:.2f}")
    print(f"Capital costs:  £{total_capital_costs:.2f}")
    print(f"Net margin:     £{total_net_margin:.2f}")
    print(f"Starting treasury: £{STARTING_TREASURY_GBP:.2f}")
    print(f"Final treasury:    £{final_treasury:.2f}")
    if administration_event:
        print(f"ADMINISTRATION: {administration_event['date']} — {administration_event['proximate_cause']}")
    else:
        print("SURVIVED — full window completed.")

    print("\nPer-customer breakdown (REPRICED):")
    for customer_id, cdata in pnl["by_customer"].items():
        c_capital = sum(r["capital_cost_gbp"] for r in all_records if r["customer_id"] == customer_id)
        c_net = sum(r["net_margin_gbp"] for r in all_records if r["customer_id"] == customer_id)
        print(
            f"  {customer_id}: gross=£{cdata['margin_gbp']:.2f} "
            f"capital=£{c_capital:.2f} net=£{c_net:.2f} "
            f"periods={cdata['settlement_period_count']}"
        )

    return {
        "all_records": all_records,
        "pnl": pnl,
        "administration_event": administration_event,
        "customer_books": customer_books,
        "total_capital_costs_gbp": total_capital_costs,
        "total_net_margin_gbp": total_net_margin,
        "final_treasury_gbp": final_treasury,
    }


if __name__ == "__main__":
    main()
