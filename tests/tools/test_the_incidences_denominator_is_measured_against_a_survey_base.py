"""The band's lower endpoint is MEASURED against a survey-matched base, not assumed away.

THE DEFECT THIS EXISTS TO CATCH. `_internal_return_as_an_incidence` bands the world between
`J_touched` and `E`, and its upper leg rests on arithmetic while its lower leg rests on ONE named
assumption -- that conversion probability does not decrease with exposure. The band straddles the
tightest annual floor, so that unmeasured assumption is the whole of what stands between an
indeterminate verdict and an established one. The defect is a band endpoint whose width nobody has
measured being read as though its width were known.

THE SECOND DEFECT, AND IT IS THE ONE A NAIVE REPAIR WALKS STRAIGHT INTO. The obvious restriction --
keep only accounts carrying at least `t` of the year ON the product -- conditions the denominator on
the OUTCOME, because converting is what ends a stint. It removes converters faster than it removes
anybody else, by construction rather than by anything about the world, and it reaches an incidence of
exactly ZERO at a full year. A session that ran the directed sweep and published its last row would
have reported that the world's internal return rate is nought. So the outcome-conditioning is
asserted here as a MEASURED property of the capture, and the exposure sweep's collapse is asserted
as a fact about the recorder rather than left as prose.

THE THIRD. The survey-matched point estimate CLEARS the tightest annual floor and its exact interval
does NOT decide it. Those two must not be collapsed: a verdict keyed to the point estimate would
publish an established clearance from a base of 254 accounts. The legs below assert that the two
disagree on this capture AND that the verdict follows the interval, which is what makes the
disagreement a control rather than a coincidence.

THE FOURTH, which is about this file's own subject rather than the code's. `_smallest_deciding_base`
answers "how much sample would settle it", and the predicate it searches is NON-MONOTONE in the
sample size because `round(rate * n)` moves the success count one account at a time. A bisection
returned 1252 and a coarse-grid-then-refine returned 1231 where the true first-clearing size is
1215 -- both overshoot, and an overshoot is the FLATTERING error here because a larger "sample we
would need" is exactly what a reader would not question. The leg for it does not check the number;
it checks the PROPERTY that no smaller size clears.

WHY THE LEGS ARE KEYED TO PROPERTIES AND NOT TO TODAY'S ANSWERS. A leg pinned to "the survey-matched
incidence is 0.188976" reds the moment the SVT decision is recalibrated, which is not a defect and
is the change this reading exists to observe. What is asserted instead is: that the restriction is
monotone; that it shrinks the denominator and not the numerator, with the machinery able to see that
end; that the outcome-conditioned sweep and the outcome-independent one disagree in the direction the
confound predicts; that the verdict is three-valued and follows the interval; that the whole
partition of interval verdicts is reachable, with the unreached value named and its cost stated; and
that a capture carrying nothing produces a named refusal rather than a number.

REUSE
-----
REUSE: tests/tools/test_the_incidences_denominator_is_measured_against_a_survey_base.py
CLASS: CUSTOM
INDEX: searched "survey base", "denominator", "exposure restricted", "incidence", "clopper",
       "binomial interval", "sample size", "opportunity", "accounts touched".
       `tests/tools/test_the_worlds_internal_return_is_stated_in_the_kind_the_record_bounds.py` is
       the nearest row and is deliberately NOT extended: every leg in it asserts what KIND of
       quantity the world's figure is, and the subject here is how wide one endpoint of the
       resulting band is -- a question that only exists once that file's answer is in place. Its
       `the_kind_matched_band` legs must keep passing unchanged while these run, which is itself
       asserted below.
       `tests/tools/test_annualising_the_internal_row_moves_the_floor_and_never_the_ceiling.py`
       owns the bar this reading is judged against and is untouched: it is about what the RECORD's
       arithmetic can do, not about what the world's denominator counts.
       No binomial-interval helper existed anywhere in `tools/`, `simulation/`, `company/`, `saas/`
       or `background/` -- the four matches are bootstrap CIs over arbitrary statistics, which is
       the wrong instrument for an exact small-sample proportion near a bar.
"""

import json

import pytest

from tools import fit_year_level_anchor as anchor


@pytest.fixture(scope="module")
def reading() -> dict:
    """The committed capture's internal-return reading, driven once."""
    rows = json.loads(anchor.DEFAULT_TABLE.read_text())
    svt_rows, reason = anchor.load_svt_decisions(anchor.DEFAULT_TABLE)
    assert svt_rows is not None, f"the capture carries no SVT decisions to read: {reason}"
    return anchor.svt_internal_return_and_tenure(rows, svt_rows)


