"""EP13: THE INPUT CEILING — how much correlation ANY dispatch model on these inputs could reach.

REUSE: tools/ep13_input_ceiling.py
CLASS: CUSTOM
INDEX: searched "ceiling", "bound", "oracle", "upper bound", "correlation", "within-day",
       "sufficient statistic", "residual demand". `tools/ep13_biomass_oracle_bound.py` is the
       nearest organ and this is the SAME MOVE ONE LEVEL UP: that one measured the ceiling of a
       single candidate term (biomass) before building an outage model for it, and retired the
       build. This one measures the ceiling of the WHOLE REMAINING PROGRAMME. It is a separate
       file for the same reason that one is: the treatment it measures is one the published feed
       is forbidden to use, and `test_the_ceiling_cannot_reach_the_published_feed` is a
       structural check rather than a promise. Every input is loaded through
       `generate_grid_intensity_feed.fuel_mix` and `sim/elexon_fuel_outturn.py`, and the baseline
       is `grid_carbon_intensity.build_shape` ITSELF rather than a reimplementation of it — so
       the "does the measurement route match the publishing route" control that
       `ep13_biomass_oracle_bound` has to compute does not arise here. There is one route.

WHY THIS EXISTS
---------------
`docs/design/maturity_map.yaml` has held EP13 at L2 through six passes. Five of them moved a
level error; the axis that actually holds the level is CORRELATION — 0.746 in 2024, "the shape
knows how clean a quiet half hour is and not which half hours were quiet". Coal, the cables, the
thermal floor, the measured must-run fleet and the biomass envelope have all been built, and the
correlation axis has moved 0.726 -> 0.746 in total.

`sim/grid_carbon_intensity.py` already states the structural reason, and states it as a claim:

    "A dispatch model handed demand, wind and solar can only be a function of residual demand;
     GB's actual intensity increasingly is not."

That claim has never been MEASURED, and it is the one that decides whether any further dispatch
work on this atom can reach L3. If it is right, the remaining programme is capped and the next
build is not a better merit order at all. Six passes of "build the next term, measure, still L2"
is the shape of a programme that should have measured its own ceiling first — which is precisely
what the biomass pass did do, one term down, and it saved an entire outage model.

So: hand the model's inputs to the BEST POSSIBLE function of them and see where correlation lands.

THE THREE RUNGS AND THE NULL, one process, identical caches, all four scored by the SAME
`neso.compare_shapes` over the SAME held-out half hours so the numbers are comparable:

  baseline             `build_shape` as shipped. Where the atom actually is.
  recalibration_ceiling the best possible function of THE MODEL'S OWN OUTPUT. Bounds every
                       post-hoc correction — every factor, curve and clamp of the kind the last
                       six passes applied. A correction cannot beat the best correction.
  input_ceiling        the best possible function of THE MODEL'S OWN INPUTS. Bounds every
                       dispatch model that can be built on demand, wind, solar, the measured
                       must-run fleet and the cables — however good its merit order, its
                       efficiency curve, its coal availability or its outage model. This is the
                       number the claim above is about.
  null_ceiling         the input ceiling refitted against a SHUFFLED target. The rung that makes
                       the other three falsifiable; see control 3.

WHY THE CEILING IS FITTED IN INTENSITY SPACE, and not in carbon space where it started. NESO's
series is LOSS-CORRECTED to a consumed basis and the reconstruction sits at Elexon's transmission
boundary, so `published_intensity * demand` is not GB's burnt carbon and subtracting an import
term from it would mix a basis difference into the target. Fitting the published INTENSITY
directly against intensive coordinates absorbs any per-year constant of that kind into the fit,
where it belongs and cannot be mistaken for timing. It also makes the null rung clean: with a
shuffled target the fitted surface goes flat and correlation goes to zero, which would not be
true of a carbon-space fit where the 1/demand term would carry real structure on its own.

THE TWO COORDINATES are the model's own reduction of its inputs, both intensive:

  u = thermal residual / demand   what the dispatch reduces its inputs to before deciding
                                  anything: demand less renewables, less the measured must-run
                                  block, less imports.
  v = import carbon / demand      the cables' contribution to intensity, which enters the answer
                                  additively and at NESO's own published factors.

A function of (u, v) is what a dispatch model IS, once the year scalars are fixed — and they are
fixed, because every rung is fitted and scored within a single year. Handing the fit the year
boundary is not a favour to it: it is what makes this a bound on the model rather than on the
model plus its calibration drift.

THIS TREATMENT MAY NEVER BE PUBLISHED. It is fitted against NESO's outturn, so it is NESO's
arithmetic by construction and every objection `sim/elexon_fuel_outturn.py` raises to handing
over half-hourly gas applies to it tenfold. An illegal treatment is still a legitimate BOUND,
because a bound is a fact about what is knowable and not a route to a number — the same
distinction `ep13_biomass_oracle_bound` draws, kept structural by the same kind of AST test.

WHAT THIS CANNOT SAY. A ceiling is an upper bound on a MODEL CLASS, not a prediction that any
buildable model reaches it. A high ceiling does not promise the build succeeds; a low ceiling
does prove it cannot. Only the second direction is load-bearing, and it is the direction the
atom needs.
"""

