#!/usr/bin/env python3
"""Measure how the run's PEAK MEMORY scales with the settlement window. A closed-loop test for a
defect whose obvious test loop is the defect itself.

WHY THIS EXISTS
---------------
2026-08-24: the producer was OOM-killed fourteen times from ~09:20 and nothing published for hours.
The mechanism is recorded in
`WORKER_FINDING_THE_PRODUCER_OOMS_BECAUSE_THE_BOOK_GREW_AND_SETTLEMENT_SCALES_WITH_IT_2026-08-24.md`:
settlement memory scales with book x years, the book went from ~13 accounts to 81 that morning, and
a run that used to fit in the guest reached ~14.2GB and was killed at ~39 minutes.

Of the three repairs, two were the director's. **One of them has since happened**: he raised the
WSL2 guest's allocation and restarted it that afternoon (~23.5GB now, `oom_kills_total` back to 0).
That is HEADROOM, not a fix -- the slope is unchanged, so the same book growing at the same rate
walks into the same wall at a later date, and the only thing bought is the time to do the third
repair properly. Never read the guest's size from a docstring: `background.resource_headroom.
sample()["total_mb"]` is the live number, and this one has already moved once.

The third repair -- reducing the footprint in code -- is ours, and it carries a trap worth naming:
**validating it means repeatedly running the 40-minute, many-GB job whose cost is the thing under
test.** The fix's own test loop is the defect it fixes.

R4 says build the smallest closed-loop test before fixing a stuck problem. This is it. Short
horizons are cheap -- `run_annual_report --end-year` truncates the window -- so the SHAPE of the
scaling can be measured in minutes and gigabytes instead of forty minutes and fourteen. Whoever
takes the footprint work gets a before/after number without needing the box to fit the full run.

WHAT IT MEASURES, and what it does not
--------------------------------------
Peak RSS of the child process, from `/usr/bin/time -v` ("Maximum resident set size"), per horizon.
That is the number the OOM killer acts on.

It does NOT prove the cause. Two horizons differing in peak RSS is consistent with settlement
dominating and with anything else that grows per year; what makes the reading useful is the SLOPE
across three or more horizons plus the intercept, which separates a per-year cost from a fixed one.
Read it as evidence, not as a verdict -- and note the run is not deterministic in memory to the
byte, so treat small differences as noise.

USAGE
-----
    python3 -m tools.settlement_footprint_probe --years 2017 2018 2019
    python3 -m tools.settlement_footprint_probe --years 2017 2019 --json out.json

**Do not run this while a real run is in flight.** It competes for exactly the memory the thing it
is measuring is short of, and a probe that causes the outage it is investigating has measured its
own interference. The tool refuses by default; `--force` overrides for a deliberately idle box.

DELIBERATELY DORMANT, and recorded as such in `docs/design/orphan_baseline.json`. Nothing schedules
this and nothing should: it is three heavy runs of the producer, taken by hand on an idle box, by
whoever picks up the footprint repair. The orphan ratchet's alternative -- wiring it to a timer --
would put a job that must not compete with the producer on a clock that cannot know whether the
producer is running.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

#: The line `/usr/bin/time -v` prints the peak RSS on, in kilobytes.
_MAXRSS_RE = re.compile(r"Maximum resident set size \(kbytes\):\s*(\d+)")
#: What a live producer's command line looks like, so the probe can refuse to compete with it.
_LIVE_RUN_PATTERN = "tools.run_annual_report"


def _argv_of(pid: str) -> list[str] | None:
    """This pid's argv as a list, or None when it cannot be read.

    None is deliberately AMBIGUOUS to the caller and is treated as "still a run" there: a
    process that exists but whose `/proc` entry we cannot read is not evidence of an idle box.
    """
    try:
        raw = Path("/proc") / pid / "cmdline"
        parts = raw.read_bytes().decode("utf-8", "replace").split("\0")
    except (OSError, ValueError):
        return None
    argv = [p for p in parts if p]
    return argv or None


def _argv_is_a_producer_run(argv: list[str]) -> bool:
    """True only when argv INVOKES the run, rather than merely mentioning it.

    `pgrep -f` matches the whole command line, so anything carrying the module's name as DATA
    matches too. On this box that is not hypothetical: the autonomous worker is launched as
    `claude -p <prompt>`, and a prompt that instructs the seat to run this probe quotes
    `tools.run_annual_report` inside its own argv. The guard then reports the agent that is
    trying to take the measurement as the producer it must stand down for -- forever, because
    the agent cannot outlive its own prompt. The only escape was `--force`, which turns a
    fail-closed guard into a bypass and would have measured the box while competing after all.

    So the shape is checked, not the substring. `background/sim_runner.py:240` launches
    `[sys.executable, "-m", "tools.run_annual_report", ...]`, and `measure()` below launches the
    same argv under `/usr/bin/time`; both put the module in its OWN argv element, immediately
    after `-m`. A script path is accepted too. A mention anywhere else is data.
    """
    if not argv or "python" not in Path(argv[0]).name:
        return False
    # The interpreter's own options come first; the module or script is the first argument that
    # is not one. Anything AFTER that belongs to the program and is its data, not its identity.
    i = 1
    while i < len(argv) and argv[i].startswith("-"):
        if argv[i] == "-m" and i + 1 < len(argv):
            module = argv[i + 1]
            return module == _LIVE_RUN_PATTERN or module.startswith(_LIVE_RUN_PATTERN + ".")
        i += 1
    if i < len(argv):
        return argv[i].endswith(_LIVE_RUN_PATTERN.replace(".", "/") + ".py")
    return False


def a_run_is_in_flight() -> str | None:
    """The PID of a live producer run, or None. Fails CLOSED -- if `pgrep` cannot be run we
    report a run in flight rather than assume the box is idle, because the harmful direction is
    launching a second 14GB job, not skipping a measurement.

    A matched pid is discarded ONLY when its argv can be read and does not invoke the run
    (`_argv_is_a_producer_run`). An unreadable argv keeps the pid, so every way of not knowing
    still refuses.
    """
    try:
        r = subprocess.run(["pgrep", "-f", _LIVE_RUN_PATTERN],
                           capture_output=True, text=True, timeout=10)
    except Exception:
        return "unknown (pgrep unavailable -- refusing rather than assuming an idle box)"
    pids = [p for p in r.stdout.split() if p.strip()]
    for pid in pids:
        argv = _argv_of(pid)
        if argv is None or _argv_is_a_producer_run(argv):
            return pid
    return None


def measure(end_year: int, fast: bool = True, timeout_s: int = 3600) -> dict:
    """Run the report to `end_year` and return its peak RSS in MB, or the failure."""
    with tempfile.TemporaryDirectory() as tmp:
        out_md = Path(tmp) / "report.md"
        out_json = Path(tmp) / "run.json"
        argv = [
            "/usr/bin/time", "-v",
            sys.executable, "-m", "tools.run_annual_report",
            "--end-year", str(end_year),
            "--save-json", str(out_json),
            "--output", str(out_md),
        ]
        if fast:
            argv.append("--fast")
        try:
            proc = subprocess.run(argv, cwd=str(PROJECT), capture_output=True,
                                  text=True, timeout=timeout_s)
        except subprocess.TimeoutExpired:
            return {"end_year": end_year, "ok": False, "error": f"timed out after {timeout_s}s"}
        # `/usr/bin/time -v` writes to STDERR, alongside the child's own stderr.
        match = _MAXRSS_RE.search(proc.stderr or "")
        peak_mb = round(int(match.group(1)) / 1024, 1) if match else None
        return {
            "end_year": end_year,
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "peak_rss_mb": peak_mb,
            # A killed child is the interesting case, not an error to hide: -9 is the OOM killer.
            "killed_by_signal": -proc.returncode if proc.returncode < 0 else None,
            "produced_output": out_json.exists(),
        }


def summarise(rows: list[dict]) -> dict:
    """Slope and intercept across the measured horizons -- the per-year cost and the fixed one."""
    usable = [r for r in rows if r.get("peak_rss_mb") and r.get("end_year")]
    if len(usable) < 2:
        return {"slope_mb_per_year": None, "fixed_mb": None,
                "note": "need at least two successful horizons to separate per-year from fixed cost"}
    usable.sort(key=lambda r: r["end_year"])
    first, last = usable[0], usable[-1]
    span = last["end_year"] - first["end_year"]
    if span <= 0:
        return {"slope_mb_per_year": None, "fixed_mb": None, "note": "horizons did not differ"}
    slope = (last["peak_rss_mb"] - first["peak_rss_mb"]) / span
    return {
        "slope_mb_per_year": round(slope, 1),
        "fixed_mb": round(first["peak_rss_mb"] - slope * (first["end_year"] - 2015), 1),
        "note": "slope is the per-settlement-year cost; a large fixed term means the win is NOT "
                "in the window length and shortening the run will not save the producer",
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--years", type=int, nargs="+", default=[2017, 2018, 2019],
                    help="settlement end-years to measure (default: 2017 2018 2019)")
    ap.add_argument("--json", type=Path, default=None, help="write the measurements here")
    ap.add_argument("--no-fast", action="store_true", help="do NOT set SIM_FAST_MODE")
    ap.add_argument("--force", action="store_true",
                    help="measure even if a producer run is in flight (it will compete for the "
                         "memory being measured)")
    args = ap.parse_args(argv)

    live = a_run_is_in_flight()
    if live and not args.force:
        print("REFUSING: a producer run is in flight (pid {}). This probe competes for exactly "
              "the memory it is measuring, and would risk causing the OOM it is investigating. "
              "Wait for the run, or pass --force on a deliberately idle box.".format(live))
        return 2

    rows = [measure(y, fast=not args.no_fast) for y in args.years]
    result = {"measurements": rows, "scaling": summarise(rows)}
    for r in rows:
        print("end-year {}: peak {} MB, ok={}{}".format(
            r["end_year"], r.get("peak_rss_mb"), r["ok"],
            " KILLED BY SIGNAL {}".format(r["killed_by_signal"]) if r.get("killed_by_signal") else ""))
    print("scaling: {}".format(result["scaling"]))
    if args.json:
        args.json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
