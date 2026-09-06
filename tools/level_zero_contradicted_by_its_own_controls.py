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

  CONTRADICTED  -- >=1 named control file, every one exists, every one was written no earlier
                   than the row itself, and the whole set PASSES. Refuses.
  UNGRADABLE    -- reported, never refuses. The row names no control file at all, or names one
                   that is not on disk, or names one OLDER THAN ITSELF, or the run could not be
                   completed. "I cannot grade this" is a finding about the row, not a verdict
                   about the work.
  (silent)      -- the named set exists and does not all pass. The map and the controls agree
                   that something is unbuilt. Nothing to say.

A CONTROL OLDER THAN THE ROW IS NOT EVIDENCE ABOUT THE ROW, and this is the leg the live tree
taught on 2026-09-06 -- the first draft did not have it and published a refusal because of that.
`H41_the_map_ratchet_has_no_ongoing_drain` was minted on 2026-08-10 and names
`tests/design/test_simplifications_store.py`, born 2026-08-05, four days earlier. All 41 of its
tests pass, so the first draft called the row CONTRADICTED and demanded a level move. But that
suite was passing before the atom existed: it grades the store's mechanics (roll, bounds,
orphans, duplicate tenants) and H41's deliverable is an ONGOING DRAIN, which does not exist --
measured, not argued, by the map refilling to 99.74% of its ceiling in the eleven days after the
one-off drain and wedging every lane's commit. The suite is green through exactly the failure
H41 exists to fix, because the narrative moved into `gain`, a field no tenant holds.

So the question "does the named set pass" is only a question ABOUT THIS ATOM when the atom's own
build is what wrote the set. Dating is how that is settled without trusting a commit-message
convention: if the control was already on disk when the row was minted, its passing today carries
no information about whether the row's work landed, and the row is UNGRADABLE ENTIRE for the same
fail-closed reason an absent path is -- grading the remainder would publish a verdict about a set
the row does not describe. On the live map the discriminator needs no tuning: SPINE_1's control was
born 2h41m AFTER its row, SITE4's in the SAME COMMIT as its row, and H41's four days before.

PROVENANCE THAT CANNOT BE ESTABLISHED DOES NOT DEGRADE TO REFUSING. No git history (a shallow
clone, a `git archive` extract, an uncommitted control) means the ages are unknown, and unknown
is UNGRADABLE, never CONTRADICTED -- the refusing verdict is the one that demands work, so it is
the one that must be earned. `--follow` is deliberate: without it a renamed suite dates from its
rename and reads as younger than it is, which fails in the refusing direction. Its known cost is
that rename detection works by SIMILARITY, so a new control that closely resembles an older file
can be followed back to it and read as older than it is -- that error direction is silence, not a
false demand, which is the trade this control is willing to make in that order.

A NAMED CONTROL THAT IS NOT ON DISK DOES NOT DEGRADE TO GRADING THE REST, and that is what the
live tree taught. Of the 34 candidate rows, ten named a test file at all and FOUR of those ten
named one that does not exist. Two of the four -- `PB4` and `PB6` -- are the very instances this
control was built for, and the reason their landed work was invisible is that each row names the
file the build MEANT to write and the build wrote a differently-named one. Grading the surviving
subset would publish a verdict about a set the row does not describe. So a row with any absent
named control is ungradable ENTIRE, the absent path is printed, and the fix is to repoint the row
at the control that exists. (PB4 and PB6 are repointed; `D9` and `PB5` remain, their work genuinely
unbuilt.)

A CONTRADICTED ROW MAY BE UNMOVABLE, and until 2026-09-06 this control said so only in a prose
footer under every row alike. The remedy it prints -- record the level -- is refused outright by
OPS11 (`background/gate_authorization.refuse_level_raise_if_lane_blocked`) for any atom whose lane
holds a live BLOCKING finding, and on the live map that is not the exception: `SITE4_ia_register_
and_nav` graded CONTRADICTED with 38 passing controls, and `H_harness` holds FOURTEEN blockers, so
the recording raises before it writes a row. `PB4` is the same shape in `W2_customer_generator`.
Both of the map's real contradictions are frozen, and a reader following the printed instruction
spends a turn discovering it.

So the verdict carries `frozen_by` -- the live blockers on the row's own lane, empty when there
are none -- and the two groups print different instructions, because they ARE different work: a
movable row is one recording away, a frozen one is a lane to discharge first. The row is still
CONTRADICTED either way and the exit code does not soften: frozen is why the map is wrong today,
never permission for it to stay wrong.

