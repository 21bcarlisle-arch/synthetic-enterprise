"""Lightweight file cache for pre-fetched API data.

Pre-fetched Elexon and weather API calls are stored here (the Qwen task queue
that first filled it, background/run_queued_tasks.py, was retired 2026-09-27). The simulation pipeline checks this
cache before hitting live APIs, so background work amortizes fetch costs and
main-pipeline runs complete faster.

Cache entries are plain JSON files — no binary format dependencies.
"""

import json
from pathlib import Path


def shared_cache_dir(module_file: str | Path = __file__) -> Path:
    """`sim/cache` of the MAIN checkout, whichever worktree or working folder the run starts in.

    IT WAS `Path("sim/cache")`, RELATIVE TO THE PROCESS'S WORKING FOLDER, and the cache is untracked,
    so a run started in a linked worktree found no cache and re-downloaded every Elexon system price
    mid-run (30 s of a 331 s 40-founder run, profiled 2026-10-08). Before `SystemPricesFetchError`
    existed (2026-10-07), a throttled download returned fewer records silently: seven runs logged
    143,881-167,978 records against the 168,026 the cache holds for 2015-11-07..2025-06-07, so they
    ran on a different world. One shared copy means every run reads the same frozen prices.

    A linked worktree's `.git` is a FILE naming `<main>/.git/worktrees/<name>`; the main checkout is
    three levels above that. Read as text, no subprocess. Anything else (the main checkout itself,
    or a layout git did not write) resolves to this module's own repository, never the working
    folder.
    """
    root = Path(module_file).resolve().parent.parent
    marker = root / ".git"
    if marker.is_file():
        line = marker.read_text(encoding="utf-8").strip()
        if line.startswith("gitdir:"):
            gitdir = Path(line.split(":", 1)[1].strip())
            if not gitdir.is_absolute():
                gitdir = (root / gitdir).resolve()
            if gitdir.parent.name == "worktrees" and gitdir.parent.parent.name == ".git":
                return gitdir.parent.parent.parent / "sim" / "cache"
    return root / "sim" / "cache"


CACHE_DIR = shared_cache_dir()


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
    # A TEST PROCESS MAY NOT APPEND TO THE LIVE TOKEN LOG (2026-08-31). This is called on every
    # cache read, so any test that touches the cache appended a line to
    # `docs/observability/token-log.md` -- the ledger `tools/activity_cost` parses to attribute
    # frontier-token spend by session. **10 of the 16 refusals remaining after the writer fixes
    # were this one call**, in tests that were not about caching at all.
    #
    # BOTH HALVES OF THE PREDICATE, which the first draft of the sibling guards got wrong: what
    # must not happen is a test process writing a LIVE record, not a test process writing at all.
    # A test that redirects this path and asserts the append still works.
    #
    # A NO-OP, not a raise: this function's own contract is that it never disturbs a cache read --
    # it already returns silently when the log is absent -- so a refusal here would break that
    # promise to protect a diary.
    from background.live_ledger_guard import in_test_process, is_live_record_path

    if in_test_process() and is_live_record_path(log_path):
        return
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if hit:
        entry = f"\n- [{ts}] cache_hit: {file_name} — background task {task_name} consumed by Phase {phase}"
    else:
        entry = f"\n- [{ts}] cache_miss: {file_name} — fetched live (Phase {phase})"
    with open(log_path, "a") as f:
        f.write(entry)
