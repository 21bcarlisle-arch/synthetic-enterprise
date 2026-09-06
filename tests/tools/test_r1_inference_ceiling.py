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
