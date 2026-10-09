"""The world's weather, keyed by CELL. Every property reads it; no property fetches it.

REUSE: sim/weather_world.py
CLASS: CUSTOM
INDEX: searched "weather store", "weather cell", "per cell weather", "shared weather", "grid".
       `sim/weather_ingestor.py` FETCHES a daily series for one coordinate and is used here rather
       than re-implemented. `simulation/weather_cell_siting.py` answers whether two PLACES share a
       cell on the heat-load drivers -- a different question, about substitutability of the four
       archive sites, and it is not a store. `tools/weather_cell_drivers.py` reads the HadUK
       NORMALS (a 30-year monthly climatology) and cannot produce a daily series.
       **Nothing held the world's daily weather keyed by anything but a customer id.**

WHY THIS EXISTS, AND WHY THE THING IT REPLACES WAS WRONG
--------------------------------------------------------
The book settles 4 of 146 premises on fabric physics; 137 of the 142 refusals are "no weather
archive for this customer's location". The obvious fix -- and the one I built first -- was to pull
a daily archive per property. The director refused it, and the refusal is architectural rather than
about speed:

    "The world exists, and a property reads its conditions from it. It doesn't call out to a data
     source when someone wants to bill it. The weather happened; everyone in that place experienced
     the same weather... Two households in the same cell must experience identical weather -- that's
     what makes the difference in their demand attributable to fabric and people rather than to two
     separate downloads."

**The argument is one number: of the book's 257 located accounts, 101 share a 1 km cell with
another account.** Under a per-property pull those 101 get a second download of a sky someone else
already has, and any difference between the two series is then indistinguishable from a difference
in fabric or people. The filenames gave it away -- `PROS-2019-0164.csv` is weather keyed by who
lives there.

And the synchrony result depends on it too: cold arriving across Britain in five-day blocks is a
property of ONE shared world. Thousands of independently-fetched series that happen to correlate
would reproduce the statistic while destroying the thing it is evidence of.

THE CELL IS THE PROJECT'S EXISTING ONE
---------------------------------------
A one-kilometre OSGB cell, indexed `(easting // 1000, northing // 1000)` -- the same key
`demand_case_coverage.demand_grid` and `weather_cell_weights` already join on, so a cell here is
the cell every other measurement in this repo means. It is derived from the HadUK-Grid geometry
rather than invented, and `cell_id_for` snaps a coordinate to the nearest land cell centre.

WHAT IS IN THE STORE AND WHERE IT COMES FROM
---------------------------------------------
One row per (regime, date): min/mean/max temperature, wind speed, cloud cover and precipitation.
**Temperature is HadUK-Grid 1 km daily. Wind, cloud and precipitation are ERA5 via Open-Meteo,
pulled ONCE PER CELL at the cell's own centre.**

CORRECTED 2026-09-16, BESIDE THE CLAIM RATHER THAN OVER IT. Until that date this paragraph said
the opposite -- that every variable including temperature came from ERA5, and that HadUK was only
a check -- and `tools/build_weather_world.py` said the same. The store's own `cells.json` had
named HadUK as the temperature source since the day it was built. The reason both docstrings gave
was specific and checkable:

    "HadUK-Grid has daily 1 km temperature already on this machine, but only for October-March
     (`fetch_haduk_grid.HEATING_SEASON_MONTHS`). Taking winter temperature from HadUK and summer
     from ERA5 would put a source discontinuity INSIDE one variable, at precisely the shoulder
     months where heating switches on -- a seam that would read as physics."

**It is false of this machine, by counting.** `tasmin`, `tas` and `tasmax` each hold 120 monthly
1 km daily grids under `~/.cache/synthetic-enterprise/haduk_grid/` -- 2016-01 through 2025-12,
twelve months of every year. October-March is the window `fetch_haduk_grid` PULLS for the
heating-season product; it was never a limit on what CEDA serves, and the full year was already
here. There is no shoulder seam to avoid, so the choice was simply between a 1 km observational
analysis and a ~9 km reanalysis, and `Cell.level_c` below is the measurement that settles it.

That temperature half is reproducible and the claim is measured, not asserted:
`tools/validate_weather_world.py` re-derives all 1,709,604 stored temperature values from those
grids and they agree exactly. The ERA5 half is a network pull and cannot be re-derived offline,
which that module says on its face rather than implying a coverage it does not have.
"""
from __future__ import annotations

