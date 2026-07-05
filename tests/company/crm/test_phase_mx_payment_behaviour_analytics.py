"""Phase MX: Company-side PaymentBehaviourAnalytics tests.

Tests score_payment_history, compute_payment_metrics, and PaymentBehaviourAnalytics
using only observable payment record dicts (ON_TIME/LATE/DD_FAILED).
"""
import pytest
from company.crm.payment_behaviour_analytics import (
    BehaviourScore,
    PaymentBehaviourAnalytics,
    compute_payment_metrics,
    score_payment_history,
    _SCORE_ORDER,
)


def _on_time(n=1):
    return [{"result": "ON_TIME"} for _ in range(n)]


def _late(n=1, days=10):
    return [{"result": "LATE", "days_late": days} for _ in range(n)]


def _dd(n=1):
    return [{"result": "DD_FAILED"} for _ in range(n)]


# --- score_payment_history ---

def test_score_all_on_time_is_EXCELLENT():
    assert score_payment_history(_on_time(20)) == BehaviourScore.EXCELLENT


def test_score_mostly_on_time_is_GOOD():
    # 16 on_time + 1 late = 94% on_time, 0 dd_fail -> GOOD (not EXCELLENT because 94 < 95)
    records = _on_time(16) + _late(1)
    assert score_payment_history(records) == BehaviourScore.GOOD


def test_score_mixed_is_FAIR():
    # 6 on_time + 4 late = 60% on_time, 0 dd_fail -> FAIR (boundary)
    records = _on_time(6) + _late(4)
    assert score_payment_history(records) == BehaviourScore.FAIR


def test_score_mostly_late_is_POOR():
    # 4 on_time + 6 late = 40% on_time, 0 dd_fail -> POOR (boundary)
    records = _on_time(4) + _late(6)
    assert score_payment_history(records) == BehaviourScore.POOR


def test_score_all_dd_failed_is_CRITICAL():
    assert score_payment_history(_dd(10)) == BehaviourScore.CRITICAL


def test_score_empty_history_returns_EXCELLENT():
    assert score_payment_history([]) == BehaviourScore.EXCELLENT


def test_dd_fail_rate_dominates_over_on_time_rate():
    # 85% on_time looks like GOOD but 1 dd_fail out of 10 = 10% dd_fail_rate -> FAIR
    records = _on_time(8) + _late(1) + _dd(1)
    result = score_payment_history(records)
    assert result in (BehaviourScore.FAIR, BehaviourScore.POOR, BehaviourScore.CRITICAL)
    assert result != BehaviourScore.EXCELLENT
    assert result != BehaviourScore.GOOD


# --- compute_payment_metrics ---

def test_compute_metrics_on_time_rate():
    records = _on_time(9) + _late(1)
    m = compute_payment_metrics(records)
    assert abs(m["on_time_rate"] - 0.9) < 0.001


def test_compute_metrics_late_rate():
    records = _on_time(8) + _late(2)
    m = compute_payment_metrics(records)
    assert abs(m["late_rate"] - 0.2) < 0.001


def test_compute_metrics_dd_fail_rate():
    records = _on_time(8) + _dd(2)
    m = compute_payment_metrics(records)
    assert abs(m["dd_fail_rate"] - 0.2) < 0.001


def test_compute_metrics_avg_days_late():
    records = _late(2, days=10) + _late(2, days=30)
    m = compute_payment_metrics(records)
    assert abs(m["avg_days_late"] - 20.0) < 0.001


# --- PaymentBehaviourAnalytics ---

def test_record_and_get_score():
    pba = PaymentBehaviourAnalytics()
    for r in _on_time(10):
        pba.record_payment("C1", r)
    assert pba.get_score("C1") == BehaviourScore.EXCELLENT


def test_get_score_none_when_no_history():
    pba = PaymentBehaviourAnalytics()
    assert pba.get_score("unknown") is None


def test_get_metrics_none_when_no_history():
    pba = PaymentBehaviourAnalytics()
    assert pba.get_metrics("unknown") is None


def test_is_at_risk_POOR_true():
    pba = PaymentBehaviourAnalytics()
    for r in _on_time(4) + _late(6):
        pba.record_payment("C1", r)
    assert pba.is_at_risk("C1") is True


def test_is_at_risk_CRITICAL_true():
    pba = PaymentBehaviourAnalytics()
    for r in _dd(10):
        pba.record_payment("C1", r)
    assert pba.is_at_risk("C1") is True


def test_is_at_risk_GOOD_false():
    pba = PaymentBehaviourAnalytics()
    for r in _on_time(9) + _late(1):
        pba.record_payment("C1", r)
    assert pba.is_at_risk("C1") is False


def test_at_risk_customers_returns_correct_ids():
    pba = PaymentBehaviourAnalytics()
    for r in _on_time(10):
        pba.record_payment("C_good", r)
    for r in _dd(10):
        pba.record_payment("C_bad", r)
    at_risk = pba.at_risk_customers()
    assert "C_bad" in at_risk
    assert "C_good" not in at_risk


def test_at_risk_customers_empty_when_none_at_risk():
    pba = PaymentBehaviourAnalytics()
    for r in _on_time(10):
        pba.record_payment("C1", r)
    assert pba.at_risk_customers() == []


