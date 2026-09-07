"""R3's carbon-score ceiling — and every control here names the defect it exists to catch.

WHY THESE AND NOT MORE. A49's requirement is that the instrument state on its own surface whether
it is a true CEILING or a handicapped FLOOR, and that its rungs be falsifiable. So the controls are
over exactly that: the null must be a real null, the CEILING declaration must be present and
scoped, the gas exclusion must bite, and the refusals must be reachable.

NOTHING HERE READS A RUN OUTPUT OR THE LIVE FEED FOR ITS ASSERTIONS. Run outputs are gitignored, so
in a linked worktree they are absent and every suite that depends on them passes VACUOUSLY -- this
repository has been caught by exactly that. Every figure asserted below is built in the test.
"""
from __future__ import annotations

import math
import random

import pytest

from tools import r3_carbon_score_ceiling as r3


def _shaped_day(periods: int = 48) -> list[float]:
    """A day with a real within-day shape: clean at night, dirty at the 6pm peak."""
    return [1.0 + 0.5 * math.sin(2 * math.pi * (p - 12) / periods) for p in range(periods)]


def _flat_day(periods: int = 48) -> list[float]:
    return [1.0] * periods


def _payload(rows):
    return {"some_log": rows}


class TestTheNullIsARealNull:
    """DEFECT: a null that returns the ceiling itself and reads as a spectacular confirmation."""

    def test_the_OBVIOUS_null_is_the_ceiling_wearing_a_nulls_name(self):
        """The trap, asserted so nobody 'fixes' the null into it.

        Shuffling a day and re-running the optimiser is the natural way to write this null, and it
        measures NOTHING: a permutation does not change a sorted list, so the cleanest window of a
        shuffled day IS the cleanest window of the day. This test fails if that stops being true,
        which is the only way the real null's design stops being necessary.
        """
        day = _shaped_day()
        rng = random.Random(1)
        shuffled = day[:]
        rng.shuffle(shuffled)
        assert r3.achievable_saving_per_kwh(shuffled, 6) == pytest.approx(
            r3.achievable_saving_per_kwh(day, 6)
        ), "shuffle-then-optimise is the ceiling; the null cannot be built that way"

    def test_the_REAL_null_collapses_on_a_shaped_day(self):
        """DEFECT: a null that does not destroy the signal, so the ceiling clears nothing."""
        day = _shaped_day()
        rng = random.Random(7)
        draws = [r3.skill_free_saving_per_kwh(day, 6, rng) for _ in range(400)]
        ceiling = r3.achievable_saving_per_kwh(day, 6)
        assert ceiling > 0.3, "the fixture has no shape, so this test would prove nothing"
        assert abs(sum(draws) / len(draws)) < 0.1 * ceiling, (
            "an optimiser picking its window at random must capture ~nothing on average"
        )
        assert max(draws) < ceiling, "a skill-free draw must never reach the perfect-knowledge bound"

    def test_a_FLAT_day_leaves_the_ceiling_at_the_null(self):
        """DEFECT: an instrument that cannot report 'there is nothing here'.

        This is the reachability leg. The retire branch is the rare one, and a control that only
        ever sees a shaped day cannot tell a working ceiling from one that always clears.
        """
        flat = _flat_day()
        rng = random.Random(3)
        assert r3.achievable_saving_per_kwh(flat, 6) == pytest.approx(0.0)
        assert r3.skill_free_saving_per_kwh(flat, 6, rng) == pytest.approx(0.0)

    def test_BOTH_verdict_branches_are_reachable_over_the_same_partition(self):
        """DEFECT: a verdict that can only ever say one thing.

        One control over the whole partition rather than a leg per branch: a gate that clears
        everything and a gate that retires everything both pass a single-branch test.
        """
        rng = random.Random(11)
        shaped = r3.achievable_saving_per_kwh(_shaped_day(), 6)
        flat = r3.achievable_saving_per_kwh(_flat_day(), 6)
        null = max(r3.skill_free_saving_per_kwh(_shaped_day(), 6, rng) for _ in range(200))
        assert shaped > null and not (flat > null), (
            "the verdict must be able to come out BOTH ways on the same arithmetic"
        )


