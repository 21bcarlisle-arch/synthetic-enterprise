"""Q5 of the EP6 blind review: a response that NEVER ARRIVES, and the caller's
defined behaviour at 1 min / 24 h / 5 working days.

R15 throughout: every control here is paired with the mutation or null control
that makes it able to fail. The two that matter most are named on their tests --
the calendar-vs-working-day differential (a ladder built on calendar days passes
every other test in this file) and the bank-holiday differential (a ladder built
on weekends-only passes that one too).
"""
from __future__ import annotations

import datetime as dt

import pytest

from company.compliance.working_days import OutsideCalendarCoverage
from company.interfaces.crossing_silence import (
    ABANDONED_AFTER_WORKING_DAYS,
    LATE_AFTER,
    OVERDUE_AFTER,
    SILENCE_OBLIGATION,
    SilenceHorizon,
    conclude_silence,
    silence_horizon,
)
from interface.contracts.wall_envelope import WallStatus

# A Monday, chosen so the plain horizons are not accidentally straddling a
# weekend -- the weekend cases below pick their own start deliberately.
MON = dt.datetime(2026, 8, 17, 9, 0)
FRI = dt.datetime(2026, 8, 21, 9, 0)


def horizon(last_heard: dt.datetime, as_of: dt.datetime) -> SilenceHorizon:
    return silence_horizon(last_heard_at=last_heard, as_of=as_of)


# ── the ladder, at and around each stated boundary ───────────────────────────


@pytest.mark.parametrize(
    "elapsed,expected",
    [
        (dt.timedelta(0), SilenceHorizon.IN_FLIGHT),
        (dt.timedelta(seconds=59), SilenceHorizon.IN_FLIGHT),
        (dt.timedelta(minutes=1), SilenceHorizon.LATE),
        (dt.timedelta(hours=23, minutes=59), SilenceHorizon.LATE),
        (dt.timedelta(hours=24), SilenceHorizon.OVERDUE),
        (dt.timedelta(days=3), SilenceHorizon.OVERDUE),
    ],
)
def test_each_stated_horizon_is_reached_at_the_moment_it_names(elapsed, expected):
    """The boundaries are INCLUSIVE, and the second in each pair is the null
    control for the first: one second earlier is a different band."""
    assert horizon(MON, MON + elapsed) == expected


def test_the_boundary_is_inclusive_and_one_second_earlier_is_not():
    """A half-open sliver here would let the company pass a stated deadline and
    still report the band below it -- the direction that flatters."""
    assert horizon(MON, MON + LATE_AFTER) == SilenceHorizon.LATE
    assert horizon(MON, MON + LATE_AFTER - dt.timedelta(seconds=1)) == SilenceHorizon.IN_FLIGHT
    assert horizon(MON, MON + OVERDUE_AFTER) == SilenceHorizon.OVERDUE
    assert horizon(MON, MON + OVERDUE_AFTER - dt.timedelta(seconds=1)) == SilenceHorizon.LATE


def test_five_working_days_reaches_abandoned():
    # Mon 17 -> Mon 24 is exactly 5 working days (18,19,20,21,24).
    assert horizon(MON, MON + dt.timedelta(days=7)) == SilenceHorizon.ABANDONED
    assert horizon(MON, MON + dt.timedelta(days=6)) == SilenceHorizon.OVERDUE


# ── THE differential: working days, not calendar days ────────────────────────


def test_MUTATION_five_CALENDAR_days_over_a_weekend_is_NOT_abandoned():
    """THE control that fails on the defect it exists to catch.

    A ladder built on calendar days passes every other test in this file,
    because they all start on a Monday and never cross a weekend. Here a Friday
    'not yet' plus five calendar days is only THREE working days (Mon/Tue/Wed),
    so a company that abandoned the crossing on the Wednesday would be giving up
    on a counterparty that has had three days to answer, not five.

    The null control is the second assertion: the same start, moved to the day
    that IS five working days out, does reach ABANDONED -- so this test is
    measuring the calendar and not merely refusing to advance.
    """
    assert FRI.strftime("%a") == "Fri"
    five_calendar_days = FRI + dt.timedelta(days=5)   # Wed 26 Aug
    assert five_calendar_days.strftime("%a") == "Wed"
    assert horizon(FRI, five_calendar_days) == SilenceHorizon.OVERDUE

    five_working_days = FRI + dt.timedelta(days=7)    # Fri 28 Aug
    assert horizon(FRI, five_working_days) == SilenceHorizon.ABANDONED


