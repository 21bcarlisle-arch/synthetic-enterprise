"""EP13: IS EMBEDDED GENERATION THE NEW INPUT? — the ceiling of the hypothesis, before the build.

REUSE: tools/ep13_embedded_generation_bound.py
CLASS: CUSTOM
INDEX: searched "embedded", "ceiling", "bound", "oracle", "within-day", "placebo",
       "third coordinate", "new input". `tools/ep13_input_ceiling.py` is the nearest organ and
       this module IMPORTS its binning, its split, its shuffle and its coordinate reduction
       rather than restating them — the two measurements are only comparable if they bin, split
       and score identically, and the way to guarantee that is to run the same code. It is a
       separate file for one reason: `ep13_input_ceiling` measures a ceiling on the model's
       EXISTING inputs and its central treatment may never be published, while this one measures
       a CANDIDATE input that is perfectly legal to publish. Those two have opposite dispositions
       on the only question that matters downstream — may the build proceed — and merging them
       would put an illegal treatment and a legal one behind one name.

WHY THIS EXISTS
---------------
Seven passes have held EP13 at L2, and the seventh closed the dispatch programme by measuring
its ceiling instead of building its next term. From this atom's own record, quoted:

    "L3 therefore needs a NEW INPUT carrying within-day timing, not a better model of the
     inputs it has; embedded generation is the hypothesis and is DISCOVER work, unmeasured."

So this measures it — before an adapter is wired into anything, before a dispatch model reads
it, and before the atom spends an eighth pass. That ordering is the method the last two passes
established: the biomass outage model was retired by bounding it one term down, the whole merit
-order programme was retired by bounding it one level up, and both saved a build. A hypothesis
that arrives with a ceiling attached is worth more than one that arrives with a model attached.

THE HYPOTHESIS, stated so it can lose. The reconstruction reads demand at Elexon's TRANSMISSION
boundary (INDO) and renewables that are TRANSMISSION-CONNECTED (AGWS). Generation embedded in
the distribution networks is invisible to both: it shows up only as demand that never arrived.
So a summer midday dip in the model's inputs is ambiguous between a country using less power and
a country generating it below the metering point — two states with opposite carbon consequences
and an identical signature. If that ambiguity is what the within-day axis is losing, then NESO's
published embedded estimate resolves it and correlation should rise. If it is not, it will not.

WHY 3-D vs 2-D IS NOT THE MEASUREMENT, and this is the whole design. Adding ANY third coordinate
multiplies the cell count, and a finer partition fits better whether or not the new axis carries
information. Comparing a 3-D ceiling against the 2-D ceiling would therefore confound "embedded
generation carries timing" with "192 cells beat 120 cells", and would report a gain for a column
of random numbers. The verdict here rests on PLACEBO rungs instead — the same grid, the same cell
count, the same everything, with only the INFORMATION in the third coordinate destroyed:

  ceiling_3d          (u, v, w) with w = embedded generation / demand. The hypothesis.
  placebo_shuffled    w dealt to other half hours. Destroys ALL of w's structure while preserving
                      its value distribution EXACTLY -- so the bins, the edges and the cell count
                      are identical to `ceiling_3d` by construction. This rung prices the CELLS.
  placebo_day_mean    w replaced by its own DAY MEAN. Destroys w's WITHIN-DAY structure and keeps
                      its between-day structure. This rung prices the axis that actually holds
                      the level, and it is the sharper of the two: the biomass pass found 70-86%
                      of that fleet's variance was BETWEEN days, which is why a candidate input
                      can look informative and still be worthless to this atom.

  embedded_gain_over_cells    = ceiling_3d - placebo_shuffled   what w buys over a random column
  embedded_gain_within_day    = ceiling_3d - placebo_day_mean   what w's TIMING buys. THE NUMBER.

AND A NULL RESULT HAS TO BE FALSIFIABLE, which is what `oracle_probe` is for. "We added the
coordinate and correlation did not move" has two readings — the input carries nothing, or the
INSTRUMENT cannot see a third coordinate at all (too coarse, too few cells per bin, fallbacks
eating the signal). Those are opposite conclusions from the same number. So the same machinery is
run once more with w set to the TARGET's own within-day deviation: an oracle, illegal to publish,
and the strongest within-day third coordinate that could possibly exist. If the instrument shows
a large gain there and none for embedded generation, the null is about the input. If it shows
nothing there either, the null is about the instrument and says nothing about the hypothesis.
That rung is the difference between "we measured nothing" and "we proved there is nothing".

WHAT A POSITIVE RESULT WOULD AND WOULD NOT LICENCE. A ceiling bounds a MODEL CLASS; it does not
promise a buildable model reaches it. A high ceiling here would licence the BUILD — an adapter
already exists in `sim/neso_embedded_generation.py` — and nothing more. A low ceiling refuses it,
and that is the direction this atom has twice needed.

THE INPUT IS LEGAL, unlike the two bounds this one is modelled on, and the difference is
deliberate rather than an oversight in copying them. `ep13_biomass_oracle_bound` and
`ep13_input_ceiling` both carry an AST control proving their treatment cannot reach the published
feed, because both are fitted against NESO's outturn and are NESO's arithmetic by construction.
Embedded generation is not: it is a published estimate on a public page that any real supplier
reads, so `sim/neso_embedded_generation.py` is a legitimate runtime input and copying that
control here would be a control that cannot fail. What IS structural here is the oracle rung —
`oracle_probe` is built from the target and is an instrument check only, so it carries its own
unreachability walk, and only it does.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Mapping, Sequence

from sim import neso_carbon_intensity as neso
from sim import neso_embedded_generation as embedded
from tools.ep13_input_ceiling import (
    MIN_FIT_OCCUPANCY,
    _bin_of,
    _quantile_edges,
    coordinates,
    held_out,
    shuffled,
)

PROJECT_DIR = Path(__file__).resolve().parents[1]
OUT_PATH = PROJECT_DIR / "docs" / "observability" / "ep13_embedded_generation_bound.json"

#: The 3-D grid. Coarser on u and v than `ep13_input_ceiling`'s 24x5 SO THAT the third axis can
#: be afforded at all. 16x4x3 = 192 cells was tried first and MEASURED to fail the occupancy
#: control -- 10-15% of scored half hours fell back to the u-marginal in four years of six, and
#: a fallback is precisely where the third coordinate stops being read, so the rung that most
#: needed the resolution was the one losing the signal. 12x4x3 = 144 against roughly 8,700
#: fit-side half hours is ~60 per cell. The grid was set by the control, not chosen to suit the
#: answer; `sweep()` reports every resolution either way.
U_BINS, V_BINS, W_BINS = 12, 4, 3

#: Grids for the sweep. Same purpose as the sibling module's: to tell "the input is exhausted"
#: from "this partition is too coarse to see it", which no single resolution can.
SWEEP_GRIDS = ((8, 3, 2), (12, 4, 3), (16, 4, 3), (20, 5, 4), (24, 5, 5))

NULL_SEEDS = (20260827, 11, 4242, 90210, 7)

#: Seed for the placebo shuffle. Distinct from the null seeds so that a placebo rung and a null
#: rung can never accidentally be the same draw.
PLACEBO_SEED = 606


def day_mean_series(
    values: Mapping[tuple[str, int], float],
) -> dict[tuple[str, int], float]:
    """Every half hour replaced by the mean of its own DAY.

    The between-day placebo. A coordinate reduced this way still knows which days were windy and
    which were still — it has simply been made blind to the ordering WITHIN each day, which is
    the axis this atom's level turns on.
    """
    totals: dict[str, list[float]] = {}
    for (date_str, _period), value in values.items():
        totals.setdefault(date_str, []).append(float(value))
    means = {date_str: sum(v) / len(v) for date_str, v in totals.items()}
    return {key: means[key[0]] for key in values}


def within_day_deviation(
    values: Mapping[tuple[str, int], float],
) -> dict[tuple[str, int], float]:
    """Each half hour less its own day's mean — a series carrying ONLY within-day structure.

    Applied to the TARGET this is the oracle probe's coordinate: the best conceivable within-day
    third axis, and therefore the instrument's own upper reference point.
    """
    day_means = day_mean_series(values)
    return {key: float(values[key]) - day_means[key] for key in values}


def _within_day_spread(
    values: Mapping[tuple[str, int], float], keys: Sequence[tuple[str, int]]
) -> float:
    deviation = within_day_deviation({k: values[k] for k in keys})
    n = len(deviation)
    if n < 2:
        return 0.0
    return (sum(d * d for d in deviation.values()) / n) ** 0.5


def _matched_scale(
    real: Mapping[tuple[str, int], float],
    deviation: Mapping[tuple[str, int], float],
    keys: Sequence[tuple[str, int]],
) -> float:
    """Scale the oracle's timing term to the SAME within-day spread the real coordinate has.

    Without this the oracle would differ from the candidate on two counts at once — how much
    timing it carries and how far its values range — and quantile bins respond to the second.
    Matching the spread makes the probe answer the question it is asked: at this resolution, and
    with a third axis of THIS size, can a perfect timing signal be seen?
    """
    real_spread = _within_day_spread(real, keys)
    oracle_spread = _within_day_spread(deviation, keys)
    if oracle_spread <= 0.0:
        return 0.0
    return real_spread / oracle_spread


def _edges_for(
    fit_keys: Sequence[tuple[str, int]],
    coords: Mapping[tuple[str, int], tuple[float, ...]],
    bins: Sequence[int],
) -> list[list[float]]:
    return [
        _quantile_edges([coords[k][axis] for k in fit_keys], bins[axis])
        for axis in range(len(bins))
    ]


def fit_surface_nd(
    fit_keys: Sequence[tuple[str, int]],
    coords: Mapping[tuple[str, int], tuple[float, ...]],
    target: Mapping[tuple[str, int], float],
    bins: Sequence[int],
) -> dict:
    """The best possible function of the given coordinates at this resolution, as cell means.

    The N-dimensional statement of `ep13_input_ceiling.fit_surface`, and it stands as a bound for
    the identical reason: a cell mean is the squared-error-optimal answer within its cell, and
    among functions constant on cells the correlation-maximiser is an affine transform of the
    cell means, so this surface maximises correlation too.

    The FALLBACK is the FIRST axis's marginal, matching the sibling module — an under-occupied
    cell answers from its u-band rather than from the grand mean, because u is the coordinate the
    dispatch is mostly a function of and falling all the way back would throw away more than the
    cell was failing to supply. Fallbacks are counted and returned, never absorbed.
    """
    usable = [k for k in fit_keys if k in coords and k in target]
    if not usable:
        raise ValueError("no fit half hour carries both coordinates and a target")
    edges = _edges_for(usable, coords, bins)

    cells: dict[tuple[int, ...], list[float]] = {}
    marginal: dict[int, list[float]] = {}
    for key in usable:
        point = coords[key]
        index = tuple(_bin_of(point[axis], edges[axis]) for axis in range(len(bins)))
        cells.setdefault(index, []).append(target[key])
        marginal.setdefault(index[0], []).append(target[key])

    effective = 1.0
    for axis_edges in edges:
        effective *= len(axis_edges) + 1
    return {
        "edges": edges,
        "effective_cells": effective,
        "cell_mean": {k: sum(v) / len(v) for k, v in cells.items()},
        "cell_count": {k: len(v) for k, v in cells.items()},
        "marginal_mean": {k: sum(v) / len(v) for k, v in marginal.items()},
        "grand_mean": sum(target[k] for k in usable) / len(usable),
    }


def apply_surface_nd(
    keys: Sequence[tuple[str, int]],
    coords: Mapping[tuple[str, int], tuple[float, ...]],
    surface: Mapping,
) -> tuple[dict[tuple[str, int], float], int]:
    """(fitted values, fallbacks used). The fallback count is RETURNED, never swallowed."""
    edges = surface["edges"]
    out: dict[tuple[str, int], float] = {}
    fallbacks = 0
    for key in keys:
        if key not in coords:
            continue
        point = coords[key]
        index = tuple(_bin_of(point[axis], edges[axis]) for axis in range(len(edges)))
        if surface["cell_count"].get(index, 0) >= MIN_FIT_OCCUPANCY:
            out[key] = surface["cell_mean"][index]
        else:
            fallbacks += 1
            out[key] = surface["marginal_mean"].get(index[0], surface["grand_mean"])
    return out, fallbacks


def build_coordinates(
    base: Mapping[tuple[str, int], tuple[float, float]],
    third: Mapping[tuple[str, int], float] | None,
) -> dict[tuple[str, int], tuple[float, ...]]:
    """(u, v) from the sibling module, optionally with a third axis appended.

    Only half hours carrying BOTH are kept. That intersection is taken ONCE and shared by every
    rung — a rung scored on a different population than the rung it is compared against is not a
    comparison, and the treatment itself decides which half hours have a third coordinate.
    """
    if third is None:
        return {key: tuple(value) for key, value in base.items()}
    return {
        key: (base[key][0], base[key][1], float(third[key]))
        for key in base
        if key in third
    }


def oracle_is_unreachable_from(source: str) -> bool:
    """True when nothing in `source` imports this module — an AST walk, not a substring search.

    The same walk as `ep13_input_ceiling.ceiling_is_unreachable_from`, and here it guards ONE
    rung rather than the module's whole purpose: `oracle_probe` is built from the target and is
    an instrument check that may never reach a published number. The embedded-generation rungs
    carry no such prohibition and are not what this protects.
    """
    tree = ast.parse(source)
    mine = Path(__file__).stem
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name.split(".")[-1] == mine for alias in node.names):
                return False
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[-1] == mine:
                return False
            if any(alias.name == mine for alias in node.names):
                return False
    return True


def _score(
    fit_keys: Sequence[tuple[str, int]],
    score_keys: Sequence[tuple[str, int]],
    coords: Mapping[tuple[str, int], tuple[float, ...]],
    published: Mapping[tuple[str, int], float],
    demand: Mapping[tuple[str, int], float],
    bins: Sequence[int],
    year: str,
) -> dict:
    surface = fit_surface_nd(fit_keys, coords, published, bins)
    scored, fallbacks = apply_surface_nd(score_keys, coords, surface)
    in_sample, _ = apply_surface_nd(fit_keys, coords, surface)
    return {
        "held_out": neso.compare_shapes(scored, published, demand, year),
        "in_sample": neso.compare_shapes(in_sample, published, demand, year),
        "cells": surface["effective_cells"],
        "occupancy_fallback_share": float(fallbacks) / max(1, len(score_keys)),
        "min_used_cell_count": float(
            min((c for c in surface["cell_count"].values() if c >= MIN_FIT_OCCUPANCY), default=0)
        ),
    }


def measure_year(
    year: str,
    *,
    shipped: Mapping[tuple[str, int], float],
    published: Mapping[tuple[str, int], float],
    demand: Mapping[tuple[str, int], float],
    base_coords: Mapping[tuple[str, int], tuple[float, float]],
    embedded_intensive: Mapping[tuple[str, int], float],
    bins: Sequence[int] = (U_BINS, V_BINS, W_BINS),
    null_seeds: Sequence[int] = NULL_SEEDS,
) -> dict:
    """Every rung for one year, on ONE shared population of half hours.

    THE POPULATION IS THE INTERSECTION, and it is taken before any rung is fitted: a half hour
    enters only if the shipped model, the published target, a positive demand reading, both base
    coordinates and an embedded reading all exist for it. The 2-D rung is then scored on that
    same restricted population rather than on every half hour it could have used, so that
    ceiling_2d and ceiling_3d differ in the third axis and NOT in which days they saw. The
    treatment decides the attrition, so the treatment's population is the one everything uses.
    """
    year_keys = [
        k
        for k in shipped
        if k[0][:4] == year
        and k in published
        and k in base_coords
        and k in embedded_intensive
        and float(demand.get(k) or 0.0) > 0.0
    ]
    fit_keys = [k for k in year_keys if not held_out(k[0])]
    score_keys = [k for k in year_keys if held_out(k[0])]
    if not fit_keys or not score_keys:
        raise neso.NesoIntensityUnavailable(f"{year} does not split into fit and score halves")

    w_real = {k: embedded_intensive[k] for k in year_keys}
    w_shuffled = shuffled(w_real, year_keys, PLACEBO_SEED)
    w_day_mean = day_mean_series(w_real)
    # THE ORACLE IS BUILT ON THE SAME BETWEEN-DAY BASE AS THE CONTROL IT IS SCORED AGAINST, and
    # the first run of this instrument got that wrong in a way worth recording. A coordinate of
    # PURE within-day deviation was tried, and it scored BELOW the day-mean placebo in all six
    # years -- which reads as "the instrument is blind" and is nothing of the sort. The two rungs
    # simply carried disjoint information: the placebo had all of the between-day structure and
    # none of the timing, the oracle had all of the timing and none of the between-day structure,
    # and between-day is worth more of a year-long correlation than timing is. Their difference
    # was never within-day headroom. The oracle is therefore w's OWN day means PLUS the target's
    # within-day deviation, so it differs from the control rung in the timing term ALONE -- and
    # `day_mean_series(w_oracle)` is `w_day_mean` exactly, because a within-day deviation has
    # zero mean within every day, which is what makes the control rung literally shared.
    oracle_deviation = within_day_deviation({k: published[k] for k in year_keys})
    w_oracle = {
        k: w_day_mean[k] + _matched_scale(w_real, oracle_deviation, year_keys) * oracle_deviation[k]
        for k in year_keys
    }

    coords_2d = build_coordinates({k: base_coords[k] for k in year_keys}, None)
    coords_3d = build_coordinates({k: base_coords[k] for k in year_keys}, w_real)

    def scored(coords, axis_bins):
        return _score(fit_keys, score_keys, coords, published, demand, axis_bins, year)

    row: dict[str, object] = {
        "baseline": neso.compare_shapes(
            {k: shipped[k] for k in score_keys}, published, demand, year
        ),
        "baseline_in_sample": neso.compare_shapes(
            {k: shipped[k] for k in fit_keys}, published, demand, year
        ),
        "ceiling_2d": scored(coords_2d, bins[:2]),
        "ceiling_3d": scored(coords_3d, bins),
        "placebo_shuffled": scored(
            build_coordinates({k: base_coords[k] for k in year_keys}, w_shuffled), bins
        ),
        "placebo_day_mean": scored(
            build_coordinates({k: base_coords[k] for k in year_keys}, w_day_mean), bins
        ),
        "oracle_probe": scored(
            build_coordinates({k: base_coords[k] for k in year_keys}, w_oracle), bins
        ),
    }

    # THE NULL, on the 3-D grid: the same surface refitted against a SHUFFLED TARGET. Distinct
    # from the placebos, which shuffle a COORDINATE. This one asks whether 144 cells manufacture
    # correlation out of nothing at all; the placebos ask what the third coordinate adds.
    nulls = []
    for seed in null_seeds:
        null_surface = fit_surface_nd(
            fit_keys, coords_3d, shuffled(published, fit_keys, seed), bins
        )
        null_scored, _ = apply_surface_nd(score_keys, coords_3d, null_surface)
        nulls.append(neso.compare_shapes(null_scored, published, demand, year)["correlation"])

    corr = {name: row[name]["held_out"]["correlation"] for name in
            ("ceiling_2d", "ceiling_3d", "placebo_shuffled", "placebo_day_mean", "oracle_probe")}
    row["null_correlations"] = nulls
    row["null_abs_max"] = max(abs(n) for n in nulls)
    row["control_fit_half_hours"] = float(len(fit_keys))
    row["control_scored_half_hours"] = float(len(score_keys))

    # THE TWO GAINS THAT ARE THE POINT, both against a rung with the SAME cell count.
    row["embedded_gain_over_cells"] = corr["ceiling_3d"] - corr["placebo_shuffled"]
    row["embedded_gain_within_day"] = corr["ceiling_3d"] - corr["placebo_day_mean"]
    # Reported for context and deliberately NOT the verdict: it is confounded with cell count.
    row["naive_gain_vs_2d"] = corr["ceiling_3d"] - corr["ceiling_2d"]
    # What the instrument CAN see, on the same grid. The scale every gain above is read against.
    row["oracle_headroom_within_day"] = corr["oracle_probe"] - corr["placebo_day_mean"]
    row["controls"] = verdicts(row)
    return row


def verdicts(row: Mapping[str, object]) -> dict[str, bool]:
    """The controls, computed from the row just published rather than only asserted elsewhere."""
    three_d = row["ceiling_3d"]
    return {
        # CONTROL 1, the fit must BITE: a surface that cannot beat the shipped model on the half
        # hours it was fitted to has either not been fitted or is too coarse to represent what
        # build_shape already does.
        "fit_bites_in_sample": three_d["in_sample"]["correlation"]
        > row["baseline_in_sample"]["correlation"],
        # CONTROL 2, occupancy: the cells that answered were populations, not memories. This is
        # the control the third axis most endangers, since it triples the cell count.
        "cells_are_populations": three_d["min_used_cell_count"] >= MIN_FIT_OCCUPANCY
        and three_d["occupancy_fallback_share"] < 0.10,
        # CONTROL 3, the null must COLLAPSE, against a threshold DERIVED from the resolution
        # rather than chosen: the cell means are the effective sample, so 3/sqrt(cells).
        "null_collapses": row["null_abs_max"] < 3.0 / (three_d["cells"] ** 0.5),
        # CONTROL 4, the placebo comparison must be CELL-MATCHED, or the gains are confounded
        # with resolution and mean nothing. NOTE HONESTLY: for `placebo_shuffled` this holds BY
        # CONSTRUCTION -- shuffling preserves the value multiset, so the quantile edges are
        # identical -- and it is therefore NOT evidence there. It can only fail for
        # `placebo_day_mean`, whose values are genuinely different and whose edges may collapse
        # onto a point mass. That is the case this control exists for.
        "placebos_are_cell_matched": (
            row["placebo_shuffled"]["cells"] == three_d["cells"]
            and row["placebo_day_mean"]["cells"] == three_d["cells"]
        ),
        # CONTROL 5, the instrument must be ABLE to see a within-day third axis at all. Without
        # this a null result on embedded generation is unreadable: it would be equally consistent
        # with an uninformative input and with a blind instrument.
        "instrument_can_see_within_day": row["oracle_headroom_within_day"] > 0.05,
    }


def sweep(
    *,
    shipped: Mapping[tuple[str, int], float],
    published: Mapping[tuple[str, int], float],
    demand: Mapping[tuple[str, int], float],
    base_coords: Mapping[tuple[str, int], tuple[float, float]],
    embedded_intensive: Mapping[tuple[str, int], float],
    grids: Sequence[tuple[int, int, int]],
    years: Sequence[str],
) -> dict:
    """The gains at every resolution — the control deciding what the answer is an answer OF.

    A single grid cannot separate "the input carries no within-day timing" from "this partition
    is too coarse to see the timing it carries". If the within-day gain stays flat as the grid
    refines while the oracle's headroom grows, the input is exhausted and the refinement is being
    spent on the oracle's real signal. If the gain climbs with resolution, no ceiling may be
    claimed at any of these grids.
    """
    out: dict[str, dict] = {}
    for grid in grids:
        gains_within_day, gains_over_cells, oracle, cells = [], [], [], []
        for year in years:
            try:
                row = measure_year(
                    year,
                    shipped=shipped,
                    published=published,
                    demand=demand,
                    base_coords=base_coords,
                    embedded_intensive=embedded_intensive,
                    bins=grid,
                    null_seeds=(NULL_SEEDS[0],),
                )
            except (neso.NesoIntensityUnavailable, ValueError):
                continue
            gains_within_day.append(row["embedded_gain_within_day"])
            gains_over_cells.append(row["embedded_gain_over_cells"])
            oracle.append(row["oracle_headroom_within_day"])
            cells.append(row["ceiling_3d"]["cells"])
        if not gains_within_day:
            continue
        out["x".join(str(g) for g in grid)] = {
            "cells": sum(cells) / len(cells),
            "mean_embedded_gain_within_day": sum(gains_within_day) / len(gains_within_day),
            "mean_embedded_gain_over_cells": sum(gains_over_cells) / len(gains_over_cells),
            "mean_oracle_headroom": sum(oracle) / len(oracle),
            "max_embedded_gain_within_day": max(gains_within_day),
        }
    return out


def measure() -> dict:
    """The bound, over every year the series share. Loads the real caches."""
    from sim import grid_carbon_intensity as gci
    from sim.generation_demand_history import aggregate_renewable_generation
    from sim.grid_carbon_intensity import aggregate_demand
    from tools.generate_grid_intensity_feed import AGWS_CACHE, DEMAND_CACHE, fuel_mix

    demand = aggregate_demand(json.loads(Path(DEMAND_CACHE).read_text(encoding="utf-8")))
    renewables = aggregate_renewable_generation(
        json.loads(Path(AGWS_CACHE).read_text(encoding="utf-8"))
    )
    (imports, coal_capacity, _coverage, thermal_floors, must_run, _mrc, _envelope) = fuel_mix()
    thermal_floor = {y: r["floor_mw"] for y, r in thermal_floors.items()}
    published = neso.actual_by_period(neso.to_settlement_periods(neso.load_cached()))

    embedded_mw = embedded.total_by_period(
        embedded.to_settlement_periods(embedded.load_cached())
    )

    shipped = gci.build_shape(
        demand,
        renewables,
        imports_by_period=imports,
        coal_capacity_by_year=coal_capacity,
        thermal_floor_by_year=thermal_floor,
        zero_carbon_must_run_by_period=must_run,
        biomass_envelope_by_year=None,
    )
    base_coords = coordinates(
        list(shipped),
        demand_by_period=demand,
        renewables_by_period=renewables,
        imports_by_period=imports,
        zero_carbon_must_run_by_period=must_run,
    )
    # INTENSIVE, like u and v, and for the same reason: the fit is scored in intensity space, so
    # a coordinate carried in MW would make the surface a function of the size of the system as
    # well as of its composition, and a year's demand growth would enter as timing.
    embedded_intensive = {
        key: embedded_mw[key] / demand[key]
        for key in embedded_mw
        if float(demand.get(key) or 0.0) > 0.0
    }

    years = sorted(
        {k[0][:4] for k in published}
        & {k[0][:4] for k in shipped}
        & {k[0][:4] for k in embedded_intensive}
    )
    rows: dict[str, dict] = {}
    for year in years:
        try:
            rows[year] = measure_year(
                year,
                shipped=shipped,
                published=published,
                demand=demand,
                base_coords=base_coords,
                embedded_intensive=embedded_intensive,
            )
        except (neso.NesoIntensityUnavailable, ValueError, embedded.EmbeddedGenerationUnavailable):
            continue

    return {
        "measured_from": "sim/cache (Elexon FUELHH + demand + AGWS, NESO Carbon Intensity, "
        "NESO Historic Demand Data embedded wind+solar)",
        "basis": neso.PUBLISHED_BASIS,
        "split": "fit on ODD days of the month, scored on EVEN days; whole days either side",
        "grid": {"u": U_BINS, "v": V_BINS, "w": W_BINS},
        "rungs": {
            "ceiling_2d": "best function of (u,v) -- the model's existing inputs",
            "ceiling_3d": "best function of (u,v,w), w = embedded generation / demand",
            "placebo_shuffled": "w dealt to other half hours -- prices the CELLS",
            "placebo_day_mean": "w replaced by its day mean -- prices the WITHIN-DAY axis",
            "oracle_probe": "w = the TARGET's within-day deviation -- INSTRUMENT CHECK, "
            "NOT PUBLISHABLE",
        },
        "verdict_rests_on": "embedded_gain_within_day = ceiling_3d - placebo_day_mean, "
        "read against oracle_headroom_within_day",
        "oracle_reaches_the_published_feed": not oracle_is_unreachable_from(
            (PROJECT_DIR / "tools" / "generate_grid_intensity_feed.py").read_text(
                encoding="utf-8"
            )
        ),
        "resolution_sweep": sweep(
            shipped=shipped,
            published=published,
            demand=demand,
            base_coords=base_coords,
            embedded_intensive=embedded_intensive,
            grids=SWEEP_GRIDS,
            years=sorted(rows),
        ),
        "years": rows,
    }


def main(argv: list[str] | None = None) -> int:
    data = measure()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, indent=1, default=str) + "\n", encoding="utf-8")
    for year, row in sorted(data["years"].items()):
        c = row["controls"]
        print(
            f"{year} n={int(row['control_scored_half_hours']):6d} "
            f"base={row['baseline']['correlation']:.4f} "
            f"2d={row['ceiling_2d']['held_out']['correlation']:.4f} "
            f"3d={row['ceiling_3d']['held_out']['correlation']:.4f} "
            f"shuf={row['placebo_shuffled']['held_out']['correlation']:.4f} "
            f"daymean={row['placebo_day_mean']['held_out']['correlation']:.4f} "
            f"ORACLE={row['oracle_probe']['held_out']['correlation']:.4f}"
        )
        print(
            f"      within-day gain={row['embedded_gain_within_day']:+.4f}  "
            f"over-cells={row['embedded_gain_over_cells']:+.4f}  "
            f"oracle headroom={row['oracle_headroom_within_day']:+.4f}  "
            f"| bite={'Y' if c['fit_bites_in_sample'] else 'N'} "
            f"pop={'Y' if c['cells_are_populations'] else 'N'} "
            f"null={'Y' if c['null_collapses'] else 'N'} "
            f"matched={'Y' if c['placebos_are_cell_matched'] else 'N'} "
            f"sees={'Y' if c['instrument_can_see_within_day'] else 'N'}"
        )
    print()
    print("RESOLUTION SWEEP -- does the within-day gain grow with resolution, or plateau?")
    for label, grid in sorted(data["resolution_sweep"].items(), key=lambda kv: kv[1]["cells"]):
        print(
            f"  {label:>8} ({int(grid['cells']):5d} cells)  "
            f"within-day={grid['mean_embedded_gain_within_day']:+.4f}  "
            f"over-cells={grid['mean_embedded_gain_over_cells']:+.4f}  "
            f"oracle={grid['mean_oracle_headroom']:+.4f}"
        )
    print(f"wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
