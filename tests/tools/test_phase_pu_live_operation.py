import json, pytest
from pathlib import Path
from unittest.mock import patch


def _minimal_run_output(year="2025", active_ids=None):
    if active_ids is None:
        active_ids = ["C1", "C_IC1"]
    return {
        "final_treasury_gbp": 3_500_000.0,
        "years": {year: {
            "treasury_end_gbp": 3_000_000.0,
            "active_customer_ids": active_ids,
            "per_customer": {
                "C1": {"commodity": "electricity", "gross_gbp": 900.0,
                        "capital_gbp": 10.0, "net_gbp": 200.0,
                        "tariff_min_gbp_per_mwh": 200.0, "tariff_max_gbp_per_mwh": 220.0},
                "C_IC1": {"commodity": "electricity", "gross_gbp": 100000.0,
                            "capital_gbp": 500.0, "net_gbp": 50000.0,
                            "tariff_min_gbp_per_mwh": 150.0, "tariff_max_gbp_per_mwh": 160.0},
            },
            "hedge_fractions": {"C1": {"avg_hf": 0.85}},
            "acquisitions": [], "committee_wake_ups": 0,
        }},
        "per_customer_lifetime": {"C1": {"segment": "resi"}, "C_IC1": {"segment": "I&C"}},
        "customer_events": [{"customer_id": "C1", "event_date": "2024-12-31",
                              "unit_rate_gbp_per_mwh": 220.0, "event_type": "renewed"}],
        "bills": [
            {"customer_id": "C1", "period_start": "2024-01-01",
             "period_end": "2024-01-31", "total_consumption_kwh": 800.0},
            {"customer_id": "C1", "period_start": "2024-02-01",
             "period_end": "2024-02-28", "total_consumption_kwh": 800.0},
        ],
    }

_STUB_MARKET = {
    "as_of_date": "2025-06-07", "elec_spot_gbp_per_mwh": 70.0,
    "gas_spot_gbp_per_mwh": 32.0, "elec_12m_forward_gbp_per_mwh": 73.5,
    "gas_12m_forward_gbp_per_mwh": 33.6,
}
_STUB_SSP = [{"settlementDate": "2025-05-" + str(d).zfill(2), "systemSellPrice": 70.0}
             for d in range(1, 31)]

def _write_run(tmp_path, ro=None):
    f = tmp_path / "run.json"
    f.write_text(json.dumps(ro or _minimal_run_output()))
    return f


def _write_portfolio(tmp_path, customers=None):
    if customers is None:
        customers = [{"cid": "C1", "commodity": "electricity", "segment": "resi",
                      "current_rate_gbp_per_mwh": 220.0, "hedge_fraction": 0.6,
                      "next_renewal_estimate": "2025-06-15", "eac_kwh_per_year": 10000.0,
                      "last_renewal_date": "2024-06-15", "net_gbp_2025": 200.0}]
    p = {"generated_at": "2025-06-01T12:00:00Z", "source_year": 2025,
         "treasury_gbp": 3_000_000.0, "active_customer_count": len(customers),
         "customers": customers}
    f = tmp_path / "portfolio.json"
    f.write_text(json.dumps(p))
    return f


class TestProjectPortfolioTo2026:
    def _gen(self, tmp_path, ro=None):
        from tools.project_portfolio_to_2026 import generate
        rf = _write_run(tmp_path, ro)
        of = tmp_path / "out.json"
        return generate(str(rf), str(of)), of

    def test_extracts_active_customers(self, tmp_path):
        p, _ = self._gen(tmp_path)
        assert p["active_customer_count"] == 2

    def test_customer_ids_present(self, tmp_path):
        p, _ = self._gen(tmp_path)
        ids = [c["cid"] for c in p["customers"]]
        assert "C1" in ids and "C_IC1" in ids

    def test_uses_last_year(self, tmp_path):
        p, _ = self._gen(tmp_path)
        assert p["source_year"] == 2025

    def test_last_renewal_from_events(self, tmp_path):
        p, _ = self._gen(tmp_path)
        c1 = next(c for c in p["customers"] if c["cid"] == "C1")
        assert c1["last_renewal_date"] == "2024-12-31"

    def test_next_renewal_plus_12_months(self, tmp_path):
        p, _ = self._gen(tmp_path)
        c1 = next(c for c in p["customers"] if c["cid"] == "C1")
        assert c1["next_renewal_estimate"] == "2025-12-31"

    def test_rate_from_event(self, tmp_path):
        p, _ = self._gen(tmp_path)
        c1 = next(c for c in p["customers"] if c["cid"] == "C1")
        assert c1["current_rate_gbp_per_mwh"] == 220.0

    def test_no_event_gets_tariff_max(self, tmp_path):
        p, _ = self._gen(tmp_path)
        ic1 = next(c for c in p["customers"] if c["cid"] == "C_IC1")
        assert ic1["current_rate_gbp_per_mwh"] == 160.0
        assert ic1["next_renewal_estimate"] is None

    def test_hedge_fraction(self, tmp_path):
        p, _ = self._gen(tmp_path)
        c1 = next(c for c in p["customers"] if c["cid"] == "C1")
        assert c1["hedge_fraction"] == 0.85

    def test_output_written(self, tmp_path):
        p, of = self._gen(tmp_path)
        assert of.exists()
        assert json.loads(of.read_text())["active_customer_count"] == 2

