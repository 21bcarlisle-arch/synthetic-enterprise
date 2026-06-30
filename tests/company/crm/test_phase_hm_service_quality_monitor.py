"""Tests for Phase HM: Service Quality Monitor."""
import pytest
from company.crm.service_quality_monitor import (
    ServiceQualityMonitor,
    ServiceQualityRAG,
    ServiceQualitySnapshot,
    _BILL_SHOCK_AMBER,
    _BILL_SHOCK_RED,
    _CLARITY_AMBER,
    _CLARITY_RED,
    _COMPLAINT_AMBER,
    _COMPLAINT_RED,
)


def _snap(year, clarity=0.90, complaint=0.02, shock=0.10, bills=100, shock_n=10):
    mon = ServiceQualityMonitor()
    return mon.record(year, clarity, complaint, shock, bills, shock_n)


class TestServiceQualitySnapshot:
    def test_clarity_rag_green(self):
        s = _snap(2024, clarity=0.90)
        assert s.clarity_rag == ServiceQualityRAG.GREEN

    def test_clarity_rag_amber(self):
        s = _snap(2024, clarity=_CLARITY_RED + 0.005)
        assert s.clarity_rag == ServiceQualityRAG.AMBER

    def test_clarity_rag_red(self):
        s = _snap(2024, clarity=0.75)
        assert s.clarity_rag == ServiceQualityRAG.RED

    def test_complaint_rag_green(self):
        s = _snap(2024, complaint=0.01)
        assert s.complaint_rag == ServiceQualityRAG.GREEN

    def test_complaint_rag_amber(self):
        s = _snap(2024, complaint=_COMPLAINT_AMBER + 0.005)
        assert s.complaint_rag == ServiceQualityRAG.AMBER

    def test_complaint_rag_red(self):
        s = _snap(2024, complaint=0.10)
        assert s.complaint_rag == ServiceQualityRAG.RED

    def test_bill_shock_rag_green(self):
        s = _snap(2024, shock=0.05)
        assert s.bill_shock_rag == ServiceQualityRAG.GREEN

    def test_bill_shock_rag_amber(self):
        s = _snap(2024, shock=_BILL_SHOCK_AMBER + 0.01)
        assert s.bill_shock_rag == ServiceQualityRAG.AMBER

    def test_bill_shock_rag_red(self):
        s = _snap(2024, shock=_BILL_SHOCK_RED + 0.05)
        assert s.bill_shock_rag == ServiceQualityRAG.RED

    def test_overall_rag_green(self):
        s = _snap(2024, clarity=0.90, complaint=0.01, shock=0.05)
        assert s.overall_rag == ServiceQualityRAG.GREEN

    def test_overall_rag_red_from_one_red(self):
        s = _snap(2024, clarity=0.70, complaint=0.01, shock=0.05)
        assert s.overall_rag == ServiceQualityRAG.RED

    def test_overall_rag_amber_when_no_red(self):
        s = _snap(2024, clarity=_CLARITY_RED + 0.005, complaint=0.01, shock=0.05)
        assert s.overall_rag == ServiceQualityRAG.AMBER

    def test_shock_rate_pct(self):
        s = _snap(2024, bills=200, shock_n=10)
        assert s.shock_rate_pct == pytest.approx(5.0)

    def test_shock_rate_pct_zero_bills(self):
        s = _snap(2024, bills=0, shock_n=0)
        assert s.shock_rate_pct == 0.0


class TestServiceQualityMonitor:
    def _build(self):
        mon = ServiceQualityMonitor()
        mon.record(2022, 0.78, 0.08, 0.35, 300, 105)
        mon.record(2023, 0.82, 0.04, 0.15, 350, 52)
        mon.record(2024, 0.88, 0.02, 0.10, 400, 40)
        return mon

    def test_record_returns_snapshot(self):
        mon = ServiceQualityMonitor()
        s = mon.record(2024, 0.90, 0.02, 0.10, 100, 10)
        assert isinstance(s, ServiceQualitySnapshot)
        assert s.year == 2024

    def test_get_existing_year(self):
        mon = self._build()
        s = mon.get(2023)
        assert s is not None
        assert s.year == 2023

    def test_get_missing_year_none(self):
        mon = self._build()
        assert mon.get(2099) is None

    def test_all_snapshots_sorted(self):
        mon = self._build()
        snaps = mon.all_snapshots
        assert [s.year for s in snaps] == [2022, 2023, 2024]

    def test_red_years(self):
        mon = self._build()
        reds = mon.red_years
        assert any(s.year == 2022 for s in reds)

    def test_amber_years(self):
        mon = self._build()
        ambers = mon.amber_years
        assert 2022 not in [s.year for s in ambers]

    def test_worst_clarity_year(self):
        mon = self._build()
        assert mon.worst_clarity_year.year == 2022

    def test_worst_clarity_year_empty(self):
        mon = ServiceQualityMonitor()
        assert mon.worst_clarity_year is None

    def test_worst_complaint_year(self):
        mon = self._build()
        assert mon.worst_complaint_year.year == 2022

    def test_worst_bill_shock_year(self):
        mon = self._build()
        assert mon.worst_bill_shock_year.year == 2022

    def test_is_improving_true(self):
        mon = self._build()
        assert mon.is_improving() is True

    def test_is_improving_false(self):
        mon = ServiceQualityMonitor()
        mon.record(2023, 0.90, 0.02, 0.10, 100, 10)
        mon.record(2024, 0.85, 0.02, 0.10, 100, 10)
        assert mon.is_improving() is False

    def test_is_improving_single_year(self):
        mon = ServiceQualityMonitor()
        mon.record(2024, 0.90, 0.02, 0.10, 100, 10)
        assert mon.is_improving() is False

    def test_quality_summary_not_empty(self):
        mon = self._build()
        s = mon.quality_summary()
        assert "Service Quality" in s
        assert "RED" in s

    def test_quality_summary_empty_monitor(self):
        mon = ServiceQualityMonitor()
        s = mon.quality_summary()
        assert "No service quality" in s

    def test_overwrite_year_with_new_record(self):
        mon = ServiceQualityMonitor()
        mon.record(2024, 0.80, 0.05, 0.20, 100, 20)
        mon.record(2024, 0.90, 0.02, 0.10, 200, 20)
        assert mon.get(2024).avg_clarity == pytest.approx(0.90)
        assert len(mon.all_snapshots) == 1

