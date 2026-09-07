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

from company.interfaces.supply_book import registered_supply_points
from simulation.weather_cell_siting import cell_matched_site

# The supply book, bound once at import: the seam hands back the LIVE roster
# objects (see company/interfaces/supply_book.py, IDENTITY), so a runtime append
# to the acquired book is visible here exactly as it was before KNIFE pass 2.
CUSTOMERS = registered_supply_points()

WEATHER_DATA_DIR = "sim/weather_data"

# C1-C4 are the only customers with their own weather CSVs.
_WEATHER_SOURCE_CUSTOMERS = [
    c for c in CUSTOMERS if c["commodity"] == "electricity" and c["segment"] == "resi"
]


def _weather_source_customer_id(customer: dict) -> str:
    """The customer_id whose weather CSV covers `customer`'s location.

    Three steps, in order, and the order is the point:

    1. **Itself, or an exact `location` match** — a C1-C4-style resi electricity customer, or one
       sharing the identical coordinate dict. Unchanged, and it still answers every premise that
       settled before this seam existed, so no live customer's weather moved.
    2. **A derived weather cell match** (`simulation.weather_cell_siting`, W1_14). The four archive
       sites are four points; the cells W1_19-W1_25 derived are what says whether some OTHER point
       experiences the same weather. Step 1 can only ever match a coordinate to four decimal
       places, which is a statement about typing rather than about climate.
    3. **Its own id**, which has no CSV, so the caller refuses. `weather_cell_siting.
       siting_refusal` is what turns that bare miss into a reason naming the driver that disagreed.

    Step 2 currently accepts nothing the supply book contains — Birmingham and Teesside each share
    some but not all of an archive site's cells, and the four sites between them cover 2.0% of GB
    households on all three drivers at once (re-cut 2026-09-07 on the UPRN placement; the 3.5% this
    line carried was the superseded centroid method's). That is a measurement of the ARCHIVE, not of this
    function: it fires the moment a fifth pull lands, and the module records why.
    """
    for source in _WEATHER_SOURCE_CUSTOMERS:
        if source["location"] == customer["location"]:
            return source["customer_id"]
    matched = cell_matched_site(customer["location"])
    if matched is not None:
        return matched
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


def load_weather_cloud_cover(customer_id: str) -> dict[str, float]:
    """Load `sim/weather_data/{customer_id}.csv` into {date: cloud_cover_pct}.

    Returns an empty dict if no weather file exists for customer_id."""
    path = f"{WEATHER_DATA_DIR}/{customer_id}.csv"
    try:
        with open(path, newline="") as f:
            return {row["date"]: float(row["cloud_cover_pct"]) for row in csv.DictReader(f)}
    except FileNotFoundError:
        return {}


def weather_means_for_customer(customer: dict) -> dict[str, float]:
    """{date: temperature_mean_c} for `customer`'s location, resolved via
    `_weather_source_customer_id` to an existing C1-C4 weather file."""
    return load_weather_means(_weather_source_customer_id(customer))


def cloud_cover_for_customer(customer: dict) -> dict[str, float]:
    """{date: cloud_cover_pct} for `customer`'s location, resolved via
    `_weather_source_customer_id` to an existing C1-C4 weather file."""
    return load_weather_cloud_cover(_weather_source_customer_id(customer))


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
