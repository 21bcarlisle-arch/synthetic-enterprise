"""The embedded-generation bound's controls.

The measurement this file guards answers one question -- does a candidate third input carry
WITHIN-DAY timing the model's existing inputs lack -- and it can fail that question in two
opposite ways. It can report a gain for a column of noise, because a third coordinate multiplies
the cell count and a finer partition fits better on its own. Or it can report no gain for a
genuinely informative input, because the grid is too coarse or occupancy fallbacks ate the
signal. Both are tested here, on synthetic worlds where the right answer is known by
construction, because on the real series neither is knowable.
"""

from __future__ import annotations

import datetime
import math
import random

import pytest

from tools import ep13_embedded_generation_bound as bound

#: A FIXTURE YEAR IS NOT A ROUND NUMBER, it is the occupancy the instrument was sized for.
#: `bound` partitions on a 12x4x3 grid and refuses any cell with fewer than MIN_FIT_OCCUPANCY
#: fit-side half hours, which on the real series leaves ~61 per cell. A fixture short enough to
#: drop below that does not measure the instrument weakly -- it measures nothing at all, because
#: almost every scored half hour answers from a fallback rather than from its own cell. Kept as a
#: named constant, and asserted against the instrument's own threshold in
#: `TestTheFixtureIsBigEnoughToBeMeasured`, so shrinking it for speed cannot silently blind the
#: positive control the way it already did once.
FIXTURE_DAYS = 366


def _synthetic_world(
    *, third_carries_signal: bool, days: int = FIXTURE_DAYS, seed: int = 5
) -> dict:
    """A world with a COMPETENT but INCOMPLETE baseline.

    The target is a real function of (u, v) plus a within-day term driven by `w`. So (u, v) alone
    explains most of it -- which is what makes the bar meaningful. A fixture whose baseline was
    hopeless would make any third coordinate look decisive and the control would prove nothing;
    that failure was found on this atom once already, in the biomass bound's first battery, where
    a baseline pinned at correlation -1 made the gain-to-beat unreachably easy.
    """
    rng = random.Random(seed)
    demand, published, shipped, base_coords, third = {}, {}, {}, {}, {}
    # THE INTERCEPT IS NOT COSMETIC. Without it this fixture's target dipped below zero on the
    # low-u half hours, and `neso.compare_shapes` refuses a non-positive intensity outright -- a
    # zero-carbon half hour is an absent reading, not a clean grid. The first run of this file
    # crashed on exactly that. A constant shifts no correlation, so the fix costs the fixture
    # nothing and keeps it inside the domain the scorer actually accepts.
    for day in range(1, days + 1):
        # REAL DATE ARITHMETIC, and the hand-rolled version it replaces is worth recording
        # because it failed SILENTLY. It was `f"2024-{1 + day // 31:02d}-{1 + day % 28:02d}"`,
        # which walks the month on a 31-day stride and the day-of-month on a 28-day one: every
        # 29th, 30th and 31st of a month block lands back on a date the block already emitted,
        # and a dict keyed by (date, period) OVERWRITES rather than complains. 120 requested days
        # produced 112 distinct ones, and asking for more made the collision rate worse instead
        # of better -- so the fixture could not be grown out of the occupancy hole it was in, and
        # nothing in the file said so. The population assertion below is the durable half of this
        # fix; this line is only the cause.
        date = (datetime.date(2024, 1, 1) + datetime.timedelta(days=day - 1)).isoformat()
        day_level = rng.uniform(0.3, 0.7)
        for period in range(1, 49):
            key = (date, period)
            hour = period / 48.0
            u = day_level + 0.15 * math.sin(2 * math.pi * hour)
            v = 0.02 * rng.random()
            # The within-day term the third coordinate is supposed to carry.
            within_day = math.sin(2 * math.pi * hour + 1.1)
            w = within_day + 0.05 * rng.gauss(0, 1) if third_carries_signal else rng.gauss(0, 1)
            demand[key] = 30000.0
            base_coords[key] = (u, v)
            third[key] = w
            published[key] = (
                0.15 + 0.20 * u + 2.0 * v + 0.05 * within_day + 0.002 * rng.gauss(0, 1)
            )
            # The shipped model sees (u, v) only -- it cannot know the within-day term.
            shipped[key] = 0.15 + 0.20 * u + 2.0 * v
    return {
        "demand": demand,
        "published": published,
        "shipped": shipped,
        "base_coords": base_coords,
        "embedded_intensive": third,
    }


