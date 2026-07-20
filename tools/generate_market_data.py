#!/usr/bin/env python3
"""Generate site/data/market.json -- the intra-day wholesale market feed for the
World door's operational window (Door 5 "World state" panel).

WHY (director, 2026-07-20): "the annual-mean SSP is too coarse for an operational
window -- I need to see what the market is DOING, not its average. Wire the real
intra-day feed into the site pipeline properly rather than inventing one."

SOURCE (real, not invented): docs/market_data/price_feed.json --
  {published_at, prices:[{fuel, period, price_gbp_per_mwh}]}. The electricity
  points are the real half-hourly intra-day wholesale series ending at the
  settlement frontier; gas is the daily NBP-style series over the same window.
  This generator READS that feed and DERIVES the movement (latest, trajectory,
  session range/min/max, last change). It authors no price -- the site is a
  rendering, never an author (SITE_CONSTITUTION).

CLOCKS (R14, binding): every figure carries its clock. The wholesale price is on
  the WHOLESALE / observed intra-day clock, and its AS-OF is the latest half-hour
  PERIOD in the feed (~2025-06-07, the settlement frontier) -- NOT published_at
  (2026-07-17). That gap between "published now" and "as-of the frontier" IS the
  settlement lag the World door makes legible (weather is realised months ahead
  of the settled books). No figure appears without its £/MWh unit + as-of period.

R12: the movement is a DIAGNOSTIC of what the market is doing, never a target.
No number is fabricated; a missing/empty feed yields available=False, not zeros
dressed as data (fail-closed, R15).
"""
import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
FEED_PATH = PROJECT / "docs" / "market_data" / "price_feed.json"
OUT_PATH = PROJECT / "site" / "data" / "market.json"


def _load(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return None


def _round(x, n=2):
    return round(float(x), n) if isinstance(x, (int, float)) else None


def _series_summary(points, unit, keep_tail):
    """Derive the movement metrics for one fuel's sorted price series.

    points: list of {period, price_gbp_per_mwh} already sorted ascending by period.
    Returns None if there is no usable data (fail-closed -- an empty feed is not
    a zeroed session)."""
    rows = [
        p for p in points
        if isinstance(p.get("price_gbp_per_mwh"), (int, float)) and p.get("period")
    ]
    rows.sort(key=lambda p: p["period"])
    if not rows:
        return None
    prices = [float(p["price_gbp_per_mwh"]) for p in rows]
    hi = max(prices)
    lo = min(prices)
    hi_period = rows[prices.index(hi)]["period"]
    lo_period = rows[prices.index(lo)]["period"]
    latest = prices[-1]
    prev = prices[-2] if len(prices) > 1 else None
    change = (latest - prev) if prev is not None else None
    change_pct = (100 * change / prev) if (change is not None and prev) else None
    # A compact recent trajectory for the sparkline (last keep_tail points).
    tail = rows[-keep_tail:]
    trajectory = [
        dict(period=p["period"], price=_round(p["price_gbp_per_mwh"]))
        for p in tail
    ]
    return dict(
        unit=unit,
        # AS-OF is the latest PERIOD in the feed -- the settlement-frontier clock,
        # not the publish time. This is the lag the World door makes visible.
        as_of_period=rows[-1]["period"],
        first_period=rows[0]["period"],
        point_count=len(rows),
        latest_price=_round(latest),
        session_open=_round(prices[0]),
        session_close=_round(latest),
        session_high=_round(hi),
        session_high_period=hi_period,
        session_low=_round(lo),
        session_low_period=lo_period,
        session_mean=_round(sum(prices) / len(prices)),
        session_range=_round(hi - lo),
        last_change_gbp=_round(change),
        last_change_pct=_round(change_pct),
        trajectory=trajectory,
    )


def generate():
    feed = _load(FEED_PATH)
    if not isinstance(feed, dict) or not isinstance(feed.get("prices"), list):
        # Fail-closed: no invented session (R15 -- a control/producer must not
        # pass on missing/empty input).
        data = dict(
            generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            available=False,
            note="price_feed.json missing or malformed -- no intra-day session to render.",
            evidence="docs/market_data/price_feed.json",
            evidence_url="../data/market.json",
        )
        OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUT_PATH.write_text(json.dumps(data, separators=(",", ":")))
        print("Written (unavailable): " + str(OUT_PATH))
        return data

    prices = feed["prices"]
    elec = [p for p in prices if p.get("fuel") == "electricity"]
    gas = [p for p in prices if p.get("fuel") == "gas"]

    electricity = _series_summary(elec, "£/MWh", keep_tail=24)
    gas_summary = _series_summary(gas, "£/MWh", keep_tail=10)

    data = dict(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        available=electricity is not None,
        # The feed's own publish time -- kept so the site can show BOTH the publish
        # clock and the as-of clock, making the settlement lag legible.
        published_at=feed.get("published_at"),
        # The settlement frontier the intra-day session ends at (== electricity
        # as-of period), surfaced as a first-class field for the World door's lag
        # computation.
        settlement_frontier=(electricity or {}).get("as_of_period"),
        basis="Real half-hourly wholesale electricity + daily gas from the settlement "
              "feed. Prices are £/MWh on the wholesale/observed clock; AS-OF is the "
              "latest feed period (the settlement frontier), not the publish time. "
              "R14 clock carried per figure; R12: movement is a diagnostic, never a target.",
        electricity=electricity,
        gas=gas_summary,
        evidence="docs/market_data/price_feed.json (published_at "
                 + str(feed.get("published_at")) + ")",
        evidence_url="../data/market.json",
    )
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, separators=(",", ":")))
    print("Written: " + str(OUT_PATH))
    return data


if __name__ == "__main__":
    generate()
