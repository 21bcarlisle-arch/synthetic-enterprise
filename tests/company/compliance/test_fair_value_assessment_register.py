"""Tests for company/compliance/fair_value_assessment_register.py (Sprint CL)."""
import datetime as dt
import pytest

from company.compliance.fair_value_assessment_register import (
    FairValueAssessmentRegister,
    FairValueAssessmentRecord,
    FairValueOutcome,
    ProductCategory,
)

DATE = dt.date(2023, 8, 1)


def _reg():
    return FairValueAssessmentRegister()


def _add(reg, outcome=FairValueOutcome.FAIR_VALUE, revenue=900.0, cost=800.0, count=100):
    return reg.create_assessment(
        "P1", ProductCategory.FIXED_TERM, DATE, outcome, cost, revenue, count
    )


def test_record_id_starts_with_fva():
    reg = _reg()
    r = _add(reg)
    assert r.record_id.startswith("FVA-")


def test_product_id_stored():
    reg = _reg()
    r = _add(reg)
    assert r.product_id == "P1"


def test_outcome_stored():
    reg = _reg()
    r = _add(reg, outcome=FairValueOutcome.POOR_VALUE)
    assert r.outcome == FairValueOutcome.POOR_VALUE


def test_margin_per_customer_computed():
    reg = _reg()
    r = _add(reg, revenue=1000.0, cost=900.0)
    assert abs(r.margin_per_customer_gbp - 100.0) < 0.01


def test_margin_pct_computed():
    reg = _reg()
    r = _add(reg, revenue=1000.0, cost=900.0)
    assert abs(r.margin_pct - 10.0) < 0.01


def test_is_poor_value_false_for_fair():
    reg = _reg()
    r = _add(reg, outcome=FairValueOutcome.FAIR_VALUE)
    assert r.is_poor_value is False


def test_is_poor_value_true():
    reg = _reg()
    r = _add(reg, outcome=FairValueOutcome.POOR_VALUE)
    assert r.is_poor_value is True


def test_poor_value_review_due_30_days():
    reg = _reg()
    r = _add(reg, outcome=FairValueOutcome.POOR_VALUE)
    import datetime as _dt
    assert r.poor_value_review_due() == DATE + _dt.timedelta(days=30)


def test_approve_sets_board_approved_date():
    reg = _reg()
    r = _add(reg)
    approved = reg.approve(r.record_id, DATE)
    assert approved.board_approved_date == DATE


def test_total_customers_assessed_sums():
    reg = _reg()
    _add(reg, count=100)
    _add(reg, count=50)
    assert reg.total_customers_assessed() == 150
