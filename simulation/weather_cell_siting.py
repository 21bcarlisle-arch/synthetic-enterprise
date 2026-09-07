"""Which derived weather cell a premise sits in, and whether the archive covers it — W1_14.

W1_19-W1_22 and W1_25 derived the cells: three heat-load drivers per 1 km land cell from the
HadUK-Grid normals, household-weighted through the censuses, and a coverage curve that priced the
partition. W1_27 then read that curve as a build decision -- **about 21 cells per driver, held
separately**. All of it landed in `tools/`, and nothing in `simulation/`, `company/` or `saas/`
imported a line of it, so the world's household heat load was not driven by any of it.

This module is that import. It is the sim-side seam between the derivation and the weather archive
the demand path actually runs on.

WHAT IT ANSWERS
---------------
`simulation/weather_inputs._weather_source_customer_id` resolves a premise to a weather archive by
**exact `location` dict identity** -- two customers share a CSV only if they share a coordinate to
the fourth decimal. Anything else falls through to its own id, finds no file, and is dropped from
the fabric path with "no weather archive for this customer's location". That refusal is honest and
it is also blind: it cannot say whether the premise's weather is genuinely unlike the four sites, or
merely unlike them in the fourth decimal of a latitude.

The derived cells can say. A cell IS the claim that two places are interchangeable for the driver
that cuts it, so `cell_matched_site` accepts a substitution exactly when the derivation says the
premise and the site share a cell **on all three drivers at once** -- because the archive CSV
carries all three (temperature, cloud, wind) and a substitution transfers all three together.

WHAT IT MEASURED, AND WHY THAT IS THE REAL ANSWER
--------------------------------------------------
Wiring the cells in was framed as a mapping problem. It is not. Run against the real grid, the four
sites the archive covers (`sim/weather_data/C1-C4.csv`) occupy 4 of the 21 cells on each driver, and
the household share of GB they cover is:

| driver | cells occupied | GB households covered |
|---|---|---|
| winter temperature | 4 / 21 | **20.4%** |
| annual wind | 4 / 21 | 27.8% |
| annual sunshine | 4 / 21 | 17.3% |
| **all three at once** | — | **2.0%** |

RE-CUT 2026-09-07 on the OS Open UPRN placement (175,188 occupied 1 km cells). The figures this
table carried until then — 20.5% / 30.7% / 27.9% / 3.5% — were the POSTCODE CENTROID method's
(121,668 cells), and the placement moved on 2026-09-06 without the artefact being regenerated. They
are kept here beside their correction because every one of them overstated the archive: annual
sunshine read 27.9% against a true 17.3%, and `all_three` read 3.5% against 2.0%. Superseded
figures, not a recalculation of the same thing.

So the substitution branch below is real but narrow, and NEITHER of the two uncovered locations in
the supply book clears it: Birmingham shares Manchester's wind cell and neither its temperature nor
its sunshine cell; Teesside shares nothing with anything. **The gap between the derivation and the
world is archive breadth, not a lookup** -- four real pulls against a decision of twenty-one -- and
no mapping written here can close it.

AND THAT IS THE I&C GAP, NOT THE HOUSEHOLD ONE (measured 2026-09-06, pre-registered in
`docs/staging/SEAT_PREREG_WEATHER_CELL_BRANCH_REACHABILITY_2026-09-06.md`)
---------------------------------------------------------------------------------------------
This atom's subject is *household* heat load, and the paragraph above was written from the supply
book's LOCATIONS rather than from its HOUSEHOLDS. Asked of the households, the answer inverts:

* Of the 18 registered supply points, 14 answer at **step 1** (exact location), 0 at **step 2**, and
  4 refuse. All four refusals are `C_IC1`, `C_IC2`, `C_IC3`, `C_IC3g` -- **I&C**. Birmingham and
  Teesside hold no resi premise at all, and **no resi premise sits at an un-archived location**.
  So the two pulls W1_14 waits on move I&C coverage from 0/4 to 4/4 and household coverage from
  100% to 100%.
* Of a drawn population (210 customers, seed 7), the coordinate now depends on the region dial.
  With the DEFAULT placeholder region, 100% still carry `lat: None, lon: None` -- correctly, since
  `UNKNOWN_SYNTHETIC` is not a real region and has no household distribution. With
  `draw_region=True`, **100% are sited** (measured 2026-09-07): W2_18 landed in `ec8a18710` and
  `simulation/household_siting.coordinate_for_customer` draws a 1 km cell from the region's own
  census household distribution.

**And 0 of those 210 resolved here** until the re-cut below. The coordinate stopped being the
binding constraint when W2_18 landed and THIS MODULE'S ARTEFACT became it: `locations` was a
precomputed TABLE of the seven locations `derive()` is handed, keyed to four decimals (~11 m), and
a drawn household's coordinate was never in it and could not collide with it.

WHAT THE ARTEFACT IS CUT OVER, AND WHY IT IS THE GRID AND NOT THE DRAWN POPULATION
----------------------------------------------------------------------------------
Re-cut 2026-09-07. `cells_for_location` now asks two tables: the JSON's named `locations` first
(archive sites, supply book, witness -- they keep their names and their measured
`km_to_cell_centre`), then `occupied_land_cells.csv`, which holds **all 175,188 occupied 1 km land
cells** with their per-driver cell. **210/210 drawn households now resolve, and 2 of them match an
archive site** (both London's cells). The site_cells.json this replaced was byte-identical
afterwards: the re-cut is purely additive and moved no coverage figure and no named location.

The join is an EQUALITY and nothing is fabricated to make it. `tools/household_siting_frame.py`
builds each frame row's coordinate from `round(d["latitude"][i], 4)` and the normals' own longitude
auxiliary coordinate -- the identical two expressions `_occupied_space()` uses -- so a drawn
coordinate IS a land cell's own coordinate at the same precision. Measured: **139,938 distinct
frame coordinates, 139,938 join, 0 miss**, and the 175,188 grid keys are 175,188 distinct keys, so
4 dp cannot merge two cells.

The direction was to cut over the drawn population; the artefact is cut over the **whole grid**
instead, which is 25% larger (4.3 MB against 3.4 MB, beside the 5.0 MB frame that is already
committed) and buys the property rather than today's answer. The frame is a SUBSET that moves --
it covers England and Wales and has no Scottish region today -- so an artefact cut to it would go
silently stale the moment the frame gained one, and "which population" would be a question every
future reader had to re-ask. Cut to the grid there is no such question: the row count IS
`occupied_land_cells` in the JSON, which is what
`test_the_two_artefacts_were_cut_by_the_same_partition` checks.

FAIL-CLOSED SURVIVES THE RE-CUT. A coordinate that is not a land cell -- offshore, outside GB, or
22 m off a cell centre -- is still refused with its reason. There is no nearest-cell fallback and
adding one is what `fabric_physics.latitude_for_weather_site` refuses one layer down. What the
re-cut changed is which refusal a drawn household receives: not "absent from the artefact" any
more, but the honest third one, "shares no archive site's cells on all three drivers" -- 208 of the
210. **The re-cut is a LOOKUP fix and not an archive-breadth fix**, and the 2.0% is untouched.

The accept branch is not decorative and is not a proximity test. Twenty-eight 1 km cells share all
three of London's cells (re-measured 2026-09-07 on the UPRN placement; seventeen on the superseded
centroid one), and the furthest of them is on the Cornish coast 301 km away
(`tests/simulation/test_weather_cell_siting.py`): the mechanism matches CLIMATE, and a control that
only ever exercised a neighbouring postcode could not tell the two apart.

WHY AN ARTEFACT AND NOT A LIVE DERIVATION
------------------------------------------
Deriving costs a 245,077-cell netCDF read, a 1.67 million-postcode census join and three weighted
k-means fits, against a `~/.cache` that a fresh worktree does not have. `weather_cell_derivation`
already records why that matters: a control nobody can afford to run is a control that gets
skipped. So `derive()` is the expensive path, run deliberately, and the committed artefact is what
the world reads -- and `derive()` is reachable from a test, so the artefact is falsifiable rather
than merely asserted.

FAIL-CLOSED: a coordinate that is not in the artefact is REFUSED with its reason, never sited by
nearest-anything. Siting a premise the derivation has never seen would be exactly the fabrication
`fabric_physics.latitude_for_weather_site` refuses one layer down.
"""

