"""Where a long background job says what it is doing, so a reader outside can tell.

REUSE: background/long_job.py
CLASS: CUSTOM
INDEX: searched "background task", "job status", "heartbeat", "progress", "long running".
       `docs/observability/background-task-*.md` is the existing convention and it records
       COMPLETED tasks -- "Completed: ... Wall time: 0.3s" -- so a job that is still going, or one
       that died halfway, writes nothing at all and is indistinguishable from one that never
       started. `background/resource_headroom.py` samples the machine, not the work.
       `docs/observability/.seat_heartbeat.json` is the seat's own liveness, not a job's.

WHY THIS EXISTS
---------------
Director, 2026-09-08: *"I can't tell from outside whether it finished, is running, or died -- a
long background job produces no commits, so all three look the same to me."*

He was right, and it had already cost something. A 600-file weather pull ran for hours, failed 240
of them, and exited. The committed receipt still said `pull_status: complete, failed: 0` from a
PREVIOUS run, because the receipt was opt-in and that run had not asked for one. So the artefact a
reader would consult did not merely omit the failure -- **it asserted the opposite.**

THE ONE THING THIS HAS TO GET RIGHT
------------------------------------
"Finished" and "running" are easy: the job says so. **"Died" is the hard state, because a dead job
says nothing at all** -- and a status file that only records what a job tells it can never
represent the case where the job stopped being able to tell it anything.

So death is inferred, not reported: a job that is STILL MARKED RUNNING and whose heartbeat has gone
stale is dead. That is why every record carries `updated_at` and an expected `heartbeat_seconds`,
and why `read()` computes the verdict rather than trusting the stored state. A status file without
that comparison is a file that reports every crash as work in progress.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

from background.live_ledger_guard import guard_live_ledger_write

PROJECT = Path(__file__).resolve().parent.parent
STATUS_PATH = PROJECT / "docs" / "observability" / "long_jobs.json"

#: How many heartbeat intervals may be missed before a running job is called dead. Two is a
#: compromise: one would call a job dead every time the machine hesitated, and ten would make the
#: verdict useless on any job that matters.
STALE_INTERVALS = 2.0


def _load() -> dict:
    if not STATUS_PATH.is_file():
        return {"jobs": {}}
    try:
        return json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return {"jobs": {}}


def heartbeat(name: str, *, done: int, total: int | None = None, state: str = "running",
              note: str = "", heartbeat_seconds: float = 120.0,
              failed: int = 0) -> dict:
    """Record where a job has got to. Called repeatedly while it runs, once when it stops.

    WRITES EVERY TIME rather than on a change: the value of the record is its FRESHNESS, and a
    writer that skips an unchanged update is a writer that makes a stalled job look dead and a
    dead job look stalled.
    """
    payload = _load()
    payload.setdefault("jobs", {})[name] = {
        "state": state,
        "done": int(done),
        "total": int(total) if total is not None else None,
        "failed": int(failed),
        "note": note[:300],
        "pid": os.getpid(),
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "updated_epoch": int(time.time()),
        "heartbeat_seconds": float(heartbeat_seconds),
    }
    STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    guard_live_ledger_write(STATUS_PATH, writer="long_job.heartbeat").write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return payload["jobs"][name]


def verdict(record: dict, *, now: float | None = None) -> str:
    """finished / failed / running / DIED — and the last is inferred, never reported.

    A job cannot tell anyone it has died. The only evidence is a record that still claims to be
    running while its heartbeat has stopped, so that comparison is the whole point of this module.
    """
    state = record.get("state", "unknown")
    if state in ("finished", "failed"):
        return state
    interval = float(record.get("heartbeat_seconds") or 120.0)
    age = (now if now is not None else time.time()) - float(record.get("updated_epoch") or 0)
    return "died" if age > interval * STALE_INTERVALS else "running"


def read() -> list[dict]:
    """Every job with its computed verdict and how stale its heartbeat is."""
    now = time.time()
    out = []
    for name, record in sorted(_load().get("jobs", {}).items()):
        row = dict(record)
        row["name"] = name
        row["verdict"] = verdict(record, now=now)
        row["age_seconds"] = int(now - float(record.get("updated_epoch") or 0))
        out.append(row)
    return out


def render() -> str:
    rows = read()
    if not rows:
        return "no long jobs recorded"
    width = max(len(r["name"]) for r in rows)
    lines = []
    for r in rows:
        total = r.get("total")
        progress = f"{r['done']}/{total}" if total else str(r["done"])
        failed = f"  {r['failed']} failed" if r.get("failed") else ""
        age = r["age_seconds"]
        stamp = f"{age}s ago" if age < 3600 else f"{age // 3600}h{(age % 3600) // 60:02d}m ago"
        lines.append(f"{r['name']:<{width}}  {r['verdict'].upper():<8} {progress:>10}"
                     f"{failed}   {stamp}   {r.get('note','')[:60]}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    print(render())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
