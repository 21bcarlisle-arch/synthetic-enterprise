"""Weather inputs for wiring 4c-2 (weather-driven demand) and 4c-3
(weather -> wholesale price sensitivity) into `simulation/run_phase2b.py`.

THE PREMISE READS THE WORLD'S WEATHER FROM THE PER-CELL STORE (2026-09-21, W1_14 step 1)
----------------------------------------------------------------------------------------
Until this date both legs resolved a premise to one of FOUR per-property archives —
`sim/weather_data/{customer_id}.csv` — by exact `location` match. That is the design the director
refused in writing on 2026-09-16 (`sim/weather_world.py`): the world exists and a property reads
its conditions from it, so two households in one cell must experience the identical sky. The
fabric physics leg moved to the store on 2026-09-17; these two legs did not, so the book was
settling its demand SHAPE and pricing its forward TEMPERATURE off a different, per-property
weather source than the one its physics ran on. That split is what this migration ends.

MEASURED ON THE BOOK, before and after, at real inputs (18 registered supply points):

| | premises with a daily mean-temperature series | days covered |
|---|---|---|
| four per-property archives | 14/18 | 3,446 (to 2025-06-07) |
| the per-cell store | **16/18** | **3,653 (to 2025-12-31)** |

The two gained are Teesside's C_IC3/C_IC3g, which matched no archive coordinate. The two still
refused are C_IC1/C_IC2 (Birmingham), 7.4 km from the nearest held cell — `MAX_SNAP_KM` is 5.0 and
the remedy is `fabric_demand_path.ADD_THE_CELL_REMEDY`, W1_14's step 2, never a per-property pull.

**THIS IS NOT AN EQUIVALENCE AND MUST NOT BE READ AS ONE.** The store's temperature is HadUK-Grid
1 km plus the cell's own `level_c`; the archives are ERA5 at ~9 km. Over the 3,446 overlapping days
the store reads +1.19 C (London), +1.19 C (Manchester), +1.27 C (C3) and +0.25 C (C4) warmer on the
mean, 1.31 C mean-absolute at London. That is the urban heat island a ~9 km reanalysis cannot
resolve, and the 1 km observational analysis is the more faithful reading — an R13 fidelity
decision, taken blind to what it does to company results, which it will move. Cloud cover is ERA5
in both and differs only by where it was sampled (cell centre vs property coordinate): mean +0.015
pp, 1.62 pp mean-absolute at C1.

The archive readers below (`load_weather_means`, `load_weather_cloud_cover`) are kept and still
read those four CSVs, for the W1_14 siting controls. **`sim/weather_hdd.py`'s own resolver is
gone as of 2026-09-21** — the gas/HDD leg was the third implementation of "which sky did this
household have", a string rule (`C1g -> C1`, else the id) that served ten of eighteen premises a
1991-2020 climate normal, and it now asks `cell_weather_for_customer_id` below. Retiring the rest
of the per-property design (`_weather_source_customer_id`, `cell_matched_site`,
`simulation/run_phase1b_weather_pull.py`) is what is left of W1_14's step 3.

This module is pure I/O plus small pure helpers: no settlement logic.
"""

import csv
import os
from dataclasses import dataclass
from datetime import date, timedelta

from company.interfaces.supply_book import registered_supply_points
from sim.weather_world import WeatherWorld, WeatherWorldRefusal

# ONE remedy sentence, imported rather than retyped. It was rewritten on 2026-09-17 precisely
# because a second copy saying "pull that coordinate" recruits the reader into rebuilding the
# refused design; a copy here would be that second copy.
from simulation.fabric_demand_path import ADD_THE_CELL_REMEDY
from simulation.weather_cell_siting import cell_matched_site

# The supply book, bound once at import: the seam hands back the LIVE roster
# objects (see company/interfaces/supply_book.py, IDENTITY), so a runtime append
# to the acquired book is visible here exactly as it was before KNIFE pass 2.
CUSTOMERS = registered_supply_points()

WEATHER_DATA_DIR = "sim/weather_data"

#: The two store columns these legs read. Named so the field a refusal reports is the field the
#: series was built from and cannot drift from it.
TEMPERATURE_FIELD = "temperature_mean_c"
CLOUD_COVER_FIELD = "cloud_cover_pct"

#: The world, loaded at most ONCE per process. `WeatherWorld.load()` reads an 8 MB gzip into
#: ~807,000 rows; a load per premise -- or a second load because a second leg asked -- is the
#: per-property architecture wearing a different coat. `run_phase2b` loads one for the fabric leg
#: and passes it in, so the runner reads the store exactly once for all three legs.
_WORLD: WeatherWorld | None = None


