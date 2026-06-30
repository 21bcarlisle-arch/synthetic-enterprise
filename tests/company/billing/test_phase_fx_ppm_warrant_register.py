"""Tests for Phase FX: PPM Installation Warrant Register."""
import datetime as dt
import pytest
from company.billing.ppm_warrant_register import (
    WarrantStatus,
    WarrantRefusalReason,
    VulnerabilityCheck,
    PPMWarrantRecord,
    PPMWarrantRegister,
    _PPM_FORCE_FIT_BAN_DATE,
    _MIN_DEBT_FOR_WARRANT_GBP,
)

BAN_DATE = _PPM_FORCE_FIT_BAN_DATE  # 2023-04-27

# ── helpers ──────────────────────────────────────────────────────────────────

def make_check(
    checked_at=None, psr=False, medical=False, hardship=False,
    children=False, cleared=True
):
    checked_at = checked_at or dt.date(2023, 1, 15)
    return VulnerabilityCheck(
        checked_at=checked_at,
        has_psr_flag=psr,
        has_medical_equipment=medical,
        has_financial_hardship=hardship,
        has_children_under_5=children,
        assessor_cleared=cleared,
    )


def make_record(
    warrant_id="WA-00001",
    account_id="ACC001",
    app_date=None,
    debt=500.0,
    check=None,
    status=WarrantStatus.APPLIED,
):
    app_date = app_date or dt.date(2023, 1, 20)
    check = check or make_check()
    return PPMWarrantRecord(
        warrant_id=warrant_id,
        account_id=account_id,
        application_date=app_date,
        debt_at_application_gbp=debt,
        vulnerability_check=check,
        status=status,
    )


# ── VulnerabilityCheck ───────────────────────────────────────────────────────

class TestVulnerabilityCheck:

    def test_clear_to_proceed_when_cleared_and_no_medical(self):
        c = make_check(cleared=True, medical=False)
        assert c.is_clear_to_proceed

    def test_not_clear_when_assessor_not_cleared(self):
        c = make_check(cleared=False)
        assert not c.is_clear_to_proceed

    def test_not_clear_when_medical_equipment(self):
        c = make_check(cleared=True, medical=True)
        assert not c.is_clear_to_proceed

    def test_is_expired_as_of_within_28_days(self):
        c = make_check(checked_at=dt.date(2023, 1, 1))
        assert not c.is_expired_as_of(dt.date(2023, 1, 29))  # 28 days = still valid

    def test_is_expired_as_of_after_28_days(self):
        c = make_check(checked_at=dt.date(2023, 1, 1))
        assert c.is_expired_as_of(dt.date(2023, 1, 30))  # 29 days > expired

    def test_frozen(self):
        c = make_check()
        with pytest.raises((AttributeError, TypeError)):
            c.assessor_cleared = False


# ── PPMWarrantRecord ─────────────────────────────────────────────────────────

class TestPPMWarrantRecord:

    def test_is_pre_ban_before_ban_date(self):
        r = make_record(app_date=dt.date(2023, 1, 10))
        assert r.is_pre_ban

    def test_is_post_ban_on_or_after_ban_date(self):
        r = make_record(app_date=BAN_DATE)
        assert r.is_post_ban

    def test_is_active_when_applied(self):
        r = make_record(status=WarrantStatus.APPLIED)
        assert r.is_active

    def test_is_active_when_granted(self):
        r = make_record(status=WarrantStatus.GRANTED)
        assert r.is_active

    def test_is_active_false_when_executed(self):
        r = make_record(status=WarrantStatus.EXECUTED)
        assert not r.is_active

    def test_is_executed(self):
        r = make_record(status=WarrantStatus.EXECUTED)
        assert r.is_executed

    def test_meets_debt_threshold(self):
        r = make_record(debt=_MIN_DEBT_FOR_WARRANT_GBP)
        assert r.meets_debt_threshold

    def test_below_debt_threshold(self):
        r = make_record(debt=_MIN_DEBT_FOR_WARRANT_GBP - 0.01)
        assert not r.meets_debt_threshold

    def test_warrant_summary_contains_id(self):
        r = make_record()
        assert "WA-00001" in r.warrant_summary()

    def test_warrant_summary_pre_ban_label(self):
        r = make_record(app_date=dt.date(2022, 6, 1))
        assert "pre-ban" in r.warrant_summary()

    def test_warrant_summary_post_ban_label(self):
        r = make_record(app_date=BAN_DATE)
        assert "POST-BAN" in r.warrant_summary()

    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.status = WarrantStatus.EXECUTED


# ── PPMWarrantRegister ───────────────────────────────────────────────────────

