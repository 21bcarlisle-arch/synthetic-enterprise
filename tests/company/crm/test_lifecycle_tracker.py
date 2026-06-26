import datetime as dt
import pytest
from company.crm.lifecycle_tracker import (
    LifecycleStage, LifecycleEvent, CustomerLifecycle, CustomerLifecycleTracker
)


def test_register_and_initial_stage():
    t = CustomerLifecycleTracker()
    lc = t.register('C001', dt.date(2022, 1, 1))
    assert lc.stage == LifecycleStage.PENDING_SWITCH
    assert lc.is_on_supply
    assert not lc.is_active_customer


def test_transition_active():
    t = CustomerLifecycleTracker()
    lc = t.register('C001', dt.date(2022, 1, 1))
    t.transition('C001', LifecycleStage.ACTIVE, dt.date(2022, 1, 21), 'switch completed')
    assert lc.stage == LifecycleStage.ACTIVE
    assert lc.is_active_customer


def test_transition_in_arrears():
    t = CustomerLifecycleTracker()
    t.register('C001', dt.date(2022, 1, 1))
    t.transition('C001', LifecycleStage.ACTIVE, dt.date(2022, 1, 21), 'switch')
    t.transition('C001', LifecycleStage.IN_ARREARS, dt.date(2022, 3, 1), 'DD failed')
    assert t.get('C001').stage == LifecycleStage.IN_ARREARS
    assert t.get('C001').is_active_customer


def test_churn_not_on_supply():
    t = CustomerLifecycleTracker()
    t.register('C001', dt.date(2022, 1, 1))
    t.transition('C001', LifecycleStage.ACTIVE, dt.date(2022, 1, 21), 'switch')
    t.transition('C001', LifecycleStage.CHURNED, dt.date(2022, 12, 1), 'switched away')
    assert not t.get('C001').is_on_supply
    assert not t.get('C001').is_active_customer


def test_tenure_days():
    t = CustomerLifecycleTracker()
    t.register('C001', dt.date(2022, 1, 1))
    assert t.get('C001').tenure_days(dt.date(2023, 1, 1)) == 365


def test_customers_in_stage():
    t = CustomerLifecycleTracker()
    t.register('C001', dt.date(2022, 1, 1))
    t.register('C002', dt.date(2022, 1, 1))
    t.transition('C001', LifecycleStage.ACTIVE, dt.date(2022, 1, 21), 'switch')
    active = t.customers_in_stage(LifecycleStage.ACTIVE)
    pending = t.customers_in_stage(LifecycleStage.PENDING_SWITCH)
    assert active == ['C001']
    assert pending == ['C002']


def test_stage_history():
    t = CustomerLifecycleTracker()
    t.register('C001', dt.date(2022, 1, 1))
    t.transition('C001', LifecycleStage.ACTIVE, dt.date(2022, 1, 21), 'switch')
    t.transition('C001', LifecycleStage.AT_RISK, dt.date(2022, 6, 1), 'missed payment')
    history = t.get('C001').stage_history()
    assert len(history) == 2
    assert history[0].to_stage == LifecycleStage.ACTIVE
    assert history[1].from_stage == LifecycleStage.ACTIVE


def test_portfolio_summary():
    t = CustomerLifecycleTracker()
    t.register('C001', dt.date(2022, 1, 1))
    t.register('C002', dt.date(2022, 1, 1))
    t.register('C003', dt.date(2022, 1, 1))
    t.transition('C001', LifecycleStage.ACTIVE, dt.date(2022, 1, 21), 'switch')
    t.transition('C002', LifecycleStage.ACTIVE, dt.date(2022, 1, 21), 'switch')
    t.transition('C002', LifecycleStage.CHURNED, dt.date(2022, 12, 1), 'left')
    s = t.portfolio_summary(dt.date(2022, 12, 31))
    assert s['total'] == 3
    assert s['on_supply'] == 2
    assert s['by_stage']['churned'] == 1
    assert s['by_stage']['active'] == 1
