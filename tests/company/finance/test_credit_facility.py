import datetime as dt
import pytest
from company.finance.credit_facility import (
    DrawdownReason, CreditFacility, FacilityDrawdown, CreditFacilityBook
)


def _book():
    book = CreditFacilityBook()
    book.register_facility(
        'RCF01', 'Barclays Corporate', 10_000_000.0,
        interest_rate_pct=5.5, commitment_fee_pct=0.5,
        maturity_date=dt.date(2025, 6, 30)
    )
    return book


def test_register_facility():
    book = _book()
    assert 'RCF01' in book._facilities
    f = book._facilities['RCF01']
    assert f.limit_gbp == pytest.approx(10_000_000.0)


def test_daily_commitment_fee():
    book = _book()
    f = book._facilities['RCF01']
    expected = 10_000_000 * 0.005 / 365
    assert f.daily_commitment_fee_gbp == pytest.approx(expected, rel=0.01)


def test_drawdown_and_balance():
    book = _book()
    book.drawdown('RCF01', 3_000_000.0, dt.date(2022, 10, 1),
                  DrawdownReason.WHOLESALE_SETTLEMENT)
    assert book.outstanding_balance('RCF01') == pytest.approx(3_000_000.0)


def test_drawdown_breach_limit_raises():
    book = _book()
    with pytest.raises(ValueError, match='breach'):
        book.drawdown('RCF01', 11_000_000.0, dt.date(2022, 10, 1),
                      DrawdownReason.EMERGENCY)


def test_repay_clears_balance():
    book = _book()
    dd = book.drawdown('RCF01', 3_000_000.0, dt.date(2022, 10, 1),
                       DrawdownReason.WORKING_CAPITAL)
    book.repay(dd.drawdown_id, dt.date(2022, 11, 1))
    assert book.outstanding_balance('RCF01') == pytest.approx(0.0)


def test_interest_accrued_30_days():
    book = _book()
    dd = book.drawdown('RCF01', 1_000_000.0, dt.date(2022, 10, 1),
                       DrawdownReason.WHOLESALE_SETTLEMENT)
    accrued = book.total_interest_accrued_gbp(dt.date(2022, 10, 31))
    expected = 1_000_000 * 0.055 / 365 * 30
    assert accrued == pytest.approx(expected, rel=0.01)


def test_utilisation_pct():
    book = _book()
    book.drawdown('RCF01', 5_000_000.0, dt.date(2022, 10, 1),
                  DrawdownReason.SEASONAL_CASHFLOW)
    assert book.utilisation_pct('RCF01') == pytest.approx(50.0)
