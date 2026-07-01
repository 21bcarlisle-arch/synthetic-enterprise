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


# --- Phase KD depth tests ---

def test_period_days_single_day():
    e = RevenueEntry('C001', dt.date(2022, 1, 15), dt.date(2022, 1, 15),
                     RevenueType.COMMODITY, RecognitionBasis.BILLED, 10.0, 'electricity')
    assert e.period_days == 1


def test_accrual_ratio_none_empty_period():
    ledger = RevenueAccrualsLedger()
    ratio = ledger.accrual_ratio(dt.date(2022, 1, 1), dt.date(2022, 1, 31))
    assert ratio is None


def test_overlap_entry_starting_before_period():
    ledger = RevenueAccrualsLedger()
    # entry starts before period but ends inside -> should be included
    ledger.post('C001', dt.date(2021, 12, 15), dt.date(2022, 1, 15),
                RevenueType.COMMODITY, RecognitionBasis.BILLED, 500.0)
    assert ledger.total_revenue_gbp(dt.date(2022, 1, 1), dt.date(2022, 1, 31)) == pytest.approx(500.0)


def test_overlap_entry_ending_after_period():
    ledger = RevenueAccrualsLedger()
    # entry starts inside period but ends after -> should be included
    ledger.post('C001', dt.date(2022, 1, 15), dt.date(2022, 2, 15),
                RevenueType.COMMODITY, RecognitionBasis.BILLED, 500.0)
    assert ledger.total_revenue_gbp(dt.date(2022, 1, 1), dt.date(2022, 1, 31)) == pytest.approx(500.0)


def test_billed_excludes_accrued():
    ledger = RevenueAccrualsLedger()
    ledger.post('C001', dt.date(2022, 1, 1), dt.date(2022, 1, 31),
                RevenueType.COMMODITY, RecognitionBasis.BILLED, 400.0)
    ledger.post('C002', dt.date(2022, 1, 1), dt.date(2022, 1, 31),
                RevenueType.COMMODITY, RecognitionBasis.ACCRUED, 100.0)
    assert ledger.billed_revenue_gbp(dt.date(2022, 1, 1), dt.date(2022, 1, 31)) == pytest.approx(400.0)


def test_accrued_excludes_billed():
    ledger = RevenueAccrualsLedger()
    ledger.post('C001', dt.date(2022, 1, 1), dt.date(2022, 1, 31),
                RevenueType.COMMODITY, RecognitionBasis.BILLED, 400.0)
    ledger.post('C002', dt.date(2022, 1, 1), dt.date(2022, 1, 31),
                RevenueType.COMMODITY, RecognitionBasis.ACCRUED, 100.0)
    assert ledger.accrued_revenue_gbp(dt.date(2022, 1, 1), dt.date(2022, 1, 31)) == pytest.approx(100.0)


def test_by_type_exit_fee():
    ledger = RevenueAccrualsLedger()
    ledger.post('C001', dt.date(2022, 1, 1), dt.date(2022, 1, 31),
                RevenueType.EXIT_FEE, RecognitionBasis.BILLED, 75.0)
    bt = ledger.by_type(dt.date(2022, 1, 1), dt.date(2022, 1, 31))
    assert bt['exit_fee'] == pytest.approx(75.0)


def test_monthly_summary_december():
    ledger = RevenueAccrualsLedger()
    ledger.post('C001', dt.date(2022, 12, 1), dt.date(2022, 12, 31),
                RevenueType.COMMODITY, RecognitionBasis.BILLED, 1200.0)
    s = ledger.monthly_summary(2022, 12)
    assert s['total_gbp'] == pytest.approx(1200.0)


def test_multiple_customers_sum():
    ledger = RevenueAccrualsLedger()
    ledger.post('C001', dt.date(2022, 1, 1), dt.date(2022, 1, 31),
                RevenueType.COMMODITY, RecognitionBasis.BILLED, 300.0)
    ledger.post('C002', dt.date(2022, 1, 1), dt.date(2022, 1, 31),
                RevenueType.COMMODITY, RecognitionBasis.BILLED, 200.0)
    assert ledger.billed_revenue_gbp(dt.date(2022, 1, 1), dt.date(2022, 1, 31)) == pytest.approx(500.0)


def test_commodity_stored():
    ledger = RevenueAccrualsLedger()
    entry = ledger.post('C001', dt.date(2022, 1, 1), dt.date(2022, 1, 31),
                        RevenueType.COMMODITY, RecognitionBasis.BILLED, 300.0, 'gas')
    assert entry.commodity == 'gas'
