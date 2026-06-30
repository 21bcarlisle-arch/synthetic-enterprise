"""Phase BQ: BSC Credit Obligation and Regulatory Levy tests."""
import pytest
from saas.reporting.annual_report import _section_bsc_regulatory_levies


def _yr(bsc_cr, cm, mute, ccl, gas_net):
    return {
        "bsc_credit_required_gbp": bsc_cr,
        "cm_levy_gbp": cm,
        "mutualization_levy_gbp": mute,
        "ccl_gbp": ccl,
        "gas_network_cost_gbp": gas_net,
    }


def _data(*year_tuples):
    return {"years": {str(2016 + i): _yr(*t) for i, t in enumerate(year_tuples)}}


# 1. Empty returns empty
def test_empty_returns_empty():
    assert _section_bsc_regulatory_levies({}) == ""
    assert _section_bsc_regulatory_levies({"years": {}}) == ""


# 2. Header present
def test_header_present():
    d = _data((10210, 37170, 100685, 71853, 54433))
    assert "BSC Credit Obligation" in _section_bsc_regulatory_levies(d)


# 3. Year row present
def test_year_row():
    d = _data((10210, 37170, 100685, 71853, 54433))
    assert "| 2016 |" in _section_bsc_regulatory_levies(d)


# 4. Peak BSC credit flagged
def test_peak_bsc_year():
    d = _data((100, 500, 0, 200, 0), (10210, 37170, 100685, 71853, 54433))
    result = _section_bsc_regulatory_levies(d)
    assert "Peak BSC credit obligation: 2017" in result


# 5. Mutualization 0 shows dash
def test_zero_mutualization_dash():
    d = _data((100, 500, 0, 200, 0))
    result = _section_bsc_regulatory_levies(d)
    assert "—" in result


# 6. Mutualization non-zero shown
def test_nonzero_mutualization():
    d = _data((10210, 37170, 100685, 71853, 54433))
    result = _section_bsc_regulatory_levies(d)
    assert "£100,685" in result


# 7. First mutualization year noted
def test_first_mutualization_year():
    d = _data((100, 500, 0, 200, 0), (200, 600, 41818, 72054, 50441))
    result = _section_bsc_regulatory_levies(d)
    assert "2017" in result and "first appeared in" in result


# 8. BSC credit amount correct
def test_bsc_credit_value():
    d = _data((10210, 37170, 100685, 71853, 54433))
    result = _section_bsc_regulatory_levies(d)
    assert "£10,210" in result


# 9. CM levy correct
def test_cm_levy_value():
    d = _data((10210, 37170, 100685, 71853, 54433))
    result = _section_bsc_regulatory_levies(d)
    assert "£37,170" in result


# 10. CCL value correct
def test_ccl_value():
    d = _data((10210, 37170, 100685, 71853, 54433))
    result = _section_bsc_regulatory_levies(d)
    assert "£71,853" in result


# 11. BSC note present
def test_bsc_note():
    d = _data((10210, 37170, 100685, 71853, 54433))
    result = _section_bsc_regulatory_levies(d)
    assert "Elexon" in result or "BSC credit" in result.lower()


# 12. Multiple years sorted
def test_years_sorted():
    d = _data(
        (5291, 50148, 41818, 72054, 50441),
        (10210, 37170, 100685, 71853, 54433),
    )
    result = _section_bsc_regulatory_levies(d)
    pos_2016 = result.find("| 2016 |")
    pos_2017 = result.find("| 2017 |")
    assert pos_2016 < pos_2017
