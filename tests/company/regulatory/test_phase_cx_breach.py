"""Phase CX: Regulatory Breach Log tests."""
import pytest
from datetime import date
from company.regulatory.regulatory_breach_log import (
    RegulatoryBreachLog, BreachSeverity, BreachStatus, BreachSource
)

_D = date(2022, 10, 1)


def _log_with_breach(severity=BreachSeverity.MEDIUM):
    log = RegulatoryBreachLog()
    rec = log.record("B001", "SLC 14", "Credit refund overdue", _D, severity)
    return log, rec


# 1. record creates POTENTIAL breach
def test_record_potential():
    log, rec = _log_with_breach()
    assert rec.status == BreachStatus.POTENTIAL
    assert rec.slc_reference == "SLC 14"


# 2. is_open True for POTENTIAL
def test_is_open_potential():
    log, rec = _log_with_breach()
    assert rec.is_open


# 3. confirm changes status to CONFIRMED
def test_confirm():
    log, rec = _log_with_breach()
    confirmed = log.confirm("B001")
    assert confirmed.status == BreachStatus.CONFIRMED
    assert confirmed.is_open


# 4. report_to_ofgem status
def test_report_to_ofgem():
    log, rec = _log_with_breach()
    reported = log.report_to_ofgem("B001")
    assert reported.status == BreachStatus.REPORTED_TO_OFGEM


# 5. remediate sets REMEDIATED and date
def test_remediate():
    log, rec = _log_with_breach()
    fix_date = date(2022, 11, 1)
    fixed = log.remediate("B001", fix_date)
    assert fixed.status == BreachStatus.REMEDIATED
    assert fixed.remediation_date == fix_date
    assert not fixed.is_open


# 6. open_breaches excludes remediated
def test_open_excludes_remediated():
    log = RegulatoryBreachLog()
    log.record("B001", "SLC 14", "Issue A", _D, BreachSeverity.LOW)
    log.record("B002", "SLC 27", "Issue B", _D, BreachSeverity.LOW)
    log.remediate("B001", date(2022, 11, 1))
    assert len(log.open_breaches) == 1


# 7. critical_breaches filtered correctly
def test_critical_breaches():
    log = RegulatoryBreachLog()
    log.record("B001", "SLC 27A", "Mass overcharge", _D, BreachSeverity.CRITICAL)
    log.record("B002", "SLC 14", "Minor late", _D, BreachSeverity.LOW)
    assert len(log.critical_breaches) == 1


# 8. reportable_breaches = HIGH or CRITICAL + open
def test_reportable_breaches():
    log = RegulatoryBreachLog()
    log.record("B001", "SLC 27A", "Systemic", _D, BreachSeverity.CRITICAL)
    log.record("B002", "SLC 14", "Minor", _D, BreachSeverity.LOW)
    assert len(log.reportable_breaches) == 1


# 9. total_estimated_penalty_gbp sums open
def test_total_penalty():
    log = RegulatoryBreachLog()
    log.record("B001", "SLC 14", "Issue", _D, BreachSeverity.HIGH, estimated_penalty_gbp=50_000)
    log.record("B002", "SLC 27", "Issue", _D, BreachSeverity.HIGH, estimated_penalty_gbp=75_000)
    assert log.total_estimated_penalty_gbp == 125_000


# 10. by_slc counts per SLC reference
def test_by_slc():
    log = RegulatoryBreachLog()
    log.record("B001", "SLC 14", "A", _D, BreachSeverity.LOW)
    log.record("B002", "SLC 14", "B", _D, BreachSeverity.LOW)
    log.record("B003", "SLC 27", "C", _D, BreachSeverity.LOW)
    slc = log.by_slc()
    assert slc["SLC 14"] == 2
    assert slc["SLC 27"] == 1


# 11. accounts_affected tracked
def test_accounts_affected():
    log = RegulatoryBreachLog()
    rec = log.record("B001", "SLC 27A", "Overcharge", _D, BreachSeverity.HIGH, accounts_affected=450)
    assert rec.accounts_affected == 450


# 12. breach_summary contains Ofgem
def test_breach_summary():
    log, rec = _log_with_breach()
    summary = log.breach_summary()
    assert "Ofgem" in summary
    assert "SLC" in summary
