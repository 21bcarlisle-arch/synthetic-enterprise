"""Phase NA: Customer Satisfaction Accumulator tests (Dim 4 emotional).

Tests company/crm/satisfaction_accumulator.py -- company-side observable signals only.
"""
import pytest
from company.crm.satisfaction_accumulator import (
    CustomerSatisfactionAccumulator,
    _BASELINE_SATISFACTION,
    _BILL_SHOCK_DELTA,
    _COMPLAINT_RAISED_DELTA,
    _COMPLAINT_RESOLVED_DELTA,
    _CSS_GOOD_DELTA,
    _CSS_POOR_DELTA,
    _LOW_SATISFACTION_THRESHOLD,
    _MONTHLY_DECAY_RATE,
)


def test_initial_satisfaction_is_baseline():
    acc = CustomerSatisfactionAccumulator()
    assert abs(acc.get_satisfaction("C1") - _BASELINE_SATISFACTION) < 1e-9


def test_bill_shock_reduces_satisfaction():
    acc = CustomerSatisfactionAccumulator()
    before = acc.get_satisfaction("C1")
    acc.record_bill_shock("C1")
    assert acc.get_satisfaction("C1") < before


def test_bill_shock_delta_correct():
    acc = CustomerSatisfactionAccumulator()
    acc.record_bill_shock("C1")
    expected = _BASELINE_SATISFACTION + _BILL_SHOCK_DELTA
    assert abs(acc.get_satisfaction("C1") - expected) < 1e-9


def test_multiple_bill_shocks_accumulate():
    acc = CustomerSatisfactionAccumulator()
    acc.record_bill_shock("C1")
    acc.record_bill_shock("C1")
    expected = _BASELINE_SATISFACTION + 2 * _BILL_SHOCK_DELTA
    assert abs(acc.get_satisfaction("C1") - expected) < 1e-9


def test_complaint_raised_reduces_more_than_bill_shock():
    acc = CustomerSatisfactionAccumulator()
    acc.record_complaint_raised("C1")
    p_complaint = acc.get_satisfaction("C1")
    
    acc2 = CustomerSatisfactionAccumulator()
    acc2.record_bill_shock("C1")
    p_shock = acc2.get_satisfaction("C1")
    
    assert p_complaint < p_shock


def test_complaint_resolved_adds_recovery():
    acc = CustomerSatisfactionAccumulator()
    acc.record_complaint_raised("C1")
    score_after_complaint = acc.get_satisfaction("C1")
    acc.record_complaint_resolved("C1")
    assert acc.get_satisfaction("C1") > score_after_complaint


def test_css_good_score_improves_satisfaction():
    acc = CustomerSatisfactionAccumulator()
    before = acc.get_satisfaction("C1")
    acc.record_css_score("C1", 8.0)
    assert acc.get_satisfaction("C1") > before


def test_css_poor_score_reduces_satisfaction():
    acc = CustomerSatisfactionAccumulator()
    before = acc.get_satisfaction("C1")
    acc.record_css_score("C1", 3.0)
    assert acc.get_satisfaction("C1") < before


def test_css_neutral_score_no_change():
    acc = CustomerSatisfactionAccumulator()
    before = acc.get_satisfaction("C1")
    acc.record_css_score("C1", 5.5)  # between 4.0 and 7.0
    assert abs(acc.get_satisfaction("C1") - before) < 1e-9


def test_satisfaction_clamped_at_one():
    acc = CustomerSatisfactionAccumulator()
    for _ in range(100):
        acc.record_css_score("C1", 9.0)
    assert acc.get_satisfaction("C1") <= 1.0


def test_satisfaction_clamped_at_zero():
    acc = CustomerSatisfactionAccumulator()
    for _ in range(100):
        acc.record_bill_shock("C1")
    assert acc.get_satisfaction("C1") >= 0.0


def test_is_low_satisfaction_below_threshold():
    acc = CustomerSatisfactionAccumulator()
    for _ in range(20):
        acc.record_bill_shock("C1")
    assert acc.is_low_satisfaction("C1") is True


def test_is_low_satisfaction_above_threshold_false():
    acc = CustomerSatisfactionAccumulator()
    assert acc.is_low_satisfaction("C1") is False  # baseline is above threshold


