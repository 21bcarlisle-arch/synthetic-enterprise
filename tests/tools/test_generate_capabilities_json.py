"""Tests for tools/generate_capabilities_json.py.

Coverage for PROJECT_TAB_OVERHAUL.md item 6: capability cards must generate a
headline number from the latest run's dashboard.json rather than carrying a
hand-written, frozen-at-writing-time statistic.
"""
import json

from tools.generate_capabilities_json import (
    CAPABILITIES,
    _settlement_engine_metric,
    _customer_model_metric,
    _churn_model_metric,
    _regulatory_metric,
    _carbon_metric,
    generate,
    OUT_PATH,
    DASHBOARD_PATH,
)


def test_settlement_engine_metric_formats_bill_count_and_window():
    d = {"portfolio": {"bills_total": 1605}, "build": {"simulation_window": "2016-2025"}}
    assert _settlement_engine_metric(d) == "1,605 bills settled over 2016-2025"


def test_settlement_engine_metric_none_when_field_missing():
    assert _settlement_engine_metric({}) is None


def test_customer_model_metric_sums_elec_and_gas_from_latest_year():
    d = {"customers": {"book_annual": [
        {"year": 2024, "active_elec": 9, "active_gas": 1},
        {"year": 2025, "active_elec": 10, "active_gas": 1},
    ]}}
    assert _customer_model_metric(d) == "11 active customer accounts (2025)"


def test_churn_model_metric_formats_recall_precision_f1():
    d = {"churn_model_performance": {"recall": 0.5, "precision": 0.25, "f1_score": 0.333}}
    assert _churn_model_metric(d) == "recall 50%, precision 25%, F1 33% (live run)"


def test_regulatory_metric_counts_green_obligations():
    d = {"regulatory": {"obligations": [
        {"status": "GREEN"}, {"status": "GREEN"}, {"status": "AMBER"},
    ]}}
    assert _regulatory_metric(d) == "3 obligations tracked, 2 GREEN"


def test_carbon_metric_honestly_returns_none_no_source_field():
    assert _carbon_metric({}) is None
    assert _carbon_metric({"regulatory": {"obligations": []}}) is None


def test_registry_ids_are_unique():
    ids = [c["id"] for c in CAPABILITIES]
    assert len(ids) == len(set(ids))


def test_registry_every_entry_has_evidence_link_and_description():
    for cap in CAPABILITIES:
        assert cap["evidence_link"]
        assert cap["description"]
        assert cap["name"]


def test_generate_writes_json_with_one_card_per_registry_entry(tmp_path, monkeypatch):
    fake_dashboard = tmp_path / "dashboard.json"
    fake_dashboard.write_text(json.dumps({
        "meta": {"generated_at": "2026-07-06T00:00:00Z", "git_commit": "abc1234"},
        "build": {"current_phase": "ZZ"},
        "portfolio": {"bills_total": 10},
    }))
    fake_out = tmp_path / "capabilities.json"
    monkeypatch.setattr("tools.generate_capabilities_json.DASHBOARD_PATH", fake_dashboard)
    monkeypatch.setattr("tools.generate_capabilities_json.OUT_PATH", fake_out)

    assert generate() is True
    data = json.loads(fake_out.read_text())
    assert data["git_commit"] == "abc1234"
    assert data["phase"] == "ZZ"
    assert len(data["cards"]) == len(CAPABILITIES)
    settlement = next(c for c in data["cards"] if c["id"] == "settlement-engine")
    assert settlement["headline"] == "10 bills settled"


def test_generate_handles_missing_dashboard_gracefully(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.generate_capabilities_json.DASHBOARD_PATH", tmp_path / "nope.json")
    monkeypatch.setattr("tools.generate_capabilities_json.OUT_PATH", tmp_path / "out.json")
    assert generate() is True
    data = json.loads((tmp_path / "out.json").read_text())
    assert all(c["headline"] is None for c in data["cards"])
