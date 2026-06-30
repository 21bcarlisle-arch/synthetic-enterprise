"""Phase IH: deeper coverage for capacity_to_pay, eep_book, meter_read_validation."""
import datetime as dt
import pytest

# ===== capacity_to_pay =====
from company.billing.capacity_to_pay import (
    CtPAssessment, AffordabilityOutcome, RecommendedAction
)

def _can_pay():
    return CtPAssessment("C1",dt.date(2022,6,1),
                          monthly_income_gbp=2000.0,
                          monthly_essential_outgoings_gbp=1500.0,
                          total_debt_gbp=400.0)  # disposable=500; repayment=50/mo; 8mo

def _fuel_poverty():
    return CtPAssessment("C2",dt.date(2022,6,1),
                          monthly_income_gbp=800.0,
                          monthly_essential_outgoings_gbp=750.0,
                          total_debt_gbp=1500.0,  # esi=1500/(800*12)=15.6%
                          is_vulnerable=False)

def _cannot_pay():
    return CtPAssessment("C3",dt.date(2022,6,1),
                          monthly_income_gbp=0.0,
                          monthly_essential_outgoings_gbp=0.0,
                          total_debt_gbp=500.0)

class TestCtPAssessmentExpanded:
    def test_disposable_income(self):
        a = _can_pay()
        assert a.disposable_income_gbp == pytest.approx(500.0)

    def test_disposable_income_floored_at_zero(self):
        a = _cannot_pay()
        assert a.disposable_income_gbp == pytest.approx(0.0)

    def test_energy_share_of_income(self):
        a = _fuel_poverty()
        expected = 1500 / (800*12) * 100
        assert a.energy_share_of_income_pct == pytest.approx(expected, rel=0.01)

    def test_outcome_fuel_poverty(self):
        assert _fuel_poverty().outcome == AffordabilityOutcome.FUEL_POVERTY

    def test_outcome_cannot_pay(self):
        assert _cannot_pay().outcome == AffordabilityOutcome.CANNOT_PAY

    def test_outcome_can_pay_in_full(self):
        # disposable=500, repayment=50, 50*12=600>=400 debt
        assert _can_pay().outcome == AffordabilityOutcome.CAN_PAY_IN_FULL

    def test_recommended_action_standard_plan(self):
        assert _can_pay().recommended_action == RecommendedAction.STANDARD_PLAN

    def test_recommended_action_write_off(self):
        assert _cannot_pay().recommended_action == RecommendedAction.WRITE_OFF_CONSIDERATION

    def test_estimated_plan_months(self):
        a = _can_pay()
        repayment = 500 * 0.10  # 50
        expected = round(400 / 50)  # 8
        assert a.estimated_plan_months == expected

    def test_summary_keys(self):
        a = _can_pay()
        s = a.summary()
        assert "outcome" in s and "recommended_action" in s


# ===== eep_book =====
from company.crm.eep_book import (
    EEPBook, EEPMeasure, EEPScheme
)

def _eep():
    book = EEPBook()
    book.record("C1","M001",EEPMeasure.LOFT_INSULATION,EEPScheme.ECO4,
                dt.date(2022,3,1),400.0,2000.0,1800.0)
    book.record("C1","M001",EEPMeasure.CAVITY_WALL,EEPScheme.ECO4,
                dt.date(2022,5,1),600.0,3000.0,2400.0)
    book.record("C2","M002",EEPMeasure.SOLAR_PV,EEPScheme.BUS,
                dt.date(2023,2,1),1200.0,8000.0,5000.0)
    return book