@pytest.fixture(scope="module")
def base(reading: dict) -> dict:
    return reading["the_base_the_lower_endpoint_divides_by"]


def test_the_exact_binomial_interval_reproduces_published_values() -> None:
    """Clopper-Pearson against textbook values, including both degenerate ends.

    THE DEFECT: an interval routine that is quietly wrong makes every verdict in this reading wrong
    in the SAME direction, and nothing else here could notice -- the verdicts are the only consumers
    and they would simply return a different three-valued answer with no sign of trouble. The two
    degenerate ends are included because they are where a bisection over a tail probability most
    easily returns a limit invented from a tail carrying no observation.
    """
    low, high = anchor._exact_binomial_interval(2, 10)
    assert round(low, 5) == 0.02521
    assert round(high, 5) == 0.55610
    zero_low, zero_high = anchor._exact_binomial_interval(0, 10)
    assert zero_low == 0.0, "no successes cannot earn a positive lower limit"
    assert round(zero_high, 5) == 0.30850
    all_low, all_high = anchor._exact_binomial_interval(10, 10)
    assert round(all_low, 5) == 0.69150
    assert all_high == 1.0, "no failures cannot earn an upper limit below one"
    assert anchor._exact_binomial_interval(0, 0) is None, "no trials is a refusal, not an interval"


def test_the_directed_exposure_restriction_is_shown_to_be_conditioned_on_the_outcome(
    base: dict,
) -> None:
    """The sweep the direction asked for measures the recorder, and the reading says so in numbers.

    THE DEFECT: publishing the exposure-restricted sweep as a reading of the world. Converting ENDS
    a stint, so a converting account-year is mechanically short; raising the threshold strips
    converters out and the last row is an incidence of zero. The three assertions are the evidence
    that this is a property of the capture and not a sentence somebody wrote: the two means, their
    ordering DERIVED rather than declared, and the collapse at a full year.
    """
    outcome = base["the_directed_restriction_is_conditioned_on_the_outcome"]
    assert outcome["converters_are_the_shorter_exposed"] is True
    assert outcome["ratio"] < 1.0
    assert outcome["mean_exposure_of_converting_account_years"] < (
        outcome["mean_exposure_of_every_other_account_year"]
    ), "the derived flag must agree with the two figures it is derived from"
    assert outcome["and_it_reaches_zero_at_a_full_year"] is True
    assert base["restricted_by_exposure"][-1]["accounts_that_converted"] == 0
    assert base["restricted_by_exposure"][-1]["accounts_in_the_base"] > 0, (
        "a base emptied by the restriction would explain the zero without the confound being real"
    )


def test_the_outcome_independent_restriction_shrinks_the_denominator_only(base: dict) -> None:
    """The opportunity sweep loses denominator and keeps every converter, and that is CHECKED.

    THE DEFECT, and it is this project's catalogued equivalence shape: the invariance holds because
    a stint that ends in a conversion STARTED in an earlier year, so every converting account-year
    opens on 1 January. That is a property of this capture's TERM LENGTHS, not of the method --
    shorten fixed terms so a conversion can open and close inside one year and the restriction
    starts losing numerator too. The flag is therefore derived and this leg compares the sweep's own
    first and last rows rather than trusting it.
    """
    sweep = base["restricted_by_opportunity"]
    assert base["the_numerator_survives_the_restriction_whole"] is True
    assert sweep[0]["accounts_that_converted"] == sweep[-1]["accounts_that_converted"]
    assert {row["accounts_that_converted"] for row in sweep} == {
        sweep[0]["accounts_that_converted"]
    }, "one row losing a converter would make the sweep a different measurement at each threshold"
    assert sweep[-1]["accounts_in_the_base"] < sweep[0]["accounts_in_the_base"], (
        "a restriction that removes nobody is not a restriction and would explain the invariance"
    )


def test_the_restriction_is_monotone_in_the_threshold(base: dict) -> None:
    """A tighter base never has a smaller base count or a lower incidence.

    THE DEFECT: a sweep that wandered would mean the threshold is not ordering anything, and every
    statement about "as the base tightens" would be reading noise. Keyed to the ORDERING property
    and not to any row's value, so recalibrating the world leaves it green and breaking the
    restriction reds it.
    """
    sweep = base["restricted_by_opportunity"]
    assert [row["at_least_this_much_of_the_year"] for row in sweep] == sorted(
        row["at_least_this_much_of_the_year"] for row in sweep
    )
    counts = [row["accounts_in_the_base"] for row in sweep]
    assert counts == sorted(counts, reverse=True)
    incidences = [row["incidence"] for row in sweep]
    assert incidences == sorted(incidences)
    assert incidences[0] < incidences[-1], (
        "a flat sweep would mean the touched base and a survey-matched base are the same "
        "population, which is the claim this whole reading exists to test"
    )


