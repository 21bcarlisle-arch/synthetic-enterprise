"""Build the world's weather store: one daily series per 1 km CELL, pulled once.

REUSE: tools/build_weather_world.py
CLASS: CUSTOM
INDEX: searched "weather pull", "open-meteo", "build store", "cell weather", "ingest".
       `sim/weather_ingestor.get_daily_weather` is the FETCHER and is called rather than
       re-implemented. `tools/fetch_haduk_grid.py` pulls the multi-GB source grids from CEDA --
       a different artefact, and its daily tier is temperature-only and October-March only.
       `sim/weather_world.py` is the STORE this writes and the reader every property uses.

       IT REPLACES `tools/pull_book_weather.py`, which pulled one archive PER PROPERTY and is
       deleted in the same commit. That tool worked and was architecturally wrong: 101 of the
       book's 257 located accounts share a 1 km cell, so it would have downloaded the same sky
       twice and made those two households' demand difference unattributable.

       CORRECTED 2026-09-08, BESIDE THE CLAIM RATHER THAN OVER IT. There was no such commit.
       The sentence above is written in the past tense of a landing that never happened: this
       file, `sim/weather_world.py` and `tools/pull_book_weather.py` were all still `??` two
       days later, so nothing was replaced and nothing was deleted. The supersession ARGUMENT
       is untouched and still right -- 101 shared cells is a measurement, not a plan -- but it
       describes an intention, and until this file is in a commit that also removes the tool it
       names, `pull_book_weather.py` is live on disk and this paragraph is the only thing
       saying otherwise.

       TWO FURTHER CLAIMS IN THIS DOCSTRING WERE NOT TRUE OF THE TREE, and they are why the
       module could not simply be landed to make the first one true:
         * `tools/validate_weather_world.py`, cited below as the HadUK check that measures the
           store's resolution instead of assuming it, DID NOT EXIST. A path in a prose comment
           is a reachability edge, so this cited a validator nothing could run.
         * `sim/weather_world/` was an EMPTY DIRECTORY. The store this builds had never been
           built, so `sim/weather_world.py` was a reader with nothing to read.
       Neither module had a single control, and neither was imported by anything but the other.
       Recorded in
       `docs/staging/SEAT_RESULT_THE_DEMAND_VECTOR_CANONS_FIVE_DELIVERABLES_ARE_THREE_LANDED_ONE_HELD_AND_ONE_UNBUILT_2026-09-08.md`.

       BOTH ARE NOW CLOSED, 2026-09-16, and the closing found a third thing neither note saw.
       The store was built 09-09 (156 cells x 3,653 days) and `tools/validate_weather_world.py`
       is written; what neither note recorded is that **the store on disk and the writer in this
       file had different SHAPES**, so re-running the tool did not rebuild the store, it
       corrupted it:
         * `_write` emitted no `level_c`, no `decomposition` and no `regimes.json`, though all
           three are on disk, and named ERA5 as the temperature source where the store names
           HadUK. `build` never called `extract_temperature` at all -- the extractor was dead
           code.
         * the series on disk is keyed by REGIME (`R00`...), and `_existing_rows` read that key
           as a CELL id. So every one of the 156 held cells read as missing, a resume re-pulled
           all of them, and the rewritten file would have carried both keyings at once.
       All three legs are repaired below, and `tools/validate_weather_world.py` re-derives the
       temperature half from the HadUK grids and diffs it against the bytes on disk, so the claim
       that the store is reproducible is measured rather than asserted.

WHAT A CELL IS
--------------
The project's existing key: `(easting // 1000, northing // 1000)` on the OSGB grid, taken from the
HadUK-Grid geometry already on this machine, so a cell here is the cell `demand_case_coverage` and
`weather_cell_weights` already mean. The pull uses the CELL CENTRE's coordinates, not any
property's -- which is what makes the series a property of the place.

WHICH SOURCE EACH VARIABLE COMES FROM, AND WHY THE ANSWER CHANGED
-----------------------------------------------------------------
**Temperature is HadUK-Grid 1 km daily. Wind, cloud and precipitation are ERA5 via Open-Meteo.**
That is what the store on disk says, and until 2026-09-16 this docstring and
`sim/weather_world.py` both said the opposite -- that temperature came from ERA5 for all twelve
months and HadUK was only a CHECK. The reason both gave was a real one:

    "HadUK has daily 1 km temperature on disk, but only October-March. Taking winter temperature
     from HadUK and summer from ERA5 would put a source discontinuity inside ONE variable at
     exactly the shoulder months where heating switches on."

**THE PREMISE IS FALSE OF THIS MACHINE, AND IT IS FALSE BY COUNTING.** Under
`~/.cache/synthetic-enterprise/haduk_grid/`, `tasmin`, `tas` and `tasmax` each hold **120 monthly
1 km daily grids for 2016-01 through 2025-12** -- twelve months of every year, not six. The
October-March limit is real of `fetch_haduk_grid.HEATING_SEASON_MONTHS`, which is the heating-season
pull that module makes; it is not a limit on what CEDA serves and it is not what is on this disk.
So there is no shoulder-month seam to avoid, and the choice is between a 1 km observational
analysis and a ~9 km reanalysis for the one variable the fabric path is most sensitive to.

The 1 km product wins on a measurement already in `sim/weather_world.Cell.level_c`: HadUK reads
+1.2 C warmer than ERA5 at London, Manchester and Glasgow and -0.55 C at the rural site. That is
the urban heat island, a reanalysis at ~9 km cannot resolve it, and it lands directly on heating
demand. ERA5 keeps the three variables HadUK does not serve daily at 1 km (`sfcWind` and `sun`
answer 404 -- see `fetch_haduk_grid.DAILY_WORLD_VARIABLES`).

WHAT CANNOT BE HAD PER CELL
----------------------------
Nothing, on this variable set. ERA5 is a grid and serves min/mean/max temperature, wind, cloud and
precipitation for any coordinate, so a per-cell pull gets everything a per-property pull would and
shares it correctly. The one honest limit is RESOLUTION rather than availability: ERA5-Land is
about 9 km, so two cells closer than that receive the same series -- which is why temperature,
where that resolution costs the most, is taken from the 1 km product instead. It is measured
rather than assumed by `tools/validate_weather_world.py`, and it is not improved by fetching per
property: two properties 200 m apart would get identical values from the same grid cell either way.

WHAT THE STORE IS SHAPED LIKE, AND WHY THE WRITER HAS TO KNOW
-------------------------------------------------------------
The store is not the raw series. It is **per-cell LEVEL + per-regime ANOMALY**, and
`sim/weather_world.WeatherWorld.for_cell` adds the level back on read:

  * `cells.json` carries each cell's `level_c` -- the mean of its own daily mean temperature over
    the whole window, which is its climatology and the thing the 1 km pull was worth making.
  * `daily.csv.gz` is keyed by REGIME id, and its three temperature columns are the anomaly about
    that level. Wind, cloud and precipitation are stored raw; they have no level to remove.
  * `regimes.json` maps cell -> regime. Under REPLAY that map is the identity and `k` equals the
    cell count, which is what `--build` writes here: one regime per cell, so no cell's daily
    wiggle is shared with another's. The indirection exists for GENERATED weather, where a few
    coherent regimes serve hundreds of thousands of cells.

`_write` is the single place that decomposition lives, and `_existing_rows` is its exact inverse,
so a resumed build reads back what a previous one wrote instead of mistaking a regime id for a
cell id.
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from sim.weather_world import (  # noqa: E402
    CELLS_PATH,
    FIELDS,
    REGIMES_PATH,
    SERIES_PATH,
    STORE_DIR,
    WeatherWorldRefusal,
    cell_id,
)

#: The three columns the level is removed from. Wind, cloud and precipitation are stored raw --
#: a "mean cloud cover anomaly" would be a quantity nobody asked for and the reader adds nothing
#: back to them.
LEVELLED = ("temperature_min_c", "temperature_mean_c", "temperature_max_c")

#: MEASURED. A one-second gap got HTTP 429 after five pulls -- Open-Meteo weights a request by the
#: data it returns and each of these is ten years of daily values across six variables.
PAUSE_SECONDS = 20.0
RETRY_ATTEMPTS = 4
RETRY_BACKOFF_SECONDS = 60.0

#: The window the simulation runs over.
START_DATE = "2016-01-01"
END_DATE = "2025-12-31"


def book_cells() -> dict[str, dict]:
    """Every 1 km cell the supply book occupies, keyed by cell id, with its centre.

    The cell centres come from the HadUK-Grid coordinates, so the store's geometry is the same
    geometry every other cell-keyed measurement in this repo uses.
    """
    import numpy as np

    from simulation.run_phase2b import ACQUIRED_CUSTOMERS, CUSTOMERS, SUCCESSOR_CUSTOMERS
    from tools import weather_cell_drivers as drv

    grid = drv.drivers()
    east, north = np.asarray(grid["east"]), np.asarray(grid["north"])
    lat, lon = np.asarray(grid["latitude"]), np.asarray(grid["longitude"])

    seen: dict[str, dict] = {}
    for book in (CUSTOMERS, ACQUIRED_CUSTOMERS, SUCCESSOR_CUSTOMERS):
        for customer in book:
            cid = str(customer.get("customer_id", ""))
            if cid:
                seen.setdefault(cid, customer)

    cells: dict[str, dict] = {}
    for customer in seen.values():
        location = customer.get("location") or {}
        plat, plon = location.get("lat"), location.get("lon") or location.get("lng")
        if plat is None or plon is None:
            continue
        plat, plon = float(plat), float(plon)
        # Nearest LAND cell centre. `drivers()` is already masked to land, so a coastal premise
        # snaps inland rather than to a sea cell with no data.
        d2 = (lat - plat) ** 2 + ((lon - plon) * np.cos(np.radians(plat))) ** 2
        i = int(np.argmin(d2))
        east_km, north_km = int(east[i] // 1000), int(north[i] // 1000)
        key = cell_id(east_km, north_km)
        cells.setdefault(key, {
            "cell_id": key,
            "east_km": east_km,
            "north_km": north_km,
            "latitude": round(float(lat[i]), 5),
            "longitude": round(float(lon[i]), 5),
        })
    return dict(sorted(cells.items()))


HADUK_DAY = Path.home() / ".cache" / "synthetic-enterprise" / "haduk_grid"

#: What HadUK actually serves daily at 1 km, measured with a real credential (sfcWind and sun
#: answer 404 -- see `fetch_haduk_grid.DAILY_WORLD_VARIABLES`).
HADUK_DAILY = {"tasmin": "temperature_min_c", "tas": "temperature_mean_c",
               "tasmax": "temperature_max_c"}


def extract_temperature(cells: dict[str, dict], progress=print) -> dict:
    """Per-cell daily min/mean/max from the HadUK 1 km grids already on this machine.

    THE LOOP IS INVERTED ON PURPOSE. Each monthly grid is opened ONCE and every cell taken from
    it, so the cost is O(files) rather than O(files x cells) -- 3 minutes instead of days, and the
    difference is entirely in which loop is outside.
    """
    import numpy as np
    import xarray as xr

    # The cell CENTRES are already in `cells`; each grid file carries its own lat/lon coords, so
    # the snap is done per file rather than against the normals grid.
    keys = list(cells)
    want_lat = np.array([cells[k]["latitude"] for k in keys])
    want_lon = np.array([cells[k]["longitude"] for k in keys])

    rows: dict[str, dict[str, dict]] = {k: {} for k in keys}
    idx_cache: dict[tuple, tuple] = {}

    for variable, field in HADUK_DAILY.items():
        paths = sorted((HADUK_DAY / variable / "day").glob("*.nc"))
        paths = [p for p in paths if any(f"_day_{y}" in p.name for y in range(2016, 2026))]
        progress(f"  {variable}: {len(paths)} monthly grid(s)")
        for path in paths:
            ds = xr.open_dataset(path)
            name = variable if variable in ds else list(ds.data_vars)[0]
            arr = ds[name]
            key = (arr.shape[1], arr.shape[2])
            if key not in idx_cache:
                lat2d = ds.coords["latitude"].values
                lon2d = ds.coords["longitude"].values
                flat_lat, flat_lon = lat2d.ravel(), lon2d.ravel()
                picks = []
                for la, lo in zip(want_lat, want_lon):
                    d2 = (flat_lat - la) ** 2 + ((flat_lon - lo) * np.cos(np.radians(la))) ** 2
                    picks.append(int(np.argmin(d2)))
                idx_cache[key] = np.unravel_index(np.array(picks), lat2d.shape)
            r, c = idx_cache[key]
            values = arr.values[:, r, c]                       # (days, cells)
            dates = [str(d)[:10] for d in ds.coords["time"].values]
            ds.close()
            for di, date in enumerate(dates):
                for ci, cell in enumerate(keys):
                    v = values[di, ci]
                    if np.isfinite(v):
                        rows[cell].setdefault(date, {})[field] = round(float(v), 2)

    # HADUK INTERPOLATES tasmin, tas AND tasmax AS INDEPENDENT FIELDS, so on a day with a small
    # diurnal range their surfaces can cross at an individual cell: the raw grid gives
    # tasmin 15.276 > tasmax 14.863 at E224N0382 on 2016-06-07, and `premise_trace` rightly
    # REFUSES that rather than modelling a house whose night is warmer than its day.
    #
    # 310 of 569,868 cell-days, 0.05%, median inversion 0.25 C against a normal diurnal range of
    # 6.31 C. They are SWAPPED rather than clamped, and the reason is checkable: HadUK's tas is
    # exactly (tasmin + tasmax) / 2, and swapping preserves that identity where clamping would
    # break it. So the two fields are crossed, not the temperature wrong.
    crossed = 0
    for cell, days in rows.items():
        for date, v in days.items():
            lo, hi = v.get("temperature_min_c"), v.get("temperature_max_c")
            if lo is not None and hi is not None and lo > hi:
                v["temperature_min_c"], v["temperature_max_c"] = hi, lo
                crossed += 1
    if crossed:
        progress(f"  reordered {crossed} crossed min/max cell-day(s) — a HadUK interpolation "
                 f"artefact, swapped so tas stays their midpoint")
    return rows


def _fetch_with_backoff(fetch, key, lat, lon, start, end, progress):
    """A 429 is "come back later", not a refusal. Anything else fails on the first attempt.

    Resumability is the real protection and it is structural: `build` skips cells already in the
    store, so an interrupted run is resumed by re-running the same command.
    """
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            return fetch(key, lat, lon, start, end)
        except Exception as exc:  # noqa: BLE001 -- re-raised below when it is not a rate limit
            if "429" not in str(exc) or attempt == RETRY_ATTEMPTS:
                raise
            wait = RETRY_BACKOFF_SECONDS * attempt
            progress(f"      rate limited; waiting {wait:.0f}s (attempt {attempt})")
            time.sleep(wait)
    raise RuntimeError("unreachable")


def _stored_geometry() -> tuple[dict[str, dict], dict[str, str]]:
    """The cells and the regime map the store already holds, or empty pairs if it holds none.

    Read SEPARATELY from the series because a build must not lose a cell that has left the book:
    its centre is only recorded here, and re-deriving it is impossible once `book_cells` stops
    returning it.
    """
    cells: dict[str, dict] = {}
    if CELLS_PATH.is_file():
        cells = dict(json.loads(CELLS_PATH.read_text(encoding="utf-8")).get("cells", {}))
    regimes: dict[str, str] = {}
    if REGIMES_PATH.is_file():
        regimes = dict(json.loads(REGIMES_PATH.read_text(encoding="utf-8"))["regime_of_cell"])
    return cells, regimes


def _existing_rows() -> tuple[dict[str, list[dict]], set[str]]:
    """What the store already holds, IN RAW TERMS, so a rebuild resumes rather than restarts.

    THE EXACT INVERSE OF `_write`, and it has to be. The file on disk is keyed by REGIME and its
    temperature columns are anomalies about each cell's `level_c`; reading that key as a cell id
    is what made every held cell look missing, so a resume re-pulled all 156 and the rewrite
    would have carried regime ids and cell ids in one column.
    """
    import csv as _csv

    if not SERIES_PATH.is_file():
        return {}, set()

    stored_cells, regimes = _stored_geometry()
    cell_of_regime = {regime: cell for cell, regime in regimes.items()}

    rows: dict[str, list[dict]] = {}
    unknown: set[str] = set()
    with gzip.open(SERIES_PATH, "rt", newline="", encoding="utf-8") as handle:
        for row in _csv.DictReader(handle):
            key = row["cell_id"]
            # No regime map at all means the identity one: every key IS a cell. That is the shape
            # a store written before `regimes.json` existed has, and it round-trips unchanged.
            if regimes and key not in cell_of_regime:
                unknown.add(key)
                continue
            cell = cell_of_regime.get(key, key)
            level = float(stored_cells.get(cell, {}).get("level_c", 0.0) or 0.0)
            raw = {"cell_id": cell, "date": row["date"]}
            for field in FIELDS:
                value = row.get(field, "")
                if value in ("", None):
                    raw[field] = ""
                elif field in LEVELLED:
                    raw[field] = round(float(value) + level, 3)
                else:
                    raw[field] = value
            rows.setdefault(cell, []).append(raw)

    if unknown:
        # NAMED, not swallowed. A key the regime map does not know is a store whose three files
        # disagree, and continuing would drop those rows on the next write.
        raise WeatherWorldRefusal(
            f"{SERIES_PATH} holds {len(unknown)} key(s) absent from {REGIMES_PATH.name} "
            f"({sorted(unknown)[:5]}...): the store's files disagree and a rebuild would silently "
            "discard those rows. Reconcile them before rebuilding.")
    return rows, set(rows)


ERA5_FIELDS = tuple(f for f in FIELDS if f not in LEVELLED)


def _has_era5(rows: list[dict]) -> bool:
    """Whether a cell's rows already carry the three ERA5 columns.

    Asked instead of "does this cell have any rows at all", because the temperature pass creates
    rows for every cell before a single archive is fetched. Under the old question every cell
    would read as done the moment temperature landed, and the network pull would never run.
    """
    return any(r.get(f) not in ("", None) for r in rows for f in ERA5_FIELDS)


def overlay_temperature(cells: dict[str, dict], rows: dict[str, list[dict]],
                        progress=print) -> dict:
    """Put HadUK 1 km daily temperature into `rows`, creating cell-days that do not exist yet.

    RUN BEFORE THE ARCHIVE PULL, not after, and the ordering is the store's honesty rather than a
    performance choice. It is local and needs no network, so running it first means an interrupted
    build leaves temperature complete and the ERA5 columns partial -- which is a store that tells
    the truth about itself. The other order leaves cells holding ERA5 temperature under a
    `cells.json` that names HadUK as the source.
    """
    derived = extract_temperature(cells, progress=progress)
    by_date = {cell: {r["date"]: r for r in rows.get(cell, [])} for cell in derived}
    written = 0
    for cell, days in derived.items():
        index = by_date[cell]
        for date, values in sorted(days.items()):
            row = index.get(date)
            if row is None:
                row = {"cell_id": cell, "date": date, **{f: "" for f in FIELDS}}
                index[date] = row
                rows.setdefault(cell, []).append(row)
            for field in LEVELLED:
                if field in values:
                    row[field] = values[field]
                    written += 1
    progress(f"  HadUK temperature: {written} value(s) over {len(derived)} cell(s)")
    return {"cells": len(derived), "values": written}


def build(limit: int | None = None, pause: float = PAUSE_SECONDS, progress=print,
          temperature: bool = True) -> dict:
    """Bring the store up to date and rewrite it. Idempotent.

    Two passes over two sources, in the order that keeps the store honest if it is interrupted:
    HadUK temperature from the local grids first, then the ERA5 archive for the cells whose
    wind/cloud/precipitation are still missing.
    """
    from sim.weather_ingestor import get_daily_weather

    STORE_DIR.mkdir(parents=True, exist_ok=True)
    cells = book_cells()
    held, _ = _existing_rows()
    stored_cells, _ = _stored_geometry()
    # The temperature pass covers the UNION, so a cell that has left the book keeps a current
    # temperature series rather than freezing at whatever it held the day it left.
    known = {**stored_cells, **cells}

    if temperature:
        overlay_temperature(known, held, progress=progress)

    todo = [c for c in cells.values() if not _has_era5(held.get(c["cell_id"], []))]
    if limit is not None:
        todo = todo[:limit]
    progress(f"{len(cells)} cell(s) in the book; {len(held)} held; "
             f"{len(todo)} still needing the ERA5 archive")

    refused = []
    for index, cell in enumerate(todo, start=1):
        key = cell["cell_id"]
        try:
            records = _fetch_with_backoff(
                get_daily_weather, key, cell["latitude"], cell["longitude"],
                START_DATE, END_DATE, progress)
        except Exception as exc:  # noqa: BLE001 -- recorded, not swallowed
            refused.append({"cell_id": key, "reason": str(exc)[:200]})
            progress(f"  [{index}/{len(todo)}] {key} REFUSED: {str(exc)[:110]}")
            continue
        # ONLY THE THREE ERA5 COLUMNS ARE TAKEN. `get_daily_weather` also returns temperature and
        # it is dropped on purpose: the store's temperature is HadUK, and letting the archive fill
        # it for whichever cells happened to be pulled would put a source seam between cells.
        index_by_date = {r["date"]: r for r in held.get(key, [])}
        for record in records:
            row = index_by_date.get(record["date"])
            if row is None:
                row = {"cell_id": key, "date": record["date"], **{f: "" for f in FIELDS}}
                index_by_date[record["date"]] = row
                held.setdefault(key, []).append(row)
            for field in ERA5_FIELDS:
                row[field] = record.get(field, "")
        progress(f"  [{index}/{len(todo)}] {key} {len(records)} days "
                 f"({cell['latitude']:.3f},{cell['longitude']:.3f})")
        _write(known, held)          # after every cell, so an interruption keeps what it got
        time.sleep(pause)

    written = _write(known, held)
    return {"cells": len(cells), "held": len(held), "refused": refused, **written}


SOURCE_LINE = ("temperature: HadUK-Grid 1 km daily (CEDA). "
               "wind/cloud/precip: ERA5 via Open-Meteo, per cell centre.")
DECOMPOSITION_LINE = "per-cell LEVEL + shared regime ANOMALY; see sim/weather_world.py"


def level_of(rows: list[dict]) -> float:
    """A cell's own climatology: the mean of its daily mean temperature over the window.

    ONE SCALAR PER CELL is the whole economy of the decomposition -- it keeps what the 1 km pull
    bought (the urban heat island, worth +1.2 C at London against a ~9 km reanalysis) for 156
    numbers rather than 156 series.

    Returns 0.0 when the cell has no temperature at all, which is not a climatology of zero: it
    is a cell whose series is wind/cloud/precip only, and adding 0.0 back on read returns exactly
    the empty columns that went in.
    """
    values = [float(r["temperature_mean_c"]) for r in rows
              if r.get("temperature_mean_c") not in ("", None)]
    if not values:
        return 0.0
    return round(sum(values) / len(values), 3)


def _write(cells: dict[str, dict], rows: dict[str, list[dict]]) -> dict:
    """Write the three artefacts that make up the store, from RAW rows.

    The decomposition lives here and nowhere else, so `_existing_rows` can invert it exactly.
    """
    import csv as _csv

    stored_cells, _ = _stored_geometry()
    # UNION, not the book. A cell that has left the book keeps its rows and its centre: the centre
    # is recorded nowhere else, the rows cost a real pull, and dropping them to match today's book
    # would make the store unable to answer for a premise the book still held last week.
    known = {**stored_cells, **cells}
    held = sorted(k for k in rows if k in known)
    orphans = sorted(k for k in rows if k not in known)

    regime_of_cell = {cell: f"R{index:02d}" for index, cell in enumerate(held)}
    levels = {cell: level_of(rows[cell]) for cell in held}

    STORE_DIR.mkdir(parents=True, exist_ok=True)
    CELLS_PATH.write_text(
        json.dumps({"source": SOURCE_LINE,
                    "window": [START_DATE, END_DATE],
                    "decomposition": DECOMPOSITION_LINE,
                    "cells": {k: {**known[k], "level_c": levels[k]} for k in held}},
                   indent=1) + "\n",
        encoding="utf-8")
    REGIMES_PATH.write_text(
        json.dumps({"k": len(regime_of_cell),
                    # WHAT THIS BUILD DID, not a clustering result it did not run. The store found
                    # on disk carried "20 regimes reproduce annual space heat to 0.10% mean" here
                    # -- a real measurement of a 20-regime GENERATOR, and nothing in this tree
                    # produces it. Writing that sentence from a build that clustered nothing would
                    # put an unattributable number where the reader expects this build's own.
                    "measured": (f"identity: {len(regime_of_cell)} regime(s) for "
                                 f"{len(regime_of_cell)} cell(s), one-to-one. Replayed weather, "
                                 "so no cell's daily anomaly is shared with another's."),
                    "regime_of_cell": regime_of_cell},
                   indent=1) + "\n",
        encoding="utf-8")
    with gzip.open(SERIES_PATH, "wt", newline="", encoding="utf-8") as handle:
        writer = _csv.DictWriter(handle, fieldnames=("cell_id", "date", *FIELDS))
        writer.writeheader()
        # BY REGIME ID, LEXICOGRAPHICALLY -- R00, R01, ... R10, R100, R101, ... R11. Not the
        # numeric order and not the cell order, which both read more naturally and neither of
        # which is what the store on disk holds. The file is keyed by regime, so the natural
        # `sorted()` over that key is what produced it; writing cell order instead moves 529,685
        # of the 569,868 rows and makes a byte-comparison against the existing artefact useless.
        for cell in sorted(held, key=lambda c: regime_of_cell[c]):
            level = levels[cell]
            for row in sorted(rows[cell], key=lambda r: r["date"]):
                out = {"cell_id": regime_of_cell[cell], "date": row["date"]}
                for field in FIELDS:
                    value = row.get(field, "")
                    if value in ("", None):
                        out[field] = ""
                    elif field in LEVELLED:
                        # `+ 0.0` NORMALISES THE SIGNED ZERO, and the 55 values it touches are
                        # measured rather than guessed. The store built 2026-09-09 holds the text
                        # `-0.0` at 55 of its 569,868 rows; re-deriving those cell-days from the
                        # HadUK grids and differencing at 3 dp yields `0.0`, so the producer
                        # reached the zero from below by an arithmetic route this one does not
                        # take. `-0.0 == 0.0` is True and `float()` erases the distinction before
                        # any consumer sees it, so this is a difference in TEXT and not in the
                        # world -- but it is the whole of what stops the rebuilt series being
                        # byte-identical, and a reader comparing files deserves to be told which
                        # of the two forms this writer emits.
                        out[field] = round(float(value) - level, 3) + 0.0
                    else:
                        out[field] = value
                writer.writerow(out)
    return {"cells": len(held), "regimes": len(regime_of_cell), "orphans": orphans}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--list", action="store_true", help="the cells, without fetching")
    parser.add_argument("--build", action="store_true", help="bring the store up to date")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--pause", type=float, default=PAUSE_SECONDS)
    parser.add_argument("--no-temperature", action="store_true",
                        help="skip the HadUK pass (the ERA5 archive only)")
    args = parser.parse_args(argv)

    if args.list:
        cells = book_cells()
        held, have = _existing_rows()
        stored_cells, _ = _stored_geometry()
        era5 = sum(1 for k in have if _has_era5(held[k]))
        left = sorted(set(stored_cells) - set(cells))
        print(f"{len(cells)} cell(s) the book occupies; {len(have)} in the store "
              f"({era5} with the ERA5 archive, {len(have) - era5} temperature-only)")
        # THE BOOK MOVES AND THE STORE DOES NOT FOLLOW IT SILENTLY. On 2026-09-16 the store held
        # 156 cells and the book wanted 149, sharing only 84 -- so a store that looked complete
        # was missing 65 of the cells the book actually occupies.
        print(f"{len(set(cells) - set(stored_cells))} book cell(s) the store has never held; "
              f"{len(left)} stored cell(s) the book no longer occupies (kept, not dropped)")
        for cell in list(cells.values())[:10]:
            print(f"  {cell['cell_id']}  ({cell['latitude']:.3f},{cell['longitude']:.3f})")
        if len(cells) > 10:
            print(f"  ... and {len(cells) - 10} more")
        return 0
    if args.build:
        result = build(limit=args.limit, pause=args.pause,
                       temperature=not args.no_temperature)
        print(f"cells held {result['held']}/{result['cells']}, "
              f"regimes {result['regimes']}, refused {len(result['refused'])}")
        return 1 if result["refused"] else 0
    parser.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
