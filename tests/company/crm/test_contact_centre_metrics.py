import datetime as dt
import pytest
from company.crm.contact_centre_metrics import (
    AgentPerformancePeriod, ContactCentreMetrics
)


def _agent(calls=100, handle_secs=400_000, fcr=72, esc=8, comp=3, csat=4.1):
    return AgentPerformancePeriod(
        agent_id='AGT001',
        period_start=dt.date(2022, 1, 1),
        period_end=dt.date(2022, 3, 31),
        calls_handled=calls,
        total_handle_time_seconds=handle_secs,
        first_contact_resolutions=fcr,
        escalations=esc,
        complaints_raised=comp,
        avg_csat=csat,
    )


def test_avg_handle_time():
    ap = _agent(calls=100, handle_secs=600_000)
    assert ap.avg_handle_time_seconds == pytest.approx(6_000.0)


def test_fcr_rate():
    ap = _agent(calls=100, fcr=72)
    assert ap.first_contact_resolution_rate == pytest.approx(72.0)


def test_escalation_rate():
    ap = _agent(calls=100, esc=8)
    assert ap.escalation_rate == pytest.approx(8.0)


def test_complaint_rate():
    ap = _agent(calls=100, comp=3)
    assert ap.complaint_rate == pytest.approx(3.0)


def test_zero_calls_returns_none():
    ap = _agent(calls=0, handle_secs=0, fcr=0, esc=0, comp=0, csat=None)
    assert ap.avg_handle_time_seconds is None
    assert ap.first_contact_resolution_rate is None


def _cc_metrics(calls=500, answered_sla=450, abandoned=25, handle=2_000_000, agents=15):
    return ContactCentreMetrics(
        period_start=dt.date(2022, 1, 1),
        period_end=dt.date(2022, 1, 31),
        total_calls=calls,
        answered_within_sla_seconds=answered_sla,
        abandoned_calls=abandoned,
        total_handle_time_seconds=handle,
        agents_on_duty=agents,
    )


def test_sla_answer_rate():
    cc = _cc_metrics(calls=500, answered_sla=450)
    assert cc.sla_answer_rate == pytest.approx(90.0)


def test_abandonment_rate():
    cc = _cc_metrics(calls=500, abandoned=25)
    assert cc.abandonment_rate == pytest.approx(4.8)


def test_calls_per_agent():
    cc = _cc_metrics(calls=500, agents=20)
    assert cc.calls_per_agent == pytest.approx(25.0)


def test_summary_keys():
    cc = _cc_metrics()
    s = cc.summary()
    assert 'abandonment_rate' in s
    assert 'sla_answer_rate' in s
    assert 'avg_handle_time_seconds' in s
    assert 'calls_per_agent' in s
