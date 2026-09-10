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
              # THE SETTLED BOOK THE 46 SCORED ACCOUNTS CAME OUT OF. Injected for the same reason
              # the ceiling is, and REQUIRED from 2026-09-10: without it a requirement in
              # scored-decision accounts cannot be carried into the population the ceiling counts,
              # and the block correctly refuses to compare them at all. Held at the live run's own
              # ratio of settled to scored accounts (164:72).
              "settled_book_accounts": 105,
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

def test_the_attainability_verdict_can_refuse_and_can_decline_and_can_do_nothing_else():
    """DEFECT: the verdict is unreachable in one of its directions -- it answers the same whatever
    it is given.

    THE REACHABILITY CONTROL, over the WHOLE partition in one assertion rather than a leg per
    branch, because a verdict stuck on any single value passes every per-branch test.

    REKEYED 2026-09-10, AND THE REKEY IS THE FINDING. Until today this test asserted that a
    departure fitting under the ceiling came back `True`, and it passed -- on arithmetic that
    could not support it. The ceiling is an UPPER bound on the book (its own block says the
    affordable book is SMALLER than the number and never larger), so `needed <= ceiling` says
    nothing whatever: the real book may be smaller than the ceiling AND smaller than the
    requirement. Only `needed > ceiling` is safe. So the reachable partition is {False, None} and
    `True` is not a value this arithmetic may produce at any effect size -- which is the property
    keyed here, rather than today's answer for any one reading.

    Fires on: restoring `needed <= ceiling_accounts` as the verdict, hard-coding either surviving
    value, or dropping the population bridge so only one branch can ever be reached.
    """
    # 0.517 needs ~806 scored accounts -- about 1,840 settled -- against a 632 ceiling. 0.540
    # needs far fewer, and fits under it.
    tight = _block()["the_book_this_would_need"]
    roomy = _block(observed=0.54)["the_book_this_would_need"]
    assert tight["settled_accounts_needed_for_the_observed_effect"] > 632
    assert roomy["settled_accounts_needed_for_the_observed_effect"] < 632
    # THE REFUSAL IS REACHABLE...
    assert tight["the_observed_effect_is_attainable"] is False
    assert tight["why_no_attainability_verdict"] is None
    assert tight["accounts_short"] > 0
    # ...AND SO IS THE DECLINE, on the very reading that used to come back affirmative, and it
    # names the upper bound as its reason rather than going out bare.
    assert roomy["the_observed_effect_is_attainable"] is None
    assert "UPPER bound" in roomy["why_no_attainability_verdict"]
    # ...AND NOTHING ANYWHERE PRODUCES THE AFFIRMATIVE. Swept across the whole range of readings
    # this instrument can take, so a `True` surviving at some effect size cannot hide.
    for observed in (0.501, 0.52, 0.54, 0.60, 0.75, 0.99, 0.46, 0.25):
        block = _block(observed=observed)["the_book_this_would_need"]
        assert block["the_observed_effect_is_attainable"] in (False, None), observed
    # And both surviving branches are present in the published floor ladder, so the page carries a
    # scale rather than a single verdict.
    within = {row["within_the_settled_book_ceiling"] for row in _block()["floor"]}
    assert within == {False, None}


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
    assert "cannot say" in blind["sentence"]
    # AND THE PROBE'S OWN REASON REACHES THE READER, rather than a bare absence a reader must
    # guess at. A refusal that does not say why is how a wrong refusal survives.
    assert "probe unavailable" in book["why_no_attainability_verdict"]
    assert "probe unavailable" in blind["sentence"]
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
    assert "this page cannot say" in _block(observed=0.54)["sentence"]


def test_the_page_can_never_serve_the_words_a_book_this_world_can_supply_does_reach_it():
    """DEFECT: THE ONE THIS REPAIR IS FOR. The page served a positive reachability claim off an
    upper bound, twice, for six days.

    The exact words a reader got were "The settled book can hold 632 accounts, so a book this
    world can supply does reach it". Every part of that was composed correctly from a comparison
    that was not a quantity: 632 was the ceiling at `years=1` against a requirement in accounts
    counted over the run's whole window, in a DIFFERENT population, read in the one direction an
    upper bound cannot be read in.

    KEYED TO THE READER'S SENTENCE AND NOT TO THE FLAG, because the flag is not what misled
    anyone. Swept over the whole range of readings, so the claim cannot come back at one effect
    size, and over an available ceiling as well as an unreadable one.

    Fires on: restoring the affirmative branch in `_detectability_sentence`. Reintroducing a
    `True` path into `_attainability` alone does NOT fire it -- measured, not assumed -- because
    there is no longer a branch for that verdict to reach. The test above is what catches that
    half, and it takes both of them to cover the defect as it actually shipped.
    """
    for observed in (0.501, 0.52, 0.54, 0.60, 0.75, 0.99, 0.46, 0.25):
        for over in ({}, {"ceiling": {"available": False, "reason": "probe unavailable"}}):
            sentence = _block(observed=observed, **over)["sentence"]
            assert "does reach it" not in sentence, (observed, over)
            # ...and not the assembled claim under any rewording. The refusal itself contains the
            # words "can supply", so the phrase alone is not the subject -- the AFFIRMATIVE is.
            assert "can supply does" not in sentence, (observed, over)
            assert "settled book can hold" not in sentence, (observed, over)


