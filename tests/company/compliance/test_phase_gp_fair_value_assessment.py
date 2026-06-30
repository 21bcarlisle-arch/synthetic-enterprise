import datetime as dt
import pytest
from company.compliance.fair_value_assessment_register import (
    ProductCategory, FairValueOutcome, FairValueAssessmentRecord,
    FairValueAssessmentRegister, _REVIEW_CYCLE_MONTHS,
)

ASSESS_DATE = dt.date(2024, 1, 15)
AS_OF = dt.date(2025, 1, 15)
PRODUCT = "SVT-2024"


def make_record(outcome=FairValueOutcome.FAIR_VALUE, revenue=1200.0, cts=900.0):
    return FairValueAssessmentRecord(
        record_id="FVA-00001", product_id=PRODUCT,
        product_category=ProductCategory.STANDARD_VARIABLE,
        assessment_date=ASSESS_DATE, outcome=outcome,
        cost_to_serve_gbp_pa=cts, revenue_per_customer_gbp_pa=revenue,
        customer_count=500)


class TestFairValueAssessmentRecord:
    def test_margin_per_customer(self):
        r = make_record(revenue=1200.0, cts=900.0)
        assert abs(r.margin_per_customer_gbp - 300.0) < 1e-9
    def test_margin_pct(self):
        r = make_record(revenue=1200.0, cts=900.0)
        assert abs(r.margin_pct - 25.0) < 1e-9
    def test_margin_pct_zero_revenue(self):
        r = make_record(revenue=0.0, cts=0.0)
        assert r.margin_pct == 0.0
    def test_is_poor_value(self):
        r = make_record(FairValueOutcome.POOR_VALUE)
        assert r.is_poor_value
    def test_is_not_poor_value(self):
        assert not make_record(FairValueOutcome.FAIR_VALUE).is_poor_value
    def test_is_board_approved_true(self):
        r = FairValueAssessmentRecord(
            record_id="X", product_id=PRODUCT,
            product_category=ProductCategory.STANDARD_VARIABLE,
            assessment_date=ASSESS_DATE, outcome=FairValueOutcome.FAIR_VALUE,
            cost_to_serve_gbp_pa=900.0, revenue_per_customer_gbp_pa=1200.0,
            customer_count=500, board_approved_date=dt.date(2024, 1, 20))
        assert r.is_board_approved
    def test_is_board_approved_false_when_none(self):
        assert not make_record().is_board_approved
    def test_is_overdue_review_after_12m(self):
        r = make_record()
        future = dt.date(ASSESS_DATE.year + 1, ASSESS_DATE.month, ASSESS_DATE.day)
        assert r.is_overdue_review(future)
    def test_is_not_overdue_review_before_12m(self):
        r = make_record()
        near = dt.date(ASSESS_DATE.year, ASSESS_DATE.month + 6, ASSESS_DATE.day)
        assert not r.is_overdue_review(near)
    def test_poor_value_review_due(self):
        r = make_record(FairValueOutcome.POOR_VALUE)
        due = r.poor_value_review_due()
        assert due is not None and due == ASSESS_DATE + dt.timedelta(30)
    def test_poor_value_review_due_none_when_not_poor(self):
        assert make_record().poor_value_review_due() is None
    def test_assessment_summary(self):
        s = make_record().assessment_summary()
        assert "FVA-00001" in s and PRODUCT in s
    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.outcome = FairValueOutcome.POOR_VALUE


