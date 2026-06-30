"""Tests for CLV Sensitivity Model (Phase DW)."""
import pytest
from company.crm.clv_sensitivity_model import (
    CLVScenario, CLVSensitivityModel,
    _BASE_DISCOUNT_RATE, _BASE_CHURN_RATE, _CAC_TO_CLV_FLOOR,
)


@pytest.fixture
def model():
    return CLVSensitivityModel()


def make_scenario(label="test", margin=200.0, churn=0.18, disc=0.08, tenure=5):
    return CLVScenario(label=label, annual_margin_gbp=margin,
                       churn_rate=churn, discount_rate=disc, tenure_years=tenure)


class TestCLVScenario:
    def test_retention_rate(self):
        s = make_scenario(churn=0.18)
        assert s.retention_rate == pytest.approx(0.82)

    def test_clv_infinite_formula(self):
        # CLV = M * R / (1 + D - R) = 200 * 0.82 / (1 + 0.08 - 0.82) = 164 / 0.26
        s = make_scenario(margin=200.0, churn=0.18, disc=0.08)
        expected = 200.0 * 0.82 / (1 + 0.08 - 0.82)
        assert s.clv_infinite_gbp == pytest.approx(expected)

    def test_clv_finite_lower_than_infinite(self):
        s = make_scenario(margin=200.0, churn=0.18, disc=0.08, tenure=5)
        assert s.clv_finite_gbp < s.clv_infinite_gbp

    def test_lower_churn_higher_clv(self):
        s_high_churn = make_scenario(churn=0.30)
        s_low_churn = make_scenario(churn=0.05)
        assert s_low_churn.clv_infinite_gbp > s_high_churn.clv_infinite_gbp

    def test_higher_margin_higher_clv(self):
        s_low = make_scenario(margin=100.0)
        s_high = make_scenario(margin=300.0)
        assert s_high.clv_infinite_gbp > s_low.clv_infinite_gbp

    def test_max_acquisition_cost(self):
        s = make_scenario(margin=200.0, churn=0.18, disc=0.08)
        expected = s.clv_infinite_gbp / _CAC_TO_CLV_FLOOR
        assert s.max_acquisition_cost_gbp == pytest.approx(expected)

    def test_max_retention_spend_positive(self):
        s = make_scenario(margin=200.0, churn=0.18, disc=0.08)
        assert s.max_retention_spend_gbp > 0

    def test_zero_churn_no_retention_spend(self):
        s = make_scenario(churn=0.0)
        assert s.max_retention_spend_gbp == pytest.approx(0.0)

    def test_clv_finite_zero_churn_higher(self):
        s_normal = make_scenario(churn=0.18, tenure=5)
        s_no_churn = make_scenario(churn=0.0, tenure=5)
        assert s_no_churn.clv_finite_gbp > s_normal.clv_finite_gbp


class TestCLVSensitivityModel:
    def test_base_case(self, model):
        base = model.base_case(annual_margin_gbp=200.0)
        assert base.churn_rate == pytest.approx(_BASE_CHURN_RATE)
        assert base.discount_rate == pytest.approx(_BASE_DISCOUNT_RATE)

    def test_churn_sensitivity(self, model):
        base = model.base_case(200.0)
        scenarios = model.run_churn_sensitivity(base, [0.10, 0.20, 0.30])
        assert len(scenarios) == 3

    def test_margin_sensitivity(self, model):
        base = model.base_case(200.0)
        scenarios = model.run_margin_sensitivity(base, [-50, 0, +50])
        assert len(scenarios) == 3

    def test_highest_clv(self, model):
        model.add_scenario(make_scenario("A", margin=100.0, churn=0.20))
        model.add_scenario(make_scenario("B", margin=400.0, churn=0.05))
        highest = model.highest_clv()
        assert highest is not None
        assert highest.label == "B"

    def test_lowest_clv(self, model):
        model.add_scenario(make_scenario("A", margin=100.0, churn=0.30))
        model.add_scenario(make_scenario("B", margin=400.0, churn=0.05))
        lowest = model.lowest_clv()
        assert lowest is not None
        assert lowest.label == "A"

    def test_scenarios_above_cac_floor(self, model):
        model.add_scenario(make_scenario("A", margin=100.0))  # low CLV
        model.add_scenario(make_scenario("B", margin=1000.0))  # high CLV
        above = model.scenarios_above_cac_floor(cac_gbp=200.0)
        # B has CLV ~= £3,154 → max CAC ~= £1,051 → above 200
        assert len(above) >= 1

    def test_clv_range(self, model):
        model.add_scenario(make_scenario("A", margin=100.0, churn=0.25))
        model.add_scenario(make_scenario("B", margin=500.0, churn=0.05))
        lo, hi = model.clv_range_gbp()
        assert hi > lo

    def test_summary_string(self, model):
        model.base_case(200.0)
        s = model.sensitivity_summary()
        assert "CLV Sensitivity" in s
        assert "18%" in s  # base churn rate

    def test_empty_model_summary(self, model):
        s = model.sensitivity_summary()
        assert "no scenarios" in s

    def test_constants(self):
        assert _BASE_CHURN_RATE == pytest.approx(0.18)
        assert _BASE_DISCOUNT_RATE == pytest.approx(0.08)
        assert _CAC_TO_CLV_FLOOR == pytest.approx(3.0)
