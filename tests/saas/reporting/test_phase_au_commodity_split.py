"""Phase AU: Commodity Split (electricity vs gas P&L) annual report section tests."""
import pytest
from saas.reporting.annual_report import _section_commodity_split


def _cs_year(e_net, g_net, e_rev, g_rev):
    return {
        "commodity_split": {
            "electricity": {"net_gbp": e_net, "revenue_gbp": e_rev, "gross_gbp": e_net * 1.2, "wholesale_cost_gbp": 0, "capital_gbp": 0},
            "gas": {"net_gbp": g_net, "revenue_gbp": g_rev, "gross_gbp": g_net * 1.1, "wholesale_cost_gbp": 0, "capital_gbp": 0},
        }
    }


# 1. Empty returns empty
def test_empty_returns_empty():
    assert _section_commodity_split({}) == ""
    assert _section_commodity_split({"years": {}}) == ""


# 2. Header present with data
def test_header_present():
    d = {"years": {"2021": _cs_year(1000, -500, 5000, 1000)}}
    result = _section_commodity_split(d)
    assert "Electricity vs Gas" in result


# 3. Year rows in table
def test_year_rows_in_table():
    d = {"years": {"2021": _cs_year(1000, -500, 5000, 1000)}}
    result = _section_commodity_split(d)
    assert "2021" in result


# 4. Gas profitable YES shown
def test_gas_profitable_yes():
    d = {"years": {"2019": _cs_year(200, 50, 1000, 100)}}
    result = _section_commodity_split(d)
    assert "YES" in result


# 5. Gas unprofitable NO shown
def test_gas_unprofitable_no():
    d = {"years": {"2021": _cs_year(1000, -500, 5000, 1000)}}
    result = _section_commodity_split(d)
    assert "**NO**" in result


# 6. Gas share of revenue computed
def test_gas_share_pct():
    d = {"years": {"2021": _cs_year(1000, -500, 8000, 2000)}}
    result = _section_commodity_split(d)
    # 2000 / (8000+2000) = 20.0%
    assert "20.0%" in result


# 7. First loss year identified in summary
def test_first_loss_year_identified():
    d = {"years": {
        "2020": _cs_year(500, 100, 5000, 1000),
        "2021": _cs_year(1000, -500, 5000, 1000),
        "2022": _cs_year(1000, -300, 5000, 1000),
    }}
    result = _section_commodity_split(d)
    assert "2021" in result
    assert "loss-making since 2021" in result.lower() or "Gas has been loss-making since 2021" in result


# 8. Consecutive years count shown
def test_consecutive_years_count():
    d = {"years": {
        "2021": _cs_year(1000, -500, 5000, 1000),
        "2022": _cs_year(1000, -300, 5000, 1000),
        "2023": _cs_year(1000, -200, 5000, 1000),
    }}
    result = _section_commodity_split(d)
    assert "3" in result


# 9. Cross-subsidy note shown
def test_cross_subsidy_note():
    d = {"years": {"2021": _cs_year(1000, -500, 5000, 1000)}}
    result = _section_commodity_split(d)
    assert "cross-subsid" in result.lower() or "Electricity cross-subsid" in result


# 10. All profitable — positive message shown
def test_all_profitable_positive_message():
    d = {"years": {
        "2018": _cs_year(500, 100, 5000, 500),
        "2019": _cs_year(800, 200, 8000, 1000),
    }}
    result = _section_commodity_split(d)
    assert "profitable" in result.lower()


# 11. Missing commodity_split returns empty
def test_missing_commodity_split_empty():
    d = {"years": {"2021": {"revenue_gbp": 1000}}}
    result = _section_commodity_split(d)
    assert result == ""


# 12. Multiple years all appear
def test_multiple_years_all_appear():
    d = {"years": {
        "2020": _cs_year(500, 100, 5000, 500),
        "2021": _cs_year(1000, -500, 5000, 1000),
        "2022": _cs_year(1500, -300, 8000, 1200),
    }}
    result = _section_commodity_split(d)
    assert "2020" in result
    assert "2021" in result
    assert "2022" in result


def test_gas_profitable_throughout_message():
    from saas.reporting.annual_report import _section_commodity_split
    d = {"years": {
        "2019": _cs_year(1000, 200, 10000, 2000),
        "2020": _cs_year(1000, 100, 10000, 2000),
    }}
    result = _section_commodity_split(d)
    assert "profitable throughout" in result


def test_gas_share_pct_in_result():
    from saas.reporting.annual_report import _section_commodity_split
    d = {"years": {"2020": _cs_year(1000, 100, 8000, 2000)}}
    result = _section_commodity_split(d)
    assert "%" in result  # gas share pct shown


def test_first_gas_loss_year_in_message():
    from saas.reporting.annual_report import _section_commodity_split
    d = {"years": {
        "2019": _cs_year(1000, 100, 8000, 2000),
        "2021": _cs_year(2000, -500, 9000, 2000),
    }}
    result = _section_commodity_split(d)
    assert "loss-making since 2021" in result
