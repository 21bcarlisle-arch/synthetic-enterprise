"""Phase 48a: Forward curve term-length premium — unit tests."""
import pytest
from company.pricing.tariff_engine import CompanyTariffEngine, TERM_LENGTH_PREMIUM_PCT_PER_YEAR


def _make_records(n=60, base_price=100.0, start_year=2015):
    """Build n days of flat price records before 2016-01-01."""
    from datetime import date, timedelta
    anchor = date(start_year, 12, 31)
    records = []
    for i in range(n):
        d = anchor - timedelta(days=i)
        records.append({"settlementDate": d.isoformat(), "systemSellPrice": base_price})
    return records


class TestTermPremiumConstant:
    def test_constant_is_two_percent(self):
        assert TERM_LENGTH_PREMIUM_PCT_PER_YEAR == pytest.approx(0.02)


class TestGetForwardPriceTermMonths:
    def setup_method(self):
        self.engine = CompanyTariffEngine()
        self.records = _make_records(n=60, base_price=100.0)

    def test_12_month_default_matches_no_term_arg(self):
        # Default term_months=12 → zero premium → same price as omitting the param
        p_default = self.engine.get_forward_price(
            "electricity", "2016-01-01", self.records, seasonal=False, adaptive_lookback=False, regime_detect=False,
        )
        p_explicit = self.engine.get_forward_price(
            "electricity", "2016-01-01", self.records, seasonal=False, adaptive_lookback=False, regime_detect=False,
            term_months=12,
        )
        assert p_default == pytest.approx(p_explicit)

    def test_24_month_is_two_pct_of_base_above_12_month(self):
        # formula: price = base × (1 + risk_prem + term_prem)
        # so p24 - p12 = base × term_prem (additive, not multiplicative on p12)
        p12 = self.engine.get_forward_price(
            "electricity", "2016-01-01", self.records, seasonal=False, adaptive_lookback=False, regime_detect=False,
            term_months=12,
        )
        p24 = self.engine.get_forward_price(
            "electricity", "2016-01-01", self.records, seasonal=False, adaptive_lookback=False, regime_detect=False,
            term_months=24,
        )
        # base=100, term_prem=0.02 → p24 - p12 = 2.0
        assert p24 - p12 == pytest.approx(100.0 * TERM_LENGTH_PREMIUM_PCT_PER_YEAR, rel=1e-6)
        assert p24 > p12

    def test_36_month_is_four_pct_of_base_above_12_month(self):
        p12 = self.engine.get_forward_price(
            "electricity", "2016-01-01", self.records, seasonal=False, adaptive_lookback=False, regime_detect=False,
            term_months=12,
        )
        p36 = self.engine.get_forward_price(
            "electricity", "2016-01-01", self.records, seasonal=False, adaptive_lookback=False, regime_detect=False,
            term_months=36,
        )
        # 2 extra years → 2 × term_prem on the base
        assert p36 - p12 == pytest.approx(100.0 * 2 * TERM_LENGTH_PREMIUM_PCT_PER_YEAR, rel=1e-6)

    def test_6_month_term_no_premium(self):
        # Sub-12-month terms get no premium (max(0, ...) floor)
        p12 = self.engine.get_forward_price(
            "electricity", "2016-01-01", self.records, seasonal=False, adaptive_lookback=False, regime_detect=False,
            term_months=12,
        )
        p6 = self.engine.get_forward_price(
            "electricity", "2016-01-01", self.records, seasonal=False, adaptive_lookback=False, regime_detect=False,
            term_months=6,
        )
        assert p6 == pytest.approx(p12)

    def test_gas_24_month_also_gets_term_premium(self):
        gas_records = _make_records(n=60, base_price=50.0)
        p12 = self.engine.get_forward_price(
            "gas", "2016-01-01", gas_records, seasonal=False, adaptive_lookback=False, regime_detect=False,
            term_months=12,
        )
        p24 = self.engine.get_forward_price(
            "gas", "2016-01-01", gas_records, seasonal=False, adaptive_lookback=False, regime_detect=False,
            term_months=24,
        )
        # base=50, term_prem=0.02 → p24 - p12 = 1.0
        assert p24 - p12 == pytest.approx(50.0 * TERM_LENGTH_PREMIUM_PCT_PER_YEAR, rel=1e-6)
        assert p24 > p12

    def test_term_premium_is_additive_to_risk_premium(self):
        # Verify: price = base × (1 + risk_prem + term_prem), not multiplicative
        base_price = 100.0
        risk_prem = 0.08
        term_prem = TERM_LENGTH_PREMIUM_PCT_PER_YEAR  # 24-month → 1 extra year
        expected = base_price * (1.0 + risk_prem + term_prem)
        p24 = self.engine.get_forward_price(
            "electricity", "2016-01-01", self.records, seasonal=False, adaptive_lookback=False, regime_detect=False,
            risk_premium=risk_prem, term_months=24,
        )
        assert p24 == pytest.approx(expected, rel=1e-4)


