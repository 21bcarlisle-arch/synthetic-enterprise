"""The R1 ceiling instrument's own guards, each named by the defect it exists to catch.

Every test here was written against a wrong headline this instrument actually produced. The
reachability test is the load-bearing one: an instrument that reports "noise" for every feature is
worthless unless it can be shown to say the opposite on a target it should recover, because
otherwise "noise" is what it says regardless of the world and R1's claim is unfalsifiable by it.
"""
from __future__ import annotations

import random
import statistics
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


def test_the_noise_signature_is_checked_on_the_winner_and_not_only_on_the_population():
    """The population control reads GREEN while the published winner shows the signature.

    THE DEFECT, live on the page from 2026-09-04 to 2026-09-06 and green the whole time.
    `held_out_exceeds_in_sample_on_most_pairs` asks whether MOST of the 45 pairs score better out of
    sample than in it. On the real book it is False. But the page does not carry most pairs -- it
    carries the WINNER, and the winner scored +0.6127 held-out against +0.1674 in-sample. The exact
    tell the module docstring names as "a fit scoring three times better on households it never saw,
    which no real fit does" was inside the published figure, and the control named for that tell
    could not see it, because an aggregate is blind to its own selected extreme.

    Both legs are asserted over the same partition: a control that answered True for everything --
    or False for everything -- would pass a single-leg version of this test and catch nothing.
    """
    inverted = {"held_out": 0.6127, "in_sample": 0.1674}
    honest = {"held_out": 0.1674, "in_sample": 0.6127}

    assert r._winner_inverts(inverted) is True, "the signature must be detectable on the winner"
    assert r._winner_inverts(honest) is False, "a fit scoring better in-sample is not the signature"
    assert r._winner_ratio(inverted) == 3.66, r._winner_ratio(inverted)
    # An infinite ratio is not a number a reader can hold, and a large float would read as measured.
    assert r._winner_ratio({"held_out": 0.5, "in_sample": 0.0}) is None


def test_the_winner_signature_is_reported_and_never_flips_the_verdict():
    """It is a REPORT, not a second grading, and the difference is the whole of its correctness.

    Under the null the winner overshoots its own fit too -- both worlds rank on `abs(held_out)`, so
    both find an overshoot. That makes inversion useless as evidence AGAINST the ceiling, and the
    p-value already contains the selection. A future edit that reaches for `clears` from here would
    be keying a control to today's answer, and this is the control that refuses it.
    """
    best = {"held_out": 0.6127, "in_sample": 0.1674, "n": 69}
    verdict = {"clears": True, "p_value": 0.0249, "bound_p95": 0.5529, "margin_over_bound": 0.0598,
               "exceedances": 4}

    head = r._headline(best, verdict, {"clears": False}, 213, 45)

    assert head["verdict"] == "clears", "the inversion must not move the verdict"
    assert head["p_value"] == 0.0249
    # ...and it must REACH THE READER, in the same object as the figure it qualifies.
    assert "never saw" in head["what_it_does_not_say"], head["what_it_does_not_say"]
    assert "3.7 times better" in head["what_it_does_not_say"], head["what_it_does_not_say"]

    # The other side of the partition: no inversion, no sentence -- so the sentence is evidence of
    # the property and not boilerplate the caveat always carries.
    quiet = r._headline({"held_out": 0.1674, "in_sample": 0.6127, "n": 69}, verdict,
                        {"clears": False}, 213, 45)
    assert "never saw" not in quiet["what_it_does_not_say"], quiet["what_it_does_not_say"]



def _reduce(rows):
    """Runs the SHIPPED reducer over hand-built per-run rows, so this grades the code that decides
    the verdict rather than a restatement of it."""
    return r._reduce_runs([
        {"run": f"r{i}.json", "n": n, "ceiling": c, "bound_p95": 0.55, "p_value": p,
         "clears": clears, "full_coverage_clears": False, "trait_spread": 0.5,
         "households_in_book": book}
        for i, (n, book, c, p, clears) in enumerate(rows)])


def test_a_verdict_that_changes_across_draws_is_reported_as_UNSTABLE_not_averaged():
    """R1's ceiling gates R3 and R4 (`A49`), and it reads `cannot tell` at n=71 and `clears` at
    n=69 on consecutive draws of one population. The instrument must say the verdict MOVED.

    THE DEFECT THIS REFUSES is the tempting alternative: report the majority, or the latest, or a
    mean p-value. Any of those publishes one side of a coin flip as a bound. `unanimous` is derived
    from the per-run verdicts every time, so it cannot stay green while the series disagrees.

    All three legs are asserted, and the stable one is not hypothetical: the eight most recent run
    outputs on 2026-09-06 ARE unanimous, and only a window reaching back to 09-04 shows the step.
    A rung answering "unstable" for everything would pass a one-leg version of this and catch
    nothing.
    """
    disagreeing = _reduce([(71, 214, 0.5661, 0.0746, False), (71, 214, 0.5661, 0.0746, False),
                           (69, 213, 0.6127, 0.0249, True), (69, 213, 0.6127, 0.0299, True)])
    assert disagreeing["unanimous"] is False, "the series disagrees and the rung reports agreement"
    assert disagreeing["clears_count"] == 2 and disagreeing["cannot_tell_count"] == 2
    assert disagreeing["verdict_is_a_step_function_of_coverage"] is True, (
        "each coverage regime is internally constant and they differ -- that is a step, and it is "
        "a stronger claim than a ratio of runs because more draws would not settle it")

    agreeing = _reduce([(69, 213, 0.6127, 0.0249, True), (69, 213, 0.6127, 0.0299, True)])
    assert agreeing["unanimous"] is True, (
        "a series that agrees must be able to say so, or 'unstable' is boilerplate")
    assert agreeing["verdict_is_a_step_function_of_coverage"] is False, (
        "one regime cannot be a step; claiming it would manufacture instability that is not there")

    # THE THIRD STATE, and the one that would be read as a step if it were not distinguished: a
    # regime disagreeing WITH ITSELF is scatter around the line, and coverage did not change.
    mixed = _reduce([(69, 213, 0.6127, 0.0249, True), (69, 213, 0.5500, 0.0600, False)])
    assert mixed["unanimous"] is False
    assert mixed["verdict_is_a_step_function_of_coverage"] is False, (
        "a single coverage regime disagreeing with itself is noise; calling it a step would "
        "attribute the move to coverage when coverage did not change")

    # ...AND THE SAME SCATTER ALONGSIDE A SECOND REGIME, which is the case the leg above cannot
    # reach. With one regime the claim is already refused by the regime COUNT, so dropping the
    # within-regime check entirely left that leg green -- found by mutating the clause out and
    # watching every test still pass. Here two regimes differ (so the count clause is satisfied)
    # while one of them is internally inconsistent, and only the within-regime check can refuse it.
    ragged = _reduce([(71, 214, 0.5661, 0.0746, False), (71, 214, 0.5661, 0.0746, False),
                      (69, 213, 0.6127, 0.0249, True), (69, 213, 0.5500, 0.0600, False)])
    assert ragged["unanimous"] is False
    assert ragged["verdict_is_a_step_function_of_coverage"] is False, (
        "one regime holds both verdicts, so the verdict is not determined by coverage and calling "
        "it a step would publish an attribution the evidence does not carry")


