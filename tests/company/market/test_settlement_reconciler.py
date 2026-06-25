"""Tests for M1: Elexon settlement interface (Phase 75)."""

import pytest
from company.market.settlement_reconciler import (
    IMBALANCE_FLAG_THRESHOLD_GBP,
    IMBALANCE_REPORT_THRESHOLD_PCT,
    imbalance_summary,
    receive_settlement,
    reconcile_against_bill,
    reconcile_period_batch,
)


def _stmt(customer_id="C1", volume_kwh=500.0, ssp=50.0, net_cost=25.0, hedge_pnl=0.0):
    return receive_settlement(
        period="2016-01-01T00:00:00",
        customer_id=customer_id,
        volume_kwh=volume_kwh,
        ssp_gbp_per_mwh=ssp,
        net_settlement_cost_gbp=net_cost,
        hedge_pnl_gbp=hedge_pnl,
    )


def test_receive_settlement_creates_statement():
    s = _stmt()
    assert s.customer_id == "C1"
    assert s.volume_kwh == 500.0
    assert s.net_settlement_cost_gbp == 25.0


def test_reconcile_zero_imbalance():
    s = _stmt(net_cost=25.0)
    result = reconcile_against_bill(s, billed_revenue_gbp=25.0)
    assert result["imbalance_gbp"] == pytest.approx(0.0)
    assert result["imbalance_pct"] == pytest.approx(0.0)
    assert result["flagged"] is False


def test_reconcile_positive_imbalance():
    s = _stmt(net_cost=20.0)
    result = reconcile_against_bill(s, billed_revenue_gbp=25.0)
    assert result["imbalance_gbp"] == pytest.approx(5.0)


def test_reconcile_negative_imbalance():
    s = _stmt(net_cost=30.0)
    result = reconcile_against_bill(s, billed_revenue_gbp=25.0)
    assert result["imbalance_gbp"] == pytest.approx(-5.0)


def test_reconcile_flags_large_imbalance():
    s = _stmt(net_cost=100.0)
    result = reconcile_against_bill(s, billed_revenue_gbp=120.0)
    assert result["imbalance_pct"] == pytest.approx(20.0)
    assert result["flagged"] is True


def test_reconcile_does_not_flag_small_imbalance():
    s = _stmt(net_cost=100.0)
    result = reconcile_against_bill(s, billed_revenue_gbp=102.0, threshold_pct=5.0)
    assert result["imbalance_pct"] == pytest.approx(2.0)
    assert result["flagged"] is False


def test_reconcile_result_structure():
    s = _stmt()
    result = reconcile_against_bill(s, billed_revenue_gbp=25.0)
    required = {"period", "customer_id", "billed_revenue_gbp",
                "net_settlement_cost_gbp", "imbalance_gbp", "imbalance_pct", "flagged"}
    assert set(result.keys()) == required


def test_batch_reconciliation_counts():
    stmts = [_stmt("C1", net_cost=100.0), _stmt("C2", net_cost=50.0)]
    revenues = {"C1": 105.0, "C2": 55.0}
    result = reconcile_period_batch(stmts, revenues)
    assert result["checked"] == 2
    assert result["total_imbalance_gbp"] == pytest.approx(10.0)


def test_batch_flags_large_imbalances():
    stmts = [_stmt("C1", net_cost=100.0), _stmt("C2", net_cost=50.0)]
    revenues = {"C1": 130.0, "C2": 50.0}
    result = reconcile_period_batch(stmts, revenues)
    assert result["flagged_count"] == 1


def test_imbalance_summary_structure():
    stmts = [_stmt("C1", net_cost=20.0), _stmt("C2", net_cost=30.0)]
    revenues = {"C1": 22.0, "C2": 28.0}
    batch = reconcile_period_batch(stmts, revenues)
    summary = imbalance_summary(batch)
    required = {"total_imbalance_gbp", "favourable_count", "unfavourable_count",
                "flagged_count", "checked", "net_position"}
    assert set(summary.keys()) == required
    assert summary["favourable_count"] == 1
    assert summary["unfavourable_count"] == 1
