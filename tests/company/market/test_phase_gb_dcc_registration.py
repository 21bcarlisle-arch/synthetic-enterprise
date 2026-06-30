"""Tests for Phase GB: DCC Meter Registration Register."""
import datetime as dt
import pytest
from company.market.dcc_meter_registration import (
    DCCRegistrationStatus,
    DCCRegistrationRecord,
    DCCMeterRegistrationRegister,
    _add_working_days,
    _DCC_REGISTRATION_DEADLINE_DAYS,
    _DCC_ORPHAN_THRESHOLD_DAYS,
)

# ── helpers ──────────────────────────────────────────────────────────────────

INSTALL = dt.date(2024, 3, 4)  # Monday
MPAN = "1234567890123"
SERIAL = "G4V0001234567"
DEADLINE = _add_working_days(INSTALL, _DCC_REGISTRATION_DEADLINE_DAYS)


# ── DCCRegistrationRecord ────────────────────────────────────────────────────

class TestDCCRegistrationRecord:

    def test_registration_deadline_is_10_working_days(self):
        r = DCCRegistrationRecord("DCC-00001", MPAN, INSTALL, SERIAL)
        assert r.registration_deadline == DEADLINE

    def test_is_pending_default(self):
        r = DCCRegistrationRecord("DCC-00001", MPAN, INSTALL, SERIAL)
        assert r.is_pending

    def test_is_registered(self):
        r = DCCRegistrationRecord("DCC-00001", MPAN, INSTALL, SERIAL,
                                  DCCRegistrationStatus.REGISTERED, dt.date(2024, 3, 10))
        assert r.is_registered and not r.is_pending

    def test_is_failed(self):
        r = DCCRegistrationRecord("DCC-00001", MPAN, INSTALL, SERIAL,
                                  DCCRegistrationStatus.FAILED, failed_date=dt.date(2024, 3, 12))
        assert r.is_failed

    def test_is_orphaned(self):
        r = DCCRegistrationRecord("DCC-00001", MPAN, INSTALL, SERIAL,
                                  DCCRegistrationStatus.ORPHANED)
        assert r.is_orphaned

    def test_is_overdue_after_deadline(self):
        r = DCCRegistrationRecord("DCC-00001", MPAN, INSTALL, SERIAL)
        assert r.is_overdue_as_of(DEADLINE + dt.timedelta(1))

    def test_is_not_overdue_on_deadline(self):
        r = DCCRegistrationRecord("DCC-00001", MPAN, INSTALL, SERIAL)
        assert not r.is_overdue_as_of(DEADLINE)

    def test_is_not_overdue_when_registered(self):
        r = DCCRegistrationRecord("DCC-00001", MPAN, INSTALL, SERIAL,
                                  DCCRegistrationStatus.REGISTERED, dt.date(2024, 3, 10))
        assert not r.is_overdue_as_of(dt.date(2030, 1, 1))

    def test_orphan_candidate_after_90_days(self):
        r = DCCRegistrationRecord("DCC-00001", MPAN, INSTALL, SERIAL)
        assert r.is_orphan_candidate_as_of(INSTALL + dt.timedelta(91))

    def test_not_orphan_candidate_when_registered(self):
        r = DCCRegistrationRecord("DCC-00001", MPAN, INSTALL, SERIAL,
                                  DCCRegistrationStatus.REGISTERED, dt.date(2024, 3, 10))
        assert not r.is_orphan_candidate_as_of(INSTALL + dt.timedelta(200))

    def test_days_since_install(self):
        r = DCCRegistrationRecord("DCC-00001", MPAN, INSTALL, SERIAL)
        assert r.days_since_install(INSTALL + dt.timedelta(10)) == 10

    def test_record_summary_contains_id_and_mpan(self):
        r = DCCRegistrationRecord("DCC-00001", MPAN, INSTALL, SERIAL)
        s = r.record_summary()
        assert "DCC-00001" in s and MPAN in s

    def test_frozen(self):
        r = DCCRegistrationRecord("DCC-00001", MPAN, INSTALL, SERIAL)
        with pytest.raises((AttributeError, TypeError)):
            r.mpan = "9999999999999"


# ── DCCMeterRegistrationRegister ─────────────────────────────────────────────

