"""The weather partition asked as a joint question over a stock whose response varies with fabric.

REUSE: tools/weather_cell_joint_partition.py
CLASS: CATALOGUE
LIBRARY: scikit-learn (weighted k-means, randomized SVD). Both are the same reasoning
         `weather_cell_derivation` gives: the weighting is the exercise and `KMeans.fit` takes
         `sample_weight`; `randomized_svd` is what makes a 274-dimensional signature affordable.
INDEX: searched "joint", "partition", "fabric", "stock response", "cells", "separable", "cluster".
       `tools/weather_cell_derivation.py` is the closest row and is the SUBJECT of the comparison,
       not the implementation: it partitions the weather against ITSELF and its `coverage_curve`
       cannot be reused because the space being partitioned here is a different space. Its
       `captured_share` and `cells_for` idioms are imported rather than restated.
       `tools/demand_case_coverage.py` supplies the (cell x house case) demand grid and is imported
       whole -- the closed form, the household weights and the national stock mixture all come from
       there. `tools/space_filling_sample.py` owns the DRAW and is imported for it; the derived cell
       count below is read off its sample rather than computed by a second one.
       `tools/reduction_dimension.py` holds the declaration.
       Nothing in the tree partitions a weather space by what it DOES to a varying stock.

WHY THIS EXISTS
---------------
`DIRECTOR_CANON_THE_DEMAND_VECTOR_2026-09-07`, WORK THIS CREATES item 2: *"The weather partition
re-opened as a joint question over a stock with varying fabric."*

The canon's section 1, on inputs: three grids -- 21 temperature, 21 wind, 5 irradiance -- assume a
household's response to weather is SEPARABLE, and this project's own measurement says it is not.
`weather_driver_sensitivity` reports solar gain moving fuel -1.2% in a leaky pre-1919 house against
-7.9% in a tight post-2000 one, and wind moving the heat loss coefficient +18.6% mid-stock against
+2.9% in that same modern house, because Part F's minimum air change rate clamps the calm end.
**The response to each driver depends on the fabric**, so the subject is the joint weather condition
over a varying stock, and a partition of the drivers knows nothing about it however fine it is.

WHAT IS BEING PARTITIONED, AND WHAT A CELL IS WORTH -- SAID BEFORE IT IS MEASURED
---------------------------------------------------------------------------------
The thing partitioned is the 143,511 occupied 1 km cells. What distinguishes two cells is NOT their
driver values but **what they do to the stock**: cell `c` is the 274-vector of annual space-heat
demand it produces across the 274 house cases `demand_case_coverage` builds from NEED. Two cells are
the same cell when the whole stock cannot tell them apart.

Captured share is then the household-weighted variance of that surface explained by the partition:

    captured = 1 - sum_ci w_ci (demand_ci - cluster_mean_li) ** 2 / sum_ci w_ci (demand_ci - mean_i) ** 2

**THE STOCK IS HELD AT THE NATIONAL MIXTURE IN EVERY CELL** -- `w_ci = households_c x mixture_i`,
with the mixture national rather than regional. That is a CHOICE and it is the controlled one: NEED
gives a different stock composition per region, and letting it vary by cell would fold "who lives
where" into a measurement of "what weather does to whom". `demand_case_coverage.measurement`'s
weather-alone leg holds the house at the national mixture for the same reason. The cost is that the
answer here is about the weather's interaction with the STOCK, not with the stock's geography.

THE THREE RIVALS, AND WHY THE THIRD IS THE ONLY FAIR ONE
--------------------------------------------------------
Scored on the identical metric, the same cells, the same weights, at matched cell counts, so the
only thing differing between two rows is what the partition is built on:

  * `joint_over_stock`    -- built on the stock-response signature. This is the subject.
  * `drivers_equal`       -- built on the three standardised drivers jointly. This is `W1_21`'s
                             space. It is fabric-blind AND it gives wind and sunshine the same say
                             as temperature, so a gap against it is two effects at once and cannot
                             be attributed to either.
  * `representative_house` -- built on ONE scalar: the demand of the national-mixture average house
                             in each cell. It knows exactly how much each driver moves demand and is
                             blind ONLY to the response varying across the stock. **This is the
                             opponent the finding rests on.** A gap here is attributable to fabric
                             non-separability and to nothing else.
  * `separable`           -- each driver clustered ALONE and the labels crossed, which is 21/21/5's
                             actual shape. Reported at its own realised cell count, never at the
                             nominal one, because `p` clusters per driver is `p**3` cells.

WHAT THE MEASUREMENT FOUND (seed 0, 143,511 cells, 274 cases, 24.7m households)

    cells    joint_over_stock   drivers_equal   representative_house
       13             0.9636          0.7790                 0.9605
       55             0.9903          0.9150                 0.9761
      233             0.9973          0.9713                 0.9773
      987             0.9992          0.9908                 0.9781

**55 cells against 987.** The joint partition reaches 99% of the stock-response variation at 55
cells; the fabric-blind driver partition needs 987 for the same metric, and the representative-house
partition does not reach it ANYWHERE in the sweep -- it is still at 0.978 with 987 cells to spend.
That last row is the finding: the residual it cannot reach is not roughness that more cells would
resolve, it is the part of a cell's effect that differs between a leaky house and a tight one.

NO ASYMPTOTE IS CLAIMED. The obvious next step -- bin the representative-house scalar finely and
call the limit a ceiling -- was measured and DISCARDED: the estimate climbed from 0.975 at 500 bins
to 0.986 at 8,000, because with 18 cells per bin the within-cluster sum of squares falls whether or
not the scalar carries the information. The same finite-sample flattery inflates every k-means row
above, and it inflates all three columns EQUALLY at matched `k`, which is exactly why the comparison
is made at matched `k` and the limit is not quoted.

THE CELL COUNT IS AN OUTPUT OF THE DRAW, NOT AN INPUT TO IT (canon section 5)
------------------------------------------------------------------------------
*"Once the sample is a set of (household, cell) cases, the number of cells is whatever the drawn
sample lands in."* `derived_cell_count` therefore does not choose anything: it takes
`space_filling_sample`'s own draw-for-difference and counts the distinct cells it landed in. 2,584
drawn cases land in 2,195 cells; 987 land in 890. The draw reuses a cell one time in seven, so the
cell count is very nearly the sample size -- which is the canon's point stated as a number, and it
is why wanting the count in advance is a data-pull question rather than a modelling one.

Run:  python3 -m tools.weather_cell_joint_partition --curve        # the three rivals, matched k
      python3 -m tools.weather_cell_joint_partition --separable    # per-driver crossed, own count
      python3 -m tools.weather_cell_joint_partition --derived-cells  # what the draw landed in
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

# Run as a script, `sys.path[0]` is `tools/` and not the repo root.
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from tools.reduction_dimension import DEMAND_VECTOR, declare  # noqa: E402  (after the path fix)
from tools.weather_cell_derivation import captured_share  # noqa: E402

#: The three drivers, in `demand_case_coverage`'s cell-array spelling rather than
#: `weather_cell_derivation`'s. Degree days and the solar index are monotone transforms of winter
#: temperature and annual sunshine, so the partitions are the same partitions; the names differ
#: because these are the arrays the demand grid actually carries.
DRIVERS = ("cell_hdd", "cell_wind", "cell_solar_index")

#: A geometric sweep, for the reason `weather_cell_derivation` gives: the curve is steep at the left
#: and flat at the right. Stops at 987 because that is `W1_21`'s answer and the row where the
#: fabric-blind partition finally reaches the target is the one worth printing.
DEFAULT_KS = (1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987)

#: Clusters per driver for the separable partition. Each `p` realises `p ** 3` cells and is reported
#: at that count, never at `p`.
DEFAULT_PER_DRIVER = (1, 2, 3, 4, 5, 6, 8, 10)

TARGETS = (0.90, 0.95, 0.99)

#: How many directions of the 274-dimensional signature the embedding keeps. TEN IS NOT A CHOICE
#: ABOUT ACCURACY: the surface is `hlc_i(wind) * hdd - aperture_i * solar - internal_i`, clipped at
#: zero, so its rank in cell-space is small and the tenth component already carries 1e-8 of the
#: energy. `stock_response` reports what was retained rather than asserting it, and every captured
#: share is computed in the embedding -- a truncation that dropped real structure would show up as a
#: retained energy below one, not as a silently wrong answer.
EMBEDDING_COMPONENTS = 10

#: WHAT THIS CLAIM REDUCES OVER. The subject is the demand vector plus the fabric, because the whole
#: content of the finding is that the fabric is a component and that a partition of the drivers is
#: blind to it. `weather_condition_x_fabric` is DERIVED and consumes three components at once, which
#: is what makes `Declaration.collapsed` name it: this is a joint reduction over a cross, and the
#: two figures it replaces read identically as "cells for 99%".
#:
#: NEITHER OLDER FIGURE IS WITHDRAWN. `W1_21`'s 987 is correct arithmetic about the drivers' own
#: variance and `weather_cell_derivation` declares it as such. What this adds is the same question
#: asked about the demand the drivers cause, where the answer is 55.
_SUBJECT = DEMAND_VECTOR + ("dwelling_fabric",)

REDUCES_OVER = declare(
    "cells for 99% of the household-weighted demand variation a weather cell drives across the "
    "stock (the 55)",
    kind="coverage",
    of=_SUBJECT,
    reduces_over=("weather_condition_x_fabric",),
    derived_from={"weather_condition_x_fabric": ("annual_gas_kwh", "annual_electricity_kwh",
                                                 "dwelling_fabric")},
    blind_to=("seasonal_gas_shape", "half_hourly_electricity_shape", "heating_fuel"),
    joint=True,
)


def stock_response(grid=None):
    """The cells in the space of what they DO to the stock, and the two rival spaces beside them.

    Returns the embedding every partition below is SCORED in, the two spaces the rivals are BUILT
    in, the household weights, and the energy the embedding retained.
    """
    import numpy as np
    from sklearn.utils.extmath import randomized_svd

    from tools import demand_case_coverage as dcc

    g = grid if grid is not None else dcc.demand_grid()
    demand = np.asarray(g["demand"])                       # (cells, cases)
    mixture = np.asarray(g["national_mixture"])            # (cases,)
    weights = np.asarray(g["cell_weights"])                # (cells,)

    # `sqrt(mixture)` puts the metric INTO the coordinates, so plain Euclidean distance in this
    # space is the mixture-weighted demand error. Without it k-means would give a case occupied by
    # 0.1% of the stock the same say as one occupied by 8%.
    signature = demand * np.sqrt(mixture)[None, :]
    signature = signature - np.average(signature, axis=0, weights=weights)
    total = float(np.sum(weights[:, None] * signature ** 2))

    # The SVD is taken on the weight-scaled rows because the subspace that matters is the one that
    # carries HOUSEHOLD-weighted energy; the embedding itself is unweighted so `sample_weight` can
    # do that job once, in k-means, rather than twice.
    _, values, directions = randomized_svd(signature * np.sqrt(weights)[:, None],
                                           n_components=EMBEDDING_COMPONENTS, random_state=0)
    embedding = signature @ directions.T
    retained = float(np.sum(weights[:, None] * embedding ** 2)) / total

    drivers = np.stack([np.asarray(g[name]) for name in DRIVERS], axis=1)
    mean = np.average(drivers, axis=0, weights=weights)
    sd = np.sqrt(np.average((drivers - mean) ** 2, axis=0, weights=weights))
    standardised = (drivers - mean) / np.where(sd == 0, 1.0, sd)

    return {
        "embedding": embedding,
        "total": total,
        "weights": weights,
        "energy_retained": round(retained, 8),
        "singular_energy": [round(float(v ** 2 / total), 8) for v in values],
        "drivers_standardised": standardised,
        "representative_house": (demand * mixture[None, :]).sum(axis=1).reshape(-1, 1),
        "cells": int(demand.shape[0]),
        "cases": int(demand.shape[1]),
        "households": float(weights.sum()),
    }


def captured(labels, space) -> float:
    """Share of the stock-response variation a labelling of the cells explains.

    ONE METRIC FOR EVERY PARTITION, and that is the only reason the comparison below means
    anything. A rival built in a different space is scored here, never on its own space's residual.
    """
    import numpy as np

    embedding, weights = space["embedding"], space["weights"]
    labels = np.asarray(labels)
    within = 0.0
    for label in np.unique(labels):
        member = labels == label
        w, y = weights[member], embedding[member]
        within += float(np.sum(w[:, None] * (y - np.average(y, axis=0, weights=w)) ** 2))
    return captured_share(within, space["total"])


def _cluster(values, k: int, weights, seed: int):
    import numpy as np
    from sklearn.cluster import KMeans

    if k <= 1:
        return np.zeros(len(weights), dtype=np.int64)
    return KMeans(n_clusters=k, n_init=1, random_state=seed).fit(
        values, sample_weight=weights).labels_


def joint_partition(k: int, space, seed: int = 0):
    """THE SUBJECT: cells grouped by what they do to the whole stock, jointly over fabric."""
    return _cluster(space["embedding"], k, space["weights"], seed)


def fabric_blind_partition(k: int, space, seed: int = 0):
    """`W1_21`'s space: the three standardised drivers, jointly, with no fabric in the partition."""
    return _cluster(space["drivers_standardised"], k, space["weights"], seed)


