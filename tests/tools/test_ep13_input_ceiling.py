"""R15 for the EP13 input ceiling.

THE CONTROL THIS FILE EXISTS FOR is the last one, and the rest are scaffolding for it. The tool's
finding is a NEGATIVE — "no function of the model's inputs beats the shipped model by more than
about +0.01" — and a negative finding is exactly where R15's fourth shape bites: an instrument
that can only ever report "no headroom" reports a CONSTANT, and a mutation test on it stays red
because it was always red. So the load-bearing test builds a world where the inputs DO carry
headroom the shipped model misses, and requires the instrument to FIND it. If that test cannot
be made to pass, the finding is worthless whatever the real caches say.

Every fixture here is synthetic and none of them loads a cache: these tests measure the
INSTRUMENT, and an instrument checked against the same data it is used on is a tautology.
"""

from __future__ import annotations

import math

import pytest

from tools import ep13_input_ceiling as ceiling

YEAR = "2020"
MONTHS = 12
DAYS = 28
PERIODS = 48

#: SIX MONTHS, NOT ONE, and the first draft's single month is why this constant carries a note.
#: The default grid is 120 cells; a 28-day fixture leaves ~5 fit half hours per cell, so the null
#: rung scored 0.52 against a signal of 0.999 and read as a leaking fit. It was a fixture too
#: small to populate the grid it was testing — the cell means were noise, and noise over 24
#: u-bins correlates with anything by chance. The instrument was never at fault. A control that
#: cannot see the thing it names is a finding about the FIXTURE (R15), so the fixture grew.


def _keys() -> list[tuple[str, int]]:
    return [
        (f"{YEAR}-{month:02d}-{day:02d}", period)
        for month in range(1, MONTHS + 1)
        for day in range(1, DAYS + 1)
        for period in range(1, PERIODS + 1)
    ]


#: The world the headroom test runs in: the published series depends on BOTH coordinates, the
#: shipped model gets u right and cannot see v at all. Shared with the null test so both run
#: against the same signal.
HEADROOM = dict(
    published_of=lambda u, v: 200.0 + 400.0 * u + 3000.0 * v,
    shipped_of=lambda u, v: 200.0 + 400.0 * u,
)


def _world(published_of, shipped_of):
    """A synthetic year. `published_of(u, v)` and `shipped_of(u, v)` decide the two series.

    The coordinates are built from real-shaped inputs rather than handed in directly, so the
    tests exercise `coordinates()` — the function that has to agree with the dispatch's own
    clamps — rather than bypassing it.
    """
    keys = _keys()
    demand, renewables, imports, must_run = {}, {}, {}, {}
    for date, period in keys:
        key = (date, period)
        # A daily shape plus a slow seasonal drift, so u varies within AND between days.
        phase = 2.0 * math.pi * (period / PERIODS)
        day = int(date[8:10]) + 31 * int(date[5:7])
        demand[key] = 30000.0 + 6000.0 * math.sin(phase)
        renewables[key] = 8000.0 + 5000.0 * math.cos(phase + day / 7.0)
        must_run[key] = 6000.0
        # THE IMPORT RATE MOVES BY DAY AND THE FLOW BY HALF HOUR, so `v` carries structure that
        # is not a function of `u`. A fixture where v tracked u would let the u-marginal alone
        # reproduce the whole surface, and the 2-D fit would never be exercised by the test that
        # exists to exercise it.
        imports[key] = (1500.0 + 500.0 * math.sin(phase / 2.0), 0.15 + 0.35 * ((day * 7) % 11) / 11.0)

    coords = ceiling.coordinates(
        keys,
        demand_by_period=demand,
        renewables_by_period=renewables,
        imports_by_period=imports,
        zero_carbon_must_run_by_period=must_run,
    )
    published = {k: published_of(*coords[k]) for k in keys}
    shipped = {k: shipped_of(*coords[k]) for k in keys}
    return dict(shipped=shipped, published=published, demand=demand, coords=coords)


# --- the load-bearing pair: the instrument must be able to say BOTH things -------------------


