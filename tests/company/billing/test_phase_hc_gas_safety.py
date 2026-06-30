"""Tests for Gas Safety Incident Register -- Phase HC (GSIUR 1998 / RIDDOR 2013)."""
import datetime as dt
import pytest
from company.billing.gas_safety_incident_register import (
    GasSafetyIncidentType, IncidentSeverity, IncidentStatus,
    GasSafetyIncidentRecord, GasSafetyIncidentRegister,
    _RIDDOR_TYPES, _RIDDOR_DAYS,
)

TODAY = dt.date(2024, 6, 10)
ACC = "A001"
MPRN = "2000000000001"


def make_reg():
    return GasSafetyIncidentRegister()


def report(reg=None, account=ACC, mprn=MPRN,
           itype=GasSafetyIncidentType.GAS_ESCAPE,
           severity=IncidentSeverity.LOW, date=TODAY, injuries=0):
    if reg is None:
        reg = make_reg()
    return reg, reg.report_incident(account, mprn, itype, severity, date, injuries)


class TestRIDDORRequired:
    def test_co_confirmed_requires_riddor(self):
        _, rec = report(itype=GasSafetyIncidentType.CO_CONFIRMED, severity=IncidentSeverity.HIGH)
        assert rec.requires_riddor_notification

    def test_explosion_requires_riddor(self):
        _, rec = report(itype=GasSafetyIncidentType.EXPLOSION, severity=IncidentSeverity.HIGH)
        assert rec.requires_riddor_notification

    def test_high_severity_requires_riddor(self):
        _, rec = report(itype=GasSafetyIncidentType.GAS_ESCAPE, severity=IncidentSeverity.HIGH)
        assert rec.requires_riddor_notification

    def test_fatal_requires_riddor(self):
        _, rec = report(itype=GasSafetyIncidentType.GAS_ESCAPE, severity=IncidentSeverity.FATAL)
        assert rec.requires_riddor_notification

    def test_injuries_requires_riddor(self):
        _, rec = report(itype=GasSafetyIncidentType.GAS_ESCAPE, severity=IncidentSeverity.LOW,
                       injuries=1)
        assert rec.requires_riddor_notification

    def test_low_severity_gas_escape_no_injury_no_riddor(self):
        _, rec = report(itype=GasSafetyIncidentType.GAS_ESCAPE, severity=IncidentSeverity.LOW)
        assert not rec.requires_riddor_notification


class TestGasSafetyIncidentRecord:
    def test_is_open_when_reported(self):
        _, rec = report()
        assert rec.is_open

    def test_riddor_deadline_when_required(self):
        _, rec = report(itype=GasSafetyIncidentType.CO_CONFIRMED, severity=IncidentSeverity.HIGH)
        expected = TODAY + dt.timedelta(days=_RIDDOR_DAYS)
        assert rec.riddor_deadline == expected

    def test_riddor_deadline_none_when_not_required(self):
        _, rec = report(severity=IncidentSeverity.LOW)
        assert rec.riddor_deadline is None

    def test_is_riddor_overdue(self):
        _, rec = report(itype=GasSafetyIncidentType.CO_CONFIRMED, severity=IncidentSeverity.HIGH)
        deadline = TODAY + dt.timedelta(days=_RIDDOR_DAYS)
        assert rec.is_riddor_overdue(deadline + dt.timedelta(days=1))

    def test_is_not_riddor_overdue_on_deadline(self):
        _, rec = report(itype=GasSafetyIncidentType.CO_CONFIRMED, severity=IncidentSeverity.HIGH)
        deadline = TODAY + dt.timedelta(days=_RIDDOR_DAYS)
        assert not rec.is_riddor_overdue(deadline)

    def test_is_not_riddor_overdue_when_notified(self):
        reg, rec = report(itype=GasSafetyIncidentType.CO_CONFIRMED, severity=IncidentSeverity.HIGH)
        reg.mark_made_safe(rec.incident_id, TODAY)
        reg.notify_riddor(rec.incident_id, TODAY)
        result = reg.incidents_for_account(ACC)[0]
        far_future = dt.date(2030, 1, 1)
        assert not result.is_riddor_overdue(far_future)

    def test_incident_summary_contains_id(self):
        _, rec = report()
        assert rec.incident_id in rec.incident_summary()

    def test_frozen(self):
        _, rec = report()
        with pytest.raises((AttributeError, TypeError)):
            rec.account_id = "other"