FAIL-CLOSED ON THE PROBE, in the direction that costs the reader nothing. If the lane cannot be
read at all, the row is reported frozen with that as the named reason rather than movable -- being
told "record this" on no information is the outcome this leg exists to stop, and the opposite
error merely sends a reader to look at a lane that turns out to be clear.

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
CONTROL_PREDATES_ROW = "names a control that was already on disk, and passing, before the row was"
PROVENANCE_UNKNOWN = "the age of the row or of its named controls could not be established"
RUN_UNAVAILABLE = "the named controls could not be run to a verdict"
BUDGET_EXHAUSTED = "the run budget was spent before this row was reached"

#: Stands in the `frozen_by` list when the lane's blockers could not be read. A string, in the
#: same list as the real finding names, so no caller can treat "unknown" as "clear" by looking
#: only at emptiness -- the shape that reads a not-found as a valid extreme.
BLOCKERS_UNREADABLE = "the lane's blocking findings could not be read"

#: Both halves of the map. A row minted into the live half and later closed keeps its ORIGINAL
#: minting commit only if both are searched, and dating it from the close would make every closed
#: row look younger than the controls its own build wrote.
MAP_PATHS = ("docs/design/maturity_map.yaml", "docs/design/maturity_map_closed.yaml")


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


def _oldest_commit_epoch(log_args: list[str], root: Path) -> float | None:
    """Unix time of the OLDEST commit `git log <log_args>` reports, or None if it reports none.

    None is "I cannot date this", never "it is infinitely old" -- the caller turns it into
    UNGRADABLE, and a not-found that fell back to an extreme is the shape that fabricates
    findings elsewhere in this repo.
    """
    try:
        r = subprocess.run(["git", "log", "--format=%ct", *log_args],
                           cwd=str(root), capture_output=True, text=True, timeout=60)
    except Exception:  # noqa: BLE001 -- no git, no history, no provenance; never a refusal
        return None
    lines = [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]
    if r.returncode != 0 or not lines:
        return None
    try:
        return float(lines[-1])
    except ValueError:
        return None


def controls_older_than_the_row(atom_id: str, controls: list[str],
                                root: Path = ROOT) -> tuple[list[str], list[str]]:
    """`(predating, undatable)` -- which named controls were already on disk when the row was
    minted, and which could not be dated at all.

    THE TWO OUTPUTS ARE KEPT APART because they carry different instructions: a predating control
    is repointed or the row is left alone as correctly-zero, while an undatable one means this
    tree cannot answer the question and the row must be graded somewhere with history. Collapsing
    them would print "older than the row" over a shallow clone, which is a claim nothing measured.

    If the ROW cannot be dated, every control is undatable -- "no predating controls" must never
    be readable out of "I could not look".

    The row is dated by the oldest commit whose diff of either map half mentions the atom id --
    `-S`, so a row moved between the halves or edited a hundred times still dates from its mint.
    """
    minted = _oldest_commit_epoch(["--diff-filter=AM", "-S{}".format(atom_id), "--", *MAP_PATHS],
                                  root)
    if minted is None:
        return [], list(controls)
    predating: list[str] = []
    undatable: list[str] = []
    for rel in controls:
        # --follow, so a suite that was renamed dates from its birth and not from the rename.
        born = _oldest_commit_epoch(["--follow", "--", rel], root)
        if born is None:
            undatable.append(rel)
        elif born < minted:
            predating.append(rel)
    return predating, undatable


def _lane_blockers(lane: str) -> list[str]:
    """The live BLOCKING findings holding `lane`, by document name.

    CALLS THE SHARED MECHANISM rather than re-reading the staging directory: `lane_blockers` is
    the same function OPS11 refuses with, so this cannot report a lane clear that the recorder
    then refuses. A second reading of the severity index here is how one control comes to
    disagree with the control it is describing.
    """
    from background.gate_authorization import lane_blockers  # local: keeps import cost off callers
    return [b.finding for b in lane_blockers(lane)]


