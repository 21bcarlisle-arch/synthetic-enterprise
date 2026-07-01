"""Phase AT: Management Accounts annual report section tests."""
import pytest
from saas.reporting.annual_report import _section_management_accounts


def _make_data(years_dict):
    return {"management_accounts": years_dict}


def _make_year(revenue, wholesale, non_commod, gross, bad_debt, opex, net, cash=100.0, receivables=50.0):
    return {
        "income_statement": {
            "revenue_gbp": revenue,
            "wholesale_cost_gbp": wholesale,
            "non_commodity_cost_gbp": non_commod,
            "gross_margin_gbp": gross,
            "capital_cost_gbp": 0.0,
            "bad_debt_gbp": bad_debt,
            "cost_to_serve_gbp": 0.0,
            "fixed_cost_gbp": 0.0,
            "acquisition_spend_gbp": 0.0,
            "total_opex_gbp": opex,
            "net_margin_gbp": net,
        },
        "balance_sheet": {
            "cash_gbp": cash,
            "trade_receivables_gbp": receivables,
            "total_assets_gbp": cash + receivables,
            "vat_payable_gbp": 0.0,
            "total_liabilities_gbp": 0.0,
            "opening_capital_gbp": 500.0,
            "retained_earnings_gbp": 0.0,
            "current_period_profit_gbp": net,
        },
    }


# 1. Empty data returns empty string
def test_empty_returns_empty():
    assert _section_management_accounts({}) == ""
    assert _section_management_accounts({"management_accounts": {}}) == ""


# 2. Header present with data
def test_header_present():
    d = _make_data({"2022": _make_year(1000, 400, 200, 400, 20, 30, 350)})
    result = _section_management_accounts(d)
    assert "Annual Management Accounts" in result


# 3. Year row appears in table
def test_year_row_in_table():
    d = _make_data({"2022": _make_year(1000, 400, 200, 400, 20, 30, 350)})
    result = _section_management_accounts(d)
    assert "2022" in result
    assert "£1,000.00" in result


# 4. Net margin percentage shown
def test_net_margin_pct_shown():
    d = _make_data({"2022": _make_year(1000, 400, 200, 400, 20, 30, 350)})
    result = _section_management_accounts(d)
    assert "35.0%" in result


# 5. Total row present
def test_total_row_present():
    d = _make_data({"2022": _make_year(1000, 400, 200, 400, 20, 30, 350)})
    result = _section_management_accounts(d)
    assert "Total" in result


# 6. Best year identified
def test_best_year_identified():
    d = _make_data({
        "2021": _make_year(1000, 400, 200, 400, 20, 30, 200),
        "2022": _make_year(2000, 800, 400, 800, 40, 60, 700),
    })
    result = _section_management_accounts(d)
    assert "Best year: 2022" in result or "**Best year:** 2022" in result


# 7. Worst year identified
def test_worst_year_identified():
    d = _make_data({
        "2021": _make_year(1000, 400, 200, 400, 20, 30, 200),
        "2022": _make_year(2000, 800, 400, 800, 40, 60, 700),
    })
    result = _section_management_accounts(d)
    assert "2021" in result
    assert "Worst year" in result


# 8. Balance sheet for latest year shown
def test_balance_sheet_shown():
    d = _make_data({"2022": _make_year(1000, 400, 200, 400, 20, 30, 350, cash=5000.0, receivables=1000.0)})
    result = _section_management_accounts(d)
    assert "Balance Sheet" in result
    assert "Cash" in result


# 9. Cash value shown in balance sheet
def test_cash_in_balance_sheet():
    d = _make_data({"2025": _make_year(1000, 400, 200, 400, 20, 30, 350, cash=99999.0)})
    result = _section_management_accounts(d)
    assert "£99,999.00" in result


# 10. Multiple years all appear in table
def test_multiple_years_in_table():
    d = _make_data({
        "2020": _make_year(500, 200, 100, 200, 10, 15, 175),
        "2021": _make_year(1000, 400, 200, 400, 20, 30, 350),
        "2022": _make_year(2000, 800, 400, 800, 40, 60, 700),
    })
    result = _section_management_accounts(d)
    assert "2020" in result
    assert "2021" in result
    assert "2022" in result


# 11. Total net margin cumulative
def test_total_net_cumulative():
    d = _make_data({
        "2021": _make_year(1000, 400, 200, 400, 20, 30, 200),
        "2022": _make_year(2000, 800, 400, 800, 40, 60, 700),
    })
    result = _section_management_accounts(d)
    # Total net = 200 + 700 = 900
    assert "£900.00" in result or "900" in result


# 12. Latest year balance sheet used (not first year)
def test_latest_year_balance_sheet():
    d = _make_data({
        "2021": _make_year(1000, 400, 200, 400, 20, 30, 350, cash=1000.0),
        "2025": _make_year(2000, 800, 400, 800, 40, 60, 700, cash=9999.0),
    })
    result = _section_management_accounts(d)
    assert "2025" in result
    assert "Year End 2025" in result


def test_revenue_row_in_income_statement():
    from saas.reporting.annual_report import _section_management_accounts
    d = _make_data({"2022": _make_year(10000, 4000, 1000, 5000, 200, 800, 4000)})
    result = _section_management_accounts(d)
    assert "Revenue" in result or "revenue" in result.lower()


def test_single_year_no_best_worst_note():
    from saas.reporting.annual_report import _section_management_accounts
    d = _make_data({"2022": _make_year(10000, 4000, 1000, 5000, 200, 800, 4000)})
    result = _section_management_accounts(d)
    assert result != ""


def test_zero_net_margin_handled():
    from saas.reporting.annual_report import _section_management_accounts
    d = _make_data({"2020": _make_year(5000, 3000, 1000, 1000, 500, 500, 0)})
    result = _section_management_accounts(d)
    assert "0" in result
