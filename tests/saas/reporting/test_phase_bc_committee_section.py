"""Phase BC: Risk Committee Activity annual report section tests."""
import pytest
from saas.reporting.annual_report import _section_risk_committee_activity


def _wk(date="2022-01-15", treas=3e6, var_cur=55000.0, var_stress=20000.0, accts=None):
    return {"settlement_date": date, "treasury_gbp": treas,
            "portfolio_var_current_gbp": var_cur, "portfolio_var_stressed_gbp": var_stress,
            "adjustments": {a: 1.0 for a in (accts or ["C_IC1", "C_IC2"])}}


def _data(years_dict):
    years = {}
    for yr, wks in years_dict.items():
        years[str(yr)] = {"committee_wake_ups": wks}
    return {"years": years}


# 1. Empty data returns empty string
def test_empty_returns_empty():
    assert _section_risk_committee_activity({}) == ""
    assert _section_risk_committee_activity({"years": {}}) == ""


# 2. No wake-ups returns empty
def test_no_wakeups_returns_empty():
    d = {"years": {"2022": {"committee_wake_ups": []}}}
    assert _section_risk_committee_activity(d) == ""


# 3. Header present when sessions exist
def test_header_present():
    d = _data({2022: [_wk()]})
    result = _section_risk_committee_activity(d)
    assert "Risk Committee Activity" in result


# 4. Total sessions count shown
def test_total_sessions_shown():
    d = _data({2022: [_wk(), _wk()], 2023: [_wk()]})
    result = _section_risk_committee_activity(d)
    assert "3" in result and "Total sessions" in result


# 5. Busiest year identified
def test_busiest_year_shown():
    d = _data({2022: [_wk(), _wk(), _wk()], 2023: [_wk()]})
    result = _section_risk_committee_activity(d)
    assert "Busiest year: 2022" in result


# 6. Peak VaR year shown
def test_peak_var_year_shown():
    d = _data({2022: [_wk(var_cur=55000.0)], 2023: [_wk(var_cur=130000.0)]})
    result = _section_risk_committee_activity(d)
    assert "Peak VaR observed: 2023" in result


# 7. Accounts touched per year in table
def test_accounts_touched_shown():
    d = _data({2022: [_wk(accts=["C_IC1", "C_IC2", "C1"])]})
    result = _section_risk_committee_activity(d)
    assert "3" in result  # 3 accounts touched in 2022


# 8. Most frequently adjusted accounts listed
def test_most_adjusted_accounts():
    wk1 = _wk(accts=["C_IC1", "C_IC2"])
    wk2 = _wk(accts=["C_IC1"])  # C_IC1 appears twice
    d = _data({2022: [wk1, wk2]})
    result = _section_risk_committee_activity(d)
    assert "C_IC1: 2 sessions" in result


# 9. Year row appears in table
def test_year_row_in_table():
    d = _data({2022: [_wk(var_cur=55742.0, var_stress=20653.0)]})
    result = _section_risk_committee_activity(d)
    assert "2022" in result
    assert "55,742" in result


# 10. Years with no wake-ups skipped
def test_years_without_wakeups_skipped():
    d = {"years": {"2021": {"committee_wake_ups": []}, "2022": {"committee_wake_ups": [_wk()]}}}
    result = _section_risk_committee_activity(d)
    assert "2022" in result
    assert "2021" not in result


# 11. Unique accounts count shown
def test_unique_accounts_count_shown():
    wk1 = _wk(accts=["C_IC1", "C_IC2"])
    wk2 = _wk(accts=["C_IC1", "C1"])  # C_IC1 duplicated, 3 unique
    d = _data({2022: [wk1, wk2]})
    result = _section_risk_committee_activity(d)
    assert "3" in result  # 3 unique accounts


# 12. Non-list wake-ups skipped gracefully
def test_non_list_wakeups_handled():
    d = {"years": {"2022": {"committee_wake_ups": 9}}}  # integer not list
    result = _section_risk_committee_activity(d)
    assert result == ""


def test_total_sessions_shown():
    d = _data({2022: [_wk(), _wk()], 2023: [_wk()]})
    result = _section_risk_committee_activity(d)
    assert "3" in result  # total sessions


def test_peak_var_shown():
    wk = _wk(var_cur=999000.0)
    d = _data({2022: [wk]})
    result = _section_risk_committee_activity(d)
    assert "999,000" in result or "999" in result


def test_empty_returns_empty():
    from saas.reporting.annual_report import _section_risk_committee_activity
    assert _section_risk_committee_activity({}) == ""
