import datetime as dt
import pytest
from company.market.mop_appointment_register import (
    MOPAppointmentRegister, MOPServiceTier, MOPAppointmentStatus, MOPChangeReason,
)

START = dt.date(2022, 1, 1)


def _reg():
    r = MOPAppointmentRegister()
    r.appoint_mop("MPAN-001", "MOP-UK", MOPServiceTier.BASIC, 12.50, START)
    return r


def test_appointment_id_prefix():
    reg = _reg()
    assert reg._records[0].appointment_id.startswith("MOP-")


def test_status_default_active():
    reg = _reg()
    assert reg._records[0].status == MOPAppointmentStatus.ACTIVE


def test_initiate_change_sets_pending():
    reg = _reg()
    aid = reg._records[0].appointment_id
    updated, _ = reg.initiate_change(aid, dt.date(2022, 6, 1))
    assert updated.status == MOPAppointmentStatus.PENDING_CHANGE


def test_initiate_change_effective_date_is_5wd_later():
    reg = _reg()
    aid = reg._records[0].appointment_id
    notice = dt.date(2022, 6, 6)
    _, effective = reg.initiate_change(aid, notice)
    assert (effective - notice).days >= 5


def test_complete_change_terminates_old_creates_new():
    reg = _reg()
    aid = reg._records[0].appointment_id
    reg.initiate_change(aid, dt.date(2022, 6, 1))
    terminated, new_rec = reg.complete_change(
        aid, "MOP-UKPN", MOPServiceTier.ENHANCED, 18.0,
        dt.date(2022, 6, 8), MOPChangeReason.SUPPLIER_CHOICE,
    )
    assert terminated.status == MOPAppointmentStatus.TERMINATED
    assert new_rec.status == MOPAppointmentStatus.ACTIVE
    assert new_rec.mop_id == "MOP-UKPN"


def test_current_mop_for_mpan_found():
    reg = _reg()
    result = reg.current_mop_for_mpan("MPAN-001", dt.date(2022, 6, 1))
    assert result is not None
    assert result.mop_id == "MOP-UK"


def test_current_mop_for_mpan_none_after_terminate():
    reg = _reg()
    aid = reg._records[0].appointment_id
    reg.terminate(aid, dt.date(2022, 3, 1))
    result = reg.current_mop_for_mpan("MPAN-001", dt.date(2022, 6, 1))
    assert result is None


def test_negative_fee_raises():
    reg = MOPAppointmentRegister()
    with pytest.raises(ValueError):
        reg.appoint_mop("MPAN-X", "MOP-X", MOPServiceTier.BASIC, -1.0, START)


def test_total_monthly_fees_sums_active():
    reg = _reg()
    reg.appoint_mop("MPAN-002", "MOP-UK", MOPServiceTier.ENHANCED, 25.0, START)
    total = reg.total_monthly_fees_gbp(dt.date(2022, 6, 1))
    assert total == pytest.approx(37.50)


def test_mpans_without_mop():
    reg = _reg()
    all_mpans = ["MPAN-001", "MPAN-999"]
    uncovered = reg.mpans_without_mop(all_mpans, dt.date(2022, 6, 1))
    assert uncovered == ["MPAN-999"]
