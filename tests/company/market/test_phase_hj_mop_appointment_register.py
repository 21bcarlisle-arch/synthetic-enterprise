"""Tests for Phase HJ: MOP Appointment Register."""
import datetime as dt
import pytest

from company.market.mop_appointment_register import (
    MOPAppointmentRegister,
    MOPAppointmentRecord,
    MOPAppointmentStatus,
    MOPChangeReason,
    MOPServiceTier,
    _add_working_days,
)

TODAY = dt.date(2024, 1, 15)


# --- _add_working_days helper ---

def test_add_working_days_skips_weekends():
    # Friday + 5WD = next Friday (skips Sat/Sun)
    friday = dt.date(2024, 1, 5)  # Friday
    result = _add_working_days(friday, 5)
    assert result == dt.date(2024, 1, 12)  # next Friday


def test_add_working_days_single():
    monday = dt.date(2024, 1, 8)
    assert _add_working_days(monday, 1) == dt.date(2024, 1, 9)


# --- appoint_mop ---

def test_appoint_mop_creates_active_record():
    reg = MOPAppointmentRegister()
    rec = reg.appoint_mop("1000000000001", "MOP_ALPHA", MOPServiceTier.BASIC, 5.0, TODAY)
    assert rec.status == MOPAppointmentStatus.ACTIVE
    assert rec.mpan == "1000000000001"
    assert rec.mop_id == "MOP_ALPHA"
    assert rec.tier == MOPServiceTier.BASIC
    assert rec.monthly_fee_gbp == 5.0


def test_appoint_mop_rejects_negative_fee():
    reg = MOPAppointmentRegister()
    with pytest.raises(ValueError):
        reg.appoint_mop("1000000000001", "MOP_ALPHA", MOPServiceTier.BASIC, -1.0, TODAY)


def test_appoint_mop_auto_increments_id():
    reg = MOPAppointmentRegister()
    r1 = reg.appoint_mop("MP1", "MOP_A", MOPServiceTier.BASIC, 5.0, TODAY)
    r2 = reg.appoint_mop("MP2", "MOP_A", MOPServiceTier.ENHANCED, 8.0, TODAY)
    assert r1.appointment_id != r2.appointment_id


# --- is_active_as_of ---

def test_record_active_before_end_date():
    rec = MOPAppointmentRecord(
        appointment_id="MOP-00001",
        mpan="MP1",
        mop_id="MOP_A",
        tier=MOPServiceTier.BASIC,
        monthly_fee_gbp=5.0,
        start_date=dt.date(2023, 1, 1),
        status=MOPAppointmentStatus.ACTIVE,
    )
    assert rec.is_active_as_of(dt.date(2023, 6, 1))


def test_record_inactive_before_start():
    rec = MOPAppointmentRecord(
        appointment_id="MOP-00001",
        mpan="MP1",
        mop_id="MOP_A",
        tier=MOPServiceTier.BASIC,
        monthly_fee_gbp=5.0,
        start_date=dt.date(2024, 3, 1),
        status=MOPAppointmentStatus.ACTIVE,
    )
    assert not rec.is_active_as_of(dt.date(2024, 1, 1))


def test_record_inactive_when_terminated():
    rec = MOPAppointmentRecord(
        appointment_id="MOP-00001",
        mpan="MP1",
        mop_id="MOP_A",
        tier=MOPServiceTier.BASIC,
        monthly_fee_gbp=5.0,
        start_date=dt.date(2023, 1, 1),
        status=MOPAppointmentStatus.TERMINATED,
        end_date=dt.date(2023, 12, 31),
    )
    assert not rec.is_active_as_of(dt.date(2024, 1, 1))


# --- initiate_change ---

def test_initiate_change_sets_pending_status():
    reg = MOPAppointmentRegister()
    rec = reg.appoint_mop("MP1", "MOP_A", MOPServiceTier.BASIC, 5.0, TODAY)
    updated, effective = reg.initiate_change(rec.appointment_id, TODAY)
    assert updated.status == MOPAppointmentStatus.PENDING_CHANGE
    assert effective > TODAY


def test_initiate_change_effective_date_is_5wd():
    reg = MOPAppointmentRegister()
    monday = dt.date(2024, 1, 8)  # Monday
    rec = reg.appoint_mop("MP1", "MOP_A", MOPServiceTier.BASIC, 5.0, monday)
    _, effective = reg.initiate_change(rec.appointment_id, monday)
    assert effective == dt.date(2024, 1, 15)  # Monday + 5WD = next Monday


def test_initiate_change_rejects_non_active():
    reg = MOPAppointmentRegister()
    rec = reg.appoint_mop("MP1", "MOP_A", MOPServiceTier.BASIC, 5.0, TODAY)
    reg.initiate_change(rec.appointment_id, TODAY)
    with pytest.raises(ValueError):
        reg.initiate_change(rec.appointment_id, TODAY)  # already PENDING_CHANGE


# --- complete_change ---

def test_complete_change_terminates_old_creates_new():
    reg = MOPAppointmentRegister()
    rec = reg.appoint_mop("MP1", "MOP_A", MOPServiceTier.BASIC, 5.0, TODAY)
    reg.initiate_change(rec.appointment_id, TODAY)
    effective = dt.date(2024, 1, 22)
    old, new = reg.complete_change(
        rec.appointment_id, "MOP_B", MOPServiceTier.ENHANCED, 8.0,
        effective, MOPChangeReason.SUPPLIER_CHOICE
    )
    assert old.status == MOPAppointmentStatus.TERMINATED
    assert old.end_date == effective
    assert new.mop_id == "MOP_B"
    assert new.tier == MOPServiceTier.ENHANCED
    assert new.monthly_fee_gbp == 8.0
    assert new.start_date == effective
    assert new.status == MOPAppointmentStatus.ACTIVE


