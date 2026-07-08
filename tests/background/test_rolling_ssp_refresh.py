"""Tests for S1 Option A rolling Elexon SSP refresh (background/refresh_elexon_ssp_rolling.py)
and its merge into the live-decision market path (tools/live_market.py).

Network is never touched: every test injects a fake fetcher. The whole point of Option A's
design is that the fetch runs in the background pipeline, not here -- so what is tested is
the windowing, merge/dedup, no-op, and error-safety logic that determines the cache never
regresses or corrupts, plus that the live path picks up the extension while the historical
cache stays isolated.
"""
import datetime as dt
import json

import pytest

import background.refresh_elexon_ssp_rolling as rr


def _rec(date, period=1, price=100.0):
    return {"settlementDate": date, "settlementPeriod": period, "systemSellPrice": price}


@pytest.fixture
def rolling_path(tmp_path, monkeypatch):
    p = tmp_path / "elexon_ssp_live_rolling.json"
    monkeypatch.setattr(rr, "ROLLING_CACHE", p)
    # keep write_cached_prices pointed at tmp too (it writes under sim/cache by name)
    import sim.cache_store as cs
    monkeypatch.setattr(cs, "CACHE_DIR", tmp_path)
    return p


def test_first_run_fetches_from_day_after_boundary(rolling_path):
    """Empty rolling file -> window starts at HISTORICAL_END + 1, ends yesterday."""
    seen = {}

    def fake(start, end):
        seen["start"], seen["end"] = start, end
        return [_rec("2025-06-08"), _rec("2025-06-09")]

    r = rr.refresh(today=dt.date(2025, 6, 11), fetcher=fake)
    assert seen["start"] == "2025-06-08"  # day after 2025-06-07 boundary
    assert seen["end"] == "2025-06-10"    # yesterday (D+1 finality)
    assert r["status"] == "updated"
    assert r["fetched_records"] == 2
    assert r["new_last_covered"] == "2025-06-09"
    written = json.loads(rolling_path.read_text())
    assert {w["settlementDate"] for w in written} == {"2025-06-08", "2025-06-09"}


def test_incremental_run_starts_after_last_covered(rolling_path):
    rolling_path.write_text(json.dumps([_rec("2025-06-08"), _rec("2025-06-09")]))
    seen = {}

    def fake(start, end):
        seen["start"], seen["end"] = start, end
        return [_rec("2025-06-10")]

    r = rr.refresh(today=dt.date(2025, 6, 12), fetcher=fake)
    assert seen["start"] == "2025-06-10"  # day after last covered (06-09)
    assert seen["end"] == "2025-06-11"
    assert r["status"] == "updated"
    written = {w["settlementDate"] for w in json.loads(rolling_path.read_text())}
    assert written == {"2025-06-08", "2025-06-09", "2025-06-10"}


def test_up_to_date_is_noop(rolling_path):
    rolling_path.write_text(json.dumps([_rec("2025-06-10")]))

    def fake(start, end):  # pragma: no cover - must not be called
        raise AssertionError("fetcher should not run when already current")

    r = rr.refresh(today=dt.date(2025, 6, 11), fetcher=fake)  # yesterday == 06-10 == last covered
    assert r["status"] == "up_to_date"
    assert r["fetched_records"] == 0


def test_fetch_failure_leaves_cache_unchanged(rolling_path):
    original = [_rec("2025-06-08", price=55.5)]
    rolling_path.write_text(json.dumps(original))

    def boom(start, end):
        raise ConnectionError("no network in this environment")

    r = rr.refresh(today=dt.date(2025, 6, 20), fetcher=boom)
    assert r["status"] == "fetch_failed"
    assert json.loads(rolling_path.read_text()) == original  # untouched


def test_network_less_run_creates_no_file(rolling_path):
    """Never-run state + failing fetch must not create a corrupt/empty cache file."""
    def boom(start, end):
        raise OSError("offline")

    r = rr.refresh(today=dt.date(2025, 6, 20), fetcher=boom)
    assert r["status"] == "fetch_failed"
    assert not rolling_path.exists()


def test_empty_fetch_is_noop(rolling_path):
    r = rr.refresh(today=dt.date(2025, 6, 20), fetcher=lambda s, e: [])
    assert r["status"] == "no_new_data"
    assert not rolling_path.exists()


