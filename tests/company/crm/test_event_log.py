"""Tests for company.crm.event_log - Phase 12a."""

import pytest

from company.crm.event_log import AcquisitionEvent, ChurnEvent, CompanyEventLog


def test_record_churn_stores_event():
    log = CompanyEventLog()
    ev = ChurnEvent(customer_id="C1", event_date="2018-01-01")
    log.record_churn(ev)
    assert len(log.churn_events()) == 1
    assert log.churn_events()[0].customer_id == "C1"


def test_record_acquisition_stores_event():
    log = CompanyEventLog()
    ev = AcquisitionEvent(customer_id="C2", event_date="2018-02-01")
    log.record_acquisition(ev)
    assert len(log.acquisition_events()) == 1
    assert log.acquisition_events()[0].customer_id == "C2"


def test_all_events_returns_insertion_order():
    log = CompanyEventLog()
    a = AcquisitionEvent(customer_id="C1", event_date="2016-01-01")
    b = ChurnEvent(customer_id="C1", event_date="2018-01-01")
    c = AcquisitionEvent(customer_id="C1_2", event_date="2018-02-01")
    log.record_acquisition(a)
    log.record_churn(b)
    log.record_acquisition(c)
    events = log.all_events()
    assert len(events) == 3
    assert events[0] is a
    assert events[1] is b
    assert events[2] is c


def test_active_accounts_acquisition_before_date_included():
    log = CompanyEventLog()
    log.record_acquisition(AcquisitionEvent(customer_id="C1", event_date="2016-01-01"))
    active = log.active_accounts("2020-12-31")
    assert "C1" in active


def test_active_accounts_churn_after_date_still_included():
    log = CompanyEventLog()
    log.record_acquisition(AcquisitionEvent(customer_id="C1", event_date="2016-01-01"))
    log.record_churn(ChurnEvent(customer_id="C1", event_date="2022-01-01"))
    active = log.active_accounts("2020-12-31")
    assert "C1" in active


def test_active_accounts_churn_before_date_excluded():
    log = CompanyEventLog()
    log.record_acquisition(AcquisitionEvent(customer_id="C1", event_date="2016-01-01"))
    log.record_churn(ChurnEvent(customer_id="C1", event_date="2018-01-01"))
    active = log.active_accounts("2020-12-31")
    assert "C1" not in active


def test_active_accounts_event_on_exact_date_included():
    log = CompanyEventLog()
    log.record_acquisition(AcquisitionEvent(customer_id="C1", event_date="2018-01-01"))
    active = log.active_accounts("2018-01-01")
    assert "C1" in active


def test_active_accounts_churn_on_exact_date_excluded():
    log = CompanyEventLog()
    log.record_acquisition(AcquisitionEvent(customer_id="C1", event_date="2016-01-01"))
    log.record_churn(ChurnEvent(customer_id="C1", event_date="2018-01-01"))
    active = log.active_accounts("2018-01-01")
    assert "C1" not in active


def test_as_dicts_churn_serialisation():
    log = CompanyEventLog()
    log.record_churn(ChurnEvent(
        customer_id="C3",
        event_date="2019-06-01",
        reason="non-renewal",
        sim_churn_probability=0.75,
        company_churn_estimate=0.50,
    ))
    dicts = log.as_dicts()
    assert len(dicts) == 1
    d = dicts[0]
    assert d["event_type"] == "churn"
    assert d["customer_id"] == "C3"
    assert d["event_date"] == "2019-06-01"
    assert d["reason"] == "non-renewal"
    assert d["sim_churn_probability"] == 0.75
    assert d["company_churn_estimate"] == 0.50


def test_as_dicts_acquisition_serialisation():
    log = CompanyEventLog()
    log.record_acquisition(AcquisitionEvent(
        customer_id="C3_succ",
        event_date="2019-07-01",
        channel="home-move-win",
        predecessor_id="C3",
    ))
    dicts = log.as_dicts()
    assert len(dicts) == 1
    d = dicts[0]
    assert d["event_type"] == "acquisition"
    assert d["customer_id"] == "C3_succ"
    assert d["event_date"] == "2019-07-01"
    assert d["channel"] == "home-move-win"
    assert d["predecessor_id"] == "C3"


