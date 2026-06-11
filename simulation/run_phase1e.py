"""Phase 1e: nine-year portfolio run with enterprise risk physics.

Two questions Phase 1d left open, answered together here:

  1. Does the agent's hedge evolution rule find a different equilibrium when
     holding naked risk actually costs something — i.e. when there is a real
     cost-of-capital signal competing with the "did hedging help this term"
     momentum signal? Phase 1d's agent converged to fully-naked because calm
     market conditions in 2016-2020 made every hedge look like a waste of
     money. But Phase 1d's cost structure was wrong: in the real world,
     carrying a naked book of wholesale exposure means posting collateral, and
     collateral is not free.

  2. Does a real (if deliberately small) treasury survive a 9.5-year run of
     a capital-aware book, or does cost-of-capital drain, a bad crisis year,
     or a catastrophic confluence of both push the portfolio into
     administration?

The agent is reset to the neutral 0.50 starting prior — Phase 1d's converged
0.00 was a lesson documented in the gate review, not a position to inherit
here. The evolution rule (sim.hedging_strategy.evolve_hedge_fraction) is
carried over completely unchanged; the new signal it now sees is that the
naked counterfactual it compares itself against also carries its own, LARGER
capital cost (more naked exposure = more collateral = more monthly CoC) — so
for the first time, being more naked is not automatically cheaper. The agent
discovers whatever equilibrium it discovers from that physics, organically.

Architecture:
  - Each customer's term-by-term decision sequence is generated independently
    in run_customer_book (causally valid — hedge decisions depend only on that
    customer's own history, not on the shared treasury).
  - All settlement records are then merged into true chronological order
    (by settlement_date, settlement_period, customer_id) and walked once,
    updating the single shared treasury_cash_balance per period, to produce
    the correct administration trigger date/cause if the balance crosses zero.
  - Only records that existed before the administration trigger are included
    in any reported figure.

Phase 1e deliverables (from MASTER_BACKLOG.md):
  sim/risk_engine.py (committed separately — pure risk physics)
  simulation/hedged_settlement.py (updated — capital cost folded in)
  simulation/run_phase1e.py (this file — hand-written per Phase 1d lesson)
  docs/observability/PHASE_1e_SUMMARY.md (generated post-run)
  docs/simulation-strategy.md (updated post-run)
"""

from collections import defaultdict
from datetime import date, timedelta

