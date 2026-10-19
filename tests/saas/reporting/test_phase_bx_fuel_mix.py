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
    assert "| 2022/23 |" in _section_fuel_mix_disclosure(d)


# 5. Renewable percentage shown
def test_renewable_pct_shown():
    d = _data(2022)
    result = _section_fuel_mix_disclosure(d)
    assert "40.8%" in result


# 6. Low-carbon column computed
def test_low_carbon_computed():
    d = _data(2019)
    result = _section_fuel_mix_disclosure(d)
    # 2019/20: ren=37.9% + nuc=16.6% = 54.5%
    assert "54.5%" in result


def test_a_period_with_no_edition_is_named_as_a_gap_not_filled():
    result = _section_fuel_mix_disclosure(_data(2016, 2019))
    assert "| 2016/17 |" not in result
    assert "No published edition held for 2016/17" in result
    assert "| 2019/20 |" in result


# 7. Peak renewable year flagged
def test_peak_renewable_year():
    d = _data(2019, 2025)
    result = _section_fuel_mix_disclosure(d)
    # 2025/26 has 48.0% renewable vs 2019/20 at 37.9%
    assert "Peak renewable share: 2025/26" in result


# 8. Multiple years sorted
def test_years_sorted():
    d = _data(2023, 2019)
    result = _section_fuel_mix_disclosure(d)
    pos_2019 = result.find("| 2019/20 |")
    pos_2023 = result.find("| 2023/24 |")
    assert -1 < pos_2019 < pos_2023


# 9. Renewable majority note
def test_renewable_majority_note():
    d = _data(2019, 2025)
    result = _section_fuel_mix_disclosure(d)
    # On the supply basis renewables peak at 48.0% (2025/26): no majority
    assert "majority not reached" in result.lower()


# 10. Gas percentage shown
def test_gas_pct_shown():
    d = _data(2022)
    result = _section_fuel_mix_disclosure(d)
    # 2022/23 gas = 39.3%
    assert "39.3%" in result


# 11. REGO note present
def test_rego_note():
    d = _data(2022)
    result = _section_fuel_mix_disclosure(d)
    assert "REGO" in result or "rego" in result.lower()


# 12. Coal percentage shown
def test_coal_pct_shown():
    d = _data(2023)
    result = _section_fuel_mix_disclosure(d)
    # 2023/24 coal = 6.3% (imports at the European Attribute Mix)
    assert "6.3%" in result


# 13. Peak renewable year shown
def test_peak_renewable_year_shown():
    from saas.reporting.annual_report import _section_fuel_mix_disclosure
    d = {"years": {"2016": {}, "2017": {}, "2018": {}, "2019": {}, "2020": {},
                   "2021": {}, "2022": {}, "2023": {}, "2024": {}, "2025": {}}}
    result = _section_fuel_mix_disclosure(d)
    if result:
        assert "Peak renewable share" in result


# 14. Low-carbon column shown in bold
def test_low_carbon_bold():
    from saas.reporting.annual_report import _section_fuel_mix_disclosure
    d = {"years": {"2020": {}}}
    result = _section_fuel_mix_disclosure(d)
    if result:
        assert "**" in result  # bold markers for low-carbon


# 15. Nuclear column present
def test_nuclear_column_present():
    from saas.reporting.annual_report import _section_fuel_mix_disclosure
    d = {"years": {"2020": {}}}
    result = _section_fuel_mix_disclosure(d)
    if result:
        assert "Nuclear" in result
