# Increment 3: the legs of tests/company/test_phase_if_coverage_expansion.py that test archived modules. Its live legs stay there.
"""Phase IF: deeper coverage for dsr_book, licence_health, revenue_accruals."""
import datetime as dt
import pytest


# ===== revenue_accruals =====
from company.finance.revenue_accruals import (
    RevenueAccrualsLedger, RevenueType, RecognitionBasis
)

def _ledger():
    ledger = RevenueAccrualsLedger()
    q1_start, q1_end = dt.date(2022,1,1), dt.date(2022,3,31)
    ledger.post("C1",q1_start,q1_end,RevenueType.COMMODITY,RecognitionBasis.BILLED,1200.0)
    ledger.post("C2",q1_start,q1_end,RevenueType.COMMODITY,RecognitionBasis.ACCRUED,400.0)
    ledger.post("C1",q1_start,q1_end,RevenueType.STANDING_CHARGE,RecognitionBasis.BILLED,36.0)
    return ledger

class TestRevenueAccrualsLedgerExpanded:
    def test_period_days_90(self):
        ledger = _ledger()
        e = ledger._entries[0]
        assert e.period_days == 90  # Jan 1 to Mar 31 = 90 days

    def test_daily_revenue_gbp(self):
        ledger = _ledger()
        e = ledger._entries[0]
        assert e.daily_revenue_gbp == pytest.approx(1200.0/90, rel=0.01)

    def test_billed_revenue_in_period(self):
        ledger = _ledger()
        billed = ledger.billed_revenue_gbp(dt.date(2022,1,1),dt.date(2022,3,31))
        assert billed == pytest.approx(1236.0)  # 1200 + 36

    def test_accrued_revenue_in_period(self):
        ledger = _ledger()
        accrued = ledger.accrued_revenue_gbp(dt.date(2022,1,1),dt.date(2022,3,31))
        assert accrued == pytest.approx(400.0)

    def test_total_revenue_in_period(self):
        ledger = _ledger()
        total = ledger.total_revenue_gbp(dt.date(2022,1,1),dt.date(2022,3,31))
        assert total == pytest.approx(1636.0)

    def test_by_type_keys(self):
        ledger = _ledger()
        by_type = ledger.by_type(dt.date(2022,1,1),dt.date(2022,3,31))
        assert "commodity" in by_type and "standing_charge" in by_type

    def test_accrual_ratio(self):
        ledger = _ledger()
        ratio = ledger.accrual_ratio(dt.date(2022,1,1),dt.date(2022,3,31))
        assert ratio == pytest.approx(400/1636*100, rel=0.01)

    def test_accrual_ratio_none_when_no_entries(self):
        ledger = RevenueAccrualsLedger()
        assert ledger.accrual_ratio(dt.date(2022,1,1),dt.date(2022,3,31)) is None

    def test_monthly_summary_keys(self):
        ledger = _ledger()
        s = ledger.monthly_summary(2022,1)
        assert "billed_gbp" in s and "accrual_ratio_pct" in s

    def test_entries_in_period_excludes_non_overlapping(self):
        ledger = _ledger()
        # Q2 should not include Q1 entries
        entries = ledger.entries_in_period(dt.date(2022,4,1),dt.date(2022,6,30))
        assert len(entries) == 0
