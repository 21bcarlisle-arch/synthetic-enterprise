"""Tests for Phase NR: Bad Debt -> Capital Stress Feedback."""
import pytest
from company.risk.credit_risk_stress import (
    CreditRiskStress, build_credit_risk_stress,
    CRISIS_BAD_DEBT_MULTIPLIER, MATERIAL_THRESHOLD_PCT,
)
from company.risk.capital_adequacy import (
    CapitalAdequacyAssessment, CapitalAdequacyStatus,
)


def make_assessment(**kwargs):
    defaults = dict(
        as_of=__import__("datetime").date(2024, 3, 31),
        annual_revenue_gbp=10_000_000.0,
        wind_down_reserve_gbp=300_000.0,
        gross_notional_exposure_gbp=4_000_000.0,
        margin_call_buffer_gbp=500_000.0,
        total_equity_gbp=2_000_000.0,
        risk_weighted_assets_gbp=15_000_000.0,
        stress_var_gbp=1_000_000.0,
    )
    defaults.update(kwargs)
    return CapitalAdequacyAssessment(**defaults)


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


class TestCapitalAdequacyCreditRisk:
    def test_default_credit_risk_is_zero(self):
        a = make_assessment()
        assert a.credit_risk_stress_gbp == 0.0

    def test_stress_test_passes_no_credit_risk(self):
        # equity 2M > var 1M + credit 0 = passes
        a = make_assessment(total_equity_gbp=2_000_000.0, stress_var_gbp=1_000_000.0)
        assert a.stress_test_passes

    def test_stress_test_fails_with_credit_risk(self):
        # equity 2M, var 1M, credit stress 1.5M -> 2M < 2.5M = FAILS
        a = make_assessment(
            total_equity_gbp=2_000_000.0,
            stress_var_gbp=1_000_000.0,
            credit_risk_stress_gbp=1_500_000.0,
        )
        assert not a.stress_test_passes

    def test_stress_test_passes_equity_covers_combined(self):
        # equity 3M > var 1M + credit 1M = passes
        a = make_assessment(
            total_equity_gbp=3_000_000.0,
            stress_var_gbp=1_000_000.0,
            credit_risk_stress_gbp=1_000_000.0,
        )
        assert a.stress_test_passes

    def test_status_marginal_when_credit_causes_stress_failure(self):
        # wind down OK, margin buf OK, equity ratio OK, stress FAILS
        a = make_assessment(
            wind_down_reserve_gbp=300_000.0, annual_revenue_gbp=10_000_000.0,   # OK
            margin_call_buffer_gbp=500_000.0, gross_notional_exposure_gbp=4_000_000.0,  # OK
            total_equity_gbp=2_000_000.0, risk_weighted_assets_gbp=15_000_000.0,  # OK ratio
            stress_var_gbp=500_000.0,
            credit_risk_stress_gbp=2_000_000.0,  # 2M + 0.5M = 2.5M > equity 2M -> FAIL
        )
        # 1 failure (stress_test) -> MARGINAL
        assert a.status == CapitalAdequacyStatus.MARGINAL

    def test_existing_tests_still_pass_no_credit_field(self):
        # Ensure backward compatibility: omitting credit_risk_stress_gbp defaults to 0
        a = CapitalAdequacyAssessment(
            as_of=__import__("datetime").date(2024, 3, 31),
            annual_revenue_gbp=10_000_000.0,
            wind_down_reserve_gbp=300_000.0,
            gross_notional_exposure_gbp=4_000_000.0,
            margin_call_buffer_gbp=500_000.0,
            total_equity_gbp=2_000_000.0,
            risk_weighted_assets_gbp=15_000_000.0,
            stress_var_gbp=1_000_000.0,
        )
        assert a.credit_risk_stress_gbp == 0.0
        assert a.stress_test_passes


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
