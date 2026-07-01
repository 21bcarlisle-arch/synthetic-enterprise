"""Phase CA: Service Quality Monitor tests."""
import pytest
from company.crm.service_quality_monitor import (
    ServiceQualityMonitor, ServiceQualityRAG, ServiceQualitySnapshot,
    _CLARITY_AMBER, _CLARITY_RED, _COMPLAINT_AMBER, _COMPLAINT_RED,
    _BILL_SHOCK_AMBER, _BILL_SHOCK_RED,
)


def _mon_with_data():
    mon = ServiceQualityMonitor()
    # Good year
    mon.record(2020, avg_clarity=0.850, avg_complaint_probability=0.040,
               avg_bill_shock_pct=0.15, bills_count=200, shock_event_count=30)
    # Crisis year (RED)
    mon.record(2022, avg_clarity=0.791, avg_complaint_probability=0.056,
               avg_bill_shock_pct=0.34, bills_count=148, shock_event_count=61)
    # Recovery (AMBER)
    mon.record(2023, avg_clarity=0.808, avg_complaint_probability=0.048,
               avg_bill_shock_pct=0.17, bills_count=144, shock_event_count=42)
    return mon


# 1. Clarity GREEN above threshold
def test_clarity_rag_green():
    snap = ServiceQualitySnapshot(2020, 0.850, 0.040, 0.15, 200, 30)
    assert snap.clarity_rag == ServiceQualityRAG.GREEN


# 2. Clarity RED below threshold
def test_clarity_rag_red():
    snap = ServiceQualitySnapshot(2022, 0.791, 0.040, 0.15, 200, 30)
    assert snap.clarity_rag == ServiceQualityRAG.RED


# 3. Complaint GREEN when below amber threshold
def test_complaint_rag_green():
    snap = ServiceQualitySnapshot(2020, 0.850, 0.040, 0.15, 200, 30)
    assert snap.complaint_rag == ServiceQualityRAG.GREEN


# 4. Complaint RED when at or above red threshold
def test_complaint_rag_red():
    snap = ServiceQualitySnapshot(2022, 0.791, 0.060, 0.15, 200, 30)
    assert snap.complaint_rag == ServiceQualityRAG.RED


# 5. Bill shock GREEN/AMBER/RED bands
def test_bill_shock_rag_bands():
    green = ServiceQualitySnapshot(2020, 0.85, 0.04, 0.10, 200, 20)
    amber = ServiceQualitySnapshot(2021, 0.85, 0.04, 0.25, 200, 50)
    red = ServiceQualitySnapshot(2022, 0.85, 0.04, 0.35, 200, 70)
    assert green.bill_shock_rag == ServiceQualityRAG.GREEN
    assert amber.bill_shock_rag == ServiceQualityRAG.AMBER
    assert red.bill_shock_rag == ServiceQualityRAG.RED


# 6. Overall RAG: any RED dimension = RED overall
def test_overall_rag_red_if_any_red():
    snap = ServiceQualitySnapshot(2022, 0.791, 0.040, 0.15, 200, 30)
    # clarity is RED, so overall is RED
    assert snap.overall_rag == ServiceQualityRAG.RED


# 7. Shock rate pct calculation
def test_shock_rate_pct():
    snap = ServiceQualitySnapshot(2022, 0.80, 0.050, 0.20, 148, 61)
    expected = 61 / 148 * 100
    assert abs(snap.shock_rate_pct - expected) < 0.01


# 8. Shock rate pct zero when no bills
def test_shock_rate_zero_bills():
    snap = ServiceQualitySnapshot(2020, 0.85, 0.04, 0.10, 0, 0)
    assert snap.shock_rate_pct == 0.0


# 9. Red years correctly identified
def test_red_years():
    mon = _mon_with_data()
    red_yrs = [s.year for s in mon.red_years]
    assert 2022 in red_yrs
    assert 2020 not in red_yrs


# 10. Worst clarity year identified
def test_worst_clarity_year():
    mon = _mon_with_data()
    assert mon.worst_clarity_year.year == 2022


# 11. Improving trend detection
def test_is_improving():
    mon = _mon_with_data()
    # 2022 clarity=0.791, 2023 clarity=0.808 — improving
    assert mon.is_improving() is True


# 12. quality_summary contains key fields
def test_quality_summary():
    mon = _mon_with_data()
    summary = mon.quality_summary()
    assert "Years recorded" in summary
    assert "RED years" in summary
    assert "Worst clarity" in summary


# --- Phase LT depth tests ---

def test_year_stored():
    snap = ServiceQualitySnapshot(2023, 0.85, 0.04, 0.15, 100, 15)
    assert snap.year == 2023


def test_avg_clarity_stored():
    snap = ServiceQualitySnapshot(2023, 0.85, 0.04, 0.15, 100, 15)
    assert snap.avg_clarity == pytest.approx(0.85)


def test_bills_count_stored():
    snap = ServiceQualitySnapshot(2023, 0.85, 0.04, 0.15, 200, 30)
    assert snap.bills_count == 200


def test_shock_event_count_stored():
    snap = ServiceQualitySnapshot(2023, 0.85, 0.04, 0.15, 200, 30)
    assert snap.shock_event_count == 30


def test_clarity_amber_constant():
    assert _CLARITY_AMBER == pytest.approx(0.82)


def test_complaint_amber_constant():
    assert _COMPLAINT_AMBER == pytest.approx(0.05)


def test_bill_shock_amber_constant():
    assert _BILL_SHOCK_AMBER == pytest.approx(0.2)


def test_record_returns_snapshot():
    mon = ServiceQualityMonitor()
    result = mon.record(2022, 0.85, 0.04, 0.15, 100, 15)
    assert isinstance(result, ServiceQualitySnapshot)


def test_get_returns_none_unknown():
    mon = ServiceQualityMonitor()
    assert mon.get(2099) is None


def test_shock_rate_pct_computed():
    snap = ServiceQualitySnapshot(2022, 0.85, 0.04, 0.15, 200, 40)
    assert snap.shock_rate_pct == pytest.approx(20.0)
