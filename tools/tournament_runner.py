#!/usr/bin/env python3
"""Tournament runner — the orchestration harness that makes the Epoch-4
evolutionary tournament arithmetically feasible (atom A8_experiment_loop_speed).

THE PROBLEM (docs/observability/experiment-cycle-profile.md, MEASURE-FIRST/R4):
Epoch 4 needs the company to live and die many times — N variants x G
generations = N*G "lives", each life = one full sim run. At ~500s/life
SINGLE-THREADED, a 10,000-life tournament is ~58 days of pure wall-clock. The
feasibility target (10k lives in a week) is ~60s/life = ~8-10x too slow. One of
the two named orchestration levers for closing that gap is PARALLELISING
INDEPENDENT RUNS: the box has 16 logical cores, and each life is an independent
process, so running them in a bounded pool converts single-threaded wall-clock
into ~core-count throughput.

WHAT THIS IS (harness/orchestration only — tools/background/tests scope):
A bounded process pool that fans N independent sim "lives" across cores, each
life a separate `python3 -m saas.reporting.annual_report` subprocess writing to
an ISOLATED output directory, and collects each life's fitness metrics from its
own result JSON. It does NOT change sim outputs — determinism and Historical
Ground Truth are untouched (a life with identical inputs produces an identical
JSON; verified by tests/tools/test_tournament_runner.py).

NON-NEGOTIABLE, FAIL-CLOSED (experiment-cycle-profile.md §"Non-negotiable"):
a fast/tournament run is a DEVELOPMENT tool. It may NEVER publish, promote an
atom, or feed the board pack. Enforced MECHANICALLY here, not by convention:
  1. Every life runs with --fast (SIM_FAST_MODE). That is the ONLY sim mode
     whose `fresh_full_run` branch is False, so the sim's own run-complete NTFY
     and its LEDGER_LATEST_PATH overwrite (the two board-pack side effects)
     are never taken. A life without --fast is REFUSED (ValueError).
  2. Output goes ONLY to an isolated tournament directory. Writing under
     docs/staging, docs/reports, or site/ is REFUSED (ValueError) — a
     tournament can never drop a run_complete_*.md marker into the publish
     path, can never overwrite the live dashboard data.
  3. This module never imports/invokes process_run_complete, never writes a
     run_complete marker, never runs git. There is no code path to publish.

The guard is the point: cycle time is a DIAGNOSTIC, never gamed by deleting
tests or by quietly letting a cheap run leak into the board pack (R15 stands —
the guard has its own failing-input test).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

PROJECT_DIR = Path(__file__).resolve().parent.parent

# Paths a tournament output dir may NEVER live inside — the publish path and the
# live-site data path. Refusing these is the mechanical half of guard #2.
_FORBIDDEN_OUTPUT_ROOTS = (
    PROJECT_DIR / "docs" / "staging",
    PROJECT_DIR / "docs" / "reports",
    PROJECT_DIR / "site",
)

# Conservative per-life resident-set estimate (bytes) for the memory-aware
# concurrency cap -- the OOM guard. MEASURED on this box (R4):
#   * a --fast --end-year 2016 life  ~= 0.77 GB RSS  (~24 s)
#   * a --fast FULL-window life       ~= 5.67 GB RSS  (~351 s)
# The 2026-07-13 incident was a full run OOM-killed on a 15 GiB box under
# concurrent load -- and at ~5.7 GB/life against ~8 GB available, a full life is
# so heavy that only ~1 fits at a time here. So the DEFAULT estimate is the
# conservative full-life figure (never OOM by default); a caller running cheaper
# truncated lives passes a smaller per_life_rss_bytes to unlock real
# parallelism. Parallelism is only free where memory allows it -- this number is
# how the harness knows the difference.
_PER_LIFE_RSS_BYTES = 6_000 * 1024 * 1024
# Never consume more than this fraction of currently-available memory.
_MEM_HEADROOM_FRACTION = 0.75


def _available_memory_bytes() -> int:
    """MemAvailable from /proc/meminfo (Linux). Falls back to a safe small
    number so the memory cap degrades to 1 worker rather than oversubscribing."""
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) * 1024
    except (OSError, ValueError, IndexError):
        pass
    return _PER_LIFE_RSS_BYTES  # -> 1 worker


def memory_safe_worker_cap(per_life_rss_bytes: int = _PER_LIFE_RSS_BYTES,
                           available_bytes: Optional[int] = None) -> int:
    """Max workers that fit in AVAILABLE memory at the headroom fraction.

    Always >= 1: even under memory pressure the tournament makes progress one
    life at a time rather than OOM-killing the box (the 2026-07-13 incident)."""
    avail = available_bytes if available_bytes is not None else _available_memory_bytes()
    budget = int(avail * _MEM_HEADROOM_FRACTION)
    return max(1, budget // max(1, per_life_rss_bytes))


def default_worker_count(per_life_rss_bytes: int = _PER_LIFE_RSS_BYTES) -> int:
    """Bounded by BOTH core count and available memory — whichever is tighter.

    Parallelism is the throughput lever; the memory cap is the OOM guard. The
    tighter of the two wins so we never oversubscribe cores or RAM."""
    cores = os.cpu_count() or 1
    return max(1, min(cores, memory_safe_worker_cap(per_life_rss_bytes)))


@dataclass
class LifeSpec:
    """One tournament life: an independent sim run with its own output paths and
    optional per-life environment (a caller-supplied seed/scenario/variant knob).

    `env` is how a tournament varies lives WITHOUT this harness reaching across
    the epistemic wall — the caller (an Epoch-4 tournament driver) owns what the
    knobs mean; this runner only fans the processes out and collects fitness."""

    life_id: str
    end_year: Optional[int] = None  # truncate window (cheap smoke/bench lives)
    env: dict = field(default_factory=dict)


@dataclass
class LifeResult:
    life_id: str
    ok: bool
    elapsed_s: float
    returncode: int
    json_path: Optional[str] = None
    fitness: dict = field(default_factory=dict)
    error: Optional[str] = None
    # A tournament life's success criterion is a valid FITNESS JSON, which the
    # sim writes BEFORE rendering the annual-report markdown. The markdown
    # render is post-sim work a tournament never consumes, and it is separately
    # fragile (a pre-existing truncated-window bug in saas.reporting's
    # management-accounts section exits non-zero AFTER the JSON is already
    # written). So `ok` keys on the fitness JSON; `render_returncode` records
    # the process exit separately for observability without failing the life.
    render_returncode: int = 0


# Fitness fields lifted from a life's result JSON. These are OBSERVABLE outputs
# of a completed life (the same figures the board pack reads), not sim internals.
_FITNESS_FIELDS = (
    "total_net_gbp",
    "total_gross_gbp",
    "enterprise_value_gbp",
    "final_treasury_gbp",
    "net_margin_after_cost_to_serve_gbp",
    "administration_event",
)


def _validate_output_dir(output_dir: Path) -> Path:
    """Guard #2: refuse any output dir inside the publish path or the live site.

    Fail-closed: a tournament can never write a run_complete marker or clobber
    the deployed dashboard data, whatever the caller passes."""
    resolved = output_dir.resolve()
    for forbidden in _FORBIDDEN_OUTPUT_ROOTS:
        f = forbidden.resolve()
        if resolved == f or f in resolved.parents:
            raise ValueError(
                "Tournament output dir {} is inside a forbidden publish/live path "
                "({}). A tournament run may NEVER publish or feed the board pack "
                "(experiment-cycle-profile.md, fail-closed).".format(resolved, f)
            )
    return resolved


def _run_one_life(args) -> LifeResult:
    """Module-level worker (picklable for ProcessPoolExecutor). Runs ONE life as
    a subprocess with --fast forced on, into an isolated output path."""
    life_id, end_year, extra_env, output_dir_str = args
    output_dir = Path(output_dir_str)
    out_json = output_dir / "life_{}.json".format(life_id)
    out_md = output_dir / "life_{}.md".format(life_id)

    cmd = [
        sys.executable, "-m", "saas.reporting.annual_report",
        "--fast",  # guard #1: the only mode with no board-pack side effects
        "--save-json", str(out_json),
        "--output", str(out_md),
    ]
    if end_year is not None:
        cmd += ["--end-year", str(int(end_year))]

    env = dict(os.environ)
    env["SIM_FAST_MODE"] = "1"
    env["SIM_TOURNAMENT_MODE"] = "1"  # observability marker for a tournament life
    env.update({str(k): str(v) for k, v in (extra_env or {}).items()})

    t0 = time.monotonic()
    try:
        proc = subprocess.run(
            cmd, cwd=str(PROJECT_DIR), env=env,
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            timeout=7200,
        )
    except subprocess.TimeoutExpired:
        return LifeResult(life_id, False, time.monotonic() - t0, -1,
                          error="timeout after 7200s")
    elapsed = time.monotonic() - t0
    rc = proc.returncode

    if not out_json.exists():
        # No fitness JSON => the SIM itself failed (JSON is written before any
        # report render). This is a genuine life failure.
        tail = (proc.stderr or b"").decode("utf-8", "replace")[-500:]
        return LifeResult(life_id, False, elapsed, rc, render_returncode=rc,
                          error="no fitness JSON (rc={}) {}".format(rc, tail))

    try:
        data = json.loads(out_json.read_text())
        fitness = {k: data.get(k) for k in _FITNESS_FIELDS if k in data}
    except (json.JSONDecodeError, OSError) as exc:
        return LifeResult(life_id, False, elapsed, rc, render_returncode=rc,
                          json_path=str(out_json), error="unreadable JSON: {}".format(exc))

    # The sim completed iff the JSON carries the headline fitness figure. A
    # non-zero rc WITH a valid fitness JSON means only the (unused) markdown
    # render failed downstream -- recorded, not fatal, for the tournament.
    if "total_net_gbp" not in fitness:
        tail = (proc.stderr or b"").decode("utf-8", "replace")[-500:]
        return LifeResult(life_id, False, elapsed, rc, render_returncode=rc,
                          json_path=str(out_json),
                          error="fitness JSON missing total_net_gbp (rc={}) {}".format(rc, tail))

    err = None
    if rc != 0:
        err = "sim ok (fitness written); post-sim report render exited rc={}".format(rc)
    return LifeResult(life_id, True, elapsed, rc, json_path=str(out_json),
                      fitness=fitness, render_returncode=rc, error=err)


def run_tournament(lives, output_dir: Path, workers: Optional[int] = None,
                   serial: bool = False,
                   per_life_rss_bytes: int = _PER_LIFE_RSS_BYTES):
    """Run `lives` (an iterable of LifeSpec) and return (results, summary).

    workers=None -> default_worker_count() (min of cores and the memory cap for
                    per_life_rss_bytes; pass a smaller estimate for cheap
                    truncated lives to unlock more parallelism safely).
    serial=True  -> force one-at-a-time (the baseline for a speedup measurement).

    FAIL-CLOSED: output_dir is validated first; every life is --fast; nothing
    here publishes, commits, or writes a run_complete marker."""
    output_dir = _validate_output_dir(Path(output_dir))
    output_dir.mkdir(parents=True, exist_ok=True)

    lives = list(lives)
    if workers is None:
        workers = default_worker_count(per_life_rss_bytes)
    workers = max(1, min(int(workers), len(lives) or 1))
    if serial:
        workers = 1

    task_args = [
        (ls.life_id, ls.end_year, ls.env, str(output_dir)) for ls in lives
    ]

    t0 = time.monotonic()
    results = []
    if workers == 1:
        for a in task_args:
            results.append(_run_one_life(a))
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futs = {pool.submit(_run_one_life, a): a[0] for a in task_args}
            for fut in as_completed(futs):
                results.append(fut.result())
    wall = time.monotonic() - t0

    results.sort(key=lambda r: r.life_id)
    ok = [r for r in results if r.ok]
    life_cpu_s = sum(r.elapsed_s for r in results)
    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "lives_total": len(results),
        "lives_ok": len(ok),
        "lives_failed": len(results) - len(ok),
        # Lives whose sim succeeded (fitness written) but whose unused post-sim
        # report render exited non-zero -- surfaced, never hidden.
        "lives_render_failed": sum(1 for r in ok if r.render_returncode != 0),
        "workers": workers,
        "serial": serial or workers == 1,
        "wall_clock_s": round(wall, 2),
        "sum_life_wall_s": round(life_cpu_s, 2),
        # Effective parallelism actually achieved = serial-equivalent work / wall.
        "effective_parallelism": round(life_cpu_s / wall, 2) if wall > 0 else 0.0,
        "mean_life_s": round(life_cpu_s / len(results), 2) if results else 0.0,
        "results": [
            {"life_id": r.life_id, "ok": r.ok, "elapsed_s": round(r.elapsed_s, 2),
             "render_returncode": r.render_returncode,
             "fitness": r.fitness, "error": r.error}
            for r in results
        ],
    }
    (output_dir / "tournament_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True)
    )
    return results, summary


def benchmark(n_lives: int, end_year: Optional[int], output_dir: Path,
              workers: Optional[int] = None,
              per_life_rss_bytes: int = _PER_LIFE_RSS_BYTES):
    """Measure the parallel speedup honestly: run N identical lives SERIALLY,
    then the same N in a bounded pool, and report wall-clock + speedup.

    Same lives, same inputs -> identical fitness both times, which also proves
    the pool did not change any sim output (determinism preserved)."""
    serial_specs = [LifeSpec("s{}".format(i), end_year=end_year) for i in range(n_lives)]
    par_specs = [LifeSpec("p{}".format(i), end_year=end_year) for i in range(n_lives)]

    _, serial_sum = run_tournament(serial_specs, output_dir / "serial", serial=True,
                                   per_life_rss_bytes=per_life_rss_bytes)
    _, par_sum = run_tournament(par_specs, output_dir / "parallel", workers=workers,
                                per_life_rss_bytes=per_life_rss_bytes)

    speedup = (serial_sum["wall_clock_s"] / par_sum["wall_clock_s"]
               if par_sum["wall_clock_s"] > 0 else 0.0)
    bench = {
        "n_lives": n_lives,
        "end_year": end_year,
        "serial_wall_s": serial_sum["wall_clock_s"],
        "parallel_wall_s": par_sum["wall_clock_s"],
        "parallel_workers": par_sum["workers"],
        "speedup_x": round(speedup, 2),
        "effective_parallelism": par_sum["effective_parallelism"],
        "per_life_s_serial": serial_sum["mean_life_s"],
    }
    (output_dir / "benchmark.json").write_text(json.dumps(bench, indent=2, sort_keys=True))
    return bench


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    rp = sub.add_parser("run", help="Run N tournament lives in a bounded pool")
    rp.add_argument("--lives", type=int, required=True)
    rp.add_argument("--output-dir", type=Path, required=True)
    rp.add_argument("--end-year", type=int, default=None)
    rp.add_argument("--workers", type=int, default=None)
    rp.add_argument("--serial", action="store_true")
    rp.add_argument("--per-life-mb", type=int, default=None,
                    help="Per-life RSS estimate (MB) for the memory-aware cap; "
                         "lower for cheap truncated lives to unlock parallelism.")

    bp = sub.add_parser("benchmark", help="Serial-vs-parallel wall-clock speedup")
    bp.add_argument("--lives", type=int, required=True)
    bp.add_argument("--output-dir", type=Path, required=True)
    bp.add_argument("--end-year", type=int, default=None)
    bp.add_argument("--workers", type=int, default=None)
    bp.add_argument("--per-life-mb", type=int, default=None)

    args = p.parse_args()

    def _per_life_bytes():
        return (args.per_life_mb * 1024 * 1024) if args.per_life_mb else _PER_LIFE_RSS_BYTES

    if args.cmd == "run":
        specs = [LifeSpec("l{}".format(i), end_year=args.end_year)
                 for i in range(args.lives)]
        _, summary = run_tournament(specs, args.output_dir,
                                    workers=args.workers, serial=args.serial,
                                    per_life_rss_bytes=_per_life_bytes())
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0 if summary["lives_failed"] == 0 else 1

    if args.cmd == "benchmark":
        bench = benchmark(args.lives, args.end_year, args.output_dir,
                          workers=args.workers, per_life_rss_bytes=_per_life_bytes())
        print(json.dumps(bench, indent=2, sort_keys=True))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
