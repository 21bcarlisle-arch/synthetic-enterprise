"""Phase IH: deeper coverage for capacity_to_pay, eep_book, meter_read_validation."""
import datetime as dt
import pytest


# ===== meter_read_validation =====
from company.billing.meter_read_validation import (
    MeterReadValidation, ValidationResult, ValidationFlag, ReadSource
)

def _good_read():
    return MeterReadValidation(
        read_date=dt.date(2022,2,1),
        read_value=10300.0,
        previous_read=10000.0,
        previous_read_date=dt.date(2022,1,1),
        expected_daily_kwh=10.0,
        source=ReadSource.CUSTOMER,
    )

def _reversal_read():
    return MeterReadValidation(
        read_date=dt.date(2022,2,1),
        read_value=9900.0,  # lower than previous
        previous_read=10000.0,
        previous_read_date=dt.date(2022,1,1),
        expected_daily_kwh=10.0,
        source=ReadSource.CUSTOMER,
    )

def _excessive_read():
    return MeterReadValidation(
        read_date=dt.date(2022,2,1),
        read_value=14000.0,  # 4000 kWh in 31 days = 129/day vs 10 expected
        previous_read=10000.0,
        previous_read_date=dt.date(2022,1,1),
        expected_daily_kwh=10.0,
        source=ReadSource.CUSTOMER,
    )

class TestMeterReadValidationExpanded:
    def test_advance_kwh(self):
        r = _good_read()
        assert r.advance_kwh == pytest.approx(300.0)

    def test_implied_daily_kwh(self):
        r = _good_read()
        assert r.implied_daily_kwh == pytest.approx(300/31, rel=0.01)

    def test_days_elapsed(self):
        r = _good_read()
        assert r.days_elapsed == 31

    def test_accepted_when_no_flags(self):
        r = _good_read()
        assert r.result == ValidationResult.ACCEPTED
        assert not r.flags

    def test_reversal_flagged_and_rejected(self):
        r = _reversal_read()
        assert ValidationFlag.REVERSAL in r.flags
        assert r.result == ValidationResult.REJECTED

    def test_excessive_daily_rate_rejected(self):
        r = _excessive_read()
        assert ValidationFlag.EXCESSIVE_DAILY_RATE in r.flags
        assert r.result == ValidationResult.REJECTED

    def test_zero_advance_over_7_days(self):
        r = MeterReadValidation(
            read_date=dt.date(2022,2,1),
            read_value=10000.0,  # same as previous
            previous_read=10000.0,
            previous_read_date=dt.date(2022,1,1),
            expected_daily_kwh=10.0,
            source=ReadSource.SMART_METER,
        )
        assert ValidationFlag.METER_ADVANCE_ZERO in r.flags
        assert r.result == ValidationResult.QUERIED

    def test_advance_kwh_negative_for_reversal(self):
        r = _reversal_read()
        assert r.advance_kwh < 0

    def test_summary_keys(self):
        r = _good_read()
        s = r.summary()
        assert "result" in s and "flags" in s

    def test_low_daily_rate_flagged_as_queried(self):
        r = MeterReadValidation(
            read_date=dt.date(2022,2,1),
            read_value=10010.0,  # only 10 kWh in 31 days = 0.32/day vs 10 expected
            previous_read=10000.0,
            previous_read_date=dt.date(2022,1,1),
            expected_daily_kwh=10.0,
            source=ReadSource.CUSTOMER,
        )
        assert ValidationFlag.LOW_DAILY_RATE in r.flags
        assert r.result == ValidationResult.QUERIED
