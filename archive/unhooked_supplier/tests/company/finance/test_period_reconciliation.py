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


def test_get_period_found():
    ledger = ReconciliationLedger()
    _make_period(ledger)
    p = ledger.get('P2022Q1')
    assert p is not None
    assert p.period_id == 'P2022Q1'


def test_get_period_not_found():
    ledger = ReconciliationLedger()
    _make_period(ledger)
    assert ledger.get('UNKNOWN') is None


def test_positive_variance_not_adverse():
    v = ReconciliationVariance('V004', dt.date(2022, 1, 1),
                               VarianceType.REVENUE_SHORTFALL, 1_500.0, 'Credit note received')
    assert not v.is_adverse
    assert v.abs_amount_gbp == pytest.approx(1_500.0)


def test_multiple_variances_sum():
    ledger = ReconciliationLedger()
    p = _make_period(ledger)
    p.add_variance('V005', VarianceType.SETTLEMENT_DIFFERENCE, -4_000.0, 'Elexon R1')
    p.add_variance('V006', VarianceType.COST_OVERRUN, -1_000.0, 'Network TUoS correction')
    assert p.total_variance_gbp == pytest.approx(-5_000.0)
    assert p.adjusted_margin_gbp == pytest.approx(125_000.0)


def test_zero_variance_adjusted_margin_equals_gross():
    ledger = ReconciliationLedger()
    p = _make_period(ledger)
    assert p.total_variance_gbp == pytest.approx(0.0)
    assert p.adjusted_margin_gbp == pytest.approx(p.gross_margin_gbp)


def test_variances_by_type_multiple_types():
    ledger = ReconciliationLedger()
    p = _make_period(ledger)
    p.add_variance('V007', VarianceType.METER_READ_ERROR, -2_000.0, 'Meter error Q1')
    p.add_variance('V008', VarianceType.ACCRUAL_REVERSAL, 500.0, 'Accrual reversal Q1')
    by_type = ledger.variances_by_type(2022)
    assert by_type.get('meter_read_error') == pytest.approx(-2_000.0)
    assert by_type.get('accrual_reversal') == pytest.approx(500.0)


def test_open_periods_shows_only_open():
    ledger = ReconciliationLedger()
    p1 = _make_period(ledger)
    ledger.open_period(
        'P2022Q2', dt.date(2022, 4, 1), dt.date(2022, 6, 30),
        900_000.0, 60_000.0, 600_000.0, 110_000.0, 90_000.0, 45_000.0
    )
    p1.close()
    open_periods = ledger.open_periods()
    assert len(open_periods) == 1
    assert open_periods[0].period_id == 'P2022Q2'


def test_annual_gross_margin_year_filter():
    ledger = ReconciliationLedger()
    _make_period(ledger)
    ledger.open_period(
        'P2021Q4', dt.date(2021, 10, 1), dt.date(2021, 12, 31),
        700_000.0, 40_000.0, 450_000.0, 90_000.0, 70_000.0, 35_000.0,
    )
    assert ledger.annual_gross_margin_gbp(2022) == pytest.approx(130_000.0)
    assert ledger.annual_gross_margin_gbp(2021) == pytest.approx(95_000.0)


def test_reconciliation_summary_open_count_after_close():
    ledger = ReconciliationLedger()
    p = _make_period(ledger)
    p.close()
    s = ledger.reconciliation_summary(2022)
    assert s['periods'] == 1
    assert s['open'] == 0


def test_annual_gross_margin_includes_variance():
    ledger = ReconciliationLedger()
    p = _make_period(ledger)
    p.add_variance('V009', VarianceType.REVENUE_SHORTFALL, -10_000.0, 'Billing shortfall')
    assert ledger.annual_gross_margin_gbp(2022) == pytest.approx(120_000.0)
