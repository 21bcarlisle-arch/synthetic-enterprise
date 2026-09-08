"""The three phase-1 heat-load drivers, per 1 km land cell, from the HadUK-Grid normals.

REUSE: tools/weather_cell_drivers.py
CLASS: CUSTOM
INDEX: searched "haduk", "normals", "weather cell", "driver", "land mask", "netcdf".
       `tools/fetch_haduk_grid.py` PULLS the archive and validates the files; it opens none of them
       for content. `simulation/weather_*.py` consume a time series for a single modelled location,
       not a national grid. Nothing reads the normals.

WHY THIS EXISTS
---------------
`W1_19` measured these driver ranges and correlations and published them, and the measurement lived
in a shell session that is now gone. A published correlation table with nothing that reproduces it
is a claim nobody can open -- and `W1_21` has to stand on these arrays, not on the document's prose.

THE LAND MASK IS THE WHOLE POINT OF THE LOADER. The grid is 1450 x 900 = 1,305,000 cells and only
245,077 of them are land; the rest are NaN. A mean taken over the full array is a mean over the
Atlantic, and every figure derived from one would be wrong in a way that looks entirely plausible.
`land_mask()` is therefore computed once, from the intersection of the three variables, and every
driver is returned already flattened to it.

WHAT THE DRIVERS ARE, AND ONE THING THEY ARE NOT
------------------------------------------------
Annual mean temperature, winter (DJF) mean temperature, annual mean wind speed, annual sunshine
duration. Sunshine is a DURATION in hours, not irradiance: HadUK publishes no irradiance product,
and converting one to the other is a Choice the weather ruling requires to be registered with its
alternative named. It is not made here.
"""
from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

CACHE = Path.home() / ".cache" / "synthetic-enterprise" / "haduk_grid"

#: The 30-year normals, one file per variable. December-January-February are months 12, 1, 2 in the
#: file's own time axis, which runs January..December.
NORMALS = {"tas": "tas", "sfcWind": "sfcWind", "sun": "sun"}
WINTER_MONTHS = (11, 0, 1)      # zero-based indices into a January-first axis

GRID_SHAPE = (1450, 900)        # y, x -- asserted, because a silent reshape would move every cell
EXPECTED_LAND_CELLS = 245_077


def _normals_path(variable: str) -> Path:
    hits = sorted(glob.glob(str(CACHE / variable / "mon-30y" / "*.nc")))
    if not hits:
        raise FileNotFoundError(
            f"no 30-year normals for {variable!r} under {CACHE / variable / 'mon-30y'}. "
            "Run `python3 tools/fetch_haduk_grid.py --pull`.")
    return Path(hits[-1])


def _open(variable: str):
    import xarray as xr

    # h5netcdf, NOT netcdf4: the netCDF4 wheel is not installed in this environment and the
    # default engine's failure is an obscure ValueError about the file format rather than a
    # missing dependency.
    return xr.open_dataset(_normals_path(variable), engine="h5netcdf")


def _monthly(variable: str):
    """(months, y, x) array of the 30-year monthly normals for one variable."""
    with _open(variable) as ds:
        arr = ds[NORMALS[variable]].values
    if arr.shape[1:] != GRID_SHAPE:
        raise ValueError(f"{variable} grid is {arr.shape[1:]}, expected {GRID_SHAPE}")
    return arr


