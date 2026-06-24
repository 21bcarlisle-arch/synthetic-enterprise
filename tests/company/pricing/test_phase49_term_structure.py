"""Phase 49: EWMA base + dynamic term structure slope — unit tests."""
import pytest
from datetime import date, timedelta

from company.pricing.tariff_engine import (
    CompanyTariffEngine,
    TERM_SLOPE_CAP,
    TERM_SLOPE_FLOOR,
    EWMA_HALF_LIFE_DAYS,
    _compute_ewma,
    _estimate_term_structure_slope,
)


def _records(prices_by_date: dict) -> list[dict]:
    return [{"settlementDate": d, "systemSellPrice": p} for d, p in prices_by_date.items()]


def _flat_records(n: int, price: float, end_date: date) -> list[dict]:
    return [
        {"settlementDate": (end_date - timedelta(days=i)).isoformat(), "systemSellPrice": price}
        for i in range(n)
    ]


def _rising_records(n: int, start_price: float, end_price: float, end_date: date) -> list[dict]:
    """Records rising linearly from start_price to end_price over n days."""
    records = []
    for i in range(n):
        t = i / max(n - 1, 1)
        price = start_price + t * (end_price - start_price)
        d = (end_date - timedelta(days=n - 1 - i)).isoformat()
        records.append({"settlementDate": d, "systemSellPrice": price})
    return records


class TestComputeEwma:
    def test_flat_prices_return_same_value(self):
        means = [100.0] * 60
        assert _compute_ewma(means) == pytest.approx(100.0, rel=1e-6)

    def test_single_value(self):
        assert _compute_ewma([42.0]) == pytest.approx(42.0)

    def test_recent_spike_shifts_ewma(self):
        # Series of 100.0 followed by a sudden spike to 200.0; EWMA should
        # be above the mean of all 100.0 values, reflecting the spike.
        means = [100.0] * 59 + [200.0]
        ewma = _compute_ewma(means)
        assert ewma > 100.0  # spike pulls EWMA up from flat baseline

    def test_ewma_tracks_settled_level(self):
        # After many observations at 200.0, EWMA should converge toward 200.0
        means = [50.0] * 10 + [200.0] * 200
        ewma = _compute_ewma(means)
        # After 200 samples at 200 following early 50s, should be close to 200
        assert ewma > 190.0


class TestEstimateTermStructureSlope:
    def _delivery(self, days_ahead: int = 91) -> str:
        return (date(2020, 1, 1) + timedelta(days=days_ahead)).isoformat()

    def test_flat_market_slope_near_zero(self):
        end = date(2020, 1, 1) - timedelta(days=1)
        records = _flat_records(120, 100.0, end)
        slope = _estimate_term_structure_slope("2020-01-01", records)
        assert abs(slope) < 0.01  # near-zero for flat market

    def test_rising_market_positive_slope(self):
        end = date(2020, 1, 1) - timedelta(days=1)
        # Prices double over 120 days — strong contango signal
        records = _rising_records(120, 50.0, 150.0, end)
        slope = _estimate_term_structure_slope("2020-01-01", records)
        assert slope > 0.0

    def test_falling_market_negative_slope(self):
        end = date(2020, 1, 1) - timedelta(days=1)
        records = _rising_records(120, 150.0, 50.0, end)
        slope = _estimate_term_structure_slope("2020-01-01", records)
        assert slope < 0.0

    def test_slope_capped_at_max(self):
        end = date(2020, 1, 1) - timedelta(days=1)
        # Extreme price rise — slope should be capped at TERM_SLOPE_CAP
        records = _rising_records(120, 10.0, 1000.0, end)
        slope = _estimate_term_structure_slope("2020-01-01", records)
        assert slope <= TERM_SLOPE_CAP

    def test_slope_floored_at_min(self):
        end = date(2020, 1, 1) - timedelta(days=1)
        records = _rising_records(120, 1000.0, 10.0, end)
        slope = _estimate_term_structure_slope("2020-01-01", records)
        assert slope >= TERM_SLOPE_FLOOR

    def test_insufficient_records_returns_zero(self):
        end = date(2020, 1, 1) - timedelta(days=1)
        records = _flat_records(10, 100.0, end)  # too few
        slope = _estimate_term_structure_slope("2020-01-01", records)
        assert slope == 0.0


