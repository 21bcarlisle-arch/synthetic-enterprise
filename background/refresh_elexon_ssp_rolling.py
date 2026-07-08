"""Rolling forward-refresh of real Elexon settlement prices past the sim's frozen boundary.

S1 Option A (docs/staging/S1_SHADOW_LIVE_TRACK_RECORD_DESIGN.md, unblocked by Rich in
docs/staging/S1_OPTION_A_UNBLOCKED.md: Elexon's Insights Solution publishes indicative
settlement prices ~15 min after each settlement period with a D+1 accuracy refresh, via
the public no-API-key endpoints already wrapped by sim.system_prices_history).

WHY A SEPARATE FILE. The historical cache sim/cache/elexon_ssp_full.json bounds the
simulation's fixed 2015-11-07..2025-06-07 decade and is read by run_phase2b.py, the
dashboards, and the Sim-tab generators. This job must NEVER perturb any of that. So it
writes to its OWN file, sim/cache/elexon_ssp_live_rolling.json, covering strictly-after
dates only; tools/live_market.py merges the two views for the LIVE decision path alone
(get_market_summary / _effective_as_of pick up the extended latest date automatically).
Deleting this file, or removing the process_run_complete.py hook, fully reverts to the
frozen-cache behaviour -- an additive, reversible extension, not a data-model change.

WHY IT IS SAFE TO DEPLOY UNVERIFIED. The fetch itself cannot be exercised from an
autonomous Claude Code turn (no network in that sandbox -- the advisor's explicit reason
for putting the fetch in the background pipeline, where network exists). This job is
therefore written to be defensive: any fetch/parse failure, or a network-less run, leaves
the rolling file exactly as it was and returns a status dict rather than raising -- worst
case is identical to today's frozen behaviour, it can never corrupt the cache or break the
pipeline. The success signal, once it does fetch, is self-evident and public: the Method
scorecard's market_data_stale_days drops below its frozen 396 and hedge grading unlocks.

ELECTRICITY ONLY. Elexon settlement prices are electricity. Gas (NBP) needs its own live
source; until one is wired, live_market.py keeps deriving gas as it does today and the
scorecard labels it frozen. Stated honestly rather than blocked (per S1_OPTION_A_UNBLOCKED).
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
ROLLING_CACHE = PROJECT / "sim" / "cache" / "elexon_ssp_live_rolling.json"
LOG_PATH = PROJECT / "docs" / "observability" / "background-worker-log.md"

# The sim's fixed historical boundary (simulation/run_phase2b.py REPORT_END,
# background/prefetch_elexon_ssp.py FETCH_END). The rolling window starts the day AFTER
# this and never re-touches the historical decade.
HISTORICAL_END = "2025-06-07"


def _log(msg: str) -> None:
    try:
        ts = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with open(LOG_PATH, "a") as f:
            f.write(f"\n- [{ts}] refresh_elexon_ssp_rolling: {msg}")
    except Exception:
        pass


def _load_rolling() -> list[dict]:
    try:
        recs = json.loads(ROLLING_CACHE.read_text())
        return recs if isinstance(recs, list) else []
    except Exception:
        return []


def _last_covered_date(rolling_records: list[dict]) -> str:
    """Latest settlementDate already in the rolling file, or the historical boundary if
    the file is empty -- so the first ever run starts fetching at HISTORICAL_END + 1 day."""
    dates = [r.get("settlementDate") for r in rolling_records if r.get("settlementDate")]
    return max(dates) if dates else HISTORICAL_END


def refresh(today=None, fetcher=None):
    """Fetch real settlement prices for (last_covered, yesterday] and append to the rolling
    cache. Pure w.r.t. network failure: on any error the file is left untouched.

    Args:
        today: UTC date to treat as "today" (defaults to real wall-clock UTC). Settlement
            data for today is not yet final, so the fetch window ends at today - 1 (D+1).
        fetcher: callable(start_iso, end_iso) -> list[dict], injectable for tests.
            Defaults to the same proven sim.system_prices_history.get_system_prices_range
            that built the historical cache.

    Returns a status dict (never raises) describing what happened.
    """
    today = today or dt.datetime.now(dt.timezone.utc).date()
    end_date = today - dt.timedelta(days=1)  # settlement data is final at D+1

    existing = _load_rolling()
    last_covered = _last_covered_date(existing)
    start_date = dt.date.fromisoformat(last_covered) + dt.timedelta(days=1)

    if start_date > end_date:
        _log(f"already current (last_covered={last_covered}, target_end={end_date.isoformat()}) -- no fetch")
        return {"status": "up_to_date", "last_covered": last_covered,
                "target_end": end_date.isoformat(), "fetched_records": 0}

    if fetcher is None:
        from sim.system_prices_history import get_system_prices_range as fetcher

    start_iso, end_iso = start_date.isoformat(), end_date.isoformat()
    try:
        fetched = fetcher(start_iso, end_iso) or []
    except Exception as exc:  # network-less run, API change, timeout -- leave cache intact
        _log(f"fetch failed ({start_iso}..{end_iso}): {exc!r} -- rolling cache left unchanged")
        return {"status": "fetch_failed", "error": repr(exc),
                "window": [start_iso, end_iso], "fetched_records": 0}

    # Defensive: keep only records strictly after the historical boundary, so this file can
    # never shadow or duplicate a historical date even if the API returns extra rows.
    fresh = [r for r in fetched if r.get("settlementDate", "") > HISTORICAL_END]
    if not fresh:
        _log(f"fetch returned no post-boundary records ({start_iso}..{end_iso}) -- unchanged")
        return {"status": "no_new_data", "window": [start_iso, end_iso], "fetched_records": 0}

    # Merge: drop any existing rows for the dates we just re-fetched (D+1 corrections win),
    # then append. Records are per settlement-period, so we key the drop on settlementDate.
    refetched_dates = {r["settlementDate"] for r in fresh}
    merged = [r for r in existing if r.get("settlementDate") not in refetched_dates] + fresh
    merged.sort(key=lambda r: (r.get("settlementDate", ""), r.get("settlementPeriod", 0)))

    try:
        from sim.cache_store import write_cached_prices
        write_cached_prices(merged, "elexon_ssp_live_rolling.json")
    except Exception as exc:
        _log(f"write failed: {exc!r} -- rolling cache left unchanged")
        return {"status": "write_failed", "error": repr(exc), "fetched_records": len(fresh)}

    new_last = max(r["settlementDate"] for r in fresh)
    _log(f"appended {len(fresh)} records for {start_iso}..{end_iso}; rolling now covers "
         f"{HISTORICAL_END}+1..{new_last} ({len(merged)} total)")
    return {"status": "updated", "window": [start_iso, end_iso],
            "fetched_records": len(fresh), "new_last_covered": new_last,
            "total_rolling_records": len(merged)}


if __name__ == "__main__":
    r = refresh()
    print("status:", r["status"])
    for k in ("window", "fetched_records", "new_last_covered", "total_rolling_records", "error"):
        if k in r:
            print(f"  {k}: {r[k]}")