def drivers() -> dict:
    """The four driver arrays flattened to land cells, plus the cell coordinates.

    Returns eastings/northings in METRES at cell centres, so a cell index is `int(east // 1000)`
    and joins directly to `tools/weather_cell_weights`.
    """
    import numpy as np

    tas = _monthly("tas")
    wind = _monthly("sfcWind")
    sun = _monthly("sun")

    mask = ~(np.isnan(tas).any(axis=0) | np.isnan(wind).any(axis=0) | np.isnan(sun).any(axis=0))
    n = int(mask.sum())
    if n != EXPECTED_LAND_CELLS:
        raise ValueError(f"land mask holds {n} cells, expected {EXPECTED_LAND_CELLS}. The mask is "
                         "the difference between a mean over Britain and a mean over the Atlantic; "
                         "a change in it invalidates every figure below.")

    with _open("tas") as ds:
        xs = ds.coords["projection_x_coordinate"].values
        ys = ds.coords["projection_y_coordinate"].values
        lat = ds.coords["latitude"].values
    yy, xx = np.meshgrid(ys, xs, indexing="ij")

    return {
        "annual_temp": tas.mean(axis=0)[mask],
        "winter_temp": tas[list(WINTER_MONTHS)].mean(axis=0)[mask],
        "annual_wind": wind.mean(axis=0)[mask],
        # SUN IS A MONTHLY TOTAL, so the annual figure is a SUM. Averaging it would give a
        # plausible ~119 and be wrong by a factor of twelve -- the units are hours, not a rate.
        "annual_sun": sun.sum(axis=0)[mask],
        "winter_wind": wind[list(WINTER_MONTHS)].mean(axis=0)[mask],
        "east": xx[mask],
        "north": yy[mask],
        # TRUE LATITUDE, from the file's own auxiliary coordinate, NOT the OSGB northing. They are
        # not interchangeable: the projection converges towards the north, so the two disagree in
        # the third decimal of a correlation. W1_19's first, ad hoc run reported -0.806 against
        # latitude and this module reproduces -0.807 against northing; both are below, so which
        # was quoted is answerable rather than assumed.
        # ALL TWELVE MONTHS, not another aggregate. Every other key here is a reduction -- an
        # annual mean, a winter mean, a sum -- and for a year this loader read the (12, y, x)
        # array and returned nothing that could tell January from July. That is why
        # `demand_vector_coverage.seasonal_swing` was an invented constant: the quantity it claims
        # to be, the share of the year's demand in the coldest half, was computable from data
        # already on disk and there was no accessor for it.
        "monthly_temp": tas[:, mask],
        # AND THE MONTHLY SUNSHINE, for the same reason and one that is specific: solar gain is the
        # most seasonal term in the heat balance, so distributing an ANNUAL gain evenly across the
        # year would bias exactly the quantity a seasonal axis measures -- it would flatten the
        # winter deficit and understate the swing. Monthly totals in hours, like `annual_sun`.
        "monthly_sun": sun[:, mask],
        "latitude": lat[mask],
        "land_cells": n,
    }


def measurement() -> dict:
    """W1_19's published table, recomputed. Ranges, and the correlations that carry the finding."""
    import numpy as np

    d = drivers()
    named = ("annual_temp", "winter_temp", "annual_wind", "annual_sun")
    ranges = {k: {"min": round(float(d[k].min()), 2),
                  "median": round(float(np.median(d[k])), 2),
                  "max": round(float(d[k].max()), 2)} for k in named}

    def corr(a: str, b: str) -> float:
        return round(float(np.corrcoef(d[a], d[b])[0, 1]), 3)

    return {
        "land_cells": d["land_cells"],
        "grid_cells": GRID_SHAPE[0] * GRID_SHAPE[1],
        "ranges": ranges,
        "correlations": {
            "latitude_x_sunshine": corr("latitude", "annual_sun"),
            "northing_x_sunshine": corr("north", "annual_sun"),
            "latitude_x_annual_temp": corr("latitude", "annual_temp"),
            "northing_x_annual_temp": corr("north", "annual_temp"),
            "annual_temp_x_sunshine": corr("annual_temp", "annual_sun"),
            "annual_temp_x_annual_wind": corr("annual_temp", "annual_wind"),
            "winter_temp_x_winter_wind": corr("winter_temp", "winter_wind"),
            "winter_wind_x_sunshine": corr("winter_wind", "annual_sun"),
        },
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--measure", action="store_true", help="recompute W1_19's published table")
    args = ap.parse_args(argv)
    if args.measure:
        print(json.dumps(measurement(), indent=2))
        return 0
    ap.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
