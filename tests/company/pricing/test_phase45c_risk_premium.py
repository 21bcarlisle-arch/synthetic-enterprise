"""Phase 45c: Forward curve risk premium recalibration.

COMPANY_RISK_PREMIUM_FRACTION: 15% → 8% (electricity)
GAS_RISK_PREMIUM_FRACTION: 20% → 10% (gas)

Rationale: UK I&C competitive market prices at 5-8% above NAP/NBP for electricity;
original 15%/20% created C_IC1/C_IC2 net margins of 33% (vs 3-8% benchmark).
"""
import pytest


def _records(start_year: int, price: float = 50.0, n_days: int = 120) -> list[dict]:
    from datetime import date, timedelta
    start = date(start_year, 1, 1)
    return [
        {"settlementDate": (start + timedelta(i)).isoformat(), "systemSellPrice": price}
        for i in range(n_days)
    ]


class TestRiskPremiumConstants:
    def test_electricity_premium_is_8_percent(self):
        from company.pricing.tariff_engine import COMPANY_RISK_PREMIUM_FRACTION
        assert COMPANY_RISK_PREMIUM_FRACTION == pytest.approx(0.08)

    def test_gas_premium_is_10_percent(self):
        from company.pricing.tariff_engine import GAS_RISK_PREMIUM_FRACTION
        assert GAS_RISK_PREMIUM_FRACTION == pytest.approx(0.10)

    def test_gas_still_higher_than_electricity(self):
        from company.pricing.tariff_engine import COMPANY_RISK_PREMIUM_FRACTION, GAS_RISK_PREMIUM_FRACTION
        assert GAS_RISK_PREMIUM_FRACTION > COMPANY_RISK_PREMIUM_FRACTION

    def test_premiums_reduced_from_prior_levels(self):
        """Both new values are below prior levels (15% elec, 20% gas)."""
        from company.pricing.tariff_engine import COMPANY_RISK_PREMIUM_FRACTION, GAS_RISK_PREMIUM_FRACTION
        assert COMPANY_RISK_PREMIUM_FRACTION < 0.15
        assert GAS_RISK_PREMIUM_FRACTION < 0.20


class TestForwardPriceWithNewPremiums:
    def setup_method(self):
        from company.pricing.tariff_engine import CompanyTariffEngine
        self.engine = CompanyTariffEngine()

    def test_elec_forward_uses_8pct_premium(self):
        from company.pricing.tariff_engine import COMPANY_RISK_PREMIUM_FRACTION
        records = _records(2017, price=50.0)
        fwd = self.engine.get_forward_price(
            "electricity", "2017-05-01", records, seasonal=False
        )
        assert fwd == pytest.approx(50.0 * (1 + COMPANY_RISK_PREMIUM_FRACTION))

    def test_gas_forward_uses_10pct_premium(self):
        from company.pricing.tariff_engine import GAS_RISK_PREMIUM_FRACTION
        records = _records(2017, price=40.0)
        fwd = self.engine.get_forward_price(
            "gas", "2017-05-01", records, seasonal=False
        )
        assert fwd == pytest.approx(40.0 * (1 + GAS_RISK_PREMIUM_FRACTION))

    def test_elec_forward_lower_than_old_15pct(self):
        records = _records(2017, price=100.0)
        fwd = self.engine.get_forward_price(
            "electricity", "2017-05-01", records, seasonal=False
        )
        assert fwd < 100.0 * 1.15   # below old 15% premium
        assert fwd > 100.0 * 1.05   # but still above spot (not zero premium)

    def test_gas_forward_lower_than_old_20pct(self):
        records = _records(2017, price=50.0)
        fwd = self.engine.get_forward_price(
            "gas", "2017-05-01", records, seasonal=False
        )
        assert fwd < 50.0 * 1.20   # below old 20% premium
        assert fwd > 50.0 * 1.05   # but still above spot
