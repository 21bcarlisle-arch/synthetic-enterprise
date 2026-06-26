import datetime as dt
import pytest
from company.crm.portal_analytics import PortalAction, PortalEvent, PortalAnalytics


def _analytics():
    pa = PortalAnalytics()
    pa.record('C001', PortalAction.LOGIN, dt.datetime(2022, 3, 1, 9, 0), 'S001')
    pa.record('C001', PortalAction.VIEW_BILL, dt.datetime(2022, 3, 1, 9, 2), 'S001')
    pa.record('C001', PortalAction.SUBMIT_METER_READ, dt.datetime(2022, 3, 1, 9, 5), 'S001')
    pa.record('C002', PortalAction.LOGIN, dt.datetime(2022, 3, 2, 10, 0), 'S002')
    pa.record('C002', PortalAction.CHANGE_DIRECT_DEBIT, dt.datetime(2022, 3, 2, 10, 5), 'S002')
    pa.record('C003', PortalAction.INITIATE_SWITCH, dt.datetime(2022, 3, 5, 14, 0), 'S003')
    return pa


def _period():
    return dt.datetime(2022, 3, 1), dt.datetime(2022, 3, 31, 23, 59, 59)


def test_record_event():
    pa = PortalAnalytics()
    ev = pa.record('C001', PortalAction.LOGIN, dt.datetime(2022, 3, 1, 9, 0), 'S001')
    assert ev.action == PortalAction.LOGIN
    assert ev.is_self_serve is False


def test_submit_meter_read_is_self_serve():
    pa = _analytics()
    evs = pa.events_in_period(*_period(), action=PortalAction.SUBMIT_METER_READ)
    assert evs[0].is_self_serve is True


def test_unique_users():
    pa = _analytics()
    assert pa.unique_users(*_period()) == 3


def test_self_serve_rate():
    pa = _analytics()
    rate = pa.self_serve_rate(*_period())
    assert rate is not None
    assert rate == pytest.approx(33.3, abs=0.1)


def test_action_counts():
    pa = _analytics()
    counts = pa.action_counts(*_period())
    assert counts.get('login') == 2
    assert counts.get('submit_meter_read') == 1


def test_monthly_summary_keys():
    pa = _analytics()
    s = pa.monthly_summary(2022, 3)
    assert 'total_events' in s
    assert 'unique_users' in s
    assert 'self_serve_rate_pct' in s
    assert 'action_counts' in s
    assert s['total_events'] == 6


def test_events_outside_period_excluded():
    pa = _analytics()
    from_dt = dt.datetime(2022, 4, 1)
    to_dt = dt.datetime(2022, 4, 30, 23, 59, 59)
    assert len(pa.events_in_period(from_dt, to_dt)) == 0