def frozen_by(lane, blockers_for=_lane_blockers) -> list[str]:
    """Why a level raise on this lane would be refused today, or `[]` if it would not be.

    A row with no lane at all is UNREADABLE, not clear: OPS11 resolves the lane from the atom
    itself, so a missing one means the refusal cannot be predicted, and predicting "movable" is
    the answer that wastes the reader's turn.
    """
    if not isinstance(lane, str) or not lane.strip():
        return [BLOCKERS_UNREADABLE]
    try:
        return list(blockers_for(lane))
    except Exception:  # noqa: BLE001 -- an unreadable lane is never a clear lane
        return [BLOCKERS_UNREADABLE]


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
           clock=time.monotonic, ages=controls_older_than_the_row,
           blockers_for=_lane_blockers) -> tuple[list[dict], list[dict]]:
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
    # Cached per lane: the probe reads the whole severity index, and the rows that reach it share
    # a handful of lanes. Cached WITHIN the pass only, so a discharge landing mid-pass is picked
    # up by the next one rather than being held for the process's lifetime.
    lane_cache: dict = {}
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
        # Dating runs BEFORE the budget check and before the run: it costs a fraction of a second
        # against pytest's seconds-to-minutes, and a set that cannot be evidence about this atom
        # should not spend the pass's budget proving it passes.
        predating, undatable = ages(aid, controls, root)
        if predating:
            ungradable.append({
                "id": aid, "reason": CONTROL_PREDATES_ROW, "paths": predating,
                "detail": "these were passing before the atom was minted, so they say nothing "
                          "about whether its work landed -- repoint the row at a control this "
                          "atom's own build wrote, or leave the row at zero because it is right"})
            continue
        if undatable:
            ungradable.append({
                "id": aid, "reason": PROVENANCE_UNKNOWN, "paths": undatable,
                "detail": "no commit history for the row or the control here -- grade this row "
                          "in a tree that has one"})
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
            lane = atom.get("lane")
            if lane not in lane_cache:
                lane_cache[lane] = frozen_by(lane, blockers_for)
            contradicted.append({"id": aid, "lane": lane,
                                 "level_target": atom.get("level_target"),
                                 "paths": controls, "detail": detail,
                                 "frozen_by": lane_cache[lane]})
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
            # The label has to track the reason: printing ABSENT over a control that is on disk
            # and merely older than its row sends the reader to look for a missing file.
            label = {NAMED_CONTROL_ABSENT: "ABSENT",
                     CONTROL_PREDATES_ROW: "OLDER THAN THE ROW",
                     PROVENANCE_UNKNOWN: "UNDATABLE"}.get(u["reason"], "NAMED")
            for p in u["paths"]:
                sys.stderr.write("      {}: {}\n".format(label, p))
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

        def _row(c):
            sys.stderr.write("  {} (lane {}, target L{})\n".format(
                c["id"], c["lane"], c["level_target"]))
            for p in c["paths"]:
                sys.stderr.write("      PASSES: {}\n".format(p))
            sys.stderr.write("      {}\n".format(c["detail"]))

        # `.get`, because a caller may hand `main` verdicts built before this field existed --
        # and an absent field must read as "not known to be frozen", the same as the group it
        # would have landed in then. Never as frozen: that would invent a blocker.
        movable = [c for c in contradicted if not c.get("frozen_by")]
        frozen = [c for c in contradicted if c.get("frozen_by")]

        if movable:
            sys.stderr.write("  MOVABLE NOW -- the lane holds no live BLOCKING finding:\n")
            for c in movable:
                _row(c)
            sys.stderr.write(
                "\n  Fix by RECORDING the level the evidence supports\n"
                "  (background.gate_authorization.record_level_up_self_certified) and moving the "
                "row,\n"
                "  or -- if the passing controls do not in fact reach the atom's target -- by "
                "saying\n"
                "  so in the row, because a control that proves nothing about its atom is the "
                "finding.\n\n")

        if frozen:
            sys.stderr.write(
                "  CONTRADICTED BUT FROZEN -- the row is wrong AND the recording is refused.\n"
                "  This is not the check contradicting itself: OPS11 blocks a level raise in a\n"
                "  lane holding a live BLOCKING finding, so the fix here is the LANE, not the "
                "row.\n")
            for c in frozen:
                _row(c)
                for f in c["frozen_by"]:
                    sys.stderr.write("      FROZEN BY: {}\n".format(f))
            sys.stderr.write(
                "\n  Discharge (repair + a checked `**Discharged:**` line in the finding's header)\n"
                "  or accept (background.gate_authorization.record_limitation_accepted) the lane's\n"
                "  findings first. Do not attempt the recording: it raises LaneBlockedError and\n"
                "  writes nothing.\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
