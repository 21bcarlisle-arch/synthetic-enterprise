"""The weather cells, and the curve that answers how many of them there need to be.

REUSE: tools/weather_cell_derivation.py
CLASS: CATALOGUE
LIBRARY: scikit-learn (weighted k-means). The weighting is the whole exercise and `KMeans.fit`
         takes `sample_weight` directly; hand-rolling Lloyd's algorithm to avoid one import would
         be the "new branch hand-rolls what a helper centralises" shape.
INDEX: searched "cluster", "kmeans", "coverage curve", "cells", "granularity", "region".
       `tools/weather_cell_drivers.py` supplies the driver arrays and `tools/weather_cell_weights.py`
       the household weights; both are imported rather than re-derived.
       `simulation/adoption_geography.py` partitions on administrative regions, which is exactly the
       input the ruling forbids here.

WHY THIS EXISTS
---------------
The director's question, verbatim: *"how much granularity is needed to capture, say 99%, versus 95
or 90% of the variation for households across these primary heat load variables"*.

**THE ANSWER IS A CURVE, NOT A NUMBER** (the ruling's decision 5), and this module owns the LEVEL
half of it -- annual heat load. Shape is `W1_18`; persistence and synchrony are `W1_22`.

WHAT "THE VARIATION" MEANS HERE, SAID BEFORE IT IS MEASURED
-----------------------------------------------------------
A percentage of variation is meaningless until three things are fixed, and this project's most
expensive recurring failure is inferring them from the answer afterwards.

  1. **Whose variation.** Households, not land. `W1_20` established that half of GB's land cells
     hold nobody and that weighting for it halves the spread on every driver. Every figure here is
     household-weighted; the area-weighted curve is computed alongside purely to show the gap.
  2. **Variation in what.** Three drivers: **winter mean temperature** (heat demand), **annual mean
     wind speed** (infiltration and wind chill) and **annual sunshine duration** (solar gain).
     Annual mean temperature is excluded as a fourth: it correlates 0.936 with winter temperature
     and adds a second copy of the same axis. Annual and winter wind correlate 0.996 -- one wind
     measure is all there is.
  3. **Measured how.** Captured share = 1 - (within-cluster household-weighted sum of squares /
     total household-weighted sum of squares) in STANDARDISED driver space.

**THE CHOICE, AND IT IS NOT NEUTRAL.** Standardising each driver by its own household-weighted
standard deviation gives the three equal say. That is a statement that a one-sigma move in sunshine
matters as much to a heat bill as a one-sigma move in winter temperature, and it is almost certainly
false -- temperature dominates. The honest alternative weights each driver by its coefficient in a
fitted heat-load model, and this company has no such model yet; `W2_21` is where it comes from.
Equal standardisation is therefore the CONSERVATIVE choice: it can only ever ask for MORE cells than
a temperature-dominant metric would, so the counts below are an upper bound on the granularity a
level-only fit needs. `native_residuals` reports the error in degrees, metres per second and hours,
so a reader who disagrees with the weighting can price the disagreement instead of arguing about it.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

# Run as a script, `sys.path[0]` is `tools/` and not the repo root. Fifth-and-sixth module in this
# repository to need this line; `test_the_curve_runs_THE_WAY_A_COMMAND_LINE_RUNS_IT` is the control.
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

#: The ruling's three primary heat-load variables, in the form the normals actually carry them.
DRIVERS = ("winter_temp", "annual_wind", "annual_sun")
UNITS = {"winter_temp": "degC", "annual_wind": "m/s", "annual_sun": "hours"}

#: Coverage targets the director named, plus the two the ruling adds.
TARGETS = (0.90, 0.95, 0.99)

#: A geometric sweep, because the curve is steep at the left and flat at the right and a linear
#: sweep spends all its runs where nothing changes.
DEFAULT_KS = (1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584)


def _space(household_weighted: bool = True):
    """(standardised driver matrix, native driver matrix, weights, mean, sd) over occupied cells."""
    import numpy as np

    from tools import weather_cell_drivers as wcd
    from tools import weather_cell_weights as wcw

    d = wcd.drivers()
    w, _ = wcw.aligned_to_land(d)
    occupied = w > 0
    native = np.column_stack([d[k][occupied] for k in DRIVERS]).astype(np.float64)
    # THE AREA-WEIGHTED COMPARISON IS OVER THE SAME CELLS, not over all land. Otherwise the two
    # curves differ both in weighting and in population and neither difference is attributable.
    weights = w[occupied] if household_weighted else np.ones(occupied.sum())
    mean = np.average(native, axis=0, weights=weights)
    sd = np.sqrt(np.average((native - mean) ** 2, axis=0, weights=weights))
    return (native - mean) / sd, native, weights, mean, sd


def coverage_curve(ks=DEFAULT_KS, household_weighted: bool = True, seed: int = 0,
                   space=None) -> list[dict]:
    """One row per k: the share of variation captured, and what the residual is in real units.

    `space` is the `_space()` tuple, injectable so a caller sweeping several metrics pays the
    census join once. It is not an optimisation for its own sake: re-reading 1.67 million postcodes
    per metric is the difference between a control that runs in the commit gate and one that does
    not, and a control nobody can afford to run is a control that gets skipped.
    """
    import numpy as np
    from sklearn.cluster import KMeans

    z, native, weights, mean, sd = space if space is not None else _space(household_weighted)
    total = float(np.sum(weights[:, None] *
                         (z - np.average(z, axis=0, weights=weights)) ** 2))

    rows = []
    for k in ks:
        if k > len(z):
            break
        km = KMeans(n_clusters=k, n_init=1, random_state=seed).fit(z, sample_weight=weights)
        centres = km.cluster_centers_[km.labels_]
        within = float(np.sum(weights[:, None] * (z - centres) ** 2))
        residual = native - (centres * sd + mean)
        rms = np.sqrt(np.average(residual ** 2, axis=0, weights=weights))
        rows.append({
            "cells": k,
            "captured": round(1.0 - within / total, 4),
            "native_residuals": {name: round(float(v), 3) for name, v in zip(DRIVERS, rms)},
        })
    return rows


def cells_for(target: float, rows: list[dict] | None = None) -> int | None:
    """The smallest swept k reaching `target`, or None -- which is a RESULT, not a failure.

    A curve that never reaches 99% within the sweep must say so. Returning the largest k, or
    extrapolating, would answer the director's question with a number the measurement does not
    contain.
    """
    for row in rows if rows is not None else coverage_curve():
        if row["captured"] >= target:
            return row["cells"]
    return None


#: The Choice, and the two neighbours that price it. Each entry weights the standardised drivers
#: before clustering; each is scored on ITS OWN metric, because the question a reader asks is
#: "how many cells do I need if temperature is what matters to me".
METRICS = {
    "equal": (1.0, 1.0, 1.0),
    "temperature_dominant_4_1_1": (4.0, 1.0, 1.0),
    "temperature_only": (1.0, 0.0, 0.0),
}


def choice_sensitivity(ks=DEFAULT_KS, space=None) -> dict:
    """WHAT THE EQUAL-WEIGHTING CHOICE COSTS, measured rather than argued.

    The docstring above calls equal standardisation conservative -- that it can only ask for MORE
    cells than a temperature-dominant metric would. That is a falsifiable claim about this data and
    it is checked here rather than asserted: if a temperature-dominant metric ever needed MORE
    cells for the same target, the reasoning behind the Choice would be wrong.
    """
    import numpy as np
    from sklearn.cluster import KMeans

    z, _, weights, _, _ = space if space is not None else _space(True)
    out: dict[str, dict] = {}
    for name, scale in METRICS.items():
        zs = z * np.array(scale)
        total = float(np.sum(weights[:, None] *
                             (zs - np.average(zs, axis=0, weights=weights)) ** 2))
        rows = []
        for k in ks:
            km = KMeans(n_clusters=k, n_init=1, random_state=0).fit(zs, sample_weight=weights)
            within = float(np.sum(weights[:, None] *
                                  (zs - km.cluster_centers_[km.labels_]) ** 2))
            rows.append({"cells": k, "captured": round(1.0 - within / total, 4)})
        out[name] = {"cells_needed": {f"{int(t * 100)}pc": cells_for(t, rows) for t in TARGETS},
                     "curve": rows}
    return out


def per_driver_curve(ks=DEFAULT_KS, space=None) -> dict:
    """One coverage curve PER DRIVER, each partitioning on that driver alone.

    THE QUESTION THE JOINT CURVE CANNOT ANSWER, and the reason `measurement()`'s 987 was read as a
    statement about wind. Asked one at a time, all three drivers want about 21 cells for 99% and
    wind wants marginally the FEWEST -- its fine structure is terrain, coast and exposure, which is
    the empty half of the country. The joint requirement is dimensionality, not any driver's own
    roughness, and a reader who only ever sees the joint number cannot tell those apart.
    """
    import numpy as np
    from sklearn.cluster import KMeans

    z, native, weights, mean, sd = space if space is not None else _space(True)
    out: dict[str, list[dict]] = {}
    for i, name in enumerate(DRIVERS):
        col = z[:, [i]]
        total = float(np.sum(weights[:, None] *
                             (col - np.average(col, axis=0, weights=weights)) ** 2))
        rows = []
        for k in ks:
            km = KMeans(n_clusters=k, n_init=1, random_state=0).fit(col, sample_weight=weights)
            centres = km.cluster_centers_[km.labels_]
            within = float(np.sum(weights[:, None] * (col - centres) ** 2))
            residual = native[:, i] - (centres[:, 0] * sd[i] + mean[i])
            rows.append({"cells": k, "captured": round(1.0 - within / total, 4),
                         "rms": round(float(np.sqrt(np.average(residual ** 2, weights=weights))), 3)})
        out[name] = rows
    return out


def measurement(ks=DEFAULT_KS) -> dict:
    """W1_21's published table: the household curve, the area curve, and the targets."""
    household = coverage_curve(ks, household_weighted=True, space=_space(True))
    area = coverage_curve(ks, household_weighted=False, space=_space(False))
    return {
        "drivers": list(DRIVERS),
        "units": UNITS,
        "household_weighted": household,
        "area_weighted_over_the_same_cells": area,
        "cells_needed": {f"{int(t * 100)}pc": cells_for(t, household) for t in TARGETS},
        "cells_needed_area_weighted": {f"{int(t * 100)}pc": cells_for(t, area) for t in TARGETS},
        "swept_to": max(r["cells"] for r in household),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--curve", action="store_true", help="print the coverage curve and the targets")
    ap.add_argument("--max-cells", type=int, default=None, help="stop the sweep at this k")
    ap.add_argument("--choice-sensitivity", action="store_true",
                    help="the same curve under three driver weightings")
    ap.add_argument("--per-driver", action="store_true",
                    help="one curve per driver, each partitioning on that driver alone")
    args = ap.parse_args(argv)

    if args.per_driver:
        ks = tuple(k for k in DEFAULT_KS if args.max_cells is None or k <= args.max_cells)
        print(json.dumps(per_driver_curve(ks), indent=2))
        return 0
    if args.choice_sensitivity:
        ks = tuple(k for k in DEFAULT_KS if args.max_cells is None or k <= args.max_cells)
        print(json.dumps(choice_sensitivity(ks), indent=2))
        return 0
    if args.curve:
        ks = tuple(k for k in DEFAULT_KS if args.max_cells is None or k <= args.max_cells)
        print(json.dumps(measurement(ks), indent=2))
        return 0
    ap.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
