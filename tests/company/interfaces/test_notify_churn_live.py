"""Tests for LiveSimInterface.notify_churn and notify_acquisition - Phase 12a."""

from company.crm.event_log import AcquisitionEvent, ChurnEvent
from company.interfaces.sim_interface import LiveSimInterface


def test_notify_churn_populates_event_log():
    iface = LiveSimInterface()
    iface.notify_churn("C1", "2018-01-01", reason="non-renewal",
                       sim_churn_probability=0.75, company_churn_estimate=0.50)
    events = iface.event_log.churn_events()
    assert len(events) == 1
    ev = events[0]
    assert ev.customer_id == "C1"
    assert ev.event_date == "2018-01-01"
    assert ev.reason == "non-renewal"
    assert ev.sim_churn_probability == 0.75
    assert ev.company_churn_estimate == 0.50


def test_notify_acquisition_populates_event_log():
    iface = LiveSimInterface()
    iface.notify_acquisition("C1_succ", "2018-02-01",
                             channel="home-move-win", predecessor_id="C1")
    events = iface.event_log.acquisition_events()
    assert len(events) == 1
    ev = events[0]
    assert ev.customer_id == "C1_succ"
    assert ev.event_date == "2018-02-01"
    assert ev.channel == "home-move-win"
    assert ev.predecessor_id == "C1"


def test_multiple_notifications_all_recorded():
    iface = LiveSimInterface()
    iface.notify_churn("C1", "2018-01-01")
    iface.notify_churn("C2", "2019-01-01")
    iface.notify_acquisition("C1_succ", "2018-02-01")
    assert len(iface.event_log.churn_events()) == 2
    assert len(iface.event_log.acquisition_events()) == 1
    assert len(iface.event_log.all_events()) == 3


def test_notify_churn_defaults():
    iface = LiveSimInterface()
    iface.notify_churn("C3", "2020-01-01")
    ev = iface.event_log.churn_events()[0]
    assert ev.reason == "non-renewal"
    assert ev.sim_churn_probability is None
    assert ev.company_churn_estimate is None


def test_notify_acquisition_defaults():
    iface = LiveSimInterface()
    iface.notify_acquisition("C3_new", "2020-02-01")
    ev = iface.event_log.acquisition_events()[0]
    assert ev.channel == "market-acquisition"
    assert ev.predecessor_id is None


def test_get_customer_status_returns_active_hardcoded():
    iface = LiveSimInterface()
    iface.notify_churn("C1", "2018-01-01")
    assert iface.get_customer_status("C1") == "active"
    assert iface.get_customer_status("unknown-account") == "active"
