import datetime as dt
import pytest
from company.market.dsr_portfolio import (
    DSREventType, CurtailmentStatus, DSREvent, CustomerCurtailment, DSRPortfolio
)


def _make_event(portfolio: DSRPortfolio) -> DSREvent:
    return portfolio.create_event(
        'DSR001', DSREventType.GRID_STRESS,
        dt.datetime(2022, 11, 15, 17, 0),
        dt.datetime(2022, 11, 15, 19, 0),
        target_mw=50.0, notice_minutes=60,
    )


def test_event_created():
    p = DSRPortfolio()
    ev = _make_event(p)
    assert ev.duration_hours == pytest.approx(2.0)
    assert ev.target_mwh == pytest.approx(100.0)
    assert not ev.is_short_notice


def test_short_notice():
    ev = DSREvent('DSR002', DSREventType.FREQUENCY_RESPONSE,
                  dt.datetime(2022, 11, 16, 8, 0),
                  dt.datetime(2022, 11, 16, 9, 0), 20.0, 15)
    assert ev.is_short_notice


def test_record_complied_curtailment():
    p = DSRPortfolio()
    _make_event(p)
    c = p.record_curtailment('IC001', 'DSR001', 500.0, 490.0, revenue_gbp=250.0)
    assert c.status == CurtailmentStatus.COMPLIED
    assert c.compliance_pct == pytest.approx(98.0)


def test_record_partial_curtailment():
    p = DSRPortfolio()
    _make_event(p)
    c = p.record_curtailment('IC002', 'DSR001', 500.0, 300.0)
    assert c.status == CurtailmentStatus.PARTIAL


def test_record_non_compliant():
    p = DSRPortfolio()
    _make_event(p)
    c = p.record_curtailment('IC003', 'DSR001', 500.0, 0.0)
    assert c.status == CurtailmentStatus.NON_COMPLIANT


def test_total_mwh_delivered():
    p = DSRPortfolio()
    _make_event(p)
    p.record_curtailment('IC001', 'DSR001', 500.0, 500.0)  # 0.5 MW * 2h = 1 MWh
    p.record_curtailment('IC002', 'DSR001', 1000.0, 1000.0)  # 1 MW * 2h = 2 MWh
    total = p.total_mwh_delivered('DSR001')
    assert total == pytest.approx(3.0, rel=0.01)


def test_compliance_rate():
    p = DSRPortfolio()
    _make_event(p)
    p.record_curtailment('IC001', 'DSR001', 500.0, 500.0)
    p.record_curtailment('IC002', 'DSR001', 500.0, 0.0)
    rate = p.compliance_rate_pct('DSR001')
    assert rate == pytest.approx(50.0)


def test_annual_revenue():
    p = DSRPortfolio()
    _make_event(p)
    p.record_curtailment('IC001', 'DSR001', 500.0, 500.0, revenue_gbp=500.0)
    assert p.annual_revenue_gbp(2022) == pytest.approx(500.0)


def test_dsr_summary():
    p = DSRPortfolio()
    _make_event(p)
    p.record_curtailment('IC001', 'DSR001', 500.0, 500.0, revenue_gbp=300.0)
    s = p.dsr_summary(2022)
    assert s['events'] == 1
    assert s['participating_customers'] == 1
    assert s['annual_revenue_gbp'] == pytest.approx(300.0)