import csv
import json
from pathlib import Path
from typing import Mapping

PROJECT = Path(__file__).resolve().parent.parent

#: The committed answer. Regenerate with `python3 -m simulation.weather_cell_siting --derive`.
ARTEFACT = PROJECT / "sim" / "weather_cells" / "site_cells.json"

#: The BULK table: every occupied 1 km land cell of the derivation, with its per-driver cell.
#: Written by the SAME `--derive` run as `ARTEFACT`, from the same partition, so the two cannot be
#: regenerated apart. See "WHAT THE ARTEFACT IS CUT OVER" above for why this is the whole grid and
#: not the frame's 139,938 cells.
LAND_CELLS = PROJECT / "sim" / "weather_cells" / "occupied_land_cells.csv"

#: W1_27's build decision, per driver and held separately -- NOT the 987 the joint curve wanted.
#: `docs/market_research/the_cell_decision_and_what_the_world_actually_uses.md`.
CELLS_PER_DRIVER = 21

#: The archive sites, and every location the supply book currently places a premise at. Siting is
#: keyed by coordinate rather than by customer id because the archive is a property of the PLACE:
#: C5 shares C1's CSV because it shares London, not because of anything about C5.
#: Sourced from `company.interfaces.supply_book.registered_supply_points()`; kept here as data so
#: `derive()` does not have to cross the supply-book seam to regenerate the artefact.
KNOWN_LOCATIONS: dict[str, tuple[float, float]] = {
    "London": (51.5074, -0.1278),
    "Manchester": (53.4808, -2.2426),
    "Glasgow": (55.8642, -4.2518),
    "Cotswolds": (51.8330, -1.8433),
    "Birmingham": (52.4862, -1.8904),
    "Teesside": (54.5973, -1.1049),
}

