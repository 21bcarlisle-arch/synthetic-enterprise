"""Retrieval of historical national demand and wind+solar generation
records over a date range, from Elexon — the demand and renewable-supply
inputs to sim.price_engine's merit-order model.

Historical Ground Truth law: this hits the real Elexon Insights Solution API
(data.elexon.co.uk) — no synthetic data.

Two endpoints, both half-hourly (settlementDate + settlementPeriod):
  - /demand/outturn (INDO/ITSDO datasets) — initialDemandOutturn, in MW.
    Supports wide date-range queries, fetched in CHUNK_DAYS-day chunks.
  - /generation/actual/per-type/wind-and-solar (AGWS dataset) — quantity in
    MW per psrType (Wind Onshore, Wind Offshore, Solar). Limited to 7-day
    ranges per request, fetched accordingly. Records for the same
    settlementDate/settlementPeriod across psrTypes are summed into a
    single renewable_generation_mw figure.

Coverage note: both endpoints return no data before ~2016-03-01 (probed
directly) — about two months after the simulation window's 2016-01-01
start. This is a real data-availability boundary, not a bug; calibration
runs should expect a short gap at the start of the window.
"""

from datetime import datetime, timedelta

import requests

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"
DEMAND_ENDPOINT = "/demand/outturn"
WIND_SOLAR_ENDPOINT = "/generation/actual/per-type/wind-and-solar"

DEMAND_CHUNK_DAYS = 28  # API-enforced maximum range
WIND_SOLAR_CHUNK_DAYS = 7  # API-enforced maximum range

_session = requests.Session()


def get_demand_outturn_range(start_date: str, end_date: str) -> list[dict]:
    """Return raw demand/outturn records for every settlement period in
    [start_date, end_date] inclusive, as a flat list, in chronological order.

    Each record includes at least settlementDate, settlementPeriod, and
    initialDemandOutturn (MW). Fetched in DEMAND_CHUNK_DAYS-day chunks.
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    records = []
    chunk_start = start
    while chunk_start <= end:
        chunk_end = min(chunk_start + timedelta(days=DEMAND_CHUNK_DAYS - 1), end)
        params = {
            "settlementDateFrom": chunk_start.strftime("%Y-%m-%d"),
            "settlementDateTo": chunk_end.strftime("%Y-%m-%d"),
        }
        response = _session.get(BASE_URL + DEMAND_ENDPOINT, params=params)
        if response.status_code == 200:
            records.extend(response.json().get("data", []))
        chunk_start = chunk_end + timedelta(days=1)

    return records


def get_wind_solar_generation_range(start_date: str, end_date: str) -> list[dict]:
    """Return raw AGWS records for every settlement period in
    [start_date, end_date] inclusive, as a flat list, in chronological order.

    Each record includes at least settlementDate, settlementPeriod, psrType,
    and quantity (MW) — one record per psrType per period (Wind Onshore,
    Wind Offshore, Solar generation). Fetched in WIND_SOLAR_CHUNK_DAYS-day
    chunks (the API-enforced maximum range).
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    records = []
    chunk_start = start
    while chunk_start <= end:
        chunk_end = min(chunk_start + timedelta(days=WIND_SOLAR_CHUNK_DAYS - 1), end)
        params = {
            "from": chunk_start.strftime("%Y-%m-%dT00:00Z"),
            "to": (chunk_end + timedelta(days=1)).strftime("%Y-%m-%dT00:00Z"),
        }
        response = _session.get(BASE_URL + WIND_SOLAR_ENDPOINT, params=params)
        if response.status_code == 200:
            records.extend(response.json().get("data", []))
        chunk_start = chunk_end + timedelta(days=1)

    return records


def aggregate_renewable_generation(wind_solar_records: list[dict]) -> dict[tuple[str, int], float]:
    """Sum AGWS quantity across psrTypes for each (settlementDate,
    settlementPeriod), returning a {(date, period): total_mw} lookup —
    the renewable_generation_mw input to sim.price_engine.system_margin_price.
    """
    totals: dict[tuple[str, int], float] = {}
    for record in wind_solar_records:
        key = (record["settlementDate"], record["settlementPeriod"])
        totals[key] = totals.get(key, 0.0) + record["quantity"]
    return totals


if __name__ == "__main__":
    demand = get_demand_outturn_range("2024-01-01", "2024-01-02")
    print(f"{len(demand)} demand records retrieved")
    wind_solar = get_wind_solar_generation_range("2024-01-01", "2024-01-02")
    print(f"{len(wind_solar)} wind/solar records retrieved")