def _measure(world, **kw):
    kw.setdefault("null_seeds", (bound.NULL_SEEDS[0],))
    return bound.measure_year("2024", **world, **kw)


# MEASURED ONCE, SHARED. Each row costs several seconds -- five rungs plus the nulls over a
# year of half hours -- and computing the same two worlds inside a dozen tests took 145s on the
# first run. Module scope, and every consumer treats the row as read-only.
@pytest.fixture(scope="module")
def signal_row():
    return _measure(_synthetic_world(third_carries_signal=True))


@pytest.fixture(scope="module")
def noise_row():
    return _measure(_synthetic_world(third_carries_signal=False))


class TestTheFixtureIsBigEnoughToBeMeasured:
    """THE CONTROL ON THE CONTROLS, and it exists because its absence already cost this file.

    Every other test here reads a correlation off a fitted surface, and a surface can only answer
    from a cell that had enough fit-side half hours to be a population rather than a memory. When
    it did not, `bound` does not raise -- it falls back to a coarser cell, exactly as designed for
    the real series' thin corners. On a fixture too small for the grid that fallback stops being
    an edge case and becomes the measurement: the first run of this file had 92% of its scored
    half hours answering from fallbacks, whereupon the POSITIVE control failed, the oracle probe
    showed no headroom, and the honest reading of the output was "the instrument is blind to a
    third coordinate". It was not. The fixture was.

    That is a nastier failure than a wrong number, because both readings of it are available and
    the flattering one -- "the instrument needs work" -- points at the wrong file. So the fixture
    now asserts its own population against the instrument's OWN threshold rather than against a
    number copied here, and a future edit that trims the fixture for speed reds this test first
    and by name, instead of quietly turning the battery into theatre.
    """

    def test_every_requested_day_is_a_distinct_date(self):
        """The collision the old date arithmetic hid: a dict overwrites, so a fixture can ask for
        120 days, receive 112, and report nothing at all about the difference."""
        world = _synthetic_world(third_carries_signal=True, days=FIXTURE_DAYS)
        assert len({k[0] for k in world["published"]}) == FIXTURE_DAYS

    def test_the_fixture_fills_the_grid_to_the_instruments_own_occupancy_floor(self):
        """Derived from `bound`'s constants, never restated -- if the grid or the floor moves,
        this moves with it, which a hardcoded 61 would not."""
        world = _synthetic_world(third_carries_signal=True, days=FIXTURE_DAYS)
        fit_keys = [k for k in world["published"] if not bound.held_out(k[0])]
        cells = bound.U_BINS * bound.V_BINS * bound.W_BINS
        assert len(fit_keys) / cells >= bound.MIN_FIT_OCCUPANCY

    def test_the_measured_rung_answers_from_cells_not_from_fallbacks(self, signal_row):
        """The floor above is necessary and not sufficient -- quantile edges are built on the fit
        half, so occupancy is uneven even when the average is comfortable. THIS is the assertion
        that would have caught the original defect on the row itself: it read 0.92, and now reads
        0.011.

        NOT ASSERTED HERE, deliberately: `min_used_cell_count >= MIN_FIT_OCCUPANCY`. It looks
        like the natural companion and it is a TAUTOLOGY -- `_score` defines that field as the
        min over cells ALREADY FILTERED to `count >= MIN_FIT_OCCUPANCY`, so it cannot come back
        below the threshold; it can only come back 0, when no cell qualified at all. Asserting it
        would have passed just as happily on the 92%-fallback fixture, which is the whole point
        of not asserting it. The fallback SHARE is the independent quantity, because it is
        measured over the scored half hours rather than derived from the same filter.
        """
        assert signal_row["ceiling_3d"]["occupancy_fallback_share"] < 0.10
        assert signal_row["ceiling_3d"]["min_used_cell_count"] > 0  # 0 == nothing qualified
        assert signal_row["controls"]["cells_are_populations"]


