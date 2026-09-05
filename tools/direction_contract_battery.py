#!/usr/bin/env python3
"""R15 mutation battery for `background/direction.py`, scored PER CALLER SUITE.

`tools/mutate_printed_figure_rederivation.py` is the same family and asserts a
different thing: that one NAMED test fires per mutation. That shape cannot
answer this question, because the question is not "is this contract proved" but
"WHICH of the four caller suites is proving it". A converged module inherits
whichever caller suite happened to be strongest, and a contract proved by one
suite dies the day that caller is refactored away. So every mutation is run
against each caller suite SEPARATELY and the answer is a row of four, never a
pass/fail.

Pre-registration and the eight predictions:
`docs/staging/SEAT_PREREG_WHICH_CALLER_SUITE_IS_EACH_DIRECTION_CONTRACT_STANDING_ON_2026-09-05.md`

Three things here are not decoration:

* **The target string is asserted present EXACTLY ONCE before patching.** A
  surviving mutation is otherwise indistinguishable from a patch that never
  applied, and this project has recorded that exact false survivor.
* **A BASELINE pass runs first and its reds are deselected** from every
  mutation run. A test already red at HEAD would otherwise be read as the
  mutation dying, in every one of the eight rows at once.
* **Restore is from a pristine copy held OUTSIDE the tree**, and `pkill -f` on
  this battery matches the calling shell, so an in-tree restore step can be
  killed along with the thing it was restoring from.

Results are written outside the tree too (`--out`), because an in-flight
mutation leaving `background/direction.py` dirty is what makes
`promote_worktree_landing` refuse.

Usage:
    python3 -m tools.direction_contract_battery --out /var/tmp/battery.json
    python3 -m tools.direction_contract_battery --only M5 M6   # resume/subset
"""
from __future__ import annotations

import argparse
import atexit
import json
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
SUBJECT = PROJECT / "background" / "direction.py"

#: The four caller suites. `tools/generate_delivery_page.py` is the fourth
#: first-party caller and has no suite that imports it AND direction, so the
#: fourth row here is the self-audit suite -- the closest thing the module has
#: to one of its own.
SUITES = (
    "tests/background/test_supervisor.py",
    "tests/background/test_delivery_lane.py",
    "tests/background/test_delivery_seat.py",
    "tests/background/test_the_self_audit_declared_a_correction_and_nothing_carried_it.py",
)

#: (id, the contract as the module states it, old, new). Each is ONE edit to a
#: named function; each `old` must appear exactly once in the subject.
MUTATIONS = (
    (
        "M1",
        "focus_multiplier is ALWAYS >= 1.0 -- direction may only ADD attention, never filter",
        "    if not atom_id or atom_id not in focus:\n        return 1.0",
        "    if not atom_id or atom_id not in focus:\n        return 0.5",
    ),
    (
        "M2",
        "focus_weights returns weights untouched when the two lists disagree in length",
        "        if not focus or len(candidates) != len(original):",
        "        if not focus:",
    ),
    (
        "M3",
        "forbidden target-shaped keys are refused at any depth",
        "            _forbidden_keys_in(value, seen)",
        "            pass",
    ),
    (
        "M4",
        "an empty not_now is refused -- the rejections are what makes it reviewable",
        "    if not isinstance(not_now, list) or not not_now:",
        "    if not isinstance(not_now, list):",
    ),
    (
        "M5",
        "wrong[i].corrected must be a BOOLEAN, not merely present",
        '            elif not isinstance(item.get("corrected"), bool):',
        '            elif "corrected" not in item:',
    ),
    (
        "M6",
        "read_direction NEVER RAISES -- missing, unreadable and malformed are one answer",
        "    except Exception:\n        # BREADTH IS THE POINT",
        "    except FileNotFoundError:\n        # BREADTH IS THE POINT",
    ),
    (
        "M7",
        "is_live is bounded BELOW as well as above -- a future-dated record must not steer",
        "        return 0.0 <= self.age_hours(now) <= FOCUS_MAX_AGE_HOURS",
        "        return self.age_hours(now) <= FOCUS_MAX_AGE_HOURS",
    ),
    (
        "M8",
        "a legacy wrong row's correction state is None, NOT False -- different claims",
        '            out.append({"what": item.strip(), "corrected": None})',
        '            out.append({"what": item.strip(), "corrected": False})',
    ),
)

_FAILED = re.compile(r"^(?:FAILED|ERROR)\s+(\S+)", re.MULTILINE)


def _clear_pycache() -> None:
    for root in ("background", "tools", "tests", "company", "saas"):
        for cached in (PROJECT / root).rglob("__pycache__"):
            shutil.rmtree(cached, ignore_errors=True)


