"""Phase CQ: Environmental Impact Register tests (SECR / TCFD)."""
import pytest
from company.sustainability.environmental_impact import (
    EnvironmentalImpactRegister, EmissionRecord, EmissionScope
)

_GAS_FACTOR = 0.18253
_GRID_FACTOR = 0.2104


# 1. Gas Scope 3 emissions correct
def test_gas_scope3_emissions():
    reg = EnvironmentalImpactRegister()
    r = reg.record_gas_scope3(2022, 100_000)
    # 100,000 kWh × 0.18253 = 18,253 kgCO2e = 18.253 tCO2e
    assert abs(r.emissions_tco2e - 100_000 * _GAS_FACTOR / 1000) < 0.001


# 2. Gas emission scope is SCOPE_3_DOWNSTREAM
def test_gas_scope():
    reg = EnvironmentalImpactRegister()
    r = reg.record_gas_scope3(2022, 50_000)
    assert r.scope == EmissionScope.SCOPE_3_DOWNSTREAM


# 3. Electricity market-based zero with 100% REGO coverage
def test_electricity_market_zero_rego():
    reg = EnvironmentalImpactRegister()
    _, market = reg.record_electricity_scope3(2022, 50_000, rego_coverage_fraction=1.0)
    assert market.emissions_tco2e == 0.0


# 4. Electricity location-based uses grid factor
def test_electricity_location_based():
    reg = EnvironmentalImpactRegister()
    location, _ = reg.record_electricity_scope3(2022, 50_000, rego_coverage_fraction=0.0)
    assert abs(location.emission_factor_kgco2e_per_kwh - _GRID_FACTOR) < 0.0001


# 5. Electricity market-based uses partial REGO factor
def test_electricity_partial_rego():
    reg = EnvironmentalImpactRegister()
    _, market = reg.record_electricity_scope3(2022, 100_000, rego_coverage_fraction=0.5)
    # 50% zero + 50% grid factor
    expected_factor = 0.5 * _GRID_FACTOR
    assert abs(market.emission_factor_kgco2e_per_kwh - expected_factor) < 0.0001


# 6. total_scope3_tco2e sums correctly
def test_total_scope3():
    reg = EnvironmentalImpactRegister()
    reg.record_gas_scope3(2022, 100_000)
    # Market-based electricity with 100% REGO = zero
    reg.record_electricity_scope3(2022, 50_000, rego_coverage_fraction=1.0)
    total = reg.total_scope3_tco2e(2022)
    # Only gas counts (elec = 0 with REGO)
    expected_gas = 100_000 * _GAS_FACTOR / 1000
    assert abs(total - expected_gas) < 0.01


# 7. emissions_by_year returns year-keyed dict
def test_emissions_by_year():
    reg = EnvironmentalImpactRegister()
    reg.record_gas_scope3(2021, 50_000)
    reg.record_gas_scope3(2022, 100_000)
    eb = reg.emissions_by_year()
    assert 2021 in eb and 2022 in eb
    assert eb[2022] > eb[2021]


# 8. peak_emission_year identifies correct year
def test_peak_emission_year():
    reg = EnvironmentalImpactRegister()
    reg.record_gas_scope3(2021, 50_000)
    reg.record_gas_scope3(2022, 200_000)
    assert reg.peak_emission_year() == 2022


# 9. emissions_mtco2e scales correctly
def test_emissions_mtco2e():
    reg = EnvironmentalImpactRegister()
    r = reg.record_gas_scope3(2022, 1_000_000_000)  # 1 TWh
    # 1e9 × 0.18253 / 1e6 = 182.53 MtCO2e
    expected = 1_000_000_000 * _GAS_FACTOR / 1_000_000_000  # in Mt
    assert abs(r.emissions_mtco2e - expected) < 0.001


# 10. records_for_year filters correctly
def test_records_for_year():
    reg = EnvironmentalImpactRegister()
    reg.record_gas_scope3(2021, 50_000)
    reg.record_gas_scope3(2022, 100_000)
    assert len(reg.records_for_year(2022)) == 1


# 11. peak_emission_year returns None for empty register
def test_peak_year_empty():
    reg = EnvironmentalImpactRegister()
    assert reg.peak_emission_year() is None


# 12. environmental_summary contains key fields
def test_environmental_summary():
    reg = EnvironmentalImpactRegister()
    reg.record_gas_scope3(2022, 100_000)
    summary = reg.environmental_summary()
    assert "SECR" in summary or "Environmental" in summary
    assert "2022" in summary


# --- Phase ME depth tests ---

def test_year_stored():
    reg = EnvironmentalImpactRegister()
    r = reg.record_gas_scope3(2023, 100_000)
    assert r.year == 2023


def test_scope_stored():
    reg = EnvironmentalImpactRegister()
    r = reg.record_gas_scope3(2022, 50_000)
    assert r.scope == EmissionScope.SCOPE_3_DOWNSTREAM


def test_commodity_gas():
    reg = EnvironmentalImpactRegister()
    r = reg.record_gas_scope3(2022, 50_000)
    assert r.commodity == 'gas'


def test_consumption_kwh_stored():
    reg = EnvironmentalImpactRegister()
    r = reg.record_gas_scope3(2022, 75_000)
    assert r.consumption_kwh == pytest.approx(75_000)


def test_emission_factor_stored():
    reg = EnvironmentalImpactRegister()
    r = reg.record_gas_scope3(2022, 100_000)
    assert r.emission_factor_kgco2e_per_kwh == pytest.approx(_GAS_FACTOR)


def test_emissions_kgco2e_computed():
    reg = EnvironmentalImpactRegister()
    r = reg.record_gas_scope3(2022, 100_000)
    assert r.emissions_kgco2e == pytest.approx(100_000 * _GAS_FACTOR)


def test_emissions_tco2e_computed():
    reg = EnvironmentalImpactRegister()
    r = reg.record_gas_scope3(2022, 100_000)
    assert r.emissions_tco2e == pytest.approx(100_000 * _GAS_FACTOR / 1000)


def test_emissions_mtco2e_is_tco2e_divided_by_million():
    reg = EnvironmentalImpactRegister()
    r = reg.record_gas_scope3(2022, 1_000_000_000)
    assert r.emissions_mtco2e == pytest.approx(r.emissions_tco2e / 1_000_000)


def test_record_gas_scope3_returns_emission_record():
    reg = EnvironmentalImpactRegister()
    result = reg.record_gas_scope3(2022, 100_000)
    assert isinstance(result, EmissionRecord)


def test_emission_scope_has_4_members():
    assert len(list(EmissionScope)) == 4
