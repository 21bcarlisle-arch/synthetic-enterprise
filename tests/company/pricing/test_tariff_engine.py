"""Tests for company.pricing.tariff_engine — Phase 11a + Phase 13d."""

from datetime import date, timedelta

import pytest

from company.pricing.tariff_engine import (
    COMPANY_LOOKBACK_DAYS,
    COMPANY_RISK_PREMIUM_FRACTION,
    GAS_SUMMER_SEASONAL_DISCOUNT,
    GAS_WINTER_SEASONAL_UPLIFT,
    SUMMER_SEASONAL_DISCOUNT,
    WINTER_MONTHS,
    WINTER_SEASONAL_UPLIFT,
    CompanyTariffEngine,
)


def _price_records(start: str, end: str, price: float = 60.0) -> list[dict]:
    d = date.fromisoformat(start)
    e = date.fromisoformat(end)
    records = []
    while d <= e:
        records.append({"settlementDate": d.isoformat(), "systemSellPrice": price})
        d += timedelta(days=1)
    return records


class TestCompanyTariffEngine:
    def setup_method(self):
        self.engine = CompanyTariffEngine()

    def test_flat_price_returns_mean_plus_premium(self):
        records = _price_records("2015-09-01", "2016-01-15", price=100.0)
        fwd = self.engine.get_forward_price("electricity", "2016-01-01", records, seasonal=False)
        assert fwd == pytest.approx(100.0 * (1 + COMPANY_RISK_PREMIUM_FRACTION))

    def test_uses_lookback_window_only(self):
        # Records before the lookback window should not affect result
        early = _price_records("2014-01-01", "2015-08-31", price=200.0)
        recent = _price_records("2015-09-01", "2016-01-15", price=100.0)
        records = early + recent
        fwd = self.engine.get_forward_price("electricity", "2016-01-01", records, seasonal=False)
        # Should only use records in the 120-day window before 2016-01-01
        # window: 2015-09-03 to 2015-12-31, which are all 100.0
        assert fwd == pytest.approx(100.0 * (1 + COMPANY_RISK_PREMIUM_FRACTION))

    def test_excludes_delivery_date_itself(self):
        records = _price_records("2015-09-01", "2016-01-01", price=50.0)
        # 2016-01-01 is the delivery date — only prior records should be used
        fwd = self.engine.get_forward_price("electricity", "2016-01-01", records, seasonal=False)
        assert fwd == pytest.approx(50.0 * (1 + COMPANY_RISK_PREMIUM_FRACTION))

    def test_raises_on_insufficient_data(self):
        records = _price_records("2015-12-25", "2015-12-31", price=80.0)
        # Only 7 records, less than MIN_RECORDS_FOR_ESTIMATE (30)
        with pytest.raises(ValueError, match="Insufficient"):
            self.engine.get_forward_price("electricity", "2016-01-01", records)

    def test_works_for_gas_fuel(self):
        records = _price_records("2015-09-01", "2016-01-15", price=45.0)
        fwd = self.engine.get_forward_price("gas", "2016-01-01", records, seasonal=False)
        assert fwd == pytest.approx(45.0 * (1 + COMPANY_RISK_PREMIUM_FRACTION))

    def test_custom_risk_premium(self):
        records = _price_records("2015-09-01", "2016-01-15", price=100.0)
        fwd = self.engine.get_forward_price("electricity", "2016-01-01", records, risk_premium=0.20, seasonal=False)
        assert fwd == pytest.approx(100.0 * 1.20)

    def test_differs_from_sim_forward_curve(self):
        """Company estimate differs from SIM forward_curve (different algo + seasonal)."""
        from sim.forward_curve import generate_forward_price

        records = _price_records("2015-09-01", "2016-01-15", price=80.0)
        company_fwd = self.engine.get_forward_price("electricity", "2016-01-01", records)
        sim_fwd = generate_forward_price("2016-01-01", records)
        # Both should be positive but they should differ (sim adds seasonal + vol premium)
        assert company_fwd > 0
        assert sim_fwd > 0
        assert company_fwd != sim_fwd

    def test_varying_prices_uses_mean(self):
        records = []
        prices = [50.0, 100.0, 150.0]
        base = date(2015, 9, 1)
        for i in range(90):
            records.append({
                "settlementDate": (base + timedelta(days=i)).isoformat(),
                "systemSellPrice": prices[i % 3],
            })
        fwd = self.engine.get_forward_price("electricity", "2015-12-01", records, seasonal=False)
        expected_mean = 100.0
        assert fwd == pytest.approx(expected_mean * (1 + COMPANY_RISK_PREMIUM_FRACTION), rel=1e-6)


# ── Seasonal adjustment tests (Phase 13d) ────────────────────────────────────

