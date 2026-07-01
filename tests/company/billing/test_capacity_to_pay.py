import datetime as dt
import pytest
from company.billing.capacity_to_pay import (
    AffordabilityOutcome, RecommendedAction, CtPAssessment
)


def test_can_pay_in_full():
    a = CtPAssessment('C001', dt.date(2022, 6, 1),
                       monthly_income_gbp=3000.0,
                       monthly_essential_outgoings_gbp=2000.0,
                       total_debt_gbp=500.0)
    # disposable = 1000; 10% = 100/month; 500/100 = 5 months <= 12
    assert a.disposable_income_gbp == pytest.approx(1000.0)
    assert a.affordable_monthly_repayment_gbp == pytest.approx(100.0)
    assert a.outcome == AffordabilityOutcome.CAN_PAY_IN_FULL
    assert a.recommended_action == RecommendedAction.STANDARD_PLAN


def test_can_pay_partial_extended():
    a = CtPAssessment('C001', dt.date(2022, 6, 1),
                       monthly_income_gbp=2000.0,
                       monthly_essential_outgoings_gbp=1800.0,
                       total_debt_gbp=1200.0)
    # disposable = 200; 10% = 20/month; 1200/20 = 60 months > 12 -> partial
    # 60 <= 24 months? no, 60 > 24 -> MINIMUM_PLAN
    assert a.outcome == AffordabilityOutcome.CAN_PAY_PARTIAL
    assert a.recommended_action == RecommendedAction.MINIMUM_PLAN


def test_cannot_pay():
    a = CtPAssessment('C001', dt.date(2022, 6, 1),
                       monthly_income_gbp=1200.0,
                       monthly_essential_outgoings_gbp=1200.0,
                       total_debt_gbp=800.0)
    assert a.disposable_income_gbp == pytest.approx(0.0)
    assert a.outcome == AffordabilityOutcome.CANNOT_PAY
    assert a.recommended_action == RecommendedAction.WRITE_OFF_CONSIDERATION


def test_fuel_poverty_threshold():
    # debt £2400 on income £12000/yr = 20% -> fuel_poverty
    a = CtPAssessment('C001', dt.date(2022, 6, 1),
                       monthly_income_gbp=1000.0,
                       monthly_essential_outgoings_gbp=900.0,
                       total_debt_gbp=2000.0)
    # energy_share = 2000/(1000*12)*100 = 16.7% > 10% -> fuel_poverty
    assert a.outcome == AffordabilityOutcome.FUEL_POVERTY
    assert a.recommended_action == RecommendedAction.DEBT_ADVICE_REFERRAL


def test_fuel_poverty_vulnerable_ppm():
    a = CtPAssessment('C001', dt.date(2022, 6, 1),
                       monthly_income_gbp=1000.0,
                       monthly_essential_outgoings_gbp=900.0,
                       total_debt_gbp=2000.0,
                       is_vulnerable=True)
    assert a.recommended_action == RecommendedAction.PPM_CONVERSION


def test_energy_share_of_income():
    a = CtPAssessment('C001', dt.date(2022, 6, 1),
                       monthly_income_gbp=2000.0,
                       monthly_essential_outgoings_gbp=1000.0,
                       total_debt_gbp=4800.0)
    # 4800/(2000*12)*100 = 20%
    assert a.energy_share_of_income_pct == pytest.approx(20.0)


def test_summary_keys():
    a = CtPAssessment('C001', dt.date(2022, 6, 1),
                       monthly_income_gbp=3000.0,
                       monthly_essential_outgoings_gbp=2000.0,
                       total_debt_gbp=500.0)
    s = a.summary()
    assert s['customer_id'] == 'C001'
    assert 'recommended_action' in s
    assert 'estimated_plan_months' in s


# --- Phase KB depth tests ---

def test_extended_plan_at_24_months():
    a = CtPAssessment('C001', dt.date(2022, 6, 1),
                      monthly_income_gbp=1200.0,
                      monthly_essential_outgoings_gbp=1100.0,
                      total_debt_gbp=240.0)
    assert a.recommended_action == RecommendedAction.EXTENDED_PLAN


def test_minimum_plan_at_25_months():
    a = CtPAssessment('C001', dt.date(2022, 6, 1),
                      monthly_income_gbp=1200.0,
                      monthly_essential_outgoings_gbp=1100.0,
                      total_debt_gbp=250.0)
    assert a.recommended_action == RecommendedAction.MINIMUM_PLAN


def test_affordable_repayment_capped_at_debt():
    a = CtPAssessment('C001', dt.date(2022, 6, 1),
                      monthly_income_gbp=5000.0,
                      monthly_essential_outgoings_gbp=2000.0,
                      total_debt_gbp=50.0)
    assert a.affordable_monthly_repayment_gbp == pytest.approx(50.0)


def test_energy_share_none_when_zero_income():
    a = CtPAssessment('C001', dt.date(2022, 6, 1),
                      monthly_income_gbp=0.0,
                      monthly_essential_outgoings_gbp=0.0,
                      total_debt_gbp=500.0)
    assert a.energy_share_of_income_pct is None


def test_estimated_plan_months_none_when_cannot_pay():
    a = CtPAssessment('C001', dt.date(2022, 6, 1),
                      monthly_income_gbp=1000.0,
                      monthly_essential_outgoings_gbp=1000.0,
                      total_debt_gbp=800.0)
    assert a.outcome == AffordabilityOutcome.CANNOT_PAY
    assert a.estimated_plan_months is None


def test_estimated_plan_months_computed():
    a = CtPAssessment('C001', dt.date(2022, 6, 1),
                      monthly_income_gbp=2000.0,
                      monthly_essential_outgoings_gbp=1500.0,
                      total_debt_gbp=600.0)
    assert a.estimated_plan_months == 12


def test_fuel_poverty_exactly_10_pct():
    a = CtPAssessment('C001', dt.date(2022, 6, 1),
                      monthly_income_gbp=1000.0,
                      monthly_essential_outgoings_gbp=500.0,
                      total_debt_gbp=1200.0)
    assert a.energy_share_of_income_pct == pytest.approx(10.0)
    assert a.outcome == AffordabilityOutcome.FUEL_POVERTY


def test_energy_share_9_pct_not_fuel_poverty():
    a = CtPAssessment('C001', dt.date(2022, 6, 1),
                      monthly_income_gbp=1000.0,
                      monthly_essential_outgoings_gbp=500.0,
                      total_debt_gbp=1080.0)
    assert a.energy_share_of_income_pct == pytest.approx(9.0)
    assert a.outcome != AffordabilityOutcome.FUEL_POVERTY


def test_summary_date_isoformat():
    a = CtPAssessment('C001', dt.date(2022, 6, 1),
                      monthly_income_gbp=3000.0,
                      monthly_essential_outgoings_gbp=2000.0,
                      total_debt_gbp=500.0)
    assert a.summary()['assessment_date'] == '2022-06-01'


def test_minimum_payment_floor_applied():
    a = CtPAssessment('C001', dt.date(2022, 6, 1),
                      monthly_income_gbp=1001.0,
                      monthly_essential_outgoings_gbp=1000.0,
                      total_debt_gbp=100.0)
    assert a.estimated_plan_months == 20
