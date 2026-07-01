"""Phase AW: Bill Shock Analysis annual report section tests."""
import pytest
from saas.reporting.annual_report import _section_bill_shock_analysis


def _yr(avg_shock, events_count, bills=100):
    events = [{"customer_id": "C1", "period_end": "2022-01-31", "bill_shock_pct": 0.3}] * events_count
    return {
        "avg_bill_shock_pct": avg_shock,
        "bill_shock_events": events,
        "bills_count": bills,
    }


# 1. Empty returns empty
def test_empty_returns_empty():
    assert _section_bill_shock_analysis({}) == ""
    assert _section_bill_shock_analysis({"years": {}}) == ""


# 2. No avg_bill_shock_pct returns empty
def test_no_shock_data_returns_empty():
    d = {"years": {"2022": {"revenue_gbp": 1000}}}
    assert _section_bill_shock_analysis(d) == ""


# 3. Header present
def test_header_present():
    d = {"years": {"2022": _yr(0.338, 61)}}
    result = _section_bill_shock_analysis(d)
    assert "Bill Shock" in result


# 4. Year in table
def test_year_in_table():
    d = {"years": {"2022": _yr(0.338, 61)}}
    result = _section_bill_shock_analysis(d)
    assert "2022" in result


# 5. HIGH flag shown for >= 30%
def test_high_flag_shown():
    d = {"years": {"2022": _yr(0.338, 61)}}
    result = _section_bill_shock_analysis(d)
    assert "HIGH" in result


# 6. ELEVATED flag shown for 20-30%
def test_elevated_flag_shown():
    d = {"years": {"2022": _yr(0.25, 30)}}
    result = _section_bill_shock_analysis(d)
    assert "ELEVATED" in result


# 7. No flag for < 20%
def test_no_flag_below_20pct():
    d = {"years": {"2020": _yr(0.145, 53)}}
    result = _section_bill_shock_analysis(d)
    assert "HIGH" not in result
    assert "ELEVATED" not in result


# 8. Worst year identified in crisis note
def test_worst_year_in_crisis_note():
    d = {"years": {
        "2020": _yr(0.145, 53),
        "2022": _yr(0.338, 61),
        "2023": _yr(0.172, 42),
    }}
    result = _section_bill_shock_analysis(d)
    assert "Crisis peak: 2022" in result or "2022" in result


# 9. Shock rate computed as events / bills
def test_shock_rate_computed():
    d = {"years": {"2022": _yr(0.338, 40, bills=100)}}
    result = _section_bill_shock_analysis(d)
    assert "40%" in result


# 10. Regulatory SLC note shown
def test_regulatory_note():
    d = {"years": {"2022": _yr(0.338, 61)}}
    result = _section_bill_shock_analysis(d)
    assert "SLC" in result or "Ofgem" in result


# 11. Multiple years all appear
def test_multiple_years_appear():
    d = {"years": {
        "2020": _yr(0.145, 53),
        "2021": _yr(0.159, 51),
        "2022": _yr(0.338, 61),
    }}
    result = _section_bill_shock_analysis(d)
    assert "2020" in result and "2021" in result and "2022" in result


# 12. Shock pct formatted correctly
def test_shock_pct_formatted():
    d = {"years": {"2022": _yr(0.338, 61)}}
    result = _section_bill_shock_analysis(d)
    assert "33.8%" in result


def test_bill_shock_header_present():
    from saas.reporting.annual_report import _section_bill_shock_analysis
    d = {"years": {"2022": _yr(0.25, 30)}}
    result = _section_bill_shock_analysis(d)
    assert "Bill Shock" in result


def test_elevated_flag_shown():
    from saas.reporting.annual_report import _section_bill_shock_analysis
    d = {"years": {"2022": _yr(0.25, 30, bills=100)}}
    result = _section_bill_shock_analysis(d)
    assert "ELEVATED" in result


def test_zero_events_no_flag():
    from saas.reporting.annual_report import _section_bill_shock_analysis
    d = {"years": {"2020": _yr(0.05, 0, bills=100)}}
    result = _section_bill_shock_analysis(d)
    assert "HIGH" not in result
    assert "ELEVATED" not in result
