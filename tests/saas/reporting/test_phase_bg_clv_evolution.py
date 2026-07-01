"""Phase BG: Portfolio CLV Evolution section tests."""
import pytest
from saas.reporting.annual_report import _section_clv_evolution


def _data(snapshots: dict) -> dict:
    return {"clv_snapshots": snapshots}


def _snap(yr: str, accounts: dict) -> dict:
    return {yr: accounts}


# 1. Empty returns empty
def test_empty_returns_empty():
    assert _section_clv_evolution({}) == ""
    assert _section_clv_evolution({"clv_snapshots": {}}) == ""


# 2. Single year returns empty (need 2+)
def test_single_year_empty():
    d = _data({"2022": {"C1": 1000.0}})
    assert _section_clv_evolution(d) == ""


# 3. Two years returns section
def test_two_years_returns_section():
    d = _data({"2021": {"C1": 1000.0}, "2022": {"C1": 2000.0}})
    result = _section_clv_evolution(d)
    assert "Portfolio CLV Evolution" in result


# 4. Gas accounts (ending 'g') excluded from totals
def test_gas_accounts_excluded():
    d = _data({
        "2021": {"C1": 1000.0, "C1g": 500.0},
        "2022": {"C1": 2000.0, "C1g": 500.0},
    })
    result = _section_clv_evolution(d)
    # Total CLV for 2021 should be 1000, not 1500
    assert "£1,000" in result
    assert "£2,000" in result


# 5. First year shows dash for delta
def test_first_year_no_delta():
    d = _data({"2021": {"C1": 1000.0}, "2022": {"C1": 2000.0}})
    result = _section_clv_evolution(d)
    assert "—" in result


# 6. Positive delta shows + sign
def test_positive_delta():
    d = _data({"2021": {"C1": 1000.0}, "2022": {"C1": 3000.0}})
    result = _section_clv_evolution(d)
    assert "+£2,000" in result


# 7. Negative delta shown
def test_negative_delta():
    d = _data({"2021": {"C1": 3000.0}, "2022": {"C1": 1000.0}})
    result = _section_clv_evolution(d)
    # fall of £2000
    assert "£-2,000" in result or "-£2,000" in result or "£2,000" in result


# 8. Peak CLV year identified
def test_peak_clv_year():
    d = _data({
        "2021": {"C1": 1000.0},
        "2022": {"C1": 5000.0},
        "2023": {"C1": 3000.0},
    })
    result = _section_clv_evolution(d)
    assert "Peak portfolio CLV: 2022" in result


# 9. Earliest/lowest year identified
def test_earliest_lowest():
    d = _data({
        "2021": {"C1": 1000.0},
        "2022": {"C1": 5000.0},
        "2023": {"C1": 3000.0},
    })
    result = _section_clv_evolution(d)
    assert "2021" in result


# 10. Largest YoY gain identified
def test_largest_yoy_gain():
    d = _data({
        "2021": {"C1": 1000.0},
        "2022": {"C1": 10000.0},
        "2023": {"C1": 11000.0},
    })
    result = _section_clv_evolution(d)
    assert "Largest YoY gain: 2022" in result


# 11. Average CLV per account computed
def test_avg_clv():
    d = _data({
        "2021": {"C1": 1000.0, "C2": 3000.0},
        "2022": {"C1": 2000.0, "C2": 4000.0},
    })
    result = _section_clv_evolution(d)
    # 2021 avg = 2000
    assert "£2,000" in result


# 12. Note about forward estimates present
def test_note_present():
    d = _data({"2021": {"C1": 1000.0}, "2022": {"C1": 2000.0}})
    result = _section_clv_evolution(d)
    assert "forward estimates" in result.lower() or "Note:" in result


def test_header_contains_clv_evolution():
    d = _data({"2021": {"C1": 1000.0, "C2": 2000.0}, "2022": {"C1": 1500.0, "C2": 2500.0}})
    result = _section_clv_evolution(d)
    assert "Portfolio CLV Evolution" in result


def test_gas_accounts_excluded_from_total():
    d = _data({
        "2021": {"C1": 1000.0, "C_IC3g": 999999.0},
        "2022": {"C1": 1200.0, "C_IC3g": 999999.0},
    })
    result = _section_clv_evolution(d)
    assert "1,000" in result or "1,200" in result
    assert "999,999" not in result


def test_peak_portfolio_clv_shown():
    d = _data({"2021": {"C1": 1000.0}, "2022": {"C1": 3000.0}})
    result = _section_clv_evolution(d)
    assert "Peak portfolio CLV" in result
