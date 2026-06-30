import datetime as dt
import pytest
from company.market.transfer_objection_register import (
    ObjectionGround, ObjectionStatus, TransferObjectionRecord,
    TransferObjectionRegister, _OBJECTION_WINDOW_WD,
)

OBJ_DATE = dt.date(2024, 3, 4)  # Monday
MPAN = "1000000000001"
SWITCH = "CSS-SW-001"
AS_OF = dt.date(2024, 4, 30)


def make_record(status=ObjectionStatus.RAISED, ground=ObjectionGround.UNPAID_DEBT):
    return TransferObjectionRecord(
        objection_id="OBJ-00001", mpan=MPAN, switch_ref=SWITCH,
        objection_date=OBJ_DATE, ground=ground, status=status)


class TestTransferObjectionRecord:
    def test_is_open_raised(self):
        assert make_record(ObjectionStatus.RAISED).is_open
    def test_is_open_valid(self):
        assert make_record(ObjectionStatus.VALID).is_open
    def test_is_not_open_invalid(self):
        assert not make_record(ObjectionStatus.INVALID).is_open
    def test_is_not_open_resolved(self):
        assert not make_record(ObjectionStatus.RESOLVED).is_open
    def test_objection_deadline_5wd_from_monday(self):
        # Mon 2024-03-04 + 5WD = Mon 2024-03-11
        r = make_record()
        assert r.objection_deadline == dt.date(2024, 3, 11)
    def test_resolution_days_no_resolution(self):
        r = make_record()
        assert r.resolution_days(OBJ_DATE + dt.timedelta(10)) == 10
    def test_resolution_days_with_resolution_date(self):
        r = TransferObjectionRecord(
            objection_id="X", mpan=MPAN, switch_ref=SWITCH,
            objection_date=OBJ_DATE, ground=ObjectionGround.UNPAID_DEBT,
            status=ObjectionStatus.RESOLVED, resolution_date=OBJ_DATE + dt.timedelta(7))
        assert r.resolution_days(AS_OF) == 7
    def test_objection_summary(self):
        s = make_record().objection_summary()
        assert "OBJ-00001" in s and MPAN in s
    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.status = ObjectionStatus.VALID