import csv
import datetime as dt
import gzip
import hashlib
import json
import math
from array import array
from bisect import bisect_left, bisect_right
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

#: The store lives in the repo, unlike the raw grids. It is derived, small (one row per cell-day
#: for the cells the book occupies, gzipped) and the simulation cannot run without it -- the
#: weather-cells ruling forbids the multi-GB SOURCE grids, not a compact derived artefact.
STORE_DIR = PROJECT / "sim" / "weather_world"
CELLS_PATH = STORE_DIR / "cells.json"
SERIES_PATH = STORE_DIR / "daily.csv.gz"

#: WHICH REGIME EACH CELL READS. The indirection is the whole future-proofing of this store and it
#: costs one dictionary today.
#:
#: THE PROBLEM IT AVOIDS, ASKED BY THE DIRECTOR BEFORE IT BIT: while weather is REPLAYED, a cell is
#: an index into a file and a series per cell is fine. The moment weather is GENERATED, nobody can
#: produce 245,077 correlated 1 km series -- a generator makes a small number of coherent regimes
#: with the right spatial correlation and synchrony, and every household reads its regime. A store
#: shaped `cell -> series` forecloses that; a store shaped `cell -> regime -> series` does not, and
#: the two are indistinguishable from the outside.
#:
#: MEASURED, so the small number is not a guess. Over the real 1 km daily field for Jan-Mar 2022
#: (245,077 land cells, 90 days): 54.2% of all day-to-day variance is ONE national number, and the
#: spatial remainder needs 3 patterns for 90% of variance, 5 for 95%, 21 for 99%. Twenty regimes
#: reproduce every cell's daily anomaly to 0.48 C mean / 1.24 C worst. Britain's weather field is
#: about five-dimensional; the 245,077 is the resolution of the FILE, not the variety of the sky.
REGIMES_PATH = STORE_DIR / "regimes.json"

#: How far a coordinate may be snapped before the store refuses. One cell is 1 km, so 5 km allows
#: for a premise just outside the built set while refusing a silent cross-country substitution.
MAX_SNAP_KM = 5.0

FIELDS = (
    "temperature_min_c",
    "temperature_max_c",
    "temperature_mean_c",
    "wind_speed_mean_ms",
    "cloud_cover_pct",
    "precipitation_mm",
)


class WeatherWorldRefusal(RuntimeError):
    """The store cannot answer, with the reason named.

    A distinct type because the callers want opposite things: a build script must stop, and a
    settlement path must be able to say WHICH cell it could not read rather than silently
    substituting a national average -- which is the failure this whole module exists to end.
    """


@dataclass(frozen=True)
class Cell:
    """One 1 km OSGB cell: its key, its centre, and the grid indices it came from."""

    cell_id: str
    east_km: int
    north_km: int
    latitude: float
    longitude: float
    #: THE CELL'S OWN CLIMATOLOGY, and the reason a 1 km product was worth pulling at all. HadUK
    #: reads +1.2 C warmer than ERA5 at London, Manchester and Glasgow and -0.55 C at the rural
    #: site: that is the urban heat island, which a ~9-31 km reanalysis cannot resolve. It is a
    #: SCALAR per cell, so keeping it costs 156 numbers rather than 156 series.
    level_c: float = 0.0

    @property
    def centre(self) -> tuple[float, float]:
        return (self.latitude, self.longitude)