def shared_world(world: WeatherWorld | None = None) -> WeatherWorld:
    """The one world this process reads.

    `world` is not an override for testing convenience: it is how a caller that has ALREADY loaded
    the store (the runner's `WeatherWorldSource`) makes sure there is one world in the process
    rather than two copies of it that could drift.

    PASSING A WORLD DOES NOT ADOPT IT, deliberately: the controls below hand this function fake
    worlds with two hand-built cells, and a passed world that became the process singleton would
    make the next caller settle on somebody's fixture. `adopt_shared_world` is the door for a
    caller that means it.
    """
    global _WORLD
    if world is not None:
        return world
    if _WORLD is None:
        _WORLD = WeatherWorld.load()
    return _WORLD


def adopt_shared_world(world: WeatherWorld) -> None:
    """Make an ALREADY-LOADED store this process's one world, for callers that cannot be passed it.

    `sim.weather_hdd` resolves a premise's sky from a bare `customer_id` five call frames below
    `run_gas_term`, with nowhere in the signature to carry a world. Without this the runner would
    hold one store for the fabric/shape/price legs and the HDD leg would load a SECOND -- 8 MB of
    gzip and ~450 MB of resident rows, twice, and two copies that can drift, which is the exact
    thing the per-cell architecture exists to make impossible.

    Idempotent and last-writer-wins: a runner calls it once, immediately after `load()`.
    """
    global _WORLD
    _WORLD = world


@dataclass(frozen=True)
class CellWeather:
    """One premise's sky: the cell it reads, the daily column, and — when there is none — why.

    THE REFUSAL TRAVELS WITH THE SERIES because the callers cannot tell the two empties apart
    otherwise. `_weather_adjusted_shape_fn` falls back to the UNADJUSTED base shape on any date it
    has no weather for, so an empty series is invisible in its output: a premise 7.4 km outside the
    store and a premise whose cell holds every day look identical downstream. That is the
    declared-`None`-collapsing-into-silent-`None` failure this repo keeps paying for.
    """

    customer_id: str
    cell: str | None
    series: dict[str, float]
    refusal: str | None = None


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

    SUPERSEDED 2026-09-21 AND NO LONGER ON ANY SETTLEMENT PATH. `weather_means_for_customer` and
    `cloud_cover_for_customer` -- the only two legs that ever reached this -- now read the per-cell
    store (`cell_weather_for_customer`). What is left here resolves the four per-property ARCHIVES
    for `load_weather_means`'s remaining readers and for the W1_14 siting controls; nothing the book
    settles, bills or hedges on comes through it. Deleting the per-property design outright --
    this, `cell_matched_site` and `simulation/run_phase1b_weather_pull.py` -- is the rest of
    W1_14's step 3; `sim/weather_hdd.py`'s own resolver went on 2026-09-21.

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
    and `fabric_demand_path.ADD_THE_CELL_REMEDY`. The world's weather lives in the PER-CELL store,
    which holds 221 cells and serves 37.1% of the drawn household population (seed 7,
    `draw_region=True`, 78/210 inside `MAX_SNAP_KM`) against these four sites' 2.0%. Measured
    2026-09-20; THE MIGRATION LANDED 2026-09-21 and this function is what it moved off.
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


def _is_a_number(value) -> bool:
    """A real float. `load_daily` writes NaN for a column the store never pulled, and `NaN != NaN`
    is the only thing that distinguishes it from a reading of zero -- which cloud cover
    legitimately is, on about a tenth of British days."""
    return isinstance(value, (int, float)) and value == value


