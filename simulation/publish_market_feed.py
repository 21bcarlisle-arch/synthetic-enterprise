"""Publish market price feed from real Elexon SSP + NBP data — Phase 80.

Called by background/process_run_complete.py after each simulation run to
make the M3 market data feed live with the most recent market prices.

Architecture: SIM layer reads raw market data and writes the feed file.
Company layer (PriceFeed) reads the file — no direct SIM imports needed.
"""
import csv
import json
from pathlib import Path

from company.market.price_feed import publish_feed

SSP_CACHE = Path("sim/cache/elexon_ssp_full.json")
NBP_CSV = Path("sim/gas_data/nbp_sap.csv")
FEED_PATH = Path("docs/market_data/price_feed.json")


def build_feed_prices(n_elec_periods: int = 48, n_gas_days: int = 10) -> list[dict]:
    """Return recent spot prices from SIM data sources.

    Electricity: last n_elec_periods (48 = 24h) from Elexon SSP.
    Gas: last n_gas_days daily NBP SAP prices.
    """
    prices: list[dict] = []

    if SSP_CACHE.exists():
        ssp = json.loads(SSP_CACHE.read_text())
        for record in ssp[-n_elec_periods:]:
            prices.append({
                "fuel": "electricity",
                "period": record.get("startTime", ""),
                "price_gbp_per_mwh": record.get("systemSellPrice", 0.0),
            })

    if NBP_CSV.exists():
        rows: list[tuple[str, str]] = []
        with open(NBP_CSV) as f:
            for row in csv.reader(f):
                if len(row) == 2:
                    rows.append((row[0], row[1]))
        for date_str, price_str in rows[-n_gas_days:]:
            try:
                price = float(price_str)
            except ValueError:
                continue
            prices.append({
                "fuel": "gas",
                "period": date_str + "T00:00:00Z",
                "price_gbp_per_mwh": price,
            })

    return prices


def publish(output_path: Path = FEED_PATH) -> None:
    """Build price feed from SIM data and write to output_path."""
    prices = build_feed_prices()
    publish_feed(prices, output_path)
