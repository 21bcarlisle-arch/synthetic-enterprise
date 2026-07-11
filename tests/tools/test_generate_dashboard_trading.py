"""Tests for tools/generate_dashboard_data.py::extract_trading -- VaR surfacing.

Backlog item (PRIORITIES.md, Trading & Market tab redesign): VaR is already
computed internally in company/trading/hedge_decision.py but was never surfaced.
Blocked on the hedge-volatility-lookback bug fix, now closed
(docs/review_gates/done/HEDGE_VOLATILITY_LOOKBACK_FORESIGHT_BUG.md) -- these
tests cover the extraction of the resulting per-year VaR aggregation.
"""
import pytest

from tools.generate_dashboard_data import extract_trading, VAR_REVENUE_LIMIT


def _hedge_var_log(*entries):
    return {"hedge_var_log": list(entries)}


def test_var_annual_empty_when_no_log():
    result = extract_trading({}, [])
    assert result["var_annual"] == []


def test_var_limit_matches_hedge_decision_constant():
    result = extract_trading({}, [])
    assert result["var_limit_pct_of_term_revenue"] == VAR_REVENUE_LIMIT


def test_var_annual_groups_by_year():
    data = _hedge_var_log(
        {"term_start": "2022-01-01", "var_gbp": 100.0, "var_pct_of_term_revenue": 0.05},
        {"term_start": "2022-06-01", "var_gbp": 200.0, "var_pct_of_term_revenue": 0.10},
        {"term_start": "2023-01-01", "var_gbp": 50.0, "var_pct_of_term_revenue": 0.02},
    )
    result = extract_trading(data, [])
    years = {row["year"]: row for row in result["var_annual"]}
    assert set(years.keys()) == {2022, 2023}
    assert years[2022]["term_count"] == 2
    assert years[2023]["term_count"] == 1


def test_var_annual_avg_and_max_pct():
    data = _hedge_var_log(
        {"term_start": "2022-01-01", "var_gbp": 100.0, "var_pct_of_term_revenue": 0.05},
        {"term_start": "2022-06-01", "var_gbp": 200.0, "var_pct_of_term_revenue": 0.15},
    )
    result = extract_trading(data, [])
    row = result["var_annual"][0]
    assert row["avg_var_pct_of_term_revenue"] == pytest.approx(0.10)
    assert row["max_var_pct_of_term_revenue"] == pytest.approx(0.15)


def test_var_annual_total_var_gbp_sums_entries():
    data = _hedge_var_log(
        {"term_start": "2022-01-01", "var_gbp": 100.0, "var_pct_of_term_revenue": 0.05},
        {"term_start": "2022-06-01", "var_gbp": 200.0, "var_pct_of_term_revenue": 0.10},
    )
    result = extract_trading(data, [])
    assert result["var_annual"][0]["total_var_gbp"] == pytest.approx(300.0)


def test_var_annual_sorted_by_year():
    data = _hedge_var_log(
        {"term_start": "2024-01-01", "var_gbp": 1.0, "var_pct_of_term_revenue": 0.01},
        {"term_start": "2020-01-01", "var_gbp": 1.0, "var_pct_of_term_revenue": 0.01},
        {"term_start": "2022-01-01", "var_gbp": 1.0, "var_pct_of_term_revenue": 0.01},
    )
    result = extract_trading(data, [])
    years = [row["year"] for row in result["var_annual"]]
    assert years == sorted(years)


def test_var_annual_ignores_entries_missing_term_start():
    data = _hedge_var_log(
        {"var_gbp": 1.0, "var_pct_of_term_revenue": 0.01},
        {"term_start": "2022-01-01", "var_gbp": 1.0, "var_pct_of_term_revenue": 0.01},
    )
    result = extract_trading(data, [])
    assert len(result["var_annual"]) == 1
    assert result["var_annual"][0]["term_count"] == 1
