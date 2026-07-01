"""Tests for company/market/uig_allocation_register.py (Sprint CXLIX)."""
import datetime as dt

from company.market.uig_allocation_register import UIGAllocationRegister

JAN22 = dt.date(2022, 1, 1)


def _reg():
    return UIGAllocationRegister()


def test_record_id_starts_with_uig():
    reg = _reg()
    r = reg.record_allocation(JAN22, 1000.0, 10.0)
    assert r.record_id.startswith("UIG-")


def test_settlement_month_normalised_to_first():
    reg = _reg()
    r = reg.record_allocation(dt.date(2022, 1, 15), 1000.0, 10.0)
    assert r.settlement_month == dt.date(2022, 1, 1)


def test_total_throughput_stored():
    reg = _reg()
    r = reg.record_allocation(JAN22, 5000.0, 50.0)
    assert r.total_throughput_mwh == 5000.0


def test_uig_allocated_stored():
    reg = _reg()
    r = reg.record_allocation(JAN22, 5000.0, 50.0)
    assert r.uig_allocated_mwh == 50.0


def test_uig_rate_pct_computed():
    reg = _reg()
    r = reg.record_allocation(JAN22, 10000.0, 100.0)
    assert abs(r.uig_rate_pct - 1.0) < 0.001


def test_is_high_uig_false_below_2pct():
    reg = _reg()
    r = reg.record_allocation(JAN22, 10000.0, 100.0)
    assert r.is_high_uig is False


def test_is_high_uig_true_at_2pct():
    reg = _reg()
    r = reg.record_allocation(JAN22, 1000.0, 20.0)
    assert r.is_high_uig is True


def test_for_month_returns_correct_record():
    reg = _reg()
    reg.record_allocation(JAN22, 1000.0, 10.0)
    found = reg.for_month(2022, 1)
    assert found is not None
    assert found.uig_allocated_mwh == 10.0


def test_high_uig_periods_filters():
    reg = _reg()
    reg.record_allocation(JAN22, 10000.0, 50.0)
    reg.record_allocation(dt.date(2022, 2, 1), 10000.0, 250.0)
    high = reg.high_uig_periods()
    assert len(high) == 1
    assert high[0].settlement_month.month == 2


def test_average_uig_rate_pct_correct():
    reg = _reg()
    reg.record_allocation(JAN22, 1000.0, 10.0)
    reg.record_allocation(dt.date(2022, 2, 1), 1000.0, 20.0)
    avg = reg.average_uig_rate_pct()
    assert abs(avg - 1.5) < 0.01
