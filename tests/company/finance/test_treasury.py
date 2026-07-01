"""Tests for FI3: Treasury management (Phase 70)."""

import pytest
from company.finance.treasury import (
    MCR_PER_ACCOUNT,
    annual_cash_changes,
    cash_flow_by_year,
    project_treasury,
    treasury_health,
    working_capital,
)


def _bs(cash=1000.0, receivables=200.0, vat_payable=0.0, liabilities=100.0):
    return {
        "cash_gbp": cash,
        "trade_receivables_gbp": receivables,
        "vat_payable_gbp": vat_payable,
        "total_liabilities_gbp": liabilities,
    }


def _pack(years_cash: dict) -> dict:
    pack = {}
    for yr, cash in years_cash.items():
        pack[str(yr)] = {
            "income_statement": {},
            "balance_sheet": _bs(cash=cash),
        }
    return pack


def test_working_capital_positive():
    bs = _bs(cash=500.0, receivables=100.0, liabilities=200.0)
    assert working_capital(bs) == 400.0


def test_working_capital_negative():
    bs = _bs(cash=100.0, receivables=0.0, liabilities=500.0)
    assert working_capital(bs) == -400.0


def test_working_capital_zero_when_balanced():
    bs = _bs(cash=200.0, receivables=0.0, liabilities=200.0)
    assert working_capital(bs) == 0.0


def test_cash_flow_by_year_returns_all_years():
    pack = _pack({2020: 1000.0, 2021: 1500.0, 2022: 900.0})
    result = cash_flow_by_year(pack)
    assert set(result.keys()) == {"2020", "2021", "2022"}
    assert result["2021"] == 1500.0


def test_annual_cash_changes_correct_delta():
    pack = _pack({2020: 1000.0, 2021: 1400.0, 2022: 1200.0})
    changes = annual_cash_changes(pack)
    assert changes["2021"] == 400.0
    assert changes["2022"] == -200.0


def test_project_treasury_returns_n_years():
    pack = _pack({2020: 1000.0, 2021: 1200.0, 2022: 1400.0, 2023: 1600.0})
    result = project_treasury(pack, "2023", horizon_years=3)
    assert set(result.keys()) == {"2024", "2025", "2026"}


def test_project_treasury_positive_trend():
    pack = _pack({2020: 1000.0, 2021: 1200.0, 2022: 1400.0, 2023: 1600.0})
    result = project_treasury(pack, "2023", horizon_years=2)
    assert result["2024"] > 1600.0
    assert result["2025"] > result["2024"]


def test_project_treasury_negative_trend():
    pack = _pack({2020: 1000.0, 2021: 800.0, 2022: 600.0, 2023: 400.0})
    result = project_treasury(pack, "2023", horizon_years=2)
    assert result["2024"] < 400.0
    assert result["2025"] < result["2024"]


def test_treasury_health_structure():
    pack = _pack({2022: 5000.0})
    result = treasury_health(pack, "2022", customer_count=10)
    required_keys = {"year", "cash_gbp", "working_capital_gbp",
                     "mcr_requirement_gbp", "mcr_headroom_gbp",
                     "mcr_headroom_ratio", "status"}
    assert set(result.keys()) == required_keys


def test_treasury_health_ok_when_comfortable():
    pack = _pack({2022: 100_000.0})
    result = treasury_health(pack, "2022", customer_count=10)
    mcr = 10 * MCR_PER_ACCOUNT
    assert result["mcr_headroom_gbp"] == round(100_000.0 - mcr, 2)
    assert result["status"] == "OK"


def test_treasury_health_critical_when_below_mcr():
    pack = _pack({2022: 50.0})
    result = treasury_health(pack, "2022", customer_count=10)
    assert result["status"] == "CRITICAL"
    assert result["mcr_headroom_gbp"] < 0


def test_treasury_health_watch_at_boundary():
    pack = _pack({2022: 10 * MCR_PER_ACCOUNT + 1.0})
    result = treasury_health(pack, "2022", customer_count=10)
    assert result["status"] == "WATCH"


# --- Phase LW depth tests ---

def test_mcr_per_account_constant():
    assert MCR_PER_ACCOUNT == pytest.approx(130.0)


def test_working_capital_basic():
    bs = _bs(cash=1000.0, receivables=200.0, vat_payable=0.0, liabilities=100.0)
    assert working_capital(bs) == pytest.approx(1100.0)


def test_working_capital_negative_when_liabilities_exceed():
    bs = _bs(cash=100.0, receivables=0.0, vat_payable=0.0, liabilities=500.0)
    assert working_capital(bs) < 0


def test_working_capital_includes_receivables():
    bs_with = _bs(cash=500.0, receivables=300.0)
    bs_without = _bs(cash=500.0, receivables=0.0)
    assert working_capital(bs_with) > working_capital(bs_without)


def test_treasury_health_status_ok():
    pack = {'2022': {'balance_sheet': {'cash_gbp': 100000.0, 'trade_receivables_gbp': 0.0,
                                       'vat_payable_gbp': 0.0, 'total_liabilities_gbp': 0.0}}}
    h = treasury_health(pack, '2022', customer_count=10)
    assert h['status'] == 'OK'


def test_treasury_health_cash_returned():
    pack = {'2022': {'balance_sheet': {'cash_gbp': 50000.0, 'trade_receivables_gbp': 0.0,
                                       'vat_payable_gbp': 0.0, 'total_liabilities_gbp': 0.0}}}
    h = treasury_health(pack, '2022', customer_count=1)
    assert h['cash_gbp'] == pytest.approx(50000.0)


def test_treasury_health_mcr_requirement():
    pack = {'2022': {'balance_sheet': {'cash_gbp': 50000.0, 'trade_receivables_gbp': 0.0,
                                       'vat_payable_gbp': 0.0, 'total_liabilities_gbp': 0.0}}}
    h = treasury_health(pack, '2022', customer_count=10)
    assert h['mcr_requirement_gbp'] == pytest.approx(10 * 130.0)


def test_treasury_health_missing_year_returns_watch_or_critical():
    h = treasury_health({}, '2099', customer_count=100)
    assert h['status'] in ('WATCH', 'CRITICAL')


def test_treasury_health_has_all_keys():
    pack = {'2022': {'balance_sheet': {'cash_gbp': 50000.0, 'trade_receivables_gbp': 0.0,
                                       'vat_payable_gbp': 0.0, 'total_liabilities_gbp': 0.0}}}
    h = treasury_health(pack, '2022', customer_count=5)
    for k in ('year', 'cash_gbp', 'working_capital_gbp', 'mcr_requirement_gbp',
              'mcr_headroom_gbp', 'mcr_headroom_ratio', 'status'):
        assert k in h


def test_working_capital_zero_everything():
    assert working_capital({}) == pytest.approx(0.0)
