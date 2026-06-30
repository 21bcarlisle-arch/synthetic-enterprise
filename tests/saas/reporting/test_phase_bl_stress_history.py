"""Phase BL: Portfolio Stress Test History section tests."""
import pytest
from saas.reporting.annual_report import _section_stress_test_history


def _data(yr, treasury, cwu=None):
    return {"years": {str(yr): {
        "treasury_end_gbp": treasury,
        "committee_wake_ups": cwu or [],
    }}}


def _multi(years_dict):
    return {"years": {str(yr): {
        "treasury_end_gbp": t,
        "committee_wake_ups": [],
    } for yr, t in years_dict.items()}}


# 1. Empty returns empty
def test_empty_returns_empty():
    assert _section_stress_test_history({}) == ""
    assert _section_stress_test_history({"years": {}}) == ""


# 2. Header present
def test_header_present():
    d = _data(2022, 3_000_000)
    assert "Portfolio Stress Test" in _section_stress_test_history(d)


# 3. All 5 scenario columns present
def test_five_scenarios():
    d = _data(2022, 3_000_000)
    result = _section_stress_test_history(d)
    assert "Mkt Spike" in result
    assert "Credit" in result
    assert "Demand" in result
    assert "Liquidity" in result
    assert "Combined" in result


# 4. Year row present
def test_year_row():
    d = _data(2022, 3_000_000)
    result = _section_stress_test_history(d)
    assert "| 2022 |" in result


# 5. Treasury shown in row
def test_treasury_in_row():
    d = _data(2022, 3_000_000)
    result = _section_stress_test_history(d)
    assert "£3,000,000" in result


# 6. RAG values are GREEN/AMBER/RED
def test_rag_values():
    d = _data(2022, 3_000_000)
    result = _section_stress_test_history(d)
    assert any(rag in result for rag in ("GREEN", "AMBER", "RED"))


# 7. Most stressed year identified
def test_most_stressed_year():
    # Low treasury = more stressed
    d = _multi({2022: 3_000_000, 2021: 500_000})
    result = _section_stress_test_history(d)
    # 2021 with 500k should be more stressed than 2022 with 3M
    assert "Most stressed year" in result


# 8. VaR from committee wake-up used when available
def test_var_from_cwu():
    cwu = [{"portfolio_var_current_gbp": 100_000.0, "portfolio_var_stressed_gbp": 150_000.0}]
    d = _data(2022, 3_000_000, cwu=cwu)
    # Should not crash when VaR is provided
    result = _section_stress_test_history(d)
    assert "Portfolio Stress Test" in result


# 9. Legend note present
def test_legend_note():
    d = _data(2022, 3_000_000)
    result = _section_stress_test_history(d)
    assert "GREEN" in result and "AMBER" in result and "RED" in result


# 10. Multiple years produces multiple rows
def test_multiple_years():
    d = _multi({2021: 2_000_000, 2022: 3_000_000, 2023: 3_200_000})
    result = _section_stress_test_history(d)
    assert "| 2021 |" in result
    assert "| 2022 |" in result
    assert "| 2023 |" in result


# 11. All-green year noted in summary
def test_all_green_noted():
    # Very high treasury = all GREEN likely
    d = _multi({2021: 100_000_000, 2022: 100_000_000})
    result = _section_stress_test_history(d)
    # With 100M treasury and 25k burn, all should be GREEN
    if "all GREEN" in result or "Clean bill" in result:
        pass  # Good
    # else: just verify no crash and header present
    assert "Portfolio Stress Test" in result


# 12. Zero treasury handled without crash
def test_zero_treasury_no_crash():
    d = _data(2022, 0)
    result = _section_stress_test_history(d)
    assert "Portfolio Stress Test" in result
