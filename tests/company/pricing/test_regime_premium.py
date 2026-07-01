"""Tests for company.pricing.tariff_engine._compute_regime_premium — Phase 18a."""
import pytest
from datetime import date, timedelta

from company.pricing.tariff_engine import (
    REGIME_PREMIUM_MAX,
    REGIME_PREMIUM_MIN,
    REGIME_SHORT_WINDOW,
    REGIME_LONG_WINDOW,
    _compute_regime_premium,
)


def _price_records(start_date: str, end_date: str, price: float) -> list[dict]:
    """Generate flat-price records for testing."""
    records = []
    d = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    while d <= end:
        for sp in [1, 2, 3]:
            records.append({"settlementDate": d.isoformat(), "settlementPeriod": sp, "systemSellPrice": price})
        d += timedelta(days=1)
    return records


def _records_with_step(delivery: str, low_price: float, high_price: float) -> list[dict]:
    """Create records where price jumps from low to high at mid-point (simulates regime change).
    long window (180d before delivery) starts low; short window (60d before delivery) is high.
    """
    end = date.fromisoformat(delivery) - timedelta(days=1)
    short_start = end - timedelta(days=REGIME_SHORT_WINDOW - 1)
    long_start = end - timedelta(days=REGIME_LONG_WINDOW - 1)

    records = []
    d = long_start
    while d <= end:
        price = high_price if d >= short_start else low_price
        for sp in [1, 2]:
            records.append({"settlementDate": d.isoformat(), "settlementPeriod": sp, "systemSellPrice": price})
        d += timedelta(days=1)
    return records


def test_flat_prices_returns_zero():
    """Flat price history (no trend) → regime premium is zero."""
    delivery = "2021-04-01"
    records = _price_records("2020-10-01", "2021-03-31", price=100.0)
    result = _compute_regime_premium(delivery, records)
    assert result == pytest.approx(0.0)


def test_upward_regime_returns_positive_premium():
    """Short-term prices 30% above long-term → upward regime → positive premium."""
    delivery = "2022-01-01"
    # Short window at 130, long window average ~100 → ratio ~1.30 → above 1.10 threshold
    records = _records_with_step(delivery, low_price=80.0, high_price=130.0)
    result = _compute_regime_premium(delivery, records)
    assert result > 0.0, f"Expected positive premium, got {result}"


def test_downward_regime_returns_negative_premium():
    """Short-term prices 20% below long-term → downward regime → negative premium (discount)."""
    delivery = "2020-04-01"
    # Short window at 60, long window average ~100 → ratio ~0.70 → below 0.90 threshold
    records = _records_with_step(delivery, low_price=100.0, high_price=60.0)
    # Note: low=100 is the older (long) price, high=60 is the short-term price
    result = _compute_regime_premium(delivery, records)
    assert result < 0.0, f"Expected negative premium, got {result}"


def test_upward_regime_capped_at_max():
    """Extreme upward regime → premium capped at REGIME_PREMIUM_MAX."""
    delivery = "2022-01-01"
    # Short=500, long=50 → ratio=10 → well above any threshold
    records = _records_with_step(delivery, low_price=50.0, high_price=500.0)
    result = _compute_regime_premium(delivery, records)
    assert result == pytest.approx(REGIME_PREMIUM_MAX)


def test_downward_regime_capped_at_min():
    """Extreme downward regime → discount capped at REGIME_PREMIUM_MIN."""
    delivery = "2020-04-01"
    # Short=10, long=200 → ratio=0.05 → way below any threshold
    records = _records_with_step(delivery, low_price=200.0, high_price=10.0)
    result = _compute_regime_premium(delivery, records)
    assert result == pytest.approx(REGIME_PREMIUM_MIN)


def test_insufficient_records_returns_zero():
    """Too few records in short window → returns zero (no regime signal)."""
    delivery = "2021-04-01"
    # Only 5 days of data — not enough for REGIME_MIN_RECORDS
    records = _price_records("2021-03-26", "2021-03-31", price=200.0)
    result = _compute_regime_premium(delivery, records)
    assert result == 0.0


def test_premium_always_in_bounds():
    """Premium is always within [REGIME_PREMIUM_MIN, REGIME_PREMIUM_MAX]."""
    delivery = "2022-01-01"
    for low, high in [(50, 100), (100, 50), (100, 200), (200, 100), (100, 100)]:
        records = _records_with_step(delivery, low_price=low, high_price=high)
        p = _compute_regime_premium(delivery, records)
        assert REGIME_PREMIUM_MIN <= p <= REGIME_PREMIUM_MAX


def test_get_forward_price_regime_false_unchanged():
    """regime_detect=False gives same result as base tariff engine without regime."""
    from company.pricing.tariff_engine import CompanyTariffEngine
    records = _price_records("2020-10-01", "2021-03-31", price=100.0)
    engine = CompanyTariffEngine()
    with_regime = engine.get_forward_price("electricity", "2021-04-01", records,
                                            seasonal=False, adaptive_lookback=False, regime_detect=True)
    without_regime = engine.get_forward_price("electricity", "2021-04-01", records,
                                               seasonal=False, adaptive_lookback=False, regime_detect=False)
    # Flat prices → regime premium = 0 → same result
    assert with_regime == pytest.approx(without_regime)


# --- Phase KM depth tests ---

def test_max_premium_is_positive():
    assert REGIME_PREMIUM_MAX > 0.0


def test_min_premium_is_negative():
    assert REGIME_PREMIUM_MIN < 0.0


def test_short_window_positive():
    assert REGIME_SHORT_WINDOW > 0


def test_long_window_greater_than_short():
    assert REGIME_LONG_WINDOW > REGIME_SHORT_WINDOW


def test_result_is_float():
    delivery = '2021-04-01'
    records = _price_records('2020-10-01', '2021-03-31', price=100.0)
    result = _compute_regime_premium(delivery, records)
    assert isinstance(result, float)


def test_flat_prices_zero_different_date():
    delivery = '2020-07-01'
    records = _price_records('2020-01-01', '2020-06-30', price=50.0)
    result = _compute_regime_premium(delivery, records)
    assert result == pytest.approx(0.0)


def test_small_upward_trend_in_bounds():
    delivery = '2022-01-01'
    records = _records_with_step(delivery, low_price=100.0, high_price=115.0)
    result = _compute_regime_premium(delivery, records)
    assert REGIME_PREMIUM_MIN <= result <= REGIME_PREMIUM_MAX


def test_small_downward_trend_in_bounds():
    delivery = '2020-04-01'
    records = _records_with_step(delivery, low_price=100.0, high_price=85.0)
    result = _compute_regime_premium(delivery, records)
    assert REGIME_PREMIUM_MIN <= result <= REGIME_PREMIUM_MAX


def test_max_constant_is_float_or_int():
    assert isinstance(REGIME_PREMIUM_MAX, (float, int))


def test_min_constant_is_float_or_int():
    assert isinstance(REGIME_PREMIUM_MIN, (float, int))
