"""Tests for Phase GA: CSS Performance Register."""
import datetime as dt
from company.compliance.working_days import add_working_days as _add_working_days

# ── helpers ──────────────────────────────────────────────────────────────────

REQ = dt.date(2023, 7, 3)   # Monday (after CSS go-live)
ELEC = "electricity"
GAS = "gas"


# ── _add_working_days ────────────────────────────────────────────────────────

class TestAddWorkingDays:

    def test_five_working_days_from_monday(self):
        monday = dt.date(2024, 1, 1)
        assert _add_working_days(monday, 5) == dt.date(2024, 1, 8)

    def test_skips_weekend(self):
        friday = dt.date(2024, 1, 5)
        # 1WD from Fri = Mon 8 Jan
        assert _add_working_days(friday, 1) == dt.date(2024, 1, 8)

    def test_five_from_friday_spans_weekend(self):
        friday = dt.date(2024, 1, 5)
        assert _add_working_days(friday, 5) == dt.date(2024, 1, 12)


# ── CSSPerformanceRecord ─────────────────────────────────────────────────────



# ── CSSPerformanceRegister ───────────────────────────────────────────────────

