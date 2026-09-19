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
import os
from datetime import date, timedelta

from company.interfaces.supply_book import registered_supply_points
from simulation.weather_cell_siting import cell_matched_site

# The supply book, bound once at import: the seam hands back the LIVE roster
# objects (see company/interfaces/supply_book.py, IDENTITY), so a runtime append
# to the acquired book is visible here exactly as it was before KNIFE pass 2.
CUSTOMERS = registered_supply_points()

WEATHER_DATA_DIR = "sim/weather_data"

def _has_archive(customer_id: str) -> bool:
    """Whether this id holds a per-property archive — `sim/weather_data/{id}.csv`, on disk.

    THE PROPERTY, where `commodity == "electricity" and segment == "resi"` was a PROXY for it.
    The proxy was wrong in both directions and safe only by book ORDER:

    - it ADMITTED C7, C8 and C9, which are resi electricity and hold no CSV. Each shares its exact
      coordinate with C1/C2/C3, which precede them in the book, so step 1 reached the archived id
      first and the right answer came out for the wrong reason. Reorder the book, or retire C1, and
      a premise resolves to an id whose CSV does not exist — which `load_weather_means` turns into
      an EMPTY DICT, not an error: no weather, no refusal, nothing on any surface.
    - it EXCLUDED any archived premise that is not resi electricity. Birmingham and Teesside each
      hold two I&C premises at one identical coordinate (C_IC1/C_IC2, C_IC3/C_IC3g); under the
      proxy, an archive pulled for the first could never answer the second.
    """
    return os.path.isfile(f"{WEATHER_DATA_DIR}/{customer_id}.csv")


def weather_source_customers(roster: list[dict] | None = None) -> list[dict]:
    """The premises that ARE a weather archive, read off disk rather than inferred.

    Derived per call from the LIVE roster (see `CUSTOMERS` above) rather than snapshotted at
    import, so a premise acquired mid-run is a candidate source the moment its archive lands.
    `roster` exists for controls that need to bind their own pair: on the live book the archived
    ids precede the un-archived ones at every shared coordinate, so nothing on it can discriminate
    this predicate from the proxy it replaced.
    """
    return [c for c in (CUSTOMERS if roster is None else roster) if _has_archive(c["customer_id"])]


def _weather_source_customer_id(customer: dict, roster: list[dict] | None = None) -> str:
    """The customer_id whose weather CSV covers `customer`'s location.

    Three steps, in order, and the order is the point:

    1. **Itself, or an exact `location` match against a premise that HOLDS AN ARCHIVE** — see
       `_has_archive`, which reads the CSV off disk where this step used to infer it from
       `commodity`/`segment`. Every premise that settled before this seam existed settles on the
       same CSV after it (18/18 unchanged): the repair is an equivalence on today's book and a
       correction on any other.
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

    AND A FIFTH PULL IS NOT THE REMEDY ANY MORE. The per-property archive this function resolves
    to is the design the director refused in writing on 2026-09-16 — see `sim/weather_world.py`
    and `fabric_demand_path.ADD_THE_CELL_REMEDY`. The world's weather now lives in the PER-CELL
    store, which holds 221 cells and already serves 37.1% of the drawn household population
    (seed 7, `draw_region=True`, 78/210 inside `MAX_SNAP_KM`) against these four sites' 2.0%.
    This function has not been migrated to it; that migration is W1_14's real remaining work and
    the atom's `block_reason` named the refused pull instead. Measured 2026-09-20.
    """
    for source in weather_source_customers(roster):
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
