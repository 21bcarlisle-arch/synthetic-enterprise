"""Phase 145: Prepayment Meter (PPM) Management."""

import pytest
from datetime import datetime
from company.billing.prepayment import PPMAccount, PPMBook, _is_friendly_hours


def test_standard_account_defaults():
    acc = PPMAccount("C1", "M1")
    assert acc.balance_gbp == 0.0
    assert acc.debt_gbp == 0.0
    assert acc.emergency_credit_limit_gbp == 5.0
    assert acc.debt_recovery_rate == 0.50
    assert not acc.is_vulnerable
    assert not acc.in_emergency_credit


def test_vulnerable_account_higher_limits():
    acc = PPMAccount("C1", "M1", is_vulnerable=True)
    assert acc.emergency_credit_limit_gbp == 10.0
    assert acc.debt_recovery_rate == 0.25


def test_emergency_credit_used():
    acc = PPMAccount("C1", "M1", balance_gbp=-3.0)
    assert acc.in_emergency_credit
    assert abs(acc.emergency_credit_used_gbp - 3.0) < 0.01
    assert abs(acc.emergency_credit_remaining_gbp - 2.0) < 0.01


def test_friendly_hours_overnight():
    dt_night = datetime(2022, 1, 10, 22, 30)
    assert _is_friendly_hours(dt_night)


def test_friendly_hours_early_morning():
    dt_early = datetime(2022, 1, 10, 5, 45)
    assert _is_friendly_hours(dt_early)


def test_friendly_hours_weekend():
    dt_sat = datetime(2022, 1, 8, 14, 0)
    assert _is_friendly_hours(dt_sat)


def test_not_friendly_hours_weekday_noon():
    dt_noon = datetime(2022, 1, 10, 12, 0)
    assert not _is_friendly_hours(dt_noon)


def _book_with_account(**kwargs):
    book = PPMBook()
    acc = PPMAccount(**kwargs)
    book.register(acc)
    return book, acc


def test_top_up_no_debt():
    book, acc = _book_with_account(customer_id="C1", meter_id="M1", balance_gbp=0.0, debt_gbp=0.0)
    result = book.top_up("C1", 10.0, "2022-01-10")
    assert abs(result["credited_to_balance_gbp"] - 10.0) < 0.01
    assert result["debt_repaid_gbp"] == 0.0
    assert abs(acc.balance_gbp - 10.0) < 0.01


def test_top_up_with_debt_recovery():
    book, acc = _book_with_account(
        customer_id="C1", meter_id="M1", balance_gbp=0.0, debt_gbp=20.0
    )
    result = book.top_up("C1", 10.0, "2022-01-10")
    assert abs(result["debt_repaid_gbp"] - 5.0) < 0.01
    assert abs(result["credited_to_balance_gbp"] - 5.0) < 0.01
    assert abs(acc.debt_gbp - 15.0) < 0.01
    assert abs(acc.balance_gbp - 5.0) < 0.01


def test_top_up_clears_small_debt():
    book, acc = _book_with_account(
        customer_id="C1", meter_id="M1", balance_gbp=0.0, debt_gbp=2.0
    )
    book.top_up("C1", 10.0, "2022-01-10")
    assert abs(acc.debt_gbp - 0.0) < 0.01
    assert abs(acc.balance_gbp - 8.0) < 0.01


def test_vulnerable_top_up_lower_recovery_rate():
    book, acc = _book_with_account(
        customer_id="C1", meter_id="M1", balance_gbp=0.0, debt_gbp=20.0,
        is_vulnerable=True
    )
    result = book.top_up("C1", 10.0, "2022-01-10")
    assert abs(result["debt_repaid_gbp"] - 2.5) < 0.01
    assert abs(result["credited_to_balance_gbp"] - 7.5) < 0.01


def test_consume_normal():
    book, acc = _book_with_account(customer_id="C1", meter_id="M1", balance_gbp=20.0)
    result = book.consume_daily("C1", kwh=10.0, rate_gbp_per_kwh=0.30, sc_gbp_per_day=0.50, date="2022-01-10")
    expected_cost = 10.0 * 0.30 + 0.50
    assert abs(result["cost_gbp"] - expected_cost) < 0.01
    assert abs(acc.balance_gbp - (20.0 - expected_cost)) < 0.01
    assert not result["in_emergency_credit"]


def test_consume_triggers_emergency_credit():
    book, acc = _book_with_account(customer_id="C1", meter_id="M1", balance_gbp=0.50)
    book.consume_daily("C1", kwh=10.0, rate_gbp_per_kwh=0.30, sc_gbp_per_day=0.50, date="2022-01-10")
    assert acc.in_emergency_credit
    assert abs(acc.emergency_credit_used_gbp - 3.0) < 0.01


def test_self_disconnection_weekday():
    book, acc = _book_with_account(
        customer_id="C1", meter_id="M1", balance_gbp=-6.0
    )
    dt_noon = datetime(2022, 1, 10, 12, 0)
    assert book.is_self_disconnected("C1", dt_noon)


def test_not_self_disconnected_friendly_hours():
    book, acc = _book_with_account(
        customer_id="C1", meter_id="M1", balance_gbp=-6.0
    )
    dt_night = datetime(2022, 1, 10, 23, 0)
    assert not book.is_self_disconnected("C1", dt_night)


def test_not_self_disconnected_within_limit():
    book, acc = _book_with_account(
        customer_id="C1", meter_id="M1", balance_gbp=-3.0
    )
    dt_noon = datetime(2022, 1, 10, 12, 0)
    assert not book.is_self_disconnected("C1", dt_noon)


def test_portfolio_summary():
    book = PPMBook()
    book.register(PPMAccount("C1", "M1", balance_gbp=10.0, debt_gbp=0.0))
    book.register(PPMAccount("C2", "M2", balance_gbp=-3.0, debt_gbp=5.0))
    book.register(PPMAccount("C3", "M3", balance_gbp=-7.0, debt_gbp=0.0))
    dt_noon = datetime(2022, 1, 10, 12, 0)
    summary = book.portfolio_summary(dt_noon)
    assert summary["total_accounts"] == 3
    assert summary["self_disconnected"] == 1
    assert summary["in_emergency_credit"] == 2
    assert abs(summary["total_debt_gbp"] - 5.0) < 0.01
    assert summary["pct_self_disconnected"] == pytest.approx(33.3, abs=0.2)


def test_portfolio_summary_empty():
    book = PPMBook()
    summary = book.portfolio_summary()
    assert summary["total_accounts"] == 0
    assert summary["self_disconnected"] == 0


def test_2022_crisis_faster_exhaustion():
    """2022 unit rates ~3x higher -> emergency credit exhausted faster."""
    def days_to_exhaustion(rate_gbp_per_kwh):
        book = PPMBook()
        book.register(PPMAccount("C1", "M1", balance_gbp=0.0))
        for day in range(60):
            book.consume_daily("C1", kwh=8.0, rate_gbp_per_kwh=rate_gbp_per_kwh,
                               sc_gbp_per_day=0.50, date=f"2022-01-{day+1:02d}")
            acc = book.get("C1")
            if acc.emergency_credit_used_gbp >= acc.emergency_credit_limit_gbp:
                return day + 1
        return 60

    days_normal = days_to_exhaustion(0.15)
    days_crisis = days_to_exhaustion(0.45)
    assert days_crisis < days_normal
    assert days_crisis <= 2
