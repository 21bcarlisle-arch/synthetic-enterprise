"""Tests for SEGExportEstimator — Phase R."""
import pytest
from company.regulatory.seg_book import SEGBook
from company.regulatory.seg_export_estimator import (
    SEGExportEstimator,
    AnnualExportEstimate,
    ANNUAL_YIELD_KWH_PER_KWP,
    SELF_CONSUMPTION_STANDARD,
    SELF_CONSUMPTION_WITH_BATTERY,
    SEG_START_YEAR,
)


def _estimator():
    return SEGExportEstimator(SEGBook())


class TestYieldAndFractions:
    def test_annual_yield_scales_with_capacity(self):
        est = _estimator()
        assert est.annual_yield_kwh(3.8) == pytest.approx(3.8 * ANNUAL_YIELD_KWH_PER_KWP)

    def test_zero_capacity_zero_yield(self):
        est = _estimator()
        assert est.annual_yield_kwh(0.0) == pytest.approx(0.0)

    def test_standard_self_consumption(self):
        est = _estimator()
        assert est.self_consumption_fraction(has_battery=False) == pytest.approx(SELF_CONSUMPTION_STANDARD)

    def test_battery_self_consumption_higher(self):
        est = _estimator()
        assert est.self_consumption_fraction(has_battery=True) > est.self_consumption_fraction(has_battery=False)

    def test_battery_self_consumption_value(self):
        est = _estimator()
        assert est.self_consumption_fraction(has_battery=True) == pytest.approx(SELF_CONSUMPTION_WITH_BATTERY)

    def test_export_fraction_complement(self):
        est = _estimator()
        assert est.export_fraction(has_battery=False) == pytest.approx(1.0 - SELF_CONSUMPTION_STANDARD)
        assert est.export_fraction(has_battery=True) == pytest.approx(1.0 - SELF_CONSUMPTION_WITH_BATTERY)


class TestEstimateAnnualExport:
    def test_standard_export(self):
        est = _estimator()
        result = est.estimate_annual_export_kwh(3.8, has_battery=False)
        expected = 3.8 * ANNUAL_YIELD_KWH_PER_KWP * (1.0 - SELF_CONSUMPTION_STANDARD)
        assert result == pytest.approx(expected)

    def test_battery_export_lower(self):
        est = _estimator()
        no_batt = est.estimate_annual_export_kwh(3.8, has_battery=False)
        with_batt = est.estimate_annual_export_kwh(3.8, has_battery=True)
        assert with_batt < no_batt

    def test_zero_capacity_zero_export(self):
        est = _estimator()
        assert est.estimate_annual_export_kwh(0.0) == pytest.approx(0.0)


class TestEstimateAndRecord:
    def test_pre_seg_year_raises(self):
        est = _estimator()
        with pytest.raises(ValueError, match="FIT"):
            est.estimate_and_record("C1", 3.8, year=2019)

    def test_returns_annual_export_estimate(self):
        est = _estimator()
        result = est.estimate_and_record("C1", 3.8, year=2022)
        assert isinstance(result, AnnualExportEstimate)
        assert result.customer_id == "C1"
        assert result.year == 2022

    def test_generation_plus_consumed_plus_exported(self):
        est = _estimator()
        r = est.estimate_and_record("C1", 3.8, year=2022)
        assert r.self_consumed_kwh + r.exported_kwh == pytest.approx(r.generation_kwh, abs=0.01)

    def test_seg_rate_from_book(self):
        book = SEGBook()
        est = SEGExportEstimator(book)
        r = est.estimate_and_record("C1", 3.8, year=2022)
        assert r.seg_rate_p_per_kwh == pytest.approx(book.seg_rate_for_year(2022))

    def test_payment_recorded_in_seg_book(self):
        book = SEGBook()
        est = SEGExportEstimator(book)
        est.estimate_and_record("C1", 3.8, year=2022)
        assert book.total_export_kwh(2022) > 0.0

    def test_2022_crisis_rate_inflates_payment(self):
        book = SEGBook()
        est = SEGExportEstimator(book)
        r2020 = est.estimate_and_record("C1", 3.8, year=2020)
        r2022 = est.estimate_and_record("C1", 3.8, year=2022)
        # 2022 SEG rate (7.5p) > 2020 rate (4.0p) → higher payment for same export
        assert r2022.seg_payment_gbp > r2020.seg_payment_gbp

    def test_battery_customer_exports_less(self):
        book = SEGBook()
        est = SEGExportEstimator(book)
        r_no_batt = est.estimate_and_record("C1", 3.8, year=2023, has_battery=False)
        r_batt = est.estimate_and_record("C2", 3.8, year=2023, has_battery=True)
        assert r_batt.exported_kwh < r_no_batt.exported_kwh

    def test_seg_start_year_is_valid(self):
        est = _estimator()
        r = est.estimate_and_record("C1", 3.8, year=SEG_START_YEAR)
        assert r.exported_kwh > 0.0


class TestPortfolioSummary:
    def test_empty_portfolio(self):
        est = _estimator()
        s = est.portfolio_summary([])
        assert s["customer_count"] == 0
        assert s["total_export_kwh"] == 0.0

    def test_multiple_customers_aggregated(self):
        book = SEGBook()
        est = SEGExportEstimator(book)
        r1 = est.estimate_and_record("C1", 3.8, year=2022)
        r2 = est.estimate_and_record("C2", 2.5, year=2022)
        s = est.portfolio_summary([r1, r2])
        assert s["customer_count"] == 2
        assert s["total_export_kwh"] == pytest.approx(r1.exported_kwh + r2.exported_kwh)

    def test_seg_cost_matches_book(self):
        book = SEGBook()
        est = SEGExportEstimator(book)
        r1 = est.estimate_and_record("C1", 3.8, year=2022)
        r2 = est.estimate_and_record("C2", 2.5, year=2022)
        s = est.portfolio_summary([r1, r2])
        assert s["total_seg_cost_gbp"] == pytest.approx(book.total_paid_gbp(2022), rel=1e-4)

    def test_unique_customer_count(self):
        book = SEGBook()
        est = SEGExportEstimator(book)
        r1 = est.estimate_and_record("C1", 3.8, year=2022)
        r2 = est.estimate_and_record("C1", 3.8, year=2023)  # same customer, different year
        s = est.portfolio_summary([r1, r2])
        assert s["customer_count"] == 1