from __future__ import annotations

import ast
import json
import random
from pathlib import Path
from typing import Mapping, Sequence

from sim import grid_carbon_intensity as gci
from sim import neso_carbon_intensity as neso

PROJECT_DIR = Path(__file__).resolve().parents[1]
OUT_PATH = PROJECT_DIR / "docs" / "observability" / "ep13_input_ceiling.json"

RUNGS = ("baseline", "recalibration_ceiling", "input_ceiling", "null_ceiling")

#: Quantile bins for the input ceiling's two coordinates. 24 x 5 = 120 cells against roughly
#: 8,700 fit-side half hours a year is ~70 per cell — coarse enough that a cell is a population
#: rather than a memory, which is the whole difference between a ceiling and a lookup table.
U_BINS = 24
V_BINS = 5

#: Bins for the 1-D recalibration ceiling. More are affordable because there is one axis.
RECALIBRATION_BINS = 40

#: A fitted cell is only allowed to answer if this many fit-side half hours went into it.
#: Below it the cell falls back to its u-marginal, and the fallback is COUNTED and published
#: rather than taken quietly — an unreported fallback is how a memorising fit passes an
#: occupancy control (R15 fail-silent).
MIN_FIT_OCCUPANCY = 30

#: The shuffle seed. Fixed so the null rung is reproducible; the null's job is to collapse, and
#: a null that moved run to run could not be asserted against.
NULL_SEED = 20260827

#: SEVERAL seeds, because the null is a distribution and one draw of it is not a control. See
#: the note in `measure_year`: the surface takes one value per CELL, so the effective sample
#: behind a null correlation is the cell count, and single draws of ±0.2 are ordinary at 120
#: cells. The control reads the spread.
NULL_SEEDS = (20260827, 11, 4242, 90210, 7)

#: The grids `sweep()` walks. Coarse enough at one end that the binning binds, fine enough at the
#: other that memorisation is visible in the in-sample/held-out divergence — the point being to
#: SEE both failure modes rather than to pick a grid that avoids them.
SWEEP_GRIDS = ((8, 3), (16, 4), (24, 5), (40, 6), (64, 8))


def held_out(date: str) -> bool:
    """EVEN days of the month are scored, ODD days are fitted.

    WHOLE DAYS EITHER SIDE, which matters more here than the ratio does: the axis under
    measurement is WITHIN-DAY ordering, and a split that cut days in half would let the fit see
    the morning of a day it is then scored on the evening of. Day-of-month parity also splits
    inside every month, so both sides carry the same seasons — a chronological split would fit
    on winter and score on summer and report the season as a ceiling.
    """
    return int(date[8:10]) % 2 == 0


