"""Tests for Phase PZ: Scenario Stress Testing via Synthetic Market.

Verifies run_scenario_analysis(): 4-scenario output structure, portfolio exposure
delta, CorrelatedGeneratorAdapter start-price params, board section rendering.
"""
import json
import pytest
from pathlib import Path


def _make_portfolio(tmp_path, customers=None):
    if customers is None:
        customers = [
            {
                "cid": "C1",
                "commodity": "electricity",
                "segment": "resi",
                "current_rate_gbp_per_mwh": 220.0,
                "hedge_fraction": 0.6,
                "next_renewal_estimate": "2025-06-15",
                "eac_kwh_per_year": 10000.0,
                "last_renewal_date": "2024-06-15",
                "net_gbp_2025": 200.0,
            },
            {
                "cid": "C_IC1",
                "commodity": "electricity",
                "segment": "I&C",
                "current_rate_gbp_per_mwh": 160.0,
                "hedge_fraction": 0.3,
                "next_renewal_estimate": None,
                "eac_kwh_per_year": 4000000.0,
                "last_renewal_date": "2024-01-01",
            },
        ]
    portfolio = {
        "generated_at": "2025-06-07T12:00:00Z",
        "source_year": 2025,
        "treasury_gbp": 3_000_000.0,
        "active_customer_count": len(customers),
        "customers": customers,
    }
    p = tmp_path / "portfolio.json"
    p.write_text(json.dumps(portfolio))
    return p


class TestCorrelatedGeneratorStartPrices:
    def test_custom_gas_start(self):
        from tools.market_adapters.synthetic_generator import CorrelatedGeneratorAdapter
        a = CorrelatedGeneratorAdapter(seed=1, gas_start=108.0)
        assert a._gas == 108.0

    def test_custom_elec_start(self):
        from tools.market_adapters.synthetic_generator import CorrelatedGeneratorAdapter
        a = CorrelatedGeneratorAdapter(seed=1, elec_start=213.0)
        assert a._elec == 213.0

    def test_default_starts_at_long_run_mean(self):
        from tools.market_adapters.synthetic_generator import (
            CorrelatedGeneratorAdapter,
            GAS_LONG_RUN_MEAN_GBP_PER_MWH,
            ELEC_LONG_RUN_MEAN_GBP_PER_MWH,
        )
        a = CorrelatedGeneratorAdapter(seed=1)
        assert a._gas == GAS_LONG_RUN_MEAN_GBP_PER_MWH
        assert a._elec == ELEC_LONG_RUN_MEAN_GBP_PER_MWH

    def test_crisis_start_price_used(self):
        from tools.market_adapters.synthetic_generator import CorrelatedGeneratorAdapter
        a = CorrelatedGeneratorAdapter(seed=3, regime="crisis", gas_start=108.0, elec_start=213.0)
        assert a._forced_crisis is True
        assert a._gas == 108.0


class TestScenarioMarketState:
    def test_base_scenario_projects_12_steps(self):
        from tools.run_live_decisions import _SCENARIO_CONFIGS, _scenario_market_state
        mkt = _scenario_market_state(_SCENARIO_CONFIGS["base"])
        assert "elec_12m_forward_gbp_per_mwh" in mkt
        assert "gas_12m_forward_gbp_per_mwh" in mkt

    def test_scenario_prices_ordered_bull_lt_base_lt_bear_lt_crisis(self):
        from tools.run_live_decisions import _SCENARIO_CONFIGS, _scenario_market_state
        prices = {n: _scenario_market_state(cfg)["elec_12m_forward_gbp_per_mwh"]
                  for n, cfg in _SCENARIO_CONFIGS.items()}
        assert prices["bull"] < prices["base"] < prices["bear"] < prices["crisis"]

    def test_scenarios_deterministic_no_advance(self):
        from tools.run_live_decisions import _SCENARIO_CONFIGS, _scenario_market_state
        r1 = _scenario_market_state(_SCENARIO_CONFIGS["crisis"])
        r2 = _scenario_market_state(_SCENARIO_CONFIGS["crisis"])
        assert r1["elec_spot_gbp_per_mwh"] == r2["elec_spot_gbp_per_mwh"]

    def test_all_four_scenarios_defined(self):
        from tools.run_live_decisions import _SCENARIO_CONFIGS
        for name in ("base", "bull", "bear", "crisis"):
            assert name in _SCENARIO_CONFIGS