class TestLiveMarket:
    def test_spot_elec_positive_float(self):
        from tools.live_market import fetch_spot_elec
        with patch("tools.live_market._best_records", return_value=_STUB_SSP):
            result = fetch_spot_elec()
        assert isinstance(result, float) and result > 0

    def test_spot_gas_fallback_to_elec_fraction(self):
        from tools.live_market import fetch_spot_gas
        with patch("tools.live_market.PRICE_FEED", Path("/nonexistent")):
            with patch("tools.live_market._best_records", return_value=_STUB_SSP):
                result = fetch_spot_gas()
        assert result > 0

    def test_effective_as_of_last_when_none(self):
        from tools.live_market import _effective_as_of
        recs = [{"settlementDate": "2025-05-01"}, {"settlementDate": "2025-05-10"}]
        assert _effective_as_of(recs, None) == "2025-05-10"

    def test_effective_as_of_exact(self):
        from tools.live_market import _effective_as_of
        recs = [{"settlementDate": "2025-05-01"}, {"settlementDate": "2025-05-10"}]
        assert _effective_as_of(recs, "2025-05-01") == "2025-05-01"

    def test_effective_as_of_prior_if_not_exact(self):
        from tools.live_market import _effective_as_of
        recs = [{"settlementDate": "2025-05-01"}, {"settlementDate": "2025-05-10"}]
        assert _effective_as_of(recs, "2025-05-05") == "2025-05-01"

    def test_gas_forward_is_spot_times_105pct(self):
        from tools.live_market import build_live_forward_price
        with patch("tools.live_market.fetch_spot_gas", return_value=32.0):
            result = build_live_forward_price(fuel="gas")
        assert result == round(32.0 * 1.05, 2)

    def test_summary_has_required_keys(self):
        from tools.live_market import get_market_summary
        with patch("tools.live_market._best_records", return_value=_STUB_SSP):
            with patch("tools.live_market.fetch_spot_gas", return_value=30.0):
                s = get_market_summary()
        for k in ["as_of_date", "elec_spot_gbp_per_mwh", "gas_spot_gbp_per_mwh",
                  "elec_12m_forward_gbp_per_mwh", "gas_12m_forward_gbp_per_mwh"]:
            assert k in s


import datetime as _dt

# Phase RX (S1 Option B): renewal windows are now computed against real wall-clock
# "today", decoupled from the frozen market as-of date. Pin the wall clock to the same
# date as _STUB_MARKET's as_of_date so these pre-existing fixtures (whose
# next_renewal_estimate values were written relative to 2025-06-07) keep meaning what
# they meant before the decoupling -- this test file is about the renewal-window/hedge
# logic, not the clock-decoupling behaviour itself (that gets its own dedicated tests).
_STUB_CLOCK = _dt.datetime(2025, 6, 7, 12, 0, 0, tzinfo=_dt.timezone.utc)


class TestRunLiveDecisions:
    def _run(self, tmp_path, customers=None):
        from tools.run_live_decisions import run_decisions
        pf = _write_portfolio(tmp_path, customers)
        with patch("tools.live_market.get_market_summary", return_value=_STUB_MARKET), \
             patch("tools.run_live_decisions._utc_now", return_value=_STUB_CLOCK):
            return run_decisions(str(pf), out_dir=str(tmp_path))

    def test_renewal_flag_within_60_days(self, tmp_path):
        d = self._run(tmp_path)
        assert len(d["renewal_flags"]) == 1
        assert d["renewal_flags"][0]["cid"] == "C1"

    def test_no_flag_outside_window(self, tmp_path):
        customers = [{"cid": "C2", "commodity": "electricity", "segment": "resi",
                      "current_rate_gbp_per_mwh": 220.0, "hedge_fraction": 0.7,
                      "next_renewal_estimate": "2025-09-01", "eac_kwh_per_year": 10000.0,
                      "last_renewal_date": "2024-09-01", "net_gbp_2025": 200.0}]
        d = self._run(tmp_path, customers)
        assert len(d["renewal_flags"]) == 0

    def test_hedge_increase_below_min(self, tmp_path):
        customers = [{"cid": "C1", "commodity": "electricity", "segment": "resi",
                      "current_rate_gbp_per_mwh": 220.0, "hedge_fraction": 0.2,
                      "next_renewal_estimate": "2025-08-01", "eac_kwh_per_year": 10000.0,
                      "last_renewal_date": "2024-08-01", "net_gbp_2025": 200.0}]
        d = self._run(tmp_path, customers)
        assert d["hedge_recommendation"] == "INCREASE"
        assert "C1" in d["hedge_affected_customers"]

    def test_hedge_hold_in_range(self, tmp_path):
        customers = [{"cid": "C1", "commodity": "electricity", "segment": "resi",
                      "current_rate_gbp_per_mwh": 220.0, "hedge_fraction": 0.7,
                      "next_renewal_estimate": "2025-08-01", "eac_kwh_per_year": 10000.0,
                      "last_renewal_date": "2024-08-01", "net_gbp_2025": 200.0}]
        d = self._run(tmp_path, customers)
        assert d["hedge_recommendation"] == "HOLD"

    def test_acquisition_prices_present(self, tmp_path):
        d = self._run(tmp_path)
        acq = d["acquisition_prices"]
        assert "resi_elec_gbp_per_mwh" in acq
        assert "ic_elec_gbp_per_mwh" in acq
        assert acq["resi_elec_gbp_per_mwh"] > acq["ic_elec_gbp_per_mwh"]

    def test_latest_json_written(self, tmp_path):
        self._run(tmp_path)
        latest = tmp_path / "live_decisions_latest.json"
        assert latest.exists()
        assert "decision_run_at" in json.loads(latest.read_text())

    def test_dated_json_written(self, tmp_path):
        self._run(tmp_path)
        assert (tmp_path / "live_decisions_20250607.json").exists()

    def test_proposed_rate_is_fwd_plus_costs(self, tmp_path):
        d = self._run(tmp_path)
        flag = d["renewal_flags"][0]
        expected = round(73.5 + 52.0 + 28.0, 2)
        assert flag["proposed_rate_gbp_per_mwh"] == expected
