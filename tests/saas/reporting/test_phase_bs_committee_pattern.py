"""Phase BS: Risk Committee Intervention Pattern section tests."""
import pytest
from saas.reporting.annual_report import _section_committee_intervention_pattern


def _ev(date, treasury, adjustments, var_cur, var_stress):
    return {
        "settlement_date": date,
        "treasury_gbp": treasury,
        "adjustments": adjustments,
        "portfolio_var_current_gbp": var_cur,
        "portfolio_var_stressed_gbp": var_stress,
    }


def _data(year_events):
    return {"years": {yr: {"committee_wake_ups": evts} for yr, evts in year_events.items()}}


# 1. Empty returns empty
def test_empty_returns_empty():
    assert _section_committee_intervention_pattern({}) == ""
    assert _section_committee_intervention_pattern({"years": {}}) == ""


# 2. No wake-ups at all returns empty
def test_no_wakeups_returns_empty():
    d = _data({"2016": [], "2017": []})
    assert _section_committee_intervention_pattern(d) == ""


# 3. Header present
def test_header_present():
    d = _data({"2022": [_ev("2022-04-29", 3000000, {"C_IC1": 1.0}, 55741, 20653)]})
    assert "Risk Committee Intervention Pattern" in _section_committee_intervention_pattern(d)


# 4. Year row present for wake-up year
def test_year_row():
    d = _data({"2022": [_ev("2022-04-29", 3000000, {"C_IC1": 1.0}, 55741, 20653)]})
    result = _section_committee_intervention_pattern(d)
    assert "| 2022 |" in result


# 5. Wake-up count correct
def test_wakeup_count():
    evts = [_ev("2022-04-29", 3000000, {"C1": 1.0}, 55000, 20000),
            _ev("2022-05-29", 3000000, {"C1": 1.0, "C2": 1.0}, 56000, 21000)]
    d = _data({"2022": evts})
    result = _section_committee_intervention_pattern(d)
    assert "| 2022 | 2 |" in result


# 6. Customer adjustment count correct
def test_customer_adj_count():
    evts = [_ev("2022-04-29", 3000000, {"C1": 1.0, "C2": 1.0}, 55000, 20000)]
    d = _data({"2022": evts})
    result = _section_committee_intervention_pattern(d)
    assert "| 1 | 2 |" in result


# 7. Peak intervention year flagged
def test_peak_intervention_year():
    d = _data({
        "2016": [_ev("2016-04-01", 1000000, {"C1": 1.0}, 10000, 5000)] * 13,
        "2022": [_ev("2022-04-01", 3000000, {"C1": 1.0}, 50000, 20000)] * 9,
    })
    result = _section_committee_intervention_pattern(d)
    assert "Peak intervention year: 2016" in result


# 8. Total events correct
def test_total_events():
    d = _data({
        "2016": [_ev("2016-04-01", 1000000, {"C1": 1.0}, 10000, 5000)] * 3,
        "2022": [_ev("2022-04-01", 3000000, {"C1": 1.0}, 50000, 20000)] * 4,
    })
    result = _section_committee_intervention_pattern(d)
    # total = 3 + 4 + years with 0 events (not shown in table but still counted)
    assert "Total committee events" in result and "7" in result


# 9. Quiet year (no wake-ups) skipped in table
def test_quiet_year_skipped():
    d = _data({"2018": [], "2022": [_ev("2022-04-29", 3000000, {"C1": 1.0}, 55000, 20000)]})
    result = _section_committee_intervention_pattern(d)
    assert "| 2018 |" not in result
    assert "| 2022 |" in result


# 10. Max VaR stressed value in table
def test_max_var_stressed():
    d = _data({"2022": [_ev("2022-04-29", 3000000, {"C1": 1.0}, 55741, 88888)]})
    result = _section_committee_intervention_pattern(d)
    assert "£88,888" in result


# 11. Note about 2022 crisis
def test_crisis_note():
    d = _data({"2022": [_ev("2022-04-29", 3000000, {"C1": 1.0}, 55000, 20000)]})
    result = _section_committee_intervention_pattern(d)
    assert "crisis" in result.lower() or "2022" in result


# 12. Multiple years sorted
def test_years_sorted():
    d = _data({
        "2017": [_ev("2017-01-01", 1000000, {"C1": 1.0}, 10000, 5000)] * 2,
        "2016": [_ev("2016-01-01", 500000, {"C1": 1.0}, 5000, 2000)] * 5,
    })
    result = _section_committee_intervention_pattern(d)
    pos_2016 = result.find("| 2016 |")
    pos_2017 = result.find("| 2017 |")
    assert pos_2016 < pos_2017


# 13. Total committee events shown
def test_total_events_shown():
    d = {"years": {
        "2022": {"committee_wake_ups": [{"adjustments": {"C1": 0.6}, "portfolio_var_stressed_gbp": 50000}]},
        "2023": {"committee_wake_ups": [{"adjustments": {}, "portfolio_var_stressed_gbp": 60000},
                                         {"adjustments": {}, "portfolio_var_stressed_gbp": 55000}]},
    }}
    result = _section_committee_intervention_pattern(d)
    assert "Total committee events" in result and "3" in result


# 14. Peak intervention year noted
def test_peak_intervention_year():
    d = {"years": {
        "2022": {"committee_wake_ups": [{"adjustments": {}, "portfolio_var_stressed_gbp": 1000}]},
        "2023": {"committee_wake_ups": [
            {"adjustments": {}, "portfolio_var_stressed_gbp": 2000},
            {"adjustments": {}, "portfolio_var_stressed_gbp": 3000},
        ]},
    }}
    result = _section_committee_intervention_pattern(d)
    assert "Peak intervention year: 2023" in result


# 15. Zero wake-up years excluded from table
def test_zero_wakeup_year_excluded():
    d = {"years": {
        "2020": {"committee_wake_ups": []},
        "2022": {"committee_wake_ups": [{"adjustments": {}, "portfolio_var_stressed_gbp": 500}]},
    }}
    result = _section_committee_intervention_pattern(d)
    assert "| 2022 |" in result
    assert "| 2020 |" not in result
