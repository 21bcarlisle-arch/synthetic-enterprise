import datetime as dt
import pytest
from company.billing.payment_behaviour import (
    PaymentResult, PaymentBehaviour, PaymentRecord, PaymentBehaviourAnalytics
)


def test_on_time_record():
    r = PaymentRecord('C001', dt.date(2022, 3, 1), 100.0, 100.0,
                       dt.date(2022, 3, 1), PaymentResult.ON_TIME)
    assert r.days_late == 0
    assert r.shortfall_gbp == pytest.approx(0.0)


def test_late_record_days():
    r = PaymentRecord('C001', dt.date(2022, 3, 1), 100.0, 100.0,
                       dt.date(2022, 3, 8), PaymentResult.LATE)
    assert r.days_late == 7


def test_partial_shortfall():
    r = PaymentRecord('C001', dt.date(2022, 3, 1), 200.0, 150.0,
                       dt.date(2022, 3, 1), PaymentResult.PARTIAL)
    assert r.shortfall_gbp == pytest.approx(50.0)


def test_on_time_rate_perfect():
    a = PaymentBehaviourAnalytics()
    for i in range(5):
        a.record('C001', dt.date(2022, i+1, 1), 100.0, 100.0,
                  dt.date(2022, i+1, 1), PaymentResult.ON_TIME)
    assert a.on_time_rate('C001') == pytest.approx(100.0)
    assert a.behaviour_score('C001') == PaymentBehaviour.EXCELLENT


def test_dd_failure_rate():
    a = PaymentBehaviourAnalytics()
    a.record('C001', dt.date(2022, 1, 1), 100.0, 0.0, None, PaymentResult.DD_FAILED)
    a.record('C001', dt.date(2022, 2, 1), 100.0, 100.0, dt.date(2022, 2, 1), PaymentResult.ON_TIME)
    a.record('C001', dt.date(2022, 3, 1), 100.0, 100.0, dt.date(2022, 3, 1), PaymentResult.ON_TIME)
    assert a.dd_failure_rate('C001') == pytest.approx(100/3, rel=0.01)


def test_behaviour_score_critical():
    a = PaymentBehaviourAnalytics()
    for i in range(3):
        a.record('C001', dt.date(2022, i+1, 1), 100.0, 0.0, None, PaymentResult.MISSED)
    a.record('C001', dt.date(2022, 4, 1), 100.0, 100.0, dt.date(2022, 4, 1), PaymentResult.ON_TIME)
    # 3/4 = 75% missed -> CRITICAL
    assert a.behaviour_score('C001') == PaymentBehaviour.CRITICAL


def test_avg_days_late():
    a = PaymentBehaviourAnalytics()
    a.record('C001', dt.date(2022, 1, 1), 100.0, 100.0,
              dt.date(2022, 1, 6), PaymentResult.LATE)
    a.record('C001', dt.date(2022, 2, 1), 100.0, 100.0,
              dt.date(2022, 2, 11), PaymentResult.LATE)
    assert a.avg_days_late('C001') == pytest.approx(7.5)


def test_total_shortfall():
    a = PaymentBehaviourAnalytics()
    a.record('C001', dt.date(2022, 1, 1), 300.0, 200.0,
              dt.date(2022, 1, 1), PaymentResult.PARTIAL)
    a.record('C001', dt.date(2022, 2, 1), 300.0, 300.0,
              dt.date(2022, 2, 1), PaymentResult.ON_TIME)
    assert a.total_shortfall_gbp('C001') == pytest.approx(100.0)


def test_portfolio_summary():
    a = PaymentBehaviourAnalytics()
    a.record('C001', dt.date(2022, 1, 1), 100.0, 100.0,
              dt.date(2022, 1, 1), PaymentResult.ON_TIME)
    a.record('C002', dt.date(2022, 1, 1), 100.0, 0.0, None, PaymentResult.MISSED)
    a.record('C002', dt.date(2022, 2, 1), 100.0, 0.0, None, PaymentResult.MISSED)
    s = a.portfolio_summary()
    assert s['total_customers'] == 2
    assert 'excellent' in s['by_behaviour']
    assert 'critical' in s['by_behaviour']


# --- Phase KT depth tests ---

def test_customer_id_stored():
    r = PaymentRecord('CUST_KT', dt.date(2022,3,1), 100.0, 100.0, dt.date(2022,3,1), PaymentResult.ON_TIME)
    assert r.customer_id == 'CUST_KT'


def test_due_date_stored():
    r = PaymentRecord('C001', dt.date(2022,5,15), 100.0, 100.0, dt.date(2022,5,15), PaymentResult.ON_TIME)
    assert r.due_date == dt.date(2022, 5, 15)


def test_amount_due_stored():
    r = PaymentRecord('C001', dt.date(2022,1,1), 250.0, 250.0, dt.date(2022,1,1), PaymentResult.ON_TIME)
    assert r.amount_due_gbp == pytest.approx(250.0)


def test_amount_paid_stored():
    r = PaymentRecord('C001', dt.date(2022,1,1), 200.0, 180.0, dt.date(2022,1,1), PaymentResult.PARTIAL)
    assert r.amount_paid_gbp == pytest.approx(180.0)


def test_result_stored():
    r = PaymentRecord('C001', dt.date(2022,1,1), 100.0, 0.0, None, PaymentResult.MISSED)
    assert r.result == PaymentResult.MISSED


def test_on_time_rate_none_unknown_customer():
    a = PaymentBehaviourAnalytics()
    assert a.on_time_rate('UNKNOWN') is None


def test_avg_days_late_none_unknown():
    a = PaymentBehaviourAnalytics()
    assert a.avg_days_late('UNKNOWN') is None


def test_total_shortfall_zero_unknown():
    a = PaymentBehaviourAnalytics()
    assert a.total_shortfall_gbp('UNKNOWN') == pytest.approx(0.0)


def test_behaviour_score_excellent_all_on_time():
    a = PaymentBehaviourAnalytics()
    for i in range(3):
        a.record('C1', dt.date(2022, i+1, 1), 100.0, 100.0, dt.date(2022, i+1, 1), PaymentResult.ON_TIME)
    assert a.behaviour_score('C1') == PaymentBehaviour.EXCELLENT


def test_dd_failure_rate_zero_no_failures():
    a = PaymentBehaviourAnalytics()
    a.record('C1', dt.date(2022,1,1), 100.0, 100.0, dt.date(2022,1,1), PaymentResult.ON_TIME)
    assert a.dd_failure_rate('C1') == pytest.approx(0.0)
