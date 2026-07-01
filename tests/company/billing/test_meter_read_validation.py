import datetime as dt
import pytest
from company.billing.meter_read_validation import (
    ReadSource, ValidationResult, ValidationFlag, MeterReadValidation
)


def test_clean_read_accepted():
    v = MeterReadValidation(
        read_date=dt.date(2022, 3, 31),
        read_value=12500.0,
        previous_read=12200.0,
        previous_read_date=dt.date(2022, 3, 1),
        expected_daily_kwh=10.0,
        source=ReadSource.CUSTOMER,
    )
    assert v.advance_kwh == pytest.approx(300.0)
    assert v.implied_daily_kwh == pytest.approx(10.0)
    assert v.result == ValidationResult.ACCEPTED
    assert v.flags == []


def test_reversal_rejected():
    v = MeterReadValidation(
        read_date=dt.date(2022, 3, 31),
        read_value=12000.0,
        previous_read=12500.0,
        previous_read_date=dt.date(2022, 3, 1),
        expected_daily_kwh=10.0,
        source=ReadSource.CUSTOMER,
    )
    assert ValidationFlag.REVERSAL in v.flags
    assert v.result == ValidationResult.REJECTED


def test_excessive_daily_rate_rejected():
    v = MeterReadValidation(
        read_date=dt.date(2022, 3, 31),
        read_value=13_200.0,
        previous_read=12_200.0,
        previous_read_date=dt.date(2022, 3, 1),
        expected_daily_kwh=10.0,
        source=ReadSource.CUSTOMER,
    )
    # advance 1000 / 30 days = 33.3 kWh/day; expected 10; 33.3 > 3*10=30 -> EXCESSIVE
    assert ValidationFlag.EXCESSIVE_DAILY_RATE in v.flags
    assert v.result == ValidationResult.REJECTED


def test_zero_advance_queried():
    v = MeterReadValidation(
        read_date=dt.date(2022, 3, 31),
        read_value=12_200.0,
        previous_read=12_200.0,
        previous_read_date=dt.date(2022, 3, 1),
        expected_daily_kwh=10.0,
        source=ReadSource.CUSTOMER,
    )
    assert ValidationFlag.METER_ADVANCE_ZERO in v.flags
    assert v.result == ValidationResult.QUERIED


def test_days_elapsed():
    v = MeterReadValidation(
        read_date=dt.date(2022, 3, 31),
        read_value=12_500.0,
        previous_read=12_200.0,
        previous_read_date=dt.date(2022, 3, 1),
        expected_daily_kwh=10.0,
        source=ReadSource.SMART_METER,
    )
    assert v.days_elapsed == 30


def test_low_rate_queried():
    v = MeterReadValidation(
        read_date=dt.date(2022, 3, 31),
        read_value=12_210.0,
        previous_read=12_200.0,
        previous_read_date=dt.date(2022, 3, 1),
        expected_daily_kwh=10.0,
        source=ReadSource.CUSTOMER,
    )
    # 10 / 30 = 0.33 kWh/day vs expected 10; ratio 0.033 < 0.2
    assert ValidationFlag.LOW_DAILY_RATE in v.flags
    assert v.result == ValidationResult.QUERIED


def test_summary_keys():
    v = MeterReadValidation(
        read_date=dt.date(2022, 3, 31),
        read_value=12_500.0,
        previous_read=12_200.0,
        previous_read_date=dt.date(2022, 3, 1),
        expected_daily_kwh=10.0,
        source=ReadSource.CUSTOMER,
    )
    s = v.summary()
    assert s['result'] == 'accepted'
    assert 'flags' in s


# --- Phase KC depth tests ---

def test_advance_kwh_computed():
    v = MeterReadValidation(
        read_date=dt.date(2022, 3, 31), read_value=12500.0,
        previous_read=12200.0, previous_read_date=dt.date(2022, 3, 1),
        expected_daily_kwh=10.0, source=ReadSource.CUSTOMER,
    )
    assert v.advance_kwh == pytest.approx(300.0)


