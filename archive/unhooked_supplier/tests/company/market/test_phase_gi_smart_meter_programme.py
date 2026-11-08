"""Tests for Phase GI: Smart Meter Installation Programme Register."""
import datetime as dt
import pytest
from company.market.smart_meter_programme_register import (
    SMETSGeneration, AppointmentSlot, InstallationOutcome,
    InstallationAppointmentRecord, SmartMeterProgrammeRegister,
)

APPT_DATE = dt.date(2024, 6, 15)
AS_OF = dt.date(2024, 6, 1)
ACCT = "DOM-001"
MPAN = "1000000000001"

def make_record(outcome=InstallationOutcome.SCHEDULED):
    return InstallationAppointmentRecord(
        appt_id="SMAPPT-00001", account_id=ACCT, mpan=MPAN,
        fuel="electricity", appointment_date=APPT_DATE,
        slot=AppointmentSlot.MORNING, outcome=outcome)

class TestInstallationAppointmentRecord:
    def test_is_complete_when_completed(self):
        assert make_record(InstallationOutcome.COMPLETED).is_complete
    def test_is_not_complete_when_scheduled(self):
        assert not make_record().is_complete
    def test_is_access_issue_refused(self):
        assert make_record(InstallationOutcome.CUSTOMER_REFUSED).is_access_issue
    def test_is_access_issue_access_failed(self):
        assert make_record(InstallationOutcome.ACCESS_FAILED).is_access_issue
    def test_is_technical_failure_aborted(self):
        assert make_record(InstallationOutcome.ABORTED_ENGINEER).is_technical_failure
    def test_is_technical_failure_failed_tech(self):
        assert make_record(InstallationOutcome.FAILED_TECHNICAL).is_technical_failure
    def test_is_terminal_completed(self):
        assert make_record(InstallationOutcome.COMPLETED).is_terminal
    def test_is_not_terminal_scheduled(self):
        assert not make_record().is_terminal
    def test_appt_summary(self):
        r = make_record()
        assert "SMAPPT-00001" in r.appt_summary() and MPAN in r.appt_summary()
    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.outcome = InstallationOutcome.COMPLETED

