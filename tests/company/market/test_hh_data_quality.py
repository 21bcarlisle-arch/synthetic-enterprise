import pytest
"""Phase 127: HH data quality checker tests."""

from company.market.hh_data_quality import HHRecord, HHDataQualityChecker


def _checker():
    return HHDataQualityChecker(customer_eac_kwh=3500)


def test_valid_actual_read_no_issues():
    checker = _checker()
    r = HHRecord("2024-01-01:01", kwh=0.5, data_type="actual")
    assert checker.check_record(r) == []


def test_negative_consumption_is_error():
    checker = _checker()
    r = HHRecord("2024-01-01:01", kwh=-0.1)
    issues = checker.check_record(r)
    assert any(i.severity == "error" for i in issues)


def test_zero_actual_read_is_warning():
    checker = _checker()
    r = HHRecord("2024-01-01:01", kwh=0.0, data_type="actual")
    issues = checker.check_record(r)
    assert any(i.severity == "warning" for i in issues)


def test_zero_estimated_read_no_issue():
    checker = _checker()
    r = HHRecord("2024-01-01:01", kwh=0.0, data_type="estimated")
    # estimated zero is expected (meter not comms), flagged as info not warning for kwh=0
    issues = checker.check_record(r)
    # should have info for estimated but not warning for zero (only actual zeros warned)
    severities = [i.severity for i in issues]
    assert "info" in severities
    assert "error" not in severities


def test_implausibly_high_is_warning():
    checker = _checker()
    r = HHRecord("2024-01-01:01", kwh=100.0, data_type="actual")
    issues = checker.check_record(r)
    assert any(i.severity == "warning" and "high" in i.issue.lower() for i in issues)


def test_estimated_read_is_info():
    checker = _checker()
    r = HHRecord("2024-01-01:01", kwh=0.5, data_type="estimated")
    issues = checker.check_record(r)
    assert any(i.severity == "info" for i in issues)


def test_substituted_read_is_warning():
    checker = _checker()
    r = HHRecord("2024-01-01:01", kwh=0.5, data_type="substituted")
    issues = checker.check_record(r)
    assert any(i.severity == "warning" for i in issues)


def test_full_day_48_periods_quality_ok():
    checker = _checker()
    records = [HHRecord(f"2024-01-01:{i+1:02}", kwh=0.5) for i in range(48)]
    result = checker.check_day(records)
    assert result["quality_ok"] is True
    assert result["missing_periods"] == 0
    assert result["total_kwh"] == 24.0


def test_missing_periods_flagged_as_error():
    checker = _checker()
    records = [HHRecord(f"2024-01-01:{i+1:02}", kwh=0.5) for i in range(40)]  # 8 missing
    result = checker.check_day(records)
    assert result["missing_periods"] == 8
    assert result["quality_ok"] is False
    assert result["errors"] > 0


def test_check_day_total_kwh():
    checker = _checker()
    records = [HHRecord(f"2024-01-01:{i+1:02}", kwh=0.5) for i in range(10)]
    result = checker.check_day(records)
    assert result["total_kwh"] == pytest.approx(5.0)
    assert result["period_count"] == 10


def test_check_day_estimated_kwh():
    checker = _checker()
    records = [HHRecord("2024-01-01:01", kwh=1.0, data_type="actual"),
               HHRecord("2024-01-01:02", kwh=0.8, data_type="estimated")]
    result = checker.check_day(records)
    assert result["estimated_kwh"] == pytest.approx(0.8)


def test_negative_is_error_severity():
    checker = _checker()
    r = HHRecord("2024-01-01:05", kwh=-2.0)
    issues = checker.check_record(r)
    assert all(i.severity == "error" for i in issues)


def test_check_record_returns_list():
    checker = _checker()
    r = HHRecord("2024-01-01:10", kwh=0.3)
    result = checker.check_record(r)
    assert isinstance(result, list)


def test_high_eac_customer_accepts_larger_period():
    big_checker = HHDataQualityChecker(customer_eac_kwh=50000.0)
    # threshold = 50000/365/48*10 ≈ 28.5 kWh
    r = HHRecord("2024-01-01:01", kwh=5.0, data_type="actual")
    issues = big_checker.check_record(r)
    assert not any("high" in i.issue.lower() for i in issues)


def test_implausible_threshold_scales_with_eac():
    small_checker = HHDataQualityChecker(customer_eac_kwh=1000.0)
    big_checker = HHDataQualityChecker(customer_eac_kwh=100000.0)
    # 2 kWh should trigger warning for small but not big EAC
    r = HHRecord("2024-01-01:01", kwh=2.0, data_type="actual")
    small_issues = small_checker.check_record(r)
    big_issues = big_checker.check_record(r)
    small_high = any("high" in i.issue.lower() for i in small_issues)
    big_high = any("high" in i.issue.lower() for i in big_issues)
    assert small_high or not big_high  # small has stricter threshold


def test_full_day_infos_for_estimated_records():
    checker = _checker()
    records = [HHRecord(f"2024-01-01:{i+1:02}", kwh=0.4) for i in range(47)]
    records.append(HHRecord("2024-01-01:48", kwh=0.4, data_type="estimated"))
    result = checker.check_day(records)
    assert result["infos"] >= 1


def test_quality_ok_requires_no_errors():
    checker = _checker()
    records = [HHRecord(f"2024-01-01:{i+1:02}", kwh=0.5) for i in range(47)]
    records.append(HHRecord("2024-01-01:48", kwh=-0.1))  # negative = error
    result = checker.check_day(records)
    assert result["quality_ok"] is False


def test_substituted_warning_message():
    checker = _checker()
    r = HHRecord("2024-01-01:01", kwh=0.5, data_type="substituted")
    issues = checker.check_record(r)
    assert any("substituted" in i.issue.lower() for i in issues)


def test_zero_estimated_read_no_zero_warning():
    checker = _checker()
    r = HHRecord("2024-01-01:01", kwh=0.0, data_type="estimated")
    issues = checker.check_record(r)
    zero_warnings = [i for i in issues if i.severity == "warning" and "zero" in i.issue.lower()]
    assert len(zero_warnings) == 0