#: A REACHABILITY WITNESS, not a premise: an occupied 1 km land cell on the north Cornish coast that
#: the derivation puts in all three of London's cells, 301 km away. It is sited into the artefact so
#: that the accept branch below can be exercised from the committed answer, with no `~/.cache` and
#: no k-means — because a branch this project cannot prove is REACHABLE is one it must assume is
#: unreachable (R15). It also fixes what the branch means: a control that only ever tried a
#: neighbouring postcode could not tell climate matching from a proximity test.
#:
#: MOVED 2026-09-07, from (50.5392, -4.2371). A WITNESS IS A MEASUREMENT AND EXPIRES WITH THE THING
#: IT WITNESSES: when the placement moved from postcode centroids to the UPRN address record the old
#: cell stopped sharing all three of London's, so the accept branch briefly had NO witness and was
#: unreachable again — the exact R15 failure this constant exists to prevent, reintroduced by a
#: re-derivation rather than by a code change. Re-measured against the current partition: 28 cells
#: share all three of London's, and this is the furthest of them.
REACHABILITY_WITNESS: dict[str, tuple[float, float]] = {
    "Cornish coast (reachability witness, not a premise)": (50.4689, -4.1492),
}

#: Which archive CSV each covered location's premises settle on.
ARCHIVE_SITES: dict[str, str] = {
    "London": "C1",
    "Manchester": "C2",
    "Glasgow": "C3",
    "Cotswolds": "C4",
}

_EARTH_RADIUS_KM = 6371.0

#: A premise must land within this of a land cell centre to be sited at all. The grid is 1 km, so
#: half a diagonal is 0.71 km; 2 km allows a coastal or estuarine coordinate whose own square is
#: sea to take the nearest land cell, and refuses anything genuinely offshore.
MAX_SITING_KM = 2.0

_cache: dict | None = None
_land_cache: tuple[tuple[str, ...], dict[str, tuple[int, ...]]] | None = None
_land_cache_path: Path | None = None