def test_the_sweep_FINDS_headroom_when_the_inputs_carry_it():
    """R15's fourth shape, head on: prove the PASS branch is reachable.

    The shipped model here is a deliberately bad function of the same coordinates — it responds
    to u with the wrong curvature — while the published series is a clean function of them. The
    information is THERE and the shipped model is not using it, so a ceiling that reports "no
    headroom" in this world is an instrument that cannot report headroom at all, and the real
    finding would be an artefact of the instrument rather than a fact about the atom.
    """
    world = _world(**HEADROOM)
    row = ceiling.measure_year(YEAR, **world)
    controls = ceiling.verdicts(row)

    # THE BASELINE MUST BE A PLAUSIBLE MODEL, NOT AN ABSURD ONE, and the first draft's was
    # absurd: it responded to u with inverted curvature, so its correlation was about -1 and the
    # gain to beat was ~2.0. A bar of +0.05 against a baseline of -1 is cleared by ANY function
    # with a positive slope, which is why replacing every cell mean with the grand mean left
    # this test green. The shipped model here instead gets u exactly right and ignores v, which
    # is the real shape of the thing being bounded: a competent model missing an input.
    assert row["baseline"]["correlation"] > 0.5, "the baseline must be a competent model"

    assert row["in_sample_gain_upper_bound"] > 0.05, (
        "the inputs carry a gain the shipped model misses and the ceiling did not see it"
    )
    assert row["held_out_gain"] > 0.05, "the gain vanished out of sample, so it was memorised"
    # AND THE CEILING MUST ACTUALLY REACH THE TARGET. This is the assertion the grand-mean
    # mutation cannot survive: a flat surface, or one answered entirely from the u-marginal,
    # cannot reconstruct a series that depends on v.
    assert row["input_ceiling"]["correlation"] > 0.95, "the 2-D surface did not recover the target"
    assert controls["fit_bites_in_sample"], "the fit did not beat the baseline where it was fitted"
    assert controls["cells_are_populations"], "the fixture did not populate the grid it tests"


def test_the_sweep_reports_NO_headroom_when_the_shipped_model_is_already_optimal():
    """The other half of the pair. Same machinery, same world shape, shipped model now EQUAL to
    the published one up to an affine transform — correlation is affine-invariant, so the true
    headroom is exactly zero and the instrument must say so rather than manufacturing a gain."""
    published_of = HEADROOM["published_of"]
    world = _world(
        published_of=published_of,
        shipped_of=lambda u, v: 1.5 * published_of(u, v) + 10.0,
    )
    row = ceiling.measure_year(YEAR, **world)

    assert row["in_sample_gain_upper_bound"] < 0.01, (
        "the shipped model is already optimal, so no ceiling above it may be reported"
    )
    assert row["held_out_gain"] < 0.01


# --- the null ------------------------------------------------------------------------------


def test_the_null_collapses_when_the_target_timing_is_destroyed():
    """Shuffling the target must stop the machinery scoring. A null that stays high means the
    bins manufacture correlation and every other number is that artefact (R15 tautology)."""
    world = _world(**HEADROOM)
    row = ceiling.measure_year(YEAR, **world, null_seeds=ceiling.NULL_SEEDS)
    assert row["null_abs_max"] < abs(row["input_ceiling"]["correlation"]) / 3.0
    assert ceiling.verdicts(row)["null_collapses"]


def test_the_null_threshold_TIGHTENS_as_the_grid_refines():
    """The threshold is DERIVED from the cell count, not chosen — which is what stops it being a
    number tuned until the null passed. Mutating it to a constant makes this fail: a constant
    cannot tighten, and at 512 cells a constant 0.27 would wave through a null six times the
    chance level."""
    coarse = ceiling.verdicts(_row_with(cells=24.0, null_abs_max=0.55))
    fine = ceiling.verdicts(_row_with(cells=512.0, null_abs_max=0.55))
    assert coarse["null_collapses"] is True, "0.55 is ordinary chance at 24 cells"
    assert fine["null_collapses"] is False, "0.55 is far above chance at 512 cells"