class TestSeasonalAdjustment:
    def setup_method(self):
        self.engine = CompanyTariffEngine()
        self.records = _price_records("2015-09-01", "2016-01-15", price=100.0)

    def test_winter_delivery_adds_uplift(self):
        """January delivery (winter) should be priced above the seasonal=False baseline."""
        no_seasonal = self.engine.get_forward_price("electricity", "2016-01-15", self.records, seasonal=False)
        with_seasonal = self.engine.get_forward_price("electricity", "2016-01-15", self.records, seasonal=True)
        assert with_seasonal > no_seasonal

    def test_winter_uplift_quantified(self):
        """Winter uplift = base × (1 + WINTER_SEASONAL_UPLIFT) × (1 + risk_premium)."""
        fwd = self.engine.get_forward_price("electricity", "2016-01-15", self.records, seasonal=True)
        expected = 100.0 * (1.0 + WINTER_SEASONAL_UPLIFT) * (1.0 + COMPANY_RISK_PREMIUM_FRACTION)
        assert fwd == pytest.approx(expected)

    def test_summer_delivery_applies_discount(self):
        """July delivery (summer) should be priced below the seasonal=False baseline."""
        records = _price_records("2016-03-01", "2016-07-15", price=100.0)
        no_seasonal = self.engine.get_forward_price("electricity", "2016-07-15", records, seasonal=False)
        with_seasonal = self.engine.get_forward_price("electricity", "2016-07-15", records, seasonal=True)
        assert with_seasonal < no_seasonal

    def test_summer_discount_quantified(self):
        """Summer discount = base × (1 - SUMMER_SEASONAL_DISCOUNT) × (1 + risk_premium)."""
        records = _price_records("2016-03-01", "2016-07-15", price=100.0)
        fwd = self.engine.get_forward_price("electricity", "2016-07-15", records, seasonal=True)
        expected = 100.0 * (1.0 - SUMMER_SEASONAL_DISCOUNT) * (1.0 + COMPANY_RISK_PREMIUM_FRACTION)
        assert fwd == pytest.approx(expected)

    def test_all_winter_months_get_uplift(self):
        """Every month in WINTER_MONTHS (Oct-Mar) should produce a price above no-seasonal."""
        # 2 years of records ensures any 120-day lookback from 2016 has data
        base_records = _price_records("2014-01-01", "2016-12-31", price=100.0)
        for month in WINTER_MONTHS:
            delivery = f"2016-{month:02d}-15"
            no_s = self.engine.get_forward_price("electricity", delivery, base_records, seasonal=False)
            with_s = self.engine.get_forward_price("electricity", delivery, base_records, seasonal=True)
            assert with_s > no_s, f"Month {month} should get winter uplift"

    def test_summer_months_get_discount(self):
        """Every month NOT in WINTER_MONTHS should produce a price below no-seasonal."""
        base_records = _price_records("2014-01-01", "2016-12-31", price=100.0)
        summer_months = {4, 5, 6, 7, 8, 9}
        for month in summer_months:
            delivery = f"2016-{month:02d}-15"
            no_s = self.engine.get_forward_price("electricity", delivery, base_records, seasonal=False)
            with_s = self.engine.get_forward_price("electricity", delivery, base_records, seasonal=True)
            assert with_s < no_s, f"Month {month} should get summer discount"

    def test_gas_seasonal_applies_winter_uplift(self):
        """Gas gets its own seasonal uplift in winter (Phase 13e)."""
        records = _price_records("2015-09-01", "2016-01-15", price=100.0)
        gas_seasonal = self.engine.get_forward_price("gas", "2016-01-15", records, seasonal=True)
        gas_no_seasonal = self.engine.get_forward_price("gas", "2016-01-15", records, seasonal=False)
        assert gas_seasonal > gas_no_seasonal

    def test_gas_winter_uplift_quantified(self):
        """Gas winter uplift = base × (1 + GAS_WINTER_SEASONAL_UPLIFT) × (1 + risk_premium)."""
        records = _price_records("2015-09-01", "2016-01-15", price=100.0)
        fwd = self.engine.get_forward_price("gas", "2016-01-15", records, seasonal=True)
        expected = 100.0 * (1.0 + GAS_WINTER_SEASONAL_UPLIFT) * (1.0 + COMPANY_RISK_PREMIUM_FRACTION)
        assert fwd == pytest.approx(expected)

    def test_gas_summer_discount_applied(self):
        """Gas gets summer discount in non-winter months."""
        records = _price_records("2016-03-01", "2016-07-15", price=100.0)
        fwd = self.engine.get_forward_price("gas", "2016-07-15", records, seasonal=True)
        expected = 100.0 * (1.0 - GAS_SUMMER_SEASONAL_DISCOUNT) * (1.0 + COMPANY_RISK_PREMIUM_FRACTION)
        assert fwd == pytest.approx(expected)

    def test_seasonal_false_matches_original_formula(self):
        """seasonal=False should reproduce the original rolling-mean + premium formula exactly."""
        records = _price_records("2015-09-01", "2016-01-15", price=80.0)
        fwd = self.engine.get_forward_price("electricity", "2016-01-01", records, seasonal=False)
        assert fwd == pytest.approx(80.0 * (1 + COMPANY_RISK_PREMIUM_FRACTION))

    def test_winter_summer_price_spread(self):
        """At identical spot prices, winter contract should be priced above summer."""
        records = _price_records("2014-01-01", "2016-12-31", price=100.0)
        winter_price = self.engine.get_forward_price("electricity", "2016-02-01", records, seasonal=True)
        summer_price = self.engine.get_forward_price("electricity", "2016-07-01", records, seasonal=True)
        assert winter_price > summer_price
