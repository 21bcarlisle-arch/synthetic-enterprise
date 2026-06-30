"""Tests for Revenue Protection Visit Register -- Phase HA (GS(SS)5)."""
import datetime as dt
import pytest
from company.billing.revenue_protection_visit_register import (
    Fuel, RPVTrigger, RPVStatus, AccessOutcome,
    RevenueProtectionVisitRecord, RevenueProtectionVisitRegister,
)

TODAY = dt.date(2024, 6, 10)
TOMORROW = dt.date(2024, 6, 11)
YESTERDAY = dt.date(2024, 6, 9)
ACC = "A001"
MPAN = "1000000000001"


def make_reg():
    return RevenueProtectionVisitRegister()


def schedule(reg=None, account=ACC, mpan=MPAN, fuel=Fuel.ELECTRICITY,
             trigger=RPVTrigger.THEFT_RISK_SCORE, date=TOMORROW):
    if reg is None:
        reg = make_reg()
    return reg, reg.schedule_visit(account, mpan, fuel, trigger, date)


class TestRevenueProtectionVisitRecord:
    def test_is_terminal_scheduled_false(self):
        _, rec = schedule()
        assert not rec.is_terminal

    def test_is_not_completed_when_scheduled(self):
        _, rec = schedule()
        assert not rec.is_completed

    def test_is_not_overdue_before_scheduled_date(self):
        _, rec = schedule()
        assert not rec.is_overdue(TODAY)

    def test_is_overdue_after_scheduled_date(self):
        reg, rec = schedule(date=YESTERDAY)
        assert rec.is_overdue(TODAY)

    def test_is_not_overdue_when_terminal(self):
        reg, rec = schedule(date=YESTERDAY)
        reg.record_outcome(rec.visit_id, AccessOutcome.CLEAR, TODAY)
        completed = reg.visits_for_account(ACC)[0]
        assert not completed.is_overdue(TODAY)

    def test_requires_theft_investigation_tamper(self):
        reg, rec = schedule()
        reg.record_outcome(rec.visit_id, AccessOutcome.TAMPER_FOUND, TODAY, 500.0)
        result = reg.visits_for_account(ACC)[0]
        assert result.requires_theft_investigation

    def test_requires_theft_investigation_meter_absent(self):
        reg, rec = schedule()
        reg.record_outcome(rec.visit_id, AccessOutcome.METER_ABSENT, TODAY, 200.0)
        result = reg.visits_for_account(ACC)[0]
        assert result.requires_theft_investigation

    def test_clear_does_not_require_investigation(self):
        reg, rec = schedule()
        reg.record_outcome(rec.visit_id, AccessOutcome.CLEAR, TODAY)
        result = reg.visits_for_account(ACC)[0]
        assert not result.requires_theft_investigation

    def test_visited_clear_is_completed(self):
        reg, rec = schedule()
        reg.record_outcome(rec.visit_id, AccessOutcome.CLEAR, TODAY)
        result = reg.visits_for_account(ACC)[0]
        assert result.is_completed

    def test_aborted_access_denied_is_terminal_not_completed(self):
        reg, rec = schedule()
        reg.record_outcome(rec.visit_id, AccessOutcome.ACCESS_DENIED, TODAY)
        result = reg.visits_for_account(ACC)[0]
        assert result.is_terminal and not result.is_completed

    def test_visit_summary_contains_id(self):
        _, rec = schedule()
        assert rec.visit_id in rec.visit_summary()

    def test_frozen(self):
        _, rec = schedule()
        with pytest.raises((AttributeError, TypeError)):
            rec.account_id = "other"


