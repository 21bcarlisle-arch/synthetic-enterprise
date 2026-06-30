"""Tests for Vulnerable Customer Register (Phase FA)."""
import datetime as dt
import pytest
from company.regulatory.vulnerable_customer_register import (
    VulnerabilityType, VulnerabilityRisk, VulnerabilityRecord,
    VulnerableCustomerRegister,
)

DATE = dt.date(2024, 1, 15)
REVIEW = dt.date(2025, 1, 15)
ACCT = "C1"


def make_rec(account=ACCT, types=None, risk=VulnerabilityRisk.MEDIUM,
             review=REVIEW, active=True):
    vtypes = types or (VulnerabilityType.FINANCIAL,)
    return VulnerabilityRecord(
        account_id=account,
        vulnerability_types=tuple(vtypes),
        risk_level=risk,
        identified_at=DATE,
        review_due_date=review,
        is_active=active,
    )


class TestVulnerabilityRecord:
    def test_is_ppm_restricted_active(self):
        r = make_rec(active=True)
        assert r.is_ppm_restricted

    def test_is_ppm_restricted_inactive(self):
        r = make_rec(active=False)
        assert not r.is_ppm_restricted

    def test_has_multiple_vulnerabilities(self):
        r = make_rec(types=[VulnerabilityType.FINANCIAL, VulnerabilityType.HEALTH_MEDICAL])
        assert r.has_multiple_vulnerabilities

    def test_single_not_multiple(self):
        r = make_rec()
        assert not r.has_multiple_vulnerabilities

    def test_is_review_overdue(self):
        r = make_rec(review=dt.date(2023, 6, 1))
        assert r.is_review_overdue(DATE)

    def test_not_overdue(self):
        r = make_rec(review=dt.date(2025, 6, 1))
        assert not r.is_review_overdue(DATE)

    def test_not_overdue_when_inactive(self):
        r = make_rec(review=dt.date(2020, 1, 1), active=False)
        assert not r.is_review_overdue(DATE)

    def test_vulnerability_summary(self):
        s = make_rec().vulnerability_summary()
        assert "VCR" in s


class TestVulnerableCustomerRegister:
    def test_register_and_active(self):
        reg = VulnerableCustomerRegister()
        reg.register(make_rec())
        assert len(reg.active_records()) == 1

    def test_inactive_excluded_from_active(self):
        reg = VulnerableCustomerRegister()
        reg.register(make_rec(active=False))
        assert len(reg.active_records()) == 0

    def test_by_risk_level(self):
        reg = VulnerableCustomerRegister()
        reg.register(make_rec(risk=VulnerabilityRisk.CRITICAL))
        reg.register(make_rec(account="C2", risk=VulnerabilityRisk.LOW))
        assert len(reg.by_risk_level(VulnerabilityRisk.CRITICAL)) == 1

    def test_critical_accounts(self):
        reg = VulnerableCustomerRegister()
        reg.register(make_rec(risk=VulnerabilityRisk.CRITICAL))
        assert len(reg.critical_accounts()) == 1

    def test_ppm_restricted(self):
        reg = VulnerableCustomerRegister()
        reg.register(make_rec(active=True))
        assert len(reg.ppm_restricted_accounts()) == 1

    def test_overdue_reviews(self):
        reg = VulnerableCustomerRegister()
        reg.register(make_rec(review=dt.date(2020, 1, 1)))
        assert len(reg.overdue_reviews(DATE)) == 1

    def test_multi_vulnerability(self):
        reg = VulnerableCustomerRegister()
        reg.register(make_rec(types=[VulnerabilityType.FINANCIAL, VulnerabilityType.MENTAL_HEALTH]))
        assert len(reg.multi_vulnerability_accounts()) == 1

    def test_vulnerability_rate_pct(self):
        reg = VulnerableCustomerRegister()
        reg.register(make_rec())
        assert reg.vulnerability_rate_pct(10) == pytest.approx(10.0)

    def test_vcr_summary(self):
        reg = VulnerableCustomerRegister()
        reg.register(make_rec())
        s = reg.vcr_summary(DATE, total_customers=18)
        assert "VCR" in s
