"""Exit tests for the canonical working-day primitive (R10 class fix).

The point of this module is NOT that it computes weekends correctly -- the 25
implementations it replaces already did that. The point is bank holidays. So the
tests that matter are the ones that would PASS against the old weekend-only code and
must now FAIL it: the moved-figure diffs in `TestMovedFigures`.
"""

import datetime as dt

import pytest

from company.compliance.working_days import (
    Nation,
    OutsideCalendarCoverage,
    add_working_days,
    bank_holidays,
    calendar_coverage,
    is_working_day,
    working_days_between,
)


def _old_weekend_only_add(start: dt.date, n: int) -> dt.date:
    """The arithmetic every one of the 25 pre-existing helpers implemented, verified
    by differential test before the canonical module was written. Kept here as the
    independent oracle for the moved-figure diffs -- NOT imported from any of them, so
    migrating a caller in Pass 2 cannot silently change what this asserts against."""
    d = start
    remaining = n
    while remaining > 0:
        d += dt.timedelta(days=1)
        if d.weekday() < 5:
            remaining -= 1
    return d


class TestCalendarProvenance:
    def test_covers_the_simulated_history_window(self):
        """CLAUDE.md: the sim runs against real 2016-2025 settlement history."""
        lo, hi = calendar_coverage()
        assert lo <= 2016 and hi >= 2026

    def test_known_gds_published_dates_are_present(self):
        """Spot-check against dates reconciled across three GDS sources (see the
        module docstring). Substitute days are the interesting ones -- they are the
        part a hand-written calendar gets wrong."""
        cal = bank_holidays()
        assert dt.date(2026, 12, 28) in cal, "Boxing Day substitute (26th is a Sat)"
        assert dt.date(2025, 12, 25) in cal
        assert dt.date(2026, 4, 3) in cal, "Good Friday 2026"
        assert dt.date(2022, 9, 19) in cal, "Queen Elizabeth II State Funeral"
        assert dt.date(2023, 5, 8) in cal, "Coronation of King Charles III"

    def test_ordinary_working_day_is_not_in_the_calendar(self):
        """Guards against a table so broad it flags everything (a calendar that says
        yes to every date would pass every 'holiday is skipped' test)."""
        assert dt.date(2026, 3, 3) not in bank_holidays()


class TestIsWorkingDay:
    @pytest.mark.parametrize(
        "day,expected",
        [
            (dt.date(2026, 3, 2), True),  # Monday
            (dt.date(2026, 3, 6), True),  # Friday
            (dt.date(2026, 3, 7), False),  # Saturday
            (dt.date(2026, 3, 8), False),  # Sunday
            (dt.date(2026, 12, 25), False),  # Christmas Day, a Friday
            (dt.date(2026, 12, 28), False),  # Boxing Day substitute, a Monday
        ],
    )
    def test_weekday_and_holiday(self, day, expected):
        assert is_working_day(day) is expected

    def test_accepts_datetime(self):
        assert is_working_day(dt.datetime(2026, 12, 25, 9, 30)) is False


class TestAddWorkingDays:
    def test_zero_returns_start_unchanged_even_on_a_holiday(self):
        """Several callers rely on n=0 being identity. It must NOT normalise to the
        next working day."""
        xmas = dt.date(2026, 12, 25)
        assert add_working_days(xmas, 0) == xmas
        saturday = dt.date(2026, 3, 7)
        assert add_working_days(saturday, 0) == saturday

    def test_result_is_always_a_working_day_for_n_at_least_one(self):
        start = dt.date(2026, 12, 24)
        for n in range(1, 30):
            assert is_working_day(add_working_days(start, n))

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            add_working_days(dt.date(2026, 3, 2), -1)

    def test_weekend_start_walks_forward(self):
        # Sat 7 Mar 2026 + 1 wd -> Mon 9 Mar
        assert add_working_days(dt.date(2026, 3, 7), 1) == dt.date(2026, 3, 9)