def _key(lat: float, lon: float) -> str:
    """The artefact key for a coordinate. Four decimals is ~11 m and is the precision the supply
    book itself carries, so a key collision means the same place."""
    return f"{lat:.4f},{lon:.4f}"


def load(path: Path | str = ARTEFACT) -> dict:
    """The committed siting, read once."""
    global _cache
    if _cache is None or path != ARTEFACT:
        with open(path) as f:
            data = json.load(f)
        if path != ARTEFACT:
            return data
        _cache = data
    return _cache


def load_land_cells(path: Path | str = LAND_CELLS) -> tuple[tuple[str, ...],
                                                            dict[str, tuple[int, ...]]]:
    """`(drivers, {key: cell labels})` over every occupied 1 km land cell, read once per process.

    The drivers come from the CSV's OWN header rather than from `DRIVERS` or from the JSON, so a
    column reordered in the artefact cannot be silently read as another driver's label. The header
    is checked against the JSON by `test_the_two_artefacts_were_cut_by_the_same_partition`.

    Held as `key -> tuple` rather than `key -> {driver: label}` because the second costs 50 MB
    against this one's 30 MB for 175,188 rows (measured), and the dict is rebuilt per lookup, which
    happens once per premise and not once per settlement period.

    FAIL-CLOSED (R15): a missing table RAISES rather than returning empty. Returning `{}` would
    turn every drawn household's lookup into "this coordinate is not in the artefact" — a refusal
    that reads as a fidelity finding when it is really an absent file, which is the exact shape
    `household_siting.load_frame` refuses for the same reason.
    """
    global _land_cache, _land_cache_path
    target = Path(path)
    if _land_cache is not None and _land_cache_path == target:
        return _land_cache
    if not target.is_file():
        raise FileNotFoundError(
            f"{target} -- the occupied land cell table is absent, so no coordinate outside the "
            f"{len(load()['locations'])} named locations can be sited. It is committed; regenerate "
            "with `python3 -m simulation.weather_cell_siting --derive` (needs the HadUK normals "
            "and the census pulls in ~/.cache/synthetic-enterprise).")
    with target.open() as fh:
        reader = csv.reader(fh)
        header = next(reader)
        drivers = tuple(header[2:])
        cells = {f"{row[0]},{row[1]}": tuple(int(c) for c in row[2:]) for row in reader}
    if not cells:
        raise ValueError(f"{target} holds no land cell -- an empty table would refuse every drawn "
                         "household and report no error")
    _land_cache, _land_cache_path = (drivers, cells), target
    return _land_cache


def cells_for_location(location: Mapping, path: Path | str = ARTEFACT,
                       land_path: Path | str = LAND_CELLS) -> dict | None:
    """The per-driver cell labels for `location`, or None if the derivation has never sited it.

    TWO tables, asked in this order and for different reasons. The JSON's `locations` holds the
    named places — the archive sites, the supply book's own coordinates, the reachability witness —
    and it answers first so that a named premise keeps its name and its measured
    `km_to_cell_centre`. The land cell table answers everything else: it is the derivation's whole
    occupied grid, so any coordinate that IS a 1 km land cell resolves, which is every coordinate
    `household_siting.coordinate_for_customer` can draw.

    None is a RESULT: it says this coordinate is not an occupied land cell of the derivation —
    offshore, outside GB, or off-grid by more than the key's ~11 m — not that it has no weather.
    """
    lat, lon = location.get("lat"), location.get("lon")
    if lat is None or lon is None:
        return None
    key = _key(lat, lon)
    named = load(path)["locations"].get(key)
    if named is not None:
        return named
    drivers, cells = load_land_cells(land_path)
    labels = cells.get(key)
    if labels is None:
        return None
    # `km_to_cell_centre` is 0.0 and that is a measurement, not a placeholder: the key matched a
    # land cell's OWN coordinate exactly, so the premise is at the cell centre by construction.
    return {"lat": lat, "lon": lon, "km_to_cell_centre": 0.0,
            "cells": dict(zip(drivers, labels))}


