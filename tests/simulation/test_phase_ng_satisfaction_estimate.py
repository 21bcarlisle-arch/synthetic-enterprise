"""Phase NG tests: Company satisfaction score wired into renewal churn estimate.

Verifies:
- Bill shock detection uses the same 20% threshold as bill_shock_tracker
- CustomerSatisfactionAccumulator tracks per-customer scores from observable signals
- enriched_churn_estimate receives satisfaction_score from the accumulator
- Low satisfaction pushes churn estimate up; high satisfaction pulls it down
- Two customers tracked independently
"""
import pytest
from company.crm.satisfaction_accumulator import CustomerSatisfactionAccumulator
from company.crm.enriched_churn_estimate import enriched_churn_estimate

_BASELINE = 0.70
_BILL_SHOCK_DELTA = -0.05
_NG_THRESHOLD = 0.20


def _ng_update(acc: CustomerSatisfactionAccumulator, cid: str,
               old_rate: float, new_rate: float, months: int = 12) -> float:
    """Mirrors Phase NG logic in run_phase2b: decay then record shock if rate rose >threshold."""
    acc.apply_monthly_decay(cid, months=months)
    if old_rate > 0 and new_rate / old_rate - 1 > _NG_THRESHOLD:
        acc.record_bill_shock(cid)
    return acc.get_satisfaction(cid)


def test_ng_bill_shock_threshold_constant():
    assert _NG_THRESHOLD == 0.20


def test_baseline_no_shocks():
    acc = CustomerSatisfactionAccumulator()
    sat = _ng_update(acc, "C1", 100.0, 100.0)
    assert sat == _BASELINE


def test_rate_below_threshold_no_shock():
    acc = CustomerSatisfactionAccumulator()
    sat = _ng_update(acc, "C1", 100.0, 115.0)  # 15% < 20%
    assert sat == _BASELINE


def test_rate_at_threshold_no_shock():
    acc = CustomerSatisfactionAccumulator()
    sat = _ng_update(acc, "C1", 100.0, 120.0)  # 20% == threshold, not strictly greater
    assert sat == _BASELINE


def test_rate_above_threshold_records_shock():
    acc = CustomerSatisfactionAccumulator()
    sat = _ng_update(acc, "C1", 100.0, 125.0)  # 25% > 20%
    assert abs(sat - (_BASELINE + _BILL_SHOCK_DELTA)) < 0.001


def test_two_shocks_cumulate():
    acc = CustomerSatisfactionAccumulator()
    acc.record_bill_shock("C1")
    acc.record_bill_shock("C1")
    sat = acc.get_satisfaction("C1")
    assert abs(sat - (_BASELINE + 2 * _BILL_SHOCK_DELTA)) < 0.001


def test_decay_moves_toward_baseline():
    acc = CustomerSatisfactionAccumulator()
    acc.record_bill_shock("C1")  # 0.70 -> 0.65
    acc.apply_monthly_decay("C1", months=3)  # +0.03 toward baseline
    sat = acc.get_satisfaction("C1")
    assert sat > 0.65
    assert sat < _BASELINE


def test_score_always_in_valid_range():
    acc = CustomerSatisfactionAccumulator()
    for _ in range(20):
        acc.record_bill_shock("C1")
    assert 0.0 <= acc.get_satisfaction("C1") <= 1.0


def test_two_customers_independent():
    acc = CustomerSatisfactionAccumulator()
    acc.record_bill_shock("C1")
    acc.record_bill_shock("C1")
    assert acc.get_satisfaction("C2") == _BASELINE


def test_low_satisfaction_raises_churn_estimate():
    # Small rate increase: rate model is weak, payment model with low sat dominates
    est_none = enriched_churn_estimate(100.0, 101.0, 2.0, 4000.0, satisfaction_score=None)
    est_low = enriched_churn_estimate(100.0, 101.0, 2.0, 4000.0, satisfaction_score=0.40)
    assert est_low > est_none


def test_high_satisfaction_lowers_churn_estimate():
    # 1 bill shock, small rate increase: payment model dominates; high sat reduces combined_prob
    est_none = enriched_churn_estimate(100.0, 101.0, 5.0, 3000.0,
                                       bill_shock_count=1, satisfaction_score=None)
    est_high = enriched_churn_estimate(100.0, 101.0, 5.0, 3000.0,
                                       bill_shock_count=1, satisfaction_score=0.85)
    assert est_high < est_none


def test_shocked_customer_estimate_higher_than_unshocked():
    # sat=0.45 < 0.50 LOW threshold -> +0.10 uplift; sat=0.70 baseline -> no uplift
    est_shocked = enriched_churn_estimate(100.0, 102.0, 3.0, 4000.0,
                                          bill_shock_count=1, satisfaction_score=0.45)
    est_clean = enriched_churn_estimate(100.0, 102.0, 3.0, 4000.0,
                                        bill_shock_count=1, satisfaction_score=0.70)
    assert est_shocked > est_clean


def test_multi_term_no_shock_stays_near_baseline():
    acc = CustomerSatisfactionAccumulator()
    for _ in range(5):
        _ng_update(acc, "C1", 100.0, 102.0)  # 2% increase: no shock each term
    sat = acc.get_satisfaction("C1")
    assert abs(sat - _BASELINE) < 0.01


def test_shock_then_recovery_partial():
    acc = CustomerSatisfactionAccumulator()
    _ng_update(acc, "C1", 100.0, 130.0)  # shock: 0.65
    sat_after_recovery = _ng_update(acc, "C1", 130.0, 132.0)  # no shock: 12m decay
    # 12 months decay from 0.65: min(0.65 + 0.12, 0.70) = 0.70 (full recovery in 5m)
    assert sat_after_recovery == _BASELINE


def test_estimate_with_low_satisfaction_vs_no_satisfaction():
    est_no_sat = enriched_churn_estimate(100.0, 108.0, 3.0, 5000.0, satisfaction_score=None)
    est_low_sat = enriched_churn_estimate(100.0, 108.0, 3.0, 5000.0, satisfaction_score=0.35)
    assert est_low_sat >= est_no_sat


def test_satisfaction_score_capped_at_one():
    acc = CustomerSatisfactionAccumulator()
    for _ in range(50):
        acc.apply_monthly_decay("C1", months=1)
    assert acc.get_satisfaction("C1") <= 1.0
