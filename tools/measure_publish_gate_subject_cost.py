#!/usr/bin/env python3
"""Measure what the publish gate's SUBJECT costs: in-tree vs a reused HEAD checkout.

OPS2_publish_gate_head_worktree exit criterion 1 says the clean-subject gate must run within
1.3x the in-tree baseline, "measured both sides, not asserted", and criterion 2 derives
GATE_SUITE_TIMEOUT_SECONDS from the NEW measured runtime. This is the harness that produces
those numbers, kept in the repo so the claim in
docs/design/OPS2_PUBLISH_GATE_HEAD_CHECKOUT.md can be re-run rather than believed.

Three phases, in this order so the cold run also does the work of warming the cache:

    COLD     -- reused checkout deleted first, so every module compiles from source
    WARM     -- the same directory refreshed in place; __pycache__ survives. THE steady state
    BASELINE -- the pre-ruling subject: the live working tree

`-x` is removed from the argv on ALL THREE sides. With it, a red suite stops at the first
failure, so "duration" would be time-to-first-failure and the sides would not be comparable.
The suite is expected to be red at HEAD for unrelated reasons; the runtime is the measurement,
the verdict is not.

The box is shared with the live publisher, whose own suite would both skew the wall-clock and
contend for a machine with ~5GB free. Each phase therefore waits for the publisher to be idle
first, and records loadavg alongside its own number so a contaminated run is visible rather
than silently averaged in.

Usage:  python3 -m tools.measure_publish_gate_subject_cost [--out PATH]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from background import process_run_complete as prc  # noqa: E402

# A phase must not start while the real publisher is mid-suite. Bounded: if it never goes quiet
# we measure anyway and say so, because a harness that can hang forever is worse than a noisy
# number that is labelled noisy.
QUIET_WAIT_SECONDS = 45 * 60
QUIET_POLL_SECONDS = 30


def _publisher_is_running() -> bool:
    """True if a real process_run_complete cycle is live (this process excepted)."""
    try:
        out = subprocess.run(["pgrep", "-af", "process_run_complete.py"],
                             capture_output=True, text=True, timeout=30).stdout
    except (OSError, subprocess.SubprocessError):
        return False
    mine = str(os.getpid())
    for line in out.splitlines():
        pid = line.split(" ", 1)[0]
        if pid != mine and "measure_publish_gate_subject_cost" not in line:
            return True
    return False


def _wait_for_quiet(log) -> bool:
    """Wait for the publisher to finish. Returns True if the box went quiet."""
    deadline = time.time() + QUIET_WAIT_SECONDS
    waited = False
    while _publisher_is_running():
        if time.time() > deadline:
            log("  ! publisher still live after {}s -- measuring anyway, flagged contended"
                .format(QUIET_WAIT_SECONDS))
            return False
        if not waited:
            log("  . waiting for the live publisher to finish before timing")
            waited = True
        time.sleep(QUIET_POLL_SECONDS)
    return True


def _argv_without_x() -> list:
    """The gate's own argv, minus -x. See the module docstring for why."""
    return [a for a in prc.publish_gate_pytest_argv("tests/") if a != "-x"]


