"""Tests for Phase PX: Correlated Synthetic Market Generator.

Verifies CorrelatedGeneratorAdapter: OU dynamics, mean-reversion, correlation,
reproducibility, regime switching, protocol conformance, and factory wiring.
"""
import datetime
import math
import pytest


def _pearson_r(xs, ys):
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs) / n)
    sy = math.sqrt(sum((y - my) ** 2 for y in ys) / n)
    return cov / (sx * sy) if sx * sy > 0 else 0.0


def _stdev(xs):
    mean = sum(xs) / len(xs)
    return math.sqrt(sum((x - mean) ** 2 for x in xs) / len(xs))


def _run_steps(adapter, n):
    """Return list of market summaries from n advance steps."""
    return [adapter.get_market_summary() for _ in range(n)]


class TestOUDynamics:
    def test_ou_gas_stays_in_plausible_range(self):
        from tools.market_adapters.synthetic_generator import CorrelatedGeneratorAdapter
        adapter = CorrelatedGeneratorAdapter(seed=1)
        summaries = _run_steps(adapter, 1000)
        for s in summaries:
            assert 2.0 <= s["gas_spot_gbp_per_mwh"] <= 300.0

    def test_ou_elec_stays_in_plausible_range(self):
        from tools.market_adapters.synthetic_generator import CorrelatedGeneratorAdapter
        adapter = CorrelatedGeneratorAdapter(seed=2)
        summaries = _run_steps(adapter, 1000)
        for s in summaries:
            assert 5.0 <= s["elec_spot_gbp_per_mwh"] <= 1000.0

    def test_gas_mean_reverts_to_long_run(self):
        from tools.market_adapters.synthetic_generator import (
            CorrelatedGeneratorAdapter, GAS_LONG_RUN_MEAN_GBP_PER_MWH,
        )
        adapter = CorrelatedGeneratorAdapter(seed=3)
        prices = [s["gas_spot_gbp_per_mwh"] for s in _run_steps(adapter, 1000)]
        mean_price = sum(prices) / len(prices)
        assert abs(mean_price - GAS_LONG_RUN_MEAN_GBP_PER_MWH) < GAS_LONG_RUN_MEAN_GBP_PER_MWH * 0.20

    def test_elec_mean_reverts_to_long_run(self):
        from tools.market_adapters.synthetic_generator import (
            CorrelatedGeneratorAdapter, ELEC_LONG_RUN_MEAN_GBP_PER_MWH,
        )
        adapter = CorrelatedGeneratorAdapter(seed=4)
        prices = [s["elec_spot_gbp_per_mwh"] for s in _run_steps(adapter, 1000)]
        mean_price = sum(prices) / len(prices)
        assert abs(mean_price - ELEC_LONG_RUN_MEAN_GBP_PER_MWH) < ELEC_LONG_RUN_MEAN_GBP_PER_MWH * 0.20

    def test_elec_gas_correlation_positive(self):
        from tools.market_adapters.synthetic_generator import CorrelatedGeneratorAdapter
        adapter = CorrelatedGeneratorAdapter(seed=5)
        summaries = _run_steps(adapter, 1000)
        gas = [s["gas_spot_gbp_per_mwh"] for s in summaries]
        elec = [s["elec_spot_gbp_per_mwh"] for s in summaries]
        r = _pearson_r(gas, elec)
        assert r > 0.5, f"Expected correlation > 0.5, got {r:.3f}"

    def test_spot_prices_always_positive(self):
        from tools.market_adapters.synthetic_generator import CorrelatedGeneratorAdapter
        adapter = CorrelatedGeneratorAdapter(seed=6)
        summaries = _run_steps(adapter, 10000)
        for s in summaries:
            assert s["gas_spot_gbp_per_mwh"] > 0
            assert s["elec_spot_gbp_per_mwh"] > 0


class TestReproducibility:
    def test_same_seed_same_first_summary(self):
        from tools.market_adapters.synthetic_generator import CorrelatedGeneratorAdapter
        a1 = CorrelatedGeneratorAdapter(seed=42)
        a2 = CorrelatedGeneratorAdapter(seed=42)
        assert a1.get_market_summary() == a2.get_market_summary()

    def test_same_seed_same_sequence(self):
        from tools.market_adapters.synthetic_generator import CorrelatedGeneratorAdapter
        a1 = CorrelatedGeneratorAdapter(seed=99)
        a2 = CorrelatedGeneratorAdapter(seed=99)
        for _ in range(20):
            assert a1.get_market_summary() == a2.get_market_summary()

    def test_different_seeds_different_prices(self):
        from tools.market_adapters.synthetic_generator import CorrelatedGeneratorAdapter
        a1 = CorrelatedGeneratorAdapter(seed=10)
        a2 = CorrelatedGeneratorAdapter(seed=20)
        s1 = a1.get_market_summary()
        s2 = a2.get_market_summary()
        assert s1["elec_spot_gbp_per_mwh"] != s2["elec_spot_gbp_per_mwh"]