def representative_house_partition(k: int, space, seed: int = 0):
    """THE FAIR OPPONENT: the demand of one average house per cell.

    It knows every driver's effect and is blind only to that effect VARYING across the stock, so
    what it cannot capture is attributable to the fabric and to nothing else.
    """
    return _cluster(space["representative_house"], k, space["weights"], seed)


def separable_partition(per_driver: int, space, seed: int = 0):
    """21/21/5's actual shape: each driver clustered ALONE and the three labels crossed."""
    import numpy as np

    standardised = space["drivers_standardised"]
    labels = np.zeros(standardised.shape[0], dtype=np.int64)
    for column in range(standardised.shape[1]):
        alone = _cluster(standardised[:, [column]], per_driver, space["weights"], seed)
        labels = labels * per_driver + alone
    return labels


#: The rivals, in the order the table prints them. Keyed by the name the output uses so a reader
#: comparing two columns can find what built each.
BUILDERS = {
    "joint_over_stock": joint_partition,
    "drivers_equal": fabric_blind_partition,
    "representative_house": representative_house_partition,
}


def coverage_curve(ks=DEFAULT_KS, space=None, seed: int = 0) -> list[dict]:
    """One row per cell count: what each rival captures of the SAME stock-response variation."""
    space = space if space is not None else stock_response()
    return [{"cells": k,
             **{name: captured(build(k, space, seed), space) for name, build in BUILDERS.items()}}
            for k in ks if k <= space["cells"]]


