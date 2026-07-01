"""Phase 80 tests: market price feed publication."""
import json
import pytest
from pathlib import Path

from simulation.publish_market_feed import build_feed_prices, publish, SSP_CACHE, NBP_CSV
from company.market.price_feed import PriceFeed


def test_build_feed_prices_returns_nonempty():
    prices = build_feed_prices(n_elec_periods=4, n_gas_days=2)
    assert len(prices) > 0


def test_build_feed_prices_contains_electricity():
    prices = build_feed_prices(n_elec_periods=4, n_gas_days=0)
    fuels = {p["fuel"] for p in prices}
    assert "electricity" in fuels


def test_build_feed_prices_contains_gas():
    prices = build_feed_prices(n_elec_periods=0, n_gas_days=2)
    fuels = {p["fuel"] for p in prices}
    assert "gas" in fuels


def test_build_feed_prices_elec_count_matches_request():
    prices = build_feed_prices(n_elec_periods=6, n_gas_days=0)
    elec = [p for p in prices if p["fuel"] == "electricity"]
    assert len(elec) == 6


def test_build_feed_prices_gas_count_matches_request():
    prices = build_feed_prices(n_elec_periods=0, n_gas_days=3)
    gas = [p for p in prices if p["fuel"] == "gas"]
    assert len(gas) == 3


def test_build_feed_prices_elec_has_valid_price():
    prices = build_feed_prices(n_elec_periods=4, n_gas_days=0)
    elec = [p for p in prices if p["fuel"] == "electricity"]
    for p in elec:
        assert p["price_gbp_per_mwh"] > 0
        assert p["period"]  # non-empty period


def test_build_feed_prices_gas_has_valid_price():
    prices = build_feed_prices(n_elec_periods=0, n_gas_days=2)
    gas_prices = [p for p in prices if p["fuel"] == "gas"]
    for p in gas_prices:
        assert p["price_gbp_per_mwh"] > 0


def test_publish_creates_feed_file(tmp_path):
    output = tmp_path / "test_feed.json"
    publish(output)
    assert output.exists()


def test_publish_creates_valid_json(tmp_path):
    output = tmp_path / "test_feed.json"
    publish(output)
    data = json.loads(output.read_text())
    assert "published_at" in data
    assert "prices" in data
    assert len(data["prices"]) > 0


def test_published_feed_readable_by_price_feed_class(tmp_path):
    output = tmp_path / "price_feed.json"
    publish(output)
    feed = PriceFeed(output)
    assert feed.is_available()
    latest = feed.get_latest_spot("electricity")
    assert latest is not None and latest > 0


def test_published_feed_gas_readable(tmp_path):
    output = tmp_path / "price_feed.json"
    publish(output)
    feed = PriceFeed(output)
    latest_gas = feed.get_latest_spot("gas")
    assert latest_gas is not None and latest_gas > 0


def test_build_feed_prices_returns_list():
    prices = build_feed_prices(n_elec_periods=2, n_gas_days=1)
    assert isinstance(prices, list)


def test_build_feed_prices_elec_has_period_field():
    prices = build_feed_prices(n_elec_periods=2, n_gas_days=0)
    elec = [p for p in prices if p["fuel"] == "electricity"]
    for p in elec:
        assert "period" in p


def test_build_feed_mixed_elec_and_gas():
    prices = build_feed_prices(n_elec_periods=3, n_gas_days=2)
    fuels = [p["fuel"] for p in prices]
    assert fuels.count("electricity") == 3
    assert fuels.count("gas") == 2
