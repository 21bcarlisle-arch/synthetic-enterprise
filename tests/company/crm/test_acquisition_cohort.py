import datetime as dt
import pytest
from company.crm.acquisition_cohort import (
    AcquisitionChannel, CohortCustomer, AcquisitionCohort
)


def _make_cohort() -> AcquisitionCohort:
    coh = AcquisitionCohort(
        'Q1_2022_PCW', 2022, 1, AcquisitionChannel.PRICE_COMPARISON
    )
    coh.add_customer('C001', dt.date(2022, 1, 15), 80.0, 1200.0)
    coh.add_customer('C002', dt.date(2022, 1, 20), 75.0, 1100.0)
    coh.add_customer('C003', dt.date(2022, 1, 25), 90.0, 1300.0)
    return coh


def test_initial_size():
    coh = _make_cohort()
    assert coh.initial_size == 3


def test_lifetime_months():
    c = CohortCustomer('X', dt.date(2022, 1, 1), 80.0, 1200.0)
    months = c.lifetime_months(dt.date(2022, 7, 1))
    assert months == pytest.approx(6.0, abs=0.5)


def test_lifetime_revenue():
    c = CohortCustomer('X', dt.date(2022, 1, 1), 80.0, 1200.0)
    rev = c.lifetime_revenue_gbp(dt.date(2023, 1, 1))
    assert rev == pytest.approx(1200.0, rel=0.05)


def test_net_clv():
    c = CohortCustomer('X', dt.date(2022, 1, 1), 80.0, 1200.0)
    clv = c.net_clv_gbp(dt.date(2023, 1, 1))
    assert clv == pytest.approx(1200.0 - 80.0, rel=0.05)


def test_churn_reduces_active_count():
    coh = _make_cohort()
    coh.churn_customer('C002', dt.date(2022, 6, 1))
    assert coh.active_count() == 2


def test_retention_rate():
    coh = _make_cohort()
    coh.churn_customer('C001', dt.date(2022, 9, 1))
    assert coh.retention_rate_pct() == pytest.approx(200/3, rel=0.01)


def test_payback_months():
    coh = _make_cohort()
    pb = coh.payback_months(dt.date(2024, 1, 1))
    avg_cac = (80 + 75 + 90) / 3
    avg_monthly_rev = ((1200 + 1100 + 1300) / 3) / 12
    expected = avg_cac / avg_monthly_rev
    assert pb == pytest.approx(expected, abs=0.05)


def test_cohort_summary():
    coh = _make_cohort()
    s = coh.cohort_summary(dt.date(2023, 6, 1))
    assert s['initial_size'] == 3
    assert s['channel'] == 'price_comparison'
    assert 'payback_months' in s