# --- Phase KH depth tests ---

class TestTermPremiumDepth:
    def setup_method(self):
        self.engine = CompanyTariffEngine()
        self.records = _make_records(n=60, base_price=100.0)

    def test_48_month_is_three_years_premium(self):
        p12 = self.engine.get_forward_price(
            'electricity', '2016-01-01', self.records,
            seasonal=False, adaptive_lookback=False, regime_detect=False, term_months=12)
        p48 = self.engine.get_forward_price(
            'electricity', '2016-01-01', self.records,
            seasonal=False, adaptive_lookback=False, regime_detect=False, term_months=48)
        assert p48 - p12 == pytest.approx(100.0 * 3 * TERM_LENGTH_PREMIUM_PCT_PER_YEAR, rel=1e-6)

    def test_1_month_term_same_as_12_month(self):
        p12 = self.engine.get_forward_price(
            'electricity', '2016-01-01', self.records,
            seasonal=False, adaptive_lookback=False, regime_detect=False, term_months=12)
        p1 = self.engine.get_forward_price(
            'electricity', '2016-01-01', self.records,
            seasonal=False, adaptive_lookback=False, regime_detect=False, term_months=1)
        assert p1 == pytest.approx(p12)

    def test_term_premium_monotonic(self):
        prices = []
        for tm in [12, 24, 36, 48]:
            p = self.engine.get_forward_price(
                'electricity', '2016-01-01', self.records,
                seasonal=False, adaptive_lookback=False, regime_detect=False, term_months=tm)
            prices.append(p)
        for i in range(len(prices) - 1):
            assert prices[i] <= prices[i + 1]

    def test_term_premium_scales_with_base_price(self):
        records_200 = _make_records(n=60, base_price=200.0)
        p12 = self.engine.get_forward_price(
            'electricity', '2016-01-01', records_200,
            seasonal=False, adaptive_lookback=False, regime_detect=False, term_months=12)
        p24 = self.engine.get_forward_price(
            'electricity', '2016-01-01', records_200,
            seasonal=False, adaptive_lookback=False, regime_detect=False, term_months=24)
        assert p24 - p12 == pytest.approx(200.0 * TERM_LENGTH_PREMIUM_PCT_PER_YEAR, rel=1e-6)

    def test_0_month_term_same_as_12_month(self):
        p12 = self.engine.get_forward_price(
            'electricity', '2016-01-01', self.records,
            seasonal=False, adaptive_lookback=False, regime_detect=False, term_months=12)
        p0 = self.engine.get_forward_price(
            'electricity', '2016-01-01', self.records,
            seasonal=False, adaptive_lookback=False, regime_detect=False, term_months=0)
        assert p0 == pytest.approx(p12)

    def test_gas_36_month_two_years_premium(self):
        gas_records = _make_records(n=60, base_price=50.0)
        p12 = self.engine.get_forward_price(
            'gas', '2016-01-01', gas_records,
            seasonal=False, adaptive_lookback=False, regime_detect=False, term_months=12)
        p36 = self.engine.get_forward_price(
            'gas', '2016-01-01', gas_records,
            seasonal=False, adaptive_lookback=False, regime_detect=False, term_months=36)
        assert p36 - p12 == pytest.approx(50.0 * 2 * TERM_LENGTH_PREMIUM_PCT_PER_YEAR, rel=1e-6)

    def test_two_engines_independent(self):
        engine_a = CompanyTariffEngine()
        engine_b = CompanyTariffEngine()
        pa = engine_a.get_forward_price(
            'electricity', '2016-01-01', self.records,
            seasonal=False, adaptive_lookback=False, regime_detect=False, term_months=24)
        pb = engine_b.get_forward_price(
            'electricity', '2016-01-01', self.records,
            seasonal=False, adaptive_lookback=False, regime_detect=False, term_months=24)
        assert pa == pytest.approx(pb)

    def test_24_month_elec_price_positive(self):
        p = self.engine.get_forward_price(
            'electricity', '2016-01-01', self.records,
            seasonal=False, adaptive_lookback=False, regime_detect=False, term_months=24)
        assert p > 0.0

    def test_12_month_price_positive(self):
        p = self.engine.get_forward_price(
            'electricity', '2016-01-01', self.records,
            seasonal=False, adaptive_lookback=False, regime_detect=False, term_months=12)
        assert p > 0.0

    def test_constant_exported_as_float(self):
        assert isinstance(TERM_LENGTH_PREMIUM_PCT_PER_YEAR, float)