def _row_with(*, cells: float, null_abs_max: float) -> dict:
    """The minimum row `verdicts` reads, so the threshold can be tested without a fit."""
    return {
        "baseline": {"correlation": 0.70},
        "input_ceiling": {"correlation": 0.75},
        "baseline_in_sample": {"correlation": 0.70},
        "input_ceiling_in_sample": {"correlation": 0.75},
        "null_abs_max": null_abs_max,
        "cells": cells,
        "control_min_used_cell_count": float(ceiling.MIN_FIT_OCCUPANCY),
        "control_occupancy_fallback_share": 0.0,
    }


# --- the split -----------------------------------------------------------------------------


def test_the_split_keeps_WHOLE_days_on_each_side():
    """The axis under measurement is within-day ordering. A split that cut days in half would let
    the fit see the morning of a day it is scored on the evening of."""
    fit_days = {d for d in range(1, 29) if not ceiling.held_out(f"2020-06-{d:02d}")}
    score_days = {d for d in range(1, 29) if ceiling.held_out(f"2020-06-{d:02d}")}
    assert fit_days and score_days
    assert not (fit_days & score_days), "a day may not be on both sides of the split"
    assert len(fit_days) == len(score_days) == 14


def test_both_sides_of_the_split_carry_every_month():
    """A chronological split would fit on winter and score on summer and report the SEASON as a
    ceiling. Day-of-month parity is what prevents that, so it is asserted rather than assumed."""
    for month in range(1, 13):
        days = [f"2020-{month:02d}-{d:02d}" for d in range(1, 29)]
        assert any(ceiling.held_out(d) for d in days)
        assert any(not ceiling.held_out(d) for d in days)


# --- the coordinates must be the dispatch's own ---------------------------------------------


def test_an_absent_must_run_reading_falls_back_to_the_block_not_to_zero():
    """`emissions_rate_t_per_mwh` treats an absent reading as "not published", not as a fleet
    that stopped. A ceiling fitted on coordinates that read it as zero would bound a different
    model than the one shipped (R15 fail-open)."""
    key = ("2020-06-02", 5)
    common = dict(
        demand_by_period={key: 30000.0},
        renewables_by_period={key: 5000.0},
        imports_by_period={key: (0.0, 0.0)},
    )
    absent = ceiling.coordinates([key], zero_carbon_must_run_by_period={}, **common)
    present = ceiling.coordinates(
        [key],
        zero_carbon_must_run_by_period={key: ceiling.gci.MUST_RUN_ZERO_CARBON_MW},
        **common,
    )
    assert absent[key] == pytest.approx(present[key])
    assert absent[key][0] == pytest.approx((30000.0 - 5000.0 - ceiling.gci.MUST_RUN_ZERO_CARBON_MW) / 30000.0)


def test_an_import_is_clamped_at_demand_because_a_half_hour_is_met_once():
    key = ("2020-06-02", 5)
    coords = ceiling.coordinates(
        [key],
        demand_by_period={key: 10000.0},
        renewables_by_period={key: 0.0},
        imports_by_period={key: (99999.0, 0.4)},
        zero_carbon_must_run_by_period={key: 0.0},
    )
    assert coords[key][1] == pytest.approx(0.4), "the import term used more than the demand"


def test_an_export_is_not_a_negative_import():
    key = ("2020-06-02", 5)
    coords = ceiling.coordinates(
        [key],
        demand_by_period={key: 10000.0},
        renewables_by_period={key: 0.0},
        imports_by_period={key: (-5000.0, 0.4)},
        zero_carbon_must_run_by_period={key: 0.0},
    )
    assert coords[key][1] == pytest.approx(0.0)


# --- binning -------------------------------------------------------------------------------


def test_bins_are_equal_COUNT_not_equal_WIDTH():
    """Both coordinates are heavily skewed. Equal-width bins would put nearly every half hour in
    one cell and measure the binning rather than the inputs."""
    skewed = [float(i) ** 5 for i in range(1000)]
    edges = ceiling._quantile_edges(skewed, 10)
    counts = [0] * (len(edges) + 1)
    for value in skewed:
        counts[ceiling._bin_of(value, edges)] += 1
    assert len(edges) == 9, "the skew collapsed edges it should not have"
    assert max(counts) <= 101, f"equal-count binning left a bin of {max(counts)}"

    width = (skewed[-1] - skewed[0]) / 10.0
    equal_width = [skewed[0] + width * i for i in range(1, 10)]
    wide_counts = [0] * 10
    for value in skewed:
        wide_counts[ceiling._bin_of(value, equal_width)] += 1
    assert max(wide_counts) > 500, "the fixture is not skewed enough to tell the two apart"


