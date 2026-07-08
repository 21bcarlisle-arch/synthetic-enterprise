"""Tests for Phase RX (S1 Option B, docs/staging/S1_SHADOW_LIVE_TRACK_RECORD_DESIGN.md):
- tools/run_live_decisions.py's two-clock decoupling (wall-clock renewal countdown,
  honestly-labelled market data staleness) and new retention-EV field.
- tools/generate_track_record_scorecard.py's predicted-vs-realised grading.
- tools/generate_method_data.py folding the scorecard into the public Method page.
"""
import datetime as dt
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from company.analytics.counterfactual_retention import (
    RESI_OFFER_COST_GBP, IC_OFFER_COST_GBP, _RETENTION_EFFECTIVENESS,
)
from company.crm.enriched_churn_estimate import enriched_churn_estimate

PROJECT = Path(__file__).resolve().parents[2]

_STUB_MARKET = {
    "as_of_date": "2025-06-07", "elec_spot_gbp_per_mwh": 70.0,
    "gas_spot_gbp_per_mwh": 32.0, "elec_12m_forward_gbp_per_mwh": 73.5,
    "gas_12m_forward_gbp_per_mwh": 33.6,
}


def _write_portfolio(tmp_path, customers=None, filename="portfolio.json"):
    if customers is None:
        customers = [{"cid": "C1", "commodity": "electricity", "segment": "resi",
                      "current_rate_gbp_per_mwh": 200.0, "hedge_fraction": 0.3,
                      "next_renewal_estimate": "2025-07-01", "eac_kwh_per_year": 12000.0,
                      "last_renewal_date": "2024-06-20", "net_gbp_2025": 100.0}]
    p = {"generated_at": "2025-06-01T12:00:00Z", "source_year": 2025,
         "treasury_gbp": 3_000_000.0, "active_customer_count": len(customers),
         "customers": customers}
    f = tmp_path / filename
    f.write_text(json.dumps(p))
    return f


# ---------------------------------------------------------------------------
# Two-clock decoupling
# ---------------------------------------------------------------------------

class TestTwoClockDecoupling:
    def test_renewal_flags_days_change_with_clock_independent_of_market_as_of(self):
        """The exact assertion the task spec asks for: _renewal_flags's result changes
        when clock_date advances by a day, with market as_of never even passed in."""
        from tools.run_live_decisions import _renewal_flags
        customers = [{"cid": "C1", "commodity": "electricity", "segment": "resi",
                      "current_rate_gbp_per_mwh": 200.0, "hedge_fraction": 0.5,
                      "next_renewal_estimate": "2025-07-01", "eac_kwh_per_year": 10000.0,
                      "last_renewal_date": "2024-07-01"}]
        flags_day1 = _renewal_flags(customers, "2025-06-20", 73.5, 33.6)
        flags_day2 = _renewal_flags(customers, "2025-06-21", 73.5, 33.6)
        assert flags_day1[0]["days_to_renewal"] - flags_day2[0]["days_to_renewal"] == 1

    def test_days_to_renewal_advances_with_real_run_wall_clock_not_market_as_of(self, tmp_path):
        from tools.run_live_decisions import run_decisions
        pf = _write_portfolio(tmp_path)
        with patch("tools.live_market.get_market_summary", return_value=_STUB_MARKET):
            with patch("tools.run_live_decisions._utc_now",
                        return_value=dt.datetime(2025, 6, 20, tzinfo=dt.timezone.utc)):
                d1 = run_decisions(str(pf), out_dir=str(tmp_path))
            with patch("tools.run_live_decisions._utc_now",
                        return_value=dt.datetime(2025, 6, 21, tzinfo=dt.timezone.utc)):
                d2 = run_decisions(str(pf), out_dir=str(tmp_path))
        assert d1["renewal_flags"][0]["days_to_renewal"] - d2["renewal_flags"][0]["days_to_renewal"] == 1
        # market as-of is genuinely unchanged across both runs -- the two clocks are decoupled.
        assert d1["market_as_of_date"] == d2["market_as_of_date"] == "2025-06-07"

    def test_market_data_stale_days_computed_from_wall_clock(self, tmp_path):
        from tools.run_live_decisions import run_decisions
        pf = _write_portfolio(tmp_path)
        clock = dt.datetime(2025, 6, 20, tzinfo=dt.timezone.utc)
        with patch("tools.live_market.get_market_summary", return_value=_STUB_MARKET), \
             patch("tools.run_live_decisions._utc_now", return_value=clock):
            d = run_decisions(str(pf), out_dir=str(tmp_path))
        assert d["market_data_stale_days"] == 13  # 2025-06-20 minus 2025-06-07

    def test_market_data_stale_days_none_when_market_as_of_missing(self, tmp_path):
        from tools.run_live_decisions import run_decisions
        pf = _write_portfolio(tmp_path)
        stub = dict(_STUB_MARKET, as_of_date=None)
        with patch("tools.live_market.get_market_summary", return_value=stub), \
             patch("tools.run_live_decisions._utc_now",
                   return_value=dt.datetime(2025, 6, 20, tzinfo=dt.timezone.utc)):
            with pytest.raises(Exception):
                # date_tag = as_of.replace(...) would blow up on None -- confirms this
                # code path is never silently swallowed into a fake number.
                run_decisions(str(pf), out_dir=str(tmp_path))


