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


# --- Phase KQ depth tests ---


class TestOfgemPriceCapDepth:
    def test_return_type_is_float(self):
        cap = get_cap_unit_rate_gbp_per_mwh("electricity", 2022)
        assert isinstance(cap, float)

    def test_2019_electricity_positive(self):
        assert get_cap_unit_rate_gbp_per_mwh("electricity", 2019) > 0.0

    def test_2019_gas_positive(self):
        assert get_cap_unit_rate_gbp_per_mwh("gas", 2019) > 0.0

    def test_2023_cap_exists(self):
        cap = get_cap_unit_rate_gbp_per_mwh("electricity", 2023)
        assert cap is not None

    def test_gas_cap_2023_exists(self):
        cap = get_cap_unit_rate_gbp_per_mwh("gas", 2023)
        assert cap is not None

    def test_electricity_cap_monotone_2019_to_2022(self):
        # 2022 was crisis peak, cap was higher than 2019
        assert get_cap_unit_rate_gbp_per_mwh("electricity", 2022) > get_cap_unit_rate_gbp_per_mwh("electricity", 2019)

    def test_gas_cap_2022_higher_than_2019(self):
        assert get_cap_unit_rate_gbp_per_mwh("gas", 2022) > get_cap_unit_rate_gbp_per_mwh("gas", 2019)

    def test_none_for_year_before_introduction(self):
        assert get_cap_unit_rate_gbp_per_mwh("electricity", 2017) is None

    def test_gas_none_before_2019(self):
        assert get_cap_unit_rate_gbp_per_mwh("gas", 2018) is None

    def test_fallback_year_returns_float(self):
        cap = get_cap_unit_rate_gbp_per_mwh("gas", 2035)
        assert isinstance(cap, float)
