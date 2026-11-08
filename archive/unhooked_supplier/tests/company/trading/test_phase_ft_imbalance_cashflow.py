"""Tests for Imbalance Cash Flow Register (Phase FT)."""
import datetime as dt
import pytest
from company.trading.imbalance_cashflow import (
    ImbalanceCashFlowRecord,
    ImbalanceCashFlowRegister,
    ImbalanceDirection,
    SettlementRunType,
    _FLAT_TOLERANCE_MWH,
)

DATE_A = dt.date(2022, 9, 1)
DATE_B = dt.date(2022, 9, 2)
DUE_FUTURE = dt.date(2022, 9, 10)
DUE_PAST = dt.date(2022, 8, 20)


def make_rec(nop=5.0, sbp=50.0, ssp=45.0, date=DATE_A, due=DUE_FUTURE):
    return ImbalanceCashFlowRecord(
        settlement_date=date,
        run_type=SettlementRunType.INITIAL,
        nop_mwh=nop,
        sbp_gbp_per_mwh=sbp,
        ssp_gbp_per_mwh=ssp,
        payment_due_date=due,
    )


class TestImbalanceCashFlowRecord:
    def test_direction_short(self):
        assert make_rec(nop=1.0).direction == ImbalanceDirection.SHORT

    def test_direction_long(self):
        assert make_rec(nop=-1.0).direction == ImbalanceDirection.LONG

    def test_direction_flat_within_tolerance(self):
        assert make_rec(nop=_FLAT_TOLERANCE_MWH * 0.5).direction == ImbalanceDirection.FLAT

    def test_direction_flat_exact_boundary(self):
        assert make_rec(nop=_FLAT_TOLERANCE_MWH).direction == ImbalanceDirection.FLAT

    def test_cash_flow_short_pays_sbp(self):
        r = make_rec(nop=10.0, sbp=50.0)
        assert r.cash_flow_gbp == pytest.approx(-500.0)

    def test_cash_flow_long_receives_ssp(self):
        r = make_rec(nop=-8.0, ssp=45.0)
        assert r.cash_flow_gbp == pytest.approx(360.0)

    def test_cash_flow_flat_is_zero(self):
        assert make_rec(nop=0.0).cash_flow_gbp == pytest.approx(0.0)

    def test_is_outflow_true_for_short(self):
        assert make_rec(nop=5.0).is_outflow is True

    def test_is_outflow_false_for_long(self):
        assert make_rec(nop=-5.0).is_outflow is False

    def test_sbp_ssp_spread(self):
        r = make_rec(sbp=60.0, ssp=45.0)
        assert r.sbp_ssp_spread == pytest.approx(15.0)

    def test_cashflow_summary_contains_direction(self):
        summary = make_rec(nop=5.0).cashflow_summary()
        assert "short" in summary

    def test_cashflow_summary_is_string(self):
        assert isinstance(make_rec().cashflow_summary(), str)


class TestImbalanceCashFlowRegister:
    def test_record_returns_record(self):
        reg = ImbalanceCashFlowRegister()
        r = make_rec()
        result = reg.record(r)
        assert result is r

    def test_records_for_date_filters(self):
        reg = ImbalanceCashFlowRegister()
        reg.record(make_rec(date=DATE_A))
        reg.record(make_rec(date=DATE_B))
        assert len(reg.records_for_date(DATE_A)) == 1

    def test_short_records_filtered(self):
        reg = ImbalanceCashFlowRegister()
        reg.record(make_rec(nop=5.0))
        reg.record(make_rec(nop=-5.0))
        assert len(reg.short_records()) == 1

    def test_long_records_filtered(self):
        reg = ImbalanceCashFlowRegister()
        reg.record(make_rec(nop=5.0))
        reg.record(make_rec(nop=-5.0))
        assert len(reg.long_records()) == 1

    def test_total_net_cashflow(self):
        reg = ImbalanceCashFlowRegister()
        reg.record(make_rec(nop=10.0, sbp=50.0))
        reg.record(make_rec(nop=-8.0, ssp=45.0))
        assert reg.total_net_cashflow_gbp() == pytest.approx(-140.0)

    def test_pending_payments_only_future_outflows(self):
        reg = ImbalanceCashFlowRegister()
        reg.record(make_rec(nop=10.0, sbp=50.0, due=DUE_FUTURE))
        reg.record(make_rec(nop=10.0, sbp=50.0, due=DUE_PAST))
        reg.record(make_rec(nop=-8.0, ssp=45.0, due=DUE_FUTURE))
        result = reg.pending_payments_gbp(DATE_A)
        assert result == pytest.approx(-500.0)

    def test_total_sbp_paid_positive(self):
        reg = ImbalanceCashFlowRegister()
        reg.record(make_rec(nop=10.0, sbp=50.0))
        reg.record(make_rec(nop=-5.0, ssp=45.0))
        assert reg.total_sbp_paid_gbp() == pytest.approx(500.0)

    def test_total_ssp_received_positive(self):
        reg = ImbalanceCashFlowRegister()
        reg.record(make_rec(nop=-8.0, ssp=45.0))
        assert reg.total_ssp_received_gbp() == pytest.approx(360.0)

    def test_cashflow_register_summary_is_string(self):
        reg = ImbalanceCashFlowRegister()
        reg.record(make_rec())
        assert isinstance(reg.cashflow_register_summary(DATE_A), str)

    def test_empty_register_totals_zero(self):
        reg = ImbalanceCashFlowRegister()
        assert reg.total_net_cashflow_gbp() == pytest.approx(0.0)
        assert reg.total_sbp_paid_gbp() == pytest.approx(0.0)
        assert reg.total_ssp_received_gbp() == pytest.approx(0.0)
