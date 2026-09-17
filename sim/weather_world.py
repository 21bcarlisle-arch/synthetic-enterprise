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
import gzip
import json
import math
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


def load_regimes(path: Path = REGIMES_PATH) -> dict[str, str]:
    """{cell_id: regime_id}. Absent means the identity map -- every cell is its own regime, which
    is what REPLAYED weather is."""
    if not path.is_file():
        return {}
    return dict(json.loads(path.read_text(encoding="utf-8"))["regime_of_cell"])


class WeatherWorld:
    """The store, loaded once. `for_cell` is a dictionary lookup, never a fetch."""

    def __init__(self, cells: dict[str, Cell], daily: dict[str, dict[str, dict[str, float]]],
                 regime_of_cell: dict[str, str] | None = None):
        self.cells = cells
        # KEYED BY REGIME, NOT BY CELL. Under replay there is one regime per cell and the map is
        # the identity, so this is invisible; under generation there are tens of regimes and
        # hundreds of thousands of cells, and only this line makes that expressible.
        self.daily = daily
        self.regime_of_cell = regime_of_cell or {}
        # Snapping needs the cell centres as flat arrays; built once here rather than per lookup.
        self._ids = list(cells)
        self._lats = [cells[c].latitude for c in self._ids]
        self._lons = [cells[c].longitude for c in self._ids]

    @classmethod
    def load(cls) -> "WeatherWorld":
        return cls(load_cells(), load_daily(), load_regimes())

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
        dates = sorted(series)
        if start:
            dates = [d for d in dates if d >= start]
        if end:
            dates = [d for d in dates if d <= end]
        # THE LEVEL IS ADDED BACK HERE. The stored series is the regime's daily ANOMALY, shared by
        # every cell that reads it; the cell's own climatology is what makes two cells in one
        # regime different. Returning the stored value raw would hand every caller a temperature
        # centred on zero -- correct-looking, and about eleven degrees wrong.
        offset = self.cells[cell].level_c if cell in self.cells else 0.0
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


