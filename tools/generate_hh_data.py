"""One-time generator for Phase 6a synthetic HH consumption data.

Produces `sim/hh_data/{C7,C8,C9}.csv` — half-hourly consumption (kWh) for
each HH smart-meter customer (`saas.customers`, `metering == "HH"`) over
REPORT_START..REPORT_END (`simulation.run_phase2b`'s 2016-01-01..2025-06-07,
exactly matching `sim/weather_data/{C1,C2,C3}.csv` coverage).

Each customer's daily shape is `sim.profile_class_1.load_pc1_shape()` (the
same real PC1 GAD shape used for C1-C4) run through
`simulation.demand_model.build_demand_shape()` with that day's weather mean
temperature and the customer's own property record (occupancy pattern,
heating system, EV/solar/smart-meter assets from `saas.property_model`) —
the same weather-driven demand adjustment profile-class customers already
get via `_weather_adjusted_shape_fn`. This keeps C7-C9's synthetic
consumption correlated with real Open-Meteo weather data without requiring
any new weather pulls (C7/C8/C9 reuse C1/C2/C3's London/Manchester/Glasgow
locations).

Run once: `python3 -m tools.generate_hh_data`.

Delegation note: hand-written (orchestration-adjacent, per protocol).
"""

import csv
import os
from datetime import date, timedelta

from saas.customers import CUSTOMERS
from saas.property_model import (
    DEFAULT_ASSETS,
    DEFAULT_HEATING_SYSTEM,
    DEFAULT_OCCUPANCY_PATTERN,
    build_properties,
)
from sim.profile_class_1 import load_pc1_shape
from simulation.demand_model import build_demand_shape
from simulation.hh_consumption import HH_DATA_DIR, is_hh_customer
from simulation.weather_inputs import weather_means_for_customer

# Matches simulation.run_phase2b.REPORT_START/REPORT_END (and
# sim/weather_data/{C1,C2,C3}.csv coverage) exactly. Not imported from
# run_phase2b to avoid a circular dependency: run_phase2b's
# EFFECTIVE_EAC_KWH reads sim/hh_data/{cid}.csv, which this script generates.
REPORT_START = "2016-01-01"
REPORT_END = "2025-06-07"

FIELDNAMES = ["date"] + [f"p{p}" for p in range(1, 49)]

DEFAULT_PROPERTY = {
    "heating_system": DEFAULT_HEATING_SYSTEM,
    "occupancy_pattern": DEFAULT_OCCUPANCY_PATTERN,
    "assets": dict(DEFAULT_ASSETS),
}


def _date_range(start: str, end: str):
    d = date.fromisoformat(start)
    end_d = date.fromisoformat(end)
    while d <= end_d:
        yield d.isoformat()
        d += timedelta(days=1)


def generate_for_customer(customer: dict, properties: dict) -> None:
    cid = customer["customer_id"]
    weather_means = weather_means_for_customer(customer)
    property_record = properties.get(cid, DEFAULT_PROPERTY)

    os.makedirs(HH_DATA_DIR, exist_ok=True)
    path = f"{HH_DATA_DIR}/{cid}.csv"
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for date_str in _date_range(REPORT_START, REPORT_END):
            base_shape = load_pc1_shape(date_str)
            mean_temp = weather_means.get(date_str)
            if mean_temp is None:
                shape = base_shape
            else:
                shape = build_demand_shape(base_shape, mean_temp, "electricity", property_record)
            row = {"date": date_str}
            row.update({f"p{p}": shape[p - 1] for p in range(1, 49)})
            writer.writerow(row)
    print(f"Wrote {path}")


def main():
    hh_customers = [c for c in CUSTOMERS if is_hh_customer(c)]
    properties = build_properties(CUSTOMERS)
    for c in hh_customers:
        generate_for_customer(c, properties)


if __name__ == "__main__":
    main()