def cell_matched_site(location: Mapping, path: Path | str = ARTEFACT,
                      land_path: Path | str = LAND_CELLS) -> str | None:
    """The archive site whose weather this premise may settle on, or None.

    Accepts ONLY when the derivation puts the premise and the site in the same cell on all three
    drivers. One driver disagreeing is a refusal, because the CSV carries all three and a
    substitution cannot take the temperature without also taking the wind and the cloud."""
    sited = cells_for_location(location, path, land_path)
    if sited is None:
        return None
    data = load(path)
    for site_location, site in ARCHIVE_SITES.items():
        site_cells = data["archive_sites"].get(site_location)
        if site_cells and site_cells["cells"] == sited["cells"]:
            return site
    return None


def siting_refusal(location: Mapping, path: Path | str = ARTEFACT,
                   land_path: Path | str = LAND_CELLS) -> str:
    """Why this premise cannot take an archive site's weather — named, per R15.

    A refusal that says which driver disagreed is how the next pull gets prioritised; a bare None
    would make the archive gap look like a coordinate typo.

    THREE refusals, not two, and the third was found by measuring rather than by reading. A premise
    with NO COORDINATE is not an unsited coordinate: until 2026-09-06 both came back "regenerate
    with `--derive`", which names a remedy that CANNOT work — re-deriving the whole GB grid puts
    nothing in the artefact for a location whose lat is `None`.

    2026-09-07: that split was right and its SECOND half was wrong. `--derive` was left prescribed
    for an unsited REAL coordinate, on the reasoning that re-deriving CAN site one — but `derive()`
    sites only the locations handed to it, and the CLI hands it the same seven every time. So bare
    `--derive` re-sites the same seven and reaches no drawn household either. It went unnoticed
    because when it was written NO real coordinate could reach this branch; W2_18 then landed and
    100% of drawn households (with `draw_region=True`) now land on it. A refusal is only tested by
    the population that actually receives it."""
    if location.get("lat") is None or location.get("lon") is None:
        return (f"{location.get('region', location)!r} carries no coordinate (lat/lon are None), so "
                f"the derivation cannot site it. This is the DRAW's placeholder — not an archive "
                f"gap and not a derivation gap: `simulation.population_draw.SyntheticCustomer."
                f"to_customer_dict` renders every drawn household with lat=None, lon=None, and "
                f"`--derive` cannot reach it. The remedy is a coordinate at the DRAW (W2_18, and "
                f"W1_24 which waits on a population); fabricating one here is what "
                f"`fabric_physics.latitude_for_weather_site` refuses one layer down")
    sited = cells_for_location(location, path, land_path)
    if sited is None:
        drivers, cells = load_land_cells(land_path)
        return (f"{location.get('region', location)!r} carries a real coordinate that is not in the "
                f"derived artefact — it is not one of the {len(cells):,} occupied 1 km land cells "
                f"the derivation covers, to the ~11 m the key resolves. That means offshore, "
                f"outside GB, or a coordinate that is not a HadUK-Grid land cell centre; it does "
                f"NOT mean the artefact is cut too narrow, which is what this refusal said until "
                f"2026-09-07, when the table held seven locations and every drawn household landed "
                f"here. Do NOT fall back to the nearest sited location — that is proximity "
                f"standing in for climate, which this seam exists to refuse, and it is what "
                f"`fabric_physics.latitude_for_weather_site` refuses one layer down")
    data = load(path)
    disagreements = []
    for site_location, site in ARCHIVE_SITES.items():
        site_cells = data["archive_sites"].get(site_location)
        if not site_cells:
            continue
        differ = [d for d, c in sited["cells"].items() if site_cells["cells"].get(d) != c]
        if not differ:
            return f"no refusal: shares every cell with {site}"
        disagreements.append(f"{site} differs on {'/'.join(differ)}")
    return (f"{location.get('region', location)!r} shares no archive site's cells on all three "
            f"drivers ({'; '.join(disagreements)}); the archive covers "
            f"{data['coverage']['all_three'] * 100:.1f}% of GB households at "
            f"{data['cells_per_driver']} cells per driver")


def archive_coverage(path: Path | str = ARTEFACT) -> dict:
    """The household share of GB the four archive sites cover, per driver and jointly."""
    return load(path)["coverage"]


