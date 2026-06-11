"""Historical gas price data ingestion — TTF proxy, used in place of UK NBP.

ACCEPTED PROXY FOR PHASE 2B: source is FRED PNGASEUUSDM (IMF "Global price of
Natural Gas, Europe"), monthly in USD/MMBtu. Downloaded via wget. This series
is based on the Dutch TTF hub — the continental European benchmark — NOT the
UK NBP. NBP and TTF are distinct trading points that move closely together
but are not identical. The original primary source (NGT MIPI API at
data.nationalgas.com PUBOB603, true UK NBP SAP) requires OAuth login for
downloads as of 2026, so this TTF-derived series is used as a proxy. See
docs/data-sources/gas-nbp.md for the full provenance discussion.

Resolution: monthly only, expanded to one repeated value per calendar day.
This is coarser than the half-hourly Elexon SSP data used for electricity —
accepted for Phase 2b given gas retail billing is monthly-cycle anyway.

Historical Ground Truth: real IMF/TTF-sourced market prices only; no invented
data.

Output schema (matches SSP schema for compatibility with forward_curve.py):
  settlementDate: YYYY-MM-DD
  systemSellPrice: float, £/MWh

Unit conversion:
  USD/MMBtu × (1/GBPUSD) / 0.29307_MWh_per_MMBtu = £/MWh
  Fixed GBPUSD = 1.28 (reasonable multi-year average for 2016-2025).
"""

import csv
import subprocess
from datetime import date, timedelta

FRED_URL = (
    "https://fred.stlouisfed.org/graph/fredgraph.csv"
    "?id=PNGASEUUSDM&cosd=2015-01-01&coed=2025-07-01"
)
OUTPUT_PATH = "sim/gas_data/nbp_sap.csv"

GBPUSD = 1.28
MWH_PER_MMBTU = 0.29307


def fetch_fred_csv() -> str:
    """Download FRED CSV via wget. Returns raw CSV text."""
    result = subprocess.run(
        ["wget", "-q", "--timeout=30", "--tries=2", "-O", "-", FRED_URL],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"wget failed (rc={result.returncode}): {result.stderr}")
    return result.stdout


def parse_fred_csv(raw_csv: str) -> dict[str, float]:
    """Parse FRED CSV into {YYYY-MM: price_gbp_mwh}."""
    prices = {}
    for line in raw_csv.strip().splitlines()[1:]:  # skip header
        parts = line.split(",")
        if len(parts) < 2:
            continue
        obs_date, value_str = parts[0].strip(), parts[1].strip()
        try:
            usd_mmbtu = float(value_str)
        except ValueError:
            continue
        gbp_mwh = usd_mmbtu / (GBPUSD * MWH_PER_MMBTU)
        year_month = obs_date[:7]  # YYYY-MM
        prices[year_month] = round(gbp_mwh, 4)
    return prices


def expand_to_daily(
    monthly_prices: dict[str, float],
    start_date: str,
    end_date: str,
) -> list[dict]:
    """Expand monthly prices to one record per calendar day."""
    records = []
    current = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)

    while current <= end:
        ym = current.strftime("%Y-%m")
        price = monthly_prices.get(ym)
        if price is not None:
            records.append(
                {"settlementDate": current.isoformat(), "systemSellPrice": price}
            )
        current += timedelta(days=1)

    return records


def write_csv(records: list[dict], path: str) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["settlementDate", "systemSellPrice"])
        writer.writeheader()
        writer.writerows(records)


def load_nbp_history(path: str = OUTPUT_PATH) -> list[dict]:
    """Load NBP SAP history from CSV. Returns list of {settlementDate, systemSellPrice}."""
    records = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            records.append(
                {
                    "settlementDate": row["settlementDate"],
                    "systemSellPrice": float(row["systemSellPrice"]),
                }
            )
    return records


if __name__ == "__main__":
    print("Fetching FRED PNGASEUUSDM (TTF gas proxy, USD/MMBtu, monthly)...")
    raw = fetch_fred_csv()
    monthly = parse_fred_csv(raw)
    print(f"  {len(monthly)} monthly records parsed")

    print("Expanding to daily (2016-01-01 → 2025-06-07)...")
    records = expand_to_daily(monthly, "2016-01-01", "2025-06-07")
    print(f"  {len(records)} daily records generated")

    write_csv(records, OUTPUT_PATH)
    print(f"Written: {OUTPUT_PATH}")

    # Sanity check
    sample_dates = ["2016-01-01", "2022-08-01", "2025-06-01"]
    for d in sample_dates:
        match = next((r for r in records if r["settlementDate"] == d), None)
        if match:
            p = match["systemSellPrice"]
            p_therm = p * 0.29307 / 0.01  # £/MWh → p/therm approx
            print(f"  {d}: £{p:.2f}/MWh  (~{p_therm:.0f} p/therm)")
