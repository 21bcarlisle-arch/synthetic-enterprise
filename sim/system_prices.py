"""Retrieval of System Sell Price (SSP) / System Buy Price (SBP) from Elexon.

Historical Ground Truth law: this hits the real Elexon Insights Solution API
(data.elexon.co.uk) — no synthetic data. See docs/data-sources/elexon.md for
the endpoint shape this depends on.
"""

import json
from datetime import datetime, timedelta, timezone

import requests

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"
SYSTEM_PRICES_ENDPOINT = "/balancing/settlement/system-prices/{settlement_date}"


def _fetch_system_prices(settlement_date: str) -> list[dict]:
    url = BASE_URL + SYSTEM_PRICES_ENDPOINT.format(settlement_date=settlement_date)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []


def get_latest_system_prices() -> dict | None:
    """Return the most recent raw SSP/SBP settlement-period record, unmodified.

    There is no "/latest" endpoint — settlement data is published per-date
    with a delay, so today's data may not exist yet. Query today first, fall
    back to yesterday, and take the entry with the highest settlementPeriod.
    """
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")

    for date in (today, yesterday):
        prices = _fetch_system_prices(date)
        if prices:
            return max(prices, key=lambda record: record["settlementPeriod"])

    return None


if __name__ == "__main__":
    print(json.dumps(get_latest_system_prices(), indent=2))