class TestForwardCurve:
    def test_forward_price_contango_3m_ahead(self):
        from tools.market_adapters.synthetic_generator import CorrelatedGeneratorAdapter
        adapter = CorrelatedGeneratorAdapter(seed=7, regime="normal")
        as_of = datetime.date(2025, 1, 1)
        delivery = datetime.date(2025, 4, 1)
        fwd = adapter.get_forward_price(as_of=as_of, delivery_date=delivery)
        spot = adapter.get_spot_elec_gbp_per_mwh()
        assert fwd > spot, f"Expected contango: fwd {fwd} > spot {spot}"

    def test_forward_price_returns_float(self):
        from tools.market_adapters.synthetic_generator import CorrelatedGeneratorAdapter
        adapter = CorrelatedGeneratorAdapter(seed=8)
        result = adapter.get_forward_price()
        assert isinstance(result, float)
        assert not math.isnan(result)

    def test_forward_price_gas_commodity(self):
        from tools.market_adapters.synthetic_generator import (
            CorrelatedGeneratorAdapter, FORWARD_CONTANGO_ANNUAL,
        )
        adapter = CorrelatedGeneratorAdapter(seed=9)
        fwd = adapter.get_forward_price(commodity="gas")
        spot = adapter.get_spot_gas_gbp_per_mwh()
        expected = round(spot * (1.0 + FORWARD_CONTANGO_ANNUAL), 2)
        assert fwd == expected


class TestMarketSummaryShape:
    def test_summary_has_same_keys_as_frozen(self):
        from tools.market_adapters.synthetic_generator import CorrelatedGeneratorAdapter
        adapter = CorrelatedGeneratorAdapter(seed=10)
        s = adapter.get_market_summary()
        expected_keys = {
            "as_of_date",
            "elec_spot_gbp_per_mwh",
            "gas_spot_gbp_per_mwh",
            "elec_12m_forward_gbp_per_mwh",
            "gas_12m_forward_gbp_per_mwh",
        }
        assert expected_keys == set(s.keys())

    def test_summary_elec_spot_matches_get_spot_elec(self):
        from tools.market_adapters.synthetic_generator import CorrelatedGeneratorAdapter
        adapter = CorrelatedGeneratorAdapter(seed=11)
        s = adapter.get_market_summary()
        assert s["elec_spot_gbp_per_mwh"] == adapter.get_spot_elec_gbp_per_mwh()

    def test_as_of_accepted_without_error(self):
        from tools.market_adapters.synthetic_generator import CorrelatedGeneratorAdapter
        adapter = CorrelatedGeneratorAdapter(seed=12)
        as_of = datetime.date(2025, 6, 1)
        s = adapter.get_market_summary(as_of=as_of)
        assert s["as_of_date"] == "2025-06-01"
        adapter.get_spot_elec_gbp_per_mwh(as_of=as_of)
        adapter.get_spot_gas_gbp_per_mwh(as_of=as_of)
        adapter.get_forward_price(as_of=as_of)


class TestRegimeSwitching:
    def test_crisis_regime_higher_volatility(self):
        from tools.market_adapters.synthetic_generator import CorrelatedGeneratorAdapter
        normal = CorrelatedGeneratorAdapter(seed=13, regime="normal")
        crisis = CorrelatedGeneratorAdapter(seed=13, regime="crisis")
        normal_prices = [s["elec_spot_gbp_per_mwh"] for s in _run_steps(normal, 1000)]
        crisis_prices = [s["elec_spot_gbp_per_mwh"] for s in _run_steps(crisis, 1000)]
        assert _stdev(crisis_prices) > _stdev(normal_prices)


class TestProtocolAndFactory:
    def test_protocol_satisfaction(self):
        from tools.market_data_port import MarketDataPort
        from tools.market_adapters.synthetic_generator import CorrelatedGeneratorAdapter
        assert isinstance(CorrelatedGeneratorAdapter(), MarketDataPort)

    def test_factory_resolves_synthetic(self):
        from tools.market_adapters import get_market_adapter
        from tools.market_adapters.synthetic_generator import CorrelatedGeneratorAdapter
        adapter = get_market_adapter("synthetic")
        assert isinstance(adapter, CorrelatedGeneratorAdapter)

    def test_factory_unknown_source_raises_value_error(self):
        from tools.market_adapters import get_market_adapter
        with pytest.raises(ValueError, match="Unknown market adapter source"):
            get_market_adapter("not_a_real_adapter")

    def test_factory_frozen2025_still_resolves(self):
        from tools.market_adapters import get_market_adapter
        from tools.market_adapters.frozen_2025 import Frozen2025Adapter
        adapter = get_market_adapter("frozen_2025")
        assert isinstance(adapter, Frozen2025Adapter)

    def test_env_var_synthetic_resolves(self, monkeypatch):
        from tools.market_adapters import get_market_adapter
        from tools.market_adapters.synthetic_generator import CorrelatedGeneratorAdapter
        monkeypatch.setenv("MARKET_ADAPTER_SOURCE", "synthetic")
        adapter = get_market_adapter()
        assert isinstance(adapter, CorrelatedGeneratorAdapter)
