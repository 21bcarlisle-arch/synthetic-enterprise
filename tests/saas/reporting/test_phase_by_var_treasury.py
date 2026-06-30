"""Phase BY: VaR Trajectory and Treasury Evolution section tests."""
import pytest
from saas.reporting.annual_report import _section_var_treasury_evolution


def _yr(var_r, treasury, net):
    return {"var_ratio": var_r, "treasury_end_gbp": treasury, "net_gbp": net}


def _data(year_tuples):
    return {"years": {str(2016 + i): _yr(*t) for i, t in enumerate(year_tuples)}}


# 1. Empty returns empty
def test_empty_returns_empty():
    assert _section_var_treasury_evolution({}) == ""
    assert _section_var_treasury_evolution({"years": {}}) == ""


# 2. Header present
def test_header_present():
    d = _data([(3.25, 2467421, 1175)])
    assert "VaR Trajectory" in _section_var_treasury_evolution(d)


# 3. Year row present
def test_year_row():
    d = _data([(3.25, 2467421, 1175)])
    assert "| 2016 |" in _section_var_treasury_evolution(d)


# 4. ALERT status for VaR >= 3.0
def test_alert_status():
    d = _data([(3.25, 2467421, 1175)])
    result = _section_var_treasury_evolution(d)
    assert "ALERT" in result


# 5. WATCH status for 0 < VaR < 3.0
def test_watch_status():
    d = _data([(2.5, 2500000, 50000)])
    result = _section_var_treasury_evolution(d)
    assert "WATCH" in result


# 6. No VaR shows dash
def test_no_var_dash():
    d = _data([(0.0, 2500000, 100000)])
    result = _section_var_treasury_evolution(d)
    row = [l for l in result.split("\n") if "| 2016 |" in l][0]
    assert "—" in row


# 7. Peak VaR year identified
def test_peak_var_year():
    d = _data([(2.69, 2497910, 30766), (3.25, 2467421, 1175)])
    result = _section_var_treasury_evolution(d)
    assert "Peak VaR year: 2017" in result


# 8. Treasury peak identified
def test_treasury_peak():
    d = _data([(3.25, 2000000, 1175), (0.0, 3500000, 100000)])
    result = _section_var_treasury_evolution(d)
    assert "Treasury peak: 2017" in result


# 9. Treasury growth shown
def test_treasury_growth():
    d = _data([(3.25, 2467421, 1175), (0.0, 3587262, 92421)])
    result = _section_var_treasury_evolution(d)
    # growth = 3587262 - 2467421 = 1119841
    assert "1,119,841" in result or "+£" in result


# 10. Net margin shown
def test_net_margin_shown():
    d = _data([(3.25, 2467421, 1175)])
    result = _section_var_treasury_evolution(d)
    assert "£1,175" in result


# 11. Negative net shown with minus
def test_negative_net_format():
    d = _data([(3.25, 2467421, -50000)])
    result = _section_var_treasury_evolution(d)
    assert "-£50,000" in result


# 12. VaR trigger note present
def test_var_trigger_note():
    d = _data([(3.25, 2467421, 1175)])
    result = _section_var_treasury_evolution(d)
    assert "3.0" in result and "committee" in result.lower()