def test_score_trend_DETERIORATING_when_score_drops():
    pba = PaymentBehaviourAnalytics()
    # First half: all on time (EXCELLENT), second half: all DD_FAILED (CRITICAL)
    for r in _on_time(4):
        pba.record_payment("C1", r)
    for r in _dd(4):
        pba.record_payment("C1", r)
    assert pba.score_trend("C1", window=8) == "DETERIORATING"


def test_score_trend_IMPROVING_when_score_rises():
    pba = PaymentBehaviourAnalytics()
    # First half: all DD_FAILED (CRITICAL), second half: all on time (EXCELLENT)
    for r in _dd(4):
        pba.record_payment("C1", r)
    for r in _on_time(4):
        pba.record_payment("C1", r)
    assert pba.score_trend("C1", window=8) == "IMPROVING"


def test_score_trend_STABLE_when_unchanged():
    pba = PaymentBehaviourAnalytics()
    for r in _on_time(8):
        pba.record_payment("C1", r)
    assert pba.score_trend("C1", window=8) == "STABLE"


def test_two_customers_independent_scores():
    pba = PaymentBehaviourAnalytics()
    for r in _on_time(10):
        pba.record_payment("C1", r)
    for r in _dd(10):
        pba.record_payment("C2", r)
    assert pba.get_score("C1") == BehaviourScore.EXCELLENT
    assert pba.get_score("C2") == BehaviourScore.CRITICAL


def test_record_accumulates():
    pba = PaymentBehaviourAnalytics()
    pba.record_payment("C1", {"result": "ON_TIME"})
    pba.record_payment("C1", {"result": "ON_TIME"})
    pba.record_payment("C1", {"result": "LATE"})
    m = pba.get_metrics("C1")
    assert abs(m["on_time_rate"] - 2/3) < 0.001
    assert abs(m["late_rate"] - 1/3) < 0.001


def test_BehaviourScore_ordering_EXCELLENT_best():
    assert _SCORE_ORDER[BehaviourScore.EXCELLENT] < _SCORE_ORDER[BehaviourScore.GOOD]
    assert _SCORE_ORDER[BehaviourScore.GOOD] < _SCORE_ORDER[BehaviourScore.FAIR]
    assert _SCORE_ORDER[BehaviourScore.FAIR] < _SCORE_ORDER[BehaviourScore.POOR]
    assert _SCORE_ORDER[BehaviourScore.POOR] < _SCORE_ORDER[BehaviourScore.CRITICAL]


# --- get_miss_trajectory (Phase QV: event frequency panel data model) ---

def test_miss_trajectory_empty_when_no_history():
    pba = PaymentBehaviourAnalytics()
    assert pba.get_miss_trajectory("unknown") == []


def test_miss_trajectory_ignores_records_without_due_date():
    pba = PaymentBehaviourAnalytics()
    pba.record_payment("C1", {"result": "LATE"})
    assert pba.get_miss_trajectory("C1") == []


def test_miss_trajectory_buckets_by_year_from_due_date():
    from datetime import date
    pba = PaymentBehaviourAnalytics()
    pba.record_payment("C1", {"result": "ON_TIME", "due_date": date(2020, 1, 28)})
    pba.record_payment("C1", {"result": "LATE", "due_date": date(2020, 2, 28)})
    pba.record_payment("C1", {"result": "DD_FAILED", "due_date": date(2021, 1, 28)})
    traj = pba.get_miss_trajectory("C1")
    assert traj == [
        {"year": 2020, "late": 1, "dd_failed": 0, "total": 2},
        {"year": 2021, "late": 0, "dd_failed": 1, "total": 1},
    ]


def test_miss_trajectory_sorted_ascending_regardless_of_insertion_order():
    from datetime import date
    pba = PaymentBehaviourAnalytics()
    pba.record_payment("C1", {"result": "LATE", "due_date": date(2022, 1, 28)})
    pba.record_payment("C1", {"result": "LATE", "due_date": date(2019, 1, 28)})
    traj = pba.get_miss_trajectory("C1")
    assert [pt["year"] for pt in traj] == [2019, 2022]


def test_miss_trajectory_accepts_string_due_date():
    pba = PaymentBehaviourAnalytics()
    pba.record_payment("C1", {"result": "DD_FAILED", "due_date": "2023-06-28"})
    traj = pba.get_miss_trajectory("C1")
    assert traj == [{"year": 2023, "late": 0, "dd_failed": 1, "total": 1}]


def test_miss_trajectory_independent_per_customer():
    from datetime import date
    pba = PaymentBehaviourAnalytics()
    pba.record_payment("C1", {"result": "DD_FAILED", "due_date": date(2020, 1, 28)})
    pba.record_payment("C2", {"result": "ON_TIME", "due_date": date(2020, 1, 28)})
    assert pba.get_miss_trajectory("C1") != pba.get_miss_trajectory("C2")


def test_integration_HIGH_stress_payments_produce_POOR_or_worse():
    """HIGH income_stress -> _PAYMENT_DELAY_DAYS HIGH(30-90), _ON_TIME_PROBABILITY=0.10.
    Observable pattern: mostly LATE/DD_FAILED. Company scores this POOR or CRITICAL.
    """
    from simulation.payment_timing import generate_payment_record
    from simulation.household import IncomeStress
    import random
    rng = random.Random(42)
    records = []
    for i in range(20):
        from datetime import date
        r = generate_payment_record(
            "C_test", date(2022, 1, 1), 100.0, IncomeStress.HIGH, rng
        )
        records.append(r)
    score = score_payment_history(records)
    assert score in (BehaviourScore.POOR, BehaviourScore.CRITICAL)