def test_a_POINT_MASS_shrinks_the_grid_and_the_artefact_SAYS_SO():
    """`v` is exactly zero for every half hour before the cables existed, so this is the real
    data's shape and not a contrived one. Quantile edges cannot split a tie, and duplicated edges
    would leave empty bins while the artefact still claimed the requested grid — a fit answering
    from a handful of cells, reported as 120. The resolution that gets published is the one the
    population actually supported."""
    mass = [0.0] * 900 + [float(i) for i in range(1, 101)]
    edges = ceiling._quantile_edges(mass, 10)
    assert edges == sorted(set(edges)), "duplicate edges survived and made phantom bins"
    assert all(e > 0.0 for e in edges), "an edge at the point mass creates an empty bin below it"

    keys = [("2020-06-02", p) for p in range(1, 5)]
    coords = {k: (0.1 * i, 0.0) for i, k in enumerate(keys)}
    surface = ceiling.fit_surface(keys, coords, {k: 1.0 for k in keys}, u_bins=2, v_bins=5)
    assert surface["effective_cells"] < 2 * 5, "the collapsed v axis was still counted as five"


def test_a_sparse_cell_falls_back_AND_IS_COUNTED():
    """The fallback is the memorisation guard's escape hatch, so an uncounted one is how a
    memorising fit passes an occupancy control (R15 fail-silent)."""
    surface = {
        "u_edges": [0.5],
        "v_edges": [0.5],
        "cell_mean": {(0, 0): 1.0, (1, 1): 2.0},
        "cell_count": {(0, 0): ceiling.MIN_FIT_OCCUPANCY, (1, 1): 1},
        "marginal_mean": {0: 1.0, 1: 5.0},
        "grand_mean": 3.0,
    }
    coords = {("2020-06-02", 1): (0.1, 0.1), ("2020-06-02", 2): (0.9, 0.9)}
    values, fallbacks = ceiling.apply_surface(list(coords), coords, surface)
    assert fallbacks == 1, "the under-occupied cell answered without being counted"
    assert values[("2020-06-02", 2)] == 5.0, "the fallback was not the u-marginal"


def test_a_shuffle_preserves_the_VALUES_and_destroys_only_the_TIMING():
    target = {("2020-06-02", p): float(p) for p in range(1, 49)}
    out = ceiling.shuffled(target, list(target), seed=3)
    assert sorted(out.values()) == sorted(target.values())
    assert out != target


# --- the wall ------------------------------------------------------------------------------


def test_the_ceiling_cannot_reach_the_published_feed():
    """This treatment is fitted against NESO's outturn, so it is NESO's arithmetic by
    construction and may never reach the published series. Structural, not a promise."""
    assert ceiling.ceiling_is_unreachable_from(ceiling._published_feed_source())


def test_the_reachability_check_is_an_AST_WALK_not_a_substring_search():
    mine = "ep13_input_ceiling"
    assert ceiling.ceiling_is_unreachable_from(f"# {mine} is mentioned in a comment only\n")
    assert not ceiling.ceiling_is_unreachable_from(f"import tools.{mine}\n")
    assert not ceiling.ceiling_is_unreachable_from(f"from tools import {mine}\n")
    assert not ceiling.ceiling_is_unreachable_from(f"from tools.{mine} import measure\n")


def test_the_published_measurement_declares_its_own_controls():
    """A verdict that lives only in another process is one a reader of the artefact has to take
    on trust."""
    row = _row_with(cells=120.0, null_abs_max=0.05)
    assert set(ceiling.verdicts(row)) == {
        "fit_bites_in_sample",
        "cells_are_populations",
        "null_collapses",
        "ceiling_exceeds_baseline_out_of_sample",
    }