def test_the_confound_is_carried_and_the_cause_is_NOT_attributed():
    """The rung's household count and the BOOK's moved together across the measured window -- 71
    in a 214-household book reads one way, 69 in a 213-household book the other. Two things
    changed, so neither can be named as the cause.

    The finding that minted this work said the verdict "flips on two households", which is the
    rung's share of a change the whole book also underwent. The caveat must carry both numbers and
    must refuse the attribution rather than quietly keeping the tidier sentence.
    """
    stability = _reduce([(71, 214, 0.5661, 0.0746, False), (69, 213, 0.6127, 0.0249, True)])
    best = {"held_out": 0.6127, "in_sample": 0.1674, "n": 69}
    verdict = {"clears": True, "p_value": 0.0249, "bound_p95": 0.5529,
               "margin_over_bound": 0.0598, "exceedances": 4}

    said = r._headline(best, verdict, {"clears": False}, 213, 45, stability)["what_it_does_not_say"]

    assert "cannot be attributed" in said, said
    assert "213" in said and "214" in said, (
        "the book sizes either side of the step are what make the confound checkable")
    # The contradiction this sentence carried on its first draft: it claimed the books differed
    # ONLY in pair coverage, two clauses before saying the whole book differed too.
    assert "differ only in which households" not in said, (
        "the caveat asserts and then denies that coverage was the only difference")

    # THE OTHER LEG: with one regime there is no confound to report and no step to claim.
    one = _reduce([(69, 213, 0.6127, 0.0249, True), (69, 213, 0.6127, 0.0299, True)])
    quiet = r._headline(best, verdict, {"clears": False}, 213, 45, one)["what_it_does_not_say"]
    assert "cannot be attributed" not in quiet, (
        "the confound sentence is emitted regardless of the evidence, so it says nothing")
    assert "consistency check" in quiet

    # THE THIRD LEG, and it is the one the real book now takes (2026-09-06). The 214-against-213
    # that made the two inseparable was an artefact of counting a household's gas leg as a second
    # household; keyed on the household the book is a CONSTANT 149 across the same 32 runs while
    # the rung still steps. A refusal to attribute is only honest while something else moved -- if
    # it survives into a window where nothing else did, it is a hedge, which is the shape this
    # instrument has already published once.
    stepped = _reduce([(71, 149, 0.5093, 0.2537, False), (69, 149, 0.6308, 0.0249, True)])
    named = r._headline(best, verdict, {"clears": False}, 149, 45, stepped)["what_it_does_not_say"]
    assert "cannot be attributed" not in named, (
        "nothing but the rung moved, so the refusal to attribute is now a hedge: " + named)
    assert "the same 149 households on every one" in named, named
    assert "IS the cause" in named, named
    # ...and the denominator is the book, not a literal. It read "over two hundred" against a book
    # of 149 for as long as the miscount stood.
    assert "over two hundred" not in named, named
    assert "in a book of 149" in named, named


def _payload_with_a_gas_leg() -> dict:
    """A run output shaped like the real one: the two log families that key on different halves.

    `dynamic_pricing_log` writes the SUPPLY POINT (`C1`, `C1g`); `churn_journey_log` writes the
    household `run_phase2b` calls the billing account (`C1`). That split is the defect, so the
    fixture has to carry both or the control is graded against a book that never had it.
    """
    return {
        "dynamic_pricing_log": [
            {"customer_id": "C1", "commodity": "electricity", "portfolio_premium_pct": 2.0},
            {"customer_id": "C1g", "commodity": "gas", "portfolio_premium_pct": 4.0},
            {"customer_id": "C5", "commodity": "electricity", "portfolio_premium_pct": 3.0},
        ],
        "churn_journey_log": [
            {"customer_id": "C1", "perceived_bill_saving_gbp": 40.0},
            {"customer_id": "C5", "perceived_bill_saving_gbp": 10.0},
        ],
    }


def test_a_gas_leg_and_its_electricity_point_are_ONE_household_not_two():
    """The defect: `households: 213` on a book of 149, because `C1` and `C1g` were counted apart.

    Keying the feature vector on the raw `customer_id` split every dual-fuel household in two and
    then handed each half to the elasticity lookup, which answers for any string -- so 82 of 213
    rows on the real run output were graded against a target belonging to nobody. The join is the
    fix, and this asserts the join, not the count it happened to produce that day.
    """
    got = r.observable_rows(_payload_with_a_gas_leg())

    assert set(got) == {"C1", "C5"}, (
        "the gas leg must fold into its electricity point's household, not stand as its own: "
        f"{sorted(got)}")
    # BOTH SIDES OF THE JOIN REACH ONE ROW. Asserting only the key count would pass on an
    # implementation that dropped the gas leg's rows entirely, which is the other way to get two.
    assert got["C1"]["perceived_bill_saving_gbp"] == 40.0, got["C1"]
    assert got["C1"]["portfolio_premium_pct"] == 3.0, (
        "the household's premium is the mean over its own supply points' priced terms "
        f"(2.0 and 4.0): {got['C1']}")
    # The household that never had a gas leg is untouched -- the other leg of the partition, so a
    # fold that swallowed everything into one row cannot pass this.
    assert got["C5"] == {"portfolio_premium_pct": 3.0, "perceived_bill_saving_gbp": 10.0}


