import datetime as dt
import pytest
from company.finance.period_reconciliation import (
    ReconciliationStatus, VarianceType, ReconciliationVariance,
    PeriodReconciliation, ReconciliationLedger
)


def _make_period(ledger: ReconciliationLedger) -> PeriodReconciliation:
    return ledger.open_period(
        'P2022Q1', dt.date(2022, 1, 1), dt.date(2022, 3, 31),
        billed_revenue_gbp=800_000.0, accrued_revenue_gbp=50_000.0,
        wholesale_cost_gbp=500_000.0, network_cost_gbp=100_000.0,
        policy_cost_gbp=80_000.0, operating_cost_gbp=40_000.0,
    )


def test_open_period():
    ledger = ReconciliationLedger()
    p = _make_period(ledger)
    assert p.status == ReconciliationStatus.OPEN


def test_total_revenue():
    ledger = ReconciliationLedger()
    p = _make_period(ledger)
    assert p.total_revenue_gbp == pytest.approx(850_000.0)


def test_total_cost():
    ledger = ReconciliationLedger()
    p = _make_period(ledger)
    assert p.total_cost_gbp == pytest.approx(720_000.0)


def test_gross_margin():
    ledger = ReconciliationLedger()
    p = _make_period(ledger)
    assert p.gross_margin_gbp == pytest.approx(130_000.0)


def test_add_variance():
    ledger = ReconciliationLedger()
    p = _make_period(ledger)
    p.add_variance('V001', VarianceType.SETTLEMENT_DIFFERENCE, -5_000.0,
                   'Elexon settlement correction')
    assert p.total_variance_gbp == pytest.approx(-5_000.0)
    assert p.adjusted_margin_gbp == pytest.approx(125_000.0)


def test_adverse_variance():
    v = ReconciliationVariance('V002', dt.date(2022, 1, 1),
                               VarianceType.COST_OVERRUN, -3_000.0, 'Network overrun')
    assert v.is_adverse
    assert v.abs_amount_gbp == pytest.approx(3_000.0)


def test_close_period():
    ledger = ReconciliationLedger()
    p = _make_period(ledger)
    p.close()
    assert p.status == ReconciliationStatus.RECONCILED
    assert len(ledger.open_periods()) == 0


def test_annual_gross_margin():
    ledger = ReconciliationLedger()
    p = _make_period(ledger)
    ledger.open_period(
        'P2022Q2', dt.date(2022, 4, 1), dt.date(2022, 6, 30),
        900_000.0, 60_000.0, 600_000.0, 110_000.0, 90_000.0, 45_000.0
    )
    total = ledger.annual_gross_margin_gbp(2022)
    # Q1: 130k, Q2: 115k
    assert total == pytest.approx(245_000.0)


def test_reconciliation_summary():
    ledger = ReconciliationLedger()
    p = _make_period(ledger)
    p.add_variance('V003', VarianceType.ACCRUAL_REVERSAL, 2_000.0, 'Accrual reversal')
    s = ledger.reconciliation_summary(2022)
    assert s['periods'] == 1
    assert s['open'] == 1
    assert 'accrual_reversal' in s['variances_by_type']
