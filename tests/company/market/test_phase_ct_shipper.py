"""Phase CT: Shipper Code Register tests (Xoserve UK Link)."""
import pytest
from datetime import date
from company.market.shipper_code_register import (
    ShipperCodeRegister, ShipperRecord, ShipperStatus, LDZ
)

_REG_DATE = date(2016, 1, 1)


def _reg_with_shipper(code="SE", name="SyntheticEnergy"):
    r = ShipperCodeRegister()
    rec = r.register(code, name, _REG_DATE)
    return r, rec


# 1. register creates ACTIVE shipper
def test_register_active():
    r, rec = _reg_with_shipper()
    assert rec.status == ShipperStatus.ACTIVE
    assert rec.shipper_code == "SE"


# 2. get returns the record
def test_get():
    r, rec = _reg_with_shipper()
    assert r.get("SE") is rec


# 3. get missing returns None
def test_get_missing():
    r = ShipperCodeRegister()
    assert r.get("XX") is None


# 4. add_ldz grants authorisation
def test_add_ldz():
    r, rec = _reg_with_shipper()
    rec.add_ldz(LDZ.EA, date(2016, 1, 1))
    assert LDZ.EA in rec.active_ldz_codes


# 5. duplicate add_ldz is idempotent
def test_add_ldz_idempotent():
    r, rec = _reg_with_shipper()
    rec.add_ldz(LDZ.EA, date(2016, 1, 1))
    rec.add_ldz(LDZ.EA, date(2016, 1, 1))
    assert rec.ldz_coverage_count == 1


# 6. revoke_ldz deactivates
def test_revoke_ldz():
    r, rec = _reg_with_shipper()
    rec.add_ldz(LDZ.EA, date(2016, 1, 1))
    rec.revoke_ldz(LDZ.EA)
    assert LDZ.EA not in rec.active_ldz_codes


# 7. can_supply_in True when active + authorised
def test_can_supply_active():
    r, rec = _reg_with_shipper()
    rec.add_ldz(LDZ.NW, date(2016, 1, 1))
    assert rec.can_supply_in(LDZ.NW)


# 8. can_supply_in False when LDZ not authorised
def test_can_supply_no_ldz():
    r, rec = _reg_with_shipper()
    assert not rec.can_supply_in(LDZ.NW)


# 9. is_national only when all 13 LDZs
def test_is_national():
    r, rec = _reg_with_shipper()
    for ldz in LDZ:
        rec.add_ldz(ldz, _REG_DATE)
    assert rec.is_national


# 10. suspend changes status
def test_suspend():
    r, rec = _reg_with_shipper()
    r.suspend("SE")
    assert r.get("SE").status == ShipperStatus.SUSPENDED


# 11. suspended shipper cannot supply
def test_suspended_cannot_supply():
    r, rec = _reg_with_shipper()
    rec.add_ldz(LDZ.EA, _REG_DATE)
    r.suspend("SE")
    # get fresh record
    assert not r.get("SE").can_supply_in(LDZ.EA)


# 12. active_shippers and suspended_shippers
def test_active_suspended_lists():
    r = ShipperCodeRegister()
    r.register("S1", "Supplier1", _REG_DATE)
    r.register("S2", "Supplier2", _REG_DATE)
    r.suspend("S1")
    assert len(r.active_shippers) == 1
    assert len(r.suspended_shippers) == 1


# 13. shipper_summary contains code and name
def test_shipper_summary():
    r, rec = _reg_with_shipper()
    rec.add_ldz(LDZ.EA, _REG_DATE)
    summary = r.shipper_summary()
    assert "SE" in summary
    assert "SyntheticEnergy" in summary


# --- Phase MI depth tests ---

def test_shipper_code_stored():
    r, rec = _reg_with_shipper(code="SE")
    assert rec.shipper_code == "SE"


def test_company_name_stored():
    r, rec = _reg_with_shipper(name="Synthetic Energy Ltd")
    assert rec.company_name == "Synthetic Energy Ltd"


def test_registration_date_stored():
    r, rec = _reg_with_shipper()
    assert rec.registration_date == _REG_DATE


def test_status_active_default():
    r, rec = _reg_with_shipper()
    assert rec.status == ShipperStatus.ACTIVE


def test_register_returns_shipper_record():
    reg = ShipperCodeRegister()
    result = reg.register("SE", "SyntheticEnergy", _REG_DATE)
    assert isinstance(result, ShipperRecord)


def test_ldz_has_13_members():
    assert len(list(LDZ)) == 13


def test_shipper_status_has_4_members():
    assert len(list(ShipperStatus)) == 4


def test_ldz_coverage_count_after_add_ldz():
    r, rec = _reg_with_shipper()
    rec.add_ldz(LDZ.SE, date(2016, 3, 1))
    rec.add_ldz(LDZ.SO, date(2016, 3, 1))
    assert rec.ldz_coverage_count == 2


def test_active_ldz_codes_after_add():
    r, rec = _reg_with_shipper()
    rec.add_ldz(LDZ.NW, date(2016, 3, 1))
    assert LDZ.NW in rec.active_ldz_codes


def test_can_supply_false_after_revoke():
    r, rec = _reg_with_shipper()
    rec.add_ldz(LDZ.EA, date(2016, 3, 1))
    rec.revoke_ldz(LDZ.EA)
    assert rec.can_supply_in(LDZ.EA) is False
