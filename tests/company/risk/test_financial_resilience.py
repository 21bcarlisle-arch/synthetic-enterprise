import datetime as dt
import pytest
from company.risk.financial_resilience import (
    FRAAssessment, FRAStatus, FRATrigger, FinancialResilienceBook,
)

def make_a(year=2023, qtr=1, treasury=2_000_000, headroom=500_000,
           monthly=200_000, stress=True, var_ok=True, exposure=100_000,
           trigger=FRATrigger.ROUTINE_QUARTERLY, date=None):
    return FRAAssessment(
        year=year, quarter=qtr,
        assessment_date=date or dt.date(year, qtr * 3, 1),
        trigger=trigger,
        treasury_gbp=treasury,
        credit_facility_headroom_gbp=headroom,
        monthly_fixed_costs_gbp=monthly,
        stress_test_passed=stress,
        var_within_limit=var_ok,
        net_wholesale_exposure_gbp=exposure,
    )


class TestFRAAssessment:
    def test_total_liquidity(self):
        a = make_a(treasury=1_000_000, headroom=500_000)
        assert a.total_liquidity_gbp == 1_500_000

    def test_months_of_liquidity(self):
        a = make_a(treasury=1_200_000, headroom=0, monthly=100_000)
        assert a.months_of_liquidity == 12.0

    def test_months_combined(self):
        a = make_a(treasury=600_000, headroom=600_000, monthly=100_000)
        assert a.months_of_liquidity == 12.0

    def test_months_zero_costs_none(self):
        a = make_a(monthly=0)
        assert a.months_of_liquidity is None

    def test_status_resilient(self):
        a = make_a(treasury=2_400_000, headroom=0, monthly=200_000, stress=True, var_ok=True)
        assert a.status == FRAStatus.RESILIENT

    def test_status_adequate(self):
        a = make_a(treasury=1_600_000, headroom=0, monthly=200_000, stress=True, var_ok=True)
        assert a.months_of_liquidity == 8.0
        assert a.status == FRAStatus.ADEQUATE

    def test_status_borderline_months(self):
        a = make_a(treasury=800_000, headroom=0, monthly=200_000, stress=True, var_ok=True)
        assert a.status == FRAStatus.BORDERLINE

    def test_status_inadequate_months(self):
        a = make_a(treasury=400_000, headroom=0, monthly=200_000, stress=True, var_ok=True)
        assert a.status == FRAStatus.INADEQUATE

    def test_status_borderline_stress_fail_good_liquidity(self):
        a = make_a(treasury=2_400_000, headroom=0, monthly=200_000, stress=False, var_ok=True)
        assert a.status == FRAStatus.BORDERLINE

    def test_status_inadequate_stress_fail_low_liquidity(self):
        a = make_a(treasury=400_000, headroom=0, monthly=200_000, stress=False)
        assert a.status == FRAStatus.INADEQUATE

    def test_status_borderline_var_fail(self):
        a = make_a(treasury=2_400_000, headroom=0, monthly=200_000, stress=True, var_ok=False)
        assert a.status == FRAStatus.BORDERLINE

    def test_is_compliant_true(self):
        a = make_a(treasury=2_400_000, headroom=0, monthly=200_000)
        assert a.is_compliant is True

    def test_is_compliant_false(self):
        a = make_a(treasury=400_000, headroom=0, monthly=200_000)
        assert a.is_compliant is False

    def test_period_label(self):
        a = make_a(year=2022, qtr=3)
        assert a.period_label == "2022Q3"

    def test_trigger_enum(self):
        a = make_a(trigger=FRATrigger.MARKET_STRESS_EVENT)
        assert a.trigger == FRATrigger.MARKET_STRESS_EVENT

    def test_frozen(self):
        a = make_a()
        with pytest.raises((AttributeError, TypeError)):
            a.treasury_gbp = 999