def test_MUTATION_a_bank_holiday_defers_abandonment_so_weekends_only_is_not_enough():
    """The second differential, and the one a weekend-aware/holiday-blind ladder
    still fails.

    Mon 31 Aug 2026 is the late summer bank holiday. From Mon 24, the following
    Monday is only FOUR working days out because the 31st is not one; a ladder
    that skipped weekends but not holidays would abandon the crossing a day
    early. The null control is the next day, which does reach five.
    """
    start = dt.datetime(2026, 8, 24, 9, 0)
    bank_holiday_monday = dt.datetime(2026, 8, 31, 9, 0)
    assert horizon(start, bank_holiday_monday) == SilenceHorizon.OVERDUE
    assert horizon(start, dt.datetime(2026, 9, 1, 9, 0)) == SilenceHorizon.ABANDONED


# ── failing closed ───────────────────────────────────────────────────────────


def test_a_clock_running_backwards_RAISES_rather_than_reporting_in_flight():
    """'No time has passed, so IN_FLIGHT' is a confident wrong answer built from
    a contradiction, and it would hide a Blindfold breach behind the most
    reassuring member of the enum."""
    with pytest.raises(ValueError, match="BEFORE last_heard_at"):
        horizon(MON, MON - dt.timedelta(seconds=1))


def test_mixing_naive_and_aware_datetimes_RAISES_at_this_seam():
    aware = MON.replace(tzinfo=dt.timezone.utc)
    with pytest.raises(ValueError, match="both be naive or both be aware"):
        horizon(MON, aware)
    with pytest.raises(ValueError, match="both be naive or both be aware"):
        horizon(aware, MON)


def test_an_uncovered_calendar_year_RAISES_rather_than_assuming_no_holidays():
    """An unavailable calendar is a FAILED calculation, not a holiday-free one
    (R15 FAIL-SILENT). This asserts the shared primitive's fail-closed behaviour
    propagates through this module rather than being swallowed."""
    with pytest.raises(OutsideCalendarCoverage):
        horizon(dt.datetime(2099, 1, 4, 9, 0), dt.datetime(2099, 1, 20, 9, 0))


def test_every_horizon_has_a_defined_obligation():
    """A horizon with no defined behaviour is precisely the gap Q5 names."""
    assert set(SILENCE_OBLIGATION) == set(SilenceHorizon)
    for band, text in SILENCE_OBLIGATION.items():
        assert text.strip(), band


# ── the conclusion: whose word is it ─────────────────────────────────────────


def test_TIMEOUT_is_concluded_only_at_abandonment_and_only_for_an_owed_answer():
    below = conclude_silence(
        correlation_id="INV-1",
        heard_status=WallStatus.NOT_KNOWABLE_YET,
        last_heard_at=MON,
        as_of=MON + dt.timedelta(days=6),
    )
    assert below.horizon == SilenceHorizon.OVERDUE
    assert below.concluded_status is None, (
        "a conclusion stamped before the horizon asserts an outcome the company "
        "has no grounds for yet"
    )

    at = conclude_silence(
        correlation_id="INV-1",
        heard_status=WallStatus.NOT_KNOWABLE_YET,
        last_heard_at=MON,
        as_of=MON + dt.timedelta(days=7),
    )
    assert at.horizon == SilenceHorizon.ABANDONED
    assert at.concluded_status == WallStatus.TIMEOUT