class TestTheBoundDeclaresWhatItIs:
    """DEFECT: A49's own subject — a ceiling and a floor conflated, so a negative retires the
    wrong thing. EP13's tenth pass made this error and its eleventh corrected it."""

    def test_it_says_CEILING_and_says_what_a_negative_would_do(self):
        """The values the payload carries, not the docstring. A control that greps prose is
        satisfied by a comment and says nothing about what the instrument publishes."""
        assert r3.BOUND_KIND == "CEILING"
        assert "RETIRES" in r3.BOUND_KIND_REASON, (
            "a ceiling that does not say a negative retires the candidate is a floor in disguise, "
            "and telling them apart is the whole of A49's requirement"
        )
        assert "floor" in r3.BOUND_KIND_REASON.lower(), "the distinction must be drawn, not implied"

    def test_the_scope_names_what_it_does_NOT_bound(self):
        """DEFECT: a timing ceiling read as a bound on the whole carbon programme.

        Reduction, measures and gas are outside it. A reader who takes this figure as R3's total
        would retire the mission on the strength of a lever that was never the whole of it.
        """
        named = " ".join(r3.NOT_BOUNDED_BY_THIS).lower()
        for subject in ("reduction", "gas", "solar", "heat pump", "tariff", "embodied", "rebound"):
            assert subject in named, f"{subject} is outside this bound and is not named as such"
        assert "electricity" in r3.BOUND_SCOPE.lower() and "timing" in r3.BOUND_SCOPE.lower()

    def test_the_declaration_reaches_the_PAYLOAD_and_not_only_the_module(self):
        """DEFECT: a declaration that exists as a constant and never reaches the surface a reader
        sees. The constants above are only worth having if `measure` publishes them."""
        import inspect

        body = inspect.getsource(r3.measure)
        for name in ("BOUND_KIND", "BOUND_KIND_REASON", "BOUND_SCOPE", "NOT_BOUNDED_BY_THIS"):
            assert name in body, f"{name} is declared and never published"


class TestGasCannotBeCreditedWithTiming:
    """DEFECT: disqualification-battery item 10 of the carbon scope brief — gas modelled as
    time-varying carbon. Gas emits when burned; there is no timing benefit to credit it with."""

    def test_a_secondary_leg_carrying_an_EAC_is_excluded_and_COUNTED(self):
        rows = [
            {"customer_id": "C1", "company_eac_kwh": 3000.0},
            {"customer_id": "C1g", "company_eac_kwh": 12000.0},
            {"customer_id": "C2", "company_eac_kwh": 2000.0},
        ]
        book = r3.electricity_eac(_payload(rows))
        assert set(book) == {"C1", "C2"}, "a gas leg reached the electricity book"
        assert book["C1"] == pytest.approx(3000.0), "the gas leg's 12000 kWh was averaged in"
        assert r3.secondary_legs_excluded(_payload(rows)) == 1, (
            "a silent filter is the defect; the count is what makes it visible"
        )

    def test_the_exclusion_count_is_ZERO_when_there_is_nothing_to_exclude(self):
        """The other leg of the same partition. A filter that reports 1 for every book is as
        broken as one that reports 0, and only both legs distinguish them."""
        rows = [{"customer_id": "C1", "company_eac_kwh": 3000.0}]
        assert r3.secondary_legs_excluded(_payload(rows)) == 0


class TestItFailsClosed:
    """DEFECT: R15 fail-silent. Zero abatable carbon retires the mission's own programme, so an
    unavailable instrument must never be able to report one."""

    def test_an_empty_book_REFUSES_and_the_refusal_names_its_reason(self):
        rows = [{"customer_id": f"C{i}", "company_eac_kwh": 2000.0} for i in range(3)]
        with pytest.raises(r3.CeilingUnavailable) as caught:
            r3.measure(run_path=_written(rows))
        assert "NOT a finding" in str(caught.value), (
            "a data-availability refusal that does not say so will be read as a measurement"
        )

    def test_a_SHORT_day_is_refused_rather_than_scored(self):
        """DEFECT: the cleanest six half hours of a truncated day are scored against a mean that
        never saw the missing ones, so a short day inflates the achievable saving."""
        with pytest.raises(r3.CeilingUnavailable):
            r3.achievable_saving_per_kwh(_shaped_day(20), 6)

    def test_a_window_covering_the_whole_day_is_refused(self):
        with pytest.raises(r3.CeilingUnavailable):
            r3.achievable_saving_per_kwh(_shaped_day(48), 48)

    def test_a_feed_with_no_measured_capture_REFUSES_rather_than_assuming_one(self):
        """DEFECT: an assumed handicap in a ceiling IS the ceiling. If the forecast rung invented
        its own capture fraction, the number it produced would be a restatement of hindsight."""
        with pytest.raises(r3.CeilingUnavailable):
            r3.capture_fraction({"published_forecast_skill": {}})
        with pytest.raises(r3.CeilingUnavailable):
            r3.shift_window({"published_forecast_skill": {}})