class TestPPMWarrantRegister:

    def setup_method(self):
        self.reg = PPMWarrantRegister()

    def test_apply_generates_id(self):
        r = self.reg.apply_for_warrant("ACC001", dt.date(2023, 1, 10), 500.0, make_check())
        assert r.warrant_id.startswith("WA-")
        assert r.status == WarrantStatus.APPLIED

    def test_sequential_ids(self):
        r1 = self.reg.apply_for_warrant("A1", dt.date(2023, 1, 10), 500.0, make_check())
        r2 = self.reg.apply_for_warrant("A2", dt.date(2023, 1, 10), 500.0, make_check())
        assert r1.warrant_id != r2.warrant_id

    def test_update_status_to_granted(self):
        r = self.reg.apply_for_warrant("ACC001", dt.date(2023, 1, 10), 500.0, make_check())
        updated = self.reg.update_status(r.warrant_id, WarrantStatus.GRANTED, dt.date(2023, 2, 1))
        assert updated.status == WarrantStatus.GRANTED
        assert updated.outcome_date == dt.date(2023, 2, 1)

    def test_update_status_with_refusal_reason(self):
        r = self.reg.apply_for_warrant("ACC001", dt.date(2023, 1, 10), 500.0, make_check())
        updated = self.reg.update_status(
            r.warrant_id, WarrantStatus.REJECTED, dt.date(2023, 2, 1),
            refusal_reason=WarrantRefusalReason.VULNERABILITY_IDENTIFIED
        )
        assert updated.refusal_reason == WarrantRefusalReason.VULNERABILITY_IDENTIFIED

    def test_update_status_missing_raises(self):
        with pytest.raises(KeyError):
            self.reg.update_status("WA-99999", WarrantStatus.GRANTED, dt.date(2023, 1, 1))

    def test_records_for_account(self):
        self.reg.apply_for_warrant("ACC001", dt.date(2023, 1, 10), 500.0, make_check())
        self.reg.apply_for_warrant("ACC001", dt.date(2023, 2, 5), 600.0, make_check())
        self.reg.apply_for_warrant("ACC002", dt.date(2023, 1, 15), 300.0, make_check())
        assert len(self.reg.records_for_account("ACC001")) == 2
        assert len(self.reg.records_for_account("ACC002")) == 1

    def test_active_warrants(self):
        r1 = self.reg.apply_for_warrant("ACC001", dt.date(2023, 1, 10), 500.0, make_check())
        self.reg.apply_for_warrant("ACC002", dt.date(2023, 1, 15), 400.0, make_check())
        self.reg.update_status(r1.warrant_id, WarrantStatus.EXECUTED, dt.date(2023, 2, 1))
        assert len(self.reg.active_warrants()) == 1

    def test_granted_warrants(self):
        r = self.reg.apply_for_warrant("ACC001", dt.date(2023, 1, 10), 500.0, make_check())
        self.reg.update_status(r.warrant_id, WarrantStatus.GRANTED, dt.date(2023, 2, 1))
        assert len(self.reg.granted_warrants()) == 1

    def test_executed_warrants(self):
        r = self.reg.apply_for_warrant("ACC001", dt.date(2023, 1, 10), 500.0, make_check())
        self.reg.update_status(r.warrant_id, WarrantStatus.EXECUTED, dt.date(2023, 2, 15))
        assert len(self.reg.executed_warrants()) == 1

    def test_post_ban_applications(self):
        self.reg.apply_for_warrant("ACC001", dt.date(2022, 12, 1), 500.0, make_check())
        self.reg.apply_for_warrant("ACC002", BAN_DATE, 500.0, make_check())
        post_ban = self.reg.post_ban_applications()
        assert len(post_ban) == 1
        assert post_ban[0].account_id == "ACC002"

    def test_vulnerability_flagged_warrants(self):
        good_check = make_check(cleared=True)
        bad_check = make_check(cleared=False)
        self.reg.apply_for_warrant("ACC001", dt.date(2023, 1, 1), 500.0, good_check)
        self.reg.apply_for_warrant("ACC002", dt.date(2023, 1, 2), 600.0, bad_check)
        flagged = self.reg.vulnerability_flagged_warrants()
        assert len(flagged) == 1
        assert flagged[0].account_id == "ACC002"

    def test_total_compensation_paid(self):
        r1 = self.reg.apply_for_warrant("ACC001", dt.date(2022, 6, 1), 500.0, make_check())
        r2 = self.reg.apply_for_warrant("ACC002", dt.date(2022, 7, 1), 400.0, make_check())
        self.reg.update_status(r1.warrant_id, WarrantStatus.REVOKED, dt.date(2023, 5, 1), compensation_gbp=150.0)
        self.reg.update_status(r2.warrant_id, WarrantStatus.REVOKED, dt.date(2023, 5, 1), compensation_gbp=200.0)
        assert abs(self.reg.total_compensation_paid_gbp() - 350.0) < 1e-9

    def test_warrant_register_summary(self):
        self.reg.apply_for_warrant("ACC001", dt.date(2022, 6, 1), 500.0, make_check())
        self.reg.apply_for_warrant("ACC002", BAN_DATE, 400.0, make_check())
        s = self.reg.warrant_register_summary()
        assert "2 total" in s
        assert "1 pre-ban" in s
        assert "1 post-ban" in s

    def test_ban_date_constant(self):
        assert _PPM_FORCE_FIT_BAN_DATE == dt.date(2023, 4, 27)
