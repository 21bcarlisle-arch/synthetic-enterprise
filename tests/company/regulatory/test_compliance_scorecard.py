import datetime as dt
import pytest
from company.regulatory.compliance_scorecard import (
    RAGStatus, ComplianceDomain, ComplianceCheck, ComplianceScorecard
)

DATE = dt.date(2023, 6, 30)


def test_rag_status_values():
    assert RAGStatus.GREEN == "GREEN"
    assert RAGStatus.AMBER == "AMBER"
    assert RAGStatus.RED == "RED"


def test_compliance_domain_slc_reference():
    check = ComplianceCheck(
        domain=ComplianceDomain.COMPLAINTS,
        check_date=DATE,
        status=RAGStatus.GREEN,
    )
    assert "SLC 25" in check.slc_reference


def test_check_is_breach_red():
    check = ComplianceCheck(
        domain=ComplianceDomain.FINANCIAL_RESILIENCE,
        check_date=DATE,
        status=RAGStatus.RED,
        metric_value=22.0,
        threshold=30.0,
        notes="Below MLR",
    )
    assert check.is_breach is True


def test_check_not_breach_green():
    check = ComplianceCheck(
        domain=ComplianceDomain.BILLING_METERING,
        check_date=DATE,
        status=RAGStatus.GREEN,
    )
    assert check.is_breach is False


def test_scorecard_record_and_latest():
    sc = ComplianceScorecard()
    sc.record_check(ComplianceDomain.COMPLAINTS, DATE, RAGStatus.GREEN)
    sc.record_check(ComplianceDomain.COMPLAINTS, dt.date(2023, 9, 30), RAGStatus.AMBER)
    assert sc.latest_status(ComplianceDomain.COMPLAINTS) == RAGStatus.AMBER


def test_scorecard_latest_status_none_if_empty():
    sc = ComplianceScorecard()
    assert sc.latest_status(ComplianceDomain.ENVIRONMENTAL) is None


def test_scorecard_overall_rag_green_all_pass():
    sc = ComplianceScorecard()
    for domain in ComplianceDomain:
        sc.record_check(domain, DATE, RAGStatus.GREEN)
    assert sc.overall_rag(DATE) == RAGStatus.GREEN


def test_scorecard_overall_rag_red_if_any_breach():
    sc = ComplianceScorecard()
    sc.record_check(ComplianceDomain.COMPLAINTS, DATE, RAGStatus.GREEN)
    sc.record_check(ComplianceDomain.FINANCIAL_RESILIENCE, DATE, RAGStatus.RED,
                    metric_value=20.0, threshold=30.0)
    sc.record_check(ComplianceDomain.TARIFF_PRICE_CAP, DATE, RAGStatus.AMBER)
    assert sc.overall_rag(DATE) == RAGStatus.RED


def test_scorecard_overall_rag_amber_no_red():
    sc = ComplianceScorecard()
    sc.record_check(ComplianceDomain.COMPLAINTS, DATE, RAGStatus.AMBER)
    sc.record_check(ComplianceDomain.BILLING_METERING, DATE, RAGStatus.GREEN)
    assert sc.overall_rag(DATE) == RAGStatus.AMBER


def test_scorecard_breaches():
    sc = ComplianceScorecard()
    sc.record_check(ComplianceDomain.FINANCIAL_RESILIENCE, DATE, RAGStatus.RED)
    sc.record_check(ComplianceDomain.COMPLAINTS, DATE, RAGStatus.GREEN)
    breaches = sc.breaches(DATE)
    assert len(breaches) == 1
    assert breaches[0].domain == ComplianceDomain.FINANCIAL_RESILIENCE


def test_scorecard_excludes_future_checks():
    sc = ComplianceScorecard()
    future = dt.date(2024, 1, 31)
    sc.record_check(ComplianceDomain.COMPLAINTS, future, RAGStatus.RED)
    # as_of DATE (2023-06-30) should not see future RED
    assert sc.overall_rag(DATE) == RAGStatus.GREEN
    assert len(sc.breaches(DATE)) == 0


def test_scorecard_summary():
    sc = ComplianceScorecard()
    sc.record_check(ComplianceDomain.COMPLAINTS, DATE, RAGStatus.GREEN)
    sc.record_check(ComplianceDomain.VULNERABLE_CUSTOMERS, DATE, RAGStatus.AMBER)
    sc.record_check(ComplianceDomain.FINANCIAL_RESILIENCE, DATE, RAGStatus.RED)
    s = sc.scorecard_summary(DATE)
    assert s["overall_rag"] == "RED"
    assert s["domains_checked"] == 3
    assert s["rag_counts"]["GREEN"] == 1
    assert s["rag_counts"]["AMBER"] == 1
    assert s["rag_counts"]["RED"] == 1
    assert "financial_resilience" in s["breach_domains"]
