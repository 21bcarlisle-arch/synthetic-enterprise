"""HH (half-hourly) consumption path — Phase 6a.

For HH smart-meter customers (`saas.customers` entries with
`"metering": "HH"` and `eac_kwh=None`), settlement reads real half-hourly
consumption from `sim/hh_data/{customer_id}.csv` directly, instead of the
profile-class shape x EAC used for C1-C6/C1g-C4g.

This module is pure I/O plus small pure helpers: no settlement logic.
"""

import csv

HH_DATA_DIR = "sim/hh_data"
PERIODS_PER_DAY = 48


def is_hh_customer(customer: dict) -> bool:
    """True if `customer` is settled from real HH consumption data
    (`saas.customers` entries with `metering == "HH"`)."""
    return customer.get("metering") == "HH"


def load_hh_consumption(customer_id: str) -> dict[str, list[float]]:
    """Load `sim/hh_data/{customer_id}.csv` into {date: [48 kWh values]}.

    Returns an empty dict if no HH data file exists for customer_id."""
    path = f"{HH_DATA_DIR}/{customer_id}.csv"
    consumption = {}
    try:
        with open(path, newline="") as f:
            for row in csv.DictReader(f):
                consumption[row["date"]] = [float(row[f"p{p}"]) for p in range(1, PERIODS_PER_DAY + 1)]
    except FileNotFoundError:
        return {}
    return consumption


def hh_shape_fn(consumption: dict[str, list[float]]):
    """A `consumption_shape(date_str)` callable for
    `simulation.hedged_settlement.run_hedged_term`, backed by real HH data.

    Falls back to all-zero consumption on dates with no HH data."""
    zeros = [0.0] * PERIODS_PER_DAY

    def shape_fn(date_str):
        return consumption.get(date_str, zeros)

    return shape_fn


def estimate_annual_kwh(consumption: dict[str, list[float]]) -> float:
    """Effective annual consumption (kWh) for hedging-volume sizing,
    extrapolated from the daily mean of `consumption` to 365 days.

    Returns 0.0 if `consumption` is empty."""
    if not consumption:
        return 0.0
    total_kwh = sum(sum(day) for day in consumption.values())
    return total_kwh / len(consumption) * 365.0