def cells_for(target: float, rows: list[dict], key: str = "joint_over_stock") -> int | None:
    """The smallest swept cell count reaching `target` for one rival, or None.

    NONE IS A RESULT AND IT IS THE FINDING HERE. `representative_house` returns None across the
    whole sweep, and returning the largest `k` or extrapolating would turn "it does not get there"
    into a number. What None means is bounded by the sweep and nothing more: not reached by 987.
    """
    for row in rows:
        if row[key] >= target:
            return row["cells"]
    return None


def separable_curve(per_driver=DEFAULT_PER_DRIVER, space=None, seed: int = 0) -> list[dict]:
    """The crossed per-driver partition against the joint one AT THE COUNT IT ACTUALLY REALISES.

    `realised` is the number of non-empty crossed groups, which is at most `p ** 3` and is usually
    fewer -- the drivers are correlated, so some conjunctions hold no cell. Comparing a nominal
    `p ** 3` against a joint `p ** 3` would credit the separable partition with cells it does not
    have.
    """
    import numpy as np

    space = space if space is not None else stock_response()
    rows = []
    for p in per_driver:
        labels = separable_partition(p, space, seed)
        realised = int(len(np.unique(labels)))
        rows.append({
            "clusters_per_driver": p,
            "realised_cells": realised,
            "separable": captured(labels, space),
            "joint_over_stock_at_the_same_count": captured(
                joint_partition(realised, space, seed), space),
        })
    return rows