def cell_id(east_km: int, north_km: int) -> str:
    """The key. Readable on purpose -- a cell id in a log should say where it is."""
    return f"E{int(east_km):03d}N{int(north_km):04d}"


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance. Used only to report how far a snap moved a point."""
    radius = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    return 2 * radius * math.asin(math.sqrt(a))


def load_cells(path: Path = CELLS_PATH) -> dict[str, Cell]:
    """Every cell the store holds."""
    if not path.is_file():
        raise WeatherWorldRefusal(
            f"{path} is absent: the world has no weather. Build it with "
            "`python3 -m tools.build_weather_world --build`.")
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {k: Cell(**v) for k, v in raw["cells"].items()}


def load_daily(path: Path = SERIES_PATH) -> dict[str, dict[str, dict[str, float]]]:
    """{cell_id: {date: {field: value}}} for the whole store.

    Read ONCE by a caller and shared, which is the point: the alternative -- a read per premise --
    is the per-property architecture wearing a different coat.

    `WeatherWorld.load` no longer calls this (it reads `load_columns`, ~11x smaller resident).
    It stays as the row-shaped reader and as the ORACLE the columnar one is held to, value by
    value, in `tests/sim/test_the_weather_world_is_columnar_and_reads_the_same_values.py`.
    """
    if not path.is_file():
        raise WeatherWorldRefusal(
            f"{path} is absent: the world has no weather. Build it with "
            "`python3 -m tools.build_weather_world --build`.")
    out: dict[str, dict[str, dict[str, float]]] = {}
    with gzip.open(path, "rt", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            values = {}
            for field in FIELDS:
                raw = row.get(field, "")
                values[field] = float(raw) if raw not in ("", None) else float("nan")
            out.setdefault(row["cell_id"], {})[row["date"]] = values
    if not out:
        raise WeatherWorldRefusal(f"{path} holds no rows")
    return out


class DailyColumns(Mapping):
    """One regime's days held COLUMNAR: a date index shared by every regime, one `array('d')` per
    field. Reads as `{date: {field: value}}`, which is what `load_daily` returns and every caller
    was written against.

    WHY (director, 2026-10-09: "the weather world is now the biggest memory holder"). As a dict of
    row dicts the store was 1,245,673 rows x (a 272-byte dict + six 24-byte float objects + a slot
    in the per-regime dict), ~540 bytes a row and ~674 MB resident for values that are 7.5 million
    float64s -- 60 MB of numbers. Here a value is its 8 bytes, and the 3,653 date strings exist
    once for the whole world rather than once per regime.

    NO VALUE CHANGES. `array('d')` stores an IEEE double and returns the same double, so a row read
    through this view equals the row `load_daily` builds, NaN included. Iteration is ASCENDING by
    date (the committed store's file order too); `for_cell` sorts either way.
    """

    __slots__ = ("dates", "index", "fields", "cols")

    def __init__(self, dates: tuple[str, ...], index: dict[str, int], fields: tuple[str, ...],
                 cols: dict[str, array]):
        self.dates, self.index, self.fields, self.cols = dates, index, fields, cols

    def __getitem__(self, date: str) -> dict[str, float]:
        i = self.index[date]
        return {f: self.cols[f][i] for f in self.fields}

    def __contains__(self, date) -> bool:
        return date in self.index

    def __iter__(self):
        return iter(self.dates)

    def __len__(self) -> int:
        return len(self.dates)


class _SharedIndex:
    """Interns date indices, so regimes on the same days share ONE tuple and ONE position dict."""

    def __init__(self):
        self._seen: dict[tuple[str, ...], tuple[tuple[str, ...], dict[str, int]]] = {}

    def __call__(self, dates: tuple[str, ...]) -> tuple[tuple[str, ...], dict[str, int]]:
        hit = self._seen.get(dates)
        if hit is None:
            hit = self._seen[dates] = (dates, {d: i for i, d in enumerate(dates)})
        return hit


def _as_columns(series, shared: _SharedIndex):
    """`series` as `DailyColumns` when that is EXACTLY representable, else `series` untouched.

    Exactly representable means every row carries the same fields in the same order and every
    value is a Python float. A hand-built fixture with an int, a missing field or a row of its own
    shape stays the dict it was handed, so no value is ever coerced and no key is ever invented.
    """
    if isinstance(series, DailyColumns) or not isinstance(series, dict) or not series:
        return series
    dates = tuple(sorted(series))
    fields = tuple(series[dates[0]]) if isinstance(series[dates[0]], dict) else None
    if fields is None:
        return series
    cols = {f: array("d") for f in fields}
    for d in dates:
        row = series[d]
        if not isinstance(row, dict) or tuple(row) != fields:
            return series
        for f in fields:
            value = row[f]
            if type(value) is not float:
                return series
            cols[f].append(value)
    dates, index = shared(dates)
    return DailyColumns(dates, index, fields, cols)


def load_columns(path: Path = SERIES_PATH) -> dict[str, DailyColumns]:
    """`load_daily`, columnar: the same values, never materialised as row dicts.

    Parsed straight into the arrays, so the load itself never holds the dict-of-rows form either.
    The file's rules are `load_daily`'s exactly: an empty or absent column is NaN, and a (cell,
    date) that appears twice keeps its LAST row, as `setdefault(...)[date] = values` did.
    """
    if not path.is_file():
        raise WeatherWorldRefusal(
            f"{path} is absent: the world has no weather. Build it with "
            "`python3 -m tools.build_weather_world --build`.")
    nan = float("nan")
    # ONE string per date for the whole store. A fresh string per row would be 1.2 million objects
    # freed after the load, scattered between the survivors -- measured as ~160 MB of RSS the
    # allocator kept after a load whose live data is ~60 MB.
    canon: dict[str, str] = {}
    raw: dict[str, tuple[list[str], dict[str, array]]] = {}
    in_order: set[str] = set()
    with gzip.open(path, "rt", newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header = next(reader, None) or []
        at = {name: i for i, name in enumerate(header)}
        cell_at, date_at = at["cell_id"], at["date"]
        field_at = [(f, at.get(f)) for f in FIELDS]
        width = len(header)
        for line in reader:
            if len(line) < width:
                # DictReader fills a short row with None, which load_daily reads as NaN.
                line = line + [""] * (width - len(line))
            cell = line[cell_at]
            entry = raw.get(cell)
            if entry is None:
                entry = raw[cell] = ([], {f: array("d") for f in FIELDS})
                in_order.add(cell)
            dates, cols = entry
            date = canon.setdefault(line[date_at], line[date_at])
            if dates and date <= dates[-1]:
                in_order.discard(cell)       # out of order or repeated: settled below
            dates.append(date)
            for f, i in field_at:
                cols[f].append(float(line[i]) if i is not None and line[i] != "" else nan)
    if not raw:
        raise WeatherWorldRefusal(f"{path} holds no rows")
    shared = _SharedIndex()
    out: dict[str, DailyColumns] = {}
    for cell, (dates, cols) in raw.items():
        if cell not in in_order:
            # load_daily's dict semantics: sorted on read, and the LAST row for a date wins.
            last = {d: i for i, d in enumerate(dates)}
            order = [last[d] for d in sorted(last)]
            dates = [dates[i] for i in order]
            cols = {f: array("d", (col[i] for i in order)) for f, col in cols.items()}
        ordered, index = shared(tuple(dates))
        out[cell] = DailyColumns(ordered, index, FIELDS, cols)
    return out


def load_regimes(path: Path = REGIMES_PATH) -> dict[str, str]:
    """{cell_id: regime_id}. Absent means the identity map -- every cell is its own regime, which
    is what REPLAYED weather is."""
    if not path.is_file():
        return {}
    return dict(json.loads(path.read_text(encoding="utf-8"))["regime_of_cell"])


class WeatherWorld:
    """The store, loaded once. `for_cell` is a dictionary lookup, never a fetch."""

    def __init__(self, cells: dict[str, Cell], daily: dict[str, Mapping[str, dict[str, float]]],
                 regime_of_cell: dict[str, str] | None = None):
        self.cells = cells
        # KEYED BY REGIME, NOT BY CELL. Under replay there is one regime per cell and the map is
        # the identity, so this is invisible; under generation there are tens of regimes and
        # hundreds of thousands of cells, and only this line makes that expressible.
        # Held COLUMNAR wherever that is exact (`DailyColumns`); a series of any other shape is
        # kept as handed. Either reads as `{date: {field: value}}`.
        shared = _SharedIndex()
        self.daily = {regime: _as_columns(series, shared) for regime, series in daily.items()}
        self.regime_of_cell = regime_of_cell or {}
        # Snapping needs the cell centres as flat arrays; built once here rather than per lookup.
        self._ids = list(cells)
        self._lats = [cells[c].latitude for c in self._ids]
        self._lons = [cells[c].longitude for c in self._ids]

    @classmethod
    def load(cls) -> "WeatherWorld":
        return cls(load_cells(), load_columns(), load_regimes())

    def regime_for(self, cell: str) -> str:
        """The regime a cell reads. Identity under replay; many-to-one under generation."""
        return self.regime_of_cell.get(cell, cell)

    def cell_id_for(self, latitude: float, longitude: float) -> str:
        """The cell a coordinate falls in — the NEAREST cell the store holds.

        REFUSES rather than guessing when the nearest held cell is far away. A silent snap across
        fifty kilometres would give a Cornish premise Birmingham's weather and read as a hit.
        """
        if not self._ids:
            raise WeatherWorldRefusal("the store holds no cells")
        best, best_km = None, float("inf")
        for cid, lat, lon in zip(self._ids, self._lats, self._lons):
            km = _haversine_km(latitude, longitude, lat, lon)
            if km < best_km:
                best, best_km = cid, km
        if best_km > MAX_SNAP_KM:
            raise WeatherWorldRefusal(
                f"({latitude:.4f},{longitude:.4f}) is {best_km:.1f} km from the nearest cell the "
                f"store holds ({best}). The store covers the cells the book occupies; a premise "
                "outside them needs its cell adding, not the nearest one substituting.")
        return best

    def for_cell(self, cell: str, start: str | None = None, end: str | None = None) -> list[dict]:
        """The cell's daily record, ascending by date. A LOOKUP -- everyone in the cell gets the
        identical list, which is the whole property this module exists to guarantee."""
        regime = self.regime_for(cell)
        series = self.daily.get(regime)
        if series is None:
            raise WeatherWorldRefusal(
                f"the store holds no weather for cell {cell!r} (regime {regime!r})")
        # THE LEVEL IS ADDED BACK HERE. The stored series is the regime's daily ANOMALY, shared by
        # every cell that reads it; the cell's own climatology is what makes two cells in one
        # regime different. Returning the stored value raw would hand every caller a temperature
        # centred on zero -- correct-looking, and about eleven degrees wrong.
        offset = self.cells[cell].level_c if cell in self.cells else 0.0
        if isinstance(series, DailyColumns):
            return _rows_from_columns(series, start, end, offset)
        dates = sorted(series)
        if start:
            dates = [d for d in dates if d >= start]
        if end:
            dates = [d for d in dates if d <= end]
        out = []
        for d in dates:
            row = dict(series[d])
            for field in ("temperature_min_c", "temperature_mean_c", "temperature_max_c"):
                if field in row and row[field] == row[field]:      # not NaN
                    row[field] = round(row[field] + offset, 3)
            out.append(dict(date=d, **row))
        return out

    def for_location(self, latitude: float, longitude: float, **kw) -> list[dict]:
        return self.for_cell(self.cell_id_for(latitude, longitude), **kw)

    def record_end(self) -> str:
        """The last date the store holds, across every regime."""
        return max(max(series) for series in self.daily.values())

    def extended_by_analogue_years(self, through: str, seed: str) -> "WeatherWorld":
        """This world, with the days after its record filled from ANALOGUE YEARS through `through`.

        Past the record there is no weather to replay, and the run still needs some. Each forward
        calendar year replays ONE complete year of the record, the SAME year in every regime, so
        the spatial structure between regimes and the seasonal shape within a year are the
        record's own, exactly; nothing is fitted. The year is drawn from the complete years the
        store holds, deterministically from `(seed, year)`, so a re-run lives through the same
        weather.

        A NAMED SIMPLIFICATION, and the error runs one known way: analogue weather is independent of
        the synthetic wholesale series it sits beside, so a cold year no longer moves the price the
        way 2021-22 did. That coupling is the price generator's to model; this does not pretend to.
        29 February is read from the analogue year's 28 February when that year is not a leap year.
        The record itself is never altered. Which record year each forward year replays is on
        `analogue_years`, so a run can say what weather it lived through.
        """
        end = dt.date.fromisoformat(self.record_end())
        stop = dt.date.fromisoformat(through)
        if stop <= end:
            return self
        complete = sorted({int(d[:4]) for series in self.daily.values() for d in series
                           if d.endswith("-12-31")} & {int(d[:4]) for series in self.daily.values()
                                                        for d in series if d.endswith("-01-01")})
        if not complete:
            raise WeatherWorldRefusal("the store holds no complete year to draw an analogue from")
        # A SEEDED PERMUTATION of the complete years, taken in turn, so no record year repeats until
        # every one has been used -- drawing each forward year independently repeated 2021 and 2016
        # inside four years on the first seed tried.
        order = sorted(complete, key=lambda y: hashlib.sha256(f"{seed}:{y}".encode()).hexdigest())
        day = end + dt.timedelta(days=1)
        analogue_of: dict[int, int] = {}
        forward_days: list[tuple[str, str]] = []
        while day <= stop:
            year = analogue_of.setdefault(day.year, order[len(analogue_of) % len(order)])
            try:
                source = day.replace(year=year)
            except ValueError:
                source = dt.date(year, 2, 28)
            forward_days.append((day.isoformat(), source.isoformat()))
            day += dt.timedelta(days=1)
        held = list(self.daily.values())
        if all(isinstance(s, DailyColumns) and s.dates is held[0].dates for s in held):
            # COLUMNAR, every regime on ONE index: a forward day exists in all of them or in none,
            # so the extended index is shared too and each column is the record plus a gather.
            kept = [(key, held[0].index[src]) for key, src in forward_days
                    if src in held[0].index]
            dates = held[0].dates + tuple(key for key, _ in kept)
            index = {d: i for i, d in enumerate(dates)}
            daily = {}
            for regime, series in self.daily.items():
                cols = {}
                for f, col in series.cols.items():
                    grown = array("d", col)
                    grown.extend(col[i] for _, i in kept)
                    cols[f] = grown
                daily[regime] = DailyColumns(dates, index, series.fields, cols)
        else:
            daily = {regime: dict(series) for regime, series in self.daily.items()}
            for key, src in forward_days:
                for regime, series in daily.items():
                    row = self.daily[regime].get(src)
                    if row is not None:
                        series[key] = dict(row)
        forward = WeatherWorld(self.cells, daily, self.regime_of_cell)
        forward.analogue_years = dict(sorted(analogue_of.items()))
        return forward




_TEMPERATURE_FIELDS = ("temperature_min_c", "temperature_mean_c", "temperature_max_c")


def _rows_from_columns(series: DailyColumns, start: str | None, end: str | None,
                       offset: float) -> list[dict]:
    """`for_cell`'s rows from a columnar series: the same dicts, keys and values, in date order.

    `bisect` over the sorted index selects exactly the dates `d >= start` and `d <= end` keep, and
    the level is added back by the same expression on the same doubles.
    """
    dates = series.dates
    lo = bisect_left(dates, start) if start else 0
    hi = bisect_right(dates, end) if end else len(dates)
    cols = [(f, series.cols[f], f in _TEMPERATURE_FIELDS) for f in series.fields]
    out = []
    for i in range(lo, hi):
        row = {"date": dates[i]}
        for f, col, is_temperature in cols:
            value = col[i]
            if is_temperature and value == value:      # not NaN
                value = round(value + offset, 3)
            row[f] = value
        out.append(row)
    return out