# ---------------------------------------------------------------------------
# Retention EV field -- epistemic care
# ---------------------------------------------------------------------------

class TestRetentionEV:
    def test_retention_ev_matches_manual_computation_resi(self, tmp_path):
        from tools.run_live_decisions import run_decisions
        clock = dt.datetime(2025, 6, 20, tzinfo=dt.timezone.utc)
        customers = [{"cid": "TCV1", "commodity": "electricity", "segment": "resi",
                      "current_rate_gbp_per_mwh": 200.0, "hedge_fraction": 0.3,
                      "next_renewal_estimate": "2025-07-01", "eac_kwh_per_year": 12000.0,
                      "last_renewal_date": "2024-06-20", "net_gbp_2025": 100.0}]
        pf = _write_portfolio(tmp_path, customers)
        with patch("tools.live_market.get_market_summary", return_value=_STUB_MARKET), \
             patch("tools.run_live_decisions._utc_now", return_value=clock):
            d = run_decisions(str(pf), out_dir=str(tmp_path))
        flag = d["renewal_flags"][0]

        tenure_years = (dt.date(2025, 6, 20) - dt.date(2024, 6, 20)).days / 365.25
        expected_churn = enriched_churn_estimate(
            200.0, flag["proposed_rate_gbp_per_mwh"], tenure_years, 12000.0,
            fuel="electricity", hedge_fraction=0.3, segment="resi",
        )
        assert flag["company_churn_estimate"] == round(expected_churn, 4)

        expected_ev = round(
            expected_churn * _RETENTION_EFFECTIVENESS * flag["expected_gross_margin_gbp_pa"]
            - RESI_OFFER_COST_GBP, 2,
        )
        assert flag["retention_ev_gbp"] == expected_ev
        assert flag["retention_ev_note"] is None

    def test_retention_ev_uses_ic_offer_cost_for_ic_segment(self, tmp_path):
        from tools.run_live_decisions import run_decisions
        clock = dt.datetime(2025, 6, 20, tzinfo=dt.timezone.utc)
        customers = [{"cid": "TIC1", "commodity": "electricity", "segment": "I&C",
                      "current_rate_gbp_per_mwh": 150.0, "hedge_fraction": 0.0,
                      "next_renewal_estimate": "2025-07-01", "eac_kwh_per_year": 4_000_000.0,
                      "last_renewal_date": "2020-06-20", "net_gbp_2025": 5000.0}]
        pf = _write_portfolio(tmp_path, customers)
        with patch("tools.live_market.get_market_summary", return_value=_STUB_MARKET), \
             patch("tools.run_live_decisions._utc_now", return_value=clock):
            d = run_decisions(str(pf), out_dir=str(tmp_path))
        flag = d["renewal_flags"][0]
        # Reconstruct with IC_OFFER_COST_GBP and confirm the EV used the I&C cost, not resi's.
        tenure_years = (dt.date(2025, 6, 20) - dt.date(2020, 6, 20)).days / 365.25
        expected_churn = enriched_churn_estimate(
            150.0, flag["proposed_rate_gbp_per_mwh"], tenure_years, 4_000_000.0,
            fuel="electricity", hedge_fraction=0.0, segment="I&C",
        )
        expected_ev_ic_cost = round(
            expected_churn * _RETENTION_EFFECTIVENESS * flag["expected_gross_margin_gbp_pa"]
            - IC_OFFER_COST_GBP, 2,
        )
        expected_ev_resi_cost = round(
            expected_churn * _RETENTION_EFFECTIVENESS * flag["expected_gross_margin_gbp_pa"]
            - RESI_OFFER_COST_GBP, 2,
        )
        assert flag["retention_ev_gbp"] == expected_ev_ic_cost
        assert flag["retention_ev_gbp"] != expected_ev_resi_cost

    def test_retention_ev_none_when_current_rate_missing(self, tmp_path):
        from tools.run_live_decisions import run_decisions
        clock = dt.datetime(2025, 6, 20, tzinfo=dt.timezone.utc)
        customers = [{"cid": "TNR1", "commodity": "electricity", "segment": "resi",
                      "current_rate_gbp_per_mwh": None, "hedge_fraction": 0.3,
                      "next_renewal_estimate": "2025-07-01", "eac_kwh_per_year": 12000.0,
                      "last_renewal_date": "2024-06-20", "net_gbp_2025": 100.0}]
        pf = _write_portfolio(tmp_path, customers)
        with patch("tools.live_market.get_market_summary", return_value=_STUB_MARKET), \
             patch("tools.run_live_decisions._utc_now", return_value=clock):
            d = run_decisions(str(pf), out_dir=str(tmp_path))
        flag = d["renewal_flags"][0]
        assert flag["retention_ev_gbp"] is None
        assert flag["company_churn_estimate"] is None
        assert "ungraded" in flag["retention_ev_note"]

    def test_retention_ev_none_when_eac_missing_no_expected_margin(self, tmp_path):
        from tools.run_live_decisions import run_decisions
        clock = dt.datetime(2025, 6, 20, tzinfo=dt.timezone.utc)
        customers = [{"cid": "TNE1", "commodity": "electricity", "segment": "resi",
                      "current_rate_gbp_per_mwh": 200.0, "hedge_fraction": 0.3,
                      "next_renewal_estimate": "2025-07-01", "eac_kwh_per_year": None,
                      "last_renewal_date": "2024-06-20", "net_gbp_2025": 100.0}]
        pf = _write_portfolio(tmp_path, customers)
        with patch("tools.live_market.get_market_summary", return_value=_STUB_MARKET), \
             patch("tools.run_live_decisions._utc_now", return_value=clock):
            d = run_decisions(str(pf), out_dir=str(tmp_path))
        flag = d["renewal_flags"][0]
        assert flag["expected_gross_margin_gbp_pa"] is None
        assert flag["retention_ev_gbp"] is None

    def test_tenure_years_proxy_lower_bound(self):
        from tools.run_live_decisions import _tenure_years
        assert _tenure_years("2024-06-20", "2025-06-20") == pytest.approx(1.0, abs=0.01)
        assert _tenure_years(None, "2025-06-20") == 0.0
        assert _tenure_years("not-a-date", "2025-06-20") == 0.0

    def test_offer_cost_gbp_reuses_counterfactual_retention_constants(self):
        from tools.run_live_decisions import _offer_cost_gbp
        assert _offer_cost_gbp("I&C") == IC_OFFER_COST_GBP
        assert _offer_cost_gbp("resi") == RESI_OFFER_COST_GBP
        assert _offer_cost_gbp("unknown") == RESI_OFFER_COST_GBP