def test_records_at_or_before_boundary_are_discarded(rolling_path):
    """Defensive: even if the API returns rows <= 2025-06-07 they must never enter the
    rolling file (that is the historical sim's territory)."""
    def fake(start, end):
        return [_rec("2025-06-07"), _rec("2025-06-05"), _rec("2025-06-08")]

    r = rr.refresh(today=dt.date(2025, 6, 10), fetcher=fake)
    written = {w["settlementDate"] for w in json.loads(rolling_path.read_text())}
    assert written == {"2025-06-08"}
    assert r["fetched_records"] == 1


def test_refetch_corrects_existing_date(rolling_path):
    """D+1 correction: a re-fetched date replaces the prior rows for that date, not duplicates."""
    rolling_path.write_text(json.dumps([_rec("2025-06-08", period=1, price=10.0)]))

    def fake(start, end):
        # last covered is 06-08, so window is 06-09..; return a fresh 06-09 row only
        return [_rec("2025-06-09", period=1, price=20.0)]

    r = rr.refresh(today=dt.date(2025, 6, 11), fetcher=fake)
    dates = sorted(w["settlementDate"] for w in json.loads(rolling_path.read_text()))
    assert dates == ["2025-06-08", "2025-06-09"]
    assert r["status"] == "updated"


# --- live_market.py merge -------------------------------------------------------------

def test_live_market_merges_rolling_extension(tmp_path, monkeypatch):
    import tools.live_market as lm
    hist = tmp_path / "hist.json"
    roll = tmp_path / "roll.json"
    hist.write_text(json.dumps([_rec("2025-06-06", 1), _rec("2025-06-07", 1), _rec("2025-06-07", 2)]))
    roll.write_text(json.dumps([_rec("2025-06-08", 1), _rec("2025-06-09", 1)]))
    monkeypatch.setattr(lm, "SSP_CACHE", hist)
    monkeypatch.setattr(lm, "ROLLING_CACHE", roll)
    recs = lm._load_ssp_records()
    dates = sorted(set(r["settlementDate"] for r in recs))
    assert dates == ["2025-06-06", "2025-06-07", "2025-06-08", "2025-06-09"]
    # every historical settlement period preserved (two rows for 06-07)
    assert sum(1 for r in recs if r["settlementDate"] == "2025-06-07") == 2
    # _effective_as_of now advances to the newest real date
    assert lm._effective_as_of(recs, None) == "2025-06-09"


def test_live_market_absent_rolling_is_frozen_behaviour(tmp_path, monkeypatch):
    import tools.live_market as lm
    hist = tmp_path / "hist.json"
    hist.write_text(json.dumps([_rec("2025-06-07", 1)]))
    monkeypatch.setattr(lm, "SSP_CACHE", hist)
    monkeypatch.setattr(lm, "ROLLING_CACHE", tmp_path / "does_not_exist.json")
    recs = lm._load_ssp_records()
    assert {r["settlementDate"] for r in recs} == {"2025-06-07"}
    assert lm._effective_as_of(recs, None) == "2025-06-07"


def test_live_market_rolling_never_shadows_historical_dates(tmp_path, monkeypatch):
    """A stray rolling row at/before hist_max must not be merged in ahead of history."""
    import tools.live_market as lm
    hist = tmp_path / "hist.json"
    roll = tmp_path / "roll.json"
    hist.write_text(json.dumps([_rec("2025-06-07", 1, price=99.0)]))
    roll.write_text(json.dumps([_rec("2025-06-07", 1, price=1.0), _rec("2025-06-08", 1)]))
    monkeypatch.setattr(lm, "SSP_CACHE", hist)
    monkeypatch.setattr(lm, "ROLLING_CACHE", roll)
    recs = lm._load_ssp_records()
    # the 06-07 row stays the historical one (price 99), the stray rolling 06-07 is dropped
    by_date_0607 = [r for r in recs if r["settlementDate"] == "2025-06-07"]
    assert len(by_date_0607) == 1
    assert by_date_0607[0]["systemSellPrice"] == 99.0
    assert any(r["settlementDate"] == "2025-06-08" for r in recs)
