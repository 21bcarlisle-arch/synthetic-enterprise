"""Phase IC: coverage expansion for supplier_fitness_register, annual_board_pack, environmental_impact."""
import datetime as dt

import pytest

from company.regulatory.carbon_emissions import GAS_EMISSION_FACTOR_G_CO2E_PER_KWH


# ===== environmental_impact =====
from company.sustainability.environmental_impact import EmissionScope, EnvironmentalImpactRegister

_GAS_FACTOR = GAS_EMISSION_FACTOR_G_CO2E_PER_KWH / 1000.0  # the one home; was 0.18253, CO2-only
_GRID_FACTOR = 0.2104

def _eir():
    reg = EnvironmentalImpactRegister()
    reg.record_gas_scope3(2022, 10_000_000.0)  # 10M kWh gas
    reg.record_gas_scope3(2023, 9_500_000.0)   # 9.5M kWh gas
    reg.record_electricity_scope3(2022, 5_000_000.0, rego_coverage_fraction=0.5)
    return reg

class TestEnvironmentalImpactRegister:
    def test_gas_scope3_emission_kgco2e(self):
        reg = EnvironmentalImpactRegister()
        r = reg.record_gas_scope3(2022, 10_000_000.0)
        assert r.emissions_kgco2e == pytest.approx(10_000_000 * _GAS_FACTOR)

    def test_gas_scope3_tco2e(self):
        reg = EnvironmentalImpactRegister()
        r = reg.record_gas_scope3(2022, 10_000_000.0)
        assert r.emissions_tco2e == pytest.approx(10_000_000 * _GAS_FACTOR / 1000)

    def test_electricity_scope3_returns_two_records(self):
        reg = EnvironmentalImpactRegister()
        loc, mkt = reg.record_electricity_scope3(2022, 5_000_000.0)
        assert loc.commodity == "electricity_location"
        assert mkt.commodity == "electricity_market"

    def test_electricity_location_uses_grid_factor(self):
        reg = EnvironmentalImpactRegister()
        loc, _ = reg.record_electricity_scope3(2022, 5_000_000.0)
        assert loc.emission_factor_kgco2e_per_kwh == pytest.approx(_GRID_FACTOR)

    def test_electricity_market_factor_with_50pct_rego(self):
        reg = EnvironmentalImpactRegister()
        _, mkt = reg.record_electricity_scope3(2022, 5_000_000.0, rego_coverage_fraction=0.5)
        expected_factor = 0.0 * 0.5 + _GRID_FACTOR * 0.5
        assert mkt.emission_factor_kgco2e_per_kwh == pytest.approx(expected_factor)

    def test_total_scope3_excludes_location_based(self):
        reg = _eir()
        total = reg.total_scope3_tco2e(2022)
        # Should include gas + electricity_market, not electricity_location
        gas_t = 10_000_000 * _GAS_FACTOR / 1000
        elec_mkt_factor = _GRID_FACTOR * 0.5
        elec_t = 5_000_000 * elec_mkt_factor / 1000
        assert total == pytest.approx(gas_t + elec_t, rel=0.01)

    def test_records_for_year(self):
        reg = _eir()
        assert len(reg.records_for_year(2022)) == 3  # gas + loc + mkt

    def test_emissions_by_year_keys(self):
        reg = _eir()
        eb = reg.emissions_by_year()
        assert 2022 in eb and 2023 in eb

    def test_peak_emission_year(self):
        reg = _eir()
        peak = reg.peak_emission_year()
        assert peak == 2022  # higher gas volume in 2022

    def test_environmental_summary_contains_key_fields(self):
        reg = _eir()
        s = reg.environmental_summary()
        assert "SECR" in s and "Scope 3" in s
