import datetime as dt
import pytest
from company.market.smart_meter_programme_register import (
    SmartMeterProgrammeRegister, AppointmentSlot, SMETSGeneration, InstallationOutcome,
)

DATE = dt.date(2022, 6, 15)


def _reg():
    r = SmartMeterProgrammeRegister()
    r.schedule_appointment("ACC-001", "MPAN-111", "electricity", DATE)
    return r


def test_appt_id_prefix():
    reg = _reg()
    assert reg._records[0].appt_id.startswith("SMAPPT-")


def test_outcome_default_scheduled():
    reg = _reg()
    assert reg._records[0].outcome == InstallationOutcome.SCHEDULED


def test_invalid_fuel_raises():
    reg = SmartMeterProgrammeRegister()
    with pytest.raises(ValueError):
        reg.schedule_appointment("ACC-X", "M", "oil", DATE)


def test_record_outcome_completed():
    reg = _reg()
    aid = reg._records[0].appt_id
    updated = reg.record_outcome(aid, InstallationOutcome.COMPLETED, DATE)
    assert updated.is_complete is True


def test_customer_refused_is_access_issue():
    reg = _reg()
    aid = reg._records[0].appt_id
    updated = reg.record_outcome(aid, InstallationOutcome.CUSTOMER_REFUSED, DATE)
    assert updated.is_access_issue is True


def test_access_failed_is_access_issue():
    reg = _reg()
    aid = reg._records[0].appt_id
    updated = reg.record_outcome(aid, InstallationOutcome.ACCESS_FAILED, DATE)
    assert updated.is_access_issue is True


def test_failed_technical_is_technical_failure():
    reg = _reg()
    aid = reg._records[0].appt_id
    updated = reg.record_outcome(aid, InstallationOutcome.FAILED_TECHNICAL, DATE)
    assert updated.is_technical_failure is True


def test_completion_rate_none_empty():
    reg = SmartMeterProgrammeRegister()
    assert reg.completion_rate_pct() is None


def test_completions_filters_completed():
    reg = _reg()
    aid = reg._records[0].appt_id
    reg.record_outcome(aid, InstallationOutcome.COMPLETED, DATE)
    assert len(reg.completions()) == 1


def test_customer_refusals_filters_refused():
    reg = SmartMeterProgrammeRegister()
    reg.schedule_appointment("A", "M1", "electricity", DATE)
    reg.schedule_appointment("B", "M2", "electricity", DATE)
    a1 = reg._records[0].appt_id
    a2 = reg._records[1].appt_id
    reg.record_outcome(a1, InstallationOutcome.CUSTOMER_REFUSED, DATE)
    reg.record_outcome(a2, InstallationOutcome.COMPLETED, DATE)
    assert len(reg.customer_refusals()) == 1
