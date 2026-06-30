"""Tests for Carbon Intensity Register (Phase FD)."""
import datetime as dt
import pytest
from company.sustainability.carbon_intensity_register import (
    FuelSource, FuelMixSnapshot, CarbonIntensityRegister,
    _CARBON_INTENSITY_G_CO2_PER_KWH,
)


def make_snap(year=2023, gas_frac=0.4, wind_frac=0.4, solar_frac=0.2,
              kwh=1_000_000.0):
    mix = {
        FuelSource.NATURAL_GAS: gas_frac,
        FuelSource.WIND_OFFSHORE: wind_frac,
        FuelSource.SOLAR: solar_frac,
    }
    return FuelMixSnapshot(year=year, fuel_mix=mix, total_kwh_supplied=kwh)


class TestFuelMixSnapshot:
    def test_carbon_intensity(self):
        snap = make_snap(gas_frac=1.0, wind_frac=0.0, solar_frac=0.0)
        expected = _CARBON_INTENSITY_G_CO2_PER_KWH[FuelSource.NATURAL_GAS]
        assert snap.carbon_intensity_g_co2_per_kwh == pytest.approx(expected)

    def test_total_co2_tonnes(self):
        snap = make_snap(gas_frac=1.0, wind_frac=0.0, solar_frac=0.0, kwh=1_000_000)
        expected_tonnes = 1_000_000 * 394.0 / 1e6
        assert snap.total_co2_tonnes == pytest.approx(expected_tonnes)

    def test_renewables_fraction(self):
        snap = make_snap(gas_frac=0.5, wind_frac=0.3, solar_frac=0.2)
        assert snap.renewables_fraction == pytest.approx(0.5)

    def test_renewables_fraction_zero(self):
        snap = make_snap(gas_frac=1.0, wind_frac=0.0, solar_frac=0.0)
        assert snap.renewables_fraction == pytest.approx(0.0)

    def test_vs_grid_average_negative_means_cleaner(self):
        # 100% nuclear = 12 gCO2, grid avg 2023 = 196 -> negative = cleaner
        mix = {FuelSource.NUCLEAR: 1.0}
        snap = FuelMixSnapshot(year=2023, fuel_mix=mix, total_kwh_supplied=1e6)
        assert snap.vs_grid_average < 0

    def test_fuel_mix_summary(self):
        s = make_snap().fuel_mix_summary()
        assert "gCO2/kWh" in s
        assert "renewables=" in s


class TestCarbonIntensityRegister:
    def test_record_and_retrieve(self):
        reg = CarbonIntensityRegister()
        reg.record(make_snap(year=2022))
        assert reg.snapshot_for_year(2022) is not None

    def test_snapshot_for_missing_year(self):
        reg = CarbonIntensityRegister()
        assert reg.snapshot_for_year(2023) is None

    def test_intensity_trend_improving(self):
        reg = CarbonIntensityRegister()
        mix_dirty = {FuelSource.COAL: 1.0}
        mix_clean = {FuelSource.NUCLEAR: 1.0}
        reg.record(FuelMixSnapshot(2020, mix_dirty, 1e6))
        reg.record(FuelMixSnapshot(2023, mix_clean, 1e6))
        assert reg.intensity_trend() == "improving"

    def test_intensity_trend_insufficient(self):
        reg = CarbonIntensityRegister()
        assert reg.intensity_trend() == "insufficient_data"

    def test_total_co2(self):
        reg = CarbonIntensityRegister()
        reg.record(make_snap(gas_frac=1.0, wind_frac=0.0, solar_frac=0.0, kwh=1_000_000))
        assert reg.total_co2_tonnes_all_years() == pytest.approx(394.0)

    def test_avg_renewables(self):
        reg = CarbonIntensityRegister()
        reg.record(make_snap(gas_frac=0.5, wind_frac=0.5, solar_frac=0.0))
        assert reg.avg_renewables_fraction() == pytest.approx(0.5)

    def test_carbon_register_summary(self):
        reg = CarbonIntensityRegister()
        reg.record(make_snap())
        s = reg.carbon_register_summary()
        assert "Carbon Intensity Register" in s
