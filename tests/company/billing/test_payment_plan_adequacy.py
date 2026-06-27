"""Tests for company/billing/payment_plan_adequacy.py -- Phase 315."""
from __future__ import annotations

import datetime as dt

import pytest

from company.billing.payment_plan_adequacy import (
    ATPCompliance,
    PaymentPlanAdequacyBook,
    PaymentPlanAdequacyCheck,
)


def _check(
    account_id: str = "A001",
    plan: float = 100.0,
    income: float = 1500.0,
    essentials: float = 1200.0,
    is_vulnerable: bool = False,
) -> PaymentPlanAdequacyCheck:
    return PaymentPlanAdequacyCheck(
        account_id=account_id,
        assessment_date=dt.date(2023, 1, 1),
        monthly_plan_gbp=plan,
        estimated_monthly_income_gbp=income,
        monthly_essential_costs_gbp=essentials,
        is_vulnerable=is_vulnerable,
    )


class TestPaymentPlanAdequacyCheck:
    def test_disposable_income(self):
        c = _check(income=1500.0, essentials=1200.0)
        assert c.disposable_income_gbp == 300.0

    def test_disposable_income_none_when_missing(self):
        c = PaymentPlanAdequacyCheck(
            account_id="A001",
            assessment_date=dt.date(2023, 1, 1),
            monthly_plan_gbp=100.0,
            estimated_monthly_income_gbp=None,
            monthly_essential_costs_gbp=None,
        )
        assert c.disposable_income_gbp is None

    def test_plan_as_pct_disposable(self):
        c = _check(plan=45.0, income=1500.0, essentials=1200.0)
        # disposable = 300; pct = 45/300 = 15%
        assert c.plan_as_pct_disposable == 15.0

    def test_plan_as_pct_none_when_no_income(self):
        c = PaymentPlanAdequacyCheck(
            account_id="A001",
            assessment_date=dt.date(2023, 1, 1),
            monthly_plan_gbp=100.0,
            estimated_monthly_income_gbp=None,
            monthly_essential_costs_gbp=None,
        )
        assert c.plan_as_pct_disposable is None

    def test_compliance_affordable(self):
        # 45/300 = 15% -> exactly at threshold -> AFFORDABLE (<=15%)
        c = _check(plan=45.0, income=1500.0, essentials=1200.0)
        assert c.compliance == ATPCompliance.AFFORDABLE

    def test_compliance_borderline(self):
        # plan=60, disposable=300 -> 20% -> BORDERLINE
        c = _check(plan=60.0, income=1500.0, essentials=1200.0)
        assert c.compliance == ATPCompliance.BORDERLINE

    def test_compliance_unaffordable_high_pct(self):
        # plan=100, disposable=300 -> 33% -> UNAFFORDABLE
        c = _check(plan=100.0, income=1500.0, essentials=1200.0)
        assert c.compliance == ATPCompliance.UNAFFORDABLE

    def test_compliance_unaffordable_low_residual(self):
        # plan=260, disposable=300 -> residual=40 < 50 -> UNAFFORDABLE
        c = _check(plan=260.0, income=1500.0, essentials=1200.0)
        assert c.compliance == ATPCompliance.UNAFFORDABLE

    def test_compliance_unknown_no_income(self):
        c = PaymentPlanAdequacyCheck(
            account_id="A001",
            assessment_date=dt.date(2023, 1, 1),
            monthly_plan_gbp=100.0,
            estimated_monthly_income_gbp=None,
            monthly_essential_costs_gbp=None,
        )
        assert c.compliance == ATPCompliance.UNKNOWN

    def test_is_compliant_affordable(self):
        c = _check(plan=45.0, income=1500.0, essentials=1200.0)
        assert c.is_compliant

    def test_is_not_compliant_unaffordable(self):
        c = _check(plan=100.0, income=1500.0, essentials=1200.0)
        assert not c.is_compliant


class TestPaymentPlanAdequacyBook:
    def _book(self) -> PaymentPlanAdequacyBook:
        return PaymentPlanAdequacyBook()

    def test_record_check(self):
        book = self._book()
        book.record_check(_check("A001"))
        assert len(book._checks) == 1

    def test_checks_for_account(self):
        book = self._book()
        book.record_check(_check("A001"))
        book.record_check(_check("A001"))
        book.record_check(_check("A002"))
        assert len(book.checks_for("A001")) == 2

    def test_latest_for_account(self):
        book = self._book()
        c1 = PaymentPlanAdequacyCheck("A001", dt.date(2022, 1, 1), 100.0, 1500.0, 1200.0)
        c2 = PaymentPlanAdequacyCheck("A001", dt.date(2023, 6, 1), 120.0, 1500.0, 1200.0)
        book.record_check(c1)
        book.record_check(c2)
        assert book.latest_for("A001").assessment_date == dt.date(2023, 6, 1)

    def test_non_compliant_plans(self):
        book = self._book()
        book.record_check(_check("A001", plan=45.0))   # affordable
        book.record_check(_check("A002", plan=100.0))  # unaffordable
        assert len(book.non_compliant_plans()) == 1
        assert book.non_compliant_plans()[0].account_id == "A002"

    def test_vulnerable_non_compliant(self):
        book = self._book()
        book.record_check(_check("A001", plan=100.0, is_vulnerable=True))
        book.record_check(_check("A002", plan=100.0, is_vulnerable=False))
        assert len(book.vulnerable_non_compliant()) == 1

    def test_total_at_risk_gbp(self):
        book = self._book()
        book.record_check(_check("A001", plan=100.0))  # unaffordable
        book.record_check(_check("A002", plan=80.0))   # unaffordable
        book.record_check(_check("A003", plan=30.0))   # affordable
        assert book.total_at_risk_gbp() == 180.0

    def test_adequacy_summary_keys(self):
        book = self._book()
        book.record_check(_check("A001", plan=45.0))
        book.record_check(_check("A002", plan=100.0))
        s = book.adequacy_summary()
        assert "total_checks" in s
        assert "affordable" in s
        assert "borderline" in s
        assert "unaffordable" in s
        assert "unknown" in s
        assert "vulnerable_non_compliant" in s
        assert "total_at_risk_gbp" in s

    def test_empty_book(self):
        book = self._book()
        s = book.adequacy_summary()
        assert s["total_checks"] == 0
        assert s["total_at_risk_gbp"] == 0.0
