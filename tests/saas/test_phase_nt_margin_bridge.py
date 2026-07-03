"""Tests for saas/reporting/margin_attribution.py -- Phase NT."""

import pytest
from saas.reporting.margin_attribution import (
    MarginBridge,
    build_margin_bridge_series,
    dominant_driver,
    _direction,
    _FLAT_THRESHOLD_GBP,
)


def _year(net=100_000, gross=300_000, bad_debt=50_000, capital=20_000,
          policy_cost=80_000, gas_policy_cost=10_000,
          network_cost=30_000, gas_network_cost=10_000,
          active_ids=None):
    return {
        "net_gbp": net,
        "gross_gbp": gross,
        "bad_debt_gbp": bad_debt,
        "capital_gbp": capital,
        "policy_cost_gbp": policy_cost,
        "gas_policy_cost_gbp": gas_policy_cost,
        "network_cost_gbp": network_cost,
        "gas_network_cost_gbp": gas_network_cost,
        "active_customer_ids": active_ids or [],
    }


def _run_data(*year_dicts):
    keys = [str(2020 + i) for i in range(len(year_dicts))]
    return {"years": dict(zip(keys, year_dicts))}


class TestMarginBridge:
    def test_net_delta_correct(self):
        run = _run_data(_year(net=100_000), _year(net=130_000))
        bridges = build_margin_bridge_series(run)
        assert bridges[0].net_delta_gbp == pytest.approx(30_000)

    def test_gross_delta_correct(self):
        run = _run_data(_year(gross=300_000), _year(gross=350_000))
        bridges = build_margin_bridge_series(run)
        assert bridges[0].gross_delta_gbp == pytest.approx(50_000)

    def test_bad_debt_delta_negative_when_cost_rose(self):
        # bad_debt rose from 50k to 100k -- margin contribution is negative
        run = _run_data(_year(bad_debt=50_000), _year(bad_debt=100_000))
        bridges = build_margin_bridge_series(run)
        assert bridges[0].bad_debt_delta_gbp == pytest.approx(-50_000)

    def test_capital_delta_negative_when_cost_rose(self):
        run = _run_data(_year(capital=20_000), _year(capital=60_000))
        bridges = build_margin_bridge_series(run)
        assert bridges[0].capital_delta_gbp == pytest.approx(-40_000)

    def test_policy_cost_delta_sums_both_components(self):
        # policy_cost 80k->90k and gas_policy_cost 10k->15k => delta = -(90+15 - 80-10) = -15k
        run = _run_data(
            _year(policy_cost=80_000, gas_policy_cost=10_000),
            _year(policy_cost=90_000, gas_policy_cost=15_000),
        )
        bridges = build_margin_bridge_series(run)
        assert bridges[0].policy_cost_delta_gbp == pytest.approx(-15_000)

    def test_network_cost_delta_sums_both_components(self):
        run = _run_data(
            _year(network_cost=30_000, gas_network_cost=10_000),
            _year(network_cost=50_000, gas_network_cost=20_000),
        )
        bridges = build_margin_bridge_series(run)
        assert bridges[0].network_cost_delta_gbp == pytest.approx(-30_000)

    def test_residual_near_zero(self):
        run = _run_data(_year(), _year(net=150_000, gross=350_000))
        bridges = build_margin_bridge_series(run)
        assert abs(bridges[0].residual_gbp) < 0.01

    def test_portfolio_change_positive_on_growth(self):
        run = _run_data(
            _year(active_ids=["A", "B"]),
            _year(active_ids=["A", "B", "C"]),
        )
        bridges = build_margin_bridge_series(run)
        assert bridges[0].portfolio_change == 1

    def test_portfolio_change_negative_on_churn(self):
        run = _run_data(
            _year(active_ids=["A", "B", "C"]),
            _year(active_ids=["A"]),
        )
        bridges = build_margin_bridge_series(run)
        assert bridges[0].portfolio_change == -2

    def test_year_label_format(self):
        run = _run_data(_year(), _year())
        bridges = build_margin_bridge_series(run)
        assert "2020" in bridges[0].year_label
        assert "2021" in bridges[0].year_label


class TestDirection:
    def test_improvement_above_threshold(self):
        assert _direction(_FLAT_THRESHOLD_GBP + 1) == "IMPROVEMENT"

    def test_deterioration_below_threshold(self):
        assert _direction(-_FLAT_THRESHOLD_GBP - 1) == "DETERIORATION"

    def test_flat_within_threshold(self):
        assert _direction(0) == "FLAT"
        assert _direction(_FLAT_THRESHOLD_GBP) == "FLAT"
        assert _direction(-_FLAT_THRESHOLD_GBP) == "FLAT"


class TestBuildSeries:
    def test_returns_n_minus_1_bridges(self):
        run = _run_data(_year(), _year(), _year())
        bridges = build_margin_bridge_series(run)
        assert len(bridges) == 2

    def test_returns_empty_for_single_year(self):
        run = _run_data(_year())
        bridges = build_margin_bridge_series(run)
        assert bridges == []

    def test_returns_empty_for_no_years(self):
        assert build_margin_bridge_series({}) == []

    def test_bridges_sorted_chronologically(self):
        run = _run_data(_year(), _year(), _year())
        bridges = build_margin_bridge_series(run)
        assert bridges[0].year_from < bridges[1].year_from


class TestDominantDriver:
    def test_bad_debt_dominates(self):
        # gross_delta=10k, bad_debt_delta=-200k => bad debt wins
        run = _run_data(_year(bad_debt=10_000), _year(bad_debt=210_000, gross=310_000))
        bridges = build_margin_bridge_series(run)
        assert dominant_driver(bridges[0]) == "bad debt"

    def test_gross_margin_dominates(self):
        run = _run_data(_year(gross=100_000), _year(gross=400_000))
        bridges = build_margin_bridge_series(run)
        assert dominant_driver(bridges[0]) == "gross margin"