class TestWorkingDaysBetween:
    def test_interval_is_start_exclusive_end_inclusive(self):
        """The SHIPPED semantics of the 4 implementations replaced -- (start, end].
        The design doc says '[start, end)'; that is the doc's error, and pinning it
        here is what stops a future 'tidy-up' from silently moving every deadline."""
        assert working_days_between(dt.date(2026, 3, 6), dt.date(2026, 3, 7)) == 0
        assert working_days_between(dt.date(2026, 3, 7), dt.date(2026, 3, 9)) == 1

    def test_same_day_is_zero(self):
        d = dt.date(2026, 3, 2)
        assert working_days_between(d, d) == 0

    def test_reversed_range_is_zero(self):
        assert working_days_between(dt.date(2026, 3, 9), dt.date(2026, 3, 2)) == 0

    def test_full_week_is_five(self):
        assert working_days_between(dt.date(2026, 3, 2), dt.date(2026, 3, 9)) == 5


class TestMovedFigures:
    """The whole reason this module exists. Each case asserts the canonical answer
    DIFFERS from the weekend-only oracle -- if these ever go quiet, the bank-holiday
    calendar has stopped being consulted and the class defect is back."""

    def test_christmas_week_deadline_moves(self):
        """A 3-working-day deadline raised on Christmas Eve 2026."""
        start = dt.date(2026, 12, 24)
        old = _old_weekend_only_add(start, 3)
        new = add_working_days(start, 3)
        assert old == dt.date(2026, 12, 29)
        assert new == dt.date(2026, 12, 31)
        assert new > old, "bank holidays must push the deadline later, never earlier"

    def test_slc14_ten_working_day_refund_deadline_moves_over_easter(self):
        """SLC 14: a credit refund is due within 10 working days. Good Friday and
        Easter Monday 2026 both fall inside this window."""
        request = dt.date(2026, 3, 30)
        old = _old_weekend_only_add(request, 10)
        new = add_working_days(request, 10)
        assert new == old + dt.timedelta(days=2)

    def test_early_may_bank_holiday_moves_a_two_day_ack(self):
        """SLC-style 2-working-day acknowledgement raised the Friday before the
        Early May bank holiday 2026 (Mon 4 May)."""
        raised = dt.date(2026, 5, 1)
        assert _old_weekend_only_add(raised, 2) == dt.date(2026, 5, 5)
        assert add_working_days(raised, 2) == dt.date(2026, 5, 6)

    def test_no_divergence_when_no_holiday_falls_in_the_window(self):
        """The counterpart that stops the above from being satisfied by a module that
        simply adds days to everything: an ordinary March window must be UNCHANGED."""
        start = dt.date(2026, 3, 2)
        assert add_working_days(start, 5) == _old_weekend_only_add(start, 5)

    def test_working_days_between_counts_the_holiday_out(self):
        # Christmas week 2026: 25th (Fri, Xmas) and 28th (Mon, Boxing sub) are out.
        start, end = dt.date(2026, 12, 24), dt.date(2026, 12, 31)
        assert working_days_between(start, end) == 3  # 29, 30, 31
        assert working_days_between(start, end) < 5


class TestFailsClosedOutsideCoverage:
    """R15: the tempting fail-open is to treat an uncovered year as holiday-free,
    which returns the exact wrong answer this module exists to prevent -- silently,
    and only when the data is missing."""

    def test_year_after_coverage_raises(self):
        _, hi = calendar_coverage()
        with pytest.raises(OutsideCalendarCoverage):
            is_working_day(dt.date(hi + 1, 6, 1))

    def test_year_before_coverage_raises(self):
        lo, _ = calendar_coverage()
        with pytest.raises(OutsideCalendarCoverage):
            add_working_days(dt.date(lo - 1, 6, 1), 3)

    def test_walking_off_the_end_of_the_calendar_raises(self):
        """The subtle one: the START is covered but the arithmetic walks past the
        end of the table. It must raise, not quietly finish weekend-only."""
        _, hi = calendar_coverage()
        with pytest.raises(OutsideCalendarCoverage):
            add_working_days(dt.date(hi, 12, 20), 40)

    def test_between_checks_both_endpoints(self):
        lo, hi = calendar_coverage()
        with pytest.raises(OutsideCalendarCoverage):
            working_days_between(dt.date(hi, 12, 1), dt.date(hi + 1, 1, 10))


class TestNation:
    def test_default_is_england_and_wales(self):
        assert bank_holidays() == bank_holidays(Nation.ENGLAND_AND_WALES)

    def test_unmodelled_nation_is_absent_not_silently_aliased(self):
        """If Scotland is added later it must come with its own table -- it must
        never resolve to the E&W one by default."""
        assert [n.name for n in Nation] == ["ENGLAND_AND_WALES"]
