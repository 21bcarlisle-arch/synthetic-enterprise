import datetime as dt
import pytest
from company.market.mprn_register import (
    GasConsumptionBand, classify_gas_band, MPRNStatus, MPRNRecord, MPRNRegister
)


def test_classify_domestic():
    assert classify_gas_band(12_000.0) == GasConsumptionBand.DOMESTIC


def test_classify_small_non_domestic():
    assert classify_gas_band(100_000.0) == GasConsumptionBand.SMALL_NON_DOMESTIC


def test_classify_large_non_domestic():
    assert classify_gas_band(1_000_000.0) == GasConsumptionBand.LARGE_NON_DOMESTIC


def _reg():
    reg = MPRNRegister()
    reg.register('7401234567890', 12_000.0, dt.date(2020, 4, 1), 'SUPPLIER_A')
    return reg


def test_register_mprn():
    reg = _reg()
    r = reg.get('7401234567890')
    assert r is not None
    assert r.status == MPRNStatus.REGISTERED
    assert r.consumption_band == GasConsumptionBand.DOMESTIC


def test_initiate_and_complete_switch():
    reg = _reg()
    reg.initiate_switch('7401234567890', dt.date(2022, 3, 1))
    r = reg.complete_switch('7401234567890', 'SUPPLIER_B', dt.date(2022, 3, 8))
    assert r.current_supplier_id == 'SUPPLIER_B'
    assert r.status == MPRNStatus.REGISTERED


def test_deregister():
    reg = _reg()
    r = reg.deregister('7401234567890', dt.date(2023, 1, 10))
    assert r.is_active is False
    assert len(reg.active_mprns()) == 0


def test_by_band():
    reg = MPRNRegister()
    reg.register('M001', 12_000.0, dt.date(2020, 1, 1), 'SA')
    reg.register('M002', 100_000.0, dt.date(2020, 1, 1), 'SA')
    reg.register('M003', 15_000.0, dt.date(2020, 1, 1), 'SA')
    domestic = reg.by_band(GasConsumptionBand.DOMESTIC)
    assert len(domestic) == 2


def test_portfolio_summary():
    reg = _reg()
    s = reg.portfolio_summary()
    assert s['total_active'] == 1
    assert s['total_aq_kwh'] == pytest.approx(12_000.0)
    assert 'by_band' in s


def test_is_active_pending_switch():
    reg = _reg()
    reg.initiate_switch('7401234567890', dt.date(2022, 3, 1))
    r = reg.get('7401234567890')
    assert r.is_active is True