class TestDCCMeterRegistrationRegister:

    def setup_method(self):
        self.reg = DCCMeterRegistrationRegister()

    def test_register_installation_stored(self):
        r = self.reg.register_installation(MPAN, INSTALL, SERIAL)
        assert r.mpan == MPAN
        assert r.status == DCCRegistrationStatus.PENDING

    def test_register_auto_id(self):
        r1 = self.reg.register_installation(MPAN, INSTALL, SERIAL)
        r2 = self.reg.register_installation("9876543210987", INSTALL, "SERIAL2")
        assert r1.record_id != r2.record_id

    def test_mark_registered(self):
        r = self.reg.register_installation(MPAN, INSTALL, SERIAL)
        done = self.reg.mark_registered(r.record_id, dt.date(2024, 3, 10))
        assert done.is_registered
        assert done.registered_date == dt.date(2024, 3, 10)

    def test_mark_failed_increments_retry(self):
        r = self.reg.register_installation(MPAN, INSTALL, SERIAL)
        failed = self.reg.mark_failed(r.record_id, dt.date(2024, 3, 12))
        assert failed.is_failed
        assert failed.retry_count == 1

    def test_mark_failed_twice_increments_again(self):
        r = self.reg.register_installation(MPAN, INSTALL, SERIAL)
        self.reg.mark_failed(r.record_id, dt.date(2024, 3, 12))
        second = self.reg.mark_failed(r.record_id, dt.date(2024, 3, 15))
        assert second.retry_count == 2

    def test_mark_orphaned(self):
        r = self.reg.register_installation(MPAN, INSTALL, SERIAL)
        orphan = self.reg.mark_orphaned(r.record_id)
        assert orphan.is_orphaned

    def test_deregister(self):
        r = self.reg.register_installation(MPAN, INSTALL, SERIAL)
        dereg = self.reg.deregister(r.record_id)
        assert dereg.status == DCCRegistrationStatus.DEREGISTERED

    def test_update_missing_raises(self):
        with pytest.raises(KeyError):
            self.reg.mark_registered("DCC-99999", dt.date(2024, 3, 10))

    def test_pending_registrations(self):
        r = self.reg.register_installation(MPAN, INSTALL, SERIAL)
        r2 = self.reg.register_installation("9876543210987", INSTALL, "S2")
        self.reg.mark_registered(r.record_id, dt.date(2024, 3, 10))
        assert len(self.reg.pending_registrations()) == 1

    def test_overdue_registrations(self):
        self.reg.register_installation(MPAN, INSTALL, SERIAL)
        assert len(self.reg.overdue_registrations(DEADLINE + dt.timedelta(1))) == 1
        assert len(self.reg.overdue_registrations(DEADLINE)) == 0

    def test_failed_registrations(self):
        r = self.reg.register_installation(MPAN, INSTALL, SERIAL)
        self.reg.mark_failed(r.record_id, dt.date(2024, 3, 12))
        assert len(self.reg.failed_registrations()) == 1

    def test_orphaned_meters(self):
        r = self.reg.register_installation(MPAN, INSTALL, SERIAL)
        self.reg.mark_orphaned(r.record_id)
        assert len(self.reg.orphaned_meters()) == 1

    def test_orphan_candidates(self):
        self.reg.register_installation(MPAN, INSTALL, SERIAL)
        assert len(self.reg.orphan_candidates(INSTALL + dt.timedelta(91))) == 1
        assert len(self.reg.orphan_candidates(INSTALL + dt.timedelta(89))) == 0

    def test_registered_meters(self):
        r = self.reg.register_installation(MPAN, INSTALL, SERIAL)
        self.reg.mark_registered(r.record_id, dt.date(2024, 3, 10))
        assert len(self.reg.registered_meters()) == 1

    def test_registration_rate_pct_all_registered(self):
        r = self.reg.register_installation(MPAN, INSTALL, SERIAL)
        self.reg.mark_registered(r.record_id, dt.date(2024, 3, 10))
        assert self.reg.registration_rate_pct() == 100.0

    def test_registration_rate_pct_partial(self):
        r1 = self.reg.register_installation(MPAN, INSTALL, SERIAL)
        self.reg.register_installation("9876543210987", INSTALL, "S2")
        self.reg.mark_registered(r1.record_id, dt.date(2024, 3, 10))
        assert self.reg.registration_rate_pct() == 50.0

    def test_registration_rate_pct_excludes_deregistered(self):
        r1 = self.reg.register_installation(MPAN, INSTALL, SERIAL)
        r2 = self.reg.register_installation("9876543210987", INSTALL, "S2")
        self.reg.mark_registered(r1.record_id, dt.date(2024, 3, 10))
        self.reg.deregister(r2.record_id)
        # 1 active (registered), 1 deregistered excluded → 100%
        assert self.reg.registration_rate_pct() == 100.0

    def test_registration_rate_none_when_empty(self):
        assert self.reg.registration_rate_pct() is None

    def test_total_retry_count(self):
        r = self.reg.register_installation(MPAN, INSTALL, SERIAL)
        self.reg.mark_failed(r.record_id, dt.date(2024, 3, 12))
        self.reg.mark_failed(r.record_id, dt.date(2024, 3, 15))
        assert self.reg.total_retry_count() == 2

    def test_dcc_summary_includes_key_counts(self):
        r = self.reg.register_installation(MPAN, INSTALL, SERIAL)
        self.reg.mark_registered(r.record_id, dt.date(2024, 3, 10))
        s = self.reg.dcc_summary(dt.date(2024, 4, 1))
        assert "1 installations" in s and "100.0%" in s

    def test_dcc_summary_empty(self):
        s = self.reg.dcc_summary(dt.date(2024, 4, 1))
        assert "0 installations" in s