def test_the_counterparty_word_is_never_overwritten_by_the_company_conclusion():
    """The distinction the whole module exists to keep: 'they told me it timed
    out' is not 'I decided it had'."""
    aged = conclude_silence(
        correlation_id="INV-1",
        heard_status=WallStatus.NOT_KNOWABLE_YET,
        last_heard_at=MON,
        as_of=MON + dt.timedelta(days=7),
    )
    assert aged.heard_status == WallStatus.NOT_KNOWABLE_YET
    assert aged.concluded_status == WallStatus.TIMEOUT
    assert aged.heard_status != aged.concluded_status


@pytest.mark.parametrize("already", [WallStatus.TIMEOUT, WallStatus.ERROR])
def test_a_failed_exchange_is_not_re_concluded_as_a_timeout(already):
    """Re-concluding a TIMEOUT as a TIMEOUT would be the company agreeing with
    itself and counting it as evidence. The horizon still advances -- that is
    the report that the company has sat on its own re-ask."""
    aged = conclude_silence(
        correlation_id="INV-1",
        heard_status=already,
        last_heard_at=MON,
        as_of=MON + dt.timedelta(days=7),
    )
    assert aged.horizon == SilenceHorizon.ABANDONED
    assert aged.concluded_status is None
    assert aged.exchange_failed is True
    assert aged.answer_owed is False


def test_an_OK_crossing_is_refused_by_the_ladder():
    """An OK crossing is RESOLVED and holds no open answer; being handed one
    means the register and its reader disagree about what 'open' means."""
    with pytest.raises(ValueError, match="status OK"):
        conclude_silence(
            correlation_id="INV-1",
            heard_status=WallStatus.OK,
            last_heard_at=MON,
            as_of=MON + dt.timedelta(days=7),
        )


# ── the reader is real, not cosmetic ─────────────────────────────────────────


def test_each_status_releases_a_DIFFERENT_next_move():
    """The defect this closes: both consumers branched on `status != OK`, so
    TIMEOUT released exactly what ERROR released and the distinction the
    contract charges for was not bought. Three statuses, three distinct moves."""
    moves = {
        status: conclude_silence(
            correlation_id="INV-1",
            heard_status=status,
            last_heard_at=MON,
            as_of=MON + dt.timedelta(days=7),
        ).next_move
        for status in (
            WallStatus.NOT_KNOWABLE_YET,
            WallStatus.TIMEOUT,
            WallStatus.ERROR,
        )
    }
    assert len(set(moves.values())) == 3, moves


def test_the_owed_answer_move_changes_once_the_promise_goes_stale():
    """`NOT_KNOWABLE_YET` is the one status whose move depends on the horizon --
    within the window the counterparty is simply working; past OVERDUE the
    company's own belief is stale."""
    early = conclude_silence(
        correlation_id="INV-1",
        heard_status=WallStatus.NOT_KNOWABLE_YET,
        last_heard_at=MON,
        as_of=MON + dt.timedelta(seconds=30),
    )
    late = conclude_silence(
        correlation_id="INV-1",
        heard_status=WallStatus.NOT_KNOWABLE_YET,
        last_heard_at=MON,
        as_of=MON + dt.timedelta(days=2),
    )
    assert early.next_move != late.next_move


def test_horizon_ranks_are_ordered_and_at_least_follows_them():
    bands = [
        SilenceHorizon.IN_FLIGHT,
        SilenceHorizon.LATE,
        SilenceHorizon.OVERDUE,
        SilenceHorizon.ABANDONED,
    ]
    assert [b.rank for b in bands] == sorted(b.rank for b in bands)
    assert SilenceHorizon.ABANDONED.at_least(SilenceHorizon.OVERDUE)
    assert not SilenceHorizon.LATE.at_least(SilenceHorizon.OVERDUE)


def test_the_horizon_constants_are_the_ones_the_review_named():
    """Pinned as literals so a silent widening of a deadline is a diff, not a
    behaviour change nobody sees."""
    assert LATE_AFTER == dt.timedelta(minutes=1)
    assert OVERDUE_AFTER == dt.timedelta(hours=24)
    assert ABANDONED_AFTER_WORKING_DAYS == 5
