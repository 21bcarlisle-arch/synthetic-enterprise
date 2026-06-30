"""Phase CB: Hedge Value-Add Analysis annual report section tests."""
import pytest


def _mk_data(years_dict):
    return {"years": years_dict}


def _section(years_dict):
    from saas.reporting.annual_report import _section_hedge_value_add
    return _section_hedge_value_add(_mk_data(years_dict))


def _yr(actual, naked):
    va = actual - naked
    return {
        "hedge_effectiveness": {
            "actual_net_gbp": actual,
            "naked_net_gbp": naked,
            "hedging_value_add_gbp": va,
        }
    }


# 1. Empty data returns empty
def test_empty_returns_empty():
    assert _section({}) == ""


# 2. Year with no hedge_effectiveness key returns empty
def test_missing_hedge_data_returns_empty():
    assert _section({"2022": {}}) == ""


# 3. Section header present
def test_section_header():
    result = _section({"2022": _yr(100000, 900000)})
    assert "Hedge Value-Add Analysis" in result


# 4. Negative value-add shown with minus sign
def test_negative_value_add_displayed():
    result = _section({"2022": _yr(100000, 1000000)})
    # Value add = -900000
    assert "£-900,000" in result


# 5. Year shown in table row
def test_year_in_row():
    result = _section({"2019": _yr(242695, 825966)})
    assert "2019" in result


# 6. Total row at bottom
def test_total_row():
    result = _section({"2022": _yr(100000, 1000000), "2023": _yr(200000, 800000)})
    assert "Total" in result


# 7. Total value-add = sum of individual value-adds
def test_total_value_add_sum():
    result = _section({"2020": _yr(73762, 934294), "2021": _yr(144025, 349142)})
    # total_actual = 217787, total_naked = 1283436, va = -1065649
    assert "1,065,649" in result


# 8. Largest hedging cost year identified (most negative)
def test_worst_year_identified():
    result = _section({
        "2020": _yr(73762, 934294),   # va = -860532
        "2022": _yr(103679, 1092096), # va = -988417
    })
    assert "Largest hedging cost" in result
    assert "2022" in result


# 9. Smallest hedging cost year identified (least negative)
def test_best_year_identified():
    result = _section({
        "2016": _yr(2033, 10918),    # va = -8885 (smallest cost)
        "2022": _yr(103679, 1092096), # va = -988417
    })
    assert "Smallest hedging cost" in result
    assert "2016" in result


# 10. Conclusion states hedging cost when total VA negative
def test_conclusion_cost_shown():
    result = _section({"2022": _yr(100000, 1000000)})
    assert "cost" in result


# 11. Actual net in table matches input
def test_actual_net_displayed():
    result = _section({"2022": _yr(103679, 1092096)})
    assert "£103,679" in result


# 12. Naked net in table matches input
def test_naked_net_displayed():
    result = _section({"2022": _yr(103679, 1092096)})
    assert "£1,092,096" in result