def derived_cell_count(ns=(13, 55, 233, 987, 2584), seed: int = 0, sample: int = 200_000) -> dict:
    """How many distinct cells the DRAW landed in -- the canon's section 5, computed not chosen.

    The draw is `space_filling_sample`'s, unchanged and not re-implemented: drawing a second sample
    here would answer the question about a sample nothing else uses.

    `cells_available_in_the_sample` is the honest bound. The draw chooses from a 200,000-point
    weighted sample of the 39.3m (cell, case) pairs, so it cannot land in more cells than that
    sample contains, and a reader needs to see that the bound is not what is binding.
    """
    import numpy as np

    from tools import space_filling_sample as sfs

    space = sfs.output_space(sample=sample, seed=seed)
    z = sfs._standardise(space["values"], space["weights"])
    drawn = sfs.select(z, max(ns), seed=seed)
    cell_of = np.asarray(space["index"]) // space["n_cases"]

    landed = {}
    for n in sorted(ns):
        if n > len(drawn):
            continue
        landed[n] = int(len(set(cell_of[drawn[:n]].tolist())))
    return {
        "houses_drawn_to_cells_landed_in": landed,
        "cells_available_in_the_sample": int(len(set(cell_of.tolist()))),
        "sample_points": int(len(space["values"])),
    }


