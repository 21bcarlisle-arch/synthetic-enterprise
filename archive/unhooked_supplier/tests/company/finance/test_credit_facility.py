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


# --- Phase KB depth tests ---

def test_drawdown_id_format():
    book = _book()
    dd = book.drawdown('RCF01', 1_000_000.0, dt.date(2022, 1, 1),
                       DrawdownReason.WHOLESALE_SETTLEMENT)
    assert dd.drawdown_id == 'DD-0001'


def test_drawdown_id_sequential():
    book = _book()
    dd1 = book.drawdown('RCF01', 1_000_000.0, dt.date(2022, 1, 1),
                        DrawdownReason.WORKING_CAPITAL)
    dd2 = book.drawdown('RCF01', 1_000_000.0, dt.date(2022, 2, 1),
                        DrawdownReason.WORKING_CAPITAL)
    assert dd1.drawdown_id == 'DD-0001'
    assert dd2.drawdown_id == 'DD-0002'


def test_is_outstanding_true_before_repay():
    book = _book()
    dd = book.drawdown('RCF01', 500_000.0, dt.date(2022, 1, 1),
                       DrawdownReason.EMERGENCY)
    assert dd.is_outstanding is True


def test_is_outstanding_false_after_repay():
    book = _book()
    dd = book.drawdown('RCF01', 500_000.0, dt.date(2022, 1, 1),
                       DrawdownReason.EMERGENCY)
    book.repay(dd.drawdown_id, dt.date(2022, 2, 1))
    assert dd.is_outstanding is False


def test_repay_unknown_raises_key_error():
    book = _book()
    with pytest.raises(KeyError):
        book.repay('DD-9999', dt.date(2022, 2, 1))


def test_interest_stops_accruing_at_repay_date():
    book = _book()
    dd = book.drawdown('RCF01', 1_000_000.0, dt.date(2022, 1, 1),
                       DrawdownReason.WORKING_CAPITAL)
    book.repay(dd.drawdown_id, dt.date(2022, 1, 31))
    accrued_at_repay = book.total_interest_accrued_gbp(dt.date(2022, 1, 31))
    accrued_later = book.total_interest_accrued_gbp(dt.date(2022, 3, 2))
    assert accrued_at_repay == pytest.approx(accrued_later)


def test_bsc_credit_cover_reason_stored():
    book = _book()
    dd = book.drawdown('RCF01', 500_000.0, dt.date(2022, 1, 1),
                       DrawdownReason.BSC_CREDIT_COVER)
    assert dd.reason == DrawdownReason.BSC_CREDIT_COVER


def test_two_drawdowns_accumulate():
    book = _book()
    book.drawdown('RCF01', 2_000_000.0, dt.date(2022, 1, 1),
                  DrawdownReason.WORKING_CAPITAL)
    book.drawdown('RCF01', 3_000_000.0, dt.date(2022, 2, 1),
                  DrawdownReason.SEASONAL_CASHFLOW)
    assert book.outstanding_balance('RCF01') == pytest.approx(5_000_000.0)


def test_utilisation_zero_no_drawdowns():
    book = _book()
    assert book.utilisation_pct('RCF01') == pytest.approx(0.0)


def test_repay_sets_repaid_amount():
    book = _book()
    dd = book.drawdown('RCF01', 1_000_000.0, dt.date(2022, 1, 1),
                       DrawdownReason.WHOLESALE_SETTLEMENT)
    book.repay(dd.drawdown_id, dt.date(2022, 2, 1), repaid_amount_gbp=1_000_000.0)
    assert dd.repaid_amount_gbp == pytest.approx(1_000_000.0)