class TestRunScenarioAnalysis:
    def _run(self, tmp_path, customers=None):
        from tools.run_live_decisions import run_scenario_analysis
        pf = _make_portfolio(tmp_path, customers)
        return run_scenario_analysis(portfolio_path=str(pf), out_dir=str(tmp_path))

    def test_four_scenarios_in_result(self, tmp_path):
        result = self._run(tmp_path)
        assert set(result["scenarios"].keys()) == {"base", "bull", "bear", "crisis"}

    def test_each_scenario_has_required_keys(self, tmp_path):
        result = self._run(tmp_path)
        for name, s in result["scenarios"].items():
            assert "elec_12m_forward_gbp_per_mwh" in s, name
            assert "gas_12m_forward_gbp_per_mwh" in s, name
            assert "hedge_recommendation" in s, name
            assert "renewal_flags" in s, name
            assert "label" in s, name

    def test_output_json_written(self, tmp_path):
        self._run(tmp_path)
        out = tmp_path / "scenario_analysis_latest.json"
        assert out.exists()
        loaded = json.loads(out.read_text())
        assert "scenarios" in loaded

    def test_exposure_delta_has_three_keys(self, tmp_path):
        result = self._run(tmp_path)
        delta = result["portfolio_exposure_delta_gbp"]
        assert set(delta.keys()) == {"bull", "bear", "crisis"}

    def test_crisis_exposure_delta_positive(self, tmp_path):
        result = self._run(tmp_path)
        assert result["portfolio_exposure_delta_gbp"]["crisis"] > 0

    def test_bull_exposure_delta_less_than_crisis(self, tmp_path):
        result = self._run(tmp_path)
        delta = result["portfolio_exposure_delta_gbp"]
        assert delta["bull"] < delta["crisis"]

    def test_generated_at_present(self, tmp_path):
        result = self._run(tmp_path)
        assert "generated_at" in result

    def test_projection_months_is_twelve(self, tmp_path):
        result = self._run(tmp_path)
        assert result["projection_months"] == 12

    def test_renewal_flags_within_window_populated(self, tmp_path):
        result = self._run(tmp_path)
        # C1 has renewal in ~8 days from as_of 2025-06-07 -> 2025-06-15
        base_flags = result["scenarios"]["base"]["renewal_flags"]
        assert any(f["cid"] == "C1" for f in base_flags)

    def test_all_scenarios_reproducible(self, tmp_path):
        pf = _make_portfolio(tmp_path)
        from tools.run_live_decisions import run_scenario_analysis
        r1 = run_scenario_analysis(portfolio_path=str(pf), out_dir=str(tmp_path))
        r2 = run_scenario_analysis(portfolio_path=str(pf), out_dir=str(tmp_path))
        for name in ("base", "bull", "bear", "crisis"):
            assert (
                r1["scenarios"][name]["elec_12m_forward_gbp_per_mwh"]
                == r2["scenarios"][name]["elec_12m_forward_gbp_per_mwh"]
            )


class TestScenarioSensitivitySection:
    def _make_data_with_scenario(self, tmp_path):
        from tools.run_live_decisions import run_scenario_analysis
        pf = _make_portfolio(tmp_path)
        sa = run_scenario_analysis(portfolio_path=str(pf), out_dir=str(tmp_path))
        return {"scenario_analysis": sa}

    def test_section_renders_all_four_scenarios(self, tmp_path):
        from saas.reporting.annual_report import _section_scenario_sensitivity
        data = self._make_data_with_scenario(tmp_path)
        text = _section_scenario_sensitivity(data)
        for name in ("Base", "Bull", "Bear", "Crisis"):
            assert name in text

    def test_section_shows_exposure_delta(self, tmp_path):
        from saas.reporting.annual_report import _section_scenario_sensitivity
        data = self._make_data_with_scenario(tmp_path)
        text = _section_scenario_sensitivity(data)
        assert "Exposure Delta" in text

    def test_section_silent_when_no_data(self):
        from saas.reporting.annual_report import _section_scenario_sensitivity
        text = _section_scenario_sensitivity({})
        assert "Not available" in text

    def test_section_regime_blindness_callout(self, tmp_path):
        from saas.reporting.annual_report import _section_scenario_sensitivity
        data = self._make_data_with_scenario(tmp_path)
        text = _section_scenario_sensitivity(data)
        assert "regime-change blindness" in text.lower() or "regime" in text.lower()