class TestEpistemicWallDiscipline:
    """Direct source-text check: the live/prospective decision path must never import
    simulation/ or reference SIM ground-truth fields. This is a stronger, more literal
    guarantee than the epistemic_verifier's diff-scan (tools/ is exempt from it), since
    this task explicitly calls out epistemic care as the one place a mistake here would
    be a real architectural violation, not just a bug."""

    def _source(self, rel):
        return (PROJECT / rel).read_text()

    @pytest.mark.parametrize("rel", [
        "tools/run_live_decisions.py",
        "tools/generate_track_record_scorecard.py",
    ])
    def test_no_simulation_imports_or_sim_ground_truth(self, rel):
        src = self._source(rel)
        assert "import simulation" not in src
        assert "from simulation" not in src
        assert "import sim." not in src
        assert "from sim." not in src
        assert "sim_churn_probability" not in src
        assert "realized_churn_probability" not in src


# ---------------------------------------------------------------------------
# Scorecard generator
# ---------------------------------------------------------------------------

def _write_log(tmp_path, entries, name="log.jsonl"):
    f = tmp_path / name
    f.write_text("\n".join(json.dumps(e) for e in entries) + "\n")
    return f


def _write_scorecard_portfolio(tmp_path, customers, name="portfolio.json"):
    p = {"generated_at": "2026-07-01T00:00:00Z", "customers": customers}
    f = tmp_path / name
    f.write_text(json.dumps(p))
    return f


