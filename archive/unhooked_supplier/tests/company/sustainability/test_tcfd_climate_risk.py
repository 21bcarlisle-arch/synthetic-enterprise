"""Tests for TCFD Climate Risk Financial Assessment (Phase DX)."""
import pytest
from company.sustainability.tcfd_climate_risk import (
    ClimatScenario, RiskType, RiskHorizon,
    ClimateRiskExposure, TCFDClimateRiskAssessment,
    _CARBON_PRICE_2030_GBP_PER_TCO2, _EXPECTED_GAS_DEMAND_REDUCTION_PCT,
)


@pytest.fixture
def assessment():
    return TCFDClimateRiskAssessment(
        assessment_year=2025,
        annual_gas_revenue_gbp=2_000_000.0,
        annual_gas_procurement_tco2=5_000.0,
        customer_count=100,
        average_annual_margin_gbp=200.0,
    )


def make_exposure(gross=100000.0, mitigation=10000.0, probability=50.0,
                  scenario=ClimatScenario.ORDERLY_1_5C,
                  rtype=RiskType.PHYSICAL_ACUTE):
    return ClimateRiskExposure(
        risk_type=rtype,
        scenario=scenario,
        horizon=RiskHorizon.MEDIUM,
        description="test",
        gross_exposure_gbp=gross,
        mitigation_gbp=mitigation,
        probability_pct=probability,
    )


class TestClimateRiskExposure:
    def test_net_exposure(self):
        e = make_exposure(gross=100_000, mitigation=20_000)
        assert e.net_exposure_gbp == pytest.approx(80_000.0)

    def test_risk_adjusted_exposure(self):
        e = make_exposure(gross=100_000, mitigation=0, probability=50.0)
        assert e.risk_adjusted_exposure_gbp == pytest.approx(50_000.0)

    def test_is_material(self):
        e = make_exposure(gross=100_000, mitigation=0, probability=50.0)
        assert e.is_material

    def test_not_material_small(self):
        e = make_exposure(gross=1_000, mitigation=500, probability=10.0)
        assert not e.is_material

    def test_mitigation_reduces_risk(self):
        e1 = make_exposure(mitigation=0)
        e2 = make_exposure(mitigation=50_000)
        assert e2.risk_adjusted_exposure_gbp < e1.risk_adjusted_exposure_gbp


class TestTCFDClimateRiskAssessment:
    def test_run_scenario_returns_five(self, assessment):
        exps = assessment.run_scenario(ClimatScenario.ORDERLY_1_5C)
        assert len(exps) == 5

    def test_all_risk_types_present(self, assessment):
        assessment.run_scenario(ClimatScenario.ORDERLY_1_5C)
        risk_types = {e.risk_type for e in assessment.exposures()}
        assert RiskType.PHYSICAL_ACUTE in risk_types
        assert RiskType.PHYSICAL_CHRONIC in risk_types
        assert RiskType.TRANSITION_POLICY in risk_types
        assert RiskType.TRANSITION_MARKET in risk_types
        assert RiskType.TRANSITION_TECHNOLOGY in risk_types

    def test_chronic_risk_uses_gas_revenue(self, assessment):
        assessment.run_scenario(ClimatScenario.ORDERLY_1_5C)
        chronic = assessment.exposures(risk_type=RiskType.PHYSICAL_CHRONIC)
        assert len(chronic) == 1
        expected_gross = 2_000_000.0 * _EXPECTED_GAS_DEMAND_REDUCTION_PCT[ClimatScenario.ORDERLY_1_5C] / 100
        assert chronic[0].gross_exposure_gbp == pytest.approx(expected_gross)

    def test_policy_risk_uses_carbon_price(self, assessment):
        assessment.run_scenario(ClimatScenario.ORDERLY_1_5C)
        policy = assessment.exposures(risk_type=RiskType.TRANSITION_POLICY)
        assert len(policy) == 1
        expected = 5_000.0 * _CARBON_PRICE_2030_GBP_PER_TCO2[ClimatScenario.ORDERLY_1_5C]
        assert policy[0].gross_exposure_gbp == pytest.approx(expected)

    def test_filter_by_scenario(self, assessment):
        assessment.run_scenario(ClimatScenario.ORDERLY_1_5C)
        assessment.run_scenario(ClimatScenario.HOT_HOUSE_4C)
        orderly = assessment.exposures(scenario=ClimatScenario.ORDERLY_1_5C)
        assert all(e.scenario == ClimatScenario.ORDERLY_1_5C for e in orderly)

    def test_total_risk_adjusted_positive(self, assessment):
        assessment.run_scenario(ClimatScenario.DISORDERLY_2C)
        total = assessment.total_risk_adjusted_exposure_gbp(ClimatScenario.DISORDERLY_2C)
        assert total > 0

    def test_orderly_lower_physical_than_hot_house(self, assessment):
        assessment.run_scenario(ClimatScenario.ORDERLY_1_5C)
        assessment.run_scenario(ClimatScenario.HOT_HOUSE_4C)
        orderly_chronic = assessment.exposures(
            scenario=ClimatScenario.ORDERLY_1_5C,
            risk_type=RiskType.PHYSICAL_CHRONIC,
        )[0]
        hot_chronic = assessment.exposures(
            scenario=ClimatScenario.HOT_HOUSE_4C,
            risk_type=RiskType.PHYSICAL_CHRONIC,
        )[0]
        # 4C = less gas demand reduction than 1.5C (no orderly transition)
        assert orderly_chronic.gross_exposure_gbp > hot_chronic.gross_exposure_gbp

    def test_worst_scenario(self, assessment):
        for s in ClimatScenario:
            assessment.run_scenario(s)
        worst = assessment.worst_scenario()
        assert worst is not None
        assert isinstance(worst, ClimatScenario)

    def test_material_exposures(self, assessment):
        assessment.run_scenario(ClimatScenario.ORDERLY_1_5C)
        material = assessment.material_exposures()
        assert len(material) >= 1

    def test_tcfd_summary(self, assessment):
        assessment.run_scenario(ClimatScenario.ORDERLY_1_5C)
        s = assessment.tcfd_summary()
        assert "TCFD Climate Risk" in s
        assert "2025" in s

    def test_constants(self):
        assert _CARBON_PRICE_2030_GBP_PER_TCO2[ClimatScenario.ORDERLY_1_5C] == 150.0
        assert _EXPECTED_GAS_DEMAND_REDUCTION_PCT[ClimatScenario.ORDERLY_1_5C] == 35.0