def _time_suite(cwd: Path, log) -> dict:
    quiet = _wait_for_quiet(log)
    env = dict(os.environ)
    env["SIM_FAST_MODE"] = "1"
    load_before = os.getloadavg()[0]
    started = time.monotonic()
    result = subprocess.run(_argv_without_x(), cwd=str(cwd), env=env,
                            capture_output=True, text=True, errors="replace")
    elapsed = time.monotonic() - started
    tail = [ln for ln in result.stdout.strip().splitlines() if ln.strip()][-1:]
    return {
        "cwd": str(cwd),
        "seconds": round(elapsed, 1),
        "returncode": result.returncode,
        "summary": tail[0][:300] if tail else "",
        "loadavg_before": round(load_before, 2),
        "loadavg_after": round(os.getloadavg()[0], 2),
        "box_was_quiet": quiet,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(prc.PROJECT_DIR / "docs" / "observability"
                                         / "publish_gate_subject_cost.json"))
    args = ap.parse_args()

    def log(msg):
        print("[measure] {}".format(msg), flush=True)

    head_sha = prc._head_sha()
    results = {"head_sha": head_sha, "phases": {}}

    log("HEAD={} -- three timed runs, expect ~45-60 min total".format(head_sha))

    # COLD: delete the reused checkout so nothing survives from an earlier cycle.
    #
    # WAIT FIRST, THEN DELETE. A live publisher may be running its suite inside that very
    # directory, and removing it mid-run would corrupt a real publish cycle to take a
    # measurement -- the harness must never be able to damage the thing it measures.
    _wait_for_quiet(log)
    reused = prc.HEAD_CHECKOUT_ROOT / prc.REUSED_HEAD_CHECKOUT_NAME
    shutil.rmtree(reused, ignore_errors=True)
    log("phase 1/3 COLD -- reused checkout deleted, bytecode compiles from source")
    with prc._head_checkout() as path:
        if path is None:
            log("! checkout unavailable -- cannot measure the clean subject")
            return 1
        if path.name != prc.REUSED_HEAD_CHECKOUT_NAME:
            log("! got a THROWAWAY checkout ({}) -- another publisher holds the reuse lock, so "
                "the warm phase would not be warm. Aborting rather than reporting a wrong ratio."
                .format(path.name))
            return 1
        results["phases"]["cold_checkout"] = _time_suite(path, log)
    log("   cold: {}s".format(results["phases"]["cold_checkout"]["seconds"]))

    # WARM: same directory, refreshed in place. __pycache__ survives the refresh.
    log("phase 2/3 WARM -- same directory refreshed in place, bytecode retained")
    with prc._head_checkout() as path:
        if path is None or path.name != prc.REUSED_HEAD_CHECKOUT_NAME:
            log("! lost the reused checkout between phases -- aborting")
            return 1
        results["phases"]["warm_checkout"] = _time_suite(path, log)
    log("   warm: {}s".format(results["phases"]["warm_checkout"]["seconds"]))

    # BASELINE: the pre-ruling subject, the live working tree.
    log("phase 3/3 BASELINE -- the live working tree, the pre-ruling subject")
    results["phases"]["in_tree_baseline"] = _time_suite(prc.PROJECT_DIR, log)
    log("   baseline: {}s".format(results["phases"]["in_tree_baseline"]["seconds"]))

    warm = results["phases"]["warm_checkout"]["seconds"]
    base = results["phases"]["in_tree_baseline"]["seconds"]
    results["ratio_warm_over_in_tree"] = round(warm / base, 3) if base else None
    results["exit_criterion_ratio_max"] = 1.3
    results["meets_exit_criterion"] = bool(base and (warm / base) <= 1.3)
    # Criterion 2: the bound is derived from the runtime the gate ACTUALLY pays, which is the
    # warm steady state -- but a cold cycle is a real outcome (a fallback throwaway, a rebuilt
    # corrupt checkout), so the bound must clear the worst legitimate case, not the usual one.
    worst = max(warm, results["phases"]["cold_checkout"]["seconds"], base)
    results["worst_legitimate_seconds"] = worst
    results["implied_timeout_floor_2x"] = int(worst * 2)

    Path(args.out).write_text(json.dumps(results, indent=2) + "\n")
    log("ratio warm/in-tree = {} (criterion <= 1.3) -- {}".format(
        results["ratio_warm_over_in_tree"],
        "MEETS" if results["meets_exit_criterion"] else "MISSES"))
    log("worst legitimate run {}s -> timeout floor at 2x = {}s".format(
        worst, results["implied_timeout_floor_2x"]))
    log("written to {}".format(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