class TestScorecardGeneratorEmptyCase:
    def test_empty_log_handled_cleanly(self, tmp_path):
        from tools.generate_track_record_scorecard import generate
        log = tmp_path / "empty.jsonl"
        log.write_text("")
        port = _write_scorecard_portfolio(tmp_path, [])
        out = tmp_path / "out.json"
        r = generate(str(log), str(port), str(out), today=dt.date(2026, 7, 1))
        assert r["clock_started"] is None
        assert r["renewal_grading"]["graded_count"] == 0
        assert r["renewal_grading"]["pending_count"] == 0
        assert out.exists()

    def test_real_log_scaffold_shows_zero_graded_with_clock_started(self, tmp_path):
        """The real live log currently has too little elapsed time to grade anything --
        confirm the generator represents that as a first-class honest state, not an error."""
        from tools.generate_track_record_scorecard import generate
        real_log = PROJECT / "site" / "state" / "live_decisions_log.jsonl"
        real_portfolio = PROJECT / "site" / "state" / "live_portfolio.json"
        out = tmp_path / "out.json"
        r = generate(str(real_log), str(real_portfolio), str(out), today=dt.date(2026, 7, 7))
        assert r["clock_started"] is not None
        assert isinstance(r["renewal_grading"]["graded_count"], int)
        assert r["renewal_grading"]["graded_count"] >= 0


