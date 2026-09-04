"""The R1 ceiling instrument's own guards, each named by the defect it exists to catch.

Every test here was written against a wrong headline this instrument actually produced. The
reachability test is the load-bearing one: an instrument that reports "noise" for every feature is
worthless unless it can be shown to say the opposite on a target it should recover, because
otherwise "noise" is what it says regardless of the world and R1's claim is unfalsifiable by it.
"""
from __future__ import annotations

import random

from tools import r1_inference_ceiling as r


def test_a_learnable_target_is_recovered_so_noise_is_a_finding_not_a_default():
    """REACHABILITY. The instrument must be able to return CLEARS, or it measures nothing.

    The defect: every full-coverage feature reports "noise" against the real book, which is exactly
    what R1 predicts -- and exactly what a broken instrument, a wrong seed or a scrambled join would
    also report. A branch that exists to be taken rarely has to be shown to be takeable before its
    not being taken means anything.
    """
    rng = random.Random(11)
    xs = [rng.uniform(0.0, 100.0) for _ in range(214)]
    # A target that IS a function of the feature, plus noise it cannot explain away.
    ts = [x * 0.01 + rng.gauss(0.0, 0.05) for x in xs]

    got = r.score_one_feature(xs, ts, cells=2)

    assert got["refused"] is None, got
    assert got["clears"] is True, f"a learnable target must clear its null: {got}"
    assert got["held_out"] > got["null"], got


def test_an_unlearnable_target_does_not_clear_so_clearing_is_not_automatic():
    """The other side of the same control: the verdict must depend on the target, not the shape.

    Without this, `clears` could be True for anything and the reachability test above would pass on
    an instrument that always says yes.
    """
    rng = random.Random(12)
    xs = [rng.uniform(0.0, 100.0) for _ in range(214)]
    ts = [rng.gauss(0.0, 1.0) for _ in xs]          # independent of xs by construction

    got = r.score_one_feature(xs, ts, cells=2)

    assert got["refused"] is None, got
    assert got["clears"] is False, f"a target unrelated to the feature must not clear: {got}"


def test_a_skewed_feature_is_refused_rather_than_scored_as_a_silent_zero():
    """The guard that had to be re-keyed after the first version fired NEVER.

    Three observables scored exactly 0.0000 on the real book. The first guard written for it --
    refuse a feature whose spread is zero -- never fired, because none of them is constant. They are
    SKEWED: one outlier sets the upper bin edge, every other household falls in the lower bin, the
    predictor emits a single value, `_corr` divides by a zero deviation and returns 0.0. That reads
    identically to "measured, and found nothing", which is a different claim about the world.
    """
    xs = [1.0] * 213 + [999.0]                      # real spread, one occupied cell
    ts = [float(i) for i in range(214)]

    got = r.score_one_feature(xs, ts, cells=2)

    assert got["refused"], f"a fit emitting one prediction is not a measurement: {got}"
    assert got["clears"] is False
    assert got["held_out"] is None, "a refused fit must not publish a figure"


def test_the_null_destroys_the_pairing_rather_than_rotating_it():
    """A rotation preserves the ordering the features may themselves be ordered by.

    The first null was `ts[n//2:] + ts[:n//2]`. On a target that rises with the feature, a rotation
    leaves most of the monotone structure intact, so the "null" scores high for a reason that has
    nothing to do with chance. The shuffle must do materially better at destroying it.
    """
    rng = random.Random(13)
    xs = sorted(rng.uniform(0.0, 100.0) for _ in range(214))
    ts = [x * 0.01 for x in xs]                     # perfectly ordered with the feature

    rotated = ts[len(ts) // 2:] + ts[: len(ts) // 2]
    rot_score = abs(r._cellwise_ceiling(xs, [0.0] * len(xs), rotated, 2)[0])

    shuffled = list(ts)
    random.Random(0).shuffle(shuffled)
    shuf_score = abs(r._cellwise_ceiling(xs, [0.0] * len(xs), shuffled, 2)[0])

    assert rot_score > shuf_score, (
        "the rotation retained more structure than the shuffle, which is why it was the wrong null: "
        f"rotation={rot_score:.4f} shuffle={shuf_score:.4f}"
    )


def test_the_null_floor_is_the_worst_draw_and_not_one_sample():
    """One draw is a sample; the floor is how high chance REACHES.

    Keyed to the property rather than to today's figure: the maximum over draws can never be below
    any individual draw, and with this many draws it must strictly exceed a typical one.
    """
    rng = random.Random(14)
    xs = [rng.uniform(0.0, 100.0) for _ in range(214)]
    ts = [rng.gauss(0.0, 1.0) for _ in xs]

    draws = []
    for d in range(r.NULL_DRAWS * 2):
        shuffled = list(ts)
        random.Random(d).shuffle(shuffled)
        draws.append(abs(r._cellwise_ceiling(xs, [0.0] * len(xs), shuffled, 2)[0]))

    assert r.score_one_feature(xs, ts, cells=2)["null"] == round(max(draws), 4)
    assert max(draws) > sorted(draws)[len(draws) // 2], "the floor must exceed the median draw"


def test_no_ground_truth_field_can_reach_the_feature_set():
    """The ceiling bounds what a SUPPLIER could build. A simulation internal in the feature set
    would make it bound nothing, while still producing a confident number."""
    assert not (set(r.OBSERVABLE_FIELDS) & set(r.GROUND_TRUTH_FIELDS))