def _quantile_edges(values: Sequence[float], bins: int) -> list[float]:
    """Interior edges at equal-count quantiles, STRICTLY INCREASING.

    Equal COUNT, not equal WIDTH, because both coordinates are heavily skewed — equal width
    would put most half hours in one cell and measure the binning instead of the inputs.

    THE DEDUPLICATION IS NOT TIDINESS, and it was found by a test rather than reasoned out. A
    coordinate with a large POINT MASS — and `v` is exactly zero for every half hour before the
    cables existed — puts many requested quantiles on the same value. Left as duplicates, those
    edges create empty bins and the grid silently shrinks: the artefact would report 120 cells
    while the fit answered from a handful. Deduplicating cannot conjure resolution that the
    population does not support, and does not try to; what it does is make the count HONEST, so
    `effective_cells` says what the fit actually had and the null threshold derived from it is
    computed against the real number.
    """
    ordered = sorted(values)
    if not ordered:
        raise ValueError("no values to bin")
    candidates = [ordered[int(len(ordered) * i / bins)] for i in range(1, bins)]
    out: list[float] = []
    for edge in candidates:
        if edge > ordered[0] and (not out or edge > out[-1]):
            out.append(edge)
    return out


def _bin_of(value: float, edges: Sequence[float]) -> int:
    lo, hi = 0, len(edges)
    while lo < hi:
        mid = (lo + hi) // 2
        if value >= edges[mid]:
            lo = mid + 1
        else:
            hi = mid
    return lo


def coordinates(
    keys: Sequence[tuple[str, int]],
    *,
    demand_by_period: Mapping[tuple[str, int], float],
    renewables_by_period: Mapping[tuple[str, int], float],
    imports_by_period: Mapping[tuple[str, int], tuple[float, float]],
    zero_carbon_must_run_by_period: Mapping[tuple[str, int], float],
) -> dict[tuple[str, int], tuple[float, float]]:
    """{key: (u, v)} — the model's own reduction of its inputs, for the half hours given.

    The clamps and the fallback are `emissions_rate_t_per_mwh`'s, deliberately and identically:
    an import is clamped at zero and at demand because a half hour cannot be met more than once,
    and an absent must-run reading falls back to the flat block rather than to zero, because an
    absent reading is not a fleet that stopped. A ceiling fitted on coordinates the dispatch
    does not actually see would bound a different model than the one shipped.
    """
    out: dict[tuple[str, int], tuple[float, float]] = {}
    for key in keys:
        demand_mw = float(demand_by_period.get(key) or 0.0)
        renewable_mw = renewables_by_period.get(key)
        if demand_mw <= 0.0 or renewable_mw is None:
            continue
        import_mw, import_rate = imports_by_period.get(key, (0.0, 0.0))
        import_mw = min(max(0.0, float(import_mw)), demand_mw)
        must_run = zero_carbon_must_run_by_period.get(key)
        must_run_mw = (
            gci.MUST_RUN_ZERO_CARBON_MW if must_run is None else max(0.0, float(must_run))
        )
        residual_mw = demand_mw - float(renewable_mw) - import_mw - must_run_mw
        out[key] = (residual_mw / demand_mw, (import_mw * float(import_rate)) / demand_mw)
    return out


def fit_surface(
    fit_keys: Sequence[tuple[str, int]],
    coords: Mapping[tuple[str, int], tuple[float, float]],
    target: Mapping[tuple[str, int], float],
    u_bins: int = U_BINS,
    v_bins: int = V_BINS,
) -> dict:
    """The best possible function of (u, v) AT THIS RESOLUTION, as cell means over the fit half
    hours.

    A cell mean IS the best possible answer for that cell under squared error, and among
    functions of the cell the correlation-maximiser is an affine transform of the cell mean —
    correlation being invariant to affine transforms, the cell-mean surface therefore maximises
    correlation too. That is what lets this stand as a bound rather than as one more model.

    THE BOUND IS ONLY AS FINE AS THE BINNING, and that caveat is load-bearing rather than
    pedantic: `build_shape` is a function of the same coordinates at CONTINUOUS resolution, so a
    surface too coarse to represent it can score BELOW it and report a ceiling beneath the floor.
    That is not a paradox and it is not noise — it is the binning being the binding constraint
    instead of the inputs. `sweep()` exists to tell those two apart, and no single resolution's
    number should be read without it.
    """
    usable = [k for k in fit_keys if k in coords and k in target]
    if not usable:
        raise ValueError("no fit half hour carries both coordinates and a target")
    u_edges = _quantile_edges([coords[k][0] for k in usable], u_bins)
    v_edges = _quantile_edges([coords[k][1] for k in usable], v_bins)

    cells: dict[tuple[int, int], list[float]] = {}
    marginal: dict[int, list[float]] = {}
    for key in usable:
        u, v = coords[key]
        iu, iv = _bin_of(u, u_edges), _bin_of(v, v_edges)
        cells.setdefault((iu, iv), []).append(target[key])
        marginal.setdefault(iu, []).append(target[key])

    grand = sum(target[k] for k in usable) / len(usable)
    return {
        "u_edges": u_edges,
        "v_edges": v_edges,
        # WHAT THE FIT ACTUALLY HAD, after a point mass collapsed whatever edges it collapsed.
        # The requested grid is an intention; this is the number every derived threshold reads.
        "effective_cells": float((len(u_edges) + 1) * (len(v_edges) + 1)),
        "cell_mean": {k: sum(v) / len(v) for k, v in cells.items()},
        "cell_count": {k: len(v) for k, v in cells.items()},
        "marginal_mean": {k: sum(v) / len(v) for k, v in marginal.items()},
        "grand_mean": grand,
    }