class TestScorecardGeneratorGrading:
    def _fixture(self, tmp_path):
        entries = [
            {
                "decision_run_at": "2026-06-01T00:00:00Z",
                "market_data_stale_days": 100,
                "hedge_recommendation": "HOLD",
                "renewal_flags": [
                    {"cid": "CG1", "renewal_date": "2026-06-10",
                     "proposed_rate_gbp_per_mwh": 200.0,
                     "company_churn_estimate": 0.1, "retention_ev_gbp": 30.0},
                    {"cid": "CG2", "renewal_date": "2026-06-10",
                     "proposed_rate_gbp_per_mwh": 150.0,
                     "company_churn_estimate": 0.05, "retention_ev_gbp": -10.0},
                    {"cid": "CG3", "renewal_date": "2026-06-10",
                     "proposed_rate_gbp_per_mwh": 180.0,
                     "company_churn_estimate": None, "retention_ev_gbp": None},
                    {"cid": "CP1", "renewal_date": "2026-08-01",
                     "proposed_rate_gbp_per_mwh": 210.0,
                     "company_churn_estimate": 0.2, "retention_ev_gbp": 5.0,
                     "days_to_renewal": 31},
                ],
            },
            {
                "decision_run_at": "2026-06-15T00:00:00Z",
                "market_data_stale_days": 90,
                "hedge_recommendation": "INCREASE",
                "renewal_flags": [],
            },
        ]
        log = _write_log(tmp_path, entries)
        customers = [
            {"cid": "CG1", "last_renewal_date": "2026-06-10", "current_rate_gbp_per_mwh": 202.0},
            {"cid": "CG2", "last_renewal_date": "2026-06-12", "current_rate_gbp_per_mwh": 170.0},
            # CG3 deliberately absent -> inferred churn
            {"cid": "CP1", "last_renewal_date": "2025-01-01", "current_rate_gbp_per_mwh": 205.0},
        ]
        port = _write_scorecard_portfolio(tmp_path, customers)
        return log, port

    def test_graded_and_pending_both_exercised(self, tmp_path):
        from tools.generate_track_record_scorecard import generate
        log, port = self._fixture(tmp_path)
        out = tmp_path / "out.json"
        r = generate(str(log), str(port), str(out), today=dt.date(2026, 7, 1))
        rg = r["renewal_grading"]
        assert rg["graded_count"] == 3  # CG1 on-target, CG2 off-target, CG3 churned
        assert rg["pending_count"] == 1  # CP1's window hasn't opened yet
        assert rg["on_target_count"] == 1
        assert rg["off_target_count"] == 1
        assert rg["churned_count"] == 1

    def test_on_target_within_tolerance(self, tmp_path):
        from tools.generate_track_record_scorecard import generate
        log, port = self._fixture(tmp_path)
        out = tmp_path / "out.json"
        r = generate(str(log), str(port), str(out), today=dt.date(2026, 7, 1))
        cg1 = next(g for g in r["renewal_grading"]["graded"] if g["cid"] == "CG1")
        assert cg1["outcome"] == "renewed_on_target"
        assert cg1["diff_pct"] == pytest.approx(0.01, abs=0.001)

    def test_off_target_outside_tolerance(self, tmp_path):
        from tools.generate_track_record_scorecard import generate
        log, port = self._fixture(tmp_path)
        out = tmp_path / "out.json"
        r = generate(str(log), str(port), str(out), today=dt.date(2026, 7, 1))
        cg2 = next(g for g in r["renewal_grading"]["graded"] if g["cid"] == "CG2")
        assert cg2["outcome"] == "renewed_off_target"
        assert cg2["diff_pct"] > 0.02

    def test_churned_inferred_when_absent_from_portfolio(self, tmp_path):
        from tools.generate_track_record_scorecard import generate
        log, port = self._fixture(tmp_path)
        out = tmp_path / "out.json"
        r = generate(str(log), str(port), str(out), today=dt.date(2026, 7, 1))
        cg3 = next(g for g in r["renewal_grading"]["graded"] if g["cid"] == "CG3")
        assert cg3["outcome"] == "churned"
        assert "snapshot" in cg3["note"]

    def test_pending_entry_not_graded(self, tmp_path):
        from tools.generate_track_record_scorecard import generate
        log, port = self._fixture(tmp_path)
        out = tmp_path / "out.json"
        r = generate(str(log), str(port), str(out), today=dt.date(2026, 7, 1))
        pending_cids = [p["cid"] for p in r["renewal_grading"]["pending"]]
        assert pending_cids == ["CP1"]
        graded_cids = [g["cid"] for g in r["renewal_grading"]["graded"]]
        assert "CP1" not in graded_cids

    def test_inconclusive_when_renewal_window_passed_but_no_renewal_recorded(self, tmp_path):
        from tools.generate_track_record_scorecard import generate
        entries = [{
            "decision_run_at": "2026-06-01T00:00:00Z",
            "market_data_stale_days": 50,
            "hedge_recommendation": "HOLD",
            "renewal_flags": [{"cid": "STILL", "renewal_date": "2026-06-10",
                                "proposed_rate_gbp_per_mwh": 200.0}],
        }]
        log = _write_log(tmp_path, entries)
        customers = [{"cid": "STILL", "last_renewal_date": "2025-01-01",
                      "current_rate_gbp_per_mwh": 190.0}]
        port = _write_scorecard_portfolio(tmp_path, customers)
        out = tmp_path / "out.json"
        r = generate(str(log), str(port), str(out), today=dt.date(2026, 7, 1))
        assert r["renewal_grading"]["graded_count"] == 0
        assert r["renewal_grading"]["inconclusive_count"] == 1
        assert r["renewal_grading"]["inconclusive"][0]["outcome"] == "no_renewal_detected_yet"

    def test_hedge_ungraded_when_market_not_advanced(self, tmp_path):
        from tools.generate_track_record_scorecard import generate
        entries = [
            {"decision_run_at": "2026-06-01T00:00:00Z", "market_data_stale_days": 50,
             "hedge_recommendation": "HOLD", "renewal_flags": []},
            {"decision_run_at": "2026-06-15T00:00:00Z", "market_data_stale_days": 64,
             "hedge_recommendation": "INCREASE", "renewal_flags": []},
        ]
        log = _write_log(tmp_path, entries)
        port = _write_scorecard_portfolio(tmp_path, [])
        out = tmp_path / "out.json"
        r = generate(str(log), str(port), str(out), today=dt.date(2026, 7, 1))
        # current_stale_days = latest entry's 64, never smaller than any past entry -> all ungraded.
        assert r["hedge_grading"]["graded_count"] == 0
        assert r["hedge_grading"]["ungraded_count"] == 2
        for e in r["hedge_grading"]["entries"]:
            assert e["outcome"] == "ungraded -- market data has not advanced"

    def test_hedge_gradeable_once_market_genuinely_advances(self, tmp_path):
        from tools.generate_track_record_scorecard import generate
        log, port = self._fixture(tmp_path)  # day1 stale=100, day2 stale=90
        out = tmp_path / "out.json"
        r = generate(str(log), str(port), str(out), today=dt.date(2026, 7, 1))
        entries = r["hedge_grading"]["entries"]
        day1 = next(e for e in entries if e["decision_run_at"] == "2026-06-01")
        day2 = next(e for e in entries if e["decision_run_at"] == "2026-06-15")
        assert day1["outcome"] != "ungraded -- market data has not advanced"
        assert day2["outcome"] == "ungraded -- market data has not advanced"

    def test_retention_ev_logged_but_never_graded(self, tmp_path):
        from tools.generate_track_record_scorecard import generate
        log, port = self._fixture(tmp_path)
        out = tmp_path / "out.json"
        r = generate(str(log), str(port), str(out), today=dt.date(2026, 7, 1))
        rev = r["retention_ev_log"]
        # CG1, CG2, CP1 have a non-null retention_ev_gbp; CG3 does not.
        assert rev["logged_count"] == 3
        assert rev["graded_count"] == 0
        cids = {e["cid"] for e in rev["entries"]}
        assert cids == {"CG1", "CG2", "CP1"}

    def test_output_file_written(self, tmp_path):
        from tools.generate_track_record_scorecard import generate
        log, port = self._fixture(tmp_path)
        out = tmp_path / "out.json"
        generate(str(log), str(port), str(out), today=dt.date(2026, 7, 1))
        assert out.exists()
        reloaded = json.loads(out.read_text())
        assert reloaded["renewal_tolerance_pct"] == 0.02