def test_implied_daily_kwh():
    v = MeterReadValidation(
        read_date=dt.date(2022, 3, 31), read_value=12500.0,
        previous_read=12200.0, previous_read_date=dt.date(2022, 3, 1),
        expected_daily_kwh=10.0, source=ReadSource.CUSTOMER,
    )
    assert v.implied_daily_kwh == pytest.approx(10.0)


def test_transposition_flag():
    # read_value=85, prev=30, days=2, expected=10
    # implied=27.5; transposed=58 -> daily=14; |14-10|=4 < |27.5-10|=17.5 -> TRANSPOSITION
    v = MeterReadValidation(
        read_date=dt.date(2022, 3, 3), read_value=85.0,
        previous_read=30.0, previous_read_date=dt.date(2022, 3, 1),
        expected_daily_kwh=10.0, source=ReadSource.CUSTOMER,
    )
    assert ValidationFlag.TRANSPOSITION_LIKELY in v.flags
    assert v.result == ValidationResult.QUERIED


def test_zero_advance_within_7_days_not_flagged():
    v = MeterReadValidation(
        read_date=dt.date(2022, 3, 6), read_value=12200.0,
        previous_read=12200.0, previous_read_date=dt.date(2022, 3, 1),
        expected_daily_kwh=10.0, source=ReadSource.CUSTOMER,
    )
    assert ValidationFlag.METER_ADVANCE_ZERO not in v.flags


def test_engineer_visit_source_stored():
    v = MeterReadValidation(
        read_date=dt.date(2022, 3, 31), read_value=12500.0,
        previous_read=12200.0, previous_read_date=dt.date(2022, 3, 1),
        expected_daily_kwh=10.0, source=ReadSource.ENGINEER_VISIT,
    )
    assert v.source == ReadSource.ENGINEER_VISIT


def test_smart_meter_source_accepted():
    v = MeterReadValidation(
        read_date=dt.date(2022, 3, 31), read_value=12500.0,
        previous_read=12200.0, previous_read_date=dt.date(2022, 3, 1),
        expected_daily_kwh=10.0, source=ReadSource.SMART_METER,
    )
    assert v.result == ValidationResult.ACCEPTED


def test_summary_advance_kwh():
    v = MeterReadValidation(
        read_date=dt.date(2022, 3, 31), read_value=12500.0,
        previous_read=12200.0, previous_read_date=dt.date(2022, 3, 1),
        expected_daily_kwh=10.0, source=ReadSource.CUSTOMER,
    )
    assert v.summary()['advance_kwh'] == pytest.approx(300.0)


def test_exactly_3x_not_excessive():
    # implied = 30 = 3*10 exactly -> NOT > 30 -> not EXCESSIVE
    v = MeterReadValidation(
        read_date=dt.date(2022, 3, 31), read_value=13100.0,
        previous_read=12200.0, previous_read_date=dt.date(2022, 3, 1),
        expected_daily_kwh=10.0, source=ReadSource.CUSTOMER,
    )
    assert ValidationFlag.EXCESSIVE_DAILY_RATE not in v.flags


def test_exactly_0_2x_not_low_rate():
    # implied = 2.0 = 0.2*10 exactly -> NOT < 0.2*10 -> not LOW_DAILY_RATE
    v = MeterReadValidation(
        read_date=dt.date(2022, 3, 31), read_value=12260.0,
        previous_read=12200.0, previous_read_date=dt.date(2022, 3, 1),
        expected_daily_kwh=10.0, source=ReadSource.CUSTOMER,
    )
    assert ValidationFlag.LOW_DAILY_RATE not in v.flags


def test_summary_result_value():
    v = MeterReadValidation(
        read_date=dt.date(2022, 3, 31), read_value=12000.0,
        previous_read=12500.0, previous_read_date=dt.date(2022, 3, 1),
        expected_daily_kwh=10.0, source=ReadSource.CUSTOMER,
    )
    assert v.summary()['result'] == 'rejected'
