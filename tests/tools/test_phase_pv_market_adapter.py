"""Tests for Phase PV: MarketDataPort swappable adapter.

Verifies the Protocol, Frozen2025Adapter, factory, and regression against direct live_market calls.
"""
import json, os, datetime, pytest
from pathlib import Path
from unittest.mock import patch

_STUB_SSP = [
    {"settlementDate": "2025-05-" + str(d).zfill(2), "systemSellPrice": 70.0}
    for d in range(1, 31)
]
_STUB_SUMMARY = {
    "as_of_date": "2025-06-07",
    "elec_spot_gbp_per_mwh": 70.0,
    "gas_spot_gbp_per_mwh": 32.0,
    "elec_12m_forward_gbp_per_mwh": 73.5,
    "gas_12m_forward_gbp_per_mwh": 33.6,
}


def _stub_adapter():
    """Minimal adapter satisfying MarketDataPort for injection tests."""
    class StubAdapter:
        def get_spot_elec_gbp_per_mwh(self, as_of=None):
            return 99.0
        def get_spot_gas_gbp_per_mwh(self, as_of=None):
            return 40.0
        def get_forward_price(self, as_of=None, delivery_date=None, commodity="electricity"):
            return 101.0 if commodity == "electricity" else 42.0
        def get_market_summary(self, as_of=None):
            return {
                "as_of_date": "2025-06-07",
                "elec_spot_gbp_per_mwh": 99.0,
                "gas_spot_gbp_per_mwh": 40.0,
                "elec_12m_forward_gbp_per_mwh": 101.0,
                "gas_12m_forward_gbp_per_mwh": 42.0,
            }
    return StubAdapter()


def _write_portfolio(tmp_path):
    customers = [{"cid": "C1", "commodity": "electricity", "segment": "resi",
                  "current_rate_gbp_per_mwh": 220.0, "hedge_fraction": 0.6,
                  "next_renewal_estimate": "2025-07-01", "eac_kwh_per_year": 10000.0,
                  "last_renewal_date": "2024-07-01", "net_gbp_2025": 200.0}]
    p = {"generated_at": "2025-06-01T12:00:00Z", "source_year": 2025,
         "treasury_gbp": 3_000_000.0, "active_customer_count": 1,
         "customers": customers}
    f = tmp_path / "portfolio.json"
    f.write_text(json.dumps(p))
    return f


class TestMarketDataPortProtocol:
    def test_frozen2025_satisfies_protocol(self):
        from tools.market_data_port import MarketDataPort
        from tools.market_adapters.frozen_2025 import Frozen2025Adapter
        assert isinstance(Frozen2025Adapter(), MarketDataPort)

    def test_stub_adapter_satisfies_protocol(self):
        from tools.market_data_port import MarketDataPort
        assert isinstance(_stub_adapter(), MarketDataPort)

    def test_protocol_methods_present(self):
        from tools.market_data_port import MarketDataPort
        for method in ("get_spot_elec_gbp_per_mwh", "get_spot_gas_gbp_per_mwh",
                       "get_forward_price", "get_market_summary"):
            assert hasattr(MarketDataPort, method)


class TestFrozen2025Adapter:
    def _adapter(self):
        from tools.market_adapters.frozen_2025 import Frozen2025Adapter
        return Frozen2025Adapter()

    def test_spot_elec_positive_float(self):
        with patch("tools.live_market._best_records", return_value=_STUB_SSP):
            result = self._adapter().get_spot_elec_gbp_per_mwh()
        assert isinstance(result, float) and result > 0

    def test_spot_gas_positive_float(self):
        with patch("tools.live_market._best_records", return_value=_STUB_SSP):
            result = self._adapter().get_spot_gas_gbp_per_mwh()
        assert isinstance(result, float) and result > 0

    def test_spot_elec_with_date(self):
        with patch("tools.live_market._best_records", return_value=_STUB_SSP):
            result = self._adapter().get_spot_elec_gbp_per_mwh(datetime.date(2025, 12, 31))
        assert isinstance(result, float) and result > 0

    def test_forward_price_elec_float(self):
        with patch("tools.live_market._best_records", return_value=_STUB_SSP):
            result = self._adapter().get_forward_price(commodity="electricity")
        assert isinstance(result, float) and result > 0

    def test_forward_price_gas_float(self):
        with patch("tools.live_market.fetch_spot_gas", return_value=32.0):
            result = self._adapter().get_forward_price(commodity="gas")
        assert result == round(32.0 * 1.05, 2)

    def test_market_summary_keys(self):
        with patch("tools.live_market.get_market_summary", return_value=_STUB_SUMMARY):
            s = self._adapter().get_market_summary()
        for k in ("as_of_date", "elec_spot_gbp_per_mwh", "gas_spot_gbp_per_mwh",
                  "elec_12m_forward_gbp_per_mwh", "gas_12m_forward_gbp_per_mwh"):
            assert k in s

    def test_regression_spot_elec_matches_live_market(self):
        """Adapter result must equal direct live_market call."""
        from tools.live_market import fetch_spot_elec
        with patch("tools.live_market._best_records", return_value=_STUB_SSP):
            direct = fetch_spot_elec()
            via_adapter = self._adapter().get_spot_elec_gbp_per_mwh()
        assert direct == via_adapter

    def test_determinism_two_instances(self):
        from tools.market_adapters.frozen_2025 import Frozen2025Adapter
        with patch("tools.live_market._best_records", return_value=_STUB_SSP):
            a1 = Frozen2025Adapter().get_spot_elec_gbp_per_mwh()
            a2 = Frozen2025Adapter().get_spot_elec_gbp_per_mwh()
        assert a1 == a2

    def test_before_as_of_date_returns_frozen_data(self):
        past_date = datetime.date(2020, 1, 1)
        with patch("tools.live_market._best_records", return_value=_STUB_SSP):
            result = self._adapter().get_spot_elec_gbp_per_mwh(past_date)
        assert isinstance(result, float) and result > 0

    def test_after_as_of_date_returns_frozen_data(self):
        future_date = datetime.date(2030, 1, 1)
        with patch("tools.live_market._best_records", return_value=_STUB_SSP):
            result = self._adapter().get_spot_elec_gbp_per_mwh(future_date)
        assert isinstance(result, float) and result > 0