def test_complete_change_rejects_active_appointment():
    reg = MOPAppointmentRegister()
    rec = reg.appoint_mop("MP1", "MOP_A", MOPServiceTier.BASIC, 5.0, TODAY)
    with pytest.raises(ValueError):
        reg.complete_change(
            rec.appointment_id, "MOP_B", MOPServiceTier.ENHANCED, 8.0,
            TODAY, MOPChangeReason.SUPPLIER_CHOICE
        )


# --- terminate ---

def test_terminate_sets_terminated_status():
    reg = MOPAppointmentRegister()
    rec = reg.appoint_mop("MP1", "MOP_A", MOPServiceTier.BASIC, 5.0, TODAY)
    terminated = reg.terminate(rec.appointment_id, TODAY)
    assert terminated.status == MOPAppointmentStatus.TERMINATED
    assert terminated.end_date == TODAY


def test_terminate_rejects_already_terminated():
    reg = MOPAppointmentRegister()
    rec = reg.appoint_mop("MP1", "MOP_A", MOPServiceTier.BASIC, 5.0, TODAY)
    reg.terminate(rec.appointment_id, TODAY)
    with pytest.raises(ValueError):
        reg.terminate(rec.appointment_id, TODAY)


# --- current_mop_for_mpan ---

def test_current_mop_returns_active():
    reg = MOPAppointmentRegister()
    reg.appoint_mop("MP1", "MOP_A", MOPServiceTier.BASIC, 5.0, TODAY)
    current = reg.current_mop_for_mpan("MP1", TODAY)
    assert current is not None
    assert current.mop_id == "MOP_A"


def test_current_mop_returns_none_for_unknown_mpan():
    reg = MOPAppointmentRegister()
    assert reg.current_mop_for_mpan("UNKNOWN", TODAY) is None


def test_current_mop_returns_none_after_termination():
    reg = MOPAppointmentRegister()
    rec = reg.appoint_mop("MP1", "MOP_A", MOPServiceTier.BASIC, 5.0, TODAY)
    reg.terminate(rec.appointment_id, TODAY)
    assert reg.current_mop_for_mpan("MP1", TODAY) is None


# --- mpans_without_mop ---

def test_mpans_without_mop_identifies_gap():
    reg = MOPAppointmentRegister()
    reg.appoint_mop("MP1", "MOP_A", MOPServiceTier.BASIC, 5.0, TODAY)
    uncovered = reg.mpans_without_mop(["MP1", "MP2"], TODAY)
    assert uncovered == ["MP2"]


def test_mpans_without_mop_all_covered():
    reg = MOPAppointmentRegister()
    reg.appoint_mop("MP1", "MOP_A", MOPServiceTier.BASIC, 5.0, TODAY)
    reg.appoint_mop("MP2", "MOP_B", MOPServiceTier.BASIC, 5.0, TODAY)
    assert reg.mpans_without_mop(["MP1", "MP2"], TODAY) == []


# --- fees ---

def test_total_monthly_fees():
    reg = MOPAppointmentRegister()
    reg.appoint_mop("MP1", "MOP_A", MOPServiceTier.BASIC, 5.0, TODAY)
    reg.appoint_mop("MP2", "MOP_B", MOPServiceTier.ENHANCED, 8.0, TODAY)
    assert reg.total_monthly_fees_gbp(TODAY) == pytest.approx(13.0)


def test_total_fees_excludes_terminated():
    reg = MOPAppointmentRegister()
    rec = reg.appoint_mop("MP1", "MOP_A", MOPServiceTier.BASIC, 5.0, TODAY)
    reg.appoint_mop("MP2", "MOP_B", MOPServiceTier.ENHANCED, 8.0, TODAY)
    reg.terminate(rec.appointment_id, TODAY)
    assert reg.total_monthly_fees_gbp(TODAY) == pytest.approx(8.0)


def test_months_of_service_basic():
    rec = MOPAppointmentRecord(
        appointment_id="MOP-00001",
        mpan="MP1",
        mop_id="MOP_A",
        tier=MOPServiceTier.BASIC,
        monthly_fee_gbp=5.0,
        start_date=dt.date(2023, 1, 1),
        status=MOPAppointmentStatus.ACTIVE,
    )
    assert rec.months_of_service(dt.date(2023, 4, 1)) == 3


# --- provider breakdown + summary ---

def test_mop_provider_breakdown():
    reg = MOPAppointmentRegister()
    reg.appoint_mop("MP1", "MOP_A", MOPServiceTier.BASIC, 5.0, TODAY)
    reg.appoint_mop("MP2", "MOP_A", MOPServiceTier.BASIC, 5.0, TODAY)
    reg.appoint_mop("MP3", "MOP_B", MOPServiceTier.ENHANCED, 8.0, TODAY)
    bd = reg.mop_provider_breakdown(TODAY)
    assert bd["MOP_A"] == 2
    assert bd["MOP_B"] == 1


def test_mop_summary_string():
    reg = MOPAppointmentRegister()
    reg.appoint_mop("MP1", "MOP_A", MOPServiceTier.BASIC, 5.0, TODAY)
    summary = reg.mop_summary(TODAY)
    assert "1 active" in summary
    assert "GBP" in summary


def test_appointment_summary_string():
    reg = MOPAppointmentRegister()
    rec = reg.appoint_mop("MP1", "MOP_A", MOPServiceTier.BASIC, 5.0, TODAY)
    s = rec.appointment_summary()
    assert "MP1" in s
    assert "MOP_A" in s
    assert "basic" in s
