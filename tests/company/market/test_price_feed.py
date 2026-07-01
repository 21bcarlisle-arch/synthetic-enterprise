"""Tests for M3: Market data feed (Phase 76)."""

import json
import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path
import tempfile

from company.market.price_feed import PriceFeed, SpotPrice, publish_feed


def _write_feed(tmp_path: Path, prices: list[dict], published_at: str) -> Path:
    feed_path = tmp_path / "price_feed.json"
    payload = {"published_at": published_at, "prices": prices}
    feed_path.write_text(json.dumps(payload))
    return feed_path


def _recent_ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stale_ts() -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()


def test_feed_not_available_when_missing(tmp_path):
    feed = PriceFeed(tmp_path / "nonexistent.json")
    assert feed.is_available() is False


def test_feed_available_when_file_exists(tmp_path):
    prices = [{"fuel": "electricity", "period": "2022-01-01T00:00:00", "price_gbp_per_mwh": 50.0}]
    path = _write_feed(tmp_path, prices, _recent_ts())
    feed = PriceFeed(path)
    assert feed.is_available() is True


def test_feed_returns_spot_prices(tmp_path):
    prices = [
        {"fuel": "electricity", "period": "2022-01-01T00:00:00", "price_gbp_per_mwh": 50.0},
        {"fuel": "electricity", "period": "2022-01-01T00:30:00", "price_gbp_per_mwh": 55.0},
        {"fuel": "gas", "period": "2022-01-01T00:00:00", "price_gbp_per_mwh": 30.0},
    ]
    path = _write_feed(tmp_path, prices, _recent_ts())
    feed = PriceFeed(path)
    elec = feed.spot_prices("electricity")
    assert len(elec) == 2
    assert all(isinstance(p, SpotPrice) for p in elec)


def test_get_latest_spot(tmp_path):
    prices = [
        {"fuel": "electricity", "period": "2022-01-01T00:00:00", "price_gbp_per_mwh": 50.0},
        {"fuel": "electricity", "period": "2022-01-01T00:30:00", "price_gbp_per_mwh": 60.0},
    ]
    path = _write_feed(tmp_path, prices, _recent_ts())
    feed = PriceFeed(path)
    assert feed.get_latest_spot("electricity") == pytest.approx(60.0)


def test_latest_spot_none_when_file_missing(tmp_path):
    feed = PriceFeed(tmp_path / "nope.json")
    assert feed.get_latest_spot("electricity") is None


def test_forward_price_estimate(tmp_path):
    prices = [
        {"fuel": "electricity", "period": f"2022-01-01T{i:02d}:00:00", "price_gbp_per_mwh": 100.0}
        for i in range(10)
    ]
    path = _write_feed(tmp_path, prices, _recent_ts())
    feed = PriceFeed(path)
    est = feed.get_forward_price_estimate("electricity", premium_pct=5.0)
    assert est == pytest.approx(105.0)


def test_feed_stale_when_old(tmp_path):
    prices = [{"fuel": "electricity", "period": "2022-01-01T00:00:00", "price_gbp_per_mwh": 50.0}]
    path = _write_feed(tmp_path, prices, _stale_ts())
    feed = PriceFeed(path)
    assert feed.is_stale(max_age_hours=24) is True


def test_feed_not_stale_when_recent(tmp_path):
    prices = [{"fuel": "electricity", "period": "2022-01-01T00:00:00", "price_gbp_per_mwh": 50.0}]
    path = _write_feed(tmp_path, prices, _recent_ts())
    feed = PriceFeed(path)
    assert feed.is_stale(max_age_hours=24) is False


def test_publish_feed_writes_json(tmp_path):
    output = tmp_path / "feed.json"
    prices = [{"fuel": "electricity", "period": "2022-01-01T00:00:00", "price_gbp_per_mwh": 80.0}]
    publish_feed(prices, output, published_at="2022-01-01T12:00:00+00:00")
    data = json.loads(output.read_text())
    assert data["published_at"] == "2022-01-01T12:00:00+00:00"
    assert len(data["prices"]) == 1
    assert data["prices"][0]["price_gbp_per_mwh"] == 80.0