class TestRevenueProtectionVisitRegister:
    def setup_method(self):
        self.reg = make_reg()

    def _schedule(self, account=ACC, mpan=MPAN, fuel=Fuel.ELECTRICITY,
                  trigger=RPVTrigger.THEFT_RISK_SCORE, date=TOMORROW):
        return self.reg.schedule_visit(account, mpan, fuel, trigger, date)

    def test_schedule_returns_scheduled_status(self):
        rec = self._schedule()
        assert rec.status == RPVStatus.SCHEDULED

    def test_auto_id_prefix(self):
        rec = self._schedule()
        assert rec.visit_id.startswith("RPV-")

    def test_auto_id_increments(self):
        r1 = self._schedule()
        r2 = self._schedule(account="A002", mpan="2000000000001")
        assert r1.visit_id != r2.visit_id

    def test_record_outcome_clear(self):
        rec = self._schedule()
        result = self.reg.record_outcome(rec.visit_id, AccessOutcome.CLEAR, TODAY)
        assert result.status == RPVStatus.VISITED_CLEAR

    def test_record_outcome_tamper(self):
        rec = self._schedule()
        result = self.reg.record_outcome(rec.visit_id, AccessOutcome.TAMPER_FOUND, TODAY, 750.0)
        assert result.status == RPVStatus.VISITED_TAMPER_FOUND

    def test_record_outcome_vacant(self):
        rec = self._schedule()
        result = self.reg.record_outcome(rec.visit_id, AccessOutcome.PROPERTY_VACANT, TODAY)
        assert result.status == RPVStatus.VISITED_VACANT

    def test_record_outcome_access_denied(self):
        rec = self._schedule()
        result = self.reg.record_outcome(rec.visit_id, AccessOutcome.ACCESS_DENIED, TODAY)
        assert result.status == RPVStatus.ABORTED_ACCESS_DENIED

    def test_record_outcome_unknown_raises(self):
        with pytest.raises(KeyError):
            self.reg.record_outcome("RPV-99999", AccessOutcome.CLEAR, TODAY)

    def test_record_outcome_non_scheduled_raises(self):
        rec = self._schedule()
        self.reg.record_outcome(rec.visit_id, AccessOutcome.CLEAR, TODAY)
        with pytest.raises(ValueError):
            self.reg.record_outcome(rec.visit_id, AccessOutcome.CLEAR, TODAY)

    def test_cancel_scheduled(self):
        rec = self._schedule()
        cancelled = self.reg.cancel(rec.visit_id)
        assert cancelled.status == RPVStatus.CANCELLED

    def test_cancel_completed_raises(self):
        rec = self._schedule()
        self.reg.record_outcome(rec.visit_id, AccessOutcome.CLEAR, TODAY)
        with pytest.raises(ValueError):
            self.reg.cancel(rec.visit_id)

    def test_cancel_unknown_raises(self):
        with pytest.raises(KeyError):
            self.reg.cancel("RPV-99999")

    def test_scheduled_visits(self):
        r1 = self._schedule()
        self._schedule(account="A002", mpan="2000000000001")
        self.reg.record_outcome(r1.visit_id, AccessOutcome.CLEAR, TODAY)
        assert len(self.reg.scheduled_visits) == 1

    def test_overdue_visits(self):
        self._schedule(date=YESTERDAY)
        self._schedule(account="A002", mpan="2000000000001", date=TOMORROW)
        overdue = self.reg.overdue_visits(TODAY)
        assert len(overdue) == 1

    def test_visits_requiring_investigation(self):
        r1 = self._schedule()
        r2 = self._schedule(account="A002", mpan="2000000000001")
        self.reg.record_outcome(r1.visit_id, AccessOutcome.TAMPER_FOUND, TODAY, 500.0)
        self.reg.record_outcome(r2.visit_id, AccessOutcome.CLEAR, TODAY)
        assert len(self.reg.visits_requiring_investigation) == 1

    def test_visits_for_account(self):
        self._schedule(account=ACC)
        self._schedule(account="A002", mpan="2000000000001")
        assert len(self.reg.visits_for_account(ACC)) == 1

    def test_by_trigger(self):
        self._schedule(trigger=RPVTrigger.THEFT_RISK_SCORE)
        self._schedule(account="A002", mpan="2000000000001", trigger=RPVTrigger.ANONYMOUS_TIP)
        assert len(self.reg.by_trigger(RPVTrigger.ANONYMOUS_TIP)) == 1

    def test_by_fuel(self):
        self._schedule(fuel=Fuel.ELECTRICITY)
        self._schedule(account="A002", mpan="2000000000001", fuel=Fuel.GAS)
        assert len(self.reg.by_fuel(Fuel.GAS)) == 1

    def test_total_estimated_loss_gbp(self):
        r1 = self._schedule()
        r2 = self._schedule(account="A002", mpan="2000000000001")
        self.reg.record_outcome(r1.visit_id, AccessOutcome.TAMPER_FOUND, TODAY, 500.0)
        self.reg.record_outcome(r2.visit_id, AccessOutcome.TAMPER_FOUND, TODAY, 300.0)
        assert abs(self.reg.total_estimated_loss_gbp - 800.0) < 1e-9

    def test_total_estimated_loss_excludes_clear(self):
        r1 = self._schedule()
        self.reg.record_outcome(r1.visit_id, AccessOutcome.CLEAR, TODAY)
        assert self.reg.total_estimated_loss_gbp == 0.0

    def test_tamper_detection_rate_none_when_no_completed(self):
        self._schedule()
        assert self.reg.tamper_detection_rate_pct() is None

    def test_tamper_detection_rate_pct(self):
        r1 = self._schedule()
        r2 = self._schedule(account="A002", mpan="2000000000001")
        self.reg.record_outcome(r1.visit_id, AccessOutcome.TAMPER_FOUND, TODAY, 500.0)
        self.reg.record_outcome(r2.visit_id, AccessOutcome.CLEAR, TODAY)
        assert abs(self.reg.tamper_detection_rate_pct() - 50.0) < 1e-9

    def test_access_denial_rate_none_when_no_terminal(self):
        self._schedule()
        assert self.reg.access_denial_rate_pct() is None

    def test_access_denial_rate_pct(self):
        r1 = self._schedule()
        r2 = self._schedule(account="A002", mpan="2000000000001")
        self.reg.record_outcome(r1.visit_id, AccessOutcome.ACCESS_DENIED, TODAY)
        self.reg.record_outcome(r2.visit_id, AccessOutcome.CLEAR, TODAY)
        assert abs(self.reg.access_denial_rate_pct() - 50.0) < 1e-9

    def test_rp_visit_summary_contains_total(self):
        self._schedule()
        s = self.reg.rp_visit_summary(TODAY)
        assert "1 total" in s

    def test_empty_summary(self):
        s = self.reg.rp_visit_summary(TODAY)
        assert "0 total" in s
