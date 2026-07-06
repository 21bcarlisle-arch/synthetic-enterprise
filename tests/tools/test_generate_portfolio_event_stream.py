"""Tests for tools/generate_portfolio_event_stream.py --
SUPPLIER_TAB_OVERHAUL.md THE SPINE: patches the real (non-shadow) dashboard.json
with the portfolio-wide decision event stream that company/analytics/
decision_event_ledger.build_portfolio_event_stream already produces."""
import json
import sys
from pathlib import Path as _P

sys.path.insert(0, str(_P(__file__).resolve().parents[2]))

import tools.generate_portfolio_event_stream as gpes


def test_generate_returns_zero_when_billing_ledger_missing(tmp_path, monkeypatch):
    run_json = tmp_path / "run.json"
    run_json.write_text(json.dumps({}))
    dashboard = tmp_path / "dashboard.json"
    dashboard.write_text(json.dumps({"customers": {}}))
    monkeypatch.setattr(gpes, "LEDGER_PATH", tmp_path / "no_such_ledger.json")
    monkeypatch.setattr(gpes, "DASHBOARD_PATH", dashboard)
    assert gpes.generate(str(run_json)) == 0


def test_generate_returns_zero_when_dashboard_missing(tmp_path, monkeypatch):
    run_json = tmp_path / "run.json"
    run_json.write_text(json.dumps({}))
    ledger = tmp_path / "billing_ledger.json"
    ledger.write_text(json.dumps({"customers": {}}))
    monkeypatch.setattr(gpes, "LEDGER_PATH", ledger)
    monkeypatch.setattr(gpes, "DASHBOARD_PATH", tmp_path / "no_such_dashboard.json")
    assert gpes.generate(str(run_json)) == 0


def test_generate_patches_stream_onto_dashboard(tmp_path, monkeypatch):
    run_json = tmp_path / "run.json"
    run_json.write_text(json.dumps({
        "customer_events": [{
            "customer_id": "C1", "event_date": "2020-01-01", "event_type": "renewed",
        }],
        "retention_log": [{
            "customer_id": "C1", "event_date": "2019-12-01",
            "company_churn_estimate": 0.3, "discount_pct": 0.1,
            "retention_cost_gbp": 50.0, "expected_term_margin_gbp": 300.0,
            "outcome": "retained",
        }],
        "churn_journey_log": [],
    }))
    ledger = tmp_path / "billing_ledger.json"
    ledger.write_text(json.dumps({"customers": {"C1": {"arrears_history": []}}}))
    dashboard = tmp_path / "dashboard.json"
    dashboard.write_text(json.dumps({"customers": {"events": []}, "financial": {}}))

    monkeypatch.setattr(gpes, "LEDGER_PATH", ledger)
    monkeypatch.setattr(gpes, "DASHBOARD_PATH", dashboard)

    count = gpes.generate(str(run_json))
    assert count == 2  # retention_decision + outcome_renewed

    written = json.loads(dashboard.read_text())
    stream = written["customers"]["portfolio_event_stream"]
    assert len(stream) == 2
    assert all(e["customer_id"] == "C1" for e in stream)
    # financial key untouched by the patch
    assert written["financial"] == {}


def test_generate_respects_limit_via_underlying_builder(tmp_path, monkeypatch):
    retention_log = [
        {"customer_id": "C{}".format(i), "event_date": "2020-01-0{}".format(i % 9 + 1),
         "company_churn_estimate": 0.2, "discount_pct": 0.1,
         "retention_cost_gbp": 10.0, "expected_term_margin_gbp": 100.0,
         "outcome": "retained"}
        for i in range(1, 6)
    ]
    run_json = tmp_path / "run.json"
    run_json.write_text(json.dumps({
        "customer_events": [], "retention_log": retention_log, "churn_journey_log": [],
    }))
    ledger = tmp_path / "billing_ledger.json"
    ledger.write_text(json.dumps({"customers": {}}))
    dashboard = tmp_path / "dashboard.json"
    dashboard.write_text(json.dumps({"customers": {}}))

    monkeypatch.setattr(gpes, "LEDGER_PATH", ledger)
    monkeypatch.setattr(gpes, "DASHBOARD_PATH", dashboard)

    count = gpes.generate(str(run_json))
    assert count == 5
