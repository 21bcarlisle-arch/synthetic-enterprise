"""Tests for Switching Cost Model (Phase DK)."""
import pytest
from company.crm.switching_cost_model import (
    MeterType, CustomerSegment, SwitchingCostBreakdown,
    SwitchingCostModel,
    _METER_READ_COST_GBP, _FINAL_BILL_COST_GBP, _MPAS_DEREGISTER_COST_GBP,
    _DA_DC_DEAPPOINT_COST_GBP, _BAD_DEBT_RATE_DOMESTIC,
)


class TestSwitchingCostBreakdown:
    def test_basic_domestic_smets2(self):
        s = SwitchingCostModel.estimate(MeterType.SMART_SMETS2, CustomerSegment.DOMESTIC)
        assert s.meter_read_cost_gbp == pytest.approx(_METER_READ_COST_GBP[MeterType.SMART_SMETS2])
        assert s.total_cost_gbp > 0

    def test_dual_fuel_doubles_meter_read(self):
        single = SwitchingCostModel.estimate(MeterType.SMART_SMETS2, CustomerSegment.DOMESTIC)
        dual = SwitchingCostModel.estimate(MeterType.SMART_SMETS2, CustomerSegment.DOMESTIC,
                                           is_dual_fuel=True)
        assert dual.meter_read_cost_gbp == pytest.approx(single.meter_read_cost_gbp * 2)

    def test_dual_fuel_increases_final_bill(self):
        single = SwitchingCostModel.estimate(MeterType.LEGACY_MANUAL, CustomerSegment.SME)
        dual = SwitchingCostModel.estimate(MeterType.LEGACY_MANUAL, CustomerSegment.SME,
                                           is_dual_fuel=True)
        assert dual.final_bill_cost_gbp > single.final_bill_cost_gbp

    def test_legacy_meter_more_expensive(self):
        legacy = SwitchingCostModel.estimate(MeterType.LEGACY_MANUAL, CustomerSegment.DOMESTIC)
        smart = SwitchingCostModel.estimate(MeterType.SMART_SMETS2, CustomerSegment.DOMESTIC)
        assert legacy.meter_read_cost_gbp > smart.meter_read_cost_gbp

    def test_ic_higher_staff_cost(self):
        dom = SwitchingCostModel.estimate(MeterType.SMART_SMETS2, CustomerSegment.DOMESTIC)
        ic = SwitchingCostModel.estimate(MeterType.SMART_SMETS2, CustomerSegment.I_AND_C)
        assert ic.staff_cost_gbp > dom.staff_cost_gbp

    def test_bad_debt_risk_positive_balance(self):
        s = SwitchingCostModel.estimate(MeterType.SMART_SMETS2, CustomerSegment.DOMESTIC,
                                        outstanding_balance_gbp=200.0)
        expected = 200.0 * _BAD_DEBT_RATE_DOMESTIC
        assert s.bad_debt_risk_gbp == pytest.approx(expected)

    def test_no_bad_debt_risk_credit_balance(self):
        s = SwitchingCostModel.estimate(MeterType.SMART_SMETS2, CustomerSegment.DOMESTIC,
                                        outstanding_balance_gbp=-50.0)
        assert s.bad_debt_risk_gbp == pytest.approx(0.0)

    def test_no_bad_debt_risk_zero_balance(self):
        s = SwitchingCostModel.estimate(MeterType.SMART_SMETS2, CustomerSegment.DOMESTIC)
        assert s.bad_debt_risk_gbp == pytest.approx(0.0)

    def test_direct_cost_excludes_bad_debt(self):
        s = SwitchingCostModel.estimate(MeterType.SMART_SMETS2, CustomerSegment.DOMESTIC,
                                        outstanding_balance_gbp=500.0)
        assert s.direct_cost_gbp == pytest.approx(s.total_cost_gbp - s.bad_debt_risk_gbp)

    def test_total_cost_sum_of_components(self):
        s = SwitchingCostModel.estimate(MeterType.LEGACY_MANUAL, CustomerSegment.SME,
                                        outstanding_balance_gbp=100.0)
        expected = (s.meter_read_cost_gbp + s.final_bill_cost_gbp + s.mpas_cost_gbp
                    + s.da_dc_cost_gbp + s.staff_cost_gbp + s.bad_debt_risk_gbp)
        assert s.total_cost_gbp == pytest.approx(expected)

    def test_cost_summary_keys(self):
        s = SwitchingCostModel.estimate(MeterType.SMART_SMETS2, CustomerSegment.DOMESTIC)
        summary = s.cost_summary()
        assert "meter_read" in summary
        assert "final_bill" in summary
        assert "total" in summary
        assert "direct" in summary

    def test_mpas_constant(self):
        s = SwitchingCostModel.estimate(MeterType.SMART_SMETS2, CustomerSegment.DOMESTIC)
        assert s.mpas_cost_gbp == pytest.approx(_MPAS_DEREGISTER_COST_GBP)

    def test_da_dc_constant(self):
        s = SwitchingCostModel.estimate(MeterType.SMART_SMETS2, CustomerSegment.DOMESTIC)
        assert s.da_dc_cost_gbp == pytest.approx(_DA_DC_DEAPPOINT_COST_GBP)


class TestSwitchingCostModelMethods:
    def test_max_retention_offer_positive_margin(self):
        s = SwitchingCostModel.estimate(MeterType.SMART_SMETS2, CustomerSegment.DOMESTIC)
        max_offer = SwitchingCostModel.max_retention_offer_gbp(500.0, s, margin_floor_pct=0.3)
        # Should be switch cost + headroom (500 - 30% floor)
        expected = s.total_cost_gbp + (500.0 * 0.7)
        assert max_offer == pytest.approx(expected)

    def test_max_retention_offer_zero_margin(self):
        s = SwitchingCostModel.estimate(MeterType.SMART_SMETS2, CustomerSegment.DOMESTIC)
        max_offer = SwitchingCostModel.max_retention_offer_gbp(0.0, s)
        assert max_offer == pytest.approx(s.total_cost_gbp)

    def test_max_retention_offer_negative_margin(self):
        s = SwitchingCostModel.estimate(MeterType.SMART_SMETS2, CustomerSegment.DOMESTIC)
        max_offer = SwitchingCostModel.max_retention_offer_gbp(-100.0, s)
        assert max_offer == pytest.approx(s.total_cost_gbp)

    def test_portfolio_summary_empty(self):
        s = SwitchingCostModel.portfolio_summary([])
        assert "no switches" in s

    def test_portfolio_summary_with_switches(self):
        switches = [
            SwitchingCostModel.estimate(MeterType.SMART_SMETS2, CustomerSegment.DOMESTIC),
            SwitchingCostModel.estimate(MeterType.SMART_SMETS2, CustomerSegment.DOMESTIC),
        ]
        s = SwitchingCostModel.portfolio_summary(switches)
        assert "2 switches" in s
        assert "SMETS2" in s

    def test_all_meter_types_defined(self):
        for mt in MeterType:
            assert mt in _METER_READ_COST_GBP

    def test_smets2_cheaper_than_legacy(self):
        assert (_METER_READ_COST_GBP[MeterType.LEGACY_MANUAL] >
                _METER_READ_COST_GBP[MeterType.SMART_SMETS2])
