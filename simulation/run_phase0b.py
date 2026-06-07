"""Phase 0b end-to-end run: four synthetic PC1 customers, priced and settled
against real 2016 market data, rolled up into a portfolio P&L for the
2016-10-01 to 2016-12-31 reporting window.

This is the orchestration glue wiring the five Phase 0b deliverables
together — not itself a delegated deliverable, just the script that drives
them and prints the result (the same role as the small __main__ blocks in
each module, scaled up to span the whole pipeline).
"""

from datetime import date, timedelta

from sim.profile_class_1 import load_pc1_shape
from sim.system_prices_history import get_system_prices_range
from saas.tariff_pricing import price_fixed_tariff
from simulation.settlement import run_settlement
from simulation.portfolio_pnl import build_portfolio_pnl

ACQUISITION_DATES = ["2016-01-01", "2016-04-01", "2016-07-01", "2016-10-01"]
REPORT_START = "2016-10-01"
REPORT_END = "2016-12-31"
PRICING_LOOKBACK_DAYS = 30


def build_priced_customers() -> list[dict]:
    """Price each customer's 1-year fixed unit rate on its acquisition date,
    using the average System Sell Price over the 30 days immediately prior
    plus a 5% margin (saas/tariff_pricing.price_fixed_tariff, fed only
    prices that were knowable as of that date — no peeking forward)."""
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
    customers = build_priced_customers()
    print("Priced customers (1-year fixed tariff, 30-day SSP lookback + 5% margin):")
    for customer in customers:
        print(
            f"  {customer['customer_id']}  acquired {customer['acquisition_date']}  "
            f"rate = {customer['unit_rate_gbp_per_mwh']:.4f} £/MWh "
            f"({customer['unit_rate_gbp_per_mwh'] / 10:.4f} p/kWh)"
        )

    settlement_prices = get_system_prices_range(REPORT_START, REPORT_END)
    print(f"\nSettlement-window SSP records fetched: {len(settlement_prices)}")

    settlement_records = run_settlement(
        customers, REPORT_START, REPORT_END, load_pc1_shape, settlement_prices
    )
    print(f"Settlement records produced: {len(settlement_records)}")

    pnl = build_portfolio_pnl(settlement_records)

    print(f"\nPortfolio P&L — {REPORT_START} to {REPORT_END}")
    portfolio = pnl["portfolio"]
    print(f"  Active customers:      {portfolio['customer_count']}")
    print(f"  Consumption:           {portfolio['consumption_kwh']:,.2f} kWh")
    print(f"  Revenue:               £{portfolio['revenue_gbp']:,.2f}")
    print(f"  Wholesale cost:        £{portfolio['wholesale_cost_gbp']:,.2f}")
    print(f"  Margin (gross profit): £{portfolio['margin_gbp']:,.2f}")

    print("\nBy customer:")
    for customer_id, figures in pnl["by_customer"].items():
        print(
            f"  {customer_id}: {figures['settlement_period_count']:>5} periods, "
            f"{figures['consumption_kwh']:>9,.2f} kWh, "
            f"revenue £{figures['revenue_gbp']:>8,.2f}, "
            f"cost £{figures['wholesale_cost_gbp']:>8,.2f}, "
            f"margin £{figures['margin_gbp']:>7,.2f}"
        )

    return pnl


if __name__ == "__main__":
    main()
