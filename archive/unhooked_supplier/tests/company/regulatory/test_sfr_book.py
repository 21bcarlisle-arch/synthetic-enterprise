import datetime as dt
import pytest
from company.regulatory.sfr_book import (
    SFRStatus, SFRMetric, SFRAssessment, SFRBook
)

Q_END = dt.date(2023, 3, 31)


def _passing_assessment(**kwargs):
    defaults = dict(
        quarter_end=Q_END,
        liquidity_days=50.0,
        credit_balance_cover_pct=1.0,
        hedge_ratio_pct=0.80,
        return_filed=True,
    )
    defaults.update(kwargs)
    return SFRAssessment(**defaults)


def test_status_pass_all_green():
    a = _passing_assessment()
    assert a.overall_status == SFRStatus.PASS
    assert a.liquidity_status == "GREEN"
    assert a.hedge_status == "GREEN"


def test_status_watch_amber_liquidity():
    a = _passing_assessment(liquidity_days=35.0)
    assert a.liquidity_status == "AMBER"
    assert a.overall_status == SFRStatus.WATCH


def test_status_breach_low_liquidity():
    a = _passing_assessment(liquidity_days=25.0)
    assert a.liquidity_status == "RED"
    assert a.overall_status == SFRStatus.BREACH
    assert SFRMetric.LIQUIDITY in a.breach_metrics


def test_status_breach_low_hedge_ratio():
    a = _passing_assessment(hedge_ratio_pct=0.50)
    assert a.hedge_status == "RED"
    assert a.overall_status == SFRStatus.BREACH
    assert SFRMetric.HEDGE_RATIO in a.breach_metrics


def test_status_breach_unfiled_return():
    a = _passing_assessment(return_filed=False)
    assert a.overall_status == SFRStatus.BREACH
    assert SFRMetric.QUARTERLY_RETURN_FILED in a.breach_metrics


def test_status_breach_credit_balance_not_covered():
    a = _passing_assessment(credit_balance_cover_pct=0.85)
    assert a.credit_cover_status == "RED"
    assert a.overall_status == SFRStatus.BREACH
    assert SFRMetric.CREDIT_BALANCE_COVER in a.breach_metrics


def test_multiple_breach_metrics():
    a = _passing_assessment(liquidity_days=20.0, hedge_ratio_pct=0.40)
    breaches = a.breach_metrics
    assert SFRMetric.LIQUIDITY in breaches
    assert SFRMetric.HEDGE_RATIO in breaches


def test_book_record_and_latest():
    book = SFRBook()
    a1 = book.record_assessment(Q_END, 50.0, 1.0, 0.80, True)
    q2 = dt.date(2023, 6, 30)
    a2 = book.record_assessment(q2, 45.0, 1.0, 0.75, True)
    latest = book.latest_assessment()
    assert latest.quarter_end == q2


def test_book_file_return():
    book = SFRBook()
    book.record_assessment(Q_END, 50.0, 1.0, 0.80, return_filed=False)
    assert book.latest_assessment().return_filed is False
    updated = book.file_return(Q_END)
    assert updated.return_filed is True
    assert book.latest_assessment().return_filed is True


def test_book_breach_quarters():
    book = SFRBook()
    book.record_assessment(Q_END, 50.0, 1.0, 0.80, True)           # PASS
    book.record_assessment(dt.date(2023, 6, 30), 22.0, 1.0, 0.80, True)   # BREACH
    book.record_assessment(dt.date(2023, 9, 30), 35.0, 1.0, 0.65, True)   # WATCH
    assert len(book.breach_quarters()) == 1


def test_book_sfr_summary():
    book = SFRBook()
    book.record_assessment(Q_END, 50.0, 1.0, 0.82, True)
    book.record_assessment(dt.date(2023, 6, 30), 38.0, 1.0, 0.68, True)
    s = book.sfr_summary()
    assert s["total_quarters"] == 2
    assert s["breach_quarters"] == 0
    assert s["watch_quarters"] == 1
    assert s["latest_status"] == "WATCH"
    assert s["latest_liquidity_days"] == pytest.approx(38.0)
    assert s["latest_hedge_ratio_pct"] == pytest.approx(0.68)


# --- Phase LM depth tests ---

def test_quarter_end_stored():
    a = _passing_assessment(quarter_end=dt.date(2023, 9, 30))
    assert a.quarter_end == dt.date(2023, 9, 30)


def test_liquidity_days_stored():
    a = _passing_assessment(liquidity_days=42.5)
    assert a.liquidity_days == pytest.approx(42.5)


def test_credit_balance_cover_stored():
    a = _passing_assessment(credit_balance_cover_pct=0.95)
    assert a.credit_balance_cover_pct == pytest.approx(0.95)


def test_hedge_ratio_stored():
    a = _passing_assessment(hedge_ratio_pct=0.73)
    assert a.hedge_ratio_pct == pytest.approx(0.73)


def test_return_filed_stored():
    a = _passing_assessment(return_filed=True)
    assert a.return_filed is True


def test_liquidity_amber_at_30_days():
    a = _passing_assessment(liquidity_days=30.0)
    assert a.liquidity_status == "AMBER"
    assert a.overall_status == SFRStatus.WATCH


def test_hedge_amber_at_60pct():
    a = _passing_assessment(hedge_ratio_pct=0.60)
    assert a.hedge_status == "AMBER"
    assert a.overall_status == SFRStatus.WATCH


def test_no_breach_metrics_when_pass():
    a = _passing_assessment()
    assert a.breach_metrics == []


def test_file_return_unknown_quarter():
    book = SFRBook()
    result = book.file_return(dt.date(2099, 12, 31))
    assert result is None


def test_sfr_summary_latest_none_when_empty():
    book = SFRBook()
    s = book.sfr_summary()
    assert s["latest_status"] is None
