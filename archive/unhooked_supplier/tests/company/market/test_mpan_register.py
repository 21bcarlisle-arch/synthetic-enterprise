import datetime as dt
import pytest
from company.market.mpan_register import (
    MPANStatus, ProfileClass, MPANRecord, MPANRegister
)


def _reg():
    reg = MPANRegister()
    reg.register('1200012345678', ProfileClass.PC1, 'A',
                 dt.date(2020, 4, 1), 'SUPPLIER_A')
    return reg


def test_register_mpan():
    reg = _reg()
    r = reg.get('1200012345678')
    assert r is not None
    assert r.status == MPANStatus.REGISTERED
    assert r.current_supplier_id == 'SUPPLIER_A'


def test_is_active_registered():
    reg = _reg()
    assert reg.get('1200012345678').is_active is True


def test_initiate_switch():
    reg = _reg()
    r = reg.initiate_switch('1200012345678', dt.date(2022, 6, 1))
    assert r.status == MPANStatus.PENDING_SWITCH
    assert r.pending_switch_date == dt.date(2022, 6, 1)


def test_complete_switch_changes_supplier():
    reg = _reg()
    reg.initiate_switch('1200012345678', dt.date(2022, 6, 1))
    r = reg.complete_switch('1200012345678', 'SUPPLIER_B', dt.date(2022, 6, 1))
    assert r.current_supplier_id == 'SUPPLIER_B'
    assert r.status == MPANStatus.REGISTERED


def test_object_to_switch():
    reg = _reg()
    reg.initiate_switch('1200012345678', dt.date(2022, 6, 1))
    r = reg.object_to_switch('1200012345678')
    assert r.status == MPANStatus.OBJECTED


def test_deregister():
    reg = _reg()
    r = reg.deregister('1200012345678', dt.date(2023, 1, 15))
    assert r.status == MPANStatus.DEREGISTERED
    assert r.is_active is False
    assert len(reg.active_mpans()) == 0


def test_pending_switches():
    reg = _reg()
    reg.register('1200099999', ProfileClass.PC2, 'A', dt.date(2020, 1, 1), 'SUPPLIER_A')
    reg.initiate_switch('1200099999', dt.date(2022, 8, 1))
    assert len(reg.pending_switches()) == 1


def test_pc1_description():
    reg = _reg()
    r = reg.get('1200012345678')
    assert 'Domestic' in r.profile_class_description


def test_portfolio_summary_keys():
    reg = _reg()
    s = reg.portfolio_summary()
    assert 'total_active' in s
    assert 'pending_switches' in s
    assert 'by_profile_class' in s
    assert s['total_active'] == 1


def test_get_returns_none_for_unknown():
    reg = _reg()
    assert reg.get('NONEXISTENT') is None


def test_deregistered_not_in_active_mpans():
    reg = _reg()
    reg.deregister('1200012345678', dt.date(2023, 1, 1))
    assert len(reg.active_mpans()) == 0


def test_by_profile_class_pc1():
    reg = MPANRegister()
    reg.register('MPAN_PC1', ProfileClass.PC1, 'A', dt.date(2020, 1, 1), 'SA')
    reg.register('MPAN_PC2', ProfileClass.PC2, 'A', dt.date(2020, 1, 1), 'SA')
    pc1 = reg.by_profile_class(ProfileClass.PC1)
    assert len(pc1) == 1
    assert pc1[0].mpan == 'MPAN_PC1'


def test_by_profile_class_excludes_deregistered():
    reg = MPANRegister()
    reg.register('MPAN_PC1', ProfileClass.PC1, 'A', dt.date(2020, 1, 1), 'SA')
    reg.deregister('MPAN_PC1', dt.date(2023, 1, 1))
    assert len(reg.by_profile_class(ProfileClass.PC1)) == 0


def test_pending_switch_still_active():
    reg = _reg()
    reg.initiate_switch('1200012345678', dt.date(2022, 6, 1))
    assert reg.get('1200012345678').is_active is True


def test_objected_is_active():
    reg = _reg()
    reg.object_to_switch('1200012345678')
    assert reg.get('1200012345678').is_active is True


def test_portfolio_summary_by_profile_class_count():
    reg = _reg()
    s = reg.portfolio_summary()
    assert s['by_profile_class']['PC1'] == 1
    assert s['by_profile_class']['PC2'] == 0


def test_measurement_class_stored():
    reg = MPANRegister()
    reg.register('MPAN_MC', ProfileClass.PC5, 'C', dt.date(2021, 6, 1), 'SA')
    r = reg.get('MPAN_MC')
    assert r.measurement_class == 'C'


def test_complete_switch_updates_registered_date():
    reg = _reg()
    switch_date = dt.date(2022, 8, 15)
    reg.initiate_switch('1200012345678', switch_date)
    r = reg.complete_switch('1200012345678', 'SUPPLIER_B', switch_date)
    assert r.registered_date == switch_date


def test_multiple_active_mpans():
    reg = MPANRegister()
    reg.register('MPAN_A', ProfileClass.PC1, 'A', dt.date(2020, 1, 1), 'SA')
    reg.register('MPAN_B', ProfileClass.PC3, 'C', dt.date(2021, 1, 1), 'SA')
    assert len(reg.active_mpans()) == 2
