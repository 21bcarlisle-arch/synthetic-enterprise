"""Tests for company.interfaces.sim_interface."""

import pytest

from company.interfaces.sim_interface import (
    SimInterface,
    StubSimInterface,
    build_sim_interface,
)


def test_stub_interface_get_settlement_returns_stub_flag():
    iface = StubSimInterface()
    result = iface.get_settlement_data("1234567890123", "2016-01-01")
    assert result["_stub"] is True
    assert result["mpan"] == "1234567890123"


def test_stub_interface_get_forward_price_electricity():
    iface = StubSimInterface()
    assert iface.get_forward_price("electricity", "2016-01-01") == 120.0


def test_stub_interface_get_forward_price_gas():
    iface = StubSimInterface()
    assert iface.get_forward_price("gas", "2016-01-01") == 50.0


def test_stub_interface_get_customer_status_defaults_active():
    iface = StubSimInterface()
    assert iface.get_customer_status("C1") == "active"


def test_stub_interface_notify_churn_updates_status():
    iface = StubSimInterface()
    iface.notify_churn("C3", "2020-06-30")
    assert iface.get_customer_status("C3") == "churned"
    assert len(iface.churn_notifications) == 1
    assert iface.churn_notifications[0]["account_id"] == "C3"


def test_stub_interface_notify_acquisition_updates_status():
    iface = StubSimInterface()
    iface.notify_acquisition("C3_3", "2020-07-01")
    assert iface.get_customer_status("C3_3") == "active"
    assert len(iface.acquisition_notifications) == 1


def test_stub_churn_then_reactivation():
    iface = StubSimInterface()
    iface.notify_churn("C1", "2021-12-30")
    assert iface.get_customer_status("C1") == "churned"
    iface.notify_acquisition("C1_2", "2021-12-30")
    assert iface.get_customer_status("C1_2") == "active"


def test_base_interface_raises_not_implemented():
    iface = SimInterface()
    with pytest.raises(NotImplementedError):
        iface.get_settlement_data("mpan", "2016-01-01")
    with pytest.raises(NotImplementedError):
        iface.get_forward_price("electricity", "2016-01-01")
    with pytest.raises(NotImplementedError):
        iface.get_customer_status("C1")


def test_build_sim_interface_returns_stub():
    iface = build_sim_interface(live=False)
    assert isinstance(iface, StubSimInterface)


def test_build_sim_interface_live_raises():
    with pytest.raises(NotImplementedError, match="Live SimInterface"):
        build_sim_interface(live=True)
