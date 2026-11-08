"""Tests for Ofgem Supplier Performance Scorecard (Phase EF)."""
import datetime as dt
import pytest
from company.regulatory.ofgem_scorecard import (
    MetricRAG, ScoreMetric, MetricResult,
    SupplierPerformanceScorecard, OfgemScorecardBuilder,
    _classify_metric, _RED_TRIGGER_COUNT,
)


DATE = dt.date(2024, 4, 1)


def build_scorecard(complaints=350, resolution=88, billing=98, wait=90, debt=2.5, satisfaction=82, smart=85):
    b = OfgemScorecardBuilder("TestEnergy", customer_count=10000)
    b.record(ScoreMetric.COMPLAINTS_PER_100K, complaints)
    b.record(ScoreMetric.COMPLAINT_RESOLUTION_8W_PCT, resolution)
    b.record(ScoreMetric.BILLING_ACCURACY_PCT, billing)
    b.record(ScoreMetric.SWITCHING_SATISFACTION_PCT, satisfaction)
    b.record(ScoreMetric.DEBT_AS_PCT_REVENUE, debt)
    b.record(ScoreMetric.CALL_WAIT_SECONDS, wait)
    b.record(ScoreMetric.SMART_METER_INSTALLATION_PCT, smart)
    return b.build("Q1 2024", DATE)


class TestMetricClassification:
    def test_complaints_green(self):
        assert _classify_metric(ScoreMetric.COMPLAINTS_PER_100K, 300.0) == MetricRAG.GREEN

    def test_complaints_amber(self):
        assert _classify_metric(ScoreMetric.COMPLAINTS_PER_100K, 500.0) == MetricRAG.AMBER

    def test_complaints_red(self):
        assert _classify_metric(ScoreMetric.COMPLAINTS_PER_100K, 800.0) == MetricRAG.RED

    def test_resolution_green(self):
        assert _classify_metric(ScoreMetric.COMPLAINT_RESOLUTION_8W_PCT, 90.0) == MetricRAG.GREEN

    def test_resolution_red(self):
        assert _classify_metric(ScoreMetric.COMPLAINT_RESOLUTION_8W_PCT, 60.0) == MetricRAG.RED

    def test_billing_green(self):
        assert _classify_metric(ScoreMetric.BILLING_ACCURACY_PCT, 98.5) == MetricRAG.GREEN

    def test_debt_red(self):
        assert _classify_metric(ScoreMetric.DEBT_AS_PCT_REVENUE, 8.0) == MetricRAG.RED


class TestSupplierPerformanceScorecard:
    def test_all_green_scorecard(self):
        sc = build_scorecard()
        assert sc.red_count == 0
        assert sc.overall_rag == MetricRAG.GREEN

    def test_red_triggers_enhanced_monitoring(self):
        sc = build_scorecard(
            complaints=800,   # RED
            resolution=60,    # RED
            billing=92,       # RED
        )
        assert sc.red_count >= _RED_TRIGGER_COUNT
        assert sc.is_enhanced_monitoring_triggered

    def test_one_red_overall_amber(self):
        sc = build_scorecard(complaints=800)  # one RED
        assert sc.overall_rag == MetricRAG.AMBER or sc.overall_rag == MetricRAG.RED

    def test_get_metric(self):
        sc = build_scorecard(complaints=350)
        result = sc.get_metric(ScoreMetric.COMPLAINTS_PER_100K)
        assert result is not None
        assert result.value == pytest.approx(350.0)
        assert result.rag == MetricRAG.GREEN

    def test_get_missing_metric(self):
        b = OfgemScorecardBuilder("X", 1000)
        b.record(ScoreMetric.COMPLAINTS_PER_100K, 300.0)
        sc = b.build("Q1", DATE)
        assert sc.get_metric(ScoreMetric.BILLING_ACCURACY_PCT) is None

    def test_amber_count(self):
        sc = build_scorecard(complaints=500, resolution=75)  # amber values
        assert sc.amber_count >= 1

    def test_supplier_name(self):
        sc = build_scorecard()
        assert sc.supplier_name == "TestEnergy"

    def test_quarter(self):
        sc = build_scorecard()
        assert sc.quarter == "Q1 2024"

    def test_constants(self):
        assert _RED_TRIGGER_COUNT == 3
