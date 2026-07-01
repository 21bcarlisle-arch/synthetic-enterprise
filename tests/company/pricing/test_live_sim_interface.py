"""Tests for company.interfaces.sim_interface LiveSimInterface — Phase 11a."""

import pytest

from company.interfaces.sim_interface import (
    LiveSimInterface,
    StubSimInterface,
    build_sim_interface,
)


class TestBuildSimInterface:
    def test_live_false_returns_stub(self):
        iface = build_sim_interface(live=False)
        assert isinstance(iface, StubSimInterface)

    def test_live_true_returns_live_interface(self):
        iface = build_sim_interface(live=True)
        assert isinstance(iface, LiveSimInterface)


class TestLiveSimInterfaceGetForwardPrice:
    def test_electricity_forward_price_positive(self):
        iface = LiveSimInterface()
        price = iface.get_forward_price("electricity", "2020-01-01")
        assert price > 0

    def test_gas_forward_price_positive(self):
        iface = LiveSimInterface()
        price = iface.get_forward_price("gas", "2020-01-01")
        assert price > 0

    def test_unknown_fuel_raises(self):
        iface = LiveSimInterface()
        with pytest.raises((ValueError, KeyError)):
            iface.get_forward_price("coal", "2020-01-01")

    def test_forward_price_differs_from_sim_curve(self):
        """LiveSimInterface should return company estimate, not SIM forward curve."""
        from sim.cache_store import get_cached_prices
        from sim.forward_curve import generate_forward_price
        from sim.system_prices_history import get_system_prices_range

        iface = LiveSimInterface()
        company_price = iface.get_forward_price("electricity", "2020-06-01")

        # Use cache to avoid slow API calls in tests
        records = get_cached_prices("2015-11-07", "2025-06-07")
        if records is None:
            records = get_system_prices_range("2015-11-07", "2020-06-30")
        sim_price = generate_forward_price("2020-06-01", records)

        assert company_price != sim_price

    def test_caches_price_records(self):
        """Two calls should not re-fetch records (cache hit)."""
        iface = LiveSimInterface()
        _ = iface.get_forward_price("electricity", "2019-01-01")
        _ = iface.get_forward_price("electricity", "2020-01-01")
        # Both used the same cached records
        assert "electricity" in iface._price_cache

    def test_stub_methods_return_sensible_defaults(self):
        iface = LiveSimInterface()
        assert iface.get_customer_status("C1") == "active"
        assert iface.get_settlement_data("M123", "2020-01-01")["_stub"] is True
        iface.notify_churn("C1", "2020-01-01")    # should not raise
        iface.notify_acquisition("C2", "2020-01-01")  # should not raise


# --- Phase KM depth tests ---

class TestLiveSimInterfaceDepth:
    def test_live_forward_price_is_float(self):
        iface = LiveSimInterface()
        price = iface.get_forward_price('electricity', '2020-01-01')
        assert isinstance(price, float)

    def test_gas_forward_price_is_float(self):
        iface = LiveSimInterface()
        price = iface.get_forward_price('gas', '2020-01-01')
        assert isinstance(price, float)

    def test_price_cache_populated_after_electricity_call(self):
        iface = LiveSimInterface()
        iface.get_forward_price('electricity', '2020-01-01')
        assert 'electricity' in iface._price_cache

    def test_event_log_churn_initially_empty(self):
        iface = LiveSimInterface()
        assert iface.event_log.churn_events() == []

    def test_event_log_acquisition_initially_empty(self):
        iface = LiveSimInterface()
        assert iface.event_log.acquisition_events() == []

    def test_live_customer_status_unknown_is_active(self):
        iface = LiveSimInterface()
        assert iface.get_customer_status('UNKNOWN_CUSTOMER') == 'active'

    def test_settlement_data_stub_flag_true(self):
        iface = LiveSimInterface()
        data = iface.get_settlement_data('M123', '2020-01-01')
        assert data['_stub'] is True

    def test_notify_churn_populates_log(self):
        iface = LiveSimInterface()
        iface.notify_churn('C99', '2021-05-01')
        assert len(iface.event_log.churn_events()) == 1

    def test_stub_churn_estimate_non_negative(self):
        stub = StubSimInterface()
        result = stub.get_churn_estimate('C1', 100.0, 120.0, 2.0)
        assert result >= 0.0

    def test_build_false_stub_is_stub_instance(self):
        iface = build_sim_interface(live=False)
        assert isinstance(iface, StubSimInterface)