class TestSmartMeterProgrammeRegister:
    def setup_method(self):
        self.reg = SmartMeterProgrammeRegister()
    def test_schedule_appointment_stored(self):
        r = self.reg.schedule_appointment(ACCT, MPAN, "electricity", APPT_DATE)
        assert r.outcome == InstallationOutcome.SCHEDULED
    def test_auto_id_increments(self):
        r1 = self.reg.schedule_appointment(ACCT, MPAN, "electricity", APPT_DATE)
        r2 = self.reg.schedule_appointment("DOM-002", MPAN, "gas", APPT_DATE)
        assert r1.appt_id != r2.appt_id
    def test_invalid_fuel_raises(self):
        with pytest.raises(ValueError):
            self.reg.schedule_appointment(ACCT, MPAN, "oil", APPT_DATE)
    def test_record_outcome_complete(self):
        r = self.reg.schedule_appointment(ACCT, MPAN, "electricity", APPT_DATE)
        done = self.reg.record_outcome(r.appt_id, InstallationOutcome.COMPLETED, APPT_DATE)
        assert done.is_complete and done.outcome_date == APPT_DATE
    def test_record_outcome_missing_raises(self):
        with pytest.raises(KeyError):
            self.reg.record_outcome("SMAPPT-99999", InstallationOutcome.COMPLETED, APPT_DATE)
    def test_completions(self):
        r = self.reg.schedule_appointment(ACCT, MPAN, "electricity", APPT_DATE)
        self.reg.record_outcome(r.appt_id, InstallationOutcome.COMPLETED, APPT_DATE)
        self.reg.schedule_appointment("DOM-002", MPAN, "gas", APPT_DATE)  # still scheduled
        assert len(self.reg.completions()) == 1
    def test_access_failures(self):
        r = self.reg.schedule_appointment(ACCT, MPAN, "electricity", APPT_DATE)
        self.reg.record_outcome(r.appt_id, InstallationOutcome.ACCESS_FAILED, APPT_DATE)
        assert len(self.reg.access_failures()) == 1
    def test_technical_failures(self):
        r = self.reg.schedule_appointment(ACCT, MPAN, "electricity", APPT_DATE)
        self.reg.record_outcome(r.appt_id, InstallationOutcome.FAILED_TECHNICAL, APPT_DATE)
        assert len(self.reg.technical_failures()) == 1
    def test_customer_refusals(self):
        r = self.reg.schedule_appointment(ACCT, MPAN, "electricity", APPT_DATE)
        self.reg.record_outcome(r.appt_id, InstallationOutcome.CUSTOMER_REFUSED, APPT_DATE)
        assert len(self.reg.customer_refusals()) == 1
    def test_pending_appointments(self):
        self.reg.schedule_appointment(ACCT, MPAN, "electricity", APPT_DATE)
        pending = self.reg.pending_appointments(AS_OF)
        assert len(pending) == 1
    def test_pending_not_returned_when_terminal(self):
        r = self.reg.schedule_appointment(ACCT, MPAN, "electricity", APPT_DATE)
        self.reg.record_outcome(r.appt_id, InstallationOutcome.COMPLETED, APPT_DATE)
        pending = self.reg.pending_appointments(AS_OF)
        assert len(pending) == 0
    def test_completion_rate_pct(self):
        r1 = self.reg.schedule_appointment(ACCT, MPAN, "electricity", APPT_DATE)
        r2 = self.reg.schedule_appointment("DOM-002", MPAN, "gas", APPT_DATE)
        self.reg.record_outcome(r1.appt_id, InstallationOutcome.COMPLETED, APPT_DATE)
        self.reg.record_outcome(r2.appt_id, InstallationOutcome.ACCESS_FAILED, APPT_DATE)
        assert self.reg.completion_rate_pct() == 50.0
    def test_completion_rate_pct_none_when_no_terminal(self):
        self.reg.schedule_appointment(ACCT, MPAN, "electricity", APPT_DATE)
        assert self.reg.completion_rate_pct() is None
    def test_access_failure_rate_pct(self):
        r1 = self.reg.schedule_appointment(ACCT, MPAN, "electricity", APPT_DATE)
        r2 = self.reg.schedule_appointment("DOM-002", MPAN, "gas", APPT_DATE)
        self.reg.record_outcome(r1.appt_id, InstallationOutcome.ACCESS_FAILED, APPT_DATE)
        self.reg.record_outcome(r2.appt_id, InstallationOutcome.COMPLETED, APPT_DATE)
        assert self.reg.access_failure_rate_pct() == 50.0
    def test_monthly_completions(self):
        r = self.reg.schedule_appointment(ACCT, MPAN, "electricity", APPT_DATE)
        self.reg.record_outcome(r.appt_id, InstallationOutcome.COMPLETED, APPT_DATE)
        assert self.reg.monthly_completions(2024, 6) == 1
        assert self.reg.monthly_completions(2024, 7) == 0
    def test_by_fuel(self):
        self.reg.schedule_appointment(ACCT, MPAN, "electricity", APPT_DATE)
        self.reg.schedule_appointment("DOM-002", "1000000000002", "gas", APPT_DATE)
        assert len(self.reg.by_fuel("electricity")) == 1
    def test_programme_summary(self):
        r = self.reg.schedule_appointment(ACCT, MPAN, "electricity", APPT_DATE)
        self.reg.record_outcome(r.appt_id, InstallationOutcome.COMPLETED, APPT_DATE)
        s = self.reg.programme_summary(AS_OF)
        assert "1 appointments" in s and "1 completed" in s
    def test_empty_summary(self):
        s = self.reg.programme_summary(AS_OF)
        assert "0 appointments" in s