class TestAdapterFactory:
    def test_default_returns_frozen2025(self):
        from tools.market_adapters import get_market_adapter
        from tools.market_adapters.frozen_2025 import Frozen2025Adapter
        adapter = get_market_adapter("frozen_2025")
        assert isinstance(adapter, Frozen2025Adapter)

    def test_no_arg_returns_frozen2025(self):
        from tools.market_adapters import get_market_adapter
        from tools.market_adapters.frozen_2025 import Frozen2025Adapter
        adapter = get_market_adapter()
        assert isinstance(adapter, Frozen2025Adapter)

    def test_unknown_source_raises_value_error(self):
        from tools.market_adapters import get_market_adapter
        with pytest.raises(ValueError, match="Unknown market adapter source"):
            get_market_adapter("synthetic_v1")

    def test_env_var_controls_selection(self, monkeypatch):
        from tools.market_adapters import get_market_adapter
        from tools.market_adapters.frozen_2025 import Frozen2025Adapter
        monkeypatch.setenv("MARKET_ADAPTER_SOURCE", "frozen_2025")
        adapter = get_market_adapter()
        assert isinstance(adapter, Frozen2025Adapter)

    def test_third_party_stub_satisfies_protocol_no_callers_change(self):
        """Adding a new adapter satisfying the Protocol requires zero changes to callers."""
        from tools.market_data_port import MarketDataPort
        stub = _stub_adapter()
        assert isinstance(stub, MarketDataPort)
        # Use it in run_decisions — callers are unchanged
        assert stub.get_market_summary()["elec_spot_gbp_per_mwh"] == 99.0


class TestRunLiveDecisionsUsesAdapter:
    def test_injected_adapter_drives_decisions(self, tmp_path):
        """run_decisions accepts a market_adapter; output reflects adapter data."""
        from tools.run_live_decisions import run_decisions
        pf = _write_portfolio(tmp_path)
        stub = _stub_adapter()
        d = run_decisions(str(pf), out_dir=str(tmp_path), market_adapter=stub)
        assert d["elec_spot_gbp_per_mwh"] == 99.0
        assert d["gas_spot_gbp_per_mwh"] == 40.0
        assert d["elec_12m_forward_gbp_per_mwh"] == 101.0

    def test_default_adapter_live_market_still_patchable(self, tmp_path):
        """Existing patch on tools.live_market.get_market_summary still works (regression)."""
        from tools.run_live_decisions import run_decisions
        pf = _write_portfolio(tmp_path)
        with patch("tools.live_market.get_market_summary", return_value=_STUB_SUMMARY):
            d = run_decisions(str(pf), out_dir=str(tmp_path))
        assert d["elec_spot_gbp_per_mwh"] == 70.0

    def test_env_var_frozen2025_runs_end_to_end(self, tmp_path, monkeypatch):
        """MARKET_ADAPTER_SOURCE=frozen_2025 produces a valid decision dict."""
        from tools.run_live_decisions import run_decisions
        pf = _write_portfolio(tmp_path)
        monkeypatch.setenv("MARKET_ADAPTER_SOURCE", "frozen_2025")
        with patch("tools.live_market.get_market_summary", return_value=_STUB_SUMMARY):
            d = run_decisions(str(pf), out_dir=str(tmp_path))
        assert "decision_run_at" in d
        assert "hedge_recommendation" in d
