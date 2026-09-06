#!/usr/bin/env python3
"""An atom at `level_current: 0` whose own named controls all PASS is contradicting itself.

THE DEFECT THIS EXISTS TO CATCH. `level_current: 0` with `loop_stage: build` is the map saying
"this is being worked on and nothing is built yet". Twice this stretch the work had landed --
tests, module, commit naming the atom -- and the row still read 0. Nothing anywhere could notice,
because every control that reads the map either keys on `level_current > 0`
(`tools/scope_evidence_ratchet.py`, by an argued design decision) or watches for level INCREASES
(`tools/level_promotion_gate.py`). The ABSENCE of a move that should have happened had no reader.

WHY IT IS NOT TIDINESS. `tools/lane_formation.py` derives `buildable_lanes` from exactly this
pair of fields, and the draw ranks off it. A row stuck at 0 is not a stale label -- it is a
permanently-buildable atom that keeps winning draws it has already been paid for, and it is why
the product share reads 0.00% over fifty commits while product work demonstrably landed. This
control guards the input to direction itself, which is the only reason it earns its place:
CLAUDE.md is right that a control over one's own controls is usually not worth having.

WHAT "THE CONTROLS NAMED IN ITS OWN ROW" MEANS, said before it is measured. A named control is a
`file_scope` entry whose basename matches `test_*.py`. A DIRECTORY is not a control, and this is
the load-bearing exclusion: `H40_full_suite_pollution_bisect` names `tests/`, and grading it
against the whole suite would grade every lane's work as that atom's evidence -- a green there
says nothing about H40 and a red there says nothing either. `SP2_2_rng_substream_primitive` names
`tests/simulation`. Both are scopes. Neither is a runnable claim about the atom, so neither is
graded, and the row is reported as ungradable rather than given a verdict it did not earn.

THREE VERDICTS, and the third is the one the first draft did not have.

  CONTRADICTED  -- >=1 named control file, every one exists, and the whole set PASSES. Refuses.
  UNGRADABLE    -- reported, never refuses. The row names no control file at all, or names one
                   that is not on disk, or the run could not be completed. "I cannot grade this"
                   is a finding about the row, not a verdict about the work.
  (silent)      -- the named set exists and does not all pass. The map and the controls agree
                   that something is unbuilt. Nothing to say.

A NAMED CONTROL THAT IS NOT ON DISK DOES NOT DEGRADE TO GRADING THE REST, and that is what the
live tree taught. Of the 34 candidate rows, ten named a test file at all and FOUR of those ten
named one that does not exist. Two of the four -- `PB4` and `PB6` -- are the very instances this
control was built for, and the reason their landed work was invisible is that each row names the
file the build MEANT to write and the build wrote a differently-named one. Grading the surviving
subset would publish a verdict about a set the row does not describe. So a row with any absent
named control is ungradable ENTIRE, the absent path is printed, and the fix is to repoint the row
at the control that exists. (PB4 and PB6 are repointed; `D9` and `PB5` remain, their work genuinely
unbuilt.)

WHY IT IS NOT A PRE-COMMIT GATE, measured rather than argued. It runs pytest over arbitrary named
files; `KNIFE3_wall_crossing_paydown` alone names twelve architecture suites. The first full pass
against the live tree was still running at SEVEN MINUTES. A gate that costs minutes gets bypassed,
and hook-bypass is a wall -- `background/head-green-census.timer` carries the same argument for the
same reason. So this runs at orientation, in `background/delivery_seat.py`, where the map is being
read for direction anyway and where the corrupted input actually does its damage. It is bounded
there by BOTH a per-atom timeout and a whole-pass budget; see `assess` for why one is not the other.

Run standalone:  python3 -m tools.level_zero_contradicted_by_its_own_controls
Exit 0 = no contradiction, 1 = a row says zero about work its own controls say is done.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from tools import maturity_map_store as map_store

ROOT = Path(__file__).resolve().parent.parent

#: Per-atom wall clock for the whole named set. A run that does not finish is UNGRADABLE, never
#: a pass -- the fail-closed direction here is silence, because only "everything passed" refuses.
DEFAULT_TIMEOUT_S = 900

CONTRADICTED = "contradicted"
UNGRADABLE = "ungradable"

#: Why a row could not be graded. Separate strings because they need different instructions: an
#: absent path is repointed, a directory-only row is given a control, a timeout is re-run, and a
#: row the budget never reached is re-run with a bigger one.
NO_CONTROL_NAMED = "names no control file a runner can execute"
NAMED_CONTROL_ABSENT = "names a control file that is not on disk"
RUN_UNAVAILABLE = "the named controls could not be run to a verdict"
BUDGET_EXHAUSTED = "the run budget was spent before this row was reached"


def named_controls(atom: dict) -> list[str]:
    """The `file_scope` entries that are executable controls, in the order the row names them.

    Basename `test_*.py` and nothing else. See the module docstring for why a directory is
    deliberately not a control -- it is the difference between grading this atom and grading
    the repository.
    """
    scope = atom.get("file_scope") or []
    if not isinstance(scope, list):
        return []
    out = []
    for entry in scope:
        rel = str(entry)
        base = rel.rsplit("/", 1)[-1]
        if base.startswith("test_") and base.endswith(".py"):
            out.append(rel)
    return out


def is_candidate(atom: dict) -> bool:
    """The partition this control speaks about: the map asserting nothing is built, while
    asserting the atom is actively being built."""
    return atom.get("level_current") == 0 and atom.get("loop_stage") == "build"


def run_controls(paths: list[str], root: Path = ROOT,
                 timeout_s: int = DEFAULT_TIMEOUT_S) -> tuple[bool | None, str]:
    """Run the whole named set in ONE pytest invocation. `(True, detail)` if all passed,
    `(False, detail)` if any did not, `(None, reason)` if no verdict could be reached.

    ONE INVOCATION IS THE RIGHT GRAIN because the question is exactly "does the named set pass",
    not "which member failed" -- and `-x` is deliberately absent: it stops at the first failure
    and would make the detail line name one file when several are red.
    """
    cmd = [sys.executable, "-m", "pytest", *paths, "-q", "--no-header", "-p", "no:randomly"]
    try:
        r = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True, timeout=timeout_s)
    except subprocess.TimeoutExpired:
        return None, "timed out after {}s".format(timeout_s)
    except Exception as exc:  # noqa: BLE001 -- a runner that cannot start is not a pass
        return None, "the runner could not be started ({})".format(exc)
    tail = [ln for ln in r.stdout.strip().splitlines() if ln.strip()]
    detail = tail[-1][:200] if tail else "pytest printed nothing (rc={})".format(r.returncode)
    if r.returncode == 0:
        return True, detail
    # rc 5 is "no tests collected" -- a file with nothing in it is not evidence of anything, and
    # calling it a pass would let an empty control file promote an atom.
    if r.returncode == 5:
        return None, "pytest collected no tests from the named set"
    return False, detail


def assess(atoms: list[dict], root: Path = ROOT, runner=run_controls,
           timeout_s: int = DEFAULT_TIMEOUT_S, budget_s: float | None = None,
           clock=time.monotonic) -> tuple[list[dict], list[dict]]:
    """`(contradicted, ungradable)` over the candidate partition. Rows whose controls do not all
    pass appear in neither: the map and the controls agree, and agreement is not a finding.

    `budget_s` BOUNDS THE WHOLE PASS, and a per-atom timeout is not a substitute for it -- that
    was measured, not reasoned. Six live rows are gradable and a per-atom cap of 120s leaves a
    worst case of twelve minutes, which is long enough to wedge the caller this was built for
    (`background/delivery_seat.py`, a three-hourly orientation whose brief has to arrive). Rows
    the budget never reaches are UNGRADABLE with their own reason, never silently dropped and
    never counted as passing: a check that quietly stops early reports a clean map.

    The budget is checked BEFORE each run rather than interrupting one in flight, so it bounds
    the pass at `budget_s + timeout_s` and not at `budget_s` -- stated because a reader who needs
    a hard ceiling needs both numbers, and the caller's real ceiling is the sum.
    """
    contradicted: list[dict] = []
    ungradable: list[dict] = []
    started = clock()
    for atom in atoms:
        if not is_candidate(atom):
            continue
        aid = atom.get("id")
        controls = named_controls(atom)
        if not controls:
            ungradable.append({"id": aid, "reason": NO_CONTROL_NAMED, "paths": [],
                               "detail": "file_scope names no test_*.py file"})
            continue
        absent = [p for p in controls if not (root / p).exists()]
        if absent:
            ungradable.append({"id": aid, "reason": NAMED_CONTROL_ABSENT, "paths": absent,
                               "detail": "repoint the row at the control that exists"})
            continue
        if budget_s is not None and clock() - started >= budget_s:
            ungradable.append({"id": aid, "reason": BUDGET_EXHAUSTED, "paths": controls,
                               "detail": "re-run this row alone: --atom {}".format(aid)})
            continue
        passed, detail = runner(controls, root, timeout_s)
        if passed is None:
            ungradable.append({"id": aid, "reason": RUN_UNAVAILABLE, "paths": controls,
                               "detail": detail})
        elif passed:
            contradicted.append({"id": aid, "lane": atom.get("lane"),
                                 "level_target": atom.get("level_target"),
                                 "paths": controls, "detail": detail})
    return contradicted, ungradable


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="machine-readable verdicts on stdout")
    ap.add_argument("--atom", action="append", default=None,
                    help="grade only these atom ids (repeatable)")
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_S)
    ap.add_argument("--budget", type=float, default=None,
                    help="bound the WHOLE pass in seconds; rows not reached are "
                         "reported ungradable rather than dropped")
    args = ap.parse_args(argv)

    try:
        atoms = map_store.load_live_atoms()
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(
            "[level-zero] ❌ the maturity map could not be read ({}), so this control could not "
            "run. An unavailable check is a failed check.\n".format(exc))
        return 1
    if args.atom:
        wanted = set(args.atom)
        atoms = [a for a in atoms if a.get("id") in wanted]

    contradicted, ungradable = assess(atoms, timeout_s=args.timeout,
                                      budget_s=args.budget)

    if args.json:
        json.dump({"contradicted": contradicted, "ungradable": ungradable}, sys.stdout, indent=2)
        sys.stdout.write("\n")

    if ungradable and not args.json:
        sys.stderr.write(
            "\n[level-zero] {} row(s) at level 0 / build CANNOT BE GRADED. This is a finding "
            "about the row, not a verdict about the work, and it does not refuse.\n".format(
                len(ungradable)))
        for u in ungradable:
            sys.stderr.write("  {}\n      {}\n".format(u["id"], u["reason"]))
            for p in u["paths"]:
                sys.stderr.write("      ABSENT: {}\n".format(p))
            if u["detail"]:
                sys.stderr.write("      {}\n".format(u["detail"]))

    if not contradicted:
        return 0

    if not args.json:
        sys.stderr.write(
            "\n[level-zero] ❌ {} atom(s) sit at `level_current: 0` with `loop_stage: build` "
            "while EVERY control their own row names PASSES. The map is saying nothing is built "
            "about work its own evidence says is done, and the draw reads these two fields to "
            "decide what to work on next.\n\n".format(len(contradicted)))
        for c in contradicted:
            sys.stderr.write("  {} (lane {}, target L{})\n".format(
                c["id"], c["lane"], c["level_target"]))
            for p in c["paths"]:
                sys.stderr.write("      PASSES: {}\n".format(p))
            sys.stderr.write("      {}\n".format(c["detail"]))
        sys.stderr.write(
            "\n  Fix by RECORDING the level the evidence supports\n"
            "  (background.gate_authorization.record_level_up_self_certified) and moving the row,\n"
            "  or -- if the passing controls do not in fact reach the atom's target -- by saying\n"
            "  so in the row, because a control that proves nothing about its atom is the finding.\n"
            "\n  THE RECORDING MAY ITSELF BE REFUSED, and that is not this check contradicting\n"
            "  itself. OPS11 blocks a level raise in a lane holding a live BLOCKING finding --\n"
            "  PB4 hit exactly that on this control's first real run, its lane's open finding\n"
            "  being about the very antecedent the atom builds. A row that is contradicted AND\n"
            "  correctly frozen is a real state: discharge or accept the lane's finding first.\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
