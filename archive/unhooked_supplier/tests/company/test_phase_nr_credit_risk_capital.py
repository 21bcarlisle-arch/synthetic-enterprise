# ARCHIVED LEGS of tests/company/test_phase_nr_credit_risk_capital.py (archive increment 3b). The tests here reach a module
# under archive/unhooked_supplier/; the live legs stay at tests/company/test_phase_nr_credit_risk_capital.py.
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


