"""Tests for Phase FY: Debt Respite (Breathing Space) Register."""
import datetime as dt
import pytest
from company.billing.breathing_space_register import (
    BreathingSpaceType,
    BreathingSpaceStatus,
    BreathingSpaceRecord,
    BreathingSpaceRegister,
    _BREATHING_SPACE_START_DATE,
    _STANDARD_DURATION_DAYS,
)

SCHEME_START = _BREATHING_SPACE_START_DATE  # 2021-05-04

# ── helpers ──────────────────────────────────────────────────────────────────

def make_record(
    record_id="BS-00001",
    account_id="ACC001",
    bs_type=BreathingSpaceType.STANDARD,
    start_date=None,
    debt=800.0,
    interest=50.0,
    status=BreathingSpaceStatus.ACTIVE,
    end_date=None,
):
    start_date = start_date or dt.date(2023, 6, 1)
    return BreathingSpaceRecord(
        record_id=record_id,
        account_id=account_id,
        bs_type=bs_type,
        start_date=start_date,
        debt_frozen_gbp=debt,
        interest_frozen_gbp=interest,
        status=status,
        end_date=end_date,
    )


# ── BreathingSpaceRecord ─────────────────────────────────────────────────────

class TestBreathingSpaceRecord:

    def test_expected_end_date_standard(self):
        r = make_record(start_date=dt.date(2023, 6, 1))
        assert r.expected_end_date == dt.date(2023, 7, 31)

    def test_expected_end_date_mh_is_none(self):
        r = make_record(bs_type=BreathingSpaceType.MENTAL_HEALTH_CRISIS)
        assert r.expected_end_date is None

    def test_is_active_within_60_days(self):
        r = make_record(start_date=dt.date(2023, 6, 1))
        assert r.is_active_as_of(dt.date(2023, 7, 31))

    def test_is_active_false_after_60_days(self):
        r = make_record(start_date=dt.date(2023, 6, 1))
        assert not r.is_active_as_of(dt.date(2023, 8, 1))

    def test_is_active_false_when_completed(self):
        r = make_record(status=BreathingSpaceStatus.COMPLETED)
        assert not r.is_active_as_of(dt.date(2023, 6, 15))

    def test_mh_crisis_always_active_while_status_active(self):
        r = make_record(
            bs_type=BreathingSpaceType.MENTAL_HEALTH_CRISIS,
            start_date=dt.date(2023, 1, 1),
        )
        assert r.is_active_as_of(dt.date(2024, 12, 31))  # no end date for MH

    def test_days_elapsed(self):
        r = make_record(start_date=dt.date(2023, 6, 1))
        assert r.days_elapsed(dt.date(2023, 6, 11)) == 10

    def test_days_remaining_standard_mid_period(self):
        r = make_record(start_date=dt.date(2023, 6, 1))
        # 60 days from Jun 1 = Jul 31; from Jun 11 = 50 days remaining
        remaining = r.days_remaining(dt.date(2023, 6, 11))
        assert remaining == 50

    def test_days_remaining_zero_when_expired(self):
        r = make_record(start_date=dt.date(2023, 6, 1))
        assert r.days_remaining(dt.date(2023, 8, 1)) == 0

    def test_days_remaining_none_for_mh(self):
        r = make_record(bs_type=BreathingSpaceType.MENTAL_HEALTH_CRISIS)
        assert r.days_remaining(dt.date(2023, 12, 1)) is None

    def test_record_summary_contains_key_fields(self):
        r = make_record()
        s = r.record_summary()
        assert "BS-00001" in s
        assert "ACC001" in s
        assert "£800.00" in s

    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.debt_frozen_gbp = 999.0


# ── BreathingSpaceRegister ───────────────────────────────────────────────────

