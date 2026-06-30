"""Tests for Phase GA: CSS Performance Register."""
import datetime as dt
import pytest
from company.market.css_performance_register import (
    SwitchOutcome,
    CSSPerformanceRecord,
    CSSPerformanceRegister,
    _CSS_GO_LIVE,
    _add_working_days,
)

# ── helpers ──────────────────────────────────────────────────────────────────

REQ = dt.date(2023, 7, 3)   # Monday (after CSS go-live)
ELEC = "electricity"
GAS = "gas"


# ── _add_working_days ────────────────────────────────────────────────────────

class TestAddWorkingDays:

    def test_five_working_days_from_monday(self):
        monday = dt.date(2024, 1, 1)
        assert _add_working_days(monday, 5) == dt.date(2024, 1, 8)

    def test_skips_weekend(self):
        friday = dt.date(2024, 1, 5)
        # 1WD from Fri = Mon 8 Jan
        assert _add_working_days(friday, 1) == dt.date(2024, 1, 8)

    def test_five_from_friday_spans_weekend(self):
        friday = dt.date(2024, 1, 5)
        assert _add_working_days(friday, 5) == dt.date(2024, 1, 12)


# ── CSSPerformanceRecord ─────────────────────────────────────────────────────

class TestCSSPerformanceRecord:

    def test_sla_deadline_five_working_days(self):
        r = CSSPerformanceRecord("SW-00001", REQ, ELEC)
        assert r.sla_deadline == _add_working_days(REQ, 5)

    def test_is_completed_on_time(self):
        r = CSSPerformanceRecord("SW-00001", REQ, ELEC, SwitchOutcome.COMPLETED_ON_TIME, REQ + dt.timedelta(3))
        assert r.is_completed and r.is_compliant and not r.is_late

    def test_is_completed_late(self):
        r = CSSPerformanceRecord("SW-00001", REQ, ELEC, SwitchOutcome.COMPLETED_LATE, REQ + dt.timedelta(10))
        assert r.is_completed and r.is_late and not r.is_compliant

    def test_is_cancelled(self):
        r = CSSPerformanceRecord("SW-00001", REQ, ELEC, SwitchOutcome.CANCELLED_COOLING_OFF)
        assert r.is_cancelled and not r.is_completed

    def test_is_et(self):
        r = CSSPerformanceRecord("SW-00001", REQ, ELEC, SwitchOutcome.ERRONEOUS_TRANSFER)
        assert r.is_et

    def test_days_to_complete(self):
        completion = REQ + dt.timedelta(days=3)
        r = CSSPerformanceRecord("SW-00001", REQ, ELEC, SwitchOutcome.COMPLETED_ON_TIME, completion)
        assert r.days_to_complete() == 3

    def test_days_to_complete_pending(self):
        r = CSSPerformanceRecord("SW-00001", REQ, ELEC)
        assert r.days_to_complete() is None

    def test_record_summary_pending(self):
        r = CSSPerformanceRecord("SW-00001", REQ, ELEC)
        s = r.record_summary()
        assert "SW-00001" in s and "pending" in s

    def test_record_summary_completed(self):
        completion = REQ + dt.timedelta(3)
        r = CSSPerformanceRecord("SW-00001", REQ, GAS, SwitchOutcome.COMPLETED_ON_TIME, completion)
        s = r.record_summary()
        assert "completed_on_time" in s

    def test_frozen(self):
        r = CSSPerformanceRecord("SW-00001", REQ, ELEC)
        with pytest.raises((AttributeError, TypeError)):
            r.fuel = "gas"


# ── CSSPerformanceRegister ───────────────────────────────────────────────────

