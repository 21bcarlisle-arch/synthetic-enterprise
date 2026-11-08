"""Tests for Meter Technical Investigation Register -- Phase GZ (SLC 21A)."""
import datetime as dt
from company.compliance.working_days import add_working_days as _add_working_days

TODAY = dt.date(2024, 6, 10)
ACC = "A001"
MPAN = "1000000000001"






class TestAddWorkingDays:
    def test_five_wd_skips_weekend(self):
        result = _add_working_days(dt.date(2024, 6, 10), 5)
        assert result == dt.date(2024, 6, 17)

    def test_20_wd_from_monday(self):
        result = _add_working_days(dt.date(2024, 6, 10), 20)
        assert result == dt.date(2024, 7, 8)

    def test_zero_days(self):
        d = dt.date(2024, 6, 10)
        assert _add_working_days(d, 0) == d