class TestTheDayMeanAndWithinDaySplit:
    def test_day_mean_replaces_every_half_hour_with_its_own_days_mean(self):
        series = {("2024-01-01", 1): 0.0, ("2024-01-01", 2): 10.0, ("2024-01-02", 1): 4.0}
        assert bound.day_mean_series(series) == {
            ("2024-01-01", 1): 5.0,
            ("2024-01-01", 2): 5.0,
            ("2024-01-02", 1): 4.0,
        }

    def test_within_day_deviation_sums_to_zero_within_each_day(self):
        series = {("2024-01-01", p): float(p) for p in range(1, 49)}
        deviation = bound.within_day_deviation(series)
        assert abs(sum(deviation.values())) < 1e-9

    def test_the_day_mean_placebo_keeps_between_day_structure(self):
        """The placebo must destroy the WITHIN-day axis and nothing else -- if it flattened the
        between-day variation too, it would be a weaker rung than the real coordinate for two
        reasons at once and the difference could not be attributed to timing."""
        series = {("2024-01-01", 1): 0.0, ("2024-01-01", 2): 10.0, ("2024-01-02", 1): 100.0}
        placebo = bound.day_mean_series(series)
        assert placebo[("2024-01-01", 1)] != placebo[("2024-01-02", 1)]


class TestTheInstrumentCanSeeAnInformativeThirdCoordinate:
    """POSITIVE CONTROL. Without this a null result on the real series is unreadable."""

    def test_a_genuinely_within_day_third_coordinate_shows_a_gain(self, signal_row):
        assert signal_row["embedded_gain_within_day"] > 0.05, signal_row["embedded_gain_within_day"]

    def test_the_oracle_probe_shows_headroom_when_the_target_has_within_day_structure(
        self, signal_row
    ):
        assert signal_row["controls"]["instrument_can_see_within_day"]


class TestTheInstrumentDoesNotRewardANoiseColumn:
    """R15 MUTATION, and the reason the verdict is not 3-D minus 2-D.

    A third coordinate of pure noise still triples the cell count. The naive comparison against
    the 2-D rung is therefore expected to be contaminated; the placebo comparison is not. Both
    are asserted, so the test states WHY the published verdict uses the rung it uses.
    """

    def test_a_noise_third_coordinate_buys_no_within_day_gain(self, noise_row):
        assert noise_row["embedded_gain_within_day"] < 0.02, noise_row["embedded_gain_within_day"]

    def test_a_noise_third_coordinate_buys_no_gain_over_the_shuffled_placebo(self, noise_row):
        assert abs(noise_row["embedded_gain_over_cells"]) < 0.02, noise_row["embedded_gain_over_cells"]

    def test_the_signal_and_noise_worlds_are_separated_by_the_within_day_gain(
        self, signal_row, noise_row
    ):
        """The control that matters: the SAME instrument must rank them correctly."""
        assert (
            signal_row["embedded_gain_within_day"]
            > noise_row["embedded_gain_within_day"] + 0.05
        )


