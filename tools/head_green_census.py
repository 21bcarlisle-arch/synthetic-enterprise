"""Is HEAD actually green? Measure it, instead of inferring it from a scoped gate.

WHY THIS EXISTS
---------------
On 2026-08-12 a full unscoped run of the publish-gate marker expression found EIGHT failing
tests among 24,204, all pre-existing, none of which any routine control was shaped to see:

  * `pre_commit_test_gate` / `surgical_land` select tests by NAME STEM from the changed paths,
    so a change to `background/finding_severity.py` can never reach a census in `tests/design/`.
  * the operational-layer check runs `-m "operational or join_report_only or scale_report_only"`
    -- the exact complement of the set those eight lived in.
  * `process_run_complete`'s publish gate carries `-x`, so it stops at the first failure. That
    day it stopped on an unrelated seat-guard red and left 1,121 tests unrun, reporting one name
    and hiding six.

So "HEAD is green" had never been measured. What was measured was "the tests name-adjacent to
the last diff are green", which is a much weaker claim wearing the same words.

WHAT THIS DOES, AND THE TWO DESIGN CHOICES THAT MATTER
------------------------------------------------------
1. **No `-x`.** Fail-fast is right for a commit gate and wrong for a health measurement. The
   whole value here is the COMPLETE list; stopping at the first red reproduces the defect.

2. **Alarm on the DELTA, not the absolute count.** A standing red set that nobody has
   dispositioned becomes wallpaper within a week, and then the control is decoration. NEW reds
   -- tests failing now that were not in the committed baseline -- are the signal. Tests that
   have started passing are reported too, because a baseline nobody prunes rots into a licence
   to stay red.

The baseline is a COMMITTED file, not a self-updating one. Nothing here writes it: a control
that quietly absorbs its own new failures into its baseline cannot fail, which is the whole
R15 anti-pattern. Updating it is a human act with a commit message attached.

DELIBERATELY NOT A COMMIT GATE. Do not wire this into the pre-commit path: a 25-minute gate
gets bypassed, and hook-bypass is a wall. The per-commit gate being scoped is a legitimate
design; the defect was that nothing else was unscoped.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
BASELINE_PATH = PROJECT_DIR / "docs" / "observability" / "head_red_baseline.json"

# The publish gate's own marker expression, so this measures the same population the gate
# claims to protect -- not a set of our own choosing that could drift away from it.
MARKER_EXPR = "not operational and not join_report_only and not scale_report_only"

# The heavy modules the publish gate ignores. Kept in step with
# process_run_complete.PUBLISH_GATE_HEAVY_IGNORES deliberately: measuring a DIFFERENT population
# from the gate would make the two incomparable, and the point is to cover the gate's blind spot,
# not to invent a third scope.
HEAVY_IGNORES = (
    "tests/simulation/test_run_phase2b.py",
    "tests/simulation/test_run_phase2b_event_log.py",
    "tests/simulation/test_run_phase4c_on_phase2b.py",
    "tests/simulation/test_phase40b_gas_pass_through.py",
    "tests/simulation/test_phase24a_ic_customer.py",
    "tests/simulation/test_phase40a_pass_through.py",
    "tests/simulation/test_phase40c_deemed_rate.py",
    "tests/simulation/test_phase41a_flex.py",
)

_FAILED_RE = re.compile(r"^FAILED\s+(\S+)", re.MULTILINE)
_SUMMARY_RE = re.compile(r"(\d+)\s+passed")


def parse_failures(output: str) -> list[str]:
    """Every `FAILED <nodeid>` line, deduped, in a stable order."""
    return sorted(set(_FAILED_RE.findall(output or "")))


def parse_passed_count(output: str):
    """How many tests PASSED, or None if the summary line is unreadable.

    None and 0 are opposite facts and are kept apart: 0 means the run demonstrably passed
    nothing, None means we cannot tell -- and only one of those is compatible with a green.
    """
    matches = _SUMMARY_RE.findall(output or "")
    return int(matches[-1]) if matches else None


def load_baseline(path: Path = BASELINE_PATH) -> set:
    """The known-red set. A missing/malformed baseline is EMPTY, so every red reads as new.

    Fail direction is towards NOISE, never towards silence: an unreadable baseline that resolved
    to "everything is known" would turn this control off exactly when its state is broken.
    """
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return set()
    known = data.get("known_red")
    return set(known) if isinstance(known, list) else set()


def diff_against_baseline(failures, baseline) -> dict:
    """New reds, fixed reds, and still-red -- the whole verdict, from two sets."""
    failures, baseline = set(failures), set(baseline)
    return {
        "new_red": sorted(failures - baseline),
        "fixed": sorted(baseline - failures),
        "still_red": sorted(failures & baseline),
    }


def verdict(delta: dict, passed_count) -> tuple[str, str]:
    """GREEN / NEW_RED / UNPROVEN, with the reason.

    A run that passed NOTHING, or whose summary could not be read, is UNPROVEN rather than
    green: pytest exits 0 when every selected test is skipped or deselected, so "no failures"
    on its own is satisfied by a run that did nothing at all -- the fail-open shape R15 names.
    """
    if passed_count is None:
        return "UNPROVEN", "no pytest summary line -- the run's own output is unreadable"
    if passed_count == 0:
        return "UNPROVEN", "the run passed ZERO tests -- it selected nothing, so it proved nothing"
    if delta["new_red"]:
        return "NEW_RED", "{} test(s) newly failing: {}".format(
            len(delta["new_red"]), ", ".join(delta["new_red"][:10]))
    if delta["still_red"]:
        return "GREEN", "no new failures ({} known-red still failing, {} passed)".format(
            len(delta["still_red"]), passed_count)
    return "GREEN", "no failures at all ({} passed)".format(passed_count)


def pytest_argv() -> list:
    argv = [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=line", "-m", MARKER_EXPR]
    argv += ["--ignore=" + i for i in HEAVY_IGNORES]
    return argv


def run_suite(timeout: int = 3600) -> str:
    proc = subprocess.run(pytest_argv(), cwd=str(PROJECT_DIR),
                          capture_output=True, text=True, timeout=timeout)
    return (proc.stdout or "") + (proc.stderr or "")


def evaluate(output: str, baseline_path: Path = BASELINE_PATH) -> dict:
    failures = parse_failures(output)
    passed = parse_passed_count(output)
    delta = diff_against_baseline(failures, load_baseline(baseline_path))
    status, reason = verdict(delta, passed)
    return {"status": status, "reason": reason, "passed": passed,
            "failures": failures, **delta}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--from-log", type=Path,
                    help="parse an existing pytest log instead of running the suite")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--notify", action="store_true",
                    help="send one NTFY when the verdict is NEW_RED (transition payload, R5)")
    args = ap.parse_args(argv)

    output = args.from_log.read_text(errors="replace") if args.from_log else run_suite()
    result = evaluate(output)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("{}: {}".format(result["status"], result["reason"]))
        for name in result["new_red"]:
            print("  NEW RED  " + name)
        for name in result["fixed"]:
            print("  FIXED    " + name + "   (prune it from the baseline)")

    if args.notify and result["status"] == "NEW_RED":
        try:
            from background.notify import notify
            notify(
                "[HEAD-GREEN] {} newly failing test(s) at HEAD:\n  {}".format(
                    len(result["new_red"]), "\n  ".join(result["new_red"][:12])),
                kind="real_alarm",
                headers={"X-Tags": "rotating_light", "X-Priority": "high"},
            )
        except Exception as exc:  # noqa: BLE001 -- a dead channel must not eat the verdict
            print("  ! notify failed: {}".format(type(exc).__name__), file=sys.stderr)

    return 1 if result["status"] == "NEW_RED" else 0


if __name__ == "__main__":
    sys.exit(main())
