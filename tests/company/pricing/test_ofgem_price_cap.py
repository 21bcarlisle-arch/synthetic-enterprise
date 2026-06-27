import pytest
from company.pricing.ofgem_price_cap import get_cap_unit_rate_gbp_per_mwh


class TestGetCapUnitRateGbpPerMwh:
    def test_none_before_2019(self):
        assert get_cap_unit_rate_gbp_per_mwh("electricity", 2018) is None
        assert get_cap_unit_rate_gbp_per_mwh("gas", 2016) is None

    def test_electricity_cap_2022(self):
        cap = get_cap_unit_rate_gbp_per_mwh("electricity", 2022)
        assert cap is not None
        assert cap > 200.0  # crisis year, high cap

    def test_gas_cap_2022(self):
        cap = get_cap_unit_rate_gbp_per_mwh("gas", 2022)
        assert cap is not None
        assert cap > 60.0  # crisis year

    def test_electricity_cap_greater_than_gas(self):
        # Electricity cap (£/MWh) is higher than gas cap in all years
        for year in range(2019, 2026):
            elec = get_cap_unit_rate_gbp_per_mwh("electricity", year)
            gas = get_cap_unit_rate_gbp_per_mwh("gas", year)
            assert elec > gas, f"Expected elec > gas in {year}"

    def test_2022_caps_higher_than_2020(self):
        elec_22 = get_cap_unit_rate_gbp_per_mwh("electricity", 2022)
        elec_20 = get_cap_unit_rate_gbp_per_mwh("electricity", 2020)
        assert elec_22 > elec_20

    def test_unknown_fuel_returns_none(self):
        result = get_cap_unit_rate_gbp_per_mwh("oil", 2022)
        assert result is None

    def test_fallback_for_future_year(self):
        cap = get_cap_unit_rate_gbp_per_mwh("electricity", 2030)
        assert cap is not None
        assert isinstance(cap, float)

    def test_2019_introduction_not_none(self):
        assert get_cap_unit_rate_gbp_per_mwh("electricity", 2019) is not None
