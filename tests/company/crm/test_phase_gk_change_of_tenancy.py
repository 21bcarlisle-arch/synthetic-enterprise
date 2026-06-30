import datetime as dt
import pytest
from company.crm.change_of_tenancy_register import (
    CoTType, CoTStatus, CoTRecord, ChangeOfTenancyRegister,
    _ABANDON_ATTEMPTS, _ABANDON_DAYS,
)

ENTRY = dt.date(2024, 3, 1)
AS_OF = dt.date(2024, 4, 30)
MPAN = "1000000000001"

def make_record(status=CoTStatus.NOTIFIED, attempts=0):
    return CoTRecord(
        cot_id="COT-00001", mpan=MPAN, entry_date=ENTRY,
        cot_type=CoTType.NEW_TENANT, status=status, contact_attempts=attempts)

class TestCoTRecord:
    def test_is_open_notified(self):
        assert make_record(CoTStatus.NOTIFIED).is_open
    def test_is_open_supply_taken(self):
        assert make_record(CoTStatus.SUPPLY_TAKEN).is_open
    def test_is_not_open_abandoned(self):
        assert not make_record(CoTStatus.ABANDONED).is_open
    def test_is_terminal_declined(self):
        assert make_record(CoTStatus.SUPPLY_DECLINED).is_terminal
    def test_is_terminal_abandoned(self):
        assert make_record(CoTStatus.ABANDONED).is_terminal
    def test_mpas_notification_due(self):
        # entry Mon 2024-03-04; +2WD = Wed 2024-03-06
        r = CoTRecord(cot_id="X", mpan=MPAN, entry_date=dt.date(2024, 3, 4),
                      cot_type=CoTType.NEW_TENANT)
        assert r.mpas_notification_due == dt.date(2024, 3, 6)
    def test_read_submission_due(self):
        # entry Mon 2024-03-04; +10WD = Mon 2024-03-18
        r = CoTRecord(cot_id="X", mpan=MPAN, entry_date=dt.date(2024, 3, 4),
                      cot_type=CoTType.NEW_TENANT)
        assert r.read_submission_due == dt.date(2024, 3, 18)
    def test_is_abandon_candidate_all_conditions_met(self):
        r = make_record(CoTStatus.NOTIFIED, attempts=_ABANDON_ATTEMPTS)
        assert r.is_abandon_candidate(ENTRY + dt.timedelta(_ABANDON_DAYS))
    def test_is_not_abandon_candidate_too_few_attempts(self):
        r = make_record(CoTStatus.NOTIFIED, attempts=_ABANDON_ATTEMPTS - 1)
        assert not r.is_abandon_candidate(ENTRY + dt.timedelta(_ABANDON_DAYS))
    def test_is_not_abandon_candidate_too_soon(self):
        r = make_record(CoTStatus.NOTIFIED, attempts=_ABANDON_ATTEMPTS)
        assert not r.is_abandon_candidate(ENTRY + dt.timedelta(_ABANDON_DAYS - 1))
    def test_is_not_abandon_candidate_when_taken(self):
        r = make_record(CoTStatus.SUPPLY_TAKEN, attempts=_ABANDON_ATTEMPTS)
        assert not r.is_abandon_candidate(ENTRY + dt.timedelta(_ABANDON_DAYS + 5))
    def test_cot_summary_string(self):
        r = make_record()
        assert "COT-00001" in r.cot_summary()
    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.status = CoTStatus.SUPPLY_TAKEN

