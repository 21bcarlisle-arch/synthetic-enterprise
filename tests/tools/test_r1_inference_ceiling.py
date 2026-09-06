"""The R1 ceiling instrument's own guards, each named by the defect it exists to catch.

Every test here was written against a wrong headline this instrument actually produced. The
reachability test is the load-bearing one: an instrument that reports "noise" for every feature is
worthless unless it can be shown to say the opposite on a target it should recover, because
otherwise "noise" is what it says regardless of the world and R1's claim is unfalsifiable by it.
"""
from __future__ import annotations

import random
from pathlib import Path

import pytest

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


# ---------------------------------------------------------------------------------------------
# THE SELECTION CORRECTION. Everything below was written against a WRONG PUBLISHED HEADLINE: the
# sweep ranked 45 pairs by `abs(held_out)`, reported the winner as the input ceiling, and graded it
# against a null drawn for that pair alone. Held-out +0.5661 against in-sample +0.1724 reached
# `site/data/delivery.json` under Poesys's name.
# ---------------------------------------------------------------------------------------------


def _noise_book(features: int, households: int, seed: int):
    """A book where NOTHING is learnable: every feature and the target are independent noise.

    Built through `_pair_grid` rather than by hand so the test exercises the same grid the sweep
    scores. Under this book every held-out figure is chance, so a correct instrument must refuse
    the winner however high it reaches.
    """
    rng = random.Random(seed)
    fields = [f"f{i}" for i in range(features)]
    obs = {f"c{h}": {f: rng.uniform(0.0, 100.0) for f in fields} for h in range(households)}
    traits = {c: rng.gauss(0.0, 1.0) for c in obs}
    return r._pair_grid(obs, fields), traits


def _shuffled(values, seed):
    out = list(values)
    random.Random(seed).shuffle(out)
    return out


def test_the_one_pair_null_accepts_a_book_with_nothing_in_it_and_the_corrected_null_does_not():
    """THE DEFECT AND ITS FIX, measured as a FALSE-POSITIVE RATE over ten books with no signal.

    This is the shape that published +0.5661 as R1's ceiling. On a book where every feature and the
    target are independent noise, the winner of a 45-way search clears the null drawn for its OWN
    pair almost every time -- that null answers "could THIS pair have arisen by chance" and the
    winner was chosen for being the most extreme of forty-five.

    WHY A RATE OVER TEN BOOKS RATHER THAN ONE ASSERTION ON ONE SEED. The statistic is uniform under
    the null by construction, so any single book can come out either way and a seed that shows the
    contrast is a seed that was fished for. The rate cannot be fished: the uncorrected null must
    accept the great majority of empty books, and the corrected null must accept them at about its
    own alpha. Delete the correction and this reds; weaken it and this reds.
    """
    accepted_uncorrected, accepted_corrected = 0, 0
    books = 10
    for seed in range(books):
        grid, traits = _noise_book(features=10, households=71, seed=700 + seed)
        assert len(grid) == 45, "the fixture must reproduce the published sweep's width"
        best_held, best_own_null = 0.0, 0.0
        for cand in grid:
            ts = [traits[c] for c in cand["ids"]]
            held = abs(r._cellwise_ceiling(cand["xs"], cand["ys"], ts, 2)[0])
            if held > best_held:
                best_held = held
                best_own_null = max(
                    abs(r._cellwise_ceiling(cand["xs"], cand["ys"], _shuffled(ts, d), 2)[0])
                    for d in range(r.NULL_DRAWS))
        accepted_uncorrected += best_held > best_own_null
        verdict = r.graded_against_selection(
            best_held, r.selection_corrected_null(grid, traits, 2, draws=100))
        accepted_corrected += bool(verdict["clears"])

    assert accepted_uncorrected >= 7, (
        "the fixture no longer reproduces the defect, so nothing here is testing the fix: the "
        f"one-pair null accepted only {accepted_uncorrected}/{books} books with no signal")
    assert accepted_corrected <= 3, (
        f"the corrected null accepted {accepted_corrected}/{books} books with NOTHING in them, "
        f"which is not a 5% false-positive rate however the arithmetic reads")
    assert accepted_corrected < accepted_uncorrected, (
        "the two nulls agreed on every empty book, so the correction is not doing anything: "
        f"{accepted_uncorrected} vs {accepted_corrected}")