def cell_weather_for_customer(
    customer: dict, weather_field: str = TEMPERATURE_FIELD, world: WeatherWorld | None = None
) -> CellWeather:
    """The premise's daily column from the PER-CELL store, keyed by the cell it sits in.

    The resolution rule is `WeatherWorld.cell_id_for` and nothing else -- the same call
    `fabric_demand_path.WeatherWorldSource.site_for` makes, so the cell a premise reads is decided
    in exactly ONE place and the physics leg and the shape leg cannot disagree about which sky a
    household had. (They did until 2026-09-21: this module resolved to a per-property CSV by exact
    `location` match while the physics ran on the cell.)

    COMPLETENESS IS ASKED PER FIELD, not over all five trace fields as the physics leg asks it.
    **8 of the store's 221 cells hold temperature and no wind, cloud or precipitation** (counted
    2026-09-21 over `for_cell` for every cell; `fabric_demand_path.WeatherWorldSource.available`
    cites 18 from the store validator — a different count, left beside this one rather than
    over it, and neither changes the rule). Refusing those cells a temperature series because they
    cannot answer a wind question would throw away a reading the store genuinely has. No premise on
    today's book sits in one of the 8; they are a drawn-population question.
    """
    cid = str(customer.get("customer_id", ""))
    location = customer.get("location") or {}
    lat, lon = location.get("lat"), location.get("lon")
    if lat is None or lon is None:
        # ITS OWN SENTENCE, because no store build can clear it. A premise with no coordinate needs
        # one at the DRAW; sending someone to extend the store would waste their afternoon.
        return CellWeather(cid, None, {},
                           f"{cid} carries no coordinate (lat/lon are None), so no cell can be "
                           "resolved -- it needs a coordinate at the draw")
    try:
        store = shared_world(world)
        cell = store.cell_id_for(float(lat), float(lon))
        rows = store.for_cell(cell)
    except WeatherWorldRefusal as exc:
        # The store's own reason, verbatim: it already names the nearest cell and the distance.
        return CellWeather(cid, None, {}, f"{exc}")
    series = {row["date"]: row[weather_field]
              for row in rows if _is_a_number(row.get(weather_field))}
    if not series:
        return CellWeather(cid, cell, {}, f"cell {cell} holds no {weather_field} on any of its "
                                          f"{len(rows)} days -- {ADD_THE_CELL_REMEDY}")
    return CellWeather(cid, cell, series, None)


def weather_means_for_customer(
    customer: dict, world: WeatherWorld | None = None
) -> dict[str, float]:
    """{date: temperature_mean_c} for the CELL `customer` sits in — the world's own weather.

    Empty when the store refuses; `cell_weather_for_customer(...).refusal` is the reason, and
    `weather_refusals_for_book` is how a run records them all rather than losing them one at a time.
    """
    return cell_weather_for_customer(customer, TEMPERATURE_FIELD, world).series


def cloud_cover_for_customer(
    customer: dict, world: WeatherWorld | None = None
) -> dict[str, float]:
    """{date: cloud_cover_pct} for the CELL `customer` sits in. See `weather_means_for_customer`."""
    return cell_weather_for_customer(customer, CLOUD_COVER_FIELD, world).series


def cell_weather_for_customer_id(
    customer_id: str, weather_field: str = TEMPERATURE_FIELD, world: WeatherWorld | None = None
) -> CellWeather:
    """`cell_weather_for_customer` for a premise named only by its id.

    WHY A SECOND DOOR. Every settlement leg that resolves weather has the customer RECORD in hand
    and uses `cell_weather_for_customer`. `sim.weather_hdd.get_hdd(date_str, customer_id)` does
    not: its signature carries an id and no coordinate, which is precisely why it grew a string
    rule of its own (`C1g -> C1`, everything else through unchanged) and served ten of eighteen
    premises a climate normal instead of their weather
    (`WORKER_FINDING_THE_HDD_LEG_IS_A_THIRD_RESOLVER_...2026-09-21.md`). The id is enough: the
    registered supply book publishes each point's coordinate, so the lookup that resolver could
    not do is one roster scan away, and doing it HERE is what keeps the cell rule in one place.

    An id that is not on the book gets its own sentence rather than a bare empty series, because
    the two need different remedies: a premise 7.4 km outside the store needs a cell added, an id
    that no registered point holds needs a caller corrected.
    """
    for customer in CUSTOMERS:
        if customer.get("customer_id") == customer_id:
            return cell_weather_for_customer(customer, weather_field, world)
    return CellWeather(
        customer_id, None, {},
        f"{customer_id} is not a registered supply point, so the book publishes no coordinate "
        "for it and no cell can be resolved -- check the id against "
        "`company.interfaces.supply_book.registered_supply_points`",
    )


def weather_refusals_for_book(
    customers: list[dict], weather_field: str = TEMPERATURE_FIELD,
    world: WeatherWorld | None = None,
) -> dict[str, str]:
    """{customer_id: reason} for every premise the store cannot give `weather_field`.

    On the surface rather than in a footnote: a premise with no weather settles on the unadjusted
    base shape, which is a number, and the only way anyone learns it happened is if the reason is
    carried out of here into the run's own record.
    """
    verdicts = (cell_weather_for_customer(c, weather_field, world) for c in customers)
    return {v.customer_id: v.refusal for v in verdicts if v.refusal is not None}


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