def apply_surface(
    keys: Sequence[tuple[str, int]],
    coords: Mapping[tuple[str, int], tuple[float, float]],
    surface: Mapping,
) -> tuple[dict[tuple[str, int], float], int]:
    """(fitted rates, fallbacks used). The fallback count is RETURNED, never swallowed."""
    out: dict[tuple[str, int], float] = {}
    fallbacks = 0
    for key in keys:
        if key not in coords:
            continue
        u, v = coords[key]
        iu = _bin_of(u, surface["u_edges"])
        iv = _bin_of(v, surface["v_edges"])
        count = surface["cell_count"].get((iu, iv), 0)
        if count >= MIN_FIT_OCCUPANCY:
            out[key] = surface["cell_mean"][(iu, iv)]
        else:
            fallbacks += 1
            out[key] = surface["marginal_mean"].get(iu, surface["grand_mean"])
    return out, fallbacks


def fit_1d(
    fit_keys: Sequence[tuple[str, int]],
    source: Mapping[tuple[str, int], float],
    target: Mapping[tuple[str, int], float],
    bins: int = RECALIBRATION_BINS,
) -> dict:
    """The best possible function of ONE series — used to bound post-hoc recalibration."""
    usable = [k for k in fit_keys if k in source and k in target]
    if not usable:
        raise ValueError("no fit half hour carries both the source series and a target")
    edges = _quantile_edges([source[k] for k in usable], bins)
    cells: dict[int, list[float]] = {}
    for key in usable:
        cells.setdefault(_bin_of(source[key], edges), []).append(target[key])
    return {
        "edges": edges,
        "cell_mean": {k: sum(v) / len(v) for k, v in cells.items()},
        "cell_count": {k: len(v) for k, v in cells.items()},
        "grand_mean": sum(target[k] for k in usable) / len(usable),
    }


def apply_1d(
    keys: Sequence[tuple[str, int]],
    source: Mapping[tuple[str, int], float],
    surface: Mapping,
) -> dict[tuple[str, int], float]:
    out: dict[tuple[str, int], float] = {}
    for key in keys:
        if key not in source:
            continue
        idx = _bin_of(source[key], surface["edges"])
        out[key] = surface["cell_mean"].get(idx, surface["grand_mean"])
    return out


def shuffled(
    target: Mapping[tuple[str, int], float], keys: Sequence[tuple[str, int]], seed: int = NULL_SEED
) -> dict[tuple[str, int], float]:
    """The same target values, dealt to different half hours. CONTROL 3's input.

    The VALUE DISTRIBUTION is preserved exactly and only the TIMING is destroyed, which is what
    makes the null a test of the axis under measurement rather than of the scale of the numbers.
    """
    ordered = sorted(keys)
    values = [target[k] for k in ordered]
    random.Random(seed).shuffle(values)
    return dict(zip(ordered, values))


def _published_feed_source() -> str:
    return (PROJECT_DIR / "tools" / "generate_grid_intensity_feed.py").read_text(encoding="utf-8")