def measurement(ks=DEFAULT_KS, space=None, seed: int = 0) -> dict:
    """The published table: the three rivals at matched counts, and where each reaches the targets."""
    space = space if space is not None else stock_response()
    rows = coverage_curve(ks, space, seed)
    return {
        "cells_partitioned": space["cells"],
        "house_cases": space["cases"],
        "households": round(space["households"]),
        "embedding_energy_retained": space["energy_retained"],
        "curve": rows,
        "cells_needed": {
            name: {f"{int(t * 100)}pc": cells_for(t, rows, name) for t in TARGETS}
            for name in BUILDERS},
        "swept_to": max(row["cells"] for row in rows),
        "declares": REDUCES_OVER.banner(),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--curve", action="store_true",
                    help="the three rivals on one metric at matched cell counts")
    ap.add_argument("--separable", action="store_true",
                    help="per-driver clusters crossed, at the count they actually realise")
    ap.add_argument("--derived-cells", action="store_true",
                    help="how many distinct cells the space-filling draw landed in")
    ap.add_argument("--max-cells", type=int, default=None, help="stop the sweep at this k")
    args = ap.parse_args(argv)

    if args.derived_cells:
        print(json.dumps(derived_cell_count(), indent=2))
        return 0
    if args.separable:
        print(json.dumps(separable_curve(), indent=2))
        return 0
    if args.curve:
        ks = tuple(k for k in DEFAULT_KS if args.max_cells is None or k <= args.max_cells)
        print(json.dumps(measurement(ks), indent=2))
        return 0
    ap.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
