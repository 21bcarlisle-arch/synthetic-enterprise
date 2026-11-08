"""Read half-hourly consumption data from the published consumption feed — Phase 82.

No SIM module imports. Reads from docs/market_data/consumption_feed.json
published by simulation/publish_consumption_data.py.
"""
import json
from pathlib import Path

DEFAULT_FEED_PATH = Path("docs/market_data/consumption_feed.json")


def get_hh_consumption(
    customer_id: str,
    feed_path: Path = DEFAULT_FEED_PATH,
) -> list[dict]:
    """Return all HH records for one customer from the published feed.

    Returns list of {customer_id, date, period, kwh, hour} sorted by date then period.
    Empty list if feed is unavailable or customer has no HH data.
    """
    if not feed_path.exists():
        return []
    data = json.loads(feed_path.read_text())
    records = [r for r in data.get("records", []) if r.get("customer_id") == customer_id]
    return sorted(records, key=lambda r: (r["date"], r["period"]))


def recent_hh_periods(records: list[dict], n_periods: int = 48) -> list[dict]:
    """Return the last n_periods half-hourly records (most recent day by default)."""
    return records[-n_periods:]


def is_feed_available(feed_path: Path = DEFAULT_FEED_PATH) -> bool:
    """Return True if the consumption feed file exists."""
    return feed_path.exists()