def test_churn_events_filter():
    log = CompanyEventLog()
    log.record_acquisition(AcquisitionEvent(customer_id="C1", event_date="2016-01-01"))
    log.record_churn(ChurnEvent(customer_id="C1", event_date="2018-01-01"))
    log.record_acquisition(AcquisitionEvent(customer_id="C2", event_date="2017-01-01"))
    assert len(log.churn_events()) == 1
    assert log.churn_events()[0].customer_id == "C1"


def test_acquisition_events_filter():
    log = CompanyEventLog()
    log.record_acquisition(AcquisitionEvent(customer_id="C1", event_date="2016-01-01"))
    log.record_churn(ChurnEvent(customer_id="C1", event_date="2018-01-01"))
    log.record_acquisition(AcquisitionEvent(customer_id="C2", event_date="2017-01-01"))
    acqs = log.acquisition_events()
    assert len(acqs) == 2
    assert {a.customer_id for a in acqs} == {"C1", "C2"}


def test_empty_log_active_accounts_returns_empty_set():
    log = CompanyEventLog()
    assert log.active_accounts("2020-12-31") == set()


def test_multiple_churn_notifications_all_recorded():
    log = CompanyEventLog()
    log.record_churn(ChurnEvent(customer_id="C1", event_date="2018-01-01"))
    log.record_churn(ChurnEvent(customer_id="C2", event_date="2019-01-01"))
    log.record_churn(ChurnEvent(customer_id="C3", event_date="2020-01-01"))
    assert len(log.churn_events()) == 3


def test_record_retention_stores_event():
    from company.crm.event_log import RetentionEvent
    log = CompanyEventLog()
    ev = RetentionEvent(
        customer_id="C1",
        event_date="2021-01-01",
        company_churn_estimate=0.45,
        discount_pct=0.05,
        outcome="retained",
    )
    log.record_retention(ev)
    assert len(log.retention_events()) == 1
    assert log.retention_events()[0].customer_id == "C1"
    assert log.retention_events()[0].outcome == "retained"


def test_retention_events_filter_excludes_churn_and_acquisition():
    from company.crm.event_log import RetentionEvent
    log = CompanyEventLog()
    log.record_churn(ChurnEvent(customer_id="C2", event_date="2019-01-01"))
    log.record_acquisition(AcquisitionEvent(customer_id="C3", event_date="2020-01-01"))
    log.record_retention(RetentionEvent(
        customer_id="C2", event_date="2018-01-01",
        company_churn_estimate=0.4, discount_pct=0.05, outcome="churned_despite_offer",
    ))
    assert len(log.retention_events()) == 1
    assert len(log.churn_events()) == 1
    assert len(log.acquisition_events()) == 1


def test_as_dicts_includes_retention_event():
    from company.crm.event_log import RetentionEvent
    log = CompanyEventLog()
    log.record_retention(RetentionEvent(
        customer_id="C4",
        event_date="2022-06-30",
        company_churn_estimate=0.55,
        discount_pct=0.05,
        outcome="churned_despite_offer",
    ))
    dicts = log.as_dicts()
    assert len(dicts) == 1
    d = dicts[0]
    assert d["event_type"] == "retention"
    assert d["customer_id"] == "C4"
    assert d["event_date"] == "2022-06-30"
    assert abs(d["company_churn_estimate"] - 0.55) < 1e-6
    assert abs(d["discount_pct"] - 0.05) < 1e-6
    assert d["outcome"] == "churned_despite_offer"


def test_retention_event_not_in_active_accounts():
    from company.crm.event_log import RetentionEvent
    log = CompanyEventLog()
    log.record_acquisition(AcquisitionEvent(customer_id="C1", event_date="2016-01-01"))
    log.record_retention(RetentionEvent(
        customer_id="C1", event_date="2017-01-01",
        company_churn_estimate=0.35, discount_pct=0.05, outcome="retained",
    ))
    active = log.active_accounts("2020-12-31")
    assert "C1" in active
