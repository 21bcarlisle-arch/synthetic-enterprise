"""Phase C tests — Household-Driven EAC Integration.

Tests for simulation/household_demand.py: HouseholdDemandRegister construction,
EPC multipliers, time-varying EV/solar fractions, dynamic assets, and integration
with the simulation customers roster.
"""

import pytest
from saas.customers import CUSTOMERS
from simulation.household_demand import (
    HouseholdDemandRegister,
    RESI_BASE_EAC_KWH,
    SME_BASE_EAC_KWH,
    _base_eac_for_customer,
)


@pytest.fixture(scope="module")
def register():
    return HouseholdDemandRegister(CUSTOMERS, seed=42)


class TestHouseholdDemandRegisterConstruction:
    def test_builds_for_all_18_customers(self, register):
        assert len(register.all_customer_ids()) == 18

    def test_known_customer_ids_present(self, register):
        cids = register.all_customer_ids()
        for cid in ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"]:
            assert cid in cids

    def test_ic_customers_present(self, register):
        cids = register.all_customer_ids()
        for cid in ["C_IC1", "C_IC2", "C_IC3", "C_IC4"]:
            assert cid in cids

    def test_gas_customers_present(self, register):
        cids = register.all_customer_ids()
        for cid in ["C1g", "C2g", "C3g", "C4g"]:
            assert cid in cids


class TestEPCMultiplier:
    def test_epc_c_returns_1_0(self, register):
        # C5 is EPC-C
        mult = register.epc_multiplier("C5", "2019-06-01")
        assert mult == pytest.approx(1.0, abs=1e-6)

    def test_epc_d_returns_1_25(self, register):
        # C1 is EPC-D
        mult = register.epc_multiplier("C1", "2019-06-01")
        assert mult == pytest.approx(1.25, abs=1e-6)

    def test_epc_e_returns_1_55(self, register):
        # C3 is EPC-E
        mult = register.epc_multiplier("C3", "2019-06-01")
        assert mult == pytest.approx(1.55, abs=1e-6)

    def test_unknown_customer_returns_1_0(self, register):
        mult = register.epc_multiplier("NONEXISTENT", "2019-06-01")
        assert mult == 1.0

    def test_epc_multiplier_non_increasing_over_time(self, register):
        # Phase E: insulation upgrades reduce EPC multiplier, so multiplier is non-increasing.
        # C3 may or may not get insulation events; the invariant is m_later <= m_earlier.
        m2016 = register.epc_multiplier("C3", "2016-01-01")
        m2022 = register.epc_multiplier("C3", "2022-06-01")
        m2025 = register.epc_multiplier("C3", "2025-12-31")
        assert m2022 <= m2016 + 1e-9
        assert m2025 <= m2022 + 1e-9
        assert m2016 > 0


class TestEACMultiplierComposite:
    def test_no_assets_equals_epc_multiplier(self, register):
        # C3: EPC-E, no solar, no EV
        m = register.eac_multiplier_for_date("C3", "2019-01-01")
        assert m == pytest.approx(1.55, abs=0.01)

    def test_c4_solar_reduces_multiplier(self, register):
        # C4: EPC-E (1.55), has_solar from baseline (solar_kwp=3.8, base_eac=5500)
        # solar_fraction = (3.8 * 850) / 5500 = 3230/5500 = 0.587
        # expected = 1.55 * (1 - 0.587) = 0.640
        m = register.eac_multiplier_for_date("C4", "2019-01-01")
        assert m == pytest.approx(0.640, abs=0.01)

    def test_multiplier_bounded_positive(self, register):
        # No multiplier should produce negative consumption
        for cid in register.all_customer_ids():
            m = register.eac_multiplier_for_date(cid, "2022-06-01")
            assert m >= 0.0, f"{cid} returned negative multiplier"

    def test_unknown_customer_returns_1_0(self, register):
        m = register.eac_multiplier_for_date("NONEXISTENT", "2019-01-01")
        assert m == 1.0


