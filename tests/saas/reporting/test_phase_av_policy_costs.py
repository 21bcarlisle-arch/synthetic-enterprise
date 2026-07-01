"""Phase AV: Policy Cost & Levy Breakdown annual report section tests."""
import pytest
from saas.reporting.annual_report import _section_policy_cost_breakdown


def _yr(ro=1000, cfd=500, ccl=200, cm=100, fit=200, policy=2000, network=500):
    return {
        "ro_levy_gbp": ro,
        "cfd_levy_gbp": cfd,
        "ccl_gbp": ccl,
        "cm_levy_gbp": cm,
        "fit_levy_gbp": fit,
        "policy_cost_gbp": policy,
        "network_cost_gbp": network,
    }


# 1. Empty returns empty
def test_empty_returns_empty():
    assert _section_policy_cost_breakdown({}) == ""
    assert _section_policy_cost_breakdown({"years": {}}) == ""


# 2. No policy_cost_gbp keys returns empty
def test_no_policy_keys_returns_empty():
    d = {"years": {"2022": {"revenue_gbp": 1000}}}
    assert _section_policy_cost_breakdown(d) == ""


# 3. Header present with data
def test_header_present():
    d = {"years": {"2022": _yr()}}
    result = _section_policy_cost_breakdown(d)
    assert "Policy Cost" in result


# 4. Year row in table
def test_year_row_in_table():
    d = {"years": {"2022": _yr()}}
    result = _section_policy_cost_breakdown(d)
    assert "2022" in result


# 5. RO levy in table
def test_ro_in_table():
    d = {"years": {"2022": _yr(ro=50000)}}
    result = _section_policy_cost_breakdown(d)
    assert "£50,000.00" in result


# 6. Negative CfD highlighted in bold
def test_negative_cfd_highlighted():
    d = {"years": {"2022": _yr(cfd=-50000)}}
    result = _section_policy_cost_breakdown(d)
    assert "**" in result
    assert "-50,000" in result or "£-50,000.00" in result


# 7. CfD rebate note shown when negative
def test_cfd_rebate_note():
    d = {"years": {"2022": _yr(cfd=-50000)}}
    result = _section_policy_cost_breakdown(d)
    assert "CfD rebate in 2022" in result


# 8. No rebate note when CfD positive
def test_no_rebate_note_when_positive():
    d = {"years": {"2022": _yr(cfd=50000)}}
    result = _section_policy_cost_breakdown(d)
    assert "rebate" not in result.lower()


# 9. CAGR shown when multiple years
def test_cagr_shown():
    d = {"years": {
        "2016": _yr(policy=1000),
        "2022": _yr(policy=64000),  # ~100% CAGR over 6 years
    }}
    result = _section_policy_cost_breakdown(d)
    assert "CAGR" in result


# 10. Total policy and network cost columns present
def test_total_policy_and_network_columns():
    d = {"years": {"2022": _yr(policy=500000, network=130000)}}
    result = _section_policy_cost_breakdown(d)
    assert "Total Policy" in result
    assert "Network" in result


# 11. Multiple years all appear
def test_multiple_years_all_appear():
    d = {"years": {
        "2020": _yr(policy=400000),
        "2021": _yr(policy=480000),
        "2022": _yr(cfd=-50000, policy=490000),
    }}
    result = _section_policy_cost_breakdown(d)
    assert "2020" in result
    assert "2021" in result
    assert "2022" in result


# 12. First CfD-negative year triggers rebate note
def test_first_cfd_negative_year_identified():
    d = {"years": {
        "2021": _yr(cfd=10000),
        "2022": _yr(cfd=-50000),
        "2023": _yr(cfd=60000),
    }}
    result = _section_policy_cost_breakdown(d)
    assert "2022" in result
    assert "rebate" in result.lower()


def test_cagr_computed_with_two_years():
    from saas.reporting.annual_report import _section_policy_cost_breakdown
    d = {"years": {
        "2020": _yr(policy=1000.0),
        "2022": _yr(policy=1210.0),
    }}
    result = _section_policy_cost_breakdown(d)
    assert "CAGR" in result


def test_missing_policy_cost_skips_section():
    from saas.reporting.annual_report import _section_policy_cost_breakdown
    d = {"years": {"2022": {}}}
    result = _section_policy_cost_breakdown(d)
    assert result == ""


def test_policy_cost_header_present():
    from saas.reporting.annual_report import _section_policy_cost_breakdown
    d = {"years": {"2022": _yr(policy=50000.0)}}
    result = _section_policy_cost_breakdown(d)
    assert "Policy Cost" in result