# ---------------------------------------------------------------------------
# The expensive path. Everything below reads `~/.cache/synthetic-enterprise`.
# ---------------------------------------------------------------------------


def _occupied_space():
    """(standardised drivers, weights, latitude, longitude) over household-occupied land cells.

    The same space `weather_cell_derivation._space` builds, plus the two true coordinates needed to
    place a premise in it. Longitude is read from the normals file's own auxiliary coordinate for
    the same reason `weather_cell_drivers` reads latitude there rather than deriving it from the
    OSGB northing: the projection converges northwards and the two are not interchangeable.
    """
    import numpy as np

    from tools import weather_cell_drivers as wcd
    from tools import weather_cell_weights as wcw
    from tools.weather_cell_derivation import DRIVERS

    d = wcd.drivers()
    w, _ = wcw.aligned_to_land(d)
    occupied = w > 0
    native = np.column_stack([d[k][occupied] for k in DRIVERS]).astype(np.float64)
    weights = w[occupied]
    mean = np.average(native, axis=0, weights=weights)
    sd = np.sqrt(np.average((native - mean) ** 2, axis=0, weights=weights))

    with wcd._open("tas") as ds:
        xs = ds.coords["projection_x_coordinate"].values
        ys = ds.coords["projection_y_coordinate"].values
        lon_grid = ds.coords["longitude"].values
    east, north = d["east"][occupied], d["north"][occupied]
    lon = lon_grid[np.searchsorted(ys, north), np.searchsorted(xs, east)]

    return (native - mean) / sd, weights, d["latitude"][occupied], lon


def _nearest_land_cell(lat, lon, cell_lat, cell_lon):
    """(index, great-circle km) of the occupied land cell nearest a coordinate."""
    import numpy as np

    dlat = np.radians(cell_lat - lat)
    dlon = np.radians(cell_lon - lon)
    a = (np.sin(dlat / 2) ** 2
         + np.cos(np.radians(lat)) * np.cos(np.radians(cell_lat)) * np.sin(dlon / 2) ** 2)
    km = _EARTH_RADIUS_KM * 2 * np.arcsin(np.sqrt(a))
    i = int(np.argmin(km))
    return i, float(km[i])


def _derived(cells_per_driver: int = CELLS_PER_DRIVER,
             locations: Mapping[str, tuple[float, float]] | None = None) -> tuple[dict, list]:
    """`(site_cells.json's payload, occupied_land_cells.csv's rows)` from ONE expensive pass.

    Both artefacts come out of a single partition here rather than from two entry points, because
    two entry points is the whole drift class: the JSON's `archive_sites` and the CSV's rows are
    the same k-means labels, and a world where one can be regenerated without the other is a world
    where a premise and the archive site it matches were cut by different partitions.
    `test_the_two_artefacts_were_cut_by_the_same_partition` is the control; this is the reason it
    can pass.

    The partition is `weather_cell_derivation.per_driver_curve`'s exactly — one weighted k-means per
    standardised driver, `n_init=1`, `random_state=0` — so a cell label here means the same thing as
    a cell in the published curve. Reproducing the clustering with different settings would give
    cells that carry the decision's NAME and not its measurement.
    """
    import numpy as np
    from sklearn.cluster import KMeans

    from tools.weather_cell_derivation import DRIVERS

    locations = dict(locations or {**KNOWN_LOCATIONS, **REACHABILITY_WITNESS})
    z, weights, cell_lat, cell_lon = _occupied_space()

    labels = {
        driver: KMeans(n_clusters=cells_per_driver, n_init=1, random_state=0)
        .fit(z[:, [i]], sample_weight=weights).labels_
        for i, driver in enumerate(DRIVERS)
    }

    land_rows = sorted(
        (round(float(cell_lat[i]), 4), round(float(cell_lon[i]), 4),
         *(int(labels[d][i]) for d in DRIVERS))
        for i in range(len(weights))
    )

    sited: dict[str, dict] = {}
    for name, (lat, lon) in locations.items():
        i, km = _nearest_land_cell(lat, lon, cell_lat, cell_lon)
        if km > MAX_SITING_KM:
            continue
        sited[name] = {
            "lat": lat,
            "lon": lon,
            "km_to_cell_centre": round(km, 3),
            "cells": {d: int(labels[d][i]) for d in DRIVERS},
        }

    site_indices = [sited[loc]["cells"] for loc in ARCHIVE_SITES if loc in sited]
    total = float(weights.sum())
    coverage = {}
    joint = np.ones(len(weights), dtype=bool)
    for driver in DRIVERS:
        occupied_cells = {c[driver] for c in site_indices}
        covered = np.isin(labels[driver], list(occupied_cells))
        coverage[driver] = round(float(weights[covered].sum()) / total, 4)
        joint &= covered
    coverage["all_three"] = round(float(weights[joint].sum()) / total, 4)

    return {
        "cells_per_driver": cells_per_driver,
        "drivers": list(DRIVERS),
        "partition": "one weighted k-means per driver, n_init=1, random_state=0 "
                     "(weather_cell_derivation.per_driver_curve)",
        "occupied_land_cells": int(len(weights)),
        "archive_sites": {loc: sited[loc] for loc in ARCHIVE_SITES if loc in sited},
        "locations": {_key(v["lat"], v["lon"]): {"name": k, **v} for k, v in sited.items()},
        "coverage": coverage,
    }, land_rows


