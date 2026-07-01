"""Tests for Phase 54: supplier mutualization levy in policy_costs.py."""

import pytest
from simulation.policy_costs import get_mutualization_levy_per_mwh


class TestMutualizationLevy:
    def test_pre_crisis_years_zero(self):
        for year in ["2016", "2017", "2018", "2019", "2020"]:
            assert get_mutualization_levy_per_mwh(f"{year}-06-01") == 0.0

    def test_2021_nonzero(self):
        result = get_mutualization_levy_per_mwh("2021-01-01")
        assert result > 0.0
        assert result == pytest.approx(4.14)

    def test_2022_highest(self):
        r2021 = get_mutualization_levy_per_mwh("2021-06-15")
        r2022 = get_mutualization_levy_per_mwh("2022-06-15")
        assert r2022 > r2021

    def test_2022_value(self):
        assert get_mutualization_levy_per_mwh("2022-09-01") == pytest.approx(10.00)

    def test_2023_lower_than_2022(self):
        r2022 = get_mutualization_levy_per_mwh("2022-01-01")
        r2023 = get_mutualization_levy_per_mwh("2023-01-01")
        assert r2023 < r2022

    def test_future_year_falls_back_to_max(self):
        r2024 = get_mutualization_levy_per_mwh("2024-01-01")
        r2030 = get_mutualization_levy_per_mwh("2030-01-01")
        assert r2030 == pytest.approx(r2024)

    def test_past_year_falls_back_to_min(self):
        r2016 = get_mutualization_levy_per_mwh("2016-01-01")
        r2010 = get_mutualization_levy_per_mwh("2010-01-01")
        assert r2010 == pytest.approx(r2016)
        assert r2010 == pytest.approx(0.0)

    def test_date_format_works(self):
        # Full datetime string should work (only year matters)
        result = get_mutualization_levy_per_mwh("2022-03-15T16:00:00")
        assert result == pytest.approx(10.00)


from simulation.policy_costs import (
    get_ro_cost_per_mwh,
    get_cfd_levy_per_mwh,
    get_ccl_per_mwh,
    get_cm_levy_per_mwh,
    get_fit_levy_per_mwh,
    get_gas_ccl_per_mwh,
)


def test_ro_cost_positive_across_period():
    for year in ["2016", "2018", "2020", "2022", "2024"]:
        assert get_ro_cost_per_mwh(f"{year}-06-01") > 0.0


def test_ro_cost_rises_over_time():
    r2016 = get_ro_cost_per_mwh("2016-01-01")
    r2024 = get_ro_cost_per_mwh("2024-01-01")
    assert r2024 > r2016


def test_cfd_levy_positive_before_crisis():
    assert get_cfd_levy_per_mwh("2019-01-01") > 0.0


def test_cfd_levy_negative_during_crisis():
    assert get_cfd_levy_per_mwh("2022-06-01") < 0.0


def test_ccl_domestic_exempt():
    assert get_ccl_per_mwh("2022-01-01", "resi") == 0.0


def test_ccl_sme_pays():
    assert get_ccl_per_mwh("2022-01-01", "sme") > 0.0
