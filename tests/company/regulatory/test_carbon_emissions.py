import pytest
from company.regulatory.carbon_emissions import (
    FuelMixRecord, CustomerCarbonFootprint, build_customer_footprint
)


def _green_mix() -> FuelMixRecord:
    return FuelMixRecord(year=2024,
                         coal_pct=0.0, gas_pct=30.0, nuclear_pct=15.0,
                         wind_pct=35.0, solar_pct=10.0, hydro_pct=5.0,
                         biomass_pct=5.0, imports_pct=0.0)


def _coal_heavy_mix() -> FuelMixRecord:
    return FuelMixRecord(year=2016,
                         coal_pct=30.0, gas_pct=40.0, nuclear_pct=20.0,
                         wind_pct=5.0, solar_pct=2.0, hydro_pct=2.0,
                         biomass_pct=1.0, imports_pct=0.0)


def test_total_pct():
    mix = _green_mix()
    assert mix.total_pct == pytest.approx(100.0)


def test_renewable_pct():
    mix = _green_mix()
    assert mix.renewable_pct == pytest.approx(50.0)


def test_emission_intensity_green_lower():
    green = _green_mix()
    coal = _coal_heavy_mix()
    assert green.emission_intensity_g_per_kwh < coal.emission_intensity_g_per_kwh


def test_emission_intensity_coal_heavy():
    mix = _coal_heavy_mix()
    expected = (30*820 + 40*490 + 20*12 + 5*11 + 2*41 + 2*24 + 1*230 + 0*300) / 100
    assert mix.emission_intensity_g_per_kwh == pytest.approx(expected, rel=0.01)


def test_customer_electricity_co2():
    mix = _green_mix()
    fp = build_customer_footprint('C001', 2024, 3000.0, 0.0, mix)
    expected = 3000 * mix.emission_intensity_g_per_kwh / 1000
    assert fp.electricity_co2_kg == pytest.approx(expected, rel=0.01)


def test_customer_gas_co2():
    mix = _green_mix()
    fp = build_customer_footprint('C001', 2024, 0.0, 11000.0, mix)
    expected = 11000 * 183.0 / 1000
    assert fp.gas_co2_kg == pytest.approx(expected, rel=0.01)


def test_total_co2_tonnes():
    mix = _green_mix()
    fp = build_customer_footprint('C001', 2024, 3000.0, 11000.0, mix)
    assert fp.total_co2_tonnes == pytest.approx(fp.total_co2_kg / 1000, rel=0.01)


def test_summary_keys():
    mix = _green_mix()
    fp = build_customer_footprint('C001', 2024, 3000.0, 11000.0, mix)
    s = fp.summary()
    assert s['customer_id'] == 'C001'
    assert 'total_co2_tonnes' in s


# --- Phase KG depth tests ---

def test_low_carbon_pct_includes_nuclear_biomass():
    mix = _green_mix()
    # renewable(50) + nuclear(15) + biomass(5) = 70
    assert mix.low_carbon_pct == pytest.approx(70.0)


def test_zero_gas_kwh_gives_zero_gas_co2():
    mix = _green_mix()
    fp = build_customer_footprint('C001', 2024, 3000.0, 0.0, mix)
    assert fp.gas_co2_kg == pytest.approx(0.0)


def test_zero_electricity_kwh_gives_zero_elec_co2():
    mix = _green_mix()
    fp = build_customer_footprint('C001', 2024, 0.0, 11000.0, mix)
    assert fp.electricity_co2_kg == pytest.approx(0.0)


def test_gas_emission_factor_183():
    mix = _green_mix()
    fp = build_customer_footprint('C001', 2024, 0.0, 1000.0, mix)
    assert fp.gas_co2_kg == pytest.approx(183.0)


def test_summary_year_stored():
    mix = _green_mix()
    fp = build_customer_footprint('C001', 2024, 3000.0, 0.0, mix)
    assert fp.summary()['year'] == 2024


def test_electricity_intensity_stored_in_footprint():
    mix = _green_mix()
    fp = build_customer_footprint('C001', 2024, 3000.0, 0.0, mix)
    assert fp.electricity_intensity_g_per_kwh == pytest.approx(mix.emission_intensity_g_per_kwh)


def test_all_nuclear_intensity():
    mix = FuelMixRecord(year=2024, coal_pct=0.0, gas_pct=0.0, nuclear_pct=100.0,
                        wind_pct=0.0, solar_pct=0.0, hydro_pct=0.0,
                        biomass_pct=0.0, imports_pct=0.0)
    assert mix.emission_intensity_g_per_kwh == pytest.approx(12.0)


def test_all_wind_intensity():
    mix = FuelMixRecord(year=2024, coal_pct=0.0, gas_pct=0.0, nuclear_pct=0.0,
                        wind_pct=100.0, solar_pct=0.0, hydro_pct=0.0,
                        biomass_pct=0.0, imports_pct=0.0)
    assert mix.emission_intensity_g_per_kwh == pytest.approx(11.0)


def test_total_co2_kg_sum_of_components():
    mix = _green_mix()
    fp = build_customer_footprint('C001', 2024, 3000.0, 5000.0, mix)
    assert fp.total_co2_kg == pytest.approx(fp.electricity_co2_kg + fp.gas_co2_kg)


def test_summary_co2_kg_present():
    mix = _green_mix()
    fp = build_customer_footprint('C001', 2024, 3000.0, 11000.0, mix)
    s = fp.summary()
    assert 'electricity_co2_kg' in s
    assert 'gas_co2_kg' in s
    assert 'total_co2_kg' in s
