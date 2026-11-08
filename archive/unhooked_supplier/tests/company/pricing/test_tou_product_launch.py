"""Tests for Phase X: ToU Product Launch Decision Engine.

Covers: LaunchReadinessSignal, ToULaunchThreshold, ToULaunchAssessment,
ToUProductLaunchBook.
"""
from __future__ import annotations

import pytest

from company.pricing.ev_cross_subsidy import CrossSubsidyRegister
from company.pricing.tou_product_launch import (
    LaunchReadinessSignal,
    ToULaunchAssessment,
    ToULaunchThreshold,
    ToUProductLaunchBook,
)
from company.pricing.tou_tariff_assessor import WholesaleBandRates


def _make_register_with_ev_customers(
    n_customers: int,
    cross_subsidy_each: float = 500.0,
    year: int = 2024,
    flat_rate: float = 28.5,
) -> CrossSubsidyRegister:
    """Build a register with n_customers EV accounts each with given cross-subsidy."""
    register = CrossSubsidyRegister()
    rates = WholesaleBandRates.normal()
    for i in range(n_customers):
        register.record(
            account_id=f"EV{i}",
            year=year,
            annual_kwh=8000.0,
            years_with_ev=2,
            flat_rate_p_per_kwh=flat_rate,
            wholesale_band_rates=rates,
        )
    return register


class TestToULaunchThreshold:
    def test_default_for_year_returns_threshold(self):
        t = ToULaunchThreshold.default_for(2024)
        assert t.year == 2024
        assert t.min_ev_penetration_pct > 0
        assert t.max_margin_loss_gbp > 0

    def test_threshold_is_frozen(self):
        t = ToULaunchThreshold.default_for(2022)
        with pytest.raises((AttributeError, TypeError)):
            t.year = 9999


class TestToULaunchAssessment:
    def _make(self, ev_count=5, total=100, cross_subsidy=200.0,
              signal=LaunchReadinessSignal.HOLD) -> ToULaunchAssessment:
        threshold = ToULaunchThreshold.default_for(2024)
        return ToULaunchAssessment(
            year=2024,
            ev_customer_count=ev_count,
            total_customers=total,
            total_cross_subsidy_gbp=cross_subsidy,
            worst_case_margin_delta_gbp=-cross_subsidy,
            signal=signal,
            threshold=threshold,
        )

    def test_ev_penetration_pct_computed(self):
        a = self._make(ev_count=10, total=200)
        assert abs(a.ev_penetration_pct - 5.0) < 0.01

    def test_margin_at_risk_property(self):
        a = self._make(cross_subsidy=750.0)
        assert abs(a.margin_at_risk_gbp - 750.0) < 0.01

    def test_is_launch_viable_true_when_small_risk(self):
        threshold = ToULaunchThreshold(2024, min_ev_penetration_pct=5.0, max_margin_loss_gbp=1000.0)
        a = ToULaunchAssessment(2024, 10, 100, 400.0, -400.0, LaunchReadinessSignal.LAUNCH, threshold)
        assert a.is_launch_viable is True

    def test_is_launch_viable_false_when_large_risk(self):
        threshold = ToULaunchThreshold(2024, min_ev_penetration_pct=5.0, max_margin_loss_gbp=100.0)
        a = ToULaunchAssessment(2024, 10, 100, 750.0, -750.0, LaunchReadinessSignal.HOLD, threshold)
        assert a.is_launch_viable is False

    def test_is_market_ready_true_when_high_ev_pct(self):
        threshold = ToULaunchThreshold(2024, min_ev_penetration_pct=5.0, max_margin_loss_gbp=500.0)
        a = ToULaunchAssessment(2024, 10, 100, 200.0, -200.0, LaunchReadinessSignal.LAUNCH, threshold)
        assert a.is_market_ready is True

    def test_is_market_ready_false_when_low_ev_pct(self):
        threshold = ToULaunchThreshold(2024, min_ev_penetration_pct=20.0, max_margin_loss_gbp=500.0)
        a = ToULaunchAssessment(2024, 5, 1000, 200.0, -200.0, LaunchReadinessSignal.MONITOR, threshold)
        assert a.is_market_ready is False

    def test_zero_total_customers_gives_zero_pct(self):
        a = self._make(ev_count=0, total=0)
        assert a.ev_penetration_pct == 0.0

    def test_assessment_is_frozen(self):
        a = self._make()
        with pytest.raises((AttributeError, TypeError)):
            a.year = 9999


