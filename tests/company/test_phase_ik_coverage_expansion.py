"""Phase IK: deeper coverage for lifecycle_tracker, margin_feedback, consumption_forecast."""
import datetime as dt
import pytest
from unittest.mock import patch

# ===== lifecycle_tracker =====
from company.crm.lifecycle_tracker import (
    CustomerLifecycleTracker, LifecycleStage
)


def _tracker():
    t = CustomerLifecycleTracker()
    t.register("C1", dt.date(2021,3,1), LifecycleStage.ACTIVE)
    t.register("C2", dt.date(2022,1,15), LifecycleStage.PENDING_SWITCH)
    t.register("C3", dt.date(2020,6,1), LifecycleStage.IN_ARREARS)
    return t


class TestLifecycleTracker:
    def test_register_sets_initial_stage(self):
        t = _tracker()
        assert t.get("C1").stage == LifecycleStage.ACTIVE

    def test_is_on_supply_pending_switch(self):
        t = _tracker()
        assert t.get("C2").is_on_supply

    def test_is_not_on_supply_churned(self):
        t = _tracker()
        t.transition("C1", LifecycleStage.CHURNED, dt.date(2022,12,31))
        assert not t.get("C1").is_on_supply

    def test_is_active_customer_excludes_pending(self):
        t = _tracker()
        # PENDING_SWITCH is on supply but not is_active_customer
        assert not t.get("C2").is_active_customer

    def test_is_active_customer_in_arrears(self):
        t = _tracker()
        assert t.get("C3").is_active_customer

    def test_transition_changes_stage(self):
        t = _tracker()
        t.transition("C1", LifecycleStage.AT_RISK, dt.date(2022,6,1))
        assert t.get("C1").stage == LifecycleStage.AT_RISK

    def test_tenure_days(self):
        t = _tracker()
        days = t.get("C1").tenure_days(dt.date(2022,3,1))
        assert days == 365

    def test_customers_in_stage(self):
        t = _tracker()
        in_active = t.customers_in_stage(LifecycleStage.ACTIVE)
        assert "C1" in in_active and "C2" not in in_active

    def test_active_customers_count(self):
        t = _tracker()
        # C1=ACTIVE, C2=PENDING_SWITCH (not active_customer), C3=IN_ARREARS(active)
        assert len(t.active_customers()) == 2

    def test_portfolio_summary_keys(self):
        t = _tracker()
        s = t.portfolio_summary(dt.date(2023,1,1))
        assert "on_supply" in s and "by_stage" in s and "total" in s

    def test_stage_history_recorded(self):
        t = _tracker()
        t.transition("C1", LifecycleStage.AT_RISK, dt.date(2022,6,1), "high usage")
        t.transition("C1", LifecycleStage.CHURNED, dt.date(2022,12,31), "tariff lapse")
        history = t.get("C1").stage_history()
        assert len(history) == 2
        assert history[-1].to_stage == LifecycleStage.CHURNED


# ===== margin_feedback =====
from company.pricing.margin_feedback import (
    compute_margin_surcharge, FEEDBACK_LOSS_THRESHOLD, FEEDBACK_MAX_SURCHARGE
)


class TestMarginFeedback:
    def test_no_surcharge_when_profitable(self):
        assert compute_margin_surcharge(500.0, 2000.0) == pytest.approx(0.0)

    def test_no_surcharge_below_threshold(self):
        # 4% loss — below 5% threshold
        surcharge = compute_margin_surcharge(-80.0, 2000.0)  # 4%
        assert surcharge == pytest.approx(0.0)

    def test_no_surcharge_at_exact_threshold(self):
        # exactly 5% loss — at threshold, no surcharge
        surcharge = compute_margin_surcharge(-100.0, 2000.0)
        assert surcharge == pytest.approx(0.0)

    def test_surcharge_above_threshold(self):
        # 15% loss → 15% - 5% = 10%
        surcharge = compute_margin_surcharge(-300.0, 2000.0)
        assert surcharge == pytest.approx(0.10)

    def test_surcharge_capped_at_max(self):
        # 40% loss → capped at 20%
        surcharge = compute_margin_surcharge(-800.0, 2000.0)
        assert surcharge == pytest.approx(FEEDBACK_MAX_SURCHARGE)

    def test_zero_revenue_returns_zero(self):
        assert compute_margin_surcharge(-500.0, 0.0) == pytest.approx(0.0)

    def test_surcharge_is_additive_fraction(self):
        # At 25% loss: 25%-5%=20% (capped) → applying to base rate increases it 20%
        base = 25.0
        surcharge = compute_margin_surcharge(-500.0, 2000.0)
        new_rate = base * (1 + surcharge)
        assert new_rate == pytest.approx(base * 1.20)

    def test_surcharge_loss_fraction_minus_threshold(self):
        # 12% loss → 12-5 = 7%
        surcharge = compute_margin_surcharge(-240.0, 2000.0)
        assert surcharge == pytest.approx(0.07)

    def test_small_positive_margin_no_surcharge(self):
        # 2% margin → still profitable, no surcharge
        assert compute_margin_surcharge(40.0, 2000.0) == pytest.approx(0.0)


# ===== consumption_forecast =====
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