class TestFinancialResilienceBook:
    def test_empty_latest_none(self):
        assert FinancialResilienceBook().latest_assessment() is None

    def test_record_and_latest(self):
        book = FinancialResilienceBook()
        a = make_a()
        book.record_assessment(a)
        assert book.latest_assessment() == a

    def test_latest_most_recent_date(self):
        book = FinancialResilienceBook()
        a1 = make_a(year=2022, qtr=1, date=dt.date(2022, 3, 31))
        a2 = make_a(year=2022, qtr=2, date=dt.date(2022, 6, 30))
        book.record_assessment(a1)
        book.record_assessment(a2)
        assert book.latest_assessment() == a2

    def test_assessments_for_year(self):
        book = FinancialResilienceBook()
        book.record_assessment(make_a(year=2022, qtr=1, date=dt.date(2022, 3, 31)))
        book.record_assessment(make_a(year=2022, qtr=2, date=dt.date(2022, 6, 30)))
        book.record_assessment(make_a(year=2023, qtr=1, date=dt.date(2023, 3, 31)))
        assert len(book.assessments_for_year(2022)) == 2
        assert len(book.assessments_for_year(2023)) == 1

    def test_inadequate_quarters(self):
        book = FinancialResilienceBook()
        book.record_assessment(make_a(year=2022, qtr=3, treasury=400_000, headroom=0,
                                      monthly=200_000, date=dt.date(2022, 9, 30)))
        book.record_assessment(make_a(year=2022, qtr=4, treasury=2_400_000, headroom=0,
                                      monthly=200_000, date=dt.date(2022, 12, 31)))
        result = book.inadequate_quarters()
        assert len(result) == 1 and result[0].quarter == 3

    def test_borderline_or_worse(self):
        book = FinancialResilienceBook()
        book.record_assessment(make_a(year=2023, qtr=1, treasury=800_000, headroom=0,
                                      monthly=200_000, date=dt.date(2023, 3, 31)))  # BORDERLINE
        book.record_assessment(make_a(year=2023, qtr=2, treasury=2_400_000, monthly=200_000,
                                      date=dt.date(2023, 6, 30)))  # RESILIENT
        assert len(book.borderline_or_worse()) == 1

    def test_trend_insufficient_data(self):
        book = FinancialResilienceBook()
        book.record_assessment(make_a(year=2023, qtr=1, date=dt.date(2023, 3, 31)))
        assert book.trend_is_deteriorating() is False

    def test_trend_deteriorating(self):
        book = FinancialResilienceBook()
        book.record_assessment(make_a(year=2022, qtr=2, treasury=2_400_000, headroom=0,
                                      monthly=200_000, date=dt.date(2022, 6, 30)))   # RESILIENT
        book.record_assessment(make_a(year=2022, qtr=3, treasury=1_600_000, headroom=0,
                                      monthly=200_000, date=dt.date(2022, 9, 30)))   # ADEQUATE
        book.record_assessment(make_a(year=2022, qtr=4, treasury=800_000, headroom=0,
                                      monthly=200_000, date=dt.date(2022, 12, 31)))  # BORDERLINE
        assert book.trend_is_deteriorating() is True

    def test_trend_stable(self):
        book = FinancialResilienceBook()
        for qtr, d in [(1, dt.date(2023, 3, 31)), (2, dt.date(2023, 6, 30)), (3, dt.date(2023, 9, 30))]:
            book.record_assessment(make_a(year=2023, qtr=qtr, treasury=2_400_000, headroom=0,
                                          monthly=200_000, date=d))
        assert book.trend_is_deteriorating() is False

    def test_summary_keys(self):
        book = FinancialResilienceBook()
        book.record_assessment(make_a(date=dt.date(2023, 3, 31)))
        s = book.fra_summary()
        for k in ("total_assessments", "inadequate_quarters", "latest_status",
                  "latest_liquidity_months", "trend_deteriorating", "borderline_or_worse"):
            assert k in s

    def test_summary_empty(self):
        book = FinancialResilienceBook()
        s = book.fra_summary()
        assert s["total_assessments"] == 0
        assert s["latest_status"] is None