class TestGasSafetyIncidentRegister:
    def setup_method(self):
        self.reg = make_reg()

    def _report(self, account=ACC, mprn=MPRN,
                itype=GasSafetyIncidentType.GAS_ESCAPE,
                severity=IncidentSeverity.LOW, date=TODAY, injuries=0):
        return self.reg.report_incident(account, mprn, itype, severity, date, injuries)

    def test_report_returns_reported_status(self):
        rec = self._report()
        assert rec.status == IncidentStatus.REPORTED

    def test_auto_id_prefix(self):
        rec = self._report()
        assert rec.incident_id.startswith("GSI-")

    def test_auto_id_increments(self):
        r1 = self._report()
        r2 = self._report(account="A002", mprn="3000000000001")
        assert r1.incident_id != r2.incident_id

    def test_negative_injuries_raises(self):
        with pytest.raises(ValueError):
            self._report(injuries=-1)

    def test_dispatch_engineer(self):
        rec = self._report()
        dispatched = self.reg.dispatch_engineer(rec.incident_id, TODAY, "GS12345")
        assert dispatched.status == IncidentStatus.ENGINEER_DISPATCHED
        assert dispatched.gas_safe_ref == "GS12345"

    def test_dispatch_non_reported_raises(self):
        rec = self._report()
        self.reg.dispatch_engineer(rec.incident_id, TODAY)
        with pytest.raises(ValueError):
            self.reg.dispatch_engineer(rec.incident_id, TODAY)

    def test_isolate_supply(self):
        rec = self._report()
        isolated = self.reg.isolate_supply(rec.incident_id)
        assert isolated.status == IncidentStatus.SUPPLY_ISOLATED

    def test_isolate_from_dispatched(self):
        rec = self._report()
        self.reg.dispatch_engineer(rec.incident_id, TODAY)
        isolated = self.reg.isolate_supply(rec.incident_id)
        assert isolated.status == IncidentStatus.SUPPLY_ISOLATED

    def test_isolate_made_safe_raises(self):
        rec = self._report()
        self.reg.mark_made_safe(rec.incident_id, TODAY)
        with pytest.raises(ValueError):
            self.reg.isolate_supply(rec.incident_id)

    def test_mark_made_safe(self):
        rec = self._report()
        safe = self.reg.mark_made_safe(rec.incident_id, TODAY)
        assert safe.status == IncidentStatus.MADE_SAFE

    def test_notify_riddor_sets_date(self):
        rec = self._report(itype=GasSafetyIncidentType.CO_CONFIRMED,
                           severity=IncidentSeverity.HIGH)
        self.reg.mark_made_safe(rec.incident_id, TODAY)
        notified = self.reg.notify_riddor(rec.incident_id, TODAY)
        assert notified.status == IncidentStatus.RIDDOR_NOTIFIED
        assert notified.riddor_notified_date == TODAY

    def test_notify_riddor_not_required_raises(self):
        rec = self._report(itype=GasSafetyIncidentType.GAS_ESCAPE, severity=IncidentSeverity.LOW)
        with pytest.raises(ValueError):
            self.reg.notify_riddor(rec.incident_id, TODAY)

    def test_close_after_made_safe(self):
        rec = self._report()
        self.reg.mark_made_safe(rec.incident_id, TODAY)
        closed = self.reg.close_incident(rec.incident_id, TODAY)
        assert closed.status == IncidentStatus.CLOSED

    def test_close_before_made_safe_raises(self):
        rec = self._report()
        with pytest.raises(ValueError):
            self.reg.close_incident(rec.incident_id, TODAY)

    def test_open_incidents(self):
        r1 = self._report()
        self._report(account="A002", mprn="3000000000001")
        self.reg.mark_made_safe(r1.incident_id, TODAY)
        self.reg.close_incident(r1.incident_id, TODAY)
        assert len(self.reg.open_incidents) == 1

    def test_riddor_overdue(self):
        self._report(itype=GasSafetyIncidentType.CO_CONFIRMED, severity=IncidentSeverity.HIGH)
        deadline = TODAY + dt.timedelta(days=_RIDDOR_DAYS)
        overdue = self.reg.riddor_overdue(deadline + dt.timedelta(days=1))
        assert len(overdue) == 1

    def test_riddor_required_open(self):
        self._report(itype=GasSafetyIncidentType.EXPLOSION, severity=IncidentSeverity.HIGH)
        self._report(account="A002", mprn="3000000000001",
                     itype=GasSafetyIncidentType.GAS_ESCAPE, severity=IncidentSeverity.LOW)
        assert len(self.reg.riddor_required_open()) == 1

    def test_incidents_for_account(self):
        self._report(account=ACC)
        self._report(account="A002", mprn="3000000000001")
        assert len(self.reg.incidents_for_account(ACC)) == 1

    def test_total_injuries(self):
        self._report(injuries=2)
        self._report(account="A002", mprn="3000000000001", injuries=1)
        assert self.reg.total_injuries == 3

    def test_fatal_incidents(self):
        self._report(severity=IncidentSeverity.FATAL)
        self._report(account="A002", mprn="3000000000001", severity=IncidentSeverity.LOW)
        assert len(self.reg.fatal_incidents) == 1

    def test_summary_contains_total(self):
        self._report()
        s = self.reg.gas_safety_register_summary(TODAY)
        assert "1 total" in s

    def test_empty_summary(self):
        s = self.reg.gas_safety_register_summary(TODAY)
        assert "0 total" in s
