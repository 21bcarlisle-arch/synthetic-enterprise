#!/usr/bin/env python3
"""Read-only test-suite throughput profiler (docs/design/TEST_THROUGHPUT_MEASUREMENT_AND_PROPOSAL.md).

WHY THIS EXISTS
---------------
The director's steer (docs/staging/DIRECTOR_STEER_TEST_THROUGHPUT_2026-07-19.md) required a real
measurement before any restructuring: "measure before restructuring... Do NOT re-run the full
~18k-test suite, that IS the problem." This gives a repeatable, bounded way to answer "where does
the wall-clock go" WITHOUT ever invoking the full suite by default -- the same mistake the
one-hour manual run made. It complements tools/generate_test_mix_data.py (which reports
composition -- how many tests per area) with DURATION (how long per area / which tests dominate),
which that tool deliberately does not do.

WHAT IT DOES NOT DO
--------------------
It does not change any gate, marker, or selection logic. It does not run the full suite unless
you pass --full and an explicit --i-understand-this-is-slow flag (belt-and-braces against an
accidental hour-long invocation from a future session that skims past --help). Default mode
profiles a small, fixed, REPRESENTATIVE sample: the known heavy full-simulation files already
named in background/process_run_complete.py::PUBLISH_GATE_HEAVY_IGNORES, plus one fast directory
per top-level test area, so a single run gives both ends of the distribution in well under a
minute for the fast set and a few minutes for the heavy set.

USAGE
-----
    python3 tools/profile_test_suite.py                  # representative sample (default, safe)
    python3 tools/profile_test_suite.py --dirs tests/sim tests/company   # specific dirs
    python3 tools/profile_test_suite.py --collect-only    # just the test-count profile (seconds)
    python3 tools/profile_test_suite.py --classify        # deterministic/stochastic heuristic scan
    python3 tools/profile_test_suite.py --full --i-understand-this-is-slow   # the whole tests/ tree

Every mode is read-only: it only ever invokes `pytest --collect-only` or `pytest --durations`
against the real tree; it writes nothing except (optionally) a JSON report to the path given by
--json-out, and never touches PUBLISH_GATE_HEAVY_IGNORES, conftest.py, or any pytest.ini/config.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The 8 files background/process_run_complete.py already excludes from the publish gate for
# SPEED (PUBLISH_GATE_HEAVY_IGNORES) -- known, named, heavy. Kept as a literal copy (not an
# import) so this read-only tool has zero coupling to the gate module's import side effects.
KNOWN_HEAVY_FILES = [
    "tests/simulation/test_run_phase2b.py",
    "tests/simulation/test_run_phase2b_event_log.py",
    "tests/simulation/test_run_phase4c_on_phase2b.py",
    "tests/simulation/test_phase40b_gas_pass_through.py",
    "tests/simulation/test_phase24a_ic_customer.py",
    "tests/simulation/test_phase40a_pass_through.py",
    "tests/simulation/test_phase40c_deemed_rate.py",
    "tests/simulation/test_phase41a_flex.py",
]

# One additional known-heavy test found by this profiler's own first run (2026-07-19): a
# dashboard-gate test that MOCKS the dashboard generator but still falls through to a real,
# un-mocked full-decade x2 frozen-baseline replay. See the measurement doc §2.2.
KNOWN_HEAVY_EXTRA = [
    "tests/tools/test_website_integrity_fix.py",
]

# A fast directory per top-level test area, for the "cheap population" side of the profile.
FAST_SAMPLE_DIRS = [
    "tests/sim",
    "tests/company/billing",
    "tests/company/compliance",
    "tests/interface",
    "tests/interfaces",
    "tests/controls",
    "tests/design",
    "tests/hooks",
]

STOCHASTIC_PATTERNS = re.compile(
    r"np\.random|numpy\.random|random\.seed|import random\b|"
    r"large_sample|_close_to_anchor|plausible|confidence_interval|"
    r"percentile|np\.std|statistics\.(mean|stdev)|population_shares|tolerance="
)
DISTRIBUTIONAL_ASSERT = re.compile(r"pytest\.approx|assert abs\(")


def _run(argv: list[str], timeout: int) -> tuple[int, str, float]:
    start = time.time()
    try:
        r = subprocess.run(argv, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout + r.stderr, time.time() - start
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or "") + (exc.stderr or "")
        return -1, out, time.time() - start


def collect_count(target: str, timeout: int = 120) -> int | None:
    rc, out, _ = _run([sys.executable, "-m", "pytest", target, "--collect-only", "-q"], timeout)
    for line in reversed(out.splitlines()):
        line = line.strip()
        if "collected" in line:
            for tok in line.split():
                if tok.isdigit():
                    return int(tok)
    return None


def profile_targets(targets: list[str], durations: int, timeout: int) -> dict:
    """Run each target with --durations and report total wall time + slowest tests."""
    report = {}
    for t in targets:
        argv = [sys.executable, "-m", "pytest", t, f"--durations={durations}", "-q", "--tb=no"]
        rc, out, wall = _run(argv, timeout)
        slow = []
        for line in out.splitlines():
            m = re.match(r"\s*([\d.]+)s\s+call\s+(\S+)", line)
            if m:
                slow.append({"seconds": float(m.group(1)), "test": m.group(2)})
        summary_line = next(
            (ln for ln in reversed(out.splitlines())
             if re.search(r"passed|failed|error", ln) and "in " in ln),
            None,
        )
        report[t] = {
            "wall_seconds": round(wall, 2),
            "returncode": rc,
            "timed_out": rc == -1,
            "summary": summary_line,
            "slowest": slow,
        }
    return report


def classify_population(dirs: list[str] | None = None) -> dict:
    """Heuristic deterministic-vs-stochastic file scan (grep-based, not exact -- a starting
    point for manual review, per the measurement doc's classification design)."""
    base = ROOT / "tests"
    files = list(base.rglob("test_*.py")) if not dirs else [
        p for d in dirs for p in (ROOT / d).rglob("test_*.py")
    ]
    stochastic, distributional_only, deterministic = [], [], []
    for f in files:
        try:
            text = f.read_text(errors="ignore")
        except OSError:
            continue
        rel = str(f.relative_to(ROOT))
        if STOCHASTIC_PATTERNS.search(text):
            stochastic.append(rel)
        elif DISTRIBUTIONAL_ASSERT.search(text):
            distributional_only.append(rel)
        else:
            deterministic.append(rel)
    return {
        "total_files": len(files),
        "stochastic_signal_files": len(stochastic),
        "distributional_assert_only_files": len(distributional_only),
        "deterministic_files": len(deterministic),
        "stochastic_signal_examples": stochastic[:15],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dirs", nargs="*", help="Specific dirs/files to profile instead of the default sample.")
    ap.add_argument("--collect-only", action="store_true", help="Just report test counts (fast).")
    ap.add_argument("--classify", action="store_true", help="Run the deterministic/stochastic heuristic scan.")
    ap.add_argument("--durations", type=int, default=15, help="How many slowest tests to report per target.")
    ap.add_argument("--timeout", type=int, default=1200, help="Per-target subprocess timeout (seconds).")
    ap.add_argument("--full", action="store_true", help="Profile the WHOLE tests/ tree. Requires --i-understand-this-is-slow.")
    ap.add_argument("--i-understand-this-is-slow", action="store_true", dest="ack_slow")
    ap.add_argument("--profile", action="store_true",
                     help="Run the durations-based sample profile (the known-heavy files + fast "
                          "sample dirs, or --dirs if given). This is the only mode that actually "
                          "executes tests beyond --collect-only, and typically takes several "
                          "minutes because it deliberately includes the known-heavy files.")
    ap.add_argument("--json-out", type=str, default=None, help="Write the full report as JSON to this path.")
    args = ap.parse_args()

    if args.full and not args.ack_slow:
        print("--full requires --i-understand-this-is-slow (this is the ~18k-test, ~60min+ run "
              "the director's steer explicitly said not to trigger by accident). Aborting.",
              file=sys.stderr)
        return 2

    # Each mode is INDEPENDENT and explicit -- no mode silently falls through to another. A bare
    # `--classify` (or `--collect-only`) must never trigger the heavy --profile sample; that
    # exact bug bit this tool's own first run (2026-07-19: `--classify` alone re-ran the full
    # known-heavy file list for no reason). Require --profile (or --full) to execute any test.
    if not any([args.classify, args.collect_only, args.full, args.profile]):
        ap.print_help()
        print("\nNo mode selected -- nothing executed (this tool never runs tests by default). "
              "Pick --collect-only, --classify, --profile, or --full.", file=sys.stderr)
        return 2

    report: dict = {"nproc_hint": "see `nproc`", "generated_by": "tools/profile_test_suite.py"}

    if args.classify:
        report["classification"] = classify_population(args.dirs)

    if args.collect_only:
        targets = args.dirs or ["tests/"]
        report["counts"] = {t: collect_count(t) for t in targets}

    if args.full:
        report["full_suite"] = profile_targets(["tests/"], args.durations, timeout=7200)
    elif args.profile:
        targets = args.dirs or (KNOWN_HEAVY_FILES + KNOWN_HEAVY_EXTRA + FAST_SAMPLE_DIRS)
        report["profile"] = profile_targets(targets, args.durations, args.timeout)

    text = json.dumps(report, indent=2, sort_keys=True)
    print(text)
    if args.json_out:
        Path(args.json_out).write_text(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
