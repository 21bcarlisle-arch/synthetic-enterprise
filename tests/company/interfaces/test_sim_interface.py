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


def test_build_sim_interface_live_returns_live_interface():
    from company.interfaces.sim_interface import LiveSimInterface
    iface = build_sim_interface(live=True)
    assert isinstance(iface, LiveSimInterface)


def test_stub_interface_notify_retention_attempt_stores_notification():
    iface = StubSimInterface()
    iface.notify_retention_attempt("C1", "2021-01-01", 0.42, 0.05)
    assert len(iface.retention_notifications) == 1
    n = iface.retention_notifications[0]
    assert n["account_id"] == "C1"
    assert n["event_date"] == "2021-01-01"
    assert abs(n["company_churn_estimate"] - 0.42) < 1e-6
    assert abs(n["discount_pct"] - 0.05) < 1e-6
    assert n["outcome"] == "pending"


def test_stub_interface_notify_retention_attempt_with_outcome():
    iface = StubSimInterface()
    iface.notify_retention_attempt("C2", "2022-06-30", 0.55, 0.05, outcome="retained")
    assert iface.retention_notifications[0]["outcome"] == "retained"


def test_stub_interface_retention_notifications_returns_copy():
    iface = StubSimInterface()
    iface.notify_retention_attempt("C1", "2021-01-01", 0.3, 0.05)
    copy1 = iface.retention_notifications
    copy2 = iface.retention_notifications
    assert copy1 == copy2
    assert copy1 is not copy2


def test_live_interface_notify_retention_records_to_event_log():
    from company.crm.event_log import RetentionEvent
    from company.interfaces.sim_interface import LiveSimInterface
    iface = LiveSimInterface()
    iface.notify_retention_attempt("C3", "2021-12-30", 0.48, 0.05, outcome="churned_despite_offer")
    ret_events = iface.event_log.retention_events()
    assert len(ret_events) == 1
    assert ret_events[0].customer_id == "C3"
    assert ret_events[0].outcome == "churned_despite_offer"
