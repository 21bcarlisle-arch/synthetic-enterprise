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
