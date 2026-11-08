# Increment 3: the legs of tests/company/test_phase_js_coverage_depth.py that test archived modules. Its live legs stay there.
"""Phase JS: Coverage Depth Sprint XLI -- 30 tests.

Modules:
  eep_book: ID sequencing, payback None, scheme/year filter, empty customer, by_measure
  meter_read_validation: boundary thresholds, transposition, source stored, summary values
  capacity_to_pay: outcome boundaries, extended plan, repayment floor, estimated months
"""
import datetime as dt
import pytest
from company.crm.eep_book import EEPMeasure, EEPScheme, EEPInstallation, EEPBook
from company.billing.capacity_to_pay import (
    AffordabilityOutcome, RecommendedAction, CtPAssessment,
    _MINIMUM_PAYMENT_GBP, _EXTENDED_PLAN_MONTHS,
)


# ---------------------------------------------------------------------------
# eep_book -- 10 tests
# ---------------------------------------------------------------------------

def _eep_book():
    book = EEPBook()
    book.record("C001", "1200011111", EEPMeasure.LOFT_INSULATION, EEPScheme.ECO4,
                dt.date(2022, 9, 15), estimated_annual_saving_gbp=180.0,
                cost_gbp=1500.0, subsidy_gbp=1500.0)
    book.record("C002", "1200022222", EEPMeasure.HEAT_PUMP, EEPScheme.BUS,
                dt.date(2022, 11, 1), estimated_annual_saving_gbp=600.0,
                cost_gbp=14_000.0, subsidy_gbp=7_500.0)
    book.record("C003", "1200033333", EEPMeasure.SOLAR_PV, EEPScheme.SEG,
                dt.date(2021, 5, 20), estimated_annual_saving_gbp=350.0,
                cost_gbp=6_000.0, subsidy_gbp=0.0)
    return book


def test_eep_id_sequential():
    book = EEPBook()
    i1 = book.record("C001", "1200011111", EEPMeasure.BOILER_UPGRADE, EEPScheme.SELF_FUNDED,
                     dt.date(2023, 1, 1), estimated_annual_saving_gbp=200.0,
                     cost_gbp=3000.0, subsidy_gbp=0.0)
    i2 = book.record("C002", "1200022222", EEPMeasure.SOLAR_PV, EEPScheme.SEG,
                     dt.date(2023, 2, 1), estimated_annual_saving_gbp=300.0,
                     cost_gbp=5000.0, subsidy_gbp=0.0)
    assert i1.installation_id == "EEP-00001"
    assert i2.installation_id == "EEP-00002"


def test_eep_simple_payback_none_zero_saving():
    book = EEPBook()
    inst = book.record("C001", "1200011111", EEPMeasure.DOUBLE_GLAZING, EEPScheme.SELF_FUNDED,
                       dt.date(2023, 1, 1), estimated_annual_saving_gbp=0.0,
                       cost_gbp=2000.0, subsidy_gbp=0.0)
    assert inst.simple_payback_years is None


def test_eep_total_subsidy_bus_scheme():
    book = _eep_book()
    assert book.total_subsidy_gbp(scheme=EEPScheme.BUS) == pytest.approx(7500.0)


def test_eep_total_subsidy_year_2021():
    book = _eep_book()
    assert book.total_subsidy_gbp(year=2021) == pytest.approx(0.0)


def test_eep_total_subsidy_no_filter():
    book = _eep_book()
    assert book.total_subsidy_gbp() == pytest.approx(1500.0 + 7500.0 + 0.0)


def test_eep_estimated_savings_all_years():
    book = _eep_book()
    assert book.estimated_savings_portfolio_gbp() == pytest.approx(180.0 + 600.0 + 350.0)


def test_eep_installs_for_unknown_customer():
    book = _eep_book()
    assert book.installs_for_customer("UNKNOWN") == []


def test_eep_annual_summary_by_measure_contains_loft():
    book = _eep_book()
    s = book.annual_summary(2022)
    assert "loft_insulation" in s["by_measure"]
    assert s["by_measure"]["loft_insulation"] == 1


def test_eep_customer_cost_partial_subsidy():
    book = _eep_book()
    inst = book.installs_for_customer("C002")[0]
    assert inst.customer_cost_gbp == pytest.approx(14_000.0 - 7_500.0)


def test_eep_annual_summary_empty_year():
    book = _eep_book()
    s = book.annual_summary(2020)
    assert s["installations"] == 0
    assert s["total_subsidy_gbp"] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# capacity_to_pay -- 10 tests
# ---------------------------------------------------------------------------

def _ctp(income, outgoings, debt, vulnerable=False):
    return CtPAssessment("C001", dt.date(2022, 6, 1),
                         monthly_income_gbp=income,
                         monthly_essential_outgoings_gbp=outgoings,
                         total_debt_gbp=debt,
                         is_vulnerable=vulnerable)


def test_ctp_disposable_floors_at_zero():
    a = _ctp(income=1000.0, outgoings=1500.0, debt=200.0)
    assert a.disposable_income_gbp == pytest.approx(0.0)


def test_ctp_energy_share_none_zero_income():
    a = _ctp(income=0.0, outgoings=0.0, debt=500.0)
    assert a.energy_share_of_income_pct is None


def test_ctp_estimated_plan_months_none_cannot_pay():
    a = _ctp(income=1000.0, outgoings=1000.0, debt=500.0)
    assert a.outcome == AffordabilityOutcome.CANNOT_PAY
    assert a.estimated_plan_months is None


def test_ctp_estimated_plan_months_computed():
    a = _ctp(income=3000.0, outgoings=2000.0, debt=500.0)
    assert a.outcome == AffordabilityOutcome.CAN_PAY_IN_FULL
    assert a.estimated_plan_months == 5


def test_ctp_extended_plan():
    a = _ctp(income=2000.0, outgoings=1500.0, debt=1000.0)
    assert a.outcome == AffordabilityOutcome.CAN_PAY_PARTIAL
    repayment_months = 1000.0 / 50.0
    assert repayment_months <= _EXTENDED_PLAN_MONTHS
    assert a.recommended_action == RecommendedAction.EXTENDED_PLAN


def test_ctp_affordable_repayment_capped_at_debt():
    a = _ctp(income=5000.0, outgoings=0.0, debt=100.0)
    assert a.affordable_monthly_repayment_gbp == pytest.approx(100.0)


def test_ctp_exact_10pct_is_fuel_poverty():
    a = _ctp(income=1000.0, outgoings=900.0, debt=1200.0)
    assert a.energy_share_of_income_pct == pytest.approx(10.0)
    assert a.outcome == AffordabilityOutcome.FUEL_POVERTY


def test_ctp_just_below_10pct_not_fuel_poverty():
    a = _ctp(income=1000.0, outgoings=900.0, debt=1140.0)
    share = a.energy_share_of_income_pct
    assert share is not None and share < 10.0
    assert a.outcome != AffordabilityOutcome.FUEL_POVERTY


def test_ctp_summary_assessment_date_iso():
    a = _ctp(income=3000.0, outgoings=2000.0, debt=500.0)
    s = a.summary()
    assert s["assessment_date"] == "2022-06-01"


def test_ctp_minimum_payment_floor_in_plan_months():
    a = _ctp(income=1010.0, outgoings=1000.0, debt=200.0)
    assert a.affordable_monthly_repayment_gbp == pytest.approx(1.0)
    assert a.estimated_plan_months == round(200.0 / _MINIMUM_PAYMENT_GBP)
