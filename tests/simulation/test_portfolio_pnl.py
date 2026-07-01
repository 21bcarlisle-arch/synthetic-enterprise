"""Tests for simulation/portfolio_pnl.py -- pure P&L aggregation.

build_portfolio_pnl is pure (no I/O), accumulating settlement records into
portfolio totals and a per-customer breakdown.
"""

from simulation.portfolio_pnl import build_portfolio_pnl


def _record(cid, consumption=100.0, revenue=50.0, wholesale=30.0, margin=20.0):
    return {
        "customer_id": cid,
        "consumption_kwh": consumption,
        "revenue_gbp": revenue,
        "wholesale_cost_gbp": wholesale,
        "margin_gbp": margin,
    }


def test_empty_input_returns_zeros():
    result = build_portfolio_pnl([])
    p = result["portfolio"]
    assert p["consumption_kwh"] == 0.0
    assert p["revenue_gbp"] == 0.0
    assert p["wholesale_cost_gbp"] == 0.0
    assert p["margin_gbp"] == 0.0
    assert p["customer_count"] == 0


def test_empty_input_by_customer_is_empty():
    result = build_portfolio_pnl([])
    assert result["by_customer"] == {}


def test_single_record_portfolio_totals():
    records = [_record("C1", consumption=100.0, revenue=50.0, wholesale=30.0, margin=20.0)]
    result = build_portfolio_pnl(records)
    p = result["portfolio"]
    assert p["consumption_kwh"] == 100.0
    assert p["revenue_gbp"] == 50.0
    assert p["wholesale_cost_gbp"] == 30.0
    assert p["margin_gbp"] == 20.0
    assert p["customer_count"] == 1


def test_two_customers_customer_count():
    records = [_record("C1"), _record("C2")]
    result = build_portfolio_pnl(records)
    assert result["portfolio"]["customer_count"] == 2


def test_same_customer_multiple_records_counts_once():
    records = [_record("C1"), _record("C1")]
    result = build_portfolio_pnl(records)
    assert result["portfolio"]["customer_count"] == 1


def test_by_customer_keys_match_customer_ids():
    records = [_record("C1"), _record("C2")]
    result = build_portfolio_pnl(records)
    assert set(result["by_customer"].keys()) == {"C1", "C2"}


def test_by_customer_settlement_period_count():
    records = [_record("C1"), _record("C1"), _record("C1")]
    result = build_portfolio_pnl(records)
    assert result["by_customer"]["C1"]["settlement_period_count"] == 3


def test_by_customer_accumulates_values():
    records = [
        _record("C1", consumption=100.0, revenue=50.0, wholesale=30.0, margin=20.0),
        _record("C1", consumption=200.0, revenue=80.0, wholesale=60.0, margin=20.0),
    ]
    result = build_portfolio_pnl(records)
    entry = result["by_customer"]["C1"]
    assert entry["consumption_kwh"] == 300.0
    assert entry["revenue_gbp"] == 130.0
    assert entry["wholesale_cost_gbp"] == 90.0
    assert entry["margin_gbp"] == 40.0


def test_portfolio_totals_match_sum_of_customers():
    records = [_record("C1", revenue=50.0, margin=20.0), _record("C2", revenue=80.0, margin=30.0)]
    result = build_portfolio_pnl(records)
    customer_margin_sum = sum(
        v["margin_gbp"] for v in result["by_customer"].values()
    )
    assert result["portfolio"]["margin_gbp"] == customer_margin_sum


def test_result_has_portfolio_and_by_customer_keys():
    result = build_portfolio_pnl([])
    assert "portfolio" in result
    assert "by_customer" in result


def test_portfolio_keys_present():
    result = build_portfolio_pnl([_record("C1")])
    p = result["portfolio"]
    assert "consumption_kwh" in p
    assert "revenue_gbp" in p
    assert "wholesale_cost_gbp" in p
    assert "margin_gbp" in p
    assert "customer_count" in p


def test_negative_margin_allowed():
    records = [_record("C1", revenue=10.0, wholesale=50.0, margin=-40.0)]
    result = build_portfolio_pnl(records)
    assert result["portfolio"]["margin_gbp"] == -40.0

import pytest as _pytest

def test_by_customer_revenue_matches_portfolio_single():
    records = [_record("C1", revenue=55.0)]
    result = build_portfolio_pnl(records)
    assert result["by_customer"]["C1"]["revenue_gbp"] == _pytest.approx(55.0)
    assert result["portfolio"]["revenue_gbp"] == _pytest.approx(55.0)


def test_by_customer_consumption_accumulates():
    records = [_record("C1", consumption=200.0), _record("C1", consumption=300.0)]
    result = build_portfolio_pnl(records)
    assert result["by_customer"]["C1"]["consumption_kwh"] == _pytest.approx(500.0)


def test_zero_margin_records_portfolio_zero():
    records = [_record("C1", margin=0.0), _record("C2", margin=0.0)]
    result = build_portfolio_pnl(records)
    assert result["portfolio"]["margin_gbp"] == 0.0
