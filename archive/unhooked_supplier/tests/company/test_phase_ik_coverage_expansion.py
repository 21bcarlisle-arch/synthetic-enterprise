# ARCHIVED LEGS of tests/company/test_phase_ik_coverage_expansion.py (archive increment 4). The tests here reach a module
# under archive/unhooked_supplier/; the live legs stay at tests/company/test_phase_ik_coverage_expansion.py.
import datetime as dt
import pytest
from unittest.mock import patch
from company.crm.lifecycle_tracker import (
    CustomerLifecycleTracker, LifecycleStage
)
from company.pricing.margin_feedback import (
    compute_margin_surcharge, FEEDBACK_LOSS_THRESHOLD, FEEDBACK_MAX_SURCHARGE
)
from company.billing.consumption_forecast import forecast_annual_cost


class TestConsumptionForecast:
    def test_returns_none_when_no_history(self, tmp_path):
        # Non-existent DB path → calibrate_eac returns None → forecast returns None
        result = forecast_annual_cost("NOEXIST", 25.0, 30.0, db_path=tmp_path / "empty.db")
        assert result is None

    def test_returns_dict_when_eac_available(self):
        with patch("company.billing.consumption_forecast.calibrate_eac", return_value=2000.0):
            result = forecast_annual_cost("C1", 25.0, 30.0)
        assert result is not None
        assert result["eac_kwh"] == pytest.approx(2000.0)

    def test_annual_commodity_gbp(self):
        with patch("company.billing.consumption_forecast.calibrate_eac", return_value=2000.0):
            result = forecast_annual_cost("C1", 25.0, 30.0)
        assert result["annual_commodity_gbp"] == pytest.approx(500.0)

    def test_annual_sc_gbp(self):
        with patch("company.billing.consumption_forecast.calibrate_eac", return_value=2000.0):
            result = forecast_annual_cost("C1", 25.0, 30.0)
        assert result["annual_sc_gbp"] == pytest.approx(30 * 365 / 100)

    def test_annual_total_is_sum(self):
        with patch("company.billing.consumption_forecast.calibrate_eac", return_value=2000.0):
            r = forecast_annual_cost("C1", 25.0, 30.0)
        assert r["annual_total_gbp"] == pytest.approx(
            r["annual_commodity_gbp"] + r["annual_sc_gbp"], abs=0.02
        )

    def test_quarterly_list_has_4_elements(self):
        with patch("company.billing.consumption_forecast.calibrate_eac", return_value=2000.0):
            r = forecast_annual_cost("C1", 25.0, 30.0)
        assert len(r["quarterly_total_gbp"]) == 4

    def test_monthly_list_has_12_elements(self):
        with patch("company.billing.consumption_forecast.calibrate_eac", return_value=2000.0):
            r = forecast_annual_cost("C1", 25.0, 30.0)
        assert len(r["monthly_total_gbp"]) == 12

    def test_q1_q4_larger_than_q3(self):
        # UK winter heating: Q1 and Q4 (30%) > Q3 (18%)
        with patch("company.billing.consumption_forecast.calibrate_eac", return_value=2000.0):
            r = forecast_annual_cost("C1", 25.0, 30.0)
        assert r["quarterly_total_gbp"][0] > r["quarterly_total_gbp"][2]
        assert r["quarterly_total_gbp"][3] > r["quarterly_total_gbp"][2]

    def test_result_has_unit_rate_and_sc_keys(self):
        with patch("company.billing.consumption_forecast.calibrate_eac", return_value=1500.0):
            r = forecast_annual_cost("C1", 28.0, 35.0)
        assert "unit_rate_p_per_kwh" in r and "standing_charge_p_per_day" in r

    def test_higher_unit_rate_increases_commodity(self):
        with patch("company.billing.consumption_forecast.calibrate_eac", return_value=2000.0):
            r_low = forecast_annual_cost("C1", 20.0, 30.0)
            r_high = forecast_annual_cost("C1", 30.0, 30.0)
        assert r_high["annual_commodity_gbp"] > r_low["annual_commodity_gbp"]