class TestGetForwardPricePhase49:
    def setup_method(self):
        self.engine = CompanyTariffEngine()
        self.anchor = date(2020, 1, 1)

    def test_flat_market_ewma_same_as_simple_mean(self):
        """Flat prices: EWMA == simple mean == 100.0."""
        end = self.anchor - timedelta(days=1)
        records = _flat_records(120, 100.0, end)
        price = self.engine.get_forward_price(
            "electricity", "2020-01-01", records,
            seasonal=False, adaptive_lookback=False, regime_detect=False,
            risk_premium=0.0, term_months=12,
        )
        assert price == pytest.approx(100.0, rel=1e-4)

    def test_rising_market_contango_adds_to_longer_tenor(self):
        """In rising market: 24m contract costs more than 12m beyond just structural premium."""
        end = self.anchor - timedelta(days=1)
        records = _rising_records(120, 60.0, 120.0, end)
        p12 = self.engine.get_forward_price(
            "electricity", "2020-01-01", records,
            seasonal=False, adaptive_lookback=False, regime_detect=False,
            risk_premium=0.0, term_months=12,
        )
        p24 = self.engine.get_forward_price(
            "electricity", "2020-01-01", records,
            seasonal=False, adaptive_lookback=False, regime_detect=False,
            risk_premium=0.0, term_months=24,
        )
        # p24 > p12 from both structural premium (2%) AND positive slope
        assert p24 > p12

    def test_falling_market_backwardation_reduces_longer_tenor_premium(self):
        """In falling market: the slope partially offsets the structural term premium."""
        end = self.anchor - timedelta(days=1)
        records_flat = _flat_records(120, 100.0, end)
        records_fall = _rising_records(120, 120.0, 60.0, end)

        p24_flat = self.engine.get_forward_price(
            "electricity", "2020-01-01", records_flat,
            seasonal=False, adaptive_lookback=False, regime_detect=False,
            risk_premium=0.0, term_months=24,
        )
        p24_fall = self.engine.get_forward_price(
            "electricity", "2020-01-01", records_fall,
            seasonal=False, adaptive_lookback=False, regime_detect=False,
            risk_premium=0.0, term_months=24,
        )
        # Falling market → negative slope → reduces 24m premium vs flat market
        assert p24_fall < p24_flat

    def test_gas_contango_also_increases_longer_tenor(self):
        end = self.anchor - timedelta(days=1)
        records = _rising_records(120, 30.0, 80.0, end)
        p12 = self.engine.get_forward_price(
            "gas", "2020-01-01", records,
            seasonal=False, adaptive_lookback=False, regime_detect=False,
            risk_premium=0.0, term_months=12,
        )
        p24 = self.engine.get_forward_price(
            "gas", "2020-01-01", records,
            seasonal=False, adaptive_lookback=False, regime_detect=False,
            risk_premium=0.0, term_months=24,
        )
        assert p24 > p12

    def test_phase48a_structural_premium_preserved_in_flat_market(self):
        """Phase 48a 2%/year structural premium still applies when slope is zero."""
        from company.pricing.tariff_engine import TERM_LENGTH_PREMIUM_PCT_PER_YEAR
        end = self.anchor - timedelta(days=1)
        records = _flat_records(120, 100.0, end)
        p12 = self.engine.get_forward_price(
            "electricity", "2020-01-01", records,
            seasonal=False, adaptive_lookback=False, regime_detect=False,
            risk_premium=0.0, term_months=12,
        )
        p24 = self.engine.get_forward_price(
            "electricity", "2020-01-01", records,
            seasonal=False, adaptive_lookback=False, regime_detect=False,
            risk_premium=0.0, term_months=24,
        )
        assert p24 - p12 == pytest.approx(100.0 * TERM_LENGTH_PREMIUM_PCT_PER_YEAR, rel=1e-4)
