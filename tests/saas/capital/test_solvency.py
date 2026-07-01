"""Tests for Phase 55: per-customer solvency signal (Ofgem MCR compliance)."""

import pytest
from saas.capital.solvency import (
    MCR_FLOOR_GBP_PER_CUSTOMER,
    compute_solvency_signal,
    compute_solvency_by_year,
)


class TestComputeSolvencySignal:
    def test_healthy_returns_ok(self):
        result = compute_solvency_signal(treasury_gbp=1_000_000.0, active_customer_count=100)
        assert result["status"] == "OK"
        assert result["per_customer_net_assets_gbp"] == pytest.approx(10_000.0)

    def test_ratio_computed_correctly(self):
        result = compute_solvency_signal(treasury_gbp=130.0 * 5, active_customer_count=5)
        assert result["solvency_ratio"] == pytest.approx(1.0)
        assert result["status"] == "Watch"  # exactly at floor = Watch (barely compliant)

    def test_below_floor_is_stress(self):
        result = compute_solvency_signal(treasury_gbp=100.0, active_customer_count=5)
        assert result["status"] == "STRESS"
        assert result["solvency_ratio"] < 1.0

    def test_between_floor_and_watch_is_watch(self):
        # per_customer = 200 / 1 = 200; floor = 130; ratio = 1.54 → Watch
        result = compute_solvency_signal(treasury_gbp=200.0, active_customer_count=1)
        assert result["status"] == "Watch"
        assert 1.0 <= result["solvency_ratio"] < 2.0

    def test_above_watch_threshold_is_ok(self):
        result = compute_solvency_signal(treasury_gbp=260.0 * 3, active_customer_count=3)
        assert result["status"] == "OK"
        assert result["solvency_ratio"] == pytest.approx(2.0)

    def test_zero_customers_is_stress(self):
        result = compute_solvency_signal(treasury_gbp=1000.0, active_customer_count=0)
        assert result["status"] == "STRESS"

    def test_negative_treasury_is_stress(self):
        result = compute_solvency_signal(treasury_gbp=-500.0, active_customer_count=10)
        assert result["status"] == "STRESS"
        assert result["solvency_ratio"] < 0

    def test_mcr_floor_returned_in_result(self):
        result = compute_solvency_signal(treasury_gbp=10000.0, active_customer_count=5)
        assert result["mcr_floor_gbp"] == MCR_FLOOR_GBP_PER_CUSTOMER

    def test_custom_mcr_floor(self):
        result = compute_solvency_signal(treasury_gbp=200.0, active_customer_count=1, mcr_floor=200.0)
        assert result["solvency_ratio"] == pytest.approx(1.0)
        assert result["status"] == "Watch"  # exactly at custom floor = Watch


class TestComputeSolvencyByYear:
    def test_returns_all_years(self):
        years_data = {
            "2020": {"treasury_gbp": 50_000.0, "active_customer_ids": ["C1", "C2"]},
            "2021": {"treasury_gbp": 30_000.0, "active_customer_ids": ["C1", "C2", "C3"]},
        }
        result = compute_solvency_by_year(years_data)
        assert "2020" in result
        assert "2021" in result

    def test_uses_active_customer_ids_when_count_missing(self):
        years_data = {
            "2022": {"treasury_gbp": 130.0 * 2, "active_customer_ids": ["C1", "C2"]},
        }
        result = compute_solvency_by_year(years_data)
        # 2 customers, 260 treasury → per_customer = 130 → ratio = 1.0 → Watch (at floor)
        assert result["2022"]["solvency_ratio"] == pytest.approx(1.0)
        assert result["2022"]["status"] == "Watch"

    def test_empty_years_returns_empty(self):
        result = compute_solvency_by_year({})
        assert result == {}



class TestSolvencyConstants:
    def test_mcr_floor_is_130(self):
        assert MCR_FLOOR_GBP_PER_CUSTOMER == 130.0

    def test_compute_solvency_signal_returns_dict(self):
        result = compute_solvency_signal(treasury_gbp=1000.0, active_customer_count=5)
        assert isinstance(result, dict)

    def test_compute_solvency_by_year_returns_dict(self):
        result = compute_solvency_by_year({})
        assert isinstance(result, dict)
