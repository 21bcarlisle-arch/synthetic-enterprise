"""The flagship figure publishes a null result; these ask whether it could have published any
other one.

THE DEFECT EACH TEST NAMES is written on the test. The class is the one the Spearman carried since
2026-09-01 and that arrived at `method_skill` on 2026-08-31: a statistic reported as "we cannot
tell" by an instrument that had no power to return anything else, on a page where that is
indistinguishable from a method with no skill.

The load-bearing claim in `tools.inference_claim.detectability` is an EXTRAPOLATION -- the
half-width of the permutation null falls as k/sqrt(n), with k measured at the run's own sample --
and the whole floor rests on it. `test_the_permuted_half_width_really_does_fall_as_one_over_root_n`
is the control that can refuse it: it permutes at four sizes, under the run's own seed and the
run's own `_concordance`, on a signal carrying the tie structure the live data actually has, and
demands the measured constants agree. Nothing else in this file would notice if the law were wrong.
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

import pytest

from tools import inference_claim as ic
from tools.run_value_cycle_ab import NULL_SEED, concordance_null_spread

PROJECT = Path(__file__).resolve().parents[2]
FEED = PROJECT / "site" / "data" / "value_arms.json"

#: The live reading this block was built for, so a fixture drifting away from the artefact is
#: visible here rather than only on the page.
LIVE_N = 86


def _block(**over):
    """The detectability block at the live reading, with the ceiling injected.

    THE CEILING IS PASSED, NEVER READ, in every test but the one that reads it. A memory-budget
    probe is machine state: letting it into these assertions would make the arithmetic tests go
    red on a different box, which is the "keyed to today's answer" shape wearing a fixture's
    clothes.
    """
    kwargs = {"observed": 0.5170998632010944, "null_low": 0.4292749658002736,
              "null_high": 0.5723666210670315, "n": LIVE_N, "accounts": 46,
              "ceiling": {"available": True, "accounts": 632, "source": "injected"}}
    kwargs.update(over)
    return ic.detectability(**kwargs)


def _tied_signal_points(n, groups=10, seed=7):
    """A sample whose SIGNAL ties like the live one does and whose outcome is continuous.

    The live run reports 290 tied signal pairs in 86 decisions and zero pairs tied on the
    outcome. Ten repeated margins over n decisions reproduces that shape (328 tied pairs at
    n=86) and scales it, which is what the law has to hold across. Testing the law on DISTINCT
    signals would test Kendall's untied closed form -- a formula this module does not use --
    rather than the permutation the run actually runs.
    """
    rng = random.Random(seed)
    return [(float(i % groups), rng.gauss(0.0, 1.0)) for i in range(n)]


# ---------------------------------------------------------------------------------------------
# The extrapolation itself. Everything below rests on this one.
# ---------------------------------------------------------------------------------------------

def test_the_permuted_half_width_really_does_fall_as_one_over_root_n():
    """DEFECT: the curve extrapolates a law nobody measured on data shaped like ours.

    `detectability` quotes decision counts hundreds of times the sample it was measured on, all
    of them from `half_width * sqrt(n)` being constant. If that constant drifts with n on tied
    data, every floor and the whole attainability verdict are wrong by whatever it drifts by, and
    the page states an unattainability that is an artefact of the formula.

    Permutes at four sizes under the RUN'S OWN seed and the run's own `concordance_null_spread`,
    so this measures the estimator the artefact was produced by and not a re-derivation of it.
    Fires on: replacing sqrt(n) with n, with log(n), or with a constant.
    """
    constants = {}
    for n in (86, 172, 344):
        spread = concordance_null_spread(_tied_signal_points(n), 0.5, draws=1500, seed=NULL_SEED)
        assert spread["available"], n
        low, high = spread["null_95_interval"]
        constants[n] = ((high - low) / 2.0) * math.sqrt(n)
    spread = list(constants.values())
    # 8% is Monte-Carlo room at 1,500 draws plus the small-n inflation at 86, and it is FAR
    # tighter than any wrong law survives: n instead of sqrt(n) puts the constants a factor of
    # two apart across this ladder, and a flat law a factor of two the other way.
    assert max(spread) / min(spread) < 1.08, constants
    # And the direction that matters for the published bound: the constant taken at the smallest
    # sample is the LARGEST, so quoting k at the run's own n overstates the decisions needed.
    assert constants[86] >= constants[344]


def test_the_scale_constant_is_the_runs_own_interval_and_not_a_second_permutation():
    """DEFECT: the block re-measures the null and drifts away from the figure it qualifies.

    `_method_skill` already rejected recomputing the spread for this reason. The curve must pass
    through the run's own reading exactly: at the run's own n, the detectable excess IS half the
    published interval, to the last bit.

    Fires on: computing `detectable_excess` from a fresh permutation, from the closed form, or
    from `null_sd` rather than from the interval.
    """
    block = _block()
    published_half_width = (0.5723666210670315 - 0.4292749658002736) / 2.0
    assert block["detectable_excess"] == published_half_width
    this_run = [row for row in block["curve"] if row["is_this_run"]]
    assert len(this_run) == 1
    assert this_run[0]["decisions_scored"] == LIVE_N
    assert this_run[0]["detectable_excess"] == pytest.approx(published_half_width, rel=1e-12)


# ---------------------------------------------------------------------------------------------
# The verdict, and the ways it could be reached without being earned.
# ---------------------------------------------------------------------------------------------

def test_an_effect_the_ceiling_book_could_resolve_is_reported_as_attainable():
    """DEFECT: the unattainability verdict is unreachable -- it says 'no' whatever it is given.

    THE REACHABILITY CONTROL, and it is the one this project keeps not writing. Every other
    assertion here checks that a too-small effect is refused; a verdict that refused EVERY effect
    would pass all of them. This drives one partition across both answers through the same
    arithmetic: a departure the 632-account ceiling can resolve must come back attainable, and a
    departure it cannot must not.

    Fires on: hard-coding `the_observed_effect_is_attainable` to False, or comparing against the
    ceiling with the inequality reversed.
    """
    # 0.517 needs ~806 accounts against a 632 ceiling; 0.540 needs far fewer.
    tight = _block()["the_book_this_would_need"]
    roomy = _block(observed=0.54)["the_book_this_would_need"]
    assert tight["the_observed_effect_is_attainable"] is False
    assert roomy["the_observed_effect_is_attainable"] is True
    assert roomy["accounts_needed_for_the_observed_effect"] < 632
    assert tight["accounts_needed_for_the_observed_effect"] > 632
    # And BOTH branches of the partition are present in the published floor ladder, so the page
    # carries a scale rather than a single verdict.
    within = {row["within_the_settled_book_ceiling"] for row in _block()["floor"]}
    assert True in within and False in within


def test_an_unreadable_ceiling_is_cannot_tell_and_never_room_to_grow():
    """DEFECT: FAIL-OPEN. A missing ceiling reads as a book with no limit.

    `within_the_settled_book_ceiling` is tri-state and None is the answer whenever either side is
    absent. A `False`-means-attainable or a truthiness test here would publish "a book this world
    can supply does reach it" off a probe that failed to run.

    Fires on: defaulting `ceiling_accounts` to infinity, or returning False for the unknown case.
    """
    blind = _block(ceiling={"available": False, "reason": "probe unavailable"})
    book = blind["the_book_this_would_need"]
    assert book["the_observed_effect_is_attainable"] is None
    assert all(row["within_the_settled_book_ceiling"] is None for row in blind["floor"])
    assert "cannot tell" in blind["sentence"]
    # The decisions floor does NOT depend on the ceiling and must survive its absence: what the
    # instrument needs is a property of the instrument.
    assert book["decisions_needed_for_the_observed_effect"] == (
        _block()["the_book_this_would_need"]["decisions_needed_for_the_observed_effect"])


def test_a_run_with_no_interval_refuses_rather_than_reporting_an_infinite_reach():
    """DEFECT: an absent null yields a zero half-width and therefore infinite detecting power.

    Fires on: defaulting either bound to 0.5, or dividing by a zero-width interval.
    """
    for over in ({"null_low": None}, {"null_high": None}, {"observed": None}, {"n": 2},
                 {"null_low": 0.5, "null_high": 0.5}):
        block = _block(**over)
        assert block["available"] is False, over
        assert block["reason"]
        assert "detectable_excess" not in block


def test_the_sentence_cannot_claim_unattainable_while_the_arithmetic_says_otherwise():
    """DEFECT: prose beside a flag rather than derived from it -- this file's founding defect.

    Fires on: writing the verdict clause as a literal instead of branching on `attainable`.
    """
    assert "No attainable book" in _block()["sentence"]
    assert "No attainable book" not in _block(observed=0.54)["sentence"]
    assert "does reach it" in _block(observed=0.54)["sentence"]


def test_the_floor_ladder_is_not_keyed_to_the_observed_reading():
    """DEFECT: a scale that moves every run, so a reader cannot hold it.

    The fixed excesses must be present whatever the run read; the observed one is one more row,
    LABELLED, so the page can show where this run sits without the ladder being about it.

    Fires on: deriving the ladder from the observed value, or dropping the label.
    """
    for observed in (0.517, 0.54, 0.31):
        rows = _block(observed=observed)["floor"]
        published = {round(row["excess_over_no_information"], 4) for row in rows}
        assert set(ic.FLOOR_EXCESSES) <= published, observed
        labelled = [row for row in rows if row["is_the_observed_effect"]]
        assert len(labelled) == 1
        assert labelled[0]["excess_over_no_information"] == pytest.approx(abs(observed - 0.5))
    # BELOW 0.5 is the director's own case and must size a book the same way: the instrument's
    # reach is symmetric about no-information.
    assert (_block(observed=0.483)["the_book_this_would_need"]
            ["decisions_needed_for_the_observed_effect"]
            == _block(observed=0.517)["the_book_this_would_need"]
            ["decisions_needed_for_the_observed_effect"])


def test_more_decisions_never_widens_the_interval():
    """DEFECT: a curve that reads the wrong way round and invites a smaller book.

    Fires on: inverting the exponent's sign.
    """
    excesses = [row["detectable_excess"] for row in _block()["curve"]]
    assert excesses == sorted(excesses, reverse=True)
    assert all(row["detectable_concordance"] > 0.5 for row in _block()["curve"])


# ---------------------------------------------------------------------------------------------
# The reader's end.
# ---------------------------------------------------------------------------------------------

def test_the_live_feed_states_what_the_concordance_could_have_detected():
    """DEFECT: the block exists and the page publishes the null result without it.

    This is the whole point: `cannot_tell` reached the reader on 2026-08-30 and the thing that
    makes it readable did not. Reads the live feed, not a fixture -- a passing unit test beside an
    unpublished field is the shape this project files findings about.

    Fires on: dropping the field from `_method_skill`, or shipping it unavailable.
    """
    msk = json.loads(FEED.read_text(encoding="utf-8"))["method_skill"]
    if not msk.get("available"):
        pytest.skip("this feed carries no method-skill reading to qualify")
    block = msk.get("what_it_could_have_detected") or {}
    assert block.get("available") is True, block.get("reason")
    # The two numbers a reader has to be able to compare, in one sentence, on the same scale.
    assert block["detectable_excess"] == pytest.approx(
        (msk["null_95_high"] - msk["null_95_low"]) / 2.0, rel=1e-12)
    assert block["observed_excess"] == pytest.approx(abs(msk["concordance"] - 0.5), rel=1e-12)
    assert "smallest departure" in block["sentence"]
    # And the funnel's own finding is carried into the book claim rather than left for the reader
    # to join up: eligibility is why only a larger book helps.
    assert "eligibility" in block["the_book_this_would_need"]["why_only_a_larger_book"]


def test_the_floor_is_published_as_a_diagnostic_and_never_as_a_target():
    """DEFECT: R12. A floor on the page reads as a book size to grow towards.

    Fires on: dropping the clause, or softening it to a recommendation.
    """
    note = _block()["it_is_a_diagnostic"]
    assert "NEVER a book size to grow towards" in note
    assert "failure this arm was built to be able to report" in note
