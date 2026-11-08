"""Tests for Customer Service Ticket Book (Phase EW)."""
import datetime as dt
import pytest
from company.compliance.working_days import add_working_days as _add_working_days

DATE = dt.date(2024, 1, 15)


class TestAddWorkingDays:
    def test_adds_3_wd(self):
        mon = dt.date(2024, 1, 15)  # Monday
        result = _add_working_days(mon, 3)
        assert result == dt.date(2024, 1, 18)  # Thursday

    def test_skips_weekend(self):
        fri = dt.date(2024, 1, 19)  # Friday
        result = _add_working_days(fri, 1)
        assert result == dt.date(2024, 1, 22)  # Monday