def test_a_learnable_target_still_clears_so_cannot_tell_is_a_finding_not_a_default():
    """REACHABILITY, and it is the load-bearing leg.

    A correction that refuses everything is not a correction, it is a mute button -- and it would
    read on the page exactly like R1's claim being confirmed. One feature genuinely carries the
    target here, so the selected winner must clear the selected-maximum null.
    """
    rng = random.Random(202)
    fields = [f"f{i}" for i in range(10)]
    obs = {f"c{h}": {f: rng.uniform(0.0, 100.0) for f in fields} for h in range(214)}
    traits = {c: obs[c]["f0"] * 0.01 + rng.gauss(0.0, 0.05) for c in obs}
    grid = r._pair_grid(obs, fields)
    observed = max(abs(r._cellwise_ceiling(c["xs"], c["ys"], [traits[i] for i in c["ids"]], 2)[0])
                   for c in grid)

    verdict = r.graded_against_selection(observed, r.selection_corrected_null(grid, traits, 2, 200))

    assert verdict["clears"] is True, (
        f"a target that IS a function of an observable must survive the correction: {verdict}")


def test_the_null_rises_with_the_number_of_candidates_searched():
    """The property the whole correction rests on, asserted directly rather than inferred.

    The reported statistic is a MAXIMUM over candidates, so its null must grow as the search
    widens. A `_sweep_winner` that returned the first candidate's score, or one candidate's own
    null, would leave this flat -- and that is precisely the defect being repaired.
    """
    grid, traits = _noise_book(features=10, households=71, seed=303)

    one = r.selection_corrected_null(grid[:1], traits, 2, draws=120)
    many = r.selection_corrected_null(grid, traits, 2, draws=120)

    assert many["p95"] > one["p95"], (
        "searching 45 candidates must raise the noise floor above searching one: "
        f"{many['p95']:.4f} vs {one['p95']:.4f}")
    assert many["candidates_per_draw"] == len(grid) and one["candidates_per_draw"] == 1


def test_every_candidate_in_a_draw_sees_the_same_shuffled_world():
    """Shuffling each candidate's target independently is a DIFFERENT null and a weaker one.

    It breaks the correlation between candidates that share households, which is what makes the
    real sweep's maximum reach as high as it does. Detected structurally: two candidates built on
    the same households must receive the same permuted trait for the same household, so a draw in
    which every candidate scores identically to a world-wide shuffle is the only shape that passes.
    """
    grid, traits = _noise_book(features=4, households=60, seed=404)
    ids = sorted({c for cand in grid for c in cand["ids"]})
    values = [traits[c] for c in ids]
    permuted = list(values)
    random.Random(90_000).shuffle(permuted)          # the first draw's own world
    world = dict(zip(ids, permuted))

    from_the_module = r.selection_corrected_null(grid, traits, 2, draws=1)
    by_hand = r._sweep_winner(grid, world, 2)

    assert abs(from_the_module["max"] - round(by_hand, 4)) < 5e-5, (
        "the module's first draw is not the world-wide shuffle it documents: "
        f"{from_the_module['max']} vs {by_hand:.4f}")


def test_a_permutation_p_value_can_never_be_published_as_zero():
    """`exceedances / draws` returns 0.0 when nothing beats the observed, which claims a certainty
    200 draws cannot buy -- and 0.0 is what would reach the page."""
    grid, traits = _noise_book(features=4, households=60, seed=505)
    null = r.selection_corrected_null(grid, traits, 2, draws=50)

    verdict = r.graded_against_selection(99.0, null)     # unbeatable by construction

    assert verdict["exceedances"] == 0
    assert verdict["p_value"] == round(1 / 51, 4) > 0.0


def test_a_book_too_small_to_measure_is_refused_rather_than_scored_as_a_ceiling_of_zero():
    """FAIL CLOSED on the empty book. In a linked worktree the gitignored run outputs are absent,
    `newest_run_output` picked a tracked stand-in with no usable rows, and the instrument returned
    `households: 0, ceiling +0.0000, clears False` -- which reads as "measured the book, found
    nothing" and is the opposite claim to "measured nothing"."""
    import json as _json
    import tempfile

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        _json.dump({"rows": [{"customer_id": f"c{i}", "company_eac_kwh": float(i)}
                             for i in range(5)]}, fh)
        path = Path(fh.name)

    with pytest.raises(SystemExit) as caught:
        r.measure(run_path=path)

    assert "REFUSED" in str(caught.value) and "households" in str(caught.value)
