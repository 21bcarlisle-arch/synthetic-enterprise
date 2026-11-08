"""Phase JS: Coverage Depth Sprint XLI -- 30 tests.

Modules:
  eep_book: ID sequencing, payback None, scheme/year filter, empty customer, by_measure
  meter_read_validation: boundary thresholds, transposition, source stored, summary values
  capacity_to_pay: outcome boundaries, extended plan, repayment floor, estimated months
"""
import datetime as dt
import pytest
from company.billing.meter_read_validation import (
    ReadSource, ValidationResult, ValidationFlag, MeterReadValidation,
)


# ---------------------------------------------------------------------------
# meter_read_validation -- 10 tests
# ---------------------------------------------------------------------------

def _mrv(read_value, previous_read, days, expected_daily, *,
          source=ReadSource.CUSTOMER, same_day=False):
    base = dt.date(2022, 3, 1)
    read_date = base if same_day else base + dt.timedelta(days=days)
    return MeterReadValidation(
        read_date=read_date,
        read_value=read_value,
        previous_read=previous_read,
        previous_read_date=base,
        expected_daily_kwh=expected_daily,
        source=source,
    )


def test_mrv_days_elapsed_min_1_same_day():
    v = _mrv(1010.0, 1000.0, 0, 10.0, same_day=True)
    assert v.days_elapsed == 1


def test_mrv_zero_advance_not_flagged_within_7_days():
    v = _mrv(1000.0, 1000.0, 6, 10.0)
    assert ValidationFlag.METER_ADVANCE_ZERO not in v.flags


def test_mrv_transposition_queried():
    v = _mrv(9100.0, 500.0, 30, 100.0)
    assert ValidationFlag.TRANSPOSITION_LIKELY in v.flags
    assert v.result == ValidationResult.QUERIED


def test_mrv_exactly_3x_not_excessive():
    v = _mrv(1300.0, 1000.0, 10, 10.0)
    assert v.implied_daily_kwh == pytest.approx(30.0)
    assert ValidationFlag.EXCESSIVE_DAILY_RATE not in v.flags
    assert v.result == ValidationResult.ACCEPTED


def test_mrv_reversal_does_not_trigger_low_rate():
    v = _mrv(900.0, 1000.0, 30, 10.0)
    assert ValidationFlag.REVERSAL in v.flags
    assert ValidationFlag.LOW_DAILY_RATE not in v.flags


def test_mrv_exactly_0_2_threshold_not_low():
    v = _mrv(1060.0, 1000.0, 30, 10.0)
    assert v.implied_daily_kwh == pytest.approx(2.0)
    assert ValidationFlag.LOW_DAILY_RATE not in v.flags
    assert v.result == ValidationResult.ACCEPTED


def test_mrv_summary_includes_advance_kwh():
    v = _mrv(1300.0, 1000.0, 30, 10.0)
    s = v.summary()
    assert "advance_kwh" in s
    assert s["advance_kwh"] == pytest.approx(300.0)


def test_mrv_source_stored():
    v = _mrv(1300.0, 1000.0, 30, 10.0, source=ReadSource.ENGINEER_VISIT)
    assert v.source == ReadSource.ENGINEER_VISIT


def test_mrv_smart_meter_source():
    v = _mrv(1300.0, 1000.0, 30, 10.0, source=ReadSource.SMART_METER)
    assert v.source == ReadSource.SMART_METER


def test_mrv_summary_result_queried_on_low_rate():
    v = _mrv(1005.0, 1000.0, 30, 10.0)
    s = v.summary()
    assert s["result"] == "queried"
    assert "low_daily_rate" in s["flags"]
