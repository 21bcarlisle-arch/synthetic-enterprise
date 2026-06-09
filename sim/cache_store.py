"""Lightweight file cache for pre-fetched API data.

Background tasks (background/run_queued_tasks.py) pre-fetch expensive Elexon
and weather API calls and store them here. The simulation pipeline checks this
cache before hitting live APIs, so background work amortizes fetch costs and
main-pipeline runs complete faster.

Cache entries are plain JSON files — no binary format dependencies.
"""

import json
from pathlib import Path

CACHE_DIR = Path("sim/cache")


def get_cached_prices(start_date: str, end_date: str) -> list[dict] | None:
    """Return cached SSP records covering start_date..end_date, or None on cache miss.

    The cache file (elexon_ssp_full.json) must cover the entire requested range.
    If it exists but is a partial range, a None is returned so the caller falls
    back to the live API — no partial-cache serving.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / "elexon_ssp_full.json"
    if not cache_file.exists():
        return None
    records = json.loads(cache_file.read_text())
    if not records:
        return None
    # Check that the cache actually covers the requested range
    dates = [r["settlementDate"] for r in records]
    if min(dates) > start_date or max(dates) < end_date:
        return None
    return [r for r in records if start_date <= r["settlementDate"] <= end_date]


def write_cached_prices(records: list[dict], cache_file_name: str = "elexon_ssp_full.json") -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (CACHE_DIR / cache_file_name).write_text(json.dumps(records))


def log_cache_access(file_name: str, hit: bool, phase: str, task_name: str = "") -> None:
    """Append a cache hit/miss entry to docs/observability/token-log.md."""
    log_path = Path("docs/observability/token-log.md")
    if not log_path.exists():
        return
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if hit:
        entry = f"\n- [{ts}] cache_hit: {file_name} — background task {task_name} consumed by Phase {phase}"
    else:
        entry = f"\n- [{ts}] cache_miss: {file_name} — fetched live (Phase {phase})"
    with open(log_path, "a") as f:
        f.write(entry)
