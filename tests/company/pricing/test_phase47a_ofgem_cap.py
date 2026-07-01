"""Phase 47a: Ofgem domestic price cap — unit tests."""
import pytest
from company.pricing.ofgem_price_cap import get_cap_unit_rate_gbp_per_mwh


class TestGetCapUnitRate:
    def test_pre_2019_returns_none_electricity(self):
        assert get_cap_unit_rate_gbp_per_mwh("electricity", 2018) is None

    def test_pre_2019_returns_none_gas(self):
        assert get_cap_unit_rate_gbp_per_mwh("gas", 2016) is None

    def test_2022_electricity_cap_reflects_crisis(self):
        cap = get_cap_unit_rate_gbp_per_mwh("electricity", 2022)
        assert cap is not None
        # Crisis EPG cap was ~28-34p/kWh = £280-340/MWh; expect in that ballpark
        assert 270 <= cap <= 350

    def test_2022_gas_cap_reflects_crisis(self):
        cap = get_cap_unit_rate_gbp_per_mwh("gas", 2022)
        assert cap is not None
        assert 70 <= cap <= 130

    def test_2020_electricity_cap_below_typical_competitive_rate(self):
        # Pre-crisis cap: ~15-17p/kWh = £150-170/MWh
        cap = get_cap_unit_rate_gbp_per_mwh("electricity", 2020)
        assert 130 <= cap <= 200

    def test_cap_decreases_post_crisis(self):
        # 2024 cap should be lower than 2022 crisis cap
        assert get_cap_unit_rate_gbp_per_mwh("electricity", 2024) < get_cap_unit_rate_gbp_per_mwh("electricity", 2022)

    def test_unknown_fuel_returns_none(self):
        assert get_cap_unit_rate_gbp_per_mwh("oil", 2022) is None

    def test_future_year_returns_fallback(self):
        cap = get_cap_unit_rate_gbp_per_mwh("electricity", 2030)
        assert cap is not None
        assert cap > 0


class TestCapAppliedInSimulation:
    def test_resi_set_imported(self):
        from simulation.run_phase2b import _RESI_CUSTOMER_IDS
        assert "C1" in _RESI_CUSTOMER_IDS
        assert "C8" in _RESI_CUSTOMER_IDS
        assert "C1g" in _RESI_CUSTOMER_IDS

    def test_non_resi_not_in_set(self):
        from simulation.run_phase2b import _RESI_CUSTOMER_IDS
        assert "C_IC1" not in _RESI_CUSTOMER_IDS
        assert "C5" not in _RESI_CUSTOMER_IDS
        assert "C6" not in _RESI_CUSTOMER_IDS


# --- Phase LG depth tests ---

def test_elec_2019_exact():
    assert get_cap_unit_rate_gbp_per_mwh('electricity', 2019) == pytest.approx(165.0)


def test_elec_2020_exact():
    assert get_cap_unit_rate_gbp_per_mwh('electricity', 2020) == pytest.approx(157.0)


def test_elec_2021_above_2020():
    assert get_cap_unit_rate_gbp_per_mwh('electricity', 2021) > get_cap_unit_rate_gbp_per_mwh('electricity', 2020)


def test_elec_2023_between_2022_and_2024():
    cap22 = get_cap_unit_rate_gbp_per_mwh('electricity', 2022)
    cap23 = get_cap_unit_rate_gbp_per_mwh('electricity', 2023)
    cap24 = get_cap_unit_rate_gbp_per_mwh('electricity', 2024)
    assert cap22 > cap23 > cap24


def test_elec_2025_exact():
    assert get_cap_unit_rate_gbp_per_mwh('electricity', 2025) == pytest.approx(190.0)


def test_gas_2019_exact():
    assert get_cap_unit_rate_gbp_per_mwh('gas', 2019) == pytest.approx(26.0)


def test_gas_2020_below_2019():
    assert get_cap_unit_rate_gbp_per_mwh('gas', 2020) < get_cap_unit_rate_gbp_per_mwh('gas', 2019)


def test_gas_2021_above_2020():
    assert get_cap_unit_rate_gbp_per_mwh('gas', 2021) > get_cap_unit_rate_gbp_per_mwh('gas', 2020)


def test_gas_2023_exact():
    assert get_cap_unit_rate_gbp_per_mwh('gas', 2023) == pytest.approx(70.0)


def test_gas_2025_exact():
    assert get_cap_unit_rate_gbp_per_mwh('gas', 2025) == pytest.approx(52.0)
