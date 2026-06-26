"""Tests for dashboard insights extraction -- Phase 258."""
import json
import pytest
from pathlib import Path
from tools.generate_dashboard_data import extract_insights

_SAMPLE_INSIGHTS = {
    "git_hash": "abc1234",
    "generated_at": "2026-06-26T13:00:00+00:00",
    "net_margin_gbp": 6322835.71,
    "executive_summary": "Business survived.",
    "insights": [
        {"area": "trading", "headline": "Hedging cost GBP4M", "narrative": "...", "key_metrics": {}},
        {"area": "customers", "headline": "445 shocks", "narrative": "...", "key_metrics": {}},
        {"area": "risk", "headline": "38 interventions", "narrative": "...", "key_metrics": {}},
        {"area": "financial", "headline": "Net margin GBP6.3M", "narrative": "...", "key_metrics": {}},
        {"area": "operations", "headline": "1531 bills", "narrative": "...", "key_metrics": {}},
    ],
}


def test_extract_insights_returns_none_when_missing(tmp_path):
    result = extract_insights(tmp_path / "nonexistent.json")
    assert result is None


def test_extract_insights_returns_data_when_present(tmp_path):
    p = tmp_path / "run_insights.json"
    p.write_text(json.dumps(_SAMPLE_INSIGHTS))
    result = extract_insights(p)
    assert result is not None
    assert result["git_hash"] == "abc1234"
    assert len(result["insights"]) == 5


def test_extract_insights_returns_none_on_invalid_json(tmp_path):
    p = tmp_path / "run_insights.json"
    p.write_text("not valid json {{{{")
    result = extract_insights(p)
    assert result is None


def test_extract_insights_includes_all_areas(tmp_path):
    p = tmp_path / "run_insights.json"
    p.write_text(json.dumps(_SAMPLE_INSIGHTS))
    result = extract_insights(p)
    areas = {i["area"] for i in result["insights"]}
    assert "trading" in areas
    assert "financial" in areas
    assert "customers" in areas
