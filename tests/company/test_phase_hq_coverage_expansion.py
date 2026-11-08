"""Phase HQ: Coverage expansion for 8 thin-test company modules."""
import datetime as dt
import pytest







# ===== licence_health =====
from company.regulatory.licence_health import (
    LicenceCheckStatus, LicenceCheck, LicenceHealthReport,
    build_licence_health_report
)

def _healthy_report():
    return build_licence_health_report(
        as_of=dt.date(2022,3,31), active_customer_count=500,
        net_assets_gbp=500_000, treasury_gbp=500_000,
        weeks_cash_runway=20, bad_debt_ratio_pct=1.0,
        complaints_per_100=0.5,
    )

class TestLicenceHealthExpanded:
    def test_all_green_report(self):
        r = _healthy_report()
        assert r.overall_status == LicenceCheckStatus.PASS
        assert r.is_going_concern

    def test_breach_on_negative_net_assets(self):
        r = build_licence_health_report(dt.date(2022,1,1), 500, -1.0, 500_000, 20, 1.0, 0.5)
        assert r.breach_count > 0
        assert not r.is_going_concern

    def test_watch_on_low_treasury(self):
        r = build_licence_health_report(dt.date(2022,1,1), 500, 500_000, 120_000, 20, 1.0, 0.5)
        assert r.get("treasury_gbp").status == LicenceCheckStatus.WATCH

    def test_breach_on_low_cash_runway(self):
        r = build_licence_health_report(dt.date(2022,1,1), 500, 500_000, 500_000, 3, 1.0, 0.5)
        assert r.get("cash_runway_weeks").status == LicenceCheckStatus.BREACH

    def test_bad_debt_breach_above_5pct(self):
        r = build_licence_health_report(dt.date(2022,1,1), 500, 500_000, 500_000, 20, 6.0, 0.5)
        assert r.get("bad_debt_ratio").status == LicenceCheckStatus.BREACH

    def test_complaints_watch_1_to_3(self):
        r = build_licence_health_report(dt.date(2022,1,1), 500, 500_000, 500_000, 20, 1.0, 2.0)
        assert r.get("complaints_per_100").status == LicenceCheckStatus.WATCH

    def test_complaints_breach_above_3(self):
        r = build_licence_health_report(dt.date(2022,1,1), 500, 500_000, 500_000, 20, 1.0, 4.0)
        assert r.get("complaints_per_100").status == LicenceCheckStatus.BREACH

    def test_summary_keys_present(self):
        r = _healthy_report()
        s = r.summary()
        assert "overall_status" in s and "is_going_concern" in s

    def test_headroom_positive_when_passing(self):
        r = _healthy_report()
        check = r.get("net_assets_gbp")
        assert check.headroom > 0

    def test_get_returns_none_for_unknown(self):
        assert _healthy_report().get("nonexistent") is None


# ===== meter_read_validation =====
from company.billing.meter_read_validation import (
    ReadSource, ValidationResult, ValidationFlag, MeterReadValidation
)

def _mrv(read=10000, prev=9630, read_dt=None, prev_dt=None, expected_kwh=10.0):
    if read_dt is None: read_dt = dt.date(2022,6,1)
    if prev_dt is None: prev_dt = dt.date(2022,5,1)
    return MeterReadValidation(read_dt, read, prev, prev_dt, expected_kwh, ReadSource.CUSTOMER)

class TestMeterReadValidationExpanded:
    def test_accepted_normal_read(self):
        v = _mrv()
        assert v.result == ValidationResult.ACCEPTED
        assert v.flags == []

    def test_reversal_flag_negative_advance(self):
        v = _mrv(read=9000, prev=9630)
        assert ValidationFlag.REVERSAL in v.flags
        assert v.result == ValidationResult.REJECTED

    def test_excessive_rate_rejected(self):
        v = _mrv(read=10500, prev=9000, expected_kwh=5.0)
        assert ValidationFlag.EXCESSIVE_DAILY_RATE in v.flags
        assert v.result == ValidationResult.REJECTED

    def test_zero_advance_flag(self):
        v = _mrv(read=9630, prev=9630)
        assert ValidationFlag.METER_ADVANCE_ZERO in v.flags
        assert v.result == ValidationResult.QUERIED

    def test_low_rate_flag(self):
        v = _mrv(read=9631, prev=9630, expected_kwh=50.0)
        assert ValidationFlag.LOW_DAILY_RATE in v.flags
        assert v.result == ValidationResult.QUERIED

    def test_advance_kwh_and_days(self):
        v = _mrv()
        assert v.days_elapsed == 31
        assert v.advance_kwh == pytest.approx(370.0)

    def test_summary_keys(self):
        v = _mrv()
        s = v.summary()
        assert "result" in s and "flags" in s and "advance_kwh" in s

    def test_smart_meter_source_accepted(self):
        v = MeterReadValidation(dt.date(2022,6,1),10000,9630,dt.date(2022,5,1),10.0,ReadSource.SMART_METER)
        assert v.result == ValidationResult.ACCEPTED
