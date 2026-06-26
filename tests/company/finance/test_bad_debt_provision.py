import datetime as dt
import pytest
from company.finance.bad_debt_provision import (
    AgingBucket, ArrearsLedgerItem, BadDebtProvision,
    classify_age, build_provision
)


def test_classify_age_boundaries():
    assert classify_age(0) == AgingBucket.CURRENT
    assert classify_age(30) == AgingBucket.CURRENT
    assert classify_age(31) == AgingBucket.DAYS_30
    assert classify_age(60) == AgingBucket.DAYS_30
    assert classify_age(61) == AgingBucket.DAYS_60
    assert classify_age(90) == AgingBucket.DAYS_60
    assert classify_age(91) == AgingBucket.DAYS_90
    assert classify_age(181) == AgingBucket.DAYS_180_PLUS


def test_item_provision_current():
    item = ArrearsLedgerItem('C001', 1000.0, 15)
    assert item.aging_bucket == AgingBucket.CURRENT
    assert item.provision_rate == pytest.approx(0.005)
    assert item.provision_gbp == pytest.approx(5.0)


def test_item_provision_180_plus():
    item = ArrearsLedgerItem('C002', 2000.0, 200)
    assert item.aging_bucket == AgingBucket.DAYS_180_PLUS
    assert item.provision_gbp == pytest.approx(1800.0)


def test_build_provision_totals():
    items = [
        ArrearsLedgerItem('C001', 500.0, 10),
        ArrearsLedgerItem('C002', 500.0, 45),
        ArrearsLedgerItem('C003', 1000.0, 200),
    ]
    p = build_provision(dt.date(2022, 12, 31), items)
    assert p.total_arrears_gbp == pytest.approx(2000.0)
    expected = 500 * 0.005 + 500 * 0.05 + 1000 * 0.90
    assert p.total_provision_gbp == pytest.approx(expected)


def test_provision_coverage_pct():
    items = [ArrearsLedgerItem('C001', 1000.0, 200)]
    p = build_provision(dt.date(2022, 12, 31), items)
    assert p.provision_coverage_pct == pytest.approx(90.0)


def test_by_bucket_groups():
    items = [
        ArrearsLedgerItem('C001', 100.0, 10),
        ArrearsLedgerItem('C002', 200.0, 10),
        ArrearsLedgerItem('C003', 500.0, 100),
    ]
    p = build_provision(dt.date(2022, 12, 31), items)
    buckets = p.by_bucket()
    assert buckets['current']['count'] == 2
    assert buckets['current']['arrears_gbp'] == pytest.approx(300.0)
    assert '91_180_days' in buckets


def test_vulnerable_provision():
    items = [
        ArrearsLedgerItem('C001', 1000.0, 200, is_vulnerable=True),
        ArrearsLedgerItem('C002', 1000.0, 200, is_vulnerable=False),
    ]
    p = build_provision(dt.date(2022, 12, 31), items)
    assert p.vulnerable_provision_gbp() == pytest.approx(900.0)


def test_summary_keys():
    items = [ArrearsLedgerItem('C001', 200.0, 50)]
    p = build_provision(dt.date(2022, 12, 31), items)
    s = p.summary()
    assert s['total_customers'] == 1
    assert 'provision_coverage_pct' in s
    assert 'by_bucket' in s
