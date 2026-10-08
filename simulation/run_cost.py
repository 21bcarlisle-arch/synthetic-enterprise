"""One line per simulation run: what it cost, against how much book it settled.

WHY THIS EXISTS (director, 2026-10-08, the run review): *"why none of this surfaced sooner, and
what would make this kind of gap surface on its own in future."* No run had ever been profiled, and
nothing recorded a run's cost against its size, so a run that got slower or heavier per customer
looked exactly like a run that got bigger. Every run through `simulation.run_phase2b.main` now
appends one JSON line; the Monday review (`background.weekly_rhythm`) reads the week's lines and
flags a move in seconds or megabytes per settled leg-year.

WHAT A "LEG-YEAR" IS, said before it is divided by. One settled record is one customer-leg-day
(a dual-fuel home is two legs), so `len(all_records) / 365.25` is settled leg-years. The peak is the
process's own `ru_maxrss` plus its children's (forked trace workers), so `mb_per_leg_year` carries
the run's fixed base inside it and is comparable only between runs of similar size. The review
compares like with like for that reason.

WHERE IT WRITES. The main checkout's untracked `sim/cache/run_cost_log.jsonl`
(`sim.cache_store.shared_cache_dir`), so runs started in any worktree land in one log, and nothing
is committed. A test process never writes (`live_ledger_guard.in_test_process`). A failed write is
reported and never raised: the run's result matters more than its cost line.
"""
from __future__ import annotations

import json
import os
import resource
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG_NAME = "run_cost_log.jsonl"


def log_path() -> Path:
    from sim.cache_store import shared_cache_dir
    return shared_cache_dir() / LOG_NAME


def _sha() -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                             text=True, timeout=10, cwd=Path(__file__).resolve().parent)
        return out.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def cost_line(result: dict, *, wall_s: float, report_end: str | None) -> dict:
    """The line for one finished run. Pure apart from reading this process's rusage and git."""
    records = (result or {}).get("all_records") or []
    leg_years = len(records) / 365.25
    self_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    child_mb = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024
    accounts = len({r.get("customer_id") for r in records if hasattr(r, "get")})
    return {
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sha": _sha(),
        "cwd": os.getcwd(),
        "argv": sys.argv[:6],
        "report_end": report_end,
        "accounts": accounts,
        "settled_leg_years": round(leg_years, 1),
        "wall_s": round(wall_s, 1),
        "peak_self_mb": round(self_mb, 1),
        "peak_children_max_mb": round(child_mb, 1),
        "s_per_leg_year": round(wall_s / leg_years, 3) if leg_years else None,
        "mb_per_leg_year": round(self_mb / leg_years, 3) if leg_years else None,
        "fork_workers": os.environ.get("SE_FORK_WORKERS") or "default",
    }


def record(result: dict, *, wall_s: float, report_end: str | None, path: Path | None = None) -> None:
    from background.live_ledger_guard import in_test_process
    if path is None and in_test_process():
        return
    try:
        line = cost_line(result, wall_s=wall_s, report_end=report_end)
        target = path or log_path()
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(line) + "\n")
    except Exception as exc:  # noqa: BLE001 -- see the docstring: never fail a run over its cost line
        print(f"run cost line NOT written: {type(exc).__name__}: {exc}", file=sys.stderr)


def read(days: float = 7.0, path: Path | None = None, now: datetime | None = None) -> list[dict]:
    target = path or log_path()
    if not target.exists():
        return []
    now = now or datetime.now(timezone.utc)
    out = []
    for raw in target.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(raw)
            at = datetime.fromisoformat(row["at"])
        except (ValueError, KeyError, TypeError):
            continue
        if (now - at).total_seconds() <= days * 86400:
            out.append(row)
    return out


#: A WEEK'S MEDIAN COST PER LEG-YEAR THAT MOVES BY MORE THAN THIS AGAINST THE WEEK BEFORE is named
#: in the review. Not a domain constant: it decides what the seat is asked to explain, nothing more.
DRIFT_SHARE = 0.25


def render(days: float = 7.0, path: Path | None = None, now: datetime | None = None) -> str:
    """The Monday table: this week's runs by size, and a drift line against the week before."""
    import statistics
    rows = read(days, path, now)
    prior = [r for r in read(2 * days, path, now) if r not in rows]
    if not rows:
        return ("NO RUNS RECORDED this week. Either nothing ran through `run_phase2b.main`, or the "
                "cost line is not being written -- the second is a defect, so check "
                f"`{log_path()}` exists.")
    lines = ["| at | sha | accounts | leg-years | wall s | peak MB | s / leg-yr | MB / leg-yr |",
             "|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: r["at"])[-20:]:
        lines.append("| {at} | {sha} | {accounts} | {settled_leg_years} | {wall_s} | "
                     "{peak_self_mb} | {s_per_leg_year} | {mb_per_leg_year} |".format(**r))
    for key in ("s_per_leg_year", "mb_per_leg_year"):
        now_vals = [r[key] for r in rows if r.get(key)]
        then_vals = [r[key] for r in prior if r.get(key)]
        if now_vals and then_vals:
            a, b = statistics.median(now_vals), statistics.median(then_vals)
            moved = (a - b) / b if b else 0.0
            flag = " **MOVED -- explain it or fix it**" if abs(moved) > DRIFT_SHARE else ""
            lines.append(f"\n{key}: median {a:.3f} this week against {b:.3f} the week before "
                         f"({moved:+.0%}){flag}")
    return "\n".join(lines)