class TestFairValueAssessmentRegister:
    def setup_method(self):
        self.reg = FairValueAssessmentRegister()

    def test_create_assessment_stored(self):
        r = self.reg.create_assessment(PRODUCT, ProductCategory.STANDARD_VARIABLE,
            ASSESS_DATE, FairValueOutcome.FAIR_VALUE, 900.0, 1200.0, 500)
        assert r.outcome == FairValueOutcome.FAIR_VALUE

    def test_auto_id_increments(self):
        r1 = self.reg.create_assessment(PRODUCT, ProductCategory.STANDARD_VARIABLE,
            ASSESS_DATE, FairValueOutcome.FAIR_VALUE, 900.0, 1200.0, 500)
        r2 = self.reg.create_assessment("PPM-2024", ProductCategory.PREPAYMENT,
            ASSESS_DATE, FairValueOutcome.FAIR_VALUE, 950.0, 1100.0, 200)
        assert r1.record_id != r2.record_id

    def test_negative_cost_raises(self):
        with pytest.raises(ValueError):
            self.reg.create_assessment(PRODUCT, ProductCategory.STANDARD_VARIABLE,
                ASSESS_DATE, FairValueOutcome.FAIR_VALUE, -1.0, 1200.0, 500)

    def test_negative_revenue_raises(self):
        with pytest.raises(ValueError):
            self.reg.create_assessment(PRODUCT, ProductCategory.STANDARD_VARIABLE,
                ASSESS_DATE, FairValueOutcome.FAIR_VALUE, 900.0, -1.0, 500)

    def test_approve(self):
        r = self.reg.create_assessment(PRODUCT, ProductCategory.STANDARD_VARIABLE,
            ASSESS_DATE, FairValueOutcome.FAIR_VALUE, 900.0, 1200.0, 500)
        approved = self.reg.approve(r.record_id, dt.date(2024, 1, 20))
        assert approved.is_board_approved

    def test_update_outcome(self):
        r = self.reg.create_assessment(PRODUCT, ProductCategory.STANDARD_VARIABLE,
            ASSESS_DATE, FairValueOutcome.FAIR_VALUE, 900.0, 1200.0, 500)
        updated = self.reg.update_outcome(r.record_id, FairValueOutcome.POOR_VALUE)
        assert updated.is_poor_value

    def test_update_missing_raises(self):
        with pytest.raises(KeyError):
            self.reg.approve("FVA-99999", dt.date(2024, 1, 20))

    def test_poor_value_products(self):
        self.reg.create_assessment(PRODUCT, ProductCategory.STANDARD_VARIABLE,
            ASSESS_DATE, FairValueOutcome.POOR_VALUE, 900.0, 1200.0, 500)
        self.reg.create_assessment("PPM-2024", ProductCategory.PREPAYMENT,
            ASSESS_DATE, FairValueOutcome.FAIR_VALUE, 950.0, 1100.0, 200)
        assert len(self.reg.poor_value_products()) == 1

    def test_overdue_reviews(self):
        self.reg.create_assessment(PRODUCT, ProductCategory.STANDARD_VARIABLE,
            ASSESS_DATE, FairValueOutcome.FAIR_VALUE, 900.0, 1200.0, 500)
        assert len(self.reg.overdue_reviews(AS_OF)) == 1
        assert len(self.reg.overdue_reviews(ASSESS_DATE)) == 0

    def test_unapproved_assessments(self):
        r1 = self.reg.create_assessment(PRODUCT, ProductCategory.STANDARD_VARIABLE,
            ASSESS_DATE, FairValueOutcome.FAIR_VALUE, 900.0, 1200.0, 500)
        r2 = self.reg.create_assessment("PPM-2024", ProductCategory.PREPAYMENT,
            ASSESS_DATE, FairValueOutcome.FAIR_VALUE, 950.0, 1100.0, 200)
        self.reg.approve(r1.record_id, dt.date(2024, 1, 20))
        assert len(self.reg.unapproved_assessments()) == 1

    def test_by_category(self):
        self.reg.create_assessment(PRODUCT, ProductCategory.STANDARD_VARIABLE,
            ASSESS_DATE, FairValueOutcome.FAIR_VALUE, 900.0, 1200.0, 500)
        self.reg.create_assessment("PPM-2024", ProductCategory.PREPAYMENT,
            ASSESS_DATE, FairValueOutcome.FAIR_VALUE, 950.0, 1100.0, 200)
        assert len(self.reg.by_category(ProductCategory.STANDARD_VARIABLE)) == 1

    def test_total_customers_assessed(self):
        self.reg.create_assessment(PRODUCT, ProductCategory.STANDARD_VARIABLE,
            ASSESS_DATE, FairValueOutcome.FAIR_VALUE, 900.0, 1200.0, 500)
        self.reg.create_assessment("PPM-2024", ProductCategory.PREPAYMENT,
            ASSESS_DATE, FairValueOutcome.FAIR_VALUE, 950.0, 1100.0, 200)
        assert self.reg.total_customers_assessed() == 700

    def test_fair_value_compliance_rate_pct(self):
        self.reg.create_assessment(PRODUCT, ProductCategory.STANDARD_VARIABLE,
            ASSESS_DATE, FairValueOutcome.FAIR_VALUE, 900.0, 1200.0, 500)
        self.reg.create_assessment("PPM-2024", ProductCategory.PREPAYMENT,
            ASSESS_DATE, FairValueOutcome.POOR_VALUE, 950.0, 1100.0, 200)
        rate = self.reg.fair_value_compliance_rate_pct()
        assert rate == 50.0

    def test_fair_value_compliance_rate_none_when_empty(self):
        assert self.reg.fair_value_compliance_rate_pct() is None

    def test_fva_summary(self):
        self.reg.create_assessment(PRODUCT, ProductCategory.STANDARD_VARIABLE,
            ASSESS_DATE, FairValueOutcome.FAIR_VALUE, 900.0, 1200.0, 500)
        s = self.reg.fva_summary(AS_OF)
        assert "1 assessments" in s

    def test_empty_summary(self):
        s = self.reg.fva_summary(AS_OF)
        assert "0 assessments" in s