def test_the_target_column_REFUSES_a_supply_point_leg_rather_than_hashing_it_an_elasticity():
    """The fail-open underneath: the lookup has no roster, so nothing below here can notice.

    Both legs of the partition in one control, because a guard that refuses EVERYTHING passes every
    test of a refusal. `C3_2` is the case that made a book-membership test wrong -- a successor
    registration after a home move is a household this run created and the drawn book has never
    heard of -- so it must pass the same guard `C1g` fails.
    """
    from simulation import live_population
    from simulation.population_draw import price_elasticity_for_customer

    live_population.live_population()
    seed = live_population.run_base_seed()
    # REACHABILITY OF THE DEFECT, AND IT MOVED ON 2026-09-06 -- the line above anticipated this in
    # so many words ("if this ever stops being true the refusal below is belt-and-braces"), so the
    # premise is updated here rather than the anticipation being quietly deleted.
    #
    # This probe used to call the lookup for `C1g` and assert it came back an ordinary elasticity,
    # different from `C1`'s -- the fail-open this refusal exists because of. The draw itself now
    # refuses a supply-point leg (`simulation.population_draw.price_elasticity_for_customer`, the
    # CLASS fix one rung up from this instrument's call site), so the fabrication is no longer
    # reachable to assert live. The evidence that it was real is the finding, not this line.
    #
    # THE GUARD BELOW IS THEREFORE THE SECOND OF TWO, AND IT IS STILL LOAD-BEARING RATHER THAN DEAD.
    # It fires FIRST on this path -- `true_traits` partitions the ids before any draw call -- and it
    # raises SystemExit where the draw raises ValueError. So deleting it does not fall through to an
    # equivalent refusal: the exception type changes and this control reds. That is the difference
    # between two guards on one property and a second guard that can never fail, which is a trap
    # this repo has paid for before.
    with pytest.raises(ValueError):
        price_elasticity_for_customer("C1g", seed)
    assert price_elasticity_for_customer("C1", seed) > 0.0

    with pytest.raises(SystemExit) as refused:
        r.true_traits(["C1", "C1g", "C5"])
    assert "C1g" in str(refused.value), str(refused.value)

    traits, got_seed = r.true_traits(["C1", "C3_2", "C5"])
    assert got_seed == seed
    assert set(traits) == {"C1", "C3_2", "C5"}, (
        "a successor registration is its own household and must survive the guard: " + str(traits))


def test_the_fold_is_reported_so_a_book_that_shrank_by_a_third_is_visible():
    """`households: 213` was wrong for two days and no surface could say so.

    Reported and never asserted on: a book with no dual-fuel household in it folds nothing, and that
    is a fact about the book rather than a failure. Both readings are exercised here so the census
    cannot be a constant.
    """
    folded = r.leg_fold_census(_payload_with_a_gas_leg())
    assert folded == {"supply_points_in_the_run_output": 3,
                      "households_they_belong_to": 2,
                      "supply_point_legs_folded_into_a_household": 1}, folded

    elec_only = {"dynamic_pricing_log": [{"customer_id": "C1"}, {"customer_id": "C5"}]}
    assert r.leg_fold_census(elec_only)["supply_point_legs_folded_into_a_household"] == 0


def _learnable_book(features: int, households: int, seed: int, strength: float = 0.01):
    """A book where f0 GENUINELY carries the target. The reachability fixture.

    Same shape as `_noise_book` so the two can be put either side of one property: an estimator that
    always returns zero passes every noise assertion in this file and is worthless, so nothing about
    the three-way split may be asserted without this book beside it.
    """
    rng = random.Random(seed)
    fields = [f"f{i}" for i in range(features)]
    obs = {f"c{h}": {f: rng.uniform(0.0, 100.0) for f in fields} for h in range(households)}
    traits = {c: obs[c]["f0"] * strength + rng.gauss(0.0, 0.05) for c in obs}
    return r._pair_grid(obs, fields), traits


def test_the_published_maximum_overshoots_an_empty_book_and_the_three_way_estimate_does_not():
    """THE DEFECT THE THREE-WAY SPLIT REPAIRS, measured as a BIAS over ten empty books.

    The selection-corrected null already grades WHETHER a ceiling is real and it does that job. It
    cannot grade HOW BIG, because the published figure is `max(abs(held_out))` over 45 candidates
    ranked on the very fold it is then reported from. On a book with nothing in it that maximum
    lands around +0.35 every time -- it is a maximum of forty-five noisy zeroes -- and a reader is
    told it is the recoverable share of a household's price sensitivity.

    THE PROPERTY, and it is keyed to the property rather than to today's answer: over books with no
    signal the two-way maximum must be far from zero and the three-way estimate must AVERAGE to
    zero. Not "be small" -- a biased-down estimator would also be small. It must straddle: the mean
    of the signed estimates sits near zero while the mean maximum does not.

    Delete the third fold and report from the selection fold, and this reds. Take `abs()` of the
    estimate instead of aligning its sign, and this reds -- which is the specific mistake this test
    was written after nearly making.
    """
    maxima, estimates = [], []
    for seed in range(10):
        grid, traits = _noise_book(features=10, households=180, seed=900 + seed)
        assert len(grid) == 45, "the fixture must reproduce the published sweep's width"
        folds = r.global_folds(list({c for cand in grid for c in cand["ids"]}))
        maxima.append(max(abs(r._cellwise_ceiling(c["xs"], c["ys"],
                                                  [traits[i] for i in c["ids"]], 2)[0])
                          for c in grid))
        estimates.append(r.three_way_split(grid, traits, 2, folds)["estimate"])

    mean_max = statistics.fmean(maxima)
    mean_est = statistics.fmean(estimates)
    assert mean_max > 0.25, (
        "the fixture no longer reproduces the defect, so nothing here is testing the fix: the "
        f"best-of-45 maximum averaged {mean_max:+.4f} on books with NOTHING in them")
    assert abs(mean_est) < mean_max / 2, (
        f"the three-way estimate averaged {mean_est:+.4f} over ten empty books against a published "
        f"maximum of {mean_max:+.4f} -- it is carrying the selection bias it exists to remove")
    assert min(estimates) < 0 < max(estimates), (
        "every estimate over ten EMPTY books came out the same side of zero, which is a biased "
        f"estimator however small its mean: {[round(e, 3) for e in estimates]}")