def test_a_ceiling_read_at_no_window_refuses_rather_than_defaulting_to_one_year():
    """DEFECT: THE UNITS LEG. A per-customer-YEAR figure compared against accounts counted over a
    ten-year window, with the ratio published as a verdict.

    `settled_book_ceiling` divides by `years`: 632 accounts at one, 63 at ten. `CEILING_SOURCE`
    read `years=1` and nothing named the window the requirement was in, so the comparison was
    between two quantities that differ by an order of magnitude. 63 is fewer than the 164 accounts
    this book demonstrably settles, which is how a reader could have seen it.

    Fires on: restoring a default for `window_years`, or accepting a non-positive one.
    """
    assert ic.settled_book_ceiling_accounts()["available"] is False
    assert "per customer-YEAR" in ic.settled_book_ceiling_accounts()["reason"]
    for bad in (0, -1, 1.5, "10"):
        assert ic.settled_book_ceiling_accounts(window_years=bad)["available"] is False, bad
    # ...and the window it IS read at travels with the number, so no later reader can put it over
    # a requirement counted over a different one.
    live = ic.settled_book_ceiling_accounts(window_years=1)
    if not live["available"]:  # a probe report this box cannot read is not this test's subject
        pytest.skip(live["reason"])
    assert live["window_years"] == 1
    assert "years=1" in live["source"]
    decade = ic.settled_book_ceiling_accounts(window_years=10)
    assert decade["accounts"] < live["accounts"]
    assert "years=10" in decade["source"]


def test_a_requirement_is_carried_into_the_ceilings_own_population_before_any_comparison():
    """DEFECT: THE POPULATION LEG. A requirement in accounts that carry a SCORED DECISION,
    compared against a ceiling on the SETTLED BOOK those were drawn from.

    They are 72 and 164 on the live run, so the requirement understated the book by 2.3x -- on top
    of the units error, and in the same direction. `settled_accounts_needed_...` is the carry, and
    the comparison may only ever be made on it.

    Fires on: comparing `accounts_needed_...` against the ceiling directly, or defaulting the
    ratio to 1 when the run declares no settled book.
    """
    book = _block()["the_book_this_would_need"]
    ratio = book["settled_accounts_per_scored_account"]
    assert ratio == pytest.approx(105 / 46)
    assert ratio > 1
    assert (book["settled_accounts_needed_for_the_observed_effect"]
            == math.ceil(book["accounts_needed_for_the_observed_effect"] * ratio))
    # THE CARRY IS WHAT DECIDES, not the scored count. Under a ceiling sitting BETWEEN the two, a
    # comparison made on the scored count says "fits" and the honest one says "does not" -- so
    # this asserts the verdict follows the carried figure, which is the whole defect.
    between = (book["accounts_needed_for_the_observed_effect"]
               + book["settled_accounts_needed_for_the_observed_effect"]) // 2
    straddled = _block(ceiling={"available": True, "accounts": between, "source": "injected"})
    assert straddled["the_book_this_would_need"]["the_observed_effect_is_attainable"] is False
    # ...and with no settled book declared, there is no carry and therefore no comparison at all.
    blind = _block(settled_book_accounts=None)["the_book_this_would_need"]
    assert blind["settled_accounts_needed_for_the_observed_effect"] is None
    assert blind["the_observed_effect_is_attainable"] is None
    assert "not the same set" in blind["why_no_attainability_verdict"]


def test_the_ceiling_row_on_the_decisions_curve_is_carried_across_the_same_bridge():
    """DEFECT: the same population error, one field along, where nobody looked for it.

    `scored_decisions_at_the_ceiling` multiplied a SETTLED-book account count by a
    decisions-per-SCORED-account rate, so the curve placed the ceiling further right than it
    belongs and the excess it "resolves at best" was better than the truth.

    Fires on: reverting to `ceiling_accounts * per_account`, or emitting the row with no bridge.
    """
    block = _block()
    book = block["the_book_this_would_need"]
    per_account = block["scored_decisions_per_account"]
    ratio = book["settled_accounts_per_scored_account"]
    assert book["scored_decisions_at_the_ceiling"] == int(632 / ratio * per_account)
    # The uncarried figure is strictly larger, which is why this was flattering and not merely
    # wrong -- so assert the published one is BELOW it rather than merely different.
    assert book["scored_decisions_at_the_ceiling"] < int(632 * per_account)
    # With no bridge there is no row: an absent ceiling on the curve beats a misplaced one.
    blind = _block(settled_book_accounts=None)
    assert blind["the_book_this_would_need"]["scored_decisions_at_the_ceiling"] is None
    assert not any(row.get("is_the_ceiling") for row in blind["curve"])


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