from saas.customers import CUSTOMERS, customer_to_settlement_input, get_customer
from sim.hedging_strategy import evolve_hedge_fraction
from sim.profile_class_1 import load_pc1_shape
from sim.risk_engine import assess_term_risk
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
    """Run one customer's full tenure, term by term, with the risk-physics-aware
    agent. The hedge_fraction evolution rule is Phase 1d's — completely unchanged
    — but it now compares NET-of-capital-cost margins (both actual and the naked
    counterfactual priced under the same physics), so the capital drag is visible
    to the agent as it decides whether to raise or lower its hedge next term.

    Returns (all_records, evolution_log, risk_log).

    all_records: flat list of settlement records with capital_cost_gbp and
      net_margin_gbp (from run_hedged_term's Phase 1e update).
    evolution_log: one entry per term — term_index, term_start,
      hedge_price_gbp_per_mwh, hedge_fraction_used, actual_margin_net_gbp,
      naked_margin_net_gbp, evolution_reasoning, next_hedge_fraction.
    risk_log: one entry per term — all risk-engine output for both the actual
      position and the naked counterfactual, indexed by term_start.
    """
    hedge_fraction = RESET_HEDGE_FRACTION
    all_records = []
    evolution_log = []
    risk_log = []

    for term_index, term in enumerate(schedule):
        term_start = term["acquisition_date"]
        term_end = _clamp_term_end(term_start)
        forward_price = term["forward_price_gbp_per_mwh"]

        # --- Risk assessment: price the capital cost of THIS agent's actual
        # chosen position and the fully-naked counterfactual side by side.
        # Using the same physics for both ensures the comparison the evolution
        # rule sees is apples-to-apples — a naked counterfactual that doesn't
        # carry its own (larger) capital cost would systematically overstate
        # how good being naked looks, exactly reversing Phase 1d's structural
        # blind spot rather than correcting it. ---
        actual_naked_volume_kwh = eac_kwh * (1 - hedge_fraction)
        actual_risk = assess_term_risk(term_start, actual_naked_volume_kwh, forward_price, price_records)

        counterfactual_naked_volume_kwh = float(eac_kwh)
        counterfactual_risk = assess_term_risk(term_start, counterfactual_naked_volume_kwh, forward_price, price_records)

        # --- Settle the term. capital_cost_gbp and net_margin_gbp are now
        # produced per period by run_hedged_term (Phase 1e update). ---
        term_records = run_hedged_term(
            customer_id, term_start, term_end,
            term["unit_rate_gbp_per_mwh"], forward_price, hedge_fraction,
            actual_risk["monthly_cost_of_capital_gbp"],
            load_pc1_shape, price_records,
        )
        all_records.extend(term_records)

        # --- Build the net-of-capital-cost margin for each scenario ---
        actual_term_margin_net_gbp = sum(r["net_margin_gbp"] for r in term_records)

        naked_term_margin_gross_gbp = sum(
            r["revenue_gbp"] - (r["consumption_kwh"] / 1000) * price_lookup[(r["settlement_date"], r["settlement_period"])]
            for r in term_records
        )
        # Counterfactual capital cost: same monthly figure × how many distinct
        # calendar months the term touched (any month with at least one settled
        # period contributes exactly one monthly CoC deduction, proportionally
        # allocated across its periods — summed back up to monthly_coc × n_months).
        distinct_months_in_term = len({r["settlement_date"][:7] for r in term_records})
        naked_capital_cost_total_gbp = counterfactual_risk["monthly_cost_of_capital_gbp"] * distinct_months_in_term
        naked_term_margin_net_gbp = naked_term_margin_gross_gbp - naked_capital_cost_total_gbp

        # --- Phase 1d's evolution rule, unchanged. It now sees net margins. ---
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
    """Classify the proximate cause of administration for the triggering period.

    Heuristic: if the period's gross trading margin (margin_gbp) was negative
    and its absolute value exceeded the capital cost deduction (capital_cost_gbp),
    the trading loss itself was the dominant driver — a "margin call" event. In
    all other cases (including when margin_gbp was positive but the cumulative
    capital drain finally exhausted a treasury that had been eroding for months
    or years), the structural capital cost was the proximate cause.
    """
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
    print("=== Phase 1e — Nine-Year Portfolio Run with Enterprise Risk Physics ===")
    print(f"Treasury: £{STARTING_TREASURY_GBP:.2f} | Hedge reset: {RESET_HEDGE_FRACTION:.2f} | Reason: {RESET_REASONING}\n")

    # Fetch price records wide enough to supply:
    #   - build_renewal_schedule / generate_forward_price: 90-day lookback from earliest term start
    #   - assess_term_risk / calculate_sigma_recent: 365-day lookback from earliest term start
    # The 365-day window is binding — use it, clamped to where Elexon data actually begins.
    earliest_acquisition = min(date.fromisoformat(c["acquisition_date"]) for c in CUSTOMERS)
    fetch_start_natural = (earliest_acquisition - timedelta(days=365)).isoformat()
    fetch_start = max(fetch_start_natural, EARLIEST_SSP_DATE)
    price_records = get_system_prices_range(fetch_start, REPORT_END)
    print(f"Retrieved {len(price_records)} SSP records ({fetch_start} to {REPORT_END}).")

    price_lookup = {
        (r["settlementDate"], r["settlementPeriod"]): r["systemSellPrice"]
        for r in price_records
    }

    # --- Per-customer: build renewal schedule, run term-by-term agent decisions ---
    customer_books = {}

    print("\n=== Per-customer agent decisions, term by term (Phase 1e) ===")
    for customer in CUSTOMERS:
        settlement_input = customer_to_settlement_input(customer)
        customer_id = settlement_input["customer_id"]
        eac_kwh = get_customer(customer_id)["eac_kwh"]
        schedule = build_renewal_schedule(customer_id, settlement_input["acquisition_date"], REPORT_END, price_records)

        customer_records, evolution_log, risk_log = run_customer_book(
            customer_id, eac_kwh, schedule, price_lookup, price_records
        )
        customer_books[customer_id] = {
            "records": customer_records,
            "evolution_log": evolution_log,
            "risk_log": risk_log,
            "eac_kwh": eac_kwh,
        }

        print(f"\n{customer_id} (EAC {eac_kwh} kWh) — Phase 1e reset: hedge_fraction = {RESET_HEDGE_FRACTION:.2f}")
        for rlog, elog in zip(risk_log, evolution_log):
            print(
                f"  term {rlog['term_index']} ({rlog['term_start']}): "
                f"hf={rlog['hedge_fraction_used']:.2f} "
                f"σ_recent={rlog['sigma_recent']:.3f} σ_stressed={rlog['sigma_stressed']:.2f} "
                f"VaR_curr=£{rlog['var_current_gbp']:.2f} VaR_str=£{rlog['var_stressed_gbp']:.2f} "
                f"collateral=£{rlog['active_collateral_gbp']:.2f} "
                f"monthly_coc=£{rlog['monthly_cost_of_capital_gbp']:.4f}"
            )
            print(
                f"    actual_net=£{elog['actual_margin_net_gbp']:.2f} "
                f"naked_net=£{elog['naked_margin_net_gbp']:.2f} → "
                f"next_hf={elog['next_hedge_fraction']:.2f}"
            )
            print(f"    {elog['evolution_reasoning']}")

    # --- Merge all records into true chronological order (by date, period, customer_id) ---
    # customer_id as final tiebreak gives stable, documented ordering for simultaneous periods.
    all_records = []
    for book in customer_books.values():
        all_records.extend(book["records"])
    all_records.sort(key=lambda r: (r["settlement_date"], r["settlement_period"], r["customer_id"]))

    # --- Walk the merged sequence, updating the single shared treasury ---
    treasury_cash_balance = STARTING_TREASURY_GBP
    administration_event = None
    settled_records = []

    for record in all_records:
        treasury_cash_balance += record["net_margin_gbp"]
        record["treasury_cash_balance_gbp"] = treasury_cash_balance
        settled_records.append(record)

        if treasury_cash_balance <= 0 and administration_event is None:
            administration_event = {
                "date": record["settlement_date"],
                "period": record["settlement_period"],
                "customer_id": record["customer_id"],
                "treasury_balance_gbp": treasury_cash_balance,
                "proximate_cause": classify_administration_cause(record),
            }
            break  # company in administration — no further settlement occurs

    all_records = settled_records

    if administration_event:
        admin_date = administration_event["date"]
        print(f"\n!!! ADMINISTRATION EVENT on {admin_date} (period {administration_event['period']}) !!!")
        print(f"    Treasury balance: £{administration_event['treasury_balance_gbp']:.4f}")
        print(f"    Proximate cause: {administration_event['proximate_cause']}")
        print(f"    Triggered by customer: {administration_event['customer_id']}")
        print("    Reporting truncated to periods before administration.")
    else:
        final_balance = all_records[-1]["treasury_cash_balance_gbp"] if all_records else STARTING_TREASURY_GBP
        print(f"\n=== Company survived the full window. Final treasury balance: £{final_balance:.2f} ===")

    # --- Add naked_margin_gbp to every record for hedge-effectiveness comparison ---
    for record in all_records:
        spot_price = price_lookup.get((record["settlement_date"], record["settlement_period"]))
        if spot_price is not None:
            record["naked_margin_gbp"] = record["revenue_gbp"] - (record["consumption_kwh"] / 1000) * spot_price

    # --- Portfolio P&L by calendar year ---
    yearly_records = defaultdict(list)
    for record in all_records:
        yearly_records[record["settlement_date"][:4]].append(record)

    print("\n=== Portfolio P&L by calendar year (gross margin / capital costs / net margin / treasury balance) ===")
    print(f"{'Year':<6} {'Gross £':>9} {'Cap £':>9} {'Net £':>9} {'Treasury £':>12} {'σ_stressed':>12} {'Crisis':>7}")
    for year in sorted(yearly_records.keys()):
        yr = yearly_records[year]
        gross_margin = sum(r["margin_gbp"] for r in yr)
        capital_costs = sum(r["capital_cost_gbp"] for r in yr)
        net_margin = sum(r["net_margin_gbp"] for r in yr)
        treasury_end = yr[-1]["treasury_cash_balance_gbp"]
        sigma_stressed = 0.50 if year < "2023" else 1.50
        crisis = "<- CRISIS" if year in CRISIS_YEARS else ""
        admin = "<- ADMIN" if administration_event and year == administration_event["date"][:4] else ""
        flag = crisis or admin
        print(f"{year:<6} {gross_margin:>9.2f} {capital_costs:>9.2f} {net_margin:>9.2f} {treasury_end:>12.2f} {sigma_stressed:>12.2f} {flag:>7}")

    # --- Per-customer, year-by-year hedge_fraction evolution ---
    print("\n=== Per-customer year-by-year hedge_fraction evolution ===")
    for customer_id, book in customer_books.items():
        print(f"\n{customer_id} (EAC {book['eac_kwh']} kWh):")
        elog_by_year = {}
        for entry in book["evolution_log"]:
            yr = entry["term_start"][:4]
            elog_by_year[yr] = entry
        rlog_by_year = {}
        for entry in book["risk_log"]:
            yr = entry["term_start"][:4]
            rlog_by_year[yr] = entry
        for year in sorted(set(list(elog_by_year) + list(rlog_by_year))):
            if year not in elog_by_year:
                continue
            elog = elog_by_year[year]
            rlog = rlog_by_year[year]
            # filter: only show if this term's records appear in settled_records
            if administration_event and year > administration_event["date"][:4]:
                print(f"  {year}: NOT REACHED (administration {administration_event['date'][:4]})")
                continue
            print(
                f"  {year}: hf={elog['hedge_fraction_used']:.2f} "
                f"VaR_curr=£{rlog['var_current_gbp']:.2f} VaR_str=£{rlog['var_stressed_gbp']:.2f} "
                f"collateral=£{rlog['active_collateral_gbp']:.2f} "
                f"actual_net=£{elog['actual_margin_net_gbp']:.2f} "
                f"naked_net=£{elog['naked_margin_net_gbp']:.2f} → next_hf={elog['next_hedge_fraction']:.2f}"
            )

    # --- Risk assessments made each year (VaR_current vs VaR_stressed regime comparison) ---
    print("\n=== Risk assessments at term starts — VaR_current vs VaR_stressed (dual-window comparison) ===")
    all_risk_entries = []
    for customer_id, book in customer_books.items():
        for rlog in book["risk_log"]:
            all_risk_entries.append((rlog["term_start"], customer_id, rlog))
    all_risk_entries.sort(key=lambda x: (x[0], x[1]))
    prev_year = None
    for term_start, customer_id, rlog in all_risk_entries:
        year = term_start[:4]
        if administration_event and term_start > administration_event["date"]:
            continue
        if year != prev_year:
            sigma_stressed = 0.50 if year < "2023" else 1.50
            print(f"\n  {year} (σ_stressed regime: {sigma_stressed:.2f}):")
            prev_year = year
        binding = "STRESSED" if rlog["var_stressed_gbp"] >= rlog["var_current_gbp"] else "CURRENT"
        print(
            f"    {customer_id} ({term_start}): hf={rlog['hedge_fraction_used']:.2f} "
            f"σ_recent={rlog['sigma_recent']:.3f} "
            f"VaR_curr=£{rlog['var_current_gbp']:.2f} VaR_str=£{rlog['var_stressed_gbp']:.2f} "
            f"[{binding} binds] collateral=£{rlog['active_collateral_gbp']:.2f} "
            f"monthly_coc=£{rlog['monthly_cost_of_capital_gbp']:.4f}"
        )

    # --- Hedge effectiveness: agent's net margin vs naked-counterfactual net margin ---
    print("\n=== Hedge effectiveness (agent net margin vs naked net margin, by calendar year) ===")
    crisis_agent = crisis_naked = stable_agent = stable_naked = 0.0
    for year in sorted(yearly_records.keys()):
        yr = yearly_records[year]
        agent = sum(r["net_margin_gbp"] for r in yr)
        naked = sum(r.get("naked_margin_gbp", 0) for r in yr)
        diff = agent - naked
        verdict = "agent beat naked (net)" if diff > 0 else ("naked would have won (net)" if diff < 0 else "tied")
        flag = "  <- CRISIS" if year in CRISIS_YEARS else ""
        print(f"  {year}: agent_net=£{agent:.2f} naked_gross=£{naked:.2f} diff=£{diff:+.2f} ({verdict}){flag}")
        if year in CRISIS_YEARS:
            crisis_agent += agent
            crisis_naked += naked
        else:
            stable_agent += agent
            stable_naked += naked
    print(f"\n  Crisis years combined: agent=£{crisis_agent:.2f} naked=£{crisis_naked:.2f} diff=£{crisis_agent-crisis_naked:+.2f}")
    print(f"  Stable years combined: agent=£{stable_agent:.2f} naked=£{stable_naked:.2f} diff=£{stable_agent-stable_naked:+.2f}")

    # --- Full-window portfolio P&L ---
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

    print("\nPer-customer breakdown:")
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