def test_low_satisfaction_customers_returns_ids():
    acc = CustomerSatisfactionAccumulator()
    for _ in range(20):
        acc.record_bill_shock("C1")
    acc.get_satisfaction("C2")  # initialise but don't lower
    low = acc.low_satisfaction_customers()
    assert "C1" in low
    assert "C2" not in low


def test_two_customers_independent():
    acc = CustomerSatisfactionAccumulator()
    acc.record_bill_shock("C1")
    s1 = acc.get_satisfaction("C1")
    s2 = acc.get_satisfaction("C2")
    assert s1 < s2


def test_monthly_decay_toward_baseline_from_above():
    acc = CustomerSatisfactionAccumulator()
    for _ in range(5):
        acc.record_css_score("C1", 9.0)
    score_high = acc.get_satisfaction("C1")
    assert score_high > _BASELINE_SATISFACTION
    acc.apply_monthly_decay("C1", months=100)
    assert abs(acc.get_satisfaction("C1") - _BASELINE_SATISFACTION) < 1e-9


def test_monthly_decay_toward_baseline_from_below():
    acc = CustomerSatisfactionAccumulator()
    for _ in range(5):
        acc.record_bill_shock("C1")
    score_low = acc.get_satisfaction("C1")
    assert score_low < _BASELINE_SATISFACTION
    acc.apply_monthly_decay("C1", months=100)
    assert abs(acc.get_satisfaction("C1") - _BASELINE_SATISFACTION) < 1e-9


def test_monthly_decay_per_month_rate():
    acc = CustomerSatisfactionAccumulator()
    # Set to higher than baseline
    for _ in range(3):
        acc.record_css_score("C1", 9.0)
    before = acc.get_satisfaction("C1")
    assert before > _BASELINE_SATISFACTION
    acc.apply_monthly_decay("C1", months=1)
    after = acc.get_satisfaction("C1")
    assert abs((before - after) - _MONTHLY_DECAY_RATE) < 1e-9


def test_complaint_delta_correct():
    acc = CustomerSatisfactionAccumulator()
    acc.record_complaint_raised("C1")
    expected = _BASELINE_SATISFACTION + _COMPLAINT_RAISED_DELTA
    assert abs(acc.get_satisfaction("C1") - expected) < 1e-9


def test_css_good_delta_correct():
    acc = CustomerSatisfactionAccumulator()
    acc.record_css_score("C1", 8.0)
    expected = _BASELINE_SATISFACTION + _CSS_GOOD_DELTA
    assert abs(acc.get_satisfaction("C1") - expected) < 1e-9


def test_get_trajectory_empty_before_any_snapshot():
    acc = CustomerSatisfactionAccumulator()
    acc.get_satisfaction("C1")
    assert acc.get_trajectory("C1") == []


def test_record_year_snapshot_captures_current_score():
    acc = CustomerSatisfactionAccumulator()
    acc.record_bill_shock("C1")
    acc.record_year_snapshot("C1", 2018)
    traj = acc.get_trajectory("C1")
    assert traj == [{"year": 2018, "satisfaction_score": round(_BASELINE_SATISFACTION + _BILL_SHOCK_DELTA, 4)}]


def test_record_year_snapshot_multiple_years_sorted():
    acc = CustomerSatisfactionAccumulator()
    acc.record_year_snapshot("C1", 2020)
    acc.record_bill_shock("C1")
    acc.record_year_snapshot("C1", 2018)
    traj = acc.get_trajectory("C1")
    assert [pt["year"] for pt in traj] == [2018, 2020]


def test_record_year_snapshot_same_year_overwrites_not_duplicates():
    acc = CustomerSatisfactionAccumulator()
    acc.record_year_snapshot("C1", 2019)
    acc.record_bill_shock("C1")
    acc.record_year_snapshot("C1", 2019)
    traj = acc.get_trajectory("C1")
    assert len(traj) == 1
    assert traj[0]["satisfaction_score"] == round(_BASELINE_SATISFACTION + _BILL_SHOCK_DELTA, 4)


def test_trajectory_independent_per_customer():
    acc = CustomerSatisfactionAccumulator()
    acc.record_bill_shock("C1")
    acc.record_year_snapshot("C1", 2018)
    acc.record_year_snapshot("C2", 2018)
    assert acc.get_trajectory("C1") != acc.get_trajectory("C2")
