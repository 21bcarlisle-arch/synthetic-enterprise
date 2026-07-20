"""Independence + fail-closed tests for tools/generate_market_data.py (R15).

The World door's intra-day movement must be DERIVED from the real settlement
price feed (docs/market_data/price_feed.json), never a relocated hardcode.
These tests prove derivation by mutating an injected price series and asserting
the emitted movement follows it, and prove the fail-closed contract (R15
FAIL-OPEN killer pattern): a missing/malformed feed must emit `available: false`,
never a zeroed session that looks the same as a real one.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT))
sys.path.insert(0, str(PROJECT / "tools"))

import generate_market_data as G  # noqa: E402


def _pt(period: str, price: float) -> dict:
    return {"fuel": "electricity", "period": period, "price_gbp_per_mwh": price}


def _series(prices: list[float]) -> list[dict]:
    return [_pt(f"2025-06-07T{h:02d}:00:00Z", p) for h, p in enumerate(prices)]


def test_series_summary_derives_movement():
    pts = _series([100.0, 120.0, 80.0, 110.0])
    s = G._series_summary(pts, "£/MWh", keep_tail=24)
    assert s["latest_price"] == 110.0
    assert s["session_open"] == 100.0
    assert s["session_high"] == 120.0
    assert s["session_low"] == 80.0
    assert s["last_change_gbp"] == 30.0          # 110 - 80
    assert s["session_range"] == 40.0            # 120 - 80
    assert s["as_of_period"] == "2025-06-07T03:00:00Z"
    assert s["point_count"] == 4


def test_series_summary_follows_a_mutated_price():
    # R15 independence: change the last price; every downstream derived field
    # that depends on it must move -- proving computation, not a hardcode.
    base = G._series_summary(_series([100.0, 120.0, 80.0, 110.0]), "£/MWh", 24)
    mutated = G._series_summary(_series([100.0, 120.0, 80.0, 300.0]), "£/MWh", 24)
    assert base["latest_price"] != mutated["latest_price"]
    assert mutated["latest_price"] == 300.0
    assert mutated["session_high"] == 300.0      # new high follows the price
    assert mutated["last_change_gbp"] == 220.0   # 300 - 80


def test_series_summary_sorts_by_period():
    # Out-of-order input must not break "latest" -- it sorts by period first.
    pts = [_pt("2025-06-07T02:00:00Z", 90.0), _pt("2025-06-07T00:00:00Z", 50.0),
           _pt("2025-06-07T01:00:00Z", 70.0)]
    s = G._series_summary(pts, "£/MWh", 24)
    assert s["session_open"] == 50.0
    assert s["latest_price"] == 90.0


def test_series_summary_fail_closed_on_empty():
    assert G._series_summary([], "£/MWh", 24) is None
    # a row with no usable price is not a data point
    assert G._series_summary([{"period": "2025-06-07T00:00:00Z"}], "£/MWh", 24) is None


def test_generate_fail_closed_on_missing_feed(tmp_path, monkeypatch):
    # R15 FAIL-OPEN killer: a missing feed emits available:false, not zeros.
    monkeypatch.setattr(G, "FEED_PATH", tmp_path / "does_not_exist.json")
    monkeypatch.setattr(G, "OUT_PATH", tmp_path / "market.json")
    data = G.generate()
    assert data["available"] is False
    assert "electricity" not in data or data.get("electricity") is None
    written = json.loads((tmp_path / "market.json").read_text())
    assert written["available"] is False


def test_generate_carries_clock_and_frontier(tmp_path, monkeypatch):
    # R14: the emitted electricity block carries its unit + as-of period, and the
    # settlement_frontier equals the electricity as-of (the lag reference date).
    # Uses an INJECTED feed (not the live one, which a background daemon rewrites
    # and which degrades to gas-only in a worktree lacking the SSP cache) so the
    # test is deterministic -- controlled input, R15.
    feed = {
        "published_at": "2026-07-17T11:07:42Z",
        "prices": [
            {"fuel": "electricity", "period": f"2025-06-07T{h:02d}:00:00Z", "price_gbp_per_mwh": 100.0 + h}
            for h in range(6)
        ] + [{"fuel": "gas", "period": "2025-06-07T00:00:00Z", "price_gbp_per_mwh": 32.79}],
    }
    fp = tmp_path / "price_feed.json"
    fp.write_text(json.dumps(feed))
    monkeypatch.setattr(G, "FEED_PATH", fp)
    monkeypatch.setattr(G, "OUT_PATH", tmp_path / "market.json")
    data = G.generate()
    assert data["available"] is True
    e = data["electricity"]
    assert e["unit"] == "£/MWh"
    assert e["as_of_period"] == data["settlement_frontier"] == "2025-06-07T05:00:00Z"
    # published_at (feed clock) and as_of (frontier) must differ -- that IS the lag.
    assert data["published_at"][:7] != e["as_of_period"][:7]


def test_generate_fail_closed_when_feed_has_no_electricity(tmp_path, monkeypatch):
    # Robustness finding, made a test: the real feed's electricity points come
    # from the gitignored SSP cache; when that is absent the producer emits a
    # gas-only feed. The intra-day electricity panel must then fail closed
    # (available:false), not fabricate a session.
    feed = {"published_at": "2026-07-20T00:00:00Z",
            "prices": [{"fuel": "gas", "period": "2025-06-07T00:00:00Z", "price_gbp_per_mwh": 32.79}]}
    fp = tmp_path / "price_feed.json"
    fp.write_text(json.dumps(feed))
    monkeypatch.setattr(G, "FEED_PATH", fp)
    monkeypatch.setattr(G, "OUT_PATH", tmp_path / "market.json")
    data = G.generate()
    assert data["available"] is False
    assert data["electricity"] is None
