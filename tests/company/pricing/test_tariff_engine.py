"""Tests for company.pricing.tariff_engine — Phase 11a."""

from datetime import date, timedelta

import pytest

from company.pricing.tariff_engine import (
    COMPANY_LOOKBACK_DAYS,
    COMPANY_RISK_PREMIUM_FRACTION,
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
        fwd = self.engine.get_forward_price("electricity", "2016-01-01", records)
        assert fwd == pytest.approx(100.0 * (1 + COMPANY_RISK_PREMIUM_FRACTION))

    def test_uses_lookback_window_only(self):
        # Records before the lookback window should not affect result
        early = _price_records("2014-01-01", "2015-08-31", price=200.0)
        recent = _price_records("2015-09-01", "2016-01-15", price=100.0)
        records = early + recent
        fwd = self.engine.get_forward_price("electricity", "2016-01-01", records)
        # Should only use records in the 120-day window before 2016-01-01
        # window: 2015-09-03 to 2015-12-31, which are all 100.0
        assert fwd == pytest.approx(100.0 * (1 + COMPANY_RISK_PREMIUM_FRACTION))

    def test_excludes_delivery_date_itself(self):
        records = _price_records("2015-09-01", "2016-01-01", price=50.0)
        # 2016-01-01 is the delivery date — only prior records should be used
        fwd = self.engine.get_forward_price("electricity", "2016-01-01", records)
        assert fwd == pytest.approx(50.0 * (1 + COMPANY_RISK_PREMIUM_FRACTION))

    def test_raises_on_insufficient_data(self):
        records = _price_records("2015-12-25", "2015-12-31", price=80.0)
        # Only 7 records, less than MIN_RECORDS_FOR_ESTIMATE (30)
        with pytest.raises(ValueError, match="Insufficient"):
            self.engine.get_forward_price("electricity", "2016-01-01", records)

    def test_works_for_gas_fuel(self):
        records = _price_records("2015-09-01", "2016-01-15", price=45.0)
        fwd = self.engine.get_forward_price("gas", "2016-01-01", records)
        assert fwd == pytest.approx(45.0 * (1 + COMPANY_RISK_PREMIUM_FRACTION))

    def test_custom_risk_premium(self):
        records = _price_records("2015-09-01", "2016-01-15", price=100.0)
        fwd = self.engine.get_forward_price("electricity", "2016-01-01", records, risk_premium=0.20)
        assert fwd == pytest.approx(100.0 * 1.20)

    def test_differs_from_sim_forward_curve(self):
        """Company estimate uses longer lookback and no seasonal adjustment —
        it should differ from the SIM's generate_forward_price() output."""
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
        fwd = self.engine.get_forward_price("electricity", "2015-12-01", records)
        expected_mean = 100.0
        assert fwd == pytest.approx(expected_mean * (1 + COMPANY_RISK_PREMIUM_FRACTION), rel=1e-6)
