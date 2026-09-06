"""Cold-spell persistence and cross-cell synchrony -- the half of the weather a hedger cares about.

REUSE: tools/weather_cell_persistence.py
CLASS: CUSTOM
INDEX: searched "persistence", "synchrony", "cold spell", "run length", "daily", "correlation".
       `tools/weather_cell_drivers.py` reads the 30-year NORMALS, which by construction say nothing
       about persistence -- an average has no runs in it. `simulation/weather_*.py` model one
       location's series. `background/weather_demand_triad.py` couples demand to weather already
       drawn, downstream of this. Nothing reads the daily grid.

WHY THIS EXISTS
---------------
The weather ruling's decision 4 puts both of these in phase 1 rather than deferring them, and gives
the reason: *"a five-day cold snap costs more than the same degree-days spread thin"*, and *"when
Glasgow is cold, is London? -- this is what turns household weather into PORTFOLIO RISK"*.

`W1_21` answered how many cells Britain needs to resolve the LEVEL of household heat load. Level is
what a tariff is priced off. **Persistence and synchrony are what a hedge is priced off**, and they
are invisible in everything measured so far: a 30-year normal is an average, and an average has no
runs in it.

WHAT IS BEING MEASURED, SAID BEFORE IT IS MEASURED
---------------------------------------------------
**A cold day is CELL-RELATIVE**: a day at or below that cell's own 10th percentile of daily mean
temperature over the 1991-2025 winter half-years. Not an absolute threshold.

That is a Choice and it is the load-bearing one. A household's building fabric, its boiler sizing
and its habits are adapted to its own climate; 2 degC is an ordinary January day in Aviemore and a
civil emergency in Penzance. An absolute threshold would report that Scotland has all the cold
spells, which is true and useless -- it would measure WHERE Britain is cold rather than WHEN each
place is colder than it is used to, and only the second one is a demand shock. `absolute_threshold`
computes the alternative so the difference can be priced rather than argued.

**A cold SPELL is a maximal run of consecutive cold days** within one winter half-year. Runs are not
allowed to span the March-to-October gap in the archive, which would splice two winters together and
manufacture spells that never happened.

**SYNCHRONY is joint exceedance, not correlation.** Two cells whose daily temperatures correlate at
0.9 can still have independent COLD TAILS, and it is the tails that cost money. The measure is
P(both cells in their own coldest decile on the same day), against the 0.01 that independence would
give -- a lift, with 1.0 meaning independent and 10.0 meaning perfectly locked.
"""
from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

# Run as a script, `sys.path[0]` is `tools/`, not the repo root.
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

CACHE = Path.home() / ".cache" / "synthetic-enterprise" / "haduk_grid"
DAILY = CACHE / "tas" / "day"
SERIES = CACHE / "derived" / "representative_daily_tas.npz"

#: The archive holds the winter half-year only -- October to March, 35 years, 210 monthly files.
#: Nothing here may assume a continuous calendar.
WINTER_MONTHS = (10, 11, 12, 1, 2, 3)
EXPECTED_FILES = 210

#: `W1_21`'s 95% answer. Enough cells that the portfolio question is about geography rather than
#: about the coarseness of the sample.
DEFAULT_CELLS = 89

COLD_DECILE = 0.10

#: HadUK's 1 km grid origin. Column index = (easting + 200000) // 1000; the grid starts at -199500,
#: not at zero, and getting this wrong shifts every series by 200 km without failing anywhere.
GRID_ORIGIN_M = -200_000


def _daily_files() -> list[Path]:
    hits = sorted(Path(p) for p in glob.glob(str(DAILY / "*.nc")))
    if not hits:
        raise FileNotFoundError(f"no daily tas under {DAILY}. Run `tools/fetch_haduk_grid.py`.")
    return hits


