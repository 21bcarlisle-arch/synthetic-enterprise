"""Tests for company/market/transfer_objection_register.py (Sprint CLI)."""
import datetime as dt

from company.market.transfer_objection_register import (
    ObjectionGround,
    ObjectionStatus,
    TransferObjectionRegister,
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


def _working_days_after(start: dt.date, end: dt.date) -> int:
    """Working days in (start, end], on the company's one calendar."""
    from company.compliance.working_days import is_working_day

    return sum(is_working_day(start + dt.timedelta(n)) for n in range(1, (end - start).days + 1))


def test_the_window_ends_on_the_REC_working_day_after_the_switch_request():
    """REC Schedule 23 v2.2 para 6.2: 17:00 on the 1st working day (domestic) or the 2nd
    (non-domestic) after the day the gaining supplier SUBMITTED THE SWITCH REQUEST. Keyed to
    that property over a year of submission days (weekends and bank holidays included), and
    independent of the day the objection was raised. Defect guarded: the 5-working-day
    window counted from the objection date this register used to carry."""
    reg = _reg()
    day = dt.date(2024, 1, 1)
    while day < dt.date(2025, 1, 1):
        for domestic, n in ((True, 1), (False, 2)):
            r = reg.raise_objection("M1", "SW001", dt.date(2024, 12, 31),
                                    ObjectionGround.UNPAID_DEBT,
                                    switch_request_submitted=day, domestic=domestic)
            deadline = r.objection_deadline
            assert _working_days_after(day, deadline) == n, (day, domestic, deadline)
            assert _working_days_after(day, deadline - dt.timedelta(1)) == n - 1
            assert r.objection_window_closes == dt.datetime.combine(deadline, dt.time(17))
        day += dt.timedelta(1)


def test_a_record_without_the_switch_request_date_cannot_say_when_its_window_closed():
    import pytest

    r = _reg().raise_objection("M1", "SW001", MONDAY, ObjectionGround.UNPAID_DEBT)
    with pytest.raises(ValueError, match="submitted the switch request"):
        r.objection_deadline


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