def test_the_verdict_follows_the_interval_and_not_the_point_estimate(base: dict) -> None:
    """The two disagree here, and the published verdict is the interval's.

    THE DEFECT, LIVE ON THIS CAPTURE: the survey-matched point estimate is ABOVE the tightest annual
    floor while its exact interval straddles that bar. A verdict keyed to the point estimate would
    publish an established clearance earned by 48 events on a base of 254 -- the same failure as
    publishing a band's upper endpoint as the band, one level down. The disagreement is asserted
    explicitly because a control that only checked "the verdict is None" would pass against a
    function returning None for everything.
    """
    survey = base["the_survey_matched_base"]
    assert base["the_point_estimate_clears_the_tightest_annual_floor"] is True
    assert base["the_interval_decides_the_tightest_annual_floor"] is None
    assert survey["incidence"] > base["the_tightest_annual_floor"]
    low, high = survey["interval_95"]
    assert low < base["the_tightest_annual_floor"] < high, (
        "the interval must genuinely straddle the bar, or the None above is not the straddle answer"
    )
    assert base["the_interval_decides_the_tightest_annual_floor"] == (
        survey["the_interval_decides_the_floor"]
    )


def test_the_interval_verdicts_reach_more_than_one_answer_across_the_sweep(base: dict) -> None:
    """One control over the whole partition, with the value it does NOT reach named and priced.

    THE DEFECT this shape exists to catch is the one CLAUDE.md records being walked into three times
    in one afternoon: a guard that refuses EVERYTHING passes every per-branch assertion about how it
    refuses. So the partition is asserted at once. `True` is genuinely unreachable on this capture --
    it needs the interval's LOWER limit above the bar, which is exactly what
    `the_smallest_base_that_would_decide_it` says takes about five times the sample we have -- so
    that is asserted as a fact with its price attached rather than left as a hole.
    """
    verdicts = {row["the_interval_decides_the_floor"] for row in base["restricted_by_opportunity"]}
    assert False in verdicts, "the loosest bases sit wholly below the bar and must say so"
    assert None in verdicts, "the tightest base straddles the bar and must refuse to decide"
    assert True not in verdicts
    assert base["the_smallest_base_that_would_decide_it"]["accounts"] > (
        base["the_survey_matched_base"]["accounts_in_the_base"]
    ), "if True is unreachable, the reading must say what would make it reachable"


def test_the_survey_matched_reading_is_not_published_as_a_band_endpoint(
    base: dict, reading: dict
) -> None:
    """It exceeds the event rate, so the pair is not ordered and must not be read as a band.

    THE DEFECT: reading the restricted incidence as a new, tighter lower endpoint of
    `the_kind_matched_band`. `J <= E` is an ordering between two readings of the SAME population;
    restricting the base changes the population and nothing carries the ordering across. Here it
    does not survive -- and a hand-written `True` on `the_two_are_still_ordered` would have hidden
    exactly that. The band this reading grades must be left standing UNCHANGED, which is the second
    half of the leg.
    """
    assert base["the_two_are_still_ordered"] is False
    assert base["the_survey_matched_base"]["incidence"] > base["the_worlds_event_rate"]
    incidence = reading["as_an_incidence_which_is_what_the_record_bounds"]
    low, high = incidence["the_kind_matched_band"]
    assert low == incidence["incidence_per_svt_account_touched"], (
        "the published lower endpoint must not have been quietly replaced by the restricted one"
    )
    assert high == base["the_worlds_event_rate"]
    assert incidence["clears_the_tightest_annual_floor"] is None, (
        "the straddle this reading was drawn to narrow is still a straddle, and still says so"
    )