class TestEEPBookExpanded:
    def test_installation_id_format(self):
        book = _eep()
        assert book._installs[0].installation_id == "EEP-00001"

    def test_customer_cost_gbp(self):
        book = _eep()
        inst = book._installs[0]
        assert inst.customer_cost_gbp == pytest.approx(200.0)

    def test_simple_payback_years(self):
        book = _eep()
        inst = book._installs[0]
        assert inst.simple_payback_years == pytest.approx(200/400, rel=0.01)

    def test_installs_for_customer(self):
        book = _eep()
        assert len(book.installs_for_customer("C1")) == 2

    def test_total_subsidy_all(self):
        book = _eep()
        assert book.total_subsidy_gbp() == pytest.approx(1800+2400+5000)

    def test_total_subsidy_by_scheme(self):
        book = _eep()
        assert book.total_subsidy_gbp(scheme=EEPScheme.ECO4) == pytest.approx(4200.0)

    def test_total_subsidy_by_year(self):
        book = _eep()
        assert book.total_subsidy_gbp(year=2022) == pytest.approx(4200.0)

    def test_estimated_savings_portfolio(self):
        book = _eep()
        assert book.estimated_savings_portfolio_gbp(2022) == pytest.approx(1000.0)

    def test_annual_summary_by_measure(self):
        book = _eep()
        s = book.annual_summary(2022)
        assert "by_measure" in s and s["installations"] == 2

    def test_annual_summary_savings(self):
        book = _eep()
        s = book.annual_summary(2022)
        assert s["estimated_savings_gbp"] == pytest.approx(1000.0)


# ===== meter_read_validation =====
from company.billing.meter_read_validation import (
    MeterReadValidation, ValidationResult, ValidationFlag, ReadSource
)

def _good_read():
    return MeterReadValidation(
        read_date=dt.date(2022,2,1),
        read_value=10300.0,
        previous_read=10000.0,
        previous_read_date=dt.date(2022,1,1),
        expected_daily_kwh=10.0,
        source=ReadSource.CUSTOMER,
    )

def _reversal_read():
    return MeterReadValidation(
        read_date=dt.date(2022,2,1),
        read_value=9900.0,  # lower than previous
        previous_read=10000.0,
        previous_read_date=dt.date(2022,1,1),
        expected_daily_kwh=10.0,
        source=ReadSource.CUSTOMER,
    )

def _excessive_read():
    return MeterReadValidation(
        read_date=dt.date(2022,2,1),
        read_value=14000.0,  # 4000 kWh in 31 days = 129/day vs 10 expected
        previous_read=10000.0,
        previous_read_date=dt.date(2022,1,1),
        expected_daily_kwh=10.0,
        source=ReadSource.CUSTOMER,
    )

class TestMeterReadValidationExpanded:
    def test_advance_kwh(self):
        r = _good_read()
        assert r.advance_kwh == pytest.approx(300.0)

    def test_implied_daily_kwh(self):
        r = _good_read()
        assert r.implied_daily_kwh == pytest.approx(300/31, rel=0.01)

    def test_days_elapsed(self):
        r = _good_read()
        assert r.days_elapsed == 31

    def test_accepted_when_no_flags(self):
        r = _good_read()
        assert r.result == ValidationResult.ACCEPTED
        assert not r.flags

    def test_reversal_flagged_and_rejected(self):
        r = _reversal_read()
        assert ValidationFlag.REVERSAL in r.flags
        assert r.result == ValidationResult.REJECTED

    def test_excessive_daily_rate_rejected(self):
        r = _excessive_read()
        assert ValidationFlag.EXCESSIVE_DAILY_RATE in r.flags
        assert r.result == ValidationResult.REJECTED

    def test_zero_advance_over_7_days(self):
        r = MeterReadValidation(
            read_date=dt.date(2022,2,1),
            read_value=10000.0,  # same as previous
            previous_read=10000.0,
            previous_read_date=dt.date(2022,1,1),
            expected_daily_kwh=10.0,
            source=ReadSource.SMART_METER,
        )
        assert ValidationFlag.METER_ADVANCE_ZERO in r.flags
        assert r.result == ValidationResult.QUERIED

    def test_advance_kwh_negative_for_reversal(self):
        r = _reversal_read()
        assert r.advance_kwh < 0

    def test_summary_keys(self):
        r = _good_read()
        s = r.summary()
        assert "result" in s and "flags" in s

    def test_low_daily_rate_flagged_as_queried(self):
        r = MeterReadValidation(
            read_date=dt.date(2022,2,1),
            read_value=10010.0,  # only 10 kWh in 31 days = 0.32/day vs 10 expected
            previous_read=10000.0,
            previous_read_date=dt.date(2022,1,1),
            expected_daily_kwh=10.0,
            source=ReadSource.CUSTOMER,
        )
        assert ValidationFlag.LOW_DAILY_RATE in r.flags
        assert r.result == ValidationResult.QUERIED