class TestToUProductLaunchBook:
    def test_monitor_when_low_ev_penetration(self):
        book = ToUProductLaunchBook()
        register = _make_register_with_ev_customers(2, year=2020)
        threshold = ToULaunchThreshold(2020, min_ev_penetration_pct=10.0, max_margin_loss_gbp=1000.0)
        assessment = book.assess(register, year=2020, total_customers=500, threshold=threshold)
        assert assessment.signal == LaunchReadinessSignal.MONITOR

    def test_hold_when_high_cross_subsidy(self):
        book = ToUProductLaunchBook()
        register = _make_register_with_ev_customers(20, cross_subsidy_each=500.0, year=2024)
        threshold = ToULaunchThreshold(2024, min_ev_penetration_pct=5.0, max_margin_loss_gbp=100.0)
        assessment = book.assess(register, year=2024, total_customers=200, threshold=threshold)
        assert assessment.signal == LaunchReadinessSignal.HOLD

    def test_launch_when_no_cross_subsidy(self):
        """Empty register = no EV customers = no at-risk cross-subsidy; MONITOR (low penetration)."""
        book = ToUProductLaunchBook()
        register = CrossSubsidyRegister()
        threshold = ToULaunchThreshold(2024, min_ev_penetration_pct=0.0, max_margin_loss_gbp=100.0)
        assessment = book.assess(register, year=2024, total_customers=100, threshold=threshold)
        assert assessment.signal == LaunchReadinessSignal.LAUNCH

    def test_assess_stores_in_history(self):
        book = ToUProductLaunchBook()
        register = _make_register_with_ev_customers(5, year=2024)
        book.assess(register, year=2024, total_customers=100)
        assert len(book.launch_history) == 1

    def test_multiple_years_history(self):
        book = ToUProductLaunchBook()
        for y in [2022, 2023, 2024]:
            register = _make_register_with_ev_customers(y - 2020, year=y)
            book.assess(register, year=y, total_customers=100)
        assert len(book.launch_history) == 3

    def test_ev_penetration_grows_in_history(self):
        book = ToUProductLaunchBook()
        for y, n in [(2022, 2), (2023, 4), (2024, 8)]:
            register = _make_register_with_ev_customers(n, year=y)
            book.assess(register, year=y, total_customers=100)
        pcts = [h.ev_penetration_pct for h in sorted(book.launch_history, key=lambda h: h.year)]
        assert pcts[0] < pcts[1] < pcts[2]

    def test_readiness_trend_improving(self):
        book = ToUProductLaunchBook()
        for y, n in [(2022, 1), (2023, 5)]:
            register = _make_register_with_ev_customers(n, year=y)
            book.assess(register, year=y, total_customers=100)
        assert book.readiness_trend() == "improving"

    def test_readiness_trend_stable(self):
        book = ToUProductLaunchBook()
        for y in [2022, 2023]:
            register = _make_register_with_ev_customers(3, year=y)
            book.assess(register, year=y, total_customers=100)
        assert book.readiness_trend() == "stable"

    def test_readiness_trend_insufficient_data(self):
        book = ToUProductLaunchBook()
        assert book.readiness_trend() == "insufficient_data"

    def test_years_until_viable_returns_none_when_not_growing(self):
        book = ToUProductLaunchBook()
        for y in [2022, 2023]:
            register = _make_register_with_ev_customers(1, year=y)
            book.assess(register, year=y, total_customers=1000)
        assert book.years_until_viable(2023) is None

    def test_years_until_viable_returns_zero_when_already_viable(self):
        book = ToUProductLaunchBook()
        for y, n in [(2022, 5), (2023, 10)]:
            register = _make_register_with_ev_customers(n, year=y)
            threshold = ToULaunchThreshold(y, min_ev_penetration_pct=5.0, max_margin_loss_gbp=50000.0)
            book.assess(register, year=y, total_customers=100, threshold=threshold)
        assert book.years_until_viable(2023) == 0

    def test_launch_summary_keys(self):
        book = ToUProductLaunchBook()
        register = _make_register_with_ev_customers(3, year=2024)
        book.assess(register, year=2024, total_customers=100)
        s = book.launch_summary()
        assert "years_assessed" in s
        assert "signals" in s
        assert "latest_signal" in s
        assert "latest_ev_penetration_pct" in s
        assert "latest_margin_at_risk_gbp" in s

    def test_empty_book_summary(self):
        book = ToUProductLaunchBook()
        s = book.launch_summary()
        assert s["years_assessed"] == 0

    def test_crisis_year_high_cross_subsidy_gives_hold(self):
        book = ToUProductLaunchBook()
        register = _make_register_with_ev_customers(
            15, cross_subsidy_each=500.0, year=2022,
            flat_rate=85.0,
        )
        threshold = ToULaunchThreshold(2022, min_ev_penetration_pct=5.0, max_margin_loss_gbp=200.0)
        assessment = book.assess(register, year=2022, total_customers=100, threshold=threshold)
        assert assessment.signal == LaunchReadinessSignal.HOLD
        assert assessment.total_cross_subsidy_gbp > 200.0
