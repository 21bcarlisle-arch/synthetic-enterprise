import json
from pathlib import Path
from unittest.mock import patch


def _decision(run_at, hedge_rec="HOLD"):
    return {
        "decision_run_at": run_at,
        "portfolio_as_of": "2025-06-01T12:00:00Z",
        "market_as_of_date": "2025-06-07",
        "elec_spot_gbp_per_mwh": 70.0,
        "gas_spot_gbp_per_mwh": 32.0,
        "elec_12m_forward_gbp_per_mwh": 73.5,
        "gas_12m_forward_gbp_per_mwh": 33.6,
        "treasury_gbp": 3_000_000.0,
        "active_customers": 2,
        "hedge_recommendation": hedge_rec,
        "hedge_affected_customers": [],
        "renewal_window_days": 60,
        "renewal_flags": [],
        "acquisition_prices": {},
    }


_STUB_MARKET = {
    "as_of_date": "2025-06-07", "elec_spot_gbp_per_mwh": 70.0,
    "gas_spot_gbp_per_mwh": 32.0, "elec_12m_forward_gbp_per_mwh": 73.5,
    "gas_12m_forward_gbp_per_mwh": 33.6,
}


def _write_portfolio(tmp_path):
    p = {"generated_at": "2025-06-01T12:00:00Z", "source_year": 2025,
         "treasury_gbp": 3_000_000.0, "active_customer_count": 1,
         "customers": [{"cid": "C1", "commodity": "electricity", "segment": "resi",
                         "current_rate_gbp_per_mwh": 220.0, "hedge_fraction": 0.7,
                         "next_renewal_estimate": "2025-09-01", "eac_kwh_per_year": 10000.0,
                         "last_renewal_date": "2024-09-01", "net_gbp_2025": 200.0}]}
    f = tmp_path / "portfolio.json"
    f.write_text(json.dumps(p))
    return f


class TestAppendDecisionLog:
    def test_first_entry_creates_log(self, tmp_path):
        from tools.run_live_decisions import append_decision_log
        log_path = tmp_path / "log.jsonl"
        wrote = append_decision_log(_decision("2026-07-04T10:00:00Z"), log_path)
        assert wrote is True
        assert log_path.exists()
        lines = log_path.read_text().splitlines()
        assert len(lines) == 1
        assert json.loads(lines[0])["decision_run_at"] == "2026-07-04T10:00:00Z"

    def test_same_day_second_call_does_not_duplicate(self, tmp_path):
        from tools.run_live_decisions import append_decision_log
        log_path = tmp_path / "log.jsonl"
        append_decision_log(_decision("2026-07-04T10:00:00Z", "HOLD"), log_path)
        wrote_again = append_decision_log(_decision("2026-07-04T15:30:00Z", "INCREASE"), log_path)
        assert wrote_again is False
        lines = log_path.read_text().splitlines()
        assert len(lines) == 1

    def test_first_of_day_prediction_is_locked(self, tmp_path):
        from tools.run_live_decisions import append_decision_log
        log_path = tmp_path / "log.jsonl"
        append_decision_log(_decision("2026-07-04T10:00:00Z", "HOLD"), log_path)
        append_decision_log(_decision("2026-07-04T15:30:00Z", "INCREASE"), log_path)
        entry = json.loads(log_path.read_text().splitlines()[0])
        assert entry["hedge_recommendation"] == "HOLD"

    def test_new_day_appends_second_entry(self, tmp_path):
        from tools.run_live_decisions import append_decision_log
        log_path = tmp_path / "log.jsonl"
        append_decision_log(_decision("2026-07-04T10:00:00Z"), log_path)
        wrote = append_decision_log(_decision("2026-07-05T09:00:00Z"), log_path)
        assert wrote is True
        lines = log_path.read_text().splitlines()
        assert len(lines) == 2

    def test_log_entries_are_valid_jsonl(self, tmp_path):
        from tools.run_live_decisions import append_decision_log
        log_path = tmp_path / "log.jsonl"
        append_decision_log(_decision("2026-07-04T10:00:00Z"), log_path)
        append_decision_log(_decision("2026-07-05T09:00:00Z"), log_path)
        for line in log_path.read_text().splitlines():
            parsed = json.loads(line)
            assert "decision_run_at" in parsed


class TestRunDecisionsWritesLog:
    def test_run_decisions_appends_to_log(self, tmp_path):
        from tools.run_live_decisions import run_decisions
        pf = _write_portfolio(tmp_path)
        with patch("tools.live_market.get_market_summary", return_value=_STUB_MARKET):
            run_decisions(str(pf), out_dir=str(tmp_path))
        log_path = tmp_path / "live_decisions_log.jsonl"
        assert log_path.exists()
        entry = json.loads(log_path.read_text().splitlines()[0])
        assert entry["hedge_recommendation"] in ("HOLD", "INCREASE", "REDUCE")

    def test_run_decisions_twice_same_day_keeps_one_log_entry(self, tmp_path):
        from tools.run_live_decisions import run_decisions
        pf = _write_portfolio(tmp_path)
        with patch("tools.live_market.get_market_summary", return_value=_STUB_MARKET):
            run_decisions(str(pf), out_dir=str(tmp_path))
            run_decisions(str(pf), out_dir=str(tmp_path))
        log_path = tmp_path / "live_decisions_log.jsonl"
        assert len(log_path.read_text().splitlines()) == 1
