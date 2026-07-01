"""Phase 50: Smart meter rollout wired into property model and acquisition — integration tests."""
import pytest
from saas.property_model import get_smart_meter_status, ASSET_PROFILE_BY_CUSTOMER
from saas.customers import make_acquired_customer


class TestGetSmartMeterStatus:
    def test_known_static_customer_uses_profile(self):
        # C1 has smart_meter=True in ASSET_PROFILE_BY_CUSTOMER
        assert get_smart_meter_status("C1", 2016, "resi") is True
        assert get_smart_meter_status("C1", 2020, "resi") is True  # unchanged by year

    def test_c3_no_smart_meter_is_static(self):
        # C3 has smart_meter=False in profile — year doesn't change it
        assert get_smart_meter_status("C3", 2016, "resi") is False
        assert get_smart_meter_status("C3", 2024, "resi") is False

    def test_acquired_customer_low_penetration_2016(self):
        # 2016 resi penetration = 10%; most acquired customers won't have smart meter
        results = [get_smart_meter_status(f"C1_A{i}", 2016, "resi") for i in range(100)]
        pct = sum(results) / len(results)
        assert 0.05 < pct < 0.20  # should be ~10% with sampling noise

    def test_acquired_customer_high_penetration_2024(self):
        # 2024 resi penetration = 72%; majority should have smart meter
        results = [get_smart_meter_status(f"C1_A{i}", 2024, "resi") for i in range(100)]
        pct = sum(results) / len(results)
        assert pct > 0.60  # majority have smart meters by 2024

    def test_monotonic_for_same_customer(self):
        # For the same acquired customer, having a smart meter in year Y means
        # they also have one in year Y+1 (penetration rate is monotonic).
        cid = "C1_acq_test"
        for year in range(2016, 2025):
            if get_smart_meter_status(cid, year, "resi"):
                # All later years must also return True (monotonic)
                assert all(get_smart_meter_status(cid, y, "resi") for y in range(year, 2026))
                break

    def test_ic_segment_always_has_smart_meter(self):
        # IC penetration = 100%, so any acquired IC customer has smart meter
        for cid in ("C_IC1_X1", "C_IC1_X2", "C_IC2_X3"):
            assert get_smart_meter_status(cid, 2016, "IC") is True

    def test_deterministic_same_customer_same_year(self):
        # Same input must always return same result
        for _ in range(5):
            assert get_smart_meter_status("C1_A42", 2020, "resi") == \
                   get_smart_meter_status("C1_A42", 2020, "resi")


class TestMakeAcquiredCustomerSmartMeter:
    def _predecessor(self, segment="resi"):
        return {
            "customer_id": "C1",
            "location": "London",
            "home_type": "urban_flat",
            "bedrooms": 2,
            "epc_rating": "C",
            "eac_kwh": 3200,
            "contract_type": "fixed_1yr",
            "segment": segment,
            "commodity": "electricity",
            "profile_class": "PC1",
        }

    def test_smart_meter_field_present(self):
        pred = self._predecessor()
        cust = make_acquired_customer("C1_A1", pred, "2020-03-01")
        assert "smart_meter" in cust

    def test_smart_meter_is_bool(self):
        pred = self._predecessor()
        cust = make_acquired_customer("C1_A1", pred, "2020-03-01")
        assert isinstance(cust["smart_meter"], bool)

    def test_ic_acquired_customer_always_has_smart_meter(self):
        pred = self._predecessor(segment="IC")
        cust = make_acquired_customer("C_IC1_A1", pred, "2018-01-01")
        assert cust["smart_meter"] is True

    def test_earlier_acquisition_lower_smart_meter_rate(self):
        pred = self._predecessor()
        # 2016 acquisitions: ~10% chance; 2024: ~72% chance
        results_2016 = [
            make_acquired_customer(f"C1_A{i}", pred, "2016-06-01")["smart_meter"]
            for i in range(80)
        ]
        results_2024 = [
            make_acquired_customer(f"C1_B{i}", pred, "2024-06-01")["smart_meter"]
            for i in range(80)
        ]
        pct_2016 = sum(results_2016) / len(results_2016)
        pct_2024 = sum(results_2024) / len(results_2024)
        assert pct_2024 > pct_2016



class TestSmartMeterConstants:
    def test_asset_profile_has_c1(self):
        assert "C1" in ASSET_PROFILE_BY_CUSTOMER

    def test_get_smart_meter_status_returns_bool(self):
        result = get_smart_meter_status("C1", 2020, "resi")
        assert isinstance(result, bool)

    def test_get_smart_meter_status_acquired_returns_bool(self):
        result = get_smart_meter_status("CNEW_99", 2020, "resi")
        assert isinstance(result, bool)
