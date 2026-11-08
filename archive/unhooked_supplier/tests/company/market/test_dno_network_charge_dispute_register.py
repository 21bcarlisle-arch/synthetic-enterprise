"""Tests for company/market/dno_network_charge_dispute_register.py (Sprint CLII)."""
import datetime as dt
import pytest

from company.market.dno_network_charge_dispute_register import (
    DNONetworkChargeDisputeRegister,
    DUoSDisputeGround,
    DUoSDisputeStatus,
)

DATE = dt.date(2022, 6, 1)


def _reg():
    return DNONetworkChargeDisputeRegister()


def _dispute(reg):
    return reg.raise_dispute("M1", "LPN", "INV-001", DATE, DUoSDisputeGround.WRONG_LLFC, 500.0)


def test_dispute_id_starts_with_duos_disp():
    reg = _reg()
    r = _dispute(reg)
    assert r.dispute_id.startswith("DUOS-DISP-")


def test_mpan_stored():
    reg = _reg()
    r = _dispute(reg)
    assert r.mpan == "M1"


def test_disputed_amount_stored():
    reg = _reg()
    r = _dispute(reg)
    assert r.disputed_amount_gbp == 500.0


def test_is_open_when_raised():
    reg = _reg()
    r = _dispute(reg)
    assert r.is_open is True


def test_dno_response_due_28_days():
    reg = _reg()
    r = _dispute(reg)
    assert r.dno_response_due == DATE + dt.timedelta(days=28)


def test_acknowledge_updates_status():
    reg = _reg()
    r = _dispute(reg)
    a = reg.acknowledge(r.dispute_id, DATE)
    assert a.status == DUoSDisputeStatus.ACKNOWLEDGED


def test_resolve_with_credit_updates_status():
    reg = _reg()
    r = _dispute(reg)
    c = reg.resolve_with_credit(r.dispute_id, 500.0, DATE)
    assert c.status == DUoSDisputeStatus.RESOLVED_CREDIT


def test_zero_disputed_amount_raises():
    reg = _reg()
    with pytest.raises(ValueError):
        reg.raise_dispute("M1", "LPN", "INV-001", DATE, DUoSDisputeGround.WRONG_LLFC, 0.0)


def test_total_open_disputed_sums():
    reg = _reg()
    reg.raise_dispute("M1", "LPN", "INV-001", DATE, DUoSDisputeGround.WRONG_LLFC, 300.0)
    reg.raise_dispute("M2", "LPN", "INV-002", DATE, DUoSDisputeGround.CALCULATION_ERROR, 200.0)
    assert abs(reg.total_open_disputed_gbp() - 500.0) < 0.01


def test_success_rate_none_when_no_terminal():
    reg = _reg()
    _dispute(reg)
    assert reg.success_rate_pct() is None
