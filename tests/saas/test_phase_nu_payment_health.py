"""Tests for saas/reporting/payment_health.py -- Phase NU."""

import pytest
from saas.reporting.payment_health import (
    PaymentHealthSummary,
    build_payment_health_series,
    _trend,
    _rag,
    _HIGH_CHURN_RISK_THRESHOLD,
    _BAD_DEBT_RATE_AMBER,
    _BAD_DEBT_RATE_RED,
    _AT_RISK_PCT_RED,
    _AT_RISK_PCT_AMBER,
)


def _year(bad_debt=5000, revenue=1_000_000, churn_risk=None):
    return {
        "bad_debt_gbp": bad_debt,
        "revenue_gbp": revenue,
        "churn_risk_by_account": churn_risk or {},
    }


def _run(*year_dicts):
    keys = [str(2020 + i) for i in range(len(year_dicts))]
    return {"years": dict(zip(keys, year_dicts))}


class TestTrend:
    def test_deteriorating_when_rate_rises_above_factor(self):
        result = _trend(0.020, 0.010)   # 2x rise > 1.2x threshold
        assert result == "DETERIORATING"

    def test_improving_when_rate_falls_below_factor(self):
        result = _trend(0.005, 0.010)   # halved < 0.8x threshold
        assert result == "IMPROVING"

    def test_stable_within_band(self):
        result = _trend(0.011, 0.010)   # 10% rise < 20% threshold
        assert result == "STABLE"

    def test_stable_with_no_prior(self):
        assert _trend(0.010, None) == "STABLE"

    def test_stable_with_zero_prior(self):
        assert _trend(0.010, 0.0) == "STABLE"


class TestRag:
    def test_green_low_rate_low_at_risk(self):
        assert _rag(0.005, 20.0) == "GREEN"

    def test_amber_on_bad_debt_rate(self):
        assert _rag(_BAD_DEBT_RATE_AMBER + 0.001, 20.0) == "AMBER"

    def test_red_on_bad_debt_rate(self):
        assert _rag(_BAD_DEBT_RATE_RED + 0.001, 20.0) == "RED"

    def test_amber_on_at_risk_pct(self):
        assert _rag(0.005, _AT_RISK_PCT_AMBER + 1) == "AMBER"

    def test_red_on_at_risk_pct(self):
        assert _rag(0.005, _AT_RISK_PCT_RED + 1) == "RED"


class TestBuildSeries:
    def test_bad_debt_rate_computed(self):
        run = _run(_year(bad_debt=10_000, revenue=1_000_000))
        s = build_payment_health_series(run)
        assert s[0].bad_debt_rate == pytest.approx(0.01)

    def test_at_risk_count_correct(self):
        crba = {"C1": 0.40, "C2": 0.20, "C3": 0.35}   # C1 and C3 above threshold
        run = _run(_year(churn_risk=crba))
        s = build_payment_health_series(run)
        assert s[0].at_risk_customer_count == 2
        assert s[0].total_customer_count == 3

    def test_at_risk_pct_computed(self):
        crba = {"C1": 0.40, "C2": 0.20}
        run = _run(_year(churn_risk=crba))
        s = build_payment_health_series(run)
        assert s[0].at_risk_pct == pytest.approx(50.0)

    def test_trend_first_year_stable(self):
        run = _run(_year(bad_debt=10_000, revenue=1_000_000))
        s = build_payment_health_series(run)
        assert s[0].trend == "STABLE"

    def test_trend_deteriorating_across_years(self):
        run = _run(
            _year(bad_debt=5_000, revenue=1_000_000),   # rate 0.5%
            _year(bad_debt=20_000, revenue=1_000_000),  # rate 2.0% > 0.5% * 1.2
        )
        s = build_payment_health_series(run)
        assert s[1].trend == "DETERIORATING"

    def test_empty_churn_risk_zero_at_risk(self):
        run = _run(_year(churn_risk={}))
        s = build_payment_health_series(run)
        assert s[0].at_risk_customer_count == 0
        assert s[0].at_risk_pct == 0.0

    def test_zero_revenue_no_crash(self):
        run = _run(_year(bad_debt=100, revenue=0))
        s = build_payment_health_series(run)
        assert s[0].bad_debt_rate == 0.0

    def test_series_length_matches_years(self):
        run = _run(_year(), _year(), _year())
        s = build_payment_health_series(run)
        assert len(s) == 3

    def test_empty_years_returns_empty(self):
        assert build_payment_health_series({}) == []

    def test_year_field_correct(self):
        run = _run(_year())
        s = build_payment_health_series(run)
        assert s[0].year == 2020
