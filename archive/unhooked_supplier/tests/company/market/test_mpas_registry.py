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


def test_get_not_found():
    r = _make_reg()
    assert r.get('NONEXISTENT') is None


def test_losing_supplier_stored():
    r = _make_reg()
    sp = r.get('MPAN001')
    assert sp.losing_supplier == 'OldSupplier'


def test_objected_points():
    r = _make_reg()
    r.get('MPAN001').raise_objection('In contract')
    assert len(r.objected_points()) == 1
    assert r.objected_points()[0].supply_point_id == 'MPAN001'


def test_objection_not_in_active():
    r = _make_reg()
    r.get('MPAN001').raise_objection('In contract')
    active = r.active_supply_points()
    ids = [sp.supply_point_id for sp in active]
    assert 'MPAN001' not in ids


def test_complete_transfer_removes_from_active():
    r = _make_reg()
    r.get('MPAN001').complete_transfer(dt.date(2022, 2, 1))
    active = r.active_supply_points()
    assert all(sp.supply_point_id != 'MPAN001' for sp in active)


def test_active_supply_points_no_filter():
    r = _make_reg()
    all_active = r.active_supply_points()
    assert len(all_active) == 2


def test_total_mwh_no_filter():
    r = _make_reg()
    total = r.total_registered_mwh()
    assert total == pytest.approx(3.5 + 15.0)


def test_registrations_in_period():
    r = _make_reg()
    results = r.registrations_in_period(dt.date(2022, 1, 1), dt.date(2022, 1, 3))
    assert len(results) == 1
    assert results[0].supply_point_id == 'MPAN001'


def test_mpas_summary_objected_count():
    r = _make_reg()
    r.get('MPAN001').raise_objection('reason')
    s = r.mpas_summary()
    assert s['objected'] == 1
    assert s['total_registered'] == 1


def test_mpas_summary_mwh_values():
    r = _make_reg()
    s = r.mpas_summary()
    assert s['total_electricity_mwh'] == pytest.approx(3.5)
    assert s['total_gas_mwh'] == pytest.approx(15.0)
