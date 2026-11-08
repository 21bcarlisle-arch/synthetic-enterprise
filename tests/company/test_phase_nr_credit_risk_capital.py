"""Tests for Phase NR: Bad Debt -> Capital Stress Feedback."""
import pytest
from company.risk.credit_risk_stress import (
    CreditRiskStress, build_credit_risk_stress,
    CRISIS_BAD_DEBT_MULTIPLIER, MATERIAL_THRESHOLD_PCT,
)




class TestCreditRiskStress:
    def test_crisis_multiplier_constant(self):
        assert CRISIS_BAD_DEBT_MULTIPLIER == pytest.approx(2.5)

    def test_material_threshold_constant(self):
        assert MATERIAL_THRESHOLD_PCT == pytest.approx(0.5)

    def test_stressed_provision(self):
        crs = build_credit_risk_stress(100_000.0, 5_000_000.0)
        assert crs.stressed_provision_gbp == pytest.approx(250_000.0)

    def test_stress_incremental(self):
        crs = build_credit_risk_stress(100_000.0, 5_000_000.0)
        # stressed = 250k, current = 100k, incremental = 150k
        assert crs.stress_incremental_gbp == pytest.approx(150_000.0)

    def test_stress_incremental_zero_with_multiplier_one(self):
        crs = build_credit_risk_stress(100_000.0, 5_000_000.0, stress_multiplier=1.0)
        assert crs.stress_incremental_gbp == pytest.approx(0.0)

    def test_is_material_true(self):
        # incremental 150k on 5M revenue = 3% > 0.5% threshold
        crs = build_credit_risk_stress(100_000.0, 5_000_000.0)
        assert crs.is_material is True

    def test_is_material_false(self):
        # incremental 150 on 5M revenue = 0.003% < 0.5%
        crs = build_credit_risk_stress(100.0, 5_000_000.0)
        assert crs.is_material is False

    def test_is_material_zero_revenue(self):
        crs = build_credit_risk_stress(100_000.0, 0.0)
        assert crs.is_material is False

    def test_summary_keys(self):
        crs = build_credit_risk_stress(50_000.0, 2_000_000.0)
        s = crs.summary()
        assert "current_provision_gbp" in s
        assert "stress_incremental_gbp" in s
        assert "is_material" in s

    def test_custom_multiplier(self):
        crs = build_credit_risk_stress(100_000.0, 5_000_000.0, stress_multiplier=3.0)
        assert crs.stressed_provision_gbp == pytest.approx(300_000.0)
        assert crs.stress_incremental_gbp == pytest.approx(200_000.0)




class TestCreditRiskCapitalBoardSection:
    def test_section_renders(self):
        from saas.reporting.annual_report import _section_credit_risk_capital
        data = {
            "total_bad_debt_gbp": 50_000.0,
            "total_revenue_gbp": 5_000_000.0,
            "by_year": {
                "2022": {"revenue_gbp": 2_000_000.0, "bad_debt_gbp": 30_000.0},
                "2023": {"revenue_gbp": 3_000_000.0, "bad_debt_gbp": 20_000.0},
            },
        }
        result = _section_credit_risk_capital(data)
        assert "Credit Risk" in result
        assert "2.5x" in result

    def test_section_rag_green_no_bad_debt(self):
        from saas.reporting.annual_report import _section_credit_risk_capital
        data = {
            "total_bad_debt_gbp": 0.0,
            "total_revenue_gbp": 5_000_000.0,
            "by_year": {},
        }
        result = _section_credit_risk_capital(data)
        assert "GREEN" in result

    def test_section_rag_red_material_stress(self):
        from saas.reporting.annual_report import _section_credit_risk_capital
        data = {
            "total_bad_debt_gbp": 1_000_000.0,  # 2.5x = 2.5M, incremental 1.5M = 30% revenue -> RED
            "total_revenue_gbp": 5_000_000.0,
            "by_year": {},
        }
        result = _section_credit_risk_capital(data)
        assert "RED" in result