def _run_suite(suite: str, deselect: tuple[str, ...], stop_first: bool) -> dict:
    """One suite, one pass. Returns the failing node ids and the wall clock."""
    cmd = [sys.executable, "-m", "pytest", suite, "-q", "--tb=no", "-rfE",
           "-p", "no:cacheprovider"]
    for node in deselect:
        cmd += ["--deselect", node]
    if stop_first:
        cmd.append("-x")
    started = time.time()
    proc = subprocess.run(cmd, cwd=PROJECT, capture_output=True, text=True)
    out = proc.stdout + proc.stderr
    return {
        "suite": suite,
        "returncode": proc.returncode,
        "failed": sorted(set(_FAILED.findall(out))),
        "seconds": round(time.time() - started, 1),
        "tail": out.strip().splitlines()[-3:],
    }


def _baseline(results: dict, suites: tuple[str, ...], out_path: Path) -> dict:
    """The unmutated pass, per suite, recorded before anything is patched.

    ITS REDS ARE THE POINT. A test already red at HEAD reads as the mutation dying, in every row at
    once, and a battery that skips this step has measured that something failed rather than what.
    """
    baseline = results.setdefault("baseline", {})
    print("BASELINE (no mutation, full pass, reds recorded and later deselected)", flush=True)
    for suite in suites:
        if suite in baseline:
            continue
        r = _run_suite(suite, (), stop_first=False)
        baseline[suite] = r
        print(f"  {suite}: rc={r['returncode']} failed={len(r['failed'])} {r['seconds']}s",
              flush=True)
        out_path.write_text(json.dumps(results, indent=2))
    return baseline


def _score(row: dict, todo: list[str], known_red: dict) -> None:
    """One mutation against each outstanding suite, scored as a row rather than a verdict."""
    for suite in todo:
        r = _run_suite(suite, known_red[suite], stop_first=True)
        r["died"] = r["returncode"] != 0
        row["per_suite"][suite] = r
        print(f"  {suite}: {'DIED' if r['died'] else 'survived'} "
              f"({r['seconds']}s) {r['failed'][:2]}", flush=True)
    graded = row["per_suite"]
    row["survived_all"] = (len(graded) == len(SUITES)
                           and not any(r["died"] for r in graded.values()))
    row["killed_by"] = [s for s, r in graded.items() if r["died"]]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="/var/tmp/direction_battery_results.json")
    ap.add_argument("--pristine", default="/var/tmp/direction_pristine.py",
                    help="restore source, held OUTSIDE the tree on purpose")
    ap.add_argument("--only", nargs="*", default=None, help="mutation ids to run")
    ap.add_argument("--suites", nargs="*", default=None,
                    help="substring match; `tests/background/test_supervisor.py` costs ~670s a "
                         "pass and the other three cost seconds, so the cheap three are worth "
                         "grading and landing on their own first")
    args = ap.parse_args(argv)
    suites = tuple(s for s in SUITES if not args.suites
                   or any(frag in s for frag in args.suites))

    out_path = Path(args.out)
    pristine = Path(args.pristine)
    original = SUBJECT.read_text(encoding="utf-8")
    pristine.write_text(original, encoding="utf-8")

    def restore() -> None:
        if SUBJECT.read_text(encoding="utf-8") != original:
            SUBJECT.write_text(original, encoding="utf-8")
            _clear_pycache()

    atexit.register(restore)
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: sys.exit(130))

    results = json.loads(out_path.read_text()) if out_path.exists() else {}
    results.setdefault("subject", "background/direction.py")
    results.setdefault("suites", list(SUITES))

    baseline = _baseline(results, suites, out_path)
    known_red = {s: tuple(baseline[s]["failed"]) for s in suites}
    results.setdefault("mutations", {})

    for mid, contract, old, new in MUTATIONS:
        if args.only and mid not in args.only:
            continue
        row = results["mutations"].setdefault(mid, {"contract": contract, "per_suite": {}})
        todo = [s for s in suites if s not in row.get("per_suite", {})]
        if not todo:
            print(f"{mid}: all requested suites already recorded, skipping", flush=True)
            continue
        occurrences = original.count(old)
        if occurrences != 1:
            # NOT a survivor -- a patch that could never have applied. Recorded
            # as its own outcome so it can never be read as evidence.
            row["error"] = f"target present {occurrences} times, expected exactly 1"
            out_path.write_text(json.dumps(results, indent=2))
            print(f"{mid}: TARGET NOT UNIQUE ({occurrences}) -- not run", flush=True)
            continue
        SUBJECT.write_text(original.replace(old, new), encoding="utf-8")
        _clear_pycache()
        row["target_occurrences"] = occurrences
        print(f"\n{mid}: {contract}", flush=True)
        _score(row, todo, known_red)
        SUBJECT.write_text(original, encoding="utf-8")
        _clear_pycache()
        out_path.write_text(json.dumps(results, indent=2))

    restore()
    survivors = [m for m, r in results["mutations"].items() if r.get("survived_all")]
    partial = [m for m, r in results["mutations"].items()
               if len(r.get("per_suite", {})) < len(SUITES)]
    print(f"\nSURVIVED ALL FOUR SUITES: {survivors or 'none'}", flush=True)
    if partial:
        # NOT survivors. A mutation graded against three of four suites has no verdict on the
        # standing prediction, and printing it beside the survivors is how a partial run gets
        # read as a finished one.
        print(f"NOT YET GRADED ON EVERY SUITE (no verdict): {partial}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
