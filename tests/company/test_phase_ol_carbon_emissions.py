"""Tests for Phase OL: Carbon Emissions Reporting Observatory."""
import pytest
from company.regulatory.carbon_emissions import (
    FuelMixRecord,
    CustomerCarbonFootprint,
    build_customer_footprint,
    _EMISSION_FACTORS_G_CO2_PER_KWH,
)


class TestFuelMixRecord:
    def _make_mix(self, coal=0.0, gas=40.0, nuclear=20.0, wind=20.0,
                  solar=5.0, hydro=3.0, biomass=10.0, imports=2.0, year=2022):
        return FuelMixRecord(
            year=year, coal_pct=coal, gas_pct=gas, nuclear_pct=nuclear,
            wind_pct=wind, solar_pct=solar, hydro_pct=hydro,
            biomass_pct=biomass, imports_pct=imports,
        )

    def test_renewable_pct(self):
        mix = self._make_mix(wind=20.0, solar=5.0, hydro=3.0)
        assert mix.renewable_pct == pytest.approx(28.0)

    def test_low_carbon_pct_includes_nuclear(self):
        mix = self._make_mix(wind=20.0, solar=5.0, hydro=3.0, nuclear=20.0, biomass=10.0)
        assert mix.low_carbon_pct == pytest.approx(58.0)

    def test_emission_intensity_coal_dominated(self):
        mix = self._make_mix(coal=100.0, gas=0.0, nuclear=0.0, wind=0.0,
                             solar=0.0, hydro=0.0, biomass=0.0, imports=0.0)
        assert mix.emission_intensity_g_per_kwh == pytest.approx(820.0)

    def test_emission_intensity_wind_dominated(self):
        mix = self._make_mix(coal=0.0, gas=0.0, nuclear=0.0, wind=100.0,
                             solar=0.0, hydro=0.0, biomass=0.0, imports=0.0)
        assert mix.emission_intensity_g_per_kwh == pytest.approx(11.0)

    def test_emission_intensity_declines_coal_to_wind(self):
        coal_mix = self._make_mix(coal=50.0, gas=50.0, nuclear=0.0, wind=0.0,
                                   solar=0.0, hydro=0.0, biomass=0.0, imports=0.0)
        wind_mix = self._make_mix(coal=0.0, gas=20.0, nuclear=20.0, wind=40.0,
                                   solar=5.0, hydro=5.0, biomass=5.0, imports=5.0)
        assert wind_mix.emission_intensity_g_per_kwh < coal_mix.emission_intensity_g_per_kwh

    def test_total_pct_is_100(self):
        mix = self._make_mix()
        assert mix.total_pct == pytest.approx(100.0, abs=0.5)


class TestCustomerCarbonFootprint:
    def test_electricity_co2_kg(self):
        fp = CustomerCarbonFootprint(
            customer_id="C_IC1", year=2022,
            electricity_kwh=1_000_000.0,
            gas_kwh=0.0,
            electricity_intensity_g_per_kwh=237.0,
        )
        expected = round(1_000_000.0 * 237.0 / 1000, 1)
        assert fp.electricity_co2_kg == pytest.approx(expected)

    def test_gas_co2_kg(self):
        fp = CustomerCarbonFootprint(
            customer_id="C_IC1", year=2022,
            electricity_kwh=0.0,
            gas_kwh=500_000.0,
            electricity_intensity_g_per_kwh=237.0,
        )
        expected = round(500_000.0 * 183.0 / 1000, 1)
        assert fp.gas_co2_kg == pytest.approx(expected)

    def test_total_co2_tonnes_conversion(self):
        fp = CustomerCarbonFootprint(
            customer_id="C_IC1", year=2020,
            electricity_kwh=100_000.0,
            gas_kwh=50_000.0,
            electricity_intensity_g_per_kwh=225.0,
        )
        assert fp.total_co2_tonnes == pytest.approx(fp.total_co2_kg / 1000, rel=1e-3)

    def test_summary_keys(self):
        fp = CustomerCarbonFootprint("C1", 2021, 100000.0, 0.0, 220.0)
        s = fp.summary()
        assert "total_co2_tonnes" in s and "customer_id" in s


class TestBuildCustomerFootprint:
    def test_footprint_uses_fuel_mix_intensity(self):
        mix = FuelMixRecord(2022, coal_pct=2.0, gas_pct=38.0, nuclear_pct=17.0,
                            wind_pct=26.0, solar_pct=4.0, hydro_pct=2.0,
                            biomass_pct=8.0, imports_pct=3.0)
        fp = build_customer_footprint("C_IC1", 2022, 1_000_000.0, 100_000.0, mix)
        assert fp.electricity_intensity_g_per_kwh == pytest.approx(mix.emission_intensity_g_per_kwh)


class TestCarbonEmissionsBoardSection:
    def _make_data(self):
        return {
            "management_accounts": {
                "2020": {"income_statement": {"revenue_gbp": 1200000.0}},
                "2022": {"income_statement": {"revenue_gbp": 1600000.0}},
            }
        }

    def _render(self):
        from saas.reporting.annual_report import _section_carbon_emissions
        return _section_carbon_emissions(self._make_data())

    def test_section_renders(self):
        assert "Carbon Emissions" in self._render()

    def test_section_shows_years(self):
        out = self._render()
        assert "2020" in out and "2022" in out

    def test_section_shows_total(self):
        assert "Total" in self._render()

    def test_section_shows_low_carbon_pct(self):
        assert "%" in self._render()

    def test_section_shows_decarbonising_note(self):
        out = self._render()
        assert "decarbonising" in out or "declining" in out

    def test_section_empty_without_data(self):
        from saas.reporting.annual_report import _section_carbon_emissions
        assert _section_carbon_emissions({}) == ""
