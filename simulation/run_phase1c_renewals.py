"""Phase 1c renewal run: four synthetic PC1 customers, with contract
renewal active — when a customer's 1-year fixed contract ends, they are
automatically renewed at the forward-curve price available on the renewal
date (100% renewal rate, no churn modelled). Each customer's full tenure
across the simulation window (2016-01-01 to 2025-06-07) is now built from
a chronological sequence of independently-priced contract terms (see
simulation.renewals.build_renewal_schedule), instead of a single term that
expires after one year and leaves the book empty.

This is a re-run of run_phase1c_full_window.py's settlement pipeline with
exactly one structural change — the customer book no longer empties out —
so the calendar-year P&L breakdown can be read as a like-for-like
comparison: same pricing methodology, same consumption shapes, same real
wholesale data, but now a living book of business across the full 9.5-year
window instead of one that runs dry after ~21 months.
"""

from collections import defaultdict
from datetime import date, timedelta

from saas.clv_seed import build_clv_seed
from saas.customer_reaction import score_dissatisfaction
from saas.customers import CUSTOMERS, customer_to_settlement_input
from sim.profile_class_1 import load_pc1_shape
from sim.system_prices_history import get_system_prices_range
from simulation.portfolio_pnl import build_portfolio_pnl
from simulation.renewals import build_renewal_schedule
from simulation.settlement import run_settlement

REPORT_START = "2016-01-01"
REPORT_END = "2025-06-07"


def build_priced_customers(price_records: list[dict]) -> list[dict]:
    """Build the full renewal-aware customer book: every contract term
    (original acquisition plus every subsequent 100%-rate renewal) for
    every customer in CUSTOMERS, flattened into one list. Each entry shares
    its real customer's customer_id with its sibling terms — run_settlement
    processes each term as its own independent 365-day contract window, and
    build_portfolio_pnl (and the other aggregators) roll terms for the same
    customer_id back up into one lifetime view, with zero changes needed to
    either function.

    price_records must already span every term's pricing lookback window
    AND the full settlement reporting window — the caller fetches this once,
    up front, wide enough to cover both (see main()).
    """
    customers = []
    for customer in CUSTOMERS:
        settlement_input = customer_to_settlement_input(customer)
        schedule = build_renewal_schedule(
            settlement_input["customer_id"],
            settlement_input["acquisition_date"],
            REPORT_END,
            price_records,
        )
        customers.extend(schedule)
    return customers


def main():
    # Fetch ONE price-record set wide enough to cover every term's 90-day
    # pricing lookback AND the full settlement reporting window. The
    # earliest possible date anything needs is the earliest customer's
    # original acquisition date minus 90 days (every renewal term starts
    # later than that, so its lookback is necessarily covered too).
    earliest_acquisition = min(date.fromisoformat(c["acquisition_date"]) for c in CUSTOMERS)
    fetch_start = (earliest_acquisition - timedelta(days=90)).isoformat()
    price_records = get_system_prices_range(fetch_start, REPORT_END)
    print(f"Retrieved {len(price_records)} SSP records for {fetch_start} to {REPORT_END} (lookback + settlement window, fetched once).")

    # Build the renewal-aware priced customer book
    priced_customers = build_priced_customers(price_records)
    print(f"\nBuilt {len(priced_customers)} contract terms across {len(CUSTOMERS)} customers (renewals active):")
    for customer in priced_customers:
        print(
            f"  {customer['customer_id']}  term starts {customer['acquisition_date']}  "
            f"forward = {customer['forward_price_gbp_per_mwh']:.4f} £/MWh  "
            f"rate = {customer['unit_rate_gbp_per_mwh']:.4f} £/MWh "
            f"({customer['unit_rate_gbp_per_mwh'] / 10:.4f} p/kWh)"
        )

    # Run settlement (price_records is the same fetched record set —
    # run_settlement only looks up dates inside [REPORT_START, REPORT_END],
    # so the wider lookback-only portion is simply never matched)
    settlement_records = run_settlement(priced_customers, REPORT_START, REPORT_END, load_pc1_shape, price_records)
    print(f"Produced {len(settlement_records)} settlement records.")

    # Group settlement records by calendar year
    yearly_settlements = defaultdict(list)
    for record in settlement_records:
        year = record["settlement_date"][:4]
        yearly_settlements[year].append(record)

    # Print portfolio P&L by calendar year
    print("\nPortfolio P&L by calendar year:")
    for year in sorted(yearly_settlements.keys()):
        yearly_pnl = build_portfolio_pnl(yearly_settlements[year])
        print(
            f"  {year}: customers={yearly_pnl['portfolio']['customer_count']} "
            f"consumption={yearly_pnl['portfolio']['consumption_kwh']:.2f} kWh "
            f"revenue=£{yearly_pnl['portfolio']['revenue_gbp']:.2f} "
            f"cost=£{yearly_pnl['portfolio']['wholesale_cost_gbp']:.2f} "
            f"margin=£{yearly_pnl['portfolio']['margin_gbp']:.2f}"
        )

    # Build portfolio P&L for the full window
    pnl = build_portfolio_pnl(settlement_records)

    # Print portfolio P&L for the full window
    print(f"\nPortfolio P&L for the reporting window {REPORT_START} to {REPORT_END}:")
    print(f"Active Customer Count: {pnl['portfolio']['customer_count']}")
    print(f"Consumption (kWh): {pnl['portfolio']['consumption_kwh']:0.2f}")
    print(f"Revenue (£): £{pnl['portfolio']['revenue_gbp']:0.2f}")
    print(f"Wholesale Cost (£): £{pnl['portfolio']['wholesale_cost_gbp']:0.2f}")
    print(f"Margin (£): £{pnl['portfolio']['margin_gbp']:0.2f}")

    # Print per-customer breakdown
    print("\nPer-Customer Breakdown:")
    for customer_id, customer_data in pnl['by_customer'].items():
        print(f"Customer ID: {customer_id}, Settlement Period Count: {customer_data['settlement_period_count']}")
        print(f"Consumption (kWh): {customer_data['consumption_kwh']:0.2f}")
        print(f"Revenue (£): £{customer_data['revenue_gbp']:0.2f}")
        print(f"Cost (£): £{customer_data['wholesale_cost_gbp']:0.2f}")
        print(f"Margin (£): £{customer_data['margin_gbp']:0.2f}\n")

    # Customer reaction
    reaction = score_dissatisfaction(settlement_records)
    print("Customer reaction — dissatisfaction count (period cost > fixed-tariff bill by more than 20%):")
    for customer_id, data in reaction.items():
        print(f"  {customer_id}: {data['dissatisfaction_count']} / {data['periods_scored']} periods triggered dissatisfaction")

    # CLV seed
    clv = build_clv_seed(settlement_records)
    print("\nCLV seed — running total (contract value minus actual cost of supply) per customer:")
    for customer_id, data in clv.items():
        print(f"  {customer_id}: £{data['running_total_gbp']:.2f} over {data['periods_counted']} periods")

    return {"pnl": pnl, "settlement_records": settlement_records, "reaction": reaction, "clv": clv}


if __name__ == "__main__":
    main()
