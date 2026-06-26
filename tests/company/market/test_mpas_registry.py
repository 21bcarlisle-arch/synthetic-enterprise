import datetime as dt
import pytest
from company.market.mpas_registry import (
    Commodity, RegistrationStatus, SupplyPoint, MPASRegistry
)


def _make_reg() -> MPASRegistry:
    r = MPASRegistry()
    r.register('MPAN001', Commodity.ELECTRICITY, 'C001', dt.date(2022, 1, 1), 3500.0, 'OldSupplier')
    r.register('MPRN001', Commodity.GAS, 'C001', dt.date(2022, 1, 5), 15000.0)
    return r


def test_registration_active():
    r = _make_reg()
    sp = r.get('MPAN001')
    assert sp is not None
    assert sp.is_active


def test_annual_mwh():
    r = _make_reg()
    sp = r.get('MPAN001')
    assert sp.annual_mwh == pytest.approx(3.5)


def test_objection_changes_status():
    r = _make_reg()
    sp = r.get('MPAN001')
    sp.raise_objection('Customer still in contract')
    assert sp.status == RegistrationStatus.OBJECTED
    assert not sp.is_active


def test_resolve_objection_allow():
    r = _make_reg()
    sp = r.get('MPAN001')
    sp.raise_objection('reason')
    sp.resolve_objection(allow_transfer=True)
    assert sp.status == RegistrationStatus.IN_TRANSFER


def test_resolve_objection_deny():
    r = _make_reg()
    sp = r.get('MPAN001')
    sp.raise_objection('reason')
    sp.resolve_objection(allow_transfer=False)
    assert sp.status == RegistrationStatus.WITHDRAWN


def test_complete_transfer():
    r = _make_reg()
    sp = r.get('MPAN001')
    sp.complete_transfer(dt.date(2022, 2, 1))
    assert sp.status == RegistrationStatus.LOST
    assert sp.transfer_effective_date == dt.date(2022, 2, 1)


def test_active_supply_points_filter():
    r = _make_reg()
    elec = r.active_supply_points(Commodity.ELECTRICITY)
    assert len(elec) == 1
    assert elec[0].supply_point_id == 'MPAN001'


def test_total_mwh():
    r = _make_reg()
    assert r.total_registered_mwh(Commodity.ELECTRICITY) == pytest.approx(3.5)
    assert r.total_registered_mwh(Commodity.GAS) == pytest.approx(15.0)


def test_mpas_summary():
    r = _make_reg()
    s = r.mpas_summary()
    assert s['total_registered'] == 2
    assert s['electricity_points'] == 1
    assert s['gas_points'] == 1
    assert s['objected'] == 0
