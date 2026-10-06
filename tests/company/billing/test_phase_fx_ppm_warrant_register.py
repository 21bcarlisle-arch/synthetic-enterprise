"""Tests for Phase FX: PPM Installation Warrant Register."""
import datetime as dt

import pytest

from company.billing.ppm_warrant_register import (
    _MIN_DEBT_FOR_WARRANT_GBP,
    PPMWarrantRecord,
    PPMWarrantRegister,
    VulnerabilityCheck,
    WarrantRefusalReason,
    WarrantRegime,
    WarrantStatus,
)

SUSPENDED = dt.date(2023, 2, 6)    # magistrates' listing suspended
SLC_28B = dt.date(2023, 11, 8)     # SLC 28B in force: involuntary PPM permitted, with conditions

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

    def test_regime_before_the_suspension(self):
        assert make_record(app_date=SUSPENDED - dt.timedelta(1)).regime is WarrantRegime.PRE_SUSPENSION

    def test_regime_in_the_suspension_window(self):
        r = make_record(app_date=SUSPENDED)
        assert r.regime is WarrantRegime.LISTING_SUSPENDED and r.is_in_suspension_window

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

    def test_warrant_summary_names_its_regime(self):
        assert "[pre_suspension]" in make_record(app_date=dt.date(2022, 6, 1)).warrant_summary()
        assert "[slc_28b]" in make_record(app_date=SLC_28B).warrant_summary()

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

    def test_suspension_window_applications(self):
        self.reg.apply_for_warrant("ACC001", dt.date(2022, 12, 1), 500.0, make_check())
        self.reg.apply_for_warrant("ACC002", SUSPENDED, 500.0, make_check())
        self.reg.apply_for_warrant("ACC003", SLC_28B, 500.0, make_check())
        window = self.reg.suspension_window_applications()
        assert [r.account_id for r in window] == ["ACC002"]

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
        self.reg.apply_for_warrant("ACC002", SLC_28B, 400.0, make_check())
        s = self.reg.warrant_register_summary()
        assert "2 total" in s
        assert "1 pre-suspension" in s
        assert "0 in the listing suspension" in s
        assert "1 under SLC 28B" in s


# ── the April 2023 "ban" that never was (corrected 2026-10-06) ───────────────

def test_there_was_no_april_2023_ban_so_an_slc_28b_application_is_not_flagged():
    """Listing was suspended 6 Feb 2023 and SLC 28B permitted involuntary PPM from 8 Nov 2023
    (read_access_and_theft_duties.md §2.5; debt_and_collections.md). The old register flagged
    every application from 27 Apr 2023 as "post-ban". The partition: all three regimes reachable,
    and only the suspension window is anomalous."""
    import company.billing.ppm_warrant_register as m
    assert not hasattr(m, "_PPM_FORCE_FIT_BAN_DATE")
    assert not hasattr(WarrantRefusalReason, "POST_BAN")
    seen = {make_record(app_date=d).regime for d in
            (dt.date(2022, 6, 1), dt.date(2023, 4, 27), dt.date(2024, 1, 15))}
    assert seen == set(WarrantRegime)
    restart = make_record(app_date=dt.date(2024, 1, 15))
    assert restart.regime is WarrantRegime.SLC_28B and not restart.is_in_suspension_window
    assert make_record(app_date=dt.date(2023, 11, 7)).is_in_suspension_window
    assert "ban" not in restart.warrant_summary().lower()


def test_the_vulnerability_check_has_no_wall_clock_expiry():
    """`is_expired` read date.today(); only the as-of form, at the simulated date, remains."""
    assert not hasattr(VulnerabilityCheck, "is_expired")
    c = make_check(checked_at=dt.date(2023, 1, 1))
    assert not c.is_expired_as_of(dt.date(2023, 1, 29)) and c.is_expired_as_of(dt.date(2023, 1, 30))