def test_summary_structure(tmp_path):
    prices = [
        {"fuel": "electricity", "period": "2022-01-01T00:00:00", "price_gbp_per_mwh": 50.0},
        {"fuel": "gas", "period": "2022-01-01T00:00:00", "price_gbp_per_mwh": 30.0},
    ]
    path = _write_feed(tmp_path, prices, _recent_ts())
    feed = PriceFeed(path)
    s = feed.summary()
    required = {"published_at", "electricity_price_count", "gas_price_count",
                "latest_electricity_period", "latest_electricity_spot",
                "forward_estimate_electricity"}
    assert set(s.keys()) == required
    assert s["electricity_price_count"] == 1
    assert s["gas_price_count"] == 1


# --- Phase LC depth tests ---

def test_spot_price_fuel_stored(tmp_path):
    prices = [{"fuel": "electricity", "period": "2022-01-01T00:00:00Z", "price_gbp_per_mwh": 100.0}]
    feed_path = _write_feed(tmp_path, prices, _recent_ts())
    feed = PriceFeed(feed_path)
    spots = feed.spot_prices("electricity")
    assert spots[0].fuel == "electricity"


def test_spot_price_period_stored(tmp_path):
    prices = [{"fuel": "electricity", "period": "2022-06-01T00:00:00Z", "price_gbp_per_mwh": 100.0}]
    feed_path = _write_feed(tmp_path, prices, _recent_ts())
    feed = PriceFeed(feed_path)
    spots = feed.spot_prices("electricity")
    assert spots[0].period == "2022-06-01T00:00:00Z"


def test_spot_price_price_stored(tmp_path):
    prices = [{"fuel": "electricity", "period": "2022-01-01T00:00:00Z", "price_gbp_per_mwh": 85.5}]
    feed_path = _write_feed(tmp_path, prices, _recent_ts())
    feed = PriceFeed(feed_path)
    spots = feed.spot_prices("electricity")
    assert spots[0].price_gbp_per_mwh == pytest.approx(85.5)


def test_feed_available_is_bool(tmp_path):
    feed = PriceFeed(tmp_path / "missing.json")
    assert isinstance(feed.is_available(), bool)


def test_spot_prices_empty_when_no_matching_fuel(tmp_path):
    prices = [{"fuel": "electricity", "period": "2022-01-01T00:00:00Z", "price_gbp_per_mwh": 100.0}]
    feed_path = _write_feed(tmp_path, prices, _recent_ts())
    feed = PriceFeed(feed_path)
    assert feed.spot_prices("gas") == []


def test_spot_prices_returns_list(tmp_path):
    prices = [{"fuel": "electricity", "period": "2022-01-01T00:00:00Z", "price_gbp_per_mwh": 100.0}]
    feed_path = _write_feed(tmp_path, prices, _recent_ts())
    feed = PriceFeed(feed_path)
    assert isinstance(feed.spot_prices("electricity"), list)


def test_latest_spot_is_float(tmp_path):
    prices = [{"fuel": "electricity", "period": "2022-01-01T00:00:00Z", "price_gbp_per_mwh": 100.0}]
    feed_path = _write_feed(tmp_path, prices, _recent_ts())
    feed = PriceFeed(feed_path)
    result = feed.get_latest_spot("electricity")
    assert isinstance(result, float)


def test_multiple_prices_latest_is_last(tmp_path):
    prices = [
        {"fuel": "electricity", "period": "2022-01-01T00:00:00Z", "price_gbp_per_mwh": 80.0},
        {"fuel": "electricity", "period": "2022-01-02T00:00:00Z", "price_gbp_per_mwh": 90.0},
    ]
    feed_path = _write_feed(tmp_path, prices, _recent_ts())
    feed = PriceFeed(feed_path)
    assert feed.get_latest_spot("electricity") == pytest.approx(90.0)


def test_is_stale_type(tmp_path):
    prices = [{"fuel": "electricity", "period": "2022-01-01T00:00:00Z", "price_gbp_per_mwh": 100.0}]
    feed_path = _write_feed(tmp_path, prices, _recent_ts())
    feed = PriceFeed(feed_path)
    assert isinstance(feed.is_stale(), bool)


def test_feed_max_age_constant():
    from company.market.price_feed import FEED_MAX_AGE_HOURS
    assert FEED_MAX_AGE_HOURS == 24
