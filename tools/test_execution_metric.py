"""Cumulative tests EXECUTED metric (2026-07-10, director page comment on
/project/: "Don't we want cumulative tests run, not the growth in the
standard test set. A genuinely different, arguably more impressive metric").

No historical execution-count log exists to derive this retroactively, and
fabricating a historical total would violate the Anchored-noise/R-A
no-fabrication rule -- so this is forward-only instrumentation, starting
from whenever it first runs. `tests/conftest.py::pytest_sessionfinish`
appends one line to TEST_EXECUTION_LOG per real pytest session (full suite
or a partial/targeted run -- deliberately every invocation counts, not just
full-suite runs, since the point of this metric is continuous verification
activity over the project's history, not suite size).
"""
from __future__ import annotations

import datetime
import json
import os
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
TEST_EXECUTION_LOG = PROJECT_DIR / "docs" / "observability" / "test_execution_log.jsonl"


def count_executed_tests(stats: dict) -> int:
    """Total real test executions (pass+fail+error+skip+xfail+xpass) from a
    pytest TerminalReporter's `.stats` dict."""
    return sum(
        len(stats.get(key, []))
        for key in ("passed", "failed", "error", "skipped", "xfailed", "xpassed")
    )


def record_execution(stats: dict, log_path: Path | None = None) -> None:
    """Append one execution record if any tests actually ran. No-ops on a
    zero-test session (e.g. a collection-only invocation)."""
    executed = count_executed_tests(stats)
    if executed == 0:
        return
    path = log_path or TEST_EXECUTION_LOG
    record = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "test_count": executed,
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(record) + "\n")


def cumulative_tests_executed(log_path: Path | None = None) -> dict:
    """Read TEST_EXECUTION_LOG and return the running total plus honesty
    metadata. Returns zero/None fields (never fabricated) if the log is
    missing or empty."""
    path = log_path or TEST_EXECUTION_LOG
    if not path.exists():
        return {"cumulative_total": 0, "since": None, "session_count": 0}

    total = 0
    since = None
    session_count = 0
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            tc = rec.get("test_count", 0)
            # The cumulative-EXECUTED total is this atom's own
            # (G1_test_progression_metrics) MONOTONIC, non-saturating
            # guarantee -- it must never decrease and must never crash the
            # phases.json generation that publishes it to the live Project
            # tab. The log is a shared, appended-to on-disk surface
            # (concurrent writers, per CLAUDE.md), so a single corrupted or
            # hand-fudged line can carry a negative, string, or null
            # test_count. Unguarded, a negative would make the running total
            # go DOWN (FAIL-OPEN, R15 killer pattern 2) and a non-int would
            # raise a TypeError on `total += tc` that wedges the whole site
            # publish. Treat any non-int (bool is not a count) or negative
            # value as malformed and skip the record entirely -- exactly as a
            # malformed LINE is skipped above -- contributing nothing rather
            # than a monotonicity-breaking or fabricated number
            # (Anchored-noise/no-fabrication rule).
            if not isinstance(tc, int) or isinstance(tc, bool) or tc < 0:
                continue
            total += tc
            session_count += 1
            ts = rec.get("timestamp")
            if ts and (since is None or ts < since):
                since = ts

    return {"cumulative_total": total, "since": since, "session_count": session_count}