def ceiling_is_unreachable_from(source: str) -> bool:
    """True when nothing in `source` imports this module — an AST walk, not a substring search.

    Same walk, and same reason, as `ep13_biomass_oracle_bound.oracle_is_unreachable_from`: a
    substring search would be satisfied by this module's name in a comment and defeated by an
    import written any way but the one it looked for.
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


def measure_year(
    year: str,
    *,
    shipped: Mapping[tuple[str, int], float],
    published: Mapping[tuple[str, int], float],
    demand: Mapping[tuple[str, int], float],
    coords: Mapping[tuple[str, int], tuple[float, float]],
    u_bins: int = U_BINS,
    v_bins: int = V_BINS,
    null_seeds: Sequence[int] = (NULL_SEED,),
) -> dict:
    """Every rung for one year, scored on the held-out half hours only."""
    year_keys = [
        k
        for k in shipped
        if k[0][:4] == year and k in published and float(demand.get(k) or 0.0) > 0.0
    ]
    fit_keys = [k for k in year_keys if not held_out(k[0])]
    score_keys = [k for k in year_keys if held_out(k[0])]
    if not fit_keys or not score_keys:
        raise neso.NesoIntensityUnavailable(f"{year} does not split into fit and score halves")

    surface = fit_surface(fit_keys, coords, published, u_bins, v_bins)
    scored, fallbacks = apply_surface(score_keys, coords, surface)
    in_sample, _ = apply_surface(fit_keys, coords, surface)

    recal = fit_1d(fit_keys, shipped, published)
    recal_scored = apply_1d(score_keys, shipped, recal)

    # THE NULL IS A DISTRIBUTION, NOT A DRAW. One seed reported +0.24 in 2021 and that was read
    # as a failed control until the arithmetic was done: the surface takes only u_bins*v_bins
    # distinct values, so the effective sample behind this correlation is the CELL COUNT and not
    # the half-hour count, and a chance correlation of that size across ~120 cells is ordinary.
    # A single draw cannot tell an unlucky seed from a leaking fit; the spread across seeds can,
    # so the spread is what is published and what the control reads.
    nulls = []
    for seed in null_seeds:
        null_surface = fit_surface(
            fit_keys, coords, shuffled(published, fit_keys, seed), u_bins, v_bins
        )
        null_scored, _ = apply_surface(score_keys, coords, null_surface)
        nulls.append(neso.compare_shapes(null_scored, published, demand, year)["correlation"])

    rungs = {
        "baseline": {k: shipped[k] for k in score_keys},
        "recalibration_ceiling": recal_scored,
        "input_ceiling": scored,
    }
    row: dict[str, object] = {
        name: neso.compare_shapes(series, published, demand, year)
        for name, series in rungs.items()
    }
    row["baseline_in_sample"] = neso.compare_shapes(
        {k: shipped[k] for k in fit_keys}, published, demand, year
    )
    row["input_ceiling_in_sample"] = neso.compare_shapes(in_sample, published, demand, year)
    row["null_correlations"] = nulls
    row["null_abs_max"] = max(abs(n) for n in nulls)
    row["null_mean"] = sum(nulls) / len(nulls)
    row["cells"] = surface["effective_cells"]
    row["cells_requested"] = float(u_bins * v_bins)
    row["control_fit_half_hours"] = float(len(fit_keys))
    row["control_scored_half_hours"] = float(len(score_keys))
    row["control_occupancy_fallbacks"] = float(fallbacks)
    row["control_occupancy_fallback_share"] = float(fallbacks) / len(score_keys)
    row["control_min_used_cell_count"] = float(
        min((c for c in surface["cell_count"].values() if c >= MIN_FIT_OCCUPANCY), default=0)
    )
    # THE RIGOROUS BOUND, and the one line here that does not depend on the held-out split, the
    # seed, or the null: no function of the model's inputs AT THIS RESOLUTION can beat the
    # in-sample cell means on the very half hours they were fitted to. So the in-sample gain is
    # an UPPER BOUND on what any dispatch model on these inputs could buy at this resolution.
    row["in_sample_gain_upper_bound"] = (
        row["input_ceiling_in_sample"]["correlation"] - row["baseline_in_sample"]["correlation"]
    )
    row["held_out_gain"] = (
        row["input_ceiling"]["correlation"] - row["baseline"]["correlation"]
    )
    return row


def verdicts(row: Mapping[str, Mapping[str, float]]) -> dict[str, bool]:
    """The three controls, as booleans computed from the row that was just published.

    Returned rather than only asserted in a test, so a run says on its face whether its own
    controls held — a control whose verdict lives only in another process is one a reader of
    this file has to take on trust.
    """
    base = row["baseline"]["correlation"]
    ceiling = row["input_ceiling"]["correlation"]
    in_sample = row["input_ceiling_in_sample"]["correlation"]
    return {
        # CONTROL 1, the fit must BITE: a surface that cannot beat the shipped model on the very
        # half hours it was fitted to has either not been fitted (R15 fail-silent) or is too
        # COARSE to represent what `build_shape` already does. Those are different faults with
        # the same symptom, and only `sweep()` separates them — so this verdict is reported
        # alongside the sweep and never read alone.
        "fit_bites_in_sample": in_sample > row["baseline_in_sample"]["correlation"],
        # CONTROL 2, occupancy: the cells that answered were populations, not memories.
        "cells_are_populations": row["control_min_used_cell_count"] >= MIN_FIT_OCCUPANCY
        and row["control_occupancy_fallback_share"] < 0.10,
        # CONTROL 3, the null must COLLAPSE, judged against the resolution rather than a
        # constant. A surface of N cells fitted to a shuffled target still scores by chance, and
        # the scale of that chance is set by N: the cell means are the effective sample. The
        # threshold is therefore derived from the cell count and not chosen — 3/sqrt(N), which
        # is 0.27 at 120 cells and tightens as the grid refines. A null ABOVE it means the bins
        # are manufacturing correlation and every other number in the row is that artefact.
        "null_collapses": row["null_abs_max"] < 3.0 / (row["cells"] ** 0.5),
        # Reported, not a control: whether the ceiling clears the shipped model out of sample.
        "ceiling_exceeds_baseline_out_of_sample": ceiling > base,
    }


def sweep(
    *,
    shipped: Mapping[tuple[str, int], float],
    published: Mapping[tuple[str, int], float],
    demand: Mapping[tuple[str, int], float],
    coords: Mapping[tuple[str, int], tuple[float, float]],
    grids: Sequence[tuple[int, int]],
    years: Sequence[str],
) -> dict:
    """The resolution sweep — the control that decides what the ceiling is a ceiling OF.

    A single grid cannot distinguish the two readings of a low ceiling:

      THE INPUTS ARE EXHAUSTED   the coordinates carry no more usable timing information, so
                                 refining the grid buys nothing out of sample.
      THE GRID IS TOO COARSE     the coordinates carry more, and this binning cannot see it, so
                                 refining the grid buys real out-of-sample gain.

    They separate cleanly under refinement. If in-sample gain climbs while held-out gain stays
    flat or falls, the extra resolution is being spent on memorisation and the information limit
    has been reached — that plateau IS the ceiling. If held-out gain climbs too, it has not been,
    and no ceiling may be claimed at any of these resolutions.

    This is the difference between a measurement and a number, and on the first run it was the
    difference between two opposite conclusions: at 24x5 the 2019 surface scored BELOW the
    shipped model in sample, which read as a broken fit and is in fact a grid coarser than
    `build_shape`'s own continuous response.
    """
    out: dict[str, dict] = {}
    for u_bins, v_bins in grids:
        label = f"{u_bins}x{v_bins}"
        rows: dict[str, dict] = {}
        for year in years:
            try:
                row = measure_year(
                    year,
                    shipped=shipped,
                    published=published,
                    demand=demand,
                    coords=coords,
                    u_bins=u_bins,
                    v_bins=v_bins,
                )
            except (neso.NesoIntensityUnavailable, ValueError):
                continue
            rows[year] = {
                "in_sample_gain_upper_bound": row["in_sample_gain_upper_bound"],
                "held_out_gain": row["held_out_gain"],
                "baseline": row["baseline"]["correlation"],
                "input_ceiling": row["input_ceiling"]["correlation"],
                "occupancy_fallback_share": row["control_occupancy_fallback_share"],
            }
        if rows:
            out[label] = {
                "cells": float(u_bins * v_bins),
                "years": rows,
                "mean_in_sample_gain": sum(
                    r["in_sample_gain_upper_bound"] for r in rows.values()
                )
                / len(rows),
                "mean_held_out_gain": sum(r["held_out_gain"] for r in rows.values()) / len(rows),
            }
    return out


def measure() -> dict:
    """The ceiling, over every year the two series share. Loads the real caches."""
    from tools.generate_grid_intensity_feed import (
        AGWS_CACHE,
        DEMAND_CACHE,
        aggregate_demand,
        aggregate_renewable_generation,
        fuel_mix,
    )

    demand = aggregate_demand(json.loads(Path(DEMAND_CACHE).read_text(encoding="utf-8")))
    renewables = aggregate_renewable_generation(
        json.loads(Path(AGWS_CACHE).read_text(encoding="utf-8"))
    )
    (imports, coal_capacity, _coverage, thermal_floors, must_run, _mrc, envelope) = fuel_mix()
    thermal_floor = {y: r["floor_mw"] for y, r in thermal_floors.items()}
    published = neso.actual_by_period(neso.to_settlement_periods(neso.load_cached()))

    shipped = gci.build_shape(
        demand,
        renewables,
        imports_by_period=imports,
        coal_capacity_by_year=coal_capacity,
        thermal_floor_by_year=thermal_floor,
        zero_carbon_must_run_by_period=must_run,
        biomass_envelope_by_year=None,
    )
    coords = coordinates(
        list(shipped),
        demand_by_period=demand,
        renewables_by_period=renewables,
        imports_by_period=imports,
        zero_carbon_must_run_by_period=must_run,
    )

    years = sorted({k[0][:4] for k in published} & {k[0][:4] for k in shipped})
    rows: dict[str, dict] = {}
    for year in years:
        try:
            row = measure_year(
                year,
                shipped=shipped,
                published=published,
                demand=demand,
                coords=coords,
                null_seeds=NULL_SEEDS,
            )
        except (neso.NesoIntensityUnavailable, ValueError):
            continue
        row["controls"] = verdicts(row)
        rows[year] = row
    resolution_sweep = sweep(
        shipped=shipped,
        published=published,
        demand=demand,
        coords=coords,
        grids=SWEEP_GRIDS,
        years=sorted(rows),
    )
    return {
        "resolution_sweep": resolution_sweep,
        "measured_from": "sim/cache (Elexon FUELHH + demand + AGWS, NESO Carbon Intensity)",
        "basis": neso.PUBLISHED_BASIS,
        "split": "fit on ODD days of the month, scored on EVEN days; whole days either side",
        "rungs": {
            "baseline": "build_shape as shipped -- where the atom is",
            "recalibration_ceiling": "best possible function of the model's OWN OUTPUT",
            "input_ceiling": "best possible function of the model's OWN INPUTS -- NOT PUBLISHABLE",
            "null_ceiling": "the input ceiling refitted on a SHUFFLED target -- must collapse",
        },
        "ceiling_reaches_the_published_feed": not ceiling_is_unreachable_from(
            _published_feed_source()
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
            f"recal={row['recalibration_ceiling']['correlation']:.4f} "
            f"INPUT={row['input_ceiling']['correlation']:.4f} "
            f"|null|max={row['null_abs_max']:.4f} "
            f"| bite={'Y' if c['fit_bites_in_sample'] else 'N'} "
            f"pop={'Y' if c['cells_are_populations'] else 'N'} "
            f"null_ok={'Y' if c['null_collapses'] else 'N'} "
            f"fallback={row['control_occupancy_fallback_share']:.3f}"
        )
    print()
    print("RESOLUTION SWEEP -- in-sample gain is the upper bound; held-out says if it is real")
    for label, grid in sorted(
        data["resolution_sweep"].items(), key=lambda kv: kv[1]["cells"]
    ):
        print(
            f"  {label:>6} ({int(grid['cells']):4d} cells)  "
            f"mean in-sample gain={grid['mean_in_sample_gain']:+.4f}  "
            f"mean held-out gain={grid['mean_held_out_gain']:+.4f}"
        )
    print(f"wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