def representative_cells(k: int = DEFAULT_CELLS):
    """(row indices, column indices, household weights) for one cell per cluster.

    THE REPRESENTATIVE IS THE OCCUPIED CELL NEAREST ITS CLUSTER CENTRE, not the centre itself: a
    centroid in standardised driver space is a point no real place occupies, and it has no daily
    series. Its weight is the whole cluster's households, so the portfolio arithmetic below is
    about the book and not about the 89 postcodes that happen to represent it.
    """
    import numpy as np
    from sklearn.cluster import KMeans

    from tools import weather_cell_derivation as wcd
    from tools import weather_cell_drivers as drv
    from tools import weather_cell_weights as wgt

    d = drv.drivers()
    w, _ = wgt.aligned_to_land(d)
    occupied = w > 0
    z, _, weights, _, _ = wcd._space(True)
    km = KMeans(n_clusters=k, n_init=1, random_state=0).fit(z, sample_weight=weights)

    east = d["east"][occupied]
    north = d["north"][occupied]
    rows, cols, mass = [], [], []
    for label in range(k):
        member = km.labels_ == label
        dist = ((z[member] - km.cluster_centers_[label]) ** 2).sum(axis=1)
        pick = np.flatnonzero(member)[int(np.argmin(dist))]
        cols.append(int((east[pick] - GRID_ORIGIN_M) // 1000))
        rows.append(int((north[pick] - GRID_ORIGIN_M) // 1000))
        mass.append(float(weights[member].sum()))
    return np.array(rows), np.array(cols), np.array(mass)


def build_series(k: int = DEFAULT_CELLS, dest: Path = SERIES, progress=print):
    """Extract each representative cell's daily series across the whole archive, once."""
    import numpy as np
    import xarray as xr

    rows, cols, mass = representative_cells(k)
    files = _daily_files()
    if len(files) != EXPECTED_FILES:
        progress(f"[persistence] WARNING {len(files)} daily files, expected {EXPECTED_FILES}")

    chunks, stamps = [], []
    for i, path in enumerate(files):
        with xr.open_dataset(path, engine="h5netcdf") as ds:
            arr = ds["tas"].values                       # (days, y, x)
            chunks.append(arr[:, rows, cols])
            stamps.append(ds.coords["time"].values)
        if i % 40 == 0:
            progress(f"[persistence] {i}/{len(files)} months")

    series = np.concatenate(chunks, axis=0)
    times = np.concatenate(stamps).astype("datetime64[D]")
    order = np.argsort(times)
    dest.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(dest, series=series[order], times=times[order].astype(str),
                        rows=rows, cols=cols, mass=mass)
    progress(f"[persistence] {series.shape[0]} days x {series.shape[1]} cells -> {dest}")
    return dest


def load_series():
    import numpy as np

    if not SERIES.is_file():
        raise FileNotFoundError(f"{SERIES} -- run `--build` first")
    z = np.load(SERIES)
    return (z["series"], np.array(z["times"], dtype="datetime64[D]"), z["mass"],
            z["rows"], z["cols"])


def _winter_index(times):
    """Which winter half-year each day belongs to, so a run cannot span the archive's gap.

    October to December belong to the winter LABELLED by that year; January to March belong to the
    previous year's. Without this, 31 March 1998 and 1 October 1998 are adjacent rows and a spell
    can be manufactured across a six-month hole in the data.
    """
    import numpy as np

    years = times.astype("datetime64[Y]").astype(int) + 1970
    months = times.astype("datetime64[M]").astype(int) % 12 + 1
    return np.where(months >= 10, years, years - 1)


def _runs(flags) -> list[int]:
    """Lengths of maximal True runs."""
    out, run = [], 0
    for flag in flags:
        if flag:
            run += 1
        elif run:
            out.append(run)
            run = 0
    if run:
        out.append(run)
    return out


def persistence(seed: int = 0) -> dict:
    """Cold-spell length against the null in which the same cold days fall independently.

    THE NULL IS A PERMUTATION OF THE SAME DAYS, not a fresh Bernoulli draw. It holds the number of
    cold days per cell and per winter exactly fixed, so the only thing that differs is whether they
    CLUSTER. A null that also resampled the count would confound frequency with persistence, and
    the ruling's claim is entirely about clustering.
    """
    import numpy as np

    series, times, mass, _, _ = load_series()
    winters = _winter_index(times)
    rng = np.random.default_rng(seed)

    observed: list[int] = []
    shuffled: list[int] = []
    for cell in range(series.shape[1]):
        threshold = np.nanpercentile(series[:, cell], COLD_DECILE * 100)
        cold = series[:, cell] <= threshold
        for winter in np.unique(winters):
            block = cold[winters == winter]
            observed.extend(_runs(block))
            shuffled.extend(_runs(rng.permutation(block)))

    obs = np.array(observed)
    null = np.array(shuffled)

    def tail(arr, n):
        return round(float((arr >= n).sum() / len(arr)), 4)

    return {
        "cold_spells_observed": len(obs),
        "cold_spells_under_independence": len(null),
        "mean_length": {"observed": round(float(obs.mean()), 3),
                        "independent": round(float(null.mean()), 3)},
        "longest": {"observed": int(obs.max()), "independent": int(null.max())},
        "share_of_spells_at_least": {
            str(n): {"observed": tail(obs, n), "independent": tail(null, n),
                     "lift": round(tail(obs, n) / tail(null, n), 2) if tail(null, n) else None}
            for n in (3, 5, 7, 10, 14)},
        "days_in_spells_of_5_or_more": {
            "observed": round(float(obs[obs >= 5].sum() / obs.sum()), 4),
            "independent": round(float(null[null >= 5].sum() / null.sum()), 4)},
    }


def synchrony() -> dict:
    """How much of the book can be cold on the same day.

    `worst_day_share` is the portfolio number: the largest household-weighted share of the book
    sitting in its own coldest decile on a single day. Under independence it would sit near 10%;
    what it actually is decides whether cells diversify or merely relabel one national exposure.
    """
    import numpy as np

    series, times, mass, grid_rows, grid_cols = load_series()
    thresholds = np.nanpercentile(series, COLD_DECILE * 100, axis=0)
    cold = series <= thresholds

    weights = mass / mass.sum()
    share = cold @ weights

    n = series.shape[1]
    joint = (cold.T.astype(float) @ cold.astype(float)) / len(series)
    iu = np.triu_indices(n, k=1)
    lift = joint[iu] / (COLD_DECILE ** 2)

    dx = (grid_cols[:, None] - grid_cols[None, :]).astype(float)
    dy = (grid_rows[:, None] - grid_rows[None, :]).astype(float)
    km_apart = np.sqrt(dx ** 2 + dy ** 2)[iu]      # grid indices ARE kilometres on this grid

    bands = {}
    for lo, hi in ((0, 100), (100, 250), (250, 500), (500, 1200)):
        sel = (km_apart >= lo) & (km_apart < hi)
        if sel.any():
            bands[f"{lo}-{hi}km"] = {"pairs": int(sel.sum()),
                                     "mean_lift": round(float(lift[sel].mean()), 2)}

    return {
        "cells": n,
        "mean_joint_cold_lift": round(float(lift.mean()), 2),
        "min_pair_lift": round(float(lift.min()), 2),
        "lift_by_separation": bands,
        "worst_day_share": round(float(share.max()), 4),
        "worst_day": str(times[int(np.argmax(share))]),
        "days_with_over_half_the_book_cold": int((share > 0.5).sum()),
        "days_measured": int(len(series)),
    }


def absolute_threshold(degc: float = 5.0) -> dict:
    """THE ALTERNATIVE TO THE CELL-RELATIVE CHOICE, priced rather than argued.

    A fixed threshold answers "where in Britain is it cold", and the answer is Scotland. The
    cell-relative definition answers "where is it colder than that place is built for", which is
    what turns into a demand shock. This reports how unevenly a fixed threshold falls, so a reader
    who prefers it can see what they are choosing.
    """
    import numpy as np

    series, _, mass, _, _ = load_series()
    cold_days = (series <= degc).mean(axis=0)
    return {
        "degc": degc,
        "share_of_days_below": {"min_cell": round(float(cold_days.min()), 4),
                                "median_cell": round(float(np.median(cold_days)), 4),
                                "max_cell": round(float(cold_days.max()), 4)},
        "ratio_max_to_min": (round(float(cold_days.max() / cold_days.min()), 1)
                             if cold_days.min() > 0 else None),
        "cells_never_below": int((cold_days == 0).sum()),
        "household_share_in_the_coldest_quartile_of_cells": round(float(
            mass[cold_days >= np.quantile(cold_days, 0.75)].sum() / mass.sum()), 4),
    }


def measurement() -> dict:
    return {"persistence": persistence(), "synchrony": synchrony(),
            "the_alternative_definition": absolute_threshold()}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--build", action="store_true", help="extract the representative daily series")
    ap.add_argument("--cells", type=int, default=DEFAULT_CELLS)
    ap.add_argument("--measure", action="store_true", help="print persistence and synchrony")
    args = ap.parse_args(argv)
    if args.build:
        build_series(args.cells)
        return 0
    if args.measure:
        print(json.dumps(measurement(), indent=2))
        return 0
    ap.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
