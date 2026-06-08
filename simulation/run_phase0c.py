"""Phase 0c end-to-end run: four synthetic PC1 customers, priced and settled
against real 2016 market data, rolled up into a portfolio P&L for the
2016-01-01 to 2016-12-31 reporting window."""

from datetime import date, timedelta

from sim.profile_class_1 import load_pc1_shape
from sim.system_prices_history import get_system_prices_range
from saas.tariff_pricing import price_fixed_tariff
from simulation.settlement import run_settlement
from simulation.portfolio_pnl import build_portfolio_pnl

ACQUISITION_DATES = ["2016-01-01", "2016-04-01", "2016-07-01", "2016-10-01"]
REPORT_START = "2016-01-01"
REPORT_END = "2016-12-31"
PRICING_LOOKBACK_DAYS = 30


def build_priced_customers() -> list[dict]:
    customers = []
    for index, acquisition_date in enumerate(ACQUISITION_DATES, start=1):
        acquisition = date.fromisoformat(acquisition_date)
        lookback_start = (acquisition - timedelta(days=PRICING_LOOKBACK_DAYS)).isoformat()
        pricing_window_records = get_system_prices_range(lookback_start, acquisition_date)
        unit_rate = price_fixed_tariff(acquisition_date, pricing_window_records)
        customers.append({
            "customer_id": f"C{index}",
            "acquisition_date": acquisition_date,
            "unit_rate_gbp_per_mwh": unit_rate,
        })
    return customers


def main():
    # Build priced customers
    priced_customers = build_priced_customers()
    for customer in priced_customers:
        print(
            f"  {customer['customer_id']}  acquired {customer['acquisition_date']}  "
            f"rate = {customer['unit_rate_gbp_per_mwh']:.4f} £/MWh "
            f"({customer['unit_rate_gbp_per_mwh'] / 10:.4f} p/kWh)"
        )
    
    # Fetch settlement-window system prices
    settlement_prices = get_system_prices_range(REPORT_START, REPORT_END)
    print(f"Retrieved {len(settlement_prices)} SSP records for the reporting window.")
    
    # Run settlement
    settlement_records = run_settlement(priced_customers, REPORT_START, REPORT_END, load_pc1_shape, settlement_prices)
    print(f"Produced {len(settlement_records)} settlement records.")
    
    # Build portfolio P&L
    pnl = build_portfolio_pnl(settlement_records)
    
    # Print portfolio P&L
    print(f"Portfolio P&L for the reporting window {REPORT_START} to {REPORT_END}:")
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
    
    return {"pnl": pnl, "settlement_records": settlement_records}


if __name__ == "__main__":
    main()
