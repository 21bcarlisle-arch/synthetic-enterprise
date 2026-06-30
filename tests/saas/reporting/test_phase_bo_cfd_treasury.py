"""Phase BO: CfD Levy, Bad Debt & Treasury Drawdowns section tests."""
import pytest
from saas.reporting.annual_report import _section_cfd_and_treasury


def _y(cfd=0.0, ro=0.0, bd=0.0, draws=0, bills=0):
    return {
        "cfd_levy_gbp": cfd,
        "ro_levy_gbp": ro,
        "bad_debt_gbp": bd,
        "treasury_drawdown_events": [{"amount": 1000}] * draws,
        "bills_count": bills,
    }


def _data(years: dict) -> dict:
    return {"years": {str(yr): d for yr, d in years.items()}}


# 1. Empty returns empty
def test_empty_returns_empty():
    assert _section_cfd_and_treasury({}) == ""
    assert _section_cfd_and_treasury({"years": {}}) == ""


# 2. Header present
def test_header_present():
    d = _data({2022: _y(cfd=50000, ro=250000, bd=35000)})
    assert "CfD Levy" in _section_cfd_and_treasury(d)


# 3. Positive CfD shown as payment
def test_positive_cfd():
    d = _data({2023: _y(cfd=65000, ro=270000, bd=13000)})
    result = _section_cfd_and_treasury(d)
    assert "+£65,000" in result


# 4. Negative CfD shown as CREDIT
def test_negative_cfd_credit():
    d = _data({2022: _y(cfd=-50342, ro=259000, bd=35000)})
    result = _section_cfd_and_treasury(d)
    assert "CREDIT" in result
    assert "£50,342" in result


# 5. CfD CREDIT flagged in summary
def test_cfd_credit_summary():
    d = _data({2022: _y(cfd=-50342, ro=259000)})
    result = _section_cfd_and_treasury(d)
    assert "CfD turned CREDIT" in result
    assert "2022" in result


# 6. Treasury drawdown years flagged
def test_drawdown_years():
    d = _data({
        2021: _y(draws=0),
        2022: _y(draws=1),
        2023: _y(draws=1),
    })
    result = _section_cfd_and_treasury(d)
    assert "Treasury drawdown years" in result
    assert "2022" in result and "2023" in result


# 7. No drawdown shows dash
def test_no_drawdown_shows_dash():
    d = _data({2021: _y(draws=0)})
    result = _section_cfd_and_treasury(d)
    assert "| — |" in result


# 8. Peak bad debt year identified
def test_peak_bad_debt():
    d = _data({
        2021: _y(bd=9000),
        2022: _y(bd=35000),  # highest
        2023: _y(bd=13000),
    })
    result = _section_cfd_and_treasury(d)
    assert "Peak bad debt year: 2022" in result


# 9. RO levy in table
def test_ro_levy_in_table():
    d = _data({2022: _y(ro=259289)})
    result = _section_cfd_and_treasury(d)
    assert "£259,289" in result


# 10. Bills count in table
def test_bills_count():
    d = _data({2022: _y(bills=148)})
    result = _section_cfd_and_treasury(d)
    assert "148" in result


# 11. Note about CfD mechanism present
def test_cfd_mechanism_note():
    d = _data({2022: _y(cfd=-50000)})
    result = _section_cfd_and_treasury(d)
    assert "strike price" in result or "CfD" in result.lower()


# 12. Multiple years sorted
def test_years_sorted():
    d = _data({
        2023: _y(cfd=65000),
        2021: _y(cfd=15000),
        2022: _y(cfd=-50000),
    })
    result = _section_cfd_and_treasury(d)
    pos_2021 = result.find("| 2021 |")
    pos_2022 = result.find("| 2022 |")
    pos_2023 = result.find("| 2023 |")
    assert pos_2021 < pos_2022 < pos_2023