def test_the_three_way_split_recovers_a_target_that_is_really_there():
    """REACHABILITY, and it is the leg the test above is worthless without.

    An estimator hard-wired to return 0.0 satisfies every assertion about empty books. This is the
    control that says the instrument can still find something, so a small estimate on the real book
    is a FINDING about the book and not a property of the estimator.
    """
    grid, traits = _learnable_book(features=10, households=180, seed=404)
    folds = r.global_folds(list({c for cand in grid for c in cand["ids"]}))

    split = r.three_way_split(grid, traits, 2, folds)
    null = r.three_way_null(grid, traits, 2, folds, draws=60)
    verdict = r.magnitude_verdict(split, null, 4)

    assert split["estimate"] > 0.30, (
        "a target that IS a function of an observable must survive the three-way split, or the "
        f"split refuses everything and proves nothing: {split}")
    assert verdict["exceeds_its_own_noise_floor"] is True, (
        f"a real target must clear the estimator's own floor: {verdict}")
    assert verdict["estimate"] is not None, (
        f"a powered rung carrying a real signal must publish a number: {verdict}")


def test_a_rung_too_small_to_estimate_REFUSES_and_a_rung_big_enough_ANSWERS():
    """ONE CONTROL OVER THE WHOLE PARTITION, because a refusal that refuses everything passes every
    test written for it -- and would read on the page exactly like R1's ceiling being unsupported.

    Both legs are asserted here rather than in two tests, so a change that collapses the estimator
    to "always refuse" or "always answer" cannot pass half of this file and be believed.
    """
    small_grid, small_traits = _learnable_book(features=10, households=60, seed=505)
    big_grid, big_traits = _learnable_book(features=10, households=240, seed=505)
    small_folds = r.global_folds(list({c for cand in small_grid for c in cand["ids"]}))
    big_folds = r.global_folds(list({c for cand in big_grid for c in cand["ids"]}))

    refused = r.magnitude_verdict(r.three_way_split(small_grid, small_traits, 2, small_folds),
                                  None, 4)
    answered = r.magnitude_verdict(r.three_way_split(big_grid, big_traits, 2, big_folds), None, 4)

    assert refused["estimate"] is None and refused["refused"], (
        f"a 60-household book cannot support a three-way split at 8 per cell: {refused}")
    assert answered["estimate"] is not None and answered["refused"] is None, (
        f"a 240-household book can, and a guard that refuses it refuses everything: {answered}")
    # THE REFUSAL NAMES ITS OWN NUMBERS. A refusal that says why is how the refusal itself gets
    # found to be wrong, and this one has to survive the constants moving.
    assert str(r.MIN_HOUSEHOLDS_PER_CELL) in refused["refused"], refused["refused"]
    assert refused["under_powered_reading"] is not None, (
        "the direction of travel is evidence and is published beside the refusal, never instead "
        f"of it: {refused}")
    assert refused["fit_fold_holds_populations"] is False