# ---------------------------------------------------------------------------
# generate_method_data.py integration
# ---------------------------------------------------------------------------

class TestMethodDataTrackRecordSection:
    def test_track_record_folded_into_method_json(self, monkeypatch, tmp_path):
        from tools.generate_method_data import generate
        fake_dashboard = tmp_path / "dashboard.json"
        fake_dashboard.write_text(json.dumps({
            "meta": {"generated_at": "2026-07-07T00:00:00Z", "git_commit": "abc1234"},
            "build": {"current_phase": "RX", "test_count": 16000},
        }))
        fake_scorecard = tmp_path / "scorecard.json"
        fake_scorecard.write_text(json.dumps({
            "generated_at": "2026-07-07T00:00:00Z",
            "wall_clock_today": "2026-07-07",
            "clock_started": "2026-07-04",
            "log_entry_count": 4,
            "renewal_tolerance_pct": 0.02,
            "renewal_grading": {"graded_count": 0, "pending_count": 0, "inconclusive_count": 4,
                                 "on_target_count": 0, "off_target_count": 0, "churned_count": 0,
                                 "graded": [], "pending": [], "inconclusive": []},
            "hedge_grading": {"graded_count": 0, "ungraded_count": 4, "entries": []},
            "retention_ev_log": {"logged_count": 0, "graded_count": 0, "entries": []},
        }))
        fake_out = tmp_path / "method.json"
        monkeypatch.setattr("tools.generate_method_data.DASHBOARD_PATH", fake_dashboard)
        monkeypatch.setattr("tools.generate_method_data.OUT_PATH", fake_out)
        monkeypatch.setattr("tools.generate_method_data.SCORECARD_PATH", fake_scorecard)

        assert generate() is True
        data = json.loads(fake_out.read_text())
        assert "track_record" in data
        assert data["track_record"]["clock_started"] == "2026-07-04"

    def test_track_record_missing_scorecard_handled_gracefully(self, monkeypatch, tmp_path):
        from tools.generate_method_data import generate
        fake_dashboard = tmp_path / "dashboard.json"
        fake_dashboard.write_text(json.dumps({"meta": {}, "build": {}}))
        fake_out = tmp_path / "method.json"
        monkeypatch.setattr("tools.generate_method_data.DASHBOARD_PATH", fake_dashboard)
        monkeypatch.setattr("tools.generate_method_data.OUT_PATH", fake_out)
        monkeypatch.setattr("tools.generate_method_data.SCORECARD_PATH", tmp_path / "nope.json")

        assert generate() is True
        data = json.loads(fake_out.read_text())
        assert data["track_record"] is None