class TestChangeOfTenancyRegister:
    def setup_method(self):
        self.reg = ChangeOfTenancyRegister()
    def test_notify_cot_stored(self):
        r = self.reg.notify_cot(MPAN, ENTRY)
        assert r.status == CoTStatus.NOTIFIED
    def test_auto_id_increments(self):
        r1 = self.reg.notify_cot(MPAN, ENTRY)
        r2 = self.reg.notify_cot("1000000000002", ENTRY)
        assert r1.cot_id != r2.cot_id
    def test_accept_supply(self):
        r = self.reg.notify_cot(MPAN, ENTRY)
        taken = self.reg.accept_supply(r.cot_id, "DOM-001", ENTRY + dt.timedelta(1))
        assert taken.status == CoTStatus.SUPPLY_TAKEN and taken.account_id == "DOM-001"
    def test_decline_supply(self):
        r = self.reg.notify_cot(MPAN, ENTRY)
        declined = self.reg.decline_supply(r.cot_id)
        assert declined.status == CoTStatus.SUPPLY_DECLINED
    def test_log_contact_attempt(self):
        r = self.reg.notify_cot(MPAN, ENTRY)
        updated = self.reg.log_contact_attempt(r.cot_id)
        assert updated.contact_attempts == 1
    def test_log_contact_attempt_accumulates(self):
        r = self.reg.notify_cot(MPAN, ENTRY)
        self.reg.log_contact_attempt(r.cot_id)
        updated = self.reg.log_contact_attempt(r.cot_id)
        assert updated.contact_attempts == 2
    def test_mark_abandoned(self):
        r = self.reg.notify_cot(MPAN, ENTRY)
        ab = self.reg.mark_abandoned(r.cot_id)
        assert ab.status == CoTStatus.ABANDONED
    def test_close(self):
        r = self.reg.notify_cot(MPAN, ENTRY)
        self.reg.accept_supply(r.cot_id, "DOM-001", ENTRY + dt.timedelta(1))
        closed = self.reg.close(r.cot_id, ENTRY + dt.timedelta(30))
        assert closed.status == CoTStatus.CLOSED
    def test_update_missing_raises(self):
        with pytest.raises(KeyError):
            self.reg.decline_supply("COT-99999")
    def test_open_cots(self):
        r1 = self.reg.notify_cot(MPAN, ENTRY)
        r2 = self.reg.notify_cot("1000000000002", ENTRY)
        self.reg.decline_supply(r1.cot_id)
        assert len(self.reg.open_cots()) == 1
    def test_abandon_candidates(self):
        r = self.reg.notify_cot(MPAN, ENTRY)
        for _ in range(_ABANDON_ATTEMPTS):
            self.reg.log_contact_attempt(r.cot_id)
        candidates = self.reg.abandon_candidates(ENTRY + dt.timedelta(_ABANDON_DAYS))
        assert len(candidates) == 1
    def test_history_for_mpan(self):
        self.reg.notify_cot(MPAN, ENTRY)
        self.reg.notify_cot(MPAN, ENTRY + dt.timedelta(365))
        self.reg.notify_cot("1000000000002", ENTRY)
        assert len(self.reg.history_for_mpan(MPAN)) == 2
    def test_active_supply_for_mpan(self):
        r1 = self.reg.notify_cot(MPAN, ENTRY)
        r2 = self.reg.notify_cot(MPAN, ENTRY + dt.timedelta(365))
        self.reg.accept_supply(r1.cot_id, "DOM-001", ENTRY)
        self.reg.accept_supply(r2.cot_id, "DOM-002", ENTRY + dt.timedelta(365))
        active = self.reg.active_supply_for_mpan(MPAN)
        assert active.account_id == "DOM-002"
    def test_active_supply_none_when_not_taken(self):
        self.reg.notify_cot(MPAN, ENTRY)
        assert self.reg.active_supply_for_mpan(MPAN) is None
    def test_by_type(self):
        self.reg.notify_cot(MPAN, ENTRY, CoTType.NEW_TENANT)
        self.reg.notify_cot("1000000000002", ENTRY, CoTType.NEW_OWNER)
        assert len(self.reg.by_type(CoTType.NEW_TENANT)) == 1
    def test_conversion_rate_pct(self):
        r1 = self.reg.notify_cot(MPAN, ENTRY)
        r2 = self.reg.notify_cot("1000000000002", ENTRY)
        self.reg.accept_supply(r1.cot_id, "DOM-001", ENTRY)
        self.reg.decline_supply(r2.cot_id)
        # taken=1, terminal (non-taken)=1 (declined); 1/(1+1)*100 = 50.0%
        assert self.reg.conversion_rate_pct() == 50.0
    def test_conversion_rate_none_when_no_terminal(self):
        self.reg.notify_cot(MPAN, ENTRY)
        assert self.reg.conversion_rate_pct() is None
    def test_cot_summary(self):
        self.reg.notify_cot(MPAN, ENTRY)
        s = self.reg.cot_summary(AS_OF)
        assert "1 CoTs" in s
    def test_empty_summary(self):
        s = self.reg.cot_summary(AS_OF)
        assert "0 CoTs" in s