def derive(cells_per_driver: int = CELLS_PER_DRIVER,
           locations: Mapping[str, tuple[float, float]] | None = None) -> dict:
    """Site every known location in the derived cells, and price what the archive covers."""
    return _derived(cells_per_driver, locations)[0]


def derive_land_cells(cells_per_driver: int = CELLS_PER_DRIVER) -> list[tuple]:
    """`(lat, lon, *cell labels)` for every occupied 1 km land cell, sorted.

    Sorted so the committed CSV is a stable diff: a re-derivation that moves one cell shows as one
    changed line rather than as 175,188 reordered ones, which is the difference between a review
    that can see a change and one that cannot.
    """
    return _derived(cells_per_driver)[1]


def _write_land_cells(rows: list[tuple], drivers: list[str], path: Path = LAND_CELLS) -> None:
    """Write the bulk table. Four decimals on the coordinate — the same ~11 m `_key` resolves and
    the same precision `tools/household_siting_frame` writes, so the two join by equality."""
    with Path(path).open("w", newline="") as fh:
        out = csv.writer(fh)
        out.writerow(["lat", "lon", *drivers])
        for lat, lon, *cells in rows:
            out.writerow([f"{lat:.4f}", f"{lon:.4f}", *cells])


def main(argv: list[str] | None = None) -> int:
    import argparse

    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--derive", action="store_true", help=f"rebuild {ARTEFACT.name} from the grid")
    p.add_argument("--show", action="store_true", help="print the committed siting")
    args = p.parse_args(argv)

    if args.derive:
        # ONE pass, BOTH artefacts. Writing them from separate commands is what would let the
        # named locations and the land cell table be cut by different partitions.
        data, land_rows = _derived()
        ARTEFACT.parent.mkdir(parents=True, exist_ok=True)
        ARTEFACT.write_text(json.dumps(data, indent=2) + "\n")
        _write_land_cells(land_rows, data["drivers"])
        print(f"wrote {ARTEFACT}")
        print(f"wrote {LAND_CELLS} ({len(land_rows):,} occupied land cells)")
    else:
        data = load()

    if args.show or not args.derive:
        cov = data["coverage"]
        print(f"{data['cells_per_driver']} cells per driver over "
              f"{data['occupied_land_cells']:,} occupied land cells")
        for driver in data["drivers"]:
            print(f"  {driver:12s} archive covers {cov[driver] * 100:5.1f}% of GB households")
        print(f"  {'ALL THREE':12s} archive covers {cov['all_three'] * 100:5.1f}% of GB households")
        for key, loc in data["locations"].items():
            site = cell_matched_site({"lat": loc["lat"], "lon": loc["lon"], "region": loc["name"]})
            print(f"  {loc['name']:12s} {loc['cells']}  -> {site or 'NO ARCHIVE SITE'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