def test_a_household_gets_ONE_fold_for_the_whole_book_and_not_one_per_candidate():
    """The selection ranges over all 45 candidates at once.

    A fold drawn inside each candidate would put a household on the SELECTING side of one pair and
    the ESTIMATING side of another, so its target would reach the estimate through a candidate it
    had already helped choose. That leak is invisible in every aggregate and would show up only as
    an estimate that stayed flatteringly high.
    """
    grid, traits = _noise_book(features=10, households=180, seed=606)
    ids = sorted({c for cand in grid for c in cand["ids"]})
    folds = r.global_folds(ids)

    assert set(folds) == set(ids), "every household in the grid needs a fold"
    assert set(folds.values()) == set(range(r.SPLIT_FOLDS))
    sizes = [sum(1 for f in folds.values() if f == k) for k in range(r.SPLIT_FOLDS)]
    assert max(sizes) - min(sizes) <= 1, f"the folds must be balanced, got {sizes}"
    # THE FOLD MUST NOT BE A HASH OF THE ID. The target is itself a hash of the id, so a fold drawn
    # by hashing the same string can correlate with the quantity being estimated. Asserted as the
    # property -- fold membership carries no information about the trait -- rather than by reading
    # the implementation, which would go stale the moment the implementation changed.
    def gap(assignment):
        means = [statistics.fmean([traits[c] for c in ids if assignment[c] == k])
                 for k in range(r.SPLIT_FOLDS)]
        return max(means) - min(means)

    spread = statistics.pstdev(list(traits.values()))
    assert gap(folds) < spread / 2, (
        f"the folds differ in mean trait by {gap(folds):.4f} against a book-wide spread of "
        f"{spread:.4f} -- the split is not independent of the target")
    # AND THE ASSERTION ABOVE CAN FIRE, which is the whole of its value. On this fixture the trait
    # is drawn independently of the id, so EVERY fold map satisfies it and it would be a tautology
    # published as a control. Here is a fold map drawn from the trait itself: the same assertion
    # must reject it, or it is testing nothing about the map it was written for.
    ranked = sorted(ids, key=lambda c: traits[c])
    drawn_from_the_target = {c: min(r.SPLIT_FOLDS - 1, i * r.SPLIT_FOLDS // len(ranked))
                             for i, c in enumerate(ranked)}
    assert gap(drawn_from_the_target) >= spread / 2, (
        "the independence assertion above accepts a fold map built by SORTING ON THE TARGET, so it "
        "would accept anything and proves nothing about the real one")


def test_every_rotation_fits_selects_and_estimates_exactly_once():
    """The estimate averages over rotations, and the null must run the IDENTICAL set.

    If the two ever diverge the observed statistic is graded against the distribution of a different
    statistic, which is the same class of defect as grading a best-of-45 against one pair's null.
    """
    assert len(r.SPLIT_ROTATIONS) == r.SPLIT_FOLDS, r.SPLIT_ROTATIONS
    for role in range(r.SPLIT_FOLDS):
        assert sorted(rot[role] for rot in r.SPLIT_ROTATIONS) == list(range(r.SPLIT_FOLDS)), (
            f"every fold must play role {role} exactly once: {r.SPLIT_ROTATIONS}")


def test_the_shrunk_figure_declares_that_it_is_not_unbiased():
    """It is the number a reader would compute themselves from two figures already on the page, so
    leaving it uncomputed invites someone to compute it and believe it. It is published WITH the
    assumption that makes it wrong, and that pairing is the control."""
    null = {"median": 0.3815}
    shrunk = r.shrunk_toward_the_null(0.6308, null)

    assert shrunk["value"] == pytest.approx(0.2493, abs=1e-4)
    assert shrunk["is_unbiased"] is False, shrunk
    assert "over-corrects" in shrunk["what_it_assumes"], shrunk
    assert r.shrunk_toward_the_null(0.6308, None)["value"] is None, (
        "with no null to shrink toward the figure is unavailable, not zero")


# ---------------------------------------------------------------------------
# THE WHOLE-BOOK RUNG. A ranked sweep reports its WINNER, so the rung's household count is the
# winner's and not the book's -- and one `decision_only` field in the candidate grid can win and
# drag the whole rung down to the renewing subset however large the book gets. On 2026-09-06 the
# book was 164, four observables had just been lifted to full coverage, and the magnitude still
# refused at 69 with a message that read "the book is too small". The book was never the problem.
# ---------------------------------------------------------------------------


def test_every_observable_declares_a_scope_and_the_declaration_is_a_partition():
    """The fail-closed exclusion in `whole_book_fields` must not be how a gap gets lived with.

    An observable added to `OBSERVABLE_FIELDS` and not to the scope table is silently dropped from
    the whole-book rung -- the rung quietly goes back to being renewal-shaped and nothing on the
    surface says so. This is the control that makes that a red instead of a shrug.
    """
    undeclared = [f for f in r.OBSERVABLE_FIELDS if f not in r.OBSERVABLE_FIELD_SCOPE]
    assert not undeclared, (
        f"{undeclared} reach the sweep with no declared scope, so the whole-book rung drops them "
        "silently and its population is set by an omission rather than a decision")
    # A PARTITION, not a free-text column: a third value would split the book three ways and
    # `whole_book_fields` would keep only one of them without saying which.
    scopes = {v[0] for v in r.OBSERVABLE_FIELD_SCOPE.values()}
    assert scopes == {"account_state", "decision_only"}, scopes
    # BOTH SIDES ARE OCCUPIED. A table that declared everything `account_state` would make the
    # whole-book rung identical to the all-candidate one and every assertion below vacuously true.
    for scope in ("account_state", "decision_only"):
        assert any(v[0] == scope for v in r.OBSERVABLE_FIELD_SCOPE.values()), scope
    # EVERY DECLARATION NAMES ITS REASON. The scope is a judgement about what a supplier holds, and
    # a judgement recorded without its reason cannot be found to be wrong.
    for field, (_, why) in r.OBSERVABLE_FIELD_SCOPE.items():
        assert why and len(why) > 20, f"{field} declares a scope with no reason: {why!r}"
    # AND NOTHING GROUND-TRUTH SNEAKS IN THROUGH THE TABLE.
    assert not (set(r.OBSERVABLE_FIELD_SCOPE) & set(r.GROUND_TRUTH_FIELDS))


def test_the_whole_book_restriction_keys_on_DECLARED_SCOPE_and_never_on_coverage():
    """THE ONE THING THAT KEEPS THIS FROM BEING A SECOND BITE AT THE SEARCH.

    A rung restricted by "keep the pairs with the most households" is outcome-driven: it would pick
    a different field set for every book and the reader could never tell the restriction from the
    result. The restriction here is on a declaration made in the source before the run, so this
    control puts the two criteria in DISAGREEMENT and asserts the declaration wins.
    """
    # `perceived_bill_saving_gbp` is `decision_only`; give it MORE households than anything else.
    # `svt_rate_gbp_per_mwh` is `account_state`; give it the fewest.
    assert r.OBSERVABLE_FIELD_SCOPE["perceived_bill_saving_gbp"][0] == "decision_only"
    assert r.OBSERVABLE_FIELD_SCOPE["svt_rate_gbp_per_mwh"][0] == "account_state"

    kept = r.whole_book_fields(["perceived_bill_saving_gbp", "svt_rate_gbp_per_mwh"])
    assert kept == ["svt_rate_gbp_per_mwh"], (
        f"the restriction followed coverage rather than the declaration: {kept}")
    # FAIL CLOSED on a field nobody declared, and the leg that proves the filter is not "keep
    # everything": an undeclared field is dropped even though nothing says it is decision-only.
    assert r.whole_book_fields(["a_field_nobody_declared"]) == []
    # AND THE FILTER CAN KEEP THINGS, so a filter that dropped everything cannot pass this file.
    account_state = [f for f in r.OBSERVABLE_FIELDS
                     if r.OBSERVABLE_FIELD_SCOPE[f][0] == "account_state"]
    assert r.whole_book_fields(r.OBSERVABLE_FIELDS) == account_state
    assert len(account_state) >= 2, (
        "fewer than two whole-book fields means the whole-book PAIR rung has no pair to score and "
        "the rung is unreachable by construction")


def _two_scope_book(households: int, seed: int):
    """A book whose winner is a `decision_only` pair on a MINORITY of households.

    This is the shape the real book has and the reason the whole-book rung exists: the strong signal
    sits on the field only the renewing accounts carry, so the sweep's winner -- and therefore the
    magnitude's fit fold -- collapses to that subset while the book itself is four times larger.
    """
    rng = random.Random(seed)
    obs, traits = {}, {}
    renewing = households // 4
    for h in range(households):
        cid = f"c{h}"
        obs[cid] = {"unit_rate_gbp_per_mwh": rng.uniform(0.0, 100.0),
                    "rate_vs_svt_pct": rng.uniform(-30.0, 30.0),
                    "company_eac_kwh": rng.uniform(1000.0, 9000.0)}
        # A weak but real signal on what the whole book carries...
        traits[cid] = obs[cid]["unit_rate_gbp_per_mwh"] * 0.004 + rng.gauss(0.0, 0.05)
        if h < renewing:
            # ...and a much stronger one on the field only the renewing quarter has.
            obs[cid]["perceived_bill_saving_gbp"] = traits[cid] * 900.0 + rng.gauss(0.0, 8.0)
            obs[cid]["discount_pct"] = rng.uniform(0.0, 15.0)
    fields = ["unit_rate_gbp_per_mwh", "rate_vs_svt_pct", "company_eac_kwh",
              "perceived_bill_saving_gbp", "discount_pct"]
    return r._pair_grid(obs, fields), traits


def test_a_decision_only_winner_collapses_the_magnitude_and_the_whole_book_rung_ANSWERS():
    """ONE CONTROL OVER THE WHOLE PARTITION, and it is the defect this rung was built for.

    Both legs are asserted together because each alone passes for the wrong reason: a rung that
    ALWAYS refuses passes the first, and a rung that ALWAYS answers passes the second. The pair the
    sweep reports must refuse for want of households while the scope-restricted rung, on the same
    book and the same fold assignment, answers -- and if that ever stops being true the restriction
    has stopped buying anything and should be deleted rather than believed.
    """
    grid, traits = _two_scope_book(households=240, seed=909)
    folds = r.global_folds(sorted({c for cand in grid for c in cand["ids"]}))

    ranked = []
    for cand in grid:
        held, _ = r._cellwise_ceiling(cand["xs"], cand["ys"],
                                      [traits[c] for c in cand["ids"]], 2)
        ranked.append({"x": cand["x"], "y": cand["y"], "n": len(cand["ids"]),
                       "held_out": round(held, 4)})
    ranked.sort(key=lambda row: -abs(row["held_out"]))
    winner = ranked[0]

    # THE PREMISE OF THE WHOLE RUNG, asserted rather than assumed: the sweep's winner really is
    # built on the minority field. Without this the two legs below would be measuring nothing.
    assert "perceived_bill_saving_gbp" in (winner["x"], winner["y"]), (
        f"this fixture no longer reproduces the defect -- the winner is {winner}")
    assert winner["n"] < len(traits) / 2, (
        f"the winner carries {winner['n']} of {len(traits)} households; the collapse is the point")

    all_candidates = r.magnitude_verdict(
        r.three_way_split(grid, traits, 2, folds), None, 4)
    book_grid = [c for c in grid
                 if c["x"] in r.whole_book_fields([c["x"]])
                 and c["y"] in r.whole_book_fields([c["y"]])]
    whole_book = r.magnitude_verdict(r.three_way_split(book_grid, traits, 2, folds), None, 4)

    assert all_candidates["estimate"] is None and all_candidates["refused"], (
        "the all-candidate rung must still refuse -- its fit fold is the winner's subset: "
        f"{all_candidates}")
    assert whole_book["estimate"] is not None and whole_book["refused"] is None, (
        "the scope-restricted rung sits on the whole book and must be able to answer, or the "
        f"restriction buys nothing: {whole_book}")
    assert whole_book["households_per_cell_on_the_fit_fold"] > \
        all_candidates["households_per_cell_on_the_fit_fold"], (
        "the restriction has to BUY power, not merely change the answer")
    # NO `decision_only` FIELD REACHED THE RESTRICTED GRID. Keyed to the scope table rather than to
    # today's field names, so it stays true when the table changes.
    for cand in book_grid:
        for axis in (cand["x"], cand["y"]):
            assert r.OBSERVABLE_FIELD_SCOPE[axis][0] == "account_state", axis
    assert book_grid, "the restricted grid is empty, so every assertion above is vacuous"


def test_field_provenance_names_the_record_and_carries_the_scope_verdict():
    """A coverage number alone cannot say whether it is a defect or a fact.

    69 of 164 is a bookkeeping accident for a field the company holds continuously and the honest
    truth for a field that only exists at a renewal. The record it came from is what lets a reader
    check the declaration against the world instead of taking it on trust.
    """
    payload = {
        "account_state_log": [
            {"customer_id": "C1", "unit_rate_gbp_per_mwh": 140.0},
            {"customer_id": "C1g", "unit_rate_gbp_per_mwh": 60.0},
            {"customer_id": "C2", "unit_rate_gbp_per_mwh": 155.0},
        ],
        "churn_journey_log": [{"customer_id": "C1", "perceived_bill_saving_gbp": 42.0}],
        # A second record carrying the SAME field: the households must union, not double-count.
        "dynamic_pricing_log": [{"customer_id": "C2", "unit_rate_gbp_per_mwh": 150.0}],
        "not_a_row_list": {"total": 3},
    }
    got = r.field_provenance(payload)

    # THE GAS LEG IS NOT A SECOND HOUSEHOLD, here as everywhere else in this instrument.
    assert got["unit_rate_gbp_per_mwh"]["households"] == 2, got["unit_rate_gbp_per_mwh"]
    assert got["unit_rate_gbp_per_mwh"]["records"] == {"account_state_log": 2,
                                                       "dynamic_pricing_log": 1}
    assert got["unit_rate_gbp_per_mwh"]["scope"] == "account_state"
    assert got["perceived_bill_saving_gbp"]["scope"] == "decision_only"
    assert got["perceived_bill_saving_gbp"]["records"] == {"churn_journey_log": 1}
    # A FIELD NO RECORD CARRIED IS REPORTED AT ZERO, not omitted: an absent key reads as "not
    # asked", and the whole point of this block is to make a missing field visible.
    assert got["discount_pct"]["households"] == 0 and got["discount_pct"]["records"] == {}


def test_the_published_sentence_cannot_ASSERT_a_verdict_it_did_not_READ():
    """Three literals in `_magnitude_sentence` asserted facts the function had no access to, and
    all three were live on `/harness/` inside the note the page renders.

    THE CLASS: a published cause authored as prose goes stale beside the measurement that refutes
    it. Each of these was written on a run where it was true and stayed put when the run moved.

      1. "So R1's ceiling clears its null on this book" -- emitted unconditionally, while the
         paragraph it is appended to opens "WE CANNOT TELL". One note contradicting itself.
      2. "inside its own noise floor -- indistinguishable from nothing" about the full-coverage
         rung -- emitted whenever a floor existed at all, while that rung reads +0.2992 against a
         floor of +0.1557 at p=0.005. It is ABOVE its floor, and the sentence understated R1.
      3. "What closes it is COVERAGE, not a re-run" -- the coverage arrived on 2026-09-06 and did
         not close it, because this rung's population is set by whichever pair WINS and the winner
         reaches through a `decision_only` field. The cause was wrong, not merely stale.

    BOTH LEGS OF EACH PARTITION, keyed to the property and not to today's answer. A control that
    pinned the current wording would go green the day the sentence stopped reading the verdict.

    MUTATION (must fire): restore any of the three literals as an unconditional string.
    """
    refused = {"estimate": None, "under_powered_reading": -0.0452, "bound_abs_p95": 0.2701,
               "p_value": 0.7761, "households_per_cell_on_the_fit_fold": 5.0}
    over_floor = {"estimate": 0.2992, "bound_abs_p95": 0.1557, "p_value": 0.005,
                  "exceeds_its_own_noise_floor": True}
    under_floor = {**over_floor, "estimate": 0.0641, "exceeds_its_own_noise_floor": False}
    answered_book = {"estimate": 0.2513, "bound_abs_p95": 0.1628, "p_value": 0.01}

    # 1. THE VERDICT CLAUSE follows `clears`, both ways.
    cleared = r._magnitude_sentence(refused, over_floor, None, 0.576, True, answered_book, 164)
    could_not = r._magnitude_sentence(refused, over_floor, None, 0.576, False, answered_book, 164)
    assert "ceiling clears its null" in cleared
    assert "ceiling clears its null" not in could_not, (
        "the sentence claims the ceiling cleared on a run whose verdict is 'we cannot tell'")
    assert "neither separate" in could_not

    # 2. THE FULL-COVERAGE CLAUSE follows that rung's own floor verdict, both ways.
    assert "indistinguishable from nothing" not in cleared, (
        "+0.2992 is above its floor at p=0.005 and the sentence calls it nothing")
    assert "above its own noise floor" in cleared
    below = r._magnitude_sentence(refused, under_floor, None, 0.576, True, answered_book, 164)
    assert "indistinguishable from nothing" in below, (
        "a rung genuinely inside its floor must still be reported as such -- the repair must not "
        "have deleted the honest reading along with the stale one")

    # 3. THE CLOSING CAUSE follows whether the whole-book rung answered, both ways.
    assert "MORE COVERAGE CANNOT CLOSE THIS RUNG" in could_not
    assert "+0.2513" in could_not and "164" in could_not, (
        "the rung that DOES carry a magnitude is named as the alternative and its figure is absent")
    no_book = r._magnitude_sentence(refused, over_floor, None, 0.576, False, None, None)
    assert "MORE COVERAGE CANNOT CLOSE THIS RUNG" not in no_book, (
        "the correction is emitted even when there is no answering rung to point at, so it asserts "
        "the same cause the old literal did")
    assert "What closes it is COVERAGE" in no_book, (
        "with no rung to point at, coverage IS still the honest cause and must not be dropped")


def _result(book_magnitude: dict, pair_magnitude: dict) -> dict:
    """A finished result shaped like the artefact, with the two rungs' magnitudes dialled by hand.

    Hand-built rather than measured because the property under test is which rung the gate NAMES,
    and the only way to show that is not read off the numbers is to invert the numbers.
    """
    return {
        "households": 164,
        "best_pair": {"n": 69, "x": "perceived_bill_saving_gbp", "y": "mean_recent_margin_rate"},
        "magnitude_three_way_split": pair_magnitude,
        "whole_book_pair_rung": {
            "best_pair": {"n": 164, "x": "rate_vs_svt_pct", "y": "mean_recent_margin_rate"},
            "clears_the_selection_corrected_null": False,
            "selection_corrected_verdict": {"observed": 0.1963, "p_value": 0.4726,
                                            "bound_p95": 0.3103},
            "magnitude_three_way_split": book_magnitude,
        },
    }


ANSWERED = {"estimate": 0.2513, "bound_abs_p95": 0.1628, "p_value": 0.01,
            "exceeds_its_own_noise_floor": True, "refused": None}
REFUSED = {"estimate": None, "bound_abs_p95": 0.2701, "p_value": 0.7761,
           "exceeds_its_own_noise_floor": False,
           "refused": "three-way split needs 8 households per cell on the fit fold"}
AT_THE_FLOOR = {"estimate": 0.0641, "bound_abs_p95": 0.1628, "p_value": 0.31,
                "exceeds_its_own_noise_floor": False, "refused": None}


def test_the_gate_does_not_follow_whichever_rung_has_a_number():
    """THE CONTROL THE WHOLE DECISION RESTS ON: the gate is chosen on scope, not on outcome.

    A49 gates R3 and R4 on ONE of two rungs that answer different questions over different
    populations. On this book only one of them carries an unbiased magnitude, so an implementation
    that reads "the rung with an estimate" is indistinguishable from the honest one HERE and is the
    outcome-driven selection the scope mechanism exists to prevent. The only way to tell them apart
    is to invert the readings and check the gate does not move.

    MUTATION (must fire): make `the_a49_gate` choose the rung whose `estimate` is not None, or fall
    back to the all-candidate rung when the gating one refuses.
    """
    # THE INVERSION. The whole-book rung refuses; the all-candidate rung is the one with a figure.
    inverted = r.the_a49_gate(_result(book_magnitude=REFUSED, pair_magnitude=ANSWERED))

    assert inverted["rung"] == "whole_book_pair_rung", (
        "the gate moved to the rung that happened to carry a number, which is the selection this "
        "decision was recorded to prevent")
    assert inverted["magnitude"] is None, (
        f"the gating rung refused and the gate published {inverted['magnitude']!r} -- it is "
        "reading the losing rung's estimate")
    assert inverted["refused"] == REFUSED["refused"], "the refusal did not reach the gate"
    assert inverted["population"] == 164, "the gate is reporting the losing rung's population"
    assert "CANNOT TELL" in inverted["consequence"], (
        "a refused gate must publish 'we cannot tell', which is a result -- neither retired nor "
        "licensed")
    # THE LOSING RUNG IS CARRIED, NOT DELETED, because a rung reported alone is a rung chosen.
    assert inverted["the_rung_it_is_not"]["magnitude"] == ANSWERED["estimate"]
    assert inverted["the_rung_it_is_not"]["population"] == 69

    # AND THE OTHER WAY UP, so the assertion above is about the CHOICE and not about the fixture:
    # the same gate on the readings the real book gives.
    upright = r.the_a49_gate(_result(book_magnitude=ANSWERED, pair_magnitude=REFUSED))
    assert upright["rung"] == "whole_book_pair_rung"
    assert upright["magnitude"] == ANSWERED["estimate"]
    assert upright["the_rung_it_is_not"]["magnitude"] is None


def test_the_gates_CONSEQUENCE_is_derived_from_the_reading_on_every_branch():
    """Three sentences on this panel asserted verdicts their function had never read (2026-09-07).

    Each was true on the run it was written against and stayed put when the run moved. So the
    gate's own sentence is computed from the reading every time, and all three branches are
    asserted -- an unmeasured gate, a gate with headroom, and a gate at its floor are three
    different claims and none of them may be rendered as another.

    MUTATION (must fire): return the "NOT retired" sentence unconditionally, or collapse the
    refused branch into the at-the-floor one.
    """
    over = r.the_a49_gate(_result(ANSWERED, REFUSED))["consequence"]
    under = r.the_a49_gate(_result(AT_THE_FLOOR, REFUSED))["consequence"]
    absent = r.the_a49_gate(_result(REFUSED, ANSWERED))["consequence"]
    missing = r.the_a49_gate({"households": 164})["consequence"]

    assert "NOT retired" in over and "no headroom" not in over
    assert "no headroom" in under, (
        "a magnitude inside its own noise floor is being published as headroom")
    assert "NOT retired" not in under
    assert "CANNOT TELL" in absent and "NOT retired" not in absent
    # AN ABSENT RUNG AND A REFUSING ONE ARE DIFFERENT CLAIMS. An artefact predating the whole-book
    # rung has not measured this gate at all, which is not the same as measuring and refusing.
    assert "no whole-book rung" in missing and "not a bound of zero" in missing
    assert missing != absent

    # AND THE GATE NEVER LICENSES THE BUILD. R1 bounds INFERENCE; what a carbon score or an advice
    # product is worth is A49's remaining work and needs a ceiling per side.
    assert "does not license" in over, (
        "the open branch reads as permission to build R3 and R4, which R1's ceiling cannot give")


def test_the_gate_on_the_REAL_artefact_reads_the_rung_it_names():
    """Keyed to the property and never to today's answer.

    It asserts the gate's figures ARE the gating rung's figures, whichever way they fall, so it
    goes red if the lift ever drifts onto the other rung and stays green when the book grows.
    Pinning +0.2513 would do the opposite of both.

    MUTATION (must fire): read `result["magnitude_three_way_split"]` -- the all-candidate rung --
    into the gate's `magnitude`.
    """
    import json

    artefact = r.OUT_PATH
    assert artefact.is_file(), (
        f"{artefact} is tracked and missing, so what the gate publishes cannot be checked against "
        "what the instrument measured")
    held = json.loads(artefact.read_text(encoding="utf-8"))
    rung = held.get(r.A49_GATING_RUNG)
    if not rung:
        pytest.skip("this artefact predates the whole-book rung; there is no gating rung to read")

    gate = r.the_a49_gate(held)
    mag = rung.get("magnitude_three_way_split") or {}

    assert gate["rung"] == r.A49_GATING_RUNG
    assert gate["magnitude"] == mag.get("estimate")
    assert gate["refused"] == mag.get("refused")
    assert gate["noise_floor"] == mag.get("bound_abs_p95")
    assert gate["population"] == (rung.get("best_pair") or {}).get("n")
    # THE GATING RUNG'S OWN SELECTED-MAXIMUM VERDICT TRAVELS WITH ITS MAGNITUDE. On this book they
    # disagree, and a magnitude published without it reads as a bound this rung has not earned.
    assert gate["and_its_own_ceiling_verdict"]["clears"] == rung.get(
        "clears_the_selection_corrected_null")
    # AND IT IS NOT THE OTHER RUNG WEARING THE GATE'S NAME.
    assert gate["the_rung_it_is_not"]["population"] == (held.get("best_pair") or {}).get("n")


def test_the_gating_rung_is_declared_where_a_reading_cannot_reach_it():
    """The decision has to be un-moveable by an outcome, which means it lives above every run.

    `A49_GATING_RUNG` is a module constant beside `OBSERVABLE_FIELD_SCOPE`, and the rung it names
    must be one built from `account_state` fields only -- otherwise the gate's population is set by
    whichever pair wins and the whole argument for the choice collapses.

    MUTATION (must fire): point `A49_GATING_RUNG` at the all-candidate rung; or widen
    `whole_book_fields` to admit a `decision_only` field.
    """
    assert r.A49_GATING_RUNG == "whole_book_pair_rung"
    book = r.whole_book_fields(r.OBSERVABLE_FIELDS)
    assert book, "the gating rung has no fields, so it cannot be over the whole book"
    assert all(r.OBSERVABLE_FIELD_SCOPE[f][0] == "account_state" for f in book), (
        "a `decision_only` field reached the gating rung, so its population is again set by "
        "whichever pair wins")
    # THE FIELD THAT ACTUALLY DID THE COLLAPSING, named so this stays a control over the real case.
    assert "perceived_bill_saving_gbp" not in book
