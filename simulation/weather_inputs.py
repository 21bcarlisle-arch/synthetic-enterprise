"""Weather inputs for wiring 4c-2 (weather-driven demand) and 4c-3
(weather -> wholesale price sensitivity) into `simulation/run_phase2b.py`.

`sim/weather_data/{customer_id}.csv` (real Open-Meteo historical reanalysis,
per Historical Ground Truth law) currently exists only for C1-C4. Every other
customer in `saas.customers.CUSTOMERS` shares its exact `location` dict with
one of those four (C5/C1 = London, C6/C2 = Manchester, C1g-C4g = their
dual-fuel electricity counterpart's location) — so `weather_means_for_customer`
resolves each customer to the C1-C4 weather file for its location rather than
requiring a duplicate pull.

This module is pure I/O plus small pure helpers: no settlement logic.
"""

import csv
from datetime import date, timedelta

from saas.customers import CUSTOMERS

WEATHER_DATA_DIR = "sim/weather_data"

# C1-C4 are the only customers with their own weather CSVs.
_WEATHER_SOURCE_CUSTOMERS = [
    c for c in CUSTOMERS if c["commodity"] == "electricity" and c["segment"] == "resi"
]


def _weather_source_customer_id(customer: dict) -> str:
    """The customer_id whose weather CSV covers `customer`'s location —
    itself if it's a C1-C4-style resi electricity customer, otherwise the
    C1-C4 customer sharing the exact same `location` dict."""
    for source in _WEATHER_SOURCE_CUSTOMERS:
        if source["location"] == customer["location"]:
            return source["customer_id"]
    return customer["customer_id"]


def load_weather_means(customer_id: str) -> dict[str, float]:
    """Load `sim/weather_data/{customer_id}.csv` into {date: temperature_mean_c}.

    Returns an empty dict if no weather file exists for customer_id."""
    path = f"{WEATHER_DATA_DIR}/{customer_id}.csv"
    try:
        with open(path, newline="") as f:
            return {row["date"]: float(row["temperature_mean_c"]) for row in csv.DictReader(f)}
    except FileNotFoundError:
        return {}


def weather_means_for_customer(customer: dict) -> dict[str, float]:
    """{date: temperature_mean_c} for `customer`'s location, resolved via
    `_weather_source_customer_id` to an existing C1-C4 weather file."""
    return load_weather_means(_weather_source_customer_id(customer))


def lookback_mean_temps(
    weather_means: dict[str, float], term_start: str, lookback_days: int = 90
) -> list[float] | None:
    """Daily mean temperatures for the `lookback_days` days strictly before
    `term_start` (matching `sim.forward_curve.generate_forward_price`'s
    default lookback window), present in `weather_means`.

    Returns None if no days in the window have weather data, so callers can
    pass the result straight as `generate_forward_price`'s
    `lookback_daily_mean_temps_c` (None = no weather adjustment).
    """
    start = date.fromisoformat(term_start)
    temps = [
        weather_means[d]
        for offset in range(1, lookback_days + 1)
        if (d := (start - timedelta(days=offset)).isoformat()) in weather_means
    ]
    return temps or None
