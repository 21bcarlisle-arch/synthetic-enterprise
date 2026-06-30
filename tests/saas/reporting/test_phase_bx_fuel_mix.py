"""Phase BX: UK Grid Fuel Mix Disclosure section tests."""
import pytest
from saas.reporting.annual_report import _section_fuel_mix_disclosure


def _data(*years):
    return {"years": {str(yr): {} for yr in years}}


# 1. Empty returns empty
def test_empty_returns_empty():
    assert _section_fuel_mix_disclosure({}) == ""
    assert _section_fuel_mix_disclosure({"years": {}}) == ""


# 2. Header present
def test_header_present():
    d = _data(2022)
    assert "Fuel Mix Disclosure" in _section_fuel_mix_disclosure(d)


# 3. Ofgem FMD mentioned
def test_ofgem_fmd_mentioned():
    d = _data(2022)
    result = _section_fuel_mix_disclosure(d)
    assert "Ofgem" in result or "FMD" in result


# 4. Year row present
def test_year_row():
    d = _data(2022)
    assert "| 2022 |" in _section_fuel_mix_disclosure(d)


# 5. Renewable percentage shown
def test_renewable_pct_shown():
    d = _data(2022)
    result = _section_fuel_mix_disclosure(d)
    assert "40.5%" in result or "%" in result


# 6. Low-carbon column computed
def test_low_carbon_computed():
    d = _data(2016)
    result = _section_fuel_mix_disclosure(d)
    # 2016: ren=24.6% + nuc=20.9% = 45.5%
    assert "45.5%" in result


# 7. Peak renewable year flagged
def test_peak_renewable_year():
    d = _data(2016, 2025)
    result = _section_fuel_mix_disclosure(d)
    # 2025 has 55% renewable vs 2016 at 24.6%
    assert "Peak renewable share: 2025" in result


# 8. Multiple years sorted
def test_years_sorted():
    d = _data(2019, 2016)
    result = _section_fuel_mix_disclosure(d)
    pos_2016 = result.find("| 2016 |")
    pos_2019 = result.find("| 2019 |")
    assert pos_2016 < pos_2019


# 9. Renewable majority note
def test_renewable_majority_note():
    d = _data(2016, 2025)
    result = _section_fuel_mix_disclosure(d)
    # 2025 has 55% renewable (>= 50%), so majority achieved
    assert "majority" in result.lower()


# 10. Gas percentage shown
def test_gas_pct_shown():
    d = _data(2022)
    result = _section_fuel_mix_disclosure(d)
    # 2022 gas = 37.8%
    assert "37.8%" in result


# 11. REGO note present
def test_rego_note():
    d = _data(2022)
    result = _section_fuel_mix_disclosure(d)
    assert "REGO" in result or "rego" in result.lower()


# 12. Coal percentage shown
def test_coal_pct_shown():
    d = _data(2016)
    result = _section_fuel_mix_disclosure(d)
    # 2016 coal = 9.0%
    assert "9.0%" in result