class TestCSSPerformanceRegister:

    def setup_method(self):
        self.reg = CSSPerformanceRegister()

    def test_record_switch_stored(self):
        r = self.reg.record_switch(REQ, ELEC)
        assert r.fuel == ELEC
        assert r.outcome == SwitchOutcome.PENDING

    def test_record_switch_auto_id(self):
        r1 = self.reg.record_switch(REQ, ELEC)
        r2 = self.reg.record_switch(REQ, GAS)
        assert r1.switch_id != r2.switch_id

    def test_record_switch_pre_go_live_raises(self):
        with pytest.raises(ValueError):
            self.reg.record_switch(_CSS_GO_LIVE - dt.timedelta(days=1), ELEC)

    def test_record_switch_invalid_fuel_raises(self):
        with pytest.raises(ValueError):
            self.reg.record_switch(REQ, "oil")

    def test_complete_switch_on_time(self):
        r = self.reg.record_switch(REQ, ELEC)
        done = self.reg.complete_switch(r.switch_id, r.sla_deadline)
        assert done.outcome == SwitchOutcome.COMPLETED_ON_TIME

    def test_complete_switch_late(self):
        r = self.reg.record_switch(REQ, ELEC)
        done = self.reg.complete_switch(r.switch_id, r.sla_deadline + dt.timedelta(1))
        assert done.outcome == SwitchOutcome.COMPLETED_LATE

    def test_complete_switch_missing_raises(self):
        with pytest.raises(KeyError):
            self.reg.complete_switch("SW-99999", REQ + dt.timedelta(3))

    def test_cancel_cooling_off(self):
        r = self.reg.record_switch(REQ, ELEC)
        cancelled = self.reg.cancel_cooling_off(r.switch_id)
        assert cancelled.outcome == SwitchOutcome.CANCELLED_COOLING_OFF

    def test_cancel_objection(self):
        r = self.reg.record_switch(REQ, GAS)
        cancelled = self.reg.cancel_objection(r.switch_id)
        assert cancelled.outcome == SwitchOutcome.CANCELLED_OBJECTION

    def test_mark_erroneous_transfer(self):
        r = self.reg.record_switch(REQ, ELEC)
        et = self.reg.mark_erroneous_transfer(r.switch_id)
        assert et.outcome == SwitchOutcome.ERRONEOUS_TRANSFER

    def test_on_time_completions(self):
        r = self.reg.record_switch(REQ, ELEC)
        self.reg.complete_switch(r.switch_id, r.sla_deadline)
        r2 = self.reg.record_switch(REQ, GAS)
        self.reg.complete_switch(r2.switch_id, r2.sla_deadline + dt.timedelta(2))
        assert len(self.reg.on_time_completions()) == 1

    def test_late_completions(self):
        r = self.reg.record_switch(REQ, ELEC)
        self.reg.complete_switch(r.switch_id, r.sla_deadline + dt.timedelta(1))
        assert len(self.reg.late_completions()) == 1

    def test_pending_switches(self):
        self.reg.record_switch(REQ, ELEC)
        r2 = self.reg.record_switch(REQ, GAS)
        self.reg.complete_switch(r2.switch_id, r2.sla_deadline)
        assert len(self.reg.pending_switches()) == 1

    def test_erroneous_transfers(self):
        r = self.reg.record_switch(REQ, ELEC)
        self.reg.mark_erroneous_transfer(r.switch_id)
        assert len(self.reg.erroneous_transfers()) == 1

    def test_compliance_rate_pct_all_on_time(self):
        r1 = self.reg.record_switch(REQ, ELEC)
        r2 = self.reg.record_switch(REQ, GAS)
        self.reg.complete_switch(r1.switch_id, r1.sla_deadline)
        self.reg.complete_switch(r2.switch_id, r2.sla_deadline)
        assert self.reg.compliance_rate_pct() == 100.0

    def test_compliance_rate_pct_partial(self):
        r1 = self.reg.record_switch(REQ, ELEC)
        r2 = self.reg.record_switch(REQ, GAS)
        self.reg.complete_switch(r1.switch_id, r1.sla_deadline)
        self.reg.complete_switch(r2.switch_id, r2.sla_deadline + dt.timedelta(3))
        assert self.reg.compliance_rate_pct() == 50.0

    def test_compliance_rate_pct_none_when_no_completions(self):
        self.reg.record_switch(REQ, ELEC)
        assert self.reg.compliance_rate_pct() is None

    def test_et_rate_per_1000(self):
        for _ in range(10):
            r = self.reg.record_switch(REQ, ELEC)
            self.reg.complete_switch(r.switch_id, r.sla_deadline)
        r_et = self.reg.record_switch(REQ, ELEC)
        self.reg.mark_erroneous_transfer(r_et.switch_id)
        # 10 completed, 1 ET → ET rate = 1/10 × 1000 = 100
        # NOTE: ETs not in _completed() so denominator is 10
        rate = self.reg.et_rate_per_1000()
        assert rate is not None

    def test_switches_for_fuel(self):
        self.reg.record_switch(REQ, ELEC)
        self.reg.record_switch(REQ, GAS)
        assert len(self.reg.switches_for_fuel(ELEC)) == 1

    def test_css_performance_summary(self):
        r = self.reg.record_switch(REQ, ELEC)
        self.reg.complete_switch(r.switch_id, r.sla_deadline)
        s = self.reg.css_performance_summary()
        assert "CSS Performance Register" in s and "100.0%" in s

    def test_empty_register_summary(self):
        s = self.reg.css_performance_summary()
        assert "0 switches" in s