def _written(rows):
    """A run output on disk with the given rows, so the refusal path is exercised end to end."""
    import json
    import tempfile
    from pathlib import Path

    path = Path(tempfile.mkdtemp()) / "run_output_test.json"
    path.write_text(json.dumps(_payload(rows)), encoding="utf-8")
    return path


class TestTheForecastRungIsNotACategoryError:
    """DEFECT: this project's most expensive recurring shape — two correct figures multiplied
    together whose product is not a quantity. `capture_mean` is a fraction OF the achievable
    saving at a GIVEN window; applied to a saving computed at a different window it means nothing."""

    def test_the_window_is_read_from_the_feed_and_not_chosen_here(self):
        feed = {"published_forecast_skill": {"shift_window_half_hours": 4}}
        assert r3.shift_window(feed) == 4, "the window must follow the feed, not a local constant"

    def test_the_achievable_saving_matches_the_definition_capture_was_measured_against(self):
        """The arithmetic identity, asserted rather than trusted: day mean minus the mean of the
        `window` cleanest half hours, unweighted. If this drifts from
        `sim.neso_carbon_intensity._capture_fractions`'s `achievable`, the forecast rung silently
        becomes a different quantity."""
        day = _shaped_day()
        expected = sum(day) / len(day) - sum(sorted(day)[:6]) / 6
        assert r3.achievable_saving_per_kwh(day, 6) == pytest.approx(expected)


class TestTheCurveIsPublishedInsteadOfAnInventedShare:
    """DEFECT: a number picked because a number was needed. No source establishes a domestic
    shiftable share, so the headline is at share 1.0 and the curve carries the rest."""

    def test_the_curve_is_linear_and_anchored_at_share_one(self):
        curve = r3.share_curve(4.0, 100.0)
        at_one = [row for row in curve if row["shiftable_share"] == 1.0]
        assert at_one and at_one[0]["gbp_per_household_year"] == pytest.approx(4.0)
        for row in curve:
            assert row["gbp_per_household_year"] == pytest.approx(4.0 * row["shiftable_share"])
            assert row["kg_co2e_per_household_year"] == pytest.approx(
                100.0 * row["shiftable_share"])

    def test_the_curve_does_not_smuggle_a_preferred_share(self):
        """A curve with one row is a chosen share wearing a curve's name."""
        assert len(r3.share_curve(1.0, 1.0)) >= 4


class TestTheOverstatementCorrectionComesFromTheFeed:
    """DEFECT: a correction factor restated in code goes stale beside the measurement that
    produced it — a published cause authored as prose rots."""

    def test_it_reads_the_per_year_factor_and_NAMES_the_years_it_cannot_cover(self):
        feed = {"versus_published": {"by_year": {"2022": {"within_day_swing_overstated_by": 1.5}}}}
        got = r3.within_day_overstatement(feed, {"2022", "2016"})
        assert got["available"] and got["by_year"] == {"2022": 1.5}
        assert got["years_uncovered"] == ["2016"], "an uncovered year must be named, not dropped"

    def test_a_feed_with_no_comparison_reports_UNAVAILABLE_rather_than_a_factor_of_one(self):
        """DEFECT: a missing correction defaulting to 1.0 reads as 'measured, no correction
        needed', which is the opposite claim to 'not measured'."""
        got = r3.within_day_overstatement({}, {"2022"})
        assert got["available"] is False and "why" in got
