"""Tests for Phase AG: Flexibility Revenue section in annual_report.py."""
import pytest
from saas.reporting.annual_report import _section_flexibility_revenue


def _make_flex_summary(years_data, total=None, cm_total=None, dfs_total=None, peak=None, enrolled_cust_years=None):
    """Build a flexibility_revenue_summary dict for testing."""
    per_year = {}
    calc_total = 0.0
    calc_cm = 0.0
    calc_dfs = 0.0
    calc_peak = 0.0
    calc_enrolled = 0
    for yr, cm, dfs, enrolled in years_data:
        tot = cm + dfs
        per_year[yr] = {"cm_gbp": cm, "dfs_gbp": dfs, "total_gbp": tot, "enrolled_customers": enrolled}
        calc_total += tot
        calc_cm += cm
        calc_dfs += dfs
        calc_peak = max(calc_peak, tot)
        calc_enrolled += enrolled
    return {
        "total_flexibility_revenue_gbp": total if total is not None else calc_total,
        "total_cm_revenue_gbp": cm_total if cm_total is not None else calc_cm,
        "total_dfs_revenue_gbp": dfs_total if dfs_total is not None else calc_dfs,
        "years_with_revenue": sorted(per_year.keys()),
        "peak_year_revenue_gbp": peak if peak is not None else calc_peak,
        "enrolled_customer_years": enrolled_cust_years if enrolled_cust_years is not None else calc_enrolled,
        "per_year": per_year,
    }


def test_returns_empty_when_no_data():
    """Section is silent when flexibility_revenue_summary is absent."""
    assert _section_flexibility_revenue({}) == ""


def test_returns_empty_when_no_years_with_revenue():
    """Section is silent when no customers hold flexible assets."""
    data = {"flexibility_revenue_summary": {"years_with_revenue": [], "per_year": {}}}
    assert _section_flexibility_revenue(data) == ""


def test_returns_empty_when_summary_is_empty_dict():
    """Section is silent when summary is an empty dict."""
    data = {"flexibility_revenue_summary": {}}
    assert _section_flexibility_revenue(data) == ""


def test_renders_section_header():
    """Section header is present when flex data exists."""
    flex = _make_flex_summary([(2020, 100.0, 0.0, 2)])
    result = _section_flexibility_revenue({"flexibility_revenue_summary": flex})
    assert "## Flexibility Revenue" in result
    assert "Phase AG" in result


def test_cm_revenue_pre_dfs_year():
    """Pre-2022 year shows CM revenue and pre-DFS label on DFS column."""
    flex = _make_flex_summary([(2019, 150.0, 0.0, 2)])
    result = _section_flexibility_revenue({"flexibility_revenue_summary": flex})
    assert "150.00" in result
    assert "pre-DFS" in result


def test_dfs_revenue_zero_pre_2022():
    """DFS column shows zero (with pre-DFS label) for years before 2022."""
    flex = _make_flex_summary([(2021, 200.0, 0.0, 3)])
    result = _section_flexibility_revenue({"flexibility_revenue_summary": flex})
    assert "pre-DFS" in result
    # CM revenue present
    assert "200.00" in result


def test_dfs_revenue_present_post_2022():
    """Post-2022 year shows both CM and DFS revenue without pre-DFS label."""
    flex = _make_flex_summary([(2023, 300.0, 90.0, 4)])
    result = _section_flexibility_revenue({"flexibility_revenue_summary": flex})
    assert "300.00" in result
    assert "90.00" in result
    assert "pre-DFS" not in result


def test_all_years_appear_in_table():
    """Every year with revenue appears as a table row."""
    years = [(2019, 100.0, 0.0, 1), (2022, 200.0, 60.0, 2), (2024, 250.0, 75.0, 3)]
    flex = _make_flex_summary(years)
    result = _section_flexibility_revenue({"flexibility_revenue_summary": flex})
    for yr, _, _, _ in years:
        assert str(yr) in result


def test_portfolio_total_in_summary_line():
    """Portfolio total and component breakdown appear in the header summary."""
    flex = _make_flex_summary([(2020, 500.0, 0.0, 5), (2023, 600.0, 200.0, 6)])
    result = _section_flexibility_revenue({"flexibility_revenue_summary": flex})
    assert "1,300.00" in result   # total CM+DFS = 500+600+200
    assert "1,100.00" in result   # CM total
    assert "200.00" in result     # DFS total


def test_enrolled_customers_count_in_row():
    """Enrolled customers count appears in each year row."""
    flex = _make_flex_summary([(2022, 150.0, 45.0, 7)])
    result = _section_flexibility_revenue({"flexibility_revenue_summary": flex})
    assert "| 7 |" in result


def test_dfs_launch_note_in_footer():
    """Footer explains DFS launch date."""
    flex = _make_flex_summary([(2022, 100.0, 30.0, 2)])
    result = _section_flexibility_revenue({"flexibility_revenue_summary": flex})
    assert "October 2022" in result
    assert "NESO" in result


def test_table_has_correct_header_columns():
    """Markdown table has the expected column headers."""
    flex = _make_flex_summary([(2023, 100.0, 30.0, 2)])
    result = _section_flexibility_revenue({"flexibility_revenue_summary": flex})
    assert "CM Revenue" in result
    assert "DFS Revenue" in result
    assert "Enrolled" in result
