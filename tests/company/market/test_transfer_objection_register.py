"""Tests for company/market/transfer_objection_register.py (Sprint CLI)."""
import datetime as dt

from company.market.transfer_objection_register import (
    TransferObjectionRegister,
    ObjectionGround,
    ObjectionStatus,
)

MONDAY = dt.date(2022, 6, 6)


def _reg():
    return TransferObjectionRegister()


def test_objection_id_starts_with_obj():
    reg = _reg()
    r = reg.raise_objection("M1", "SW001", MONDAY, ObjectionGround.UNPAID_DEBT)
    assert r.objection_id.startswith("OBJ-")


def test_mpan_stored():
    reg = _reg()
    r = reg.raise_objection("M1", "SW001", MONDAY, ObjectionGround.UNPAID_DEBT)
    assert r.mpan == "M1"


def test_ground_stored():
    reg = _reg()
    r = reg.raise_objection("M1", "SW001", MONDAY, ObjectionGround.METER_DISPUTE)
    assert r.ground == ObjectionGround.METER_DISPUTE


def test_is_open_true_when_raised():
    reg = _reg()
    r = reg.raise_objection("M1", "SW001", MONDAY, ObjectionGround.COOLING_OFF)
    assert r.is_open is True


def test_objection_deadline_is_5_working_days():
    reg = _reg()
    r = reg.raise_objection("M1", "SW001", MONDAY, ObjectionGround.UNPAID_DEBT)
    assert r.objection_deadline == dt.date(2022, 6, 13)


def test_mark_valid_updates_status():
    reg = _reg()
    r = reg.raise_objection("M1", "SW001", MONDAY, ObjectionGround.UNPAID_DEBT)
    v = reg.mark_valid(r.objection_id)
    assert v.status == ObjectionStatus.VALID


def test_mark_invalid_updates_status():
    reg = _reg()
    r = reg.raise_objection("M1", "SW001", MONDAY, ObjectionGround.UNPAID_DEBT)
    inv = reg.mark_invalid(r.objection_id)
    assert inv.status == ObjectionStatus.INVALID


def test_open_objections_filters():
    reg = _reg()
    r1 = reg.raise_objection("M1", "SW001", MONDAY, ObjectionGround.UNPAID_DEBT)
    r2 = reg.raise_objection("M2", "SW002", MONDAY, ObjectionGround.UNPAID_DEBT)
    reg.mark_invalid(r2.objection_id)
    assert len(reg.open_objections()) == 1


def test_by_ground_filters():
    reg = _reg()
    reg.raise_objection("M1", "SW001", MONDAY, ObjectionGround.UNPAID_DEBT)
    reg.raise_objection("M2", "SW002", MONDAY, ObjectionGround.METER_DISPUTE)
    result = reg.by_ground(ObjectionGround.UNPAID_DEBT)
    assert len(result) == 1


def test_invalid_rate_pct_none_when_no_terminal():
    reg = _reg()
    reg.raise_objection("M1", "SW001", MONDAY, ObjectionGround.UNPAID_DEBT)
    assert reg.invalid_rate_pct() is None