def test_no_smaller_sample_than_the_one_reported_would_decide_it(base: dict) -> None:
    """The reported size is the SMALLEST, which a monotonicity-assuming search does not return.

    THE DEFECT, and it was live in this file's own subject twice before landing: `round(rate * n)`
    makes "does the interval clear the bar" non-monotone in `n`, so a bisection (1252) and a
    coarse-grid-then-refine (1231) both overshot the true 1215. Keyed to the PROPERTY -- the
    reported size clears and a window of smaller ones does not -- so it survives recalibration and
    reds the moment anybody reaches for a faster search that assumes monotonicity.
    """
    smallest = base["the_smallest_base_that_would_decide_it"]
    assert smallest["refused"] is None
    size = smallest["accounts"]
    rate = base["the_survey_matched_base"]["incidence"]
    floor = base["the_tightest_annual_floor"]
    assert anchor._exact_binomial_interval(round(rate * size), size)[0] > floor
    for smaller in range(max(1, size - 40), size):
        assert anchor._exact_binomial_interval(round(rate * smaller), smaller)[0] <= floor, (
            f"{smaller} accounts already decides it, so {size} is not the smallest"
        )


def test_a_rate_below_the_bar_earns_a_named_refusal_rather_than_a_sample_size(base: dict) -> None:
    """No sample size settles a question whose point estimate is on the wrong side of the bar.

    THE DEFECT: scanning to the ceiling and reporting "no base below N would decide it", which reads
    as "we did not look far enough" when the truth is that no base ever would. Those are different
    answers and only one of them is about the world. Driven directly because the capture does not
    produce this branch, and a branch only ever exercised by the capture is a branch nobody has
    established can be taken.
    """
    floor = base["the_tightest_annual_floor"]
    refused = anchor._smallest_deciding_base(254, floor * 0.5, floor)
    assert refused["accounts"] is None
    assert "The gap is in the world, not in the sample" in refused["refused"]
    assert anchor._smallest_deciding_base(254, None, floor)["accounts"] is None
    assert anchor._smallest_deciding_base(0, 0.2, floor)["accounts"] is None
    assert anchor._smallest_deciding_base(254, 0.2, None)["accounts"] is None


def test_a_converting_year_the_denominator_cannot_contain_is_reported_not_absorbed(
    base: dict,
) -> None:
    """The numerator and denominator count populations that differ, and the difference is published.

    THE DEFECT: `accounts_that_converted` is binned on the year a STINT ends and
    `svt_accounts_touched` on the year a SEGMENT falls in, so a stint whose last segment runs into
    January can land a conversion in a year whose denominator does not contain that account. One
    such cell exists here. CLAUDE.md: before dividing two numbers, say what each one counts.

    THE LEG IS A PARTITION AND NOT A HEADCOUNT, and it took a mutation to find out why. A first
    draft asserted only that the stray list was non-empty, and deleting the `not in base` filter --
    which reports every converting stint as a stray, twelve of them on an earlier draft of the
    producer -- left it GREEN. A silent mutation is a missing test or an equivalence and never the
    flattering one; this was the first. What is asserted now is that the converting cells split
    EXACTLY into the ones the denominator contains and the ones it does not, which no filter error
    can satisfy.
    """
    rows = json.loads(anchor.DEFAULT_TABLE.read_text())
    svt_rows, _ = anchor.load_svt_decisions(anchor.DEFAULT_TABLE)
    converting = anchor._converting_account_years(rows, svt_rows)
    strays = base["converter_cells_absent_from_the_denominator"]
    named = strays["stint_end_years_with_no_segment_of_their_own"]
    assert named, "if no cell is misaligned the reading must still say so, not omit the key"
    assert len(named) + strays["converters_inside_the_base"] == len(converting), (
        "every converting account-year is either inside the denominator or reported as outside it; "
        "a count that does not partition means the strays are not what they are labelled"
    )
    assert set(named) == {
        f"{account}@{year}" for account, year in converting
    } - {
        f"{cell['account']}@{cell['year']}"
        for cell in anchor._svt_account_year_cells(svt_rows, converting)
    }
    assert strays["aligned_incidence_on_the_touched_base"] == (
        base["restricted_by_opportunity"][0]["incidence"]
    ), "the aligned figure and the sweep's own untightened row must be the same number"


def test_a_capture_with_no_svt_cells_refuses_rather_than_returning_a_number(base: dict) -> None:
    """Fails closed. An empty capture produces a named refusal, never a zero incidence.

    THE DEFECT: an empty base dividing to `0.0` and being published as an incidence of nought, which
    is the shape `docs/design/CONTROLS_THAT_CANNOT_FAIL.md` calls a producer emptying its own
    evidence. Driven directly, because the committed capture cannot reach this branch and a branch
    nobody can take is not a branch anybody has tested.
    """
    assert base["refused"] is None, "the committed capture must NOT be on the refusing branch"
    empty = anchor._internal_return_incidence_by_its_base([], [], None)
    assert empty["refused"] is not None
    assert "no SVT account-year cell" in empty["refused"]
    assert "incidence" not in empty
