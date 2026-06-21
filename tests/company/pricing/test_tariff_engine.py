"""Tests for company.pricing.tariff_engine — Phase 11a + Phase 13d + Phase 14c."""

from datetime import date, timedelta

import pytest

from company.pricing.tariff_engine import (
    ADAPTIVE_LOOKBACK_MAX,
    ADAPTIVE_LOOKBACK_MIN,
    ADAPTIVE_VOL_BASELINE_DAYS,
    ADAPTIVE_VOL_RECENT_DAYS,
    COMPANY_LOOKBACK_DAYS,
    COMPANY_RISK_PREMIUM_FRACTION,
    GAS_RISK_PREMIUM_FRACTION,
    GAS_SUMMER_SEASONAL_DISCOUNT,
    GAS_WINTER_SEASONAL_UPLIFT,
    SUMMER_SEASONAL_DISCOUNT,
    WINTER_MONTHS,
    WINTER_SEASONAL_UPLIFT,
    CompanyTariffEngine,
    _compute_adaptive_lookback,
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
        # Records before the lookback window should not affect result.
        # regime_detect=False: this test isolates the lookback-window logic, not regime detection.
        early = _price_records("2014-01-01", "2015-08-31", price=200.0)
        recent = _price_records("2015-09-01", "2016-01-15", price=100.0)
        records = early + recent
        fwd = self.engine.get_forward_price(
            "electricity", "2016-01-01", records, seasonal=False, regime_detect=False
        )
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
        """Phase 20a: gas defaults to GAS_RISK_PREMIUM_FRACTION (20%), not the electricity 15%."""
        records = _price_records("2015-09-01", "2016-01-15", price=45.0)
        fwd = self.engine.get_forward_price("gas", "2016-01-01", records, seasonal=False)
        assert fwd == pytest.approx(45.0 * (1 + GAS_RISK_PREMIUM_FRACTION))

    def test_gas_risk_premium_higher_than_electricity(self):
        """Phase 20a: same spot price → gas forward > electricity forward due to higher risk premium."""
        records = _price_records("2015-09-01", "2016-01-15", price=100.0)
        elec = self.engine.get_forward_price("electricity", "2016-01-01", records, seasonal=False)
        gas = self.engine.get_forward_price("gas", "2016-01-01", records, seasonal=False)
        assert gas > elec
        assert gas == pytest.approx(100.0 * (1 + GAS_RISK_PREMIUM_FRACTION))

    def test_explicit_risk_premium_overrides_fuel_default(self):
        """Passing risk_premium explicitly overrides the fuel-based default."""
        records = _price_records("2015-09-01", "2016-01-15", price=100.0)
        fwd = self.engine.get_forward_price("gas", "2016-01-01", records, risk_premium=0.10, seasonal=False)
        assert fwd == pytest.approx(100.0 * 1.10)

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
        """Gas winter uplift = base × (1 + GAS_WINTER_SEASONAL_UPLIFT) × (1 + GAS_RISK_PREMIUM_FRACTION)."""
        records = _price_records("2015-09-01", "2016-01-15", price=100.0)
        fwd = self.engine.get_forward_price("gas", "2016-01-15", records, seasonal=True)
        expected = 100.0 * (1.0 + GAS_WINTER_SEASONAL_UPLIFT) * (1.0 + GAS_RISK_PREMIUM_FRACTION)
        assert fwd == pytest.approx(expected)

    def test_gas_summer_discount_applied(self):
        """Gas gets summer discount in non-winter months (Phase 20a: uses GAS_RISK_PREMIUM_FRACTION)."""
        records = _price_records("2016-03-01", "2016-07-15", price=100.0)
        fwd = self.engine.get_forward_price("gas", "2016-07-15", records, seasonal=True)
        expected = 100.0 * (1.0 - GAS_SUMMER_SEASONAL_DISCOUNT) * (1.0 + GAS_RISK_PREMIUM_FRACTION)
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


# ── Adaptive lookback tests (Phase 14c) ─────────────────────────────────────

def _volatility_records(
    start: str, end: str,
    base_low: float = 48.0, base_high: float = 52.0,
    spike_start: str | None = None,
    spike_low: float = 50.0, spike_high: float = 200.0,
) -> list[dict]:
    """Build price records alternating between low/high in each period.

    The base period alternates between base_low and base_high (low std).
    If spike_start is given, from that date onward alternates between
    spike_low and spike_high (much higher std).
    """
    d = date.fromisoformat(start)
    sp = date.fromisoformat(spike_start) if spike_start else None
    e = date.fromisoformat(end)
    records = []
    toggle = 0
    while d <= e:
        if sp is None or d < sp:
            price = base_low if toggle % 2 == 0 else base_high
        else:
            price = spike_low if toggle % 2 == 0 else spike_high
        records.append({"settlementDate": d.isoformat(), "systemSellPrice": price})
        toggle += 1
        d += timedelta(days=1)
    return records


class TestAdaptiveLookback:
    def setup_method(self):
        self.engine = CompanyTariffEngine()

    def test_high_vol_regime_shortens_lookback(self):
        """When recent 30d is more volatile than prior 90d, adaptive lookback < base."""
        # Baseline: low std (±2 around 50); Recent (last 30d): high std (50 vs 200)
        delivery = "2022-01-01"
        records = _volatility_records(
            "2021-04-01", "2021-12-31",
            base_low=48.0, base_high=52.0,
            spike_start="2021-12-02", spike_low=50.0, spike_high=200.0,
        )
        adaptive = _compute_adaptive_lookback(delivery, records, COMPANY_LOOKBACK_DAYS)
        assert adaptive < COMPANY_LOOKBACK_DAYS

    def test_low_vol_regime_extends_lookback(self):
        """When recent 30d is calmer than prior 90d, adaptive lookback > base (up to max)."""
        # Baseline: high std (50 vs 200); Recent (last 30d): low std (98 vs 102)
        delivery = "2022-01-01"
        records = _volatility_records(
            "2021-04-01", "2021-12-31",
            base_low=50.0, base_high=200.0,
            spike_start="2021-12-02", spike_low=98.0, spike_high=102.0,
        )
        adaptive = _compute_adaptive_lookback(delivery, records, COMPANY_LOOKBACK_DAYS)
        assert adaptive > COMPANY_LOOKBACK_DAYS

    def test_adaptive_lookback_respects_min_floor(self):
        """Even in extreme high-vol regimes, lookback never goes below ADAPTIVE_LOOKBACK_MIN."""
        delivery = "2022-01-01"
        records = _volatility_records(
            "2021-04-01", "2021-12-31",
            base_low=49.0, base_high=51.0,
            spike_start="2021-12-02", spike_low=10.0, spike_high=2000.0,
        )
        adaptive = _compute_adaptive_lookback(delivery, records, COMPANY_LOOKBACK_DAYS)
        assert adaptive >= ADAPTIVE_LOOKBACK_MIN

    def test_adaptive_lookback_respects_max_ceiling(self):
        """In very low-vol regimes, lookback never exceeds ADAPTIVE_LOOKBACK_MAX."""
        delivery = "2022-01-01"
        records = _volatility_records(
            "2021-04-01", "2021-12-31",
            base_low=10.0, base_high=500.0,
            spike_start="2021-12-02", spike_low=99.0, spike_high=101.0,
        )
        adaptive = _compute_adaptive_lookback(delivery, records, COMPANY_LOOKBACK_DAYS)
        assert adaptive <= ADAPTIVE_LOOKBACK_MAX

    def test_adaptive_lookback_falls_back_on_flat_prices(self):
        """Flat prices → baseline std near zero → falls back to base lookback."""
        records = _price_records("2021-04-01", "2021-12-31", price=100.0)
        adaptive = _compute_adaptive_lookback("2022-01-01", records, COMPANY_LOOKBACK_DAYS)
        assert adaptive == COMPANY_LOOKBACK_DAYS

    def test_adaptive_lookback_falls_back_on_sparse_data(self):
        """Too few records for vol windows → falls back to base lookback."""
        records = _price_records("2021-11-15", "2021-12-31", price=100.0)
        adaptive = _compute_adaptive_lookback("2022-01-01", records, COMPANY_LOOKBACK_DAYS)
        assert adaptive == COMPANY_LOOKBACK_DAYS

    def test_get_forward_price_adaptive_false_matches_non_adaptive(self):
        """adaptive_lookback=False should give same result as explicit lookback_days."""
        records = _price_records("2021-04-01", "2021-12-31", price=100.0)
        engine = CompanyTariffEngine()
        result_no_adaptive = engine.get_forward_price(
            "electricity", "2022-01-01", records, seasonal=False, adaptive_lookback=False
        )
        result_explicit = engine.get_forward_price(
            "electricity", "2022-01-01", records,
            lookback_days=COMPANY_LOOKBACK_DAYS, seasonal=False, adaptive_lookback=False
        )
        assert result_no_adaptive == pytest.approx(result_explicit)