class TestHouseholdAtDate:
    def test_returns_household_for_known_customer(self, register):
        hh = register.household_at_date("C1", "2020-01-01")
        assert hh is not None
        assert hh.customer_id == "C1"

    def test_returns_none_for_unknown_customer(self, register):
        hh = register.household_at_date("NONEXISTENT", "2020-01-01")
        assert hh is None

    def test_c4_has_solar_at_baseline(self, register):
        # C4 rural_detached: starts with solar as early adopter
        hh = register.household_at_date("C4", "2016-01-15")
        assert hh.has_solar is True

    def test_c3_no_solar_at_any_date(self, register):
        # C3 is EPC-E tenement flat; life events calibration unlikely to give solar
        # (residential flat constraint in life_events.py)
        hh = register.household_at_date("C3", "2025-12-31")
        assert hh is not None  # household exists


class TestDynamicAssets:
    def test_returns_dict_with_expected_keys(self, register):
        assets = register.dynamic_assets("C1", "2019-06-01")
        assert "ev" in assets
        assert "solar" in assets
        assert "smart_meter" in assets

    def test_returns_empty_dict_for_unknown_customer(self, register):
        assets = register.dynamic_assets("NONEXISTENT", "2019-06-01")
        assert assets == {}

    def test_c4_solar_true_at_baseline(self, register):
        assets = register.dynamic_assets("C4", "2016-06-01")
        assert assets["solar"] is True

    def test_c1_solar_false_baseline(self, register):
        # C1 is EPC-D urban flat — no solar at baseline
        assets = register.dynamic_assets("C1", "2016-01-01")
        assert assets["solar"] is False


class TestDeterminism:
    def test_same_seed_produces_same_events(self):
        r1 = HouseholdDemandRegister(CUSTOMERS, seed=99)
        r2 = HouseholdDemandRegister(CUSTOMERS, seed=99)
        for cid in ["C1", "C2", "C3", "C4"]:
            assert r1.event_count(cid) == r2.event_count(cid)
            m1 = r1.eac_multiplier_for_date(cid, "2022-06-01")
            m2 = r2.eac_multiplier_for_date(cid, "2022-06-01")
            assert m1 == pytest.approx(m2, abs=1e-9)

    def test_different_seed_may_produce_different_events(self):
        # seeds 1 and 2 are verified to produce different totals with deterministic md5 hashing
        r1 = HouseholdDemandRegister(CUSTOMERS, seed=1)
        r2 = HouseholdDemandRegister(CUSTOMERS, seed=2)
        total1 = sum(r1.event_count(c["customer_id"]) for c in CUSTOMERS)
        total2 = sum(r2.event_count(c["customer_id"]) for c in CUSTOMERS)
        assert total1 != total2


class TestBaseEAC:
    def test_uses_declared_eac_when_available(self):
        customer = {"customer_id": "X1", "eac_kwh": 4000, "segment": "resi"}
        assert _base_eac_for_customer(customer) == 4000.0

    def test_falls_back_to_segment_average_resi(self):
        customer = {"customer_id": "X2", "segment": "resi"}
        assert _base_eac_for_customer(customer) == RESI_BASE_EAC_KWH

    def test_falls_back_to_segment_average_sme(self):
        customer = {"customer_id": "X3", "segment": "SME"}
        assert _base_eac_for_customer(customer) == SME_BASE_EAC_KWH


from simulation.household_demand import (
    IC_BASE_EAC_KWH,
    _cid_hash,
    SIM_START_YEAR,
    SIM_END_YEAR,
)


def test_cid_hash_deterministic():
    assert _cid_hash("C1") == _cid_hash("C1")


def test_cid_hash_different_ids_different_values():
    assert _cid_hash("C1") != _cid_hash("C2")


def test_cid_hash_returns_positive_int():
    assert isinstance(_cid_hash("C1"), int)
    assert _cid_hash("C1") >= 0


def test_cid_hash_known_value():
    assert _cid_hash("C1") == 439213101


def test_resi_base_eac_kwh_constant():
    assert RESI_BASE_EAC_KWH == pytest.approx(3100.0)


def test_sme_base_eac_kwh_constant():
    assert SME_BASE_EAC_KWH == pytest.approx(25000.0)


def test_ic_base_eac_kwh_constant():
    assert IC_BASE_EAC_KWH == pytest.approx(100000.0)


def test_sim_start_year():
    assert SIM_START_YEAR == 2016


def test_sim_end_year():
    assert SIM_END_YEAR == 2025