class TestThePlacebosAreCellMatched:
    def test_the_shuffled_placebo_has_the_identical_cell_count_by_construction(self, signal_row):
        assert signal_row["placebo_shuffled"]["cells"] == signal_row["ceiling_3d"]["cells"]

    def test_the_three_dimensional_rungs_have_more_cells_than_the_two_dimensional_one(
        self, signal_row
    ):
        """States the confound the placebo design exists to defeat, rather than assuming it."""
        assert signal_row["ceiling_3d"]["cells"] > signal_row["ceiling_2d"]["cells"]

    def test_the_cell_match_control_fires_when_a_placebo_collapses(self, signal_row):
        """R15 MUTATION: a day-mean placebo whose values collapse onto a point mass loses bins,
        and the comparison silently stops being like-for-like. The control must catch that."""
        row = signal_row
        assert row["controls"]["placebos_are_cell_matched"]
        broken = dict(row)
        broken["placebo_day_mean"] = dict(row["placebo_day_mean"])
        broken["placebo_day_mean"]["cells"] = row["ceiling_3d"]["cells"] / 2.0
        assert not bound.verdicts(broken)["placebos_are_cell_matched"]


class TestTheStandardControls:
    def test_the_fit_bites_in_sample(self, signal_row):
        assert signal_row["controls"]["fit_bites_in_sample"]

    def test_the_null_collapses_against_a_shuffled_target(self):
        """The one test that pays for ALL the seeds: the null is a distribution, and a single
        draw cannot tell an unlucky seed from a leaking fit."""
        row = _measure(
            _synthetic_world(third_carries_signal=True), null_seeds=bound.NULL_SEEDS
        )
        assert row["controls"]["null_collapses"], row["null_abs_max"]

    def test_the_fit_and_score_halves_are_whole_days_and_disjoint(self):
        """The axis under measurement is within-day ordering, so a split cutting days in half
        would let the fit see the morning of a day it is scored on the evening of."""
        world = _synthetic_world(third_carries_signal=True)
        dates = {k[0] for k in world["published"]}
        fit_dates = {d for d in dates if not bound.held_out(d)}
        score_dates = {d for d in dates if bound.held_out(d)}
        assert fit_dates and score_dates
        assert not (fit_dates & score_dates)

    def test_occupancy_fallbacks_are_counted_and_returned_not_swallowed(self):
        world = _synthetic_world(third_carries_signal=True, days=8)
        keys = sorted(world["published"])
        coords = bound.build_coordinates(
            world["base_coords"], world["embedded_intensive"]
        )
        surface = bound.fit_surface_nd(keys, coords, world["published"], (16, 4, 3))
        _scored, fallbacks = bound.apply_surface_nd(keys, coords, surface)
        # Eight days cannot populate the 16x4x3 = 192 cells asked for here, so this MUST fall
        # back -- a fixture where the
        # count stayed at zero would not be exercising the counter at all.
        assert fallbacks > 0


class TestTheOracleRungCannotReachThePublishedFeed:
    def test_a_source_importing_this_module_is_detected(self):
        assert not bound.oracle_is_unreachable_from(
            "from tools.ep13_embedded_generation_bound import measure"
        )
        assert not bound.oracle_is_unreachable_from(
            "import tools.ep13_embedded_generation_bound"
        )

    def test_a_mention_in_a_comment_is_not_an_import(self):
        """A substring search would be satisfied by the name in prose. This walks the AST."""
        assert bound.oracle_is_unreachable_from(
            "# see tools/ep13_embedded_generation_bound for the ceiling\nx = 1\n"
        )

    def test_the_real_published_feed_does_not_import_this_module(self):
        source = (
            bound.PROJECT_DIR / "tools" / "generate_grid_intensity_feed.py"
        ).read_text(encoding="utf-8")
        assert bound.oracle_is_unreachable_from(source)


class TestThePopulationIsSharedAcrossRungs:
    def test_every_rung_is_scored_on_the_same_half_hours(self):
        """The treatment decides the attrition, so the 2-D rung is restricted to the half hours
        the third coordinate exists for -- otherwise the rungs differ in which days they saw and
        the comparison is not one."""
        world = _synthetic_world(third_carries_signal=True)
        thinned = dict(world["embedded_intensive"])
        for key in list(thinned)[:2000]:
            del thinned[key]
        world["embedded_intensive"] = thinned
        row = _measure(world)
        n = row["control_scored_half_hours"] + row["control_fit_half_hours"]
        assert n == pytest.approx(len(thinned), rel=0.02)
