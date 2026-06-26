"""Publish HH consumption data for smart meter customers — Phase 82.

Reads half-hourly consumption profiles from sim/hh_data/{customer_id}.csv
and publishes recent periods to docs/market_data/consumption_feed.json.
Called by process_run_complete.py after each sim run.

Architecture: SIM layer reads raw HH data and writes the feed.
Company layer reads the feed — no direct SIM imports.
"""
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

HH_DATA_DIR = Path("sim/hh_data")
FEED_PATH = Path("docs/market_data/consumption_feed.json")
HH_CUSTOMERS = ("C7", "C8", "C9")


def read_hh_data(customer_id: str, n_days: int = 2) -> list[dict]:
    """Return last n_days of half-hourly consumption for one HH customer.

    Returns list of {customer_id, date, period (1-48), kwh} dicts.
    """
    path = HH_DATA_DIR / f"{customer_id}.csv"
    if not path.exists():
        return []
    rows: list[list[str]] = []
    with open(path) as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if row:
                rows.append(row)
    recent = rows[-n_days:]
    records: list[dict] = []
    for row in recent:
        if len(row) < 49:
            continue
        date_str = row[0]
        for period in range(1, 49):
            try:
                kwh = float(row[period])
            except (ValueError, IndexError):
                kwh = 0.0
            records.append({
                "customer_id": customer_id,
                "date": date_str,
                "period": period,
                "kwh": round(kwh, 4),
                "hour": (period - 1) * 0.5,  # decimal hour (0.0 = 00:00, 23.5 = 23:30)
            })
    return records


def publish_consumption(
    hh_customers: tuple = HH_CUSTOMERS,
    n_days: int = 2,
    output_path: Path = FEED_PATH,
) -> None:
    """Build consumption feed and write to output_path."""
    all_records: list[dict] = []
    for cid in hh_customers:
        all_records.extend(read_hh_data(cid, n_days=n_days))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "published_at": datetime.now(timezone.utc).isoformat(),
        "records": all_records,
    }
    with open(output_path, "w") as f:
        json.dump(payload, f)
