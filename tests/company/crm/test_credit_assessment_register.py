"""Tests for Customer Credit Assessment Register (Phase DU)."""
import datetime as dt
import pytest
from company.crm.credit_assessment_register import (
    CreditDecision, CreditReferenceAgency, CustomerSegmentType,
    CreditAssessmentRecord, CreditAssessmentRegister,
    _DEPOSIT_REFUND_DAYS, _MAX_DOMESTIC_DEPOSIT_GBP,
)


@pytest.fixture
def reg():
    return CreditAssessmentRegister()


DATE = dt.date(2024, 1, 15)


def assess(reg, cid="C1", decision=CreditDecision.APPROVED, deposit=0.0,
           score=750, agency=CreditReferenceAgency.EXPERIAN,
           segment=CustomerSegmentType.DOMESTIC):
    return reg.assess(
        customer_id=cid,
        segment=segment,
        assessed_at=DATE,
        agency=agency,
        credit_score=score,
        decision=decision,
        deposit_gbp=deposit,
    )


class TestCreditAssessmentRecord:
    def test_approved_no_deposit(self, reg):
        rec = assess(reg, decision=CreditDecision.APPROVED)
        assert not rec.requires_deposit
        assert not rec.is_ppm_required
        assert not rec.deposit_paid

    def test_approved_with_deposit(self, reg):
        rec = assess(reg, decision=CreditDecision.APPROVED_WITH_DEPOSIT, deposit=100.0)
        assert rec.requires_deposit
        assert rec.deposit_gbp == pytest.approx(100.0)

    def test_ppm_required(self, reg):
        rec = assess(reg, decision=CreditDecision.APPROVED_PPM_ONLY)
        assert rec.is_ppm_required

    def test_thin_file_no_score(self, reg):
        rec = assess(reg, decision=CreditDecision.THIN_FILE, score=None)
        assert rec.credit_score is None
        assert rec.decision == CreditDecision.THIN_FILE

    def test_deposit_refund_eligible_after_12m(self, reg):
        rec = assess(reg, decision=CreditDecision.APPROVED_WITH_DEPOSIT, deposit=100.0)
        reg.record_deposit_paid("C1", DATE)
        updated = reg.get("C1")
        as_of = DATE + dt.timedelta(days=_DEPOSIT_REFUND_DAYS + 1)
        assert updated.deposit_refund_eligible(as_of)

    def test_deposit_not_refund_eligible_before_12m(self, reg):
        rec = assess(reg, decision=CreditDecision.APPROVED_WITH_DEPOSIT, deposit=100.0)
        reg.record_deposit_paid("C1", DATE)
        as_of = DATE + dt.timedelta(days=30)
        assert not reg.get("C1").deposit_refund_eligible(as_of)

    def test_deposit_not_eligible_if_already_refunded(self, reg):
        assess(reg, decision=CreditDecision.APPROVED_WITH_DEPOSIT, deposit=100.0)
        reg.record_deposit_paid("C1", DATE)
        reg.record_deposit_refunded("C1", DATE + dt.timedelta(days=400))
        as_of = DATE + dt.timedelta(days=500)
        assert not reg.get("C1").deposit_refund_eligible(as_of)


class TestCreditAssessmentRegister:
    def test_unique_ids(self, reg):
        r1 = assess(reg, "C1")
        r2 = assess(reg, "C2")
        assert r1.assessment_id != r2.assessment_id

    def test_get(self, reg):
        assess(reg, "C1")
        assert reg.get("C1") is not None

    def test_get_missing(self, reg):
        assert reg.get("MISSING") is None

    def test_accounts_with_deposits(self, reg):
        assess(reg, "C1", decision=CreditDecision.APPROVED_WITH_DEPOSIT, deposit=100.0)
        assess(reg, "C2", decision=CreditDecision.APPROVED)
        reg.record_deposit_paid("C1", DATE)
        assert len(reg.accounts_with_deposits()) == 1

    def test_ppm_required_accounts(self, reg):
        assess(reg, "C1", decision=CreditDecision.APPROVED_PPM_ONLY)
        assess(reg, "C2", decision=CreditDecision.APPROVED)
        assert len(reg.ppm_required_accounts()) == 1

    def test_deposits_eligible_for_refund(self, reg):
        assess(reg, "C1", decision=CreditDecision.APPROVED_WITH_DEPOSIT, deposit=100.0)
        assess(reg, "C2", decision=CreditDecision.APPROVED_WITH_DEPOSIT, deposit=80.0)
        reg.record_deposit_paid("C1", DATE)
        reg.record_deposit_paid("C2", DATE + dt.timedelta(days=400))
        as_of = DATE + dt.timedelta(days=370)
        eligible = reg.deposits_eligible_for_refund(as_of)
        assert len(eligible) == 1

    def test_total_deposits_held(self, reg):
        assess(reg, "C1", decision=CreditDecision.APPROVED_WITH_DEPOSIT, deposit=100.0)
        assess(reg, "C2", decision=CreditDecision.APPROVED_WITH_DEPOSIT, deposit=80.0)
        reg.record_deposit_paid("C1", DATE)
        reg.record_deposit_paid("C2", DATE)
        assert reg.total_deposits_held_gbp() == pytest.approx(180.0)

    def test_deposit_not_held_after_refund(self, reg):
        assess(reg, "C1", decision=CreditDecision.APPROVED_WITH_DEPOSIT, deposit=100.0)
        reg.record_deposit_paid("C1", DATE)
        reg.record_deposit_refunded("C1", DATE + dt.timedelta(days=400))
        assert reg.total_deposits_held_gbp() == pytest.approx(0.0)

    def test_thin_file_accounts(self, reg):
        assess(reg, "C1", decision=CreditDecision.THIN_FILE, score=None)
        assess(reg, "C2", decision=CreditDecision.APPROVED)
        assert len(reg.thin_file_accounts()) == 1

    def test_constants(self):
        assert _DEPOSIT_REFUND_DAYS == 365
        assert _MAX_DOMESTIC_DEPOSIT_GBP == 300.0

    def test_credit_assessment_summary(self, reg):
        assess(reg, "C1")
        s = reg.credit_assessment_summary()
        assert "Credit Assessment Register" in s
        assert "Ofgem" in s
