import datetime as dt
import pytest
from company.finance.revenue_accruals import (
    RevenueType, RecognitionBasis, RevenueEntry, RevenueAccrualsLedger
)


def test_entry_period_days():
    e = RevenueEntry('C001', dt.date(2022, 1, 1), dt.date(2022, 1, 31),
                     RevenueType.COMMODITY, RecognitionBasis.BILLED, 310.0, 'electricity')
    assert e.period_days == 31
    assert e.daily_revenue_gbp == pytest.approx(10.0)


def test_post_and_billed():
    ledger = RevenueAccrualsLedger()
    ledger.post('C001', dt.date(2022, 1, 1), dt.date(2022, 1, 31),
                RevenueType.COMMODITY, RecognitionBasis.BILLED, 500.0)
    start, end = dt.date(2022, 1, 1), dt.date(2022, 1, 31)
    assert ledger.billed_revenue_gbp(start, end) == pytest.approx(500.0)
    assert ledger.accrued_revenue_gbp(start, end) == pytest.approx(0.0)


def test_accrued_revenue():
    ledger = RevenueAccrualsLedger()
    ledger.post('C001', dt.date(2022, 1, 1), dt.date(2022, 1, 31),
                RevenueType.COMMODITY, RecognitionBasis.ACCRUED, 300.0)
    start, end = dt.date(2022, 1, 1), dt.date(2022, 1, 31)
    assert ledger.accrual_ratio(start, end) == pytest.approx(100.0)


def test_total_revenue_mix():
    ledger = RevenueAccrualsLedger()
    ledger.post('C001', dt.date(2022, 1, 1), dt.date(2022, 1, 31),
                RevenueType.COMMODITY, RecognitionBasis.BILLED, 400.0)
    ledger.post('C002', dt.date(2022, 1, 1), dt.date(2022, 1, 31),
                RevenueType.COMMODITY, RecognitionBasis.ACCRUED, 100.0)
    start, end = dt.date(2022, 1, 1), dt.date(2022, 1, 31)
    assert ledger.total_revenue_gbp(start, end) == pytest.approx(500.0)
    assert ledger.accrual_ratio(start, end) == pytest.approx(20.0)


def test_by_type():
    ledger = RevenueAccrualsLedger()
    ledger.post('C001', dt.date(2022, 1, 1), dt.date(2022, 1, 31),
                RevenueType.COMMODITY, RecognitionBasis.BILLED, 800.0)
    ledger.post('C001', dt.date(2022, 1, 1), dt.date(2022, 1, 31),
                RevenueType.STANDING_CHARGE, RecognitionBasis.BILLED, 50.0)
    bt = ledger.by_type(dt.date(2022, 1, 1), dt.date(2022, 1, 31))
    assert bt['commodity'] == pytest.approx(800.0)
    assert bt['standing_charge'] == pytest.approx(50.0)


def test_entries_outside_period_excluded():
    ledger = RevenueAccrualsLedger()
    ledger.post('C001', dt.date(2022, 2, 1), dt.date(2022, 2, 28),
                RevenueType.COMMODITY, RecognitionBasis.BILLED, 500.0)
    jan_total = ledger.total_revenue_gbp(dt.date(2022, 1, 1), dt.date(2022, 1, 31))
    assert jan_total == pytest.approx(0.0)


def test_monthly_summary():
    ledger = RevenueAccrualsLedger()
    ledger.post('C001', dt.date(2022, 3, 1), dt.date(2022, 3, 31),
                RevenueType.COMMODITY, RecognitionBasis.BILLED, 1200.0)
    ledger.post('C002', dt.date(2022, 3, 1), dt.date(2022, 3, 31),
                RevenueType.COMMODITY, RecognitionBasis.ACCRUED, 300.0)
    s = ledger.monthly_summary(2022, 3)
    assert s['total_gbp'] == pytest.approx(1500.0)
    assert s['accrual_ratio_pct'] == pytest.approx(20.0)
    assert 'by_type' in s
