"""Phase 51: ToU eligibility gate — unit tests."""
from saas.smart_meter_rollout import is_tou_eligible


class TestIsTouEligible:
    def test_hh_metered_customer_always_eligible(self):
        assert is_tou_eligible({"metering": "HH"}) is True

    def test_nhh_metered_no_smart_meter_not_eligible(self):
        assert is_tou_eligible({"metering": "NHH", "smart_meter": False}) is False

    def test_nhh_metered_with_smart_meter_eligible(self):
        # Phase 51: acquired customers with smart_meter=True get ToU pricing
        assert is_tou_eligible({"metering": "NHH", "smart_meter": True}) is True

    def test_no_metering_field_with_smart_meter_eligible(self):
        # make_acquired_customer doesn't set metering field, only smart_meter
        assert is_tou_eligible({"smart_meter": True}) is True

    def test_no_metering_no_smart_meter_not_eligible(self):
        assert is_tou_eligible({}) is False
        assert is_tou_eligible({"smart_meter": False}) is False

    def test_ic_customers_eligible_via_hh_metering(self):
        assert is_tou_eligible({"metering": "HH", "segment": "IC"}) is True

    def test_none_smart_meter_not_eligible(self):
        # smart_meter field absent or None → not eligible
        assert is_tou_eligible({"metering": "NHH"}) is False

    def test_acquired_customer_structure(self):
        # Simulate what make_acquired_customer produces for a smart-meter customer
        acquired = {
            "customer_id": "C1_A1",
            "acquisition_type": "fresh_market",
            "segment": "resi",
            "smart_meter": True,
        }
        assert is_tou_eligible(acquired) is True

    def test_acquired_customer_no_smart_meter(self):
        acquired = {
            "customer_id": "C1_A2",
            "acquisition_type": "fresh_market",
            "segment": "resi",
            "smart_meter": False,
        }
        assert is_tou_eligible(acquired) is False
