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

    def test_gas_premium_is_5_percent(self):
        """Phase 46a: gas further reduced 10%→5%. Pass-through gas now bills at spot,
        so gas premium only covers fixed-term risk. UK resi gas margins near-zero in
        stable markets (realistic for competitive gas market)."""
        from company.pricing.tariff_engine import GAS_RISK_PREMIUM_FRACTION
        assert GAS_RISK_PREMIUM_FRACTION == pytest.approx(0.05)

    def test_premiums_reduced_from_prior_levels(self):
        """Both values below prior levels (15% elec, 20% gas)."""
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

    def test_gas_forward_uses_5pct_premium(self):
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
        assert fwd > 50.0 * 1.00   # above raw spot (has some premium)


# --- Phase KI depth tests ---

class TestRiskPremiumDepth:
    def setup_method(self):
        from company.pricing.tariff_engine import (
            CompanyTariffEngine, COMPANY_RISK_PREMIUM_FRACTION, GAS_RISK_PREMIUM_FRACTION
        )
        self.engine = CompanyTariffEngine()
        self.elec_prem = COMPANY_RISK_PREMIUM_FRACTION
        self.gas_prem = GAS_RISK_PREMIUM_FRACTION

    def test_elec_premium_greater_than_gas_premium(self):
        assert self.elec_prem > self.gas_prem

    def test_elec_premium_is_float(self):
        assert isinstance(self.elec_prem, float)

    def test_gas_premium_is_float(self):
        assert isinstance(self.gas_prem, float)

    def test_elec_forward_above_spot(self):
        records = _records(2017, price=80.0)
        fwd = self.engine.get_forward_price(
            'electricity', '2017-05-01', records, seasonal=False)
        assert fwd > 80.0

    def test_gas_forward_above_spot(self):
        records = _records(2017, price=40.0)
        fwd = self.engine.get_forward_price(
            'gas', '2017-05-01', records, seasonal=False)
        assert fwd > 40.0

    def test_elec_price_scales_with_base(self):
        r50 = _records(2017, price=50.0)
        r100 = _records(2017, price=100.0)
        p50 = self.engine.get_forward_price(
            'electricity', '2017-05-01', r50, seasonal=False)
        p100 = self.engine.get_forward_price(
            'electricity', '2017-05-01', r100, seasonal=False)
        assert p100 == pytest.approx(p50 * 2.0, rel=1e-6)

    def test_gas_price_scales_with_base(self):
        r40 = _records(2017, price=40.0)
        r80 = _records(2017, price=80.0)
        p40 = self.engine.get_forward_price(
            'gas', '2017-05-01', r40, seasonal=False)
        p80 = self.engine.get_forward_price(
            'gas', '2017-05-01', r80, seasonal=False)
        assert p80 == pytest.approx(p40 * 2.0, rel=1e-6)

    def test_elec_forward_exact_value(self):
        records = _records(2017, price=100.0)
        fwd = self.engine.get_forward_price(
            'electricity', '2017-05-01', records, seasonal=False)
        assert fwd == pytest.approx(100.0 * (1 + self.elec_prem), rel=1e-6)

    def test_two_engines_agree(self):
        from company.pricing.tariff_engine import CompanyTariffEngine
        engine2 = CompanyTariffEngine()
        records = _records(2017, price=60.0)
        p1 = self.engine.get_forward_price(
            'electricity', '2017-05-01', records, seasonal=False)
        p2 = engine2.get_forward_price(
            'electricity', '2017-05-01', records, seasonal=False)
        assert p1 == pytest.approx(p2)

    def test_elec_premium_positive(self):
        assert self.elec_prem > 0.0

    def test_gas_premium_positive(self):
        assert self.gas_prem > 0.0
