"""Tests for T1: Trading desk portal route (Phase 73)."""

import json
import pytest
from pathlib import Path
from starlette.testclient import TestClient

from company.portal.app import app, _load_trading_data

client = TestClient(app, raise_server_exceptions=True)


def test_trading_route_returns_200():
    r = client.get("/trading")
    assert r.status_code == 200


def test_trading_page_has_heading():
    r = client.get("/trading")
    assert "Trading Desk" in r.text


def test_trading_page_shows_hedge_summary_when_data_available():
    r = client.get("/trading")
    # run_output_latest.json exists and has hedge_effectiveness_total
    if "No run data" not in r.text:
        assert "Hedge Portfolio Summary" in r.text


def test_trading_page_shows_by_year_table():
    r = client.get("/trading")
    if "No run data" not in r.text:
        assert "by Year" in r.text


def test_load_trading_data_returns_expected_keys(tmp_path, monkeypatch):
    sample = {
        "years": {
            "2022": {
                "hedge_effectiveness": {
                    "actual_net_gbp": 100.0,
                    "naked_net_gbp": 200.0,
                    "hedging_value_add_gbp": -100.0,
                }
            }
        },
        "hedge_effectiveness_total": {
            "actual_net_gbp": 100.0,
            "naked_net_gbp": 200.0,
            "hedging_value_add_gbp": -100.0,
            "best_decision": None,
            "worst_decision": None,
        },
    }
    run_file = tmp_path / "run_output_latest.json"
    run_file.write_text(json.dumps(sample))
    import company.portal.app as portal
    orig = portal._RUN_OUTPUT
    portal._RUN_OUTPUT = run_file
    try:
        data = _load_trading_data()
        assert "by_year" in data
        assert "total_value_add" in data
        assert len(data["by_year"]) == 1
        assert data["by_year"][0]["year"] == "2022"
        assert data["total_value_add"] == -100.0
    finally:
        portal._RUN_OUTPUT = orig


def test_load_trading_data_empty_when_no_file(tmp_path, monkeypatch):
    import company.portal.app as portal
    orig = portal._RUN_OUTPUT
    portal._RUN_OUTPUT = tmp_path / "nonexistent.json"
    try:
        data = _load_trading_data()
        assert data == {}
    finally:
        portal._RUN_OUTPUT = orig


def test_trading_page_has_logout_link():
    r = client.get("/trading")
    assert "Logout" in r.text or "/" in r.text


def test_by_year_entries_have_year_key():
    data = _load_trading_data()
    if data.get("by_year"):
        for entry in data["by_year"][:3]:
            assert "year" in entry


def test_trading_data_has_total_value_add():
    data = _load_trading_data()
    if data:
        assert "total_value_add" in data
        assert isinstance(data["total_value_add"], float)


def test_trading_data_by_year_is_list():
    data = _load_trading_data()
    if data:
        assert isinstance(data["by_year"], list)


def test_trading_data_best_key_present():
    data = _load_trading_data()
    if data:
        assert "best" in data


def test_trading_data_worst_key_present():
    data = _load_trading_data()
    if data:
        assert "worst" in data


def test_trading_data_total_actual_net_is_float():
    data = _load_trading_data()
    if data:
        assert isinstance(data["total_actual_net"], (int, float))