class TestBreathingSpaceRegister:

    def setup_method(self):
        self.reg = BreathingSpaceRegister()

    def test_register_entry_stored(self):
        r = self.reg.register_entry("ACC001", BreathingSpaceType.STANDARD, dt.date(2023, 6, 1), 500.0)
        assert r.account_id == "ACC001"
        assert r.status == BreathingSpaceStatus.ACTIVE

    def test_register_entry_auto_id(self):
        r1 = self.reg.register_entry("A1", BreathingSpaceType.STANDARD, dt.date(2023, 6, 1), 400.0)
        r2 = self.reg.register_entry("A2", BreathingSpaceType.STANDARD, dt.date(2023, 6, 2), 300.0)
        assert r1.record_id != r2.record_id

    def test_register_entry_pre_scheme_raises(self):
        with pytest.raises(ValueError):
            self.reg.register_entry("ACC001", BreathingSpaceType.STANDARD, dt.date(2021, 5, 3), 400.0)

    def test_complete(self):
        r = self.reg.register_entry("ACC001", BreathingSpaceType.STANDARD, dt.date(2023, 6, 1), 500.0)
        completed = self.reg.complete(r.record_id, dt.date(2023, 7, 31))
        assert completed.status == BreathingSpaceStatus.COMPLETED
        assert completed.end_date == dt.date(2023, 7, 31)

    def test_cancel_by_adviser(self):
        r = self.reg.register_entry("ACC001", BreathingSpaceType.STANDARD, dt.date(2023, 6, 1), 500.0)
        cancelled = self.reg.cancel_by_adviser(r.record_id, dt.date(2023, 6, 20))
        assert cancelled.status == BreathingSpaceStatus.CANCELLED_BY_ADVISER
        assert cancelled.end_date == dt.date(2023, 6, 20)

    def test_update_missing_raises(self):
        with pytest.raises(KeyError):
            self.reg.complete("BS-99999", dt.date(2023, 7, 31))

    def test_records_for_account(self):
        self.reg.register_entry("ACC001", BreathingSpaceType.STANDARD, dt.date(2023, 6, 1), 400.0)
        self.reg.register_entry("ACC001", BreathingSpaceType.STANDARD, dt.date(2024, 1, 1), 300.0)
        self.reg.register_entry("ACC002", BreathingSpaceType.STANDARD, dt.date(2023, 7, 1), 200.0)
        assert len(self.reg.records_for_account("ACC001")) == 2

    def test_active_records_as_of(self):
        r1 = self.reg.register_entry("ACC001", BreathingSpaceType.STANDARD, dt.date(2023, 6, 1), 400.0)
        r2 = self.reg.register_entry("ACC002", BreathingSpaceType.STANDARD, dt.date(2023, 6, 1), 300.0)
        # complete r1
        self.reg.complete(r1.record_id, dt.date(2023, 7, 31))
        # Jun 15: r2 still active (not completed, within 60d)
        active = self.reg.active_records(dt.date(2023, 6, 15))
        assert len(active) == 1  # only r2 (r1 is COMPLETED)

    def test_mental_health_crisis_records(self):
        self.reg.register_entry("ACC001", BreathingSpaceType.MENTAL_HEALTH_CRISIS, dt.date(2023, 3, 1), 600.0)
        self.reg.register_entry("ACC002", BreathingSpaceType.STANDARD, dt.date(2023, 4, 1), 400.0)
        mh = self.reg.mental_health_crisis_records()
        assert len(mh) == 1 and mh[0].account_id == "ACC001"

    def test_standard_records(self):
        self.reg.register_entry("ACC001", BreathingSpaceType.STANDARD, dt.date(2023, 4, 1), 400.0)
        self.reg.register_entry("ACC002", BreathingSpaceType.MENTAL_HEALTH_CRISIS, dt.date(2023, 3, 1), 600.0)
        assert len(self.reg.standard_records()) == 1

    def test_total_debt_frozen_gbp(self):
        self.reg.register_entry("ACC001", BreathingSpaceType.STANDARD, dt.date(2023, 6, 1), 400.0)
        self.reg.register_entry("ACC002", BreathingSpaceType.STANDARD, dt.date(2023, 6, 1), 300.0)
        assert abs(self.reg.total_debt_frozen_gbp() - 700.0) < 1e-9

    def test_total_interest_frozen_gbp(self):
        self.reg.register_entry("ACC001", BreathingSpaceType.STANDARD, dt.date(2023, 6, 1), 400.0, 30.0)
        self.reg.register_entry("ACC002", BreathingSpaceType.STANDARD, dt.date(2023, 6, 1), 300.0, 20.0)
        assert abs(self.reg.total_interest_frozen_gbp() - 50.0) < 1e-9

    def test_active_debt_frozen_excludes_completed(self):
        r1 = self.reg.register_entry("ACC001", BreathingSpaceType.STANDARD, dt.date(2023, 6, 1), 400.0)
        self.reg.register_entry("ACC002", BreathingSpaceType.STANDARD, dt.date(2023, 6, 1), 300.0)
        self.reg.complete(r1.record_id, dt.date(2023, 7, 31))
        # as_of Jun 15: r2 still active
        active_debt = self.reg.active_debt_frozen_gbp(dt.date(2023, 6, 15))
        assert abs(active_debt - 300.0) < 1e-9

    def test_breathing_space_summary(self):
        self.reg.register_entry("ACC001", BreathingSpaceType.STANDARD, dt.date(2023, 6, 1), 400.0)
        s = self.reg.breathing_space_summary(dt.date(2023, 6, 15))
        assert "1 total" in s
        assert "1 active" in s

    def test_empty_register_summary(self):
        s = self.reg.breathing_space_summary(dt.date(2023, 6, 1))
        assert "0 total" in s

    def test_scheme_start_date_constant(self):
        assert _BREATHING_SPACE_START_DATE == dt.date(2021, 5, 4)

    def test_standard_duration_constant(self):
        assert _STANDARD_DURATION_DAYS == 60