class TestTransferObjectionRegister:
    def setup_method(self):
        self.reg = TransferObjectionRegister()

    def test_raise_objection_stored(self):
        r = self.reg.raise_objection(MPAN, SWITCH, OBJ_DATE, ObjectionGround.UNPAID_DEBT)
        assert r.status == ObjectionStatus.RAISED

    def test_auto_id_increments(self):
        r1 = self.reg.raise_objection(MPAN, SWITCH, OBJ_DATE, ObjectionGround.UNPAID_DEBT)
        r2 = self.reg.raise_objection("1000000000002", "CSS-SW-002", OBJ_DATE, ObjectionGround.METER_DISPUTE)
        assert r1.objection_id != r2.objection_id

    def test_mark_valid(self):
        r = self.reg.raise_objection(MPAN, SWITCH, OBJ_DATE, ObjectionGround.UNPAID_DEBT)
        v = self.reg.mark_valid(r.objection_id)
        assert v.status == ObjectionStatus.VALID

    def test_mark_invalid(self):
        r = self.reg.raise_objection(MPAN, SWITCH, OBJ_DATE, ObjectionGround.UNPAID_DEBT)
        inv = self.reg.mark_invalid(r.objection_id)
        assert inv.status == ObjectionStatus.INVALID

    def test_resolve(self):
        r = self.reg.raise_objection(MPAN, SWITCH, OBJ_DATE, ObjectionGround.UNPAID_DEBT)
        resolved = self.reg.resolve(r.objection_id, OBJ_DATE + dt.timedelta(7))
        assert resolved.status == ObjectionStatus.RESOLVED
        assert resolved.resolution_date == OBJ_DATE + dt.timedelta(7)

    def test_withdraw(self):
        r = self.reg.raise_objection(MPAN, SWITCH, OBJ_DATE, ObjectionGround.UNPAID_DEBT)
        w = self.reg.withdraw(r.objection_id)
        assert w.status == ObjectionStatus.WITHDRAWN

    def test_update_missing_raises(self):
        with pytest.raises(KeyError):
            self.reg.mark_valid("OBJ-99999")

    def test_open_objections(self):
        r1 = self.reg.raise_objection(MPAN, SWITCH, OBJ_DATE, ObjectionGround.UNPAID_DEBT)
        r2 = self.reg.raise_objection("1000000000002", "CSS-SW-002", OBJ_DATE, ObjectionGround.METER_DISPUTE)
        self.reg.mark_invalid(r1.objection_id)
        assert len(self.reg.open_objections()) == 1

    def test_invalid_objections(self):
        r = self.reg.raise_objection(MPAN, SWITCH, OBJ_DATE, ObjectionGround.UNPAID_DEBT)
        self.reg.mark_invalid(r.objection_id)
        assert len(self.reg.invalid_objections()) == 1

    def test_by_ground(self):
        self.reg.raise_objection(MPAN, SWITCH, OBJ_DATE, ObjectionGround.UNPAID_DEBT)
        self.reg.raise_objection("1000000000002", "CSS-SW-002", OBJ_DATE, ObjectionGround.METER_DISPUTE)
        assert len(self.reg.by_ground(ObjectionGround.UNPAID_DEBT)) == 1

    def test_by_switch(self):
        self.reg.raise_objection(MPAN, SWITCH, OBJ_DATE, ObjectionGround.UNPAID_DEBT)
        self.reg.raise_objection("1000000000002", "CSS-SW-002", OBJ_DATE, ObjectionGround.METER_DISPUTE)
        assert len(self.reg.by_switch(SWITCH)) == 1

    def test_average_resolution_days(self):
        r1 = self.reg.raise_objection(MPAN, SWITCH, OBJ_DATE, ObjectionGround.UNPAID_DEBT)
        r2 = self.reg.raise_objection("1000000000002", "CSS-SW-002", OBJ_DATE, ObjectionGround.METER_DISPUTE)
        self.reg.resolve(r1.objection_id, OBJ_DATE + dt.timedelta(10))
        self.reg.mark_invalid(r2.objection_id)
        # r1: 10 days, r2: 0 days (no resolution_date, as_of=OBJ_DATE for r2)
        avg = self.reg.average_resolution_days(OBJ_DATE)
        assert avg is not None

    def test_average_resolution_days_none_when_no_terminal(self):
        self.reg.raise_objection(MPAN, SWITCH, OBJ_DATE, ObjectionGround.UNPAID_DEBT)
        assert self.reg.average_resolution_days(AS_OF) is None

    def test_invalid_rate_pct(self):
        r1 = self.reg.raise_objection(MPAN, SWITCH, OBJ_DATE, ObjectionGround.UNPAID_DEBT)
        r2 = self.reg.raise_objection("1000000000002", "CSS-SW-002", OBJ_DATE, ObjectionGround.METER_DISPUTE)
        self.reg.mark_invalid(r1.objection_id)
        self.reg.resolve(r2.objection_id, OBJ_DATE + dt.timedelta(5))
        rate = self.reg.invalid_rate_pct()
        assert rate == 50.0

    def test_invalid_rate_none_when_no_terminal(self):
        self.reg.raise_objection(MPAN, SWITCH, OBJ_DATE, ObjectionGround.UNPAID_DEBT)
        assert self.reg.invalid_rate_pct() is None

    def test_objection_register_summary(self):
        self.reg.raise_objection(MPAN, SWITCH, OBJ_DATE, ObjectionGround.UNPAID_DEBT)
        s = self.reg.objection_register_summary(AS_OF)
        assert "1 objections" in s

    def test_empty_summary(self):
        s = self.reg.objection_register_summary(AS_OF)
        assert "0 objections" in s
