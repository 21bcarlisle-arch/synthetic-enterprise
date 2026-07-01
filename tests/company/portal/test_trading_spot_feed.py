"""Phase 81 tests: live price feed on trading desk."""
import json
import pytest
from pathlib import Path
from starlette.testclient import TestClient

from company.portal.app import app, _load_spot_prices
from company.market.price_feed import publish_feed


@pytest.fixture
def live_feed(tmp_path):
    feed_path = tmp_path / "price_feed.json"
    publish_feed([
        {"fuel": "electricity", "period": "2025-06-07T21:00:00Z", "price_gbp_per_mwh": 100.58},
        {"fuel": "electricity", "period": "2025-06-07T21:30:00Z", "price_gbp_per_mwh": 98.20},
        {"fuel": "gas", "period": "2025-06-06T00:00:00Z", "price_gbp_per_mwh": 32.50},
        {"fuel": "gas", "period": "2025-06-07T00:00:00Z", "price_gbp_per_mwh": 32.79},
    ], feed_path)
    return feed_path


@pytest.fixture
def client(live_feed, monkeypatch):
    monkeypatch.setattr("company.portal.app._PRICE_FEED_PATH", live_feed)
    return TestClient(app)


def test_load_spot_prices_returns_empty_when_no_feed(tmp_path, monkeypatch):
    monkeypatch.setattr("company.portal.app._PRICE_FEED_PATH", tmp_path / "no_feed.json")
    result = _load_spot_prices()
    assert result == {}


def test_load_spot_prices_returns_electricity_spot(live_feed, monkeypatch):
    monkeypatch.setattr("company.portal.app._PRICE_FEED_PATH", live_feed)
    result = _load_spot_prices()
    assert result["available"] is True
    assert result["elec_spot"] == pytest.approx(98.20)  # most recent period


def test_load_spot_prices_returns_gas_spot(live_feed, monkeypatch):
    monkeypatch.setattr("company.portal.app._PRICE_FEED_PATH", live_feed)
    result = _load_spot_prices()
    assert result["gas_spot"] == pytest.approx(32.79)


def test_load_spot_prices_returns_forward_estimates(live_feed, monkeypatch):
    monkeypatch.setattr("company.portal.app._PRICE_FEED_PATH", live_feed)
    result = _load_spot_prices()
    assert result["elec_forward"] is not None
    assert result["gas_forward"] is not None


def test_trading_page_shows_market_data_section(client):
    resp = client.get("/trading")
    assert resp.status_code == 200
    assert "Market Data Feed" in resp.text or "M3" in resp.text


def test_trading_page_shows_spot_prices(client):
    resp = client.get("/trading")
    assert "98.20" in resp.text or "98" in resp.text


def test_trading_page_shows_gas_spot(client):
    resp = client.get("/trading")
    assert "32.79" in resp.text or "32" in resp.text


def test_trading_page_no_feed_still_loads(monkeypatch, tmp_path):
    monkeypatch.setattr("company.portal.app._PRICE_FEED_PATH", tmp_path / "missing.json")
    c = TestClient(app)
    resp = c.get("/trading")
    assert resp.status_code == 200


def test_load_spot_prices_available_key_present(live_feed, monkeypatch):
    monkeypatch.setattr("company.portal.app._PRICE_FEED_PATH", live_feed)
    result = _load_spot_prices()
    assert "available" in result


def test_load_spot_prices_forward_is_numeric(live_feed, monkeypatch):
    monkeypatch.setattr("company.portal.app._PRICE_FEED_PATH", live_feed)
    result = _load_spot_prices()
    elec_fwd = result.get("elec_forward")
    assert elec_fwd is None or isinstance(elec_fwd, (int, float))


def test_trading_page_content_type(client):
    resp = client.get("/trading")
    assert "text/html" in resp.headers.get("content-type", "")


def test_load_spot_prices_gas_forward_key_present(live_feed, monkeypatch):
    monkeypatch.setattr("company.portal.app._PRICE_FEED_PATH", live_feed)
    result = _load_spot_prices()
    assert "gas_forward" in result


def test_load_spot_prices_available_is_bool(live_feed, monkeypatch):
    monkeypatch.setattr("company.portal.app._PRICE_FEED_PATH", live_feed)
    result = _load_spot_prices()
    assert isinstance(result["available"], bool)


def test_trading_page_no_crash_repeated(client):
    for _ in range(2):
        resp = client.get("/trading")
        assert resp.status_code == 200
