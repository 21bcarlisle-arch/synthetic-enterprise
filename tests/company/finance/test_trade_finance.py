import datetime as dt
import pytest
from company.finance.trade_finance import (
    InstrumentType, InstrumentStatus, CreditInstrument, TradeFinanceLedger
)


def test_register_and_active():
    ledger = TradeFinanceLedger()
    inst = ledger.register(
        'LC001', 'IC_001', InstrumentType.LETTER_OF_CREDIT, 'HSBC',
        500_000.0, dt.date(2022, 1, 1), dt.date(2022, 12, 31)
    )
    assert inst.status == InstrumentStatus.ACTIVE
    assert inst.face_value_gbp == 500_000.0


def test_days_to_expiry():
    ledger = TradeFinanceLedger()
    inst = ledger.register(
        'LC002', 'IC_001', InstrumentType.BANK_GUARANTEE, 'Barclays',
        200_000.0, dt.date(2022, 1, 1), dt.date(2022, 12, 31)
    )
    assert inst.days_to_expiry(dt.date(2022, 12, 1)) == 30


def test_expiring_soon_status():
    ledger = TradeFinanceLedger()
    inst = ledger.register(
        'LC003', 'IC_001', InstrumentType.SURETY_BOND, 'Aviva',
        100_000.0, dt.date(2022, 1, 1), dt.date(2022, 6, 20)
    )
    inst.refresh_status(dt.date(2022, 6, 1))
    assert inst.status == InstrumentStatus.EXPIRING_SOON


def test_expired_status():
    ledger = TradeFinanceLedger()
    inst = ledger.register(
        'LC004', 'IC_001', InstrumentType.LETTER_OF_CREDIT, 'Lloyds',
        150_000.0, dt.date(2021, 1, 1), dt.date(2021, 12, 31)
    )
    inst.refresh_status(dt.date(2022, 1, 15))
    assert inst.status == InstrumentStatus.EXPIRED


def test_call_instrument():
    ledger = TradeFinanceLedger()
    ledger.register(
        'LC005', 'IC_001', InstrumentType.PARENT_GUARANTEE, 'Group Ltd',
        300_000.0, dt.date(2022, 1, 1), dt.date(2022, 12, 31)
    )
    ledger.call_instrument('LC005', dt.date(2022, 9, 1), 180_000.0)
    inst = ledger.get('LC005')
    assert inst.status == InstrumentStatus.CALLED
    assert inst.call_amount_gbp == 180_000.0


def test_total_credit_support_excludes_expired():
    ledger = TradeFinanceLedger()
    ledger.register(
        'LC006', 'IC_002', InstrumentType.LETTER_OF_CREDIT, 'HSBC',
        100_000.0, dt.date(2022, 1, 1), dt.date(2022, 12, 31)
    )
    ledger.register(
        'LC007', 'IC_002', InstrumentType.LETTER_OF_CREDIT, 'HSBC',
        200_000.0, dt.date(2020, 1, 1), dt.date(2020, 12, 31)
    )
    total = ledger.total_credit_support_gbp('IC_002', dt.date(2022, 6, 1))
    assert total == pytest.approx(100_000.0)


def test_expiring_within():
    ledger = TradeFinanceLedger()
    ledger.register(
        'LC008', 'IC_003', InstrumentType.BANK_GUARANTEE, 'NatWest',
        50_000.0, dt.date(2022, 1, 1), dt.date(2022, 6, 25)
    )
    result = ledger.expiring_within(dt.date(2022, 6, 1), 30)
    assert len(result) == 1


def test_portfolio_summary():
    ledger = TradeFinanceLedger()
    ledger.register(
        'LC009', 'IC_004', InstrumentType.CASH_DEPOSIT, 'Internal',
        75_000.0, dt.date(2022, 1, 1), dt.date(2022, 12, 31)
    )
    s = ledger.portfolio_summary(dt.date(2022, 6, 1))
    assert s['active_count'] == 1
    assert s['total_coverage_gbp'] == pytest.approx(75_000.0)
    assert 'cash_deposit' in s['by_type']
