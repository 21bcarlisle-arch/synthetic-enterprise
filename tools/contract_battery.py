#!/usr/bin/env python3
"""The per-caller-suite mutation battery engine, with the SUBJECT as a parameter.

This is `tools/direction_contract_battery.py`'s procedure with the subject,
suites and mutations lifted out. It was extracted rather than copied, on the
third subject of the convergence-evidence sweep, because the sweep's own finding
is that converged mechanisms proved through one caller die quietly when that
caller moves -- and a battery copied per subject would be that defect, committed
by the instrument that exists to find it.

WHAT THIS ANSWERS, AND WHAT IT DOES NOT
---------------------------------------
Not "is this contract proved" -- `tools/mutate_printed_figure_rederivation.py`
is that shape, and it asserts one NAMED test fires. This asks WHICH suite is
proving it, so every mutation runs against each suite SEPARATELY and the answer
is a row, never a pass/fail. A converged module inherits whichever caller suite
happened to be strongest, and the row is the only thing that says which.

THE FIVE THINGS THAT ARE NOT DECORATION
---------------------------------------
* **The reachability floor runs FIRST.** An import-time raise, before any
  mutation. A suite that stays green under it never reaches the subject, and
  every "survived" it reports afterwards means UNREACHABLE, not UNPROVED. Those
  are the same green and the flattering one is the one that gets written down.
  Earned on `direction.py`'s fourth column: eight survivals, all eight
  unreachable, four turns of the column unable to tell.
* **A SECOND floor runs for a subject whose callers catch the first one.** The
  first raises an `Exception`; a call site written `try: from <subject> import x`
  / `except Exception:` catches it and its suite stays green having run the
  caller end to end. The second raises a `BaseException`, which that handler
  does not catch, so green-then-red separates NEVER REACHES from
  REACHES-AND-SWALLOWS. Earned on `generate_company_data`, where two of the
  three callers are written exactly that way.
* **The target string is asserted present EXACTLY ONCE before patching.** A
  surviving mutation is otherwise indistinguishable from a patch that never
  applied, and this project has recorded that exact false survivor.
* **A BASELINE pass runs first and its reds are deselected** from every mutation
  run. A test already red at HEAD reads as the mutation dying, in every row at
  once.
* **The NULL round runs second.** A source edit that changes the bytes and the
  AST but cannot change behaviour. A suite that reddens under it is grading the
  subject's TEXT and its later kills are not execution evidence. The poison
  round asks whether a suite CAN redden for this subject; this asks whether it
  only reddens for the right reason. A subject with no null round is stamped
  UNKNOWN and says so on the summary line -- never a clean bill.
* **Restore is from a pristine copy held OUTSIDE the tree**, and results are
  written outside it too: `pkill -f` on a battery matches the calling shell, so
  an in-tree restore can be killed along with the thing it restores from, and an
  in-flight mutation left on disk is what makes `promote_worktree_landing`
  refuse.

A spec is a `BatterySpec`; see `direction_contract_battery.py` and
`segment_vocabulary_contract_battery.py` for the two live ones.
"""
from __future__ import annotations

import argparse
import atexit
import hashlib
import json
import re
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

#: Every first-party root. The direction battery listed five and that was
#: correct for its own subject; a subject in `simulation/` needs the rest, and a
#: stale `.pyc` under an unlisted root is a mutation that silently never applied.
_SOURCE_ROOTS = ("background", "tools", "tests", "company", "saas",
                 "simulation", "sim", "interface", "functions")

_FAILED = re.compile(r"^(?:FAILED|ERROR)\s+(\S+)", re.MULTILINE)


@dataclass(frozen=True)
class BatterySpec:
    """One subject: what to mutate, which suites to score it against, how to poison it."""

    #: Short slug, used for the default result and pristine paths.
    name: str
    #: The module under mutation, relative to the project root.
    subject: str
    #: The CALLER suites. `survived_all` is scored over exactly this population.
    suites: tuple[str, ...]
    #: `(id, contract, old, new)`. Each `old` must appear exactly once in the subject.
    mutations: tuple[tuple[str, str, str, str], ...]
    #: The reachability floor: a unique anchor in the subject, and that anchor with an
    #: import-time raise in front of it.
    poison_old: str
    poison_new: str
    #: THE SECOND FLOOR, for a subject whose CALL SITES catch what the first floor raises.
    #:
    #: The standard poison raises an `Exception`. `tools/generate_company_data.py` has three
    #: callers and TWO of them write `try: from tools.generate_company_data import ...` /
    #: `except Exception:` -- so the floor is caught at the call site and the suite stays GREEN
    #: while executing the caller end to end. That green is indistinguishable from a suite that
    #: never runs the caller at all, and the engine was stamping both as `NEVER REACHES`.
    #:
    #: This raise must not be an `Exception`. A `BaseException` subclass passes straight through
    #: `except Exception` and is still reported by pytest as a failure, so a suite green under
    #: the first floor and RED under this one is proved to run the call site and swallow the
    #: subject's failure -- `swallows_subject_failure`, a third state, and the one that reads
    #: most like the good answer.
    #:
    #: Run ONLY over the suites the first floor left green: for the rest the question is already
    #: answered and the round would cost a full pass to re-confirm it.
    hard_poison_old: str | None = None
    hard_poison_new: str | None = None
    #: A suite written AS THE REPAIR, scored as its own column and never folded into
    #: `survived_all` -- otherwise the pre-registered question becomes unanswerable the
    #: moment the repair lands.
    repair_suite: str | None = None
    #: The subject's OWN dedicated test files -- the suites that import it directly and are the
    #: only ones that can NAME one of its contracts. Scored as their own columns and, like
    #: `repair_suite`, never folded into `survived_all`.
    #:
    #: Same mechanism, different reason, and both are named rather than merged: a repair suite is
    #: written to close a gap the battery found, while these predate it. What they share is the
    #: only thing that matters to the reduction -- neither is a CALLER, so neither belongs in the
    #: population of "did anything OTHER than the subject's own tests prove this".
    #:
    #: THE DEFECT THIS CLOSES, 2026-09-06. Three of the five specs in this family wrote
    #: `SUITES = DIRECT_SUITES + CALLER_SUITES` and had nowhere else to put the direct column, so
    #: the subject graded itself and `survived_all`'s survivor count came out too LOW -- a
    #: contract killed only by the subject's own suite was struck off the caller survivor list by
    #: a suite no caller reaches through. Measured on both remaining subjects rather than argued:
    #: `segment_vocabulary` published "no contract on the busiest converged module is unproved"
    #: where three of eight are unproved by any caller, and `fuel_mix` published two of ten killed
    #: where the caller answer is ten of ten.
    #: `SEAT_RESULT_THREE_OF_SEGMENT_VOCABULARYS_CONTRACTS_ARE_PROVED_ONLY_BY_ITS_OWN_SUITE_AND_SO_WERE_BOTH_OF_FUEL_MIXS_2026-09-06.md`
    direct_suites: tuple[str, ...] = field(default_factory=tuple)
    #: Suites with NO import path to the subject. The poison round must leave these GREEN;
    #: if it reddens everything including these, the floor is measuring the harness and not
    #: the subject, and the whole round is void.
    control_suites: tuple[str, ...] = field(default_factory=tuple)
    #: THE NULL ROUND, and the mirror image of the poison round. A source edit that changes
    #: the BYTES and the AST but cannot change behaviour. Any suite that reddens under it is
    #: grading the subject's TEXT, not running it -- and its later kills are not evidence
    #: that a contract is proved.
    #:
    #: This is not hypothetical. `tools/generate_grid_intensity_feed.py` has six callers that
    #: do `(PROJECT_DIR / "tools" / "generate_grid_intensity_feed.py").read_text()` and walk
    #: the result as an AST. For a subject like that, `died` and "the suite executed the
    #: mutated line" are different claims, and every battery in this family has silently
    #: assumed they were the same.
    #:
    #: A subject with no null round is stamped `grades_text: null` -- UNKNOWN, never False.
    #: An unavailable check reports itself unavailable; it does not report a pass.
    null_old: str | None = None
    null_new: str | None = None

    @property
    def selectable(self) -> tuple[str, ...]:
        return (self.suites + self.direct_suites
                + ((self.repair_suite,) if self.repair_suite else ()))

    @property
    def scored_outside_the_caller_population(self) -> tuple[str, ...]:
        """Scored, reported, and never counted toward `survived_all`."""
        return self.direct_suites + ((self.repair_suite,) if self.repair_suite else ())

    @property
    def subject_path(self) -> Path:
        return PROJECT / self.subject


def _clear_pycache() -> None:
    for root in _SOURCE_ROOTS:
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


def _poison(spec: BatterySpec, results: dict, suites: tuple[str, ...], out_path: Path,
            known_red: dict) -> dict:
    """Can each suite go red for this subject AT ALL? Run before any mutation, never after.

    A battery whose cells are all green has measured nothing until this round has run: "the
    contract held" and "the suite never reached the line" are the same green. Recorded per suite as
    `reaches_subject`, and every later survivor in a suite that does not reach the subject is
    stamped `survived_but_unreachable` so the cell carries its own interpretation rather than
    relying on a reader to remember this one.

    `control_suites` are run under the same poison and must stay GREEN. Without them a floor that
    reddens every suite for a reason that has nothing to do with the subject -- a syntax error, a
    collection-time import of the whole tree -- reads exactly like total reachability.
    """
    subject = spec.subject_path
    poison = results.setdefault("poison", {})
    original = subject.read_text(encoding="utf-8")
    occurrences = original.count(spec.poison_old)
    if occurrences != 1:
        # The floor itself failed to apply. NOT recorded as "every suite reaches the subject" --
        # an unavailable check reports itself unavailable, it does not report a pass.
        results["poison_error"] = f"target present {occurrences} times, expected exactly 1"
        print(f"POISON: TARGET NOT UNIQUE ({occurrences}) -- reachability UNKNOWN", flush=True)
        out_path.write_text(json.dumps(results, indent=2))
        return poison
    todo = [s for s in tuple(suites) + spec.control_suites if s not in poison]
    if not todo:
        return poison
    print("POISON (import-time raise -- proves each suite can go red for this subject at all)",
          flush=True)
    poisoned = original.replace(spec.poison_old, spec.poison_new)
    subject.write_text(poisoned, encoding="utf-8")
    _clear_pycache()
    try:
        if subject.read_text(encoding="utf-8") != poisoned:
            results["poison_error"] = "subject on disk is not the poisoned text"
            return poison
        for suite in todo:
            is_control = suite in spec.control_suites
            r = _run_suite(suite, known_red.get(suite, ()), stop_first=True)
            r["reaches_subject"] = r["returncode"] != 0
            r["is_control"] = is_control
            poison[suite] = r
            label = "reaches" if r["reaches_subject"] else "NEVER REACHES"
            if is_control:
                label = ("CONTROL WENT RED -- floor is not discriminating"
                         if r["reaches_subject"] else "control stayed green (floor discriminates)")
            print(f"  {suite}: {label} the subject ({r['seconds']}s)", flush=True)
            out_path.write_text(json.dumps(results, indent=2))
    finally:
        subject.write_text(original, encoding="utf-8")
        _clear_pycache()
    return poison


def _hard_poison(spec: BatterySpec, results: dict, out_path: Path, known_red: dict,
                 reaches: dict) -> dict:
    """The second floor, run ONLY over the suites the first floor left green.

    The first floor raises an `Exception` at import time. A caller that writes
    `try: from <subject> import x` / `except Exception:` catches it, and its suite stays green
    having executed the call site end to end. That is a THIRD state -- not `NEVER REACHES`, not
    proved -- and the engine reported it as the first one, which is the flattering reading.

    This floor raises a `BaseException` subclass, which `except Exception` does not catch. A
    suite RED here after green above runs the call site and swallows the subject's failure.
    Returns `{suite: swallows}` for the suites this round graded.

    A suite still green under BOTH floors is genuinely blind, and `reaches` is left False.
    """
    if spec.hard_poison_old is None or spec.hard_poison_new is None:
        return {}
    todo_all = [s for s, hit in reaches.items() if not hit and s not in spec.control_suites]
    hard = results.setdefault("hard_poison", {})
    if not todo_all:
        print("HARD POISON: the first floor reddened every caller suite -- not run", flush=True)
        return {s: r["swallows_subject_failure"] for s, r in hard.items()}
    subject = spec.subject_path
    original = subject.read_text(encoding="utf-8")
    occurrences = original.count(spec.hard_poison_old)
    if occurrences != 1:
        # UNKNOWN, never a pass: without this round every green above stays ambiguous, and
        # saying so is the whole point of having it.
        results["hard_poison_error"] = f"target present {occurrences} times, expected exactly 1"
        print(f"HARD POISON: TARGET NOT UNIQUE ({occurrences}) -- swallowing UNKNOWN", flush=True)
        out_path.write_text(json.dumps(results, indent=2))
        return {}
    todo = [s for s in todo_all if s not in hard]
    if not todo:
        return {s: r["swallows_subject_failure"] for s, r in hard.items()}
    print("HARD POISON (BaseException -- passes through `except Exception` at the call site; "
          "separates NEVER REACHES from REACHES-AND-SWALLOWS)", flush=True)
    poisoned = original.replace(spec.hard_poison_old, spec.hard_poison_new)
    subject.write_text(poisoned, encoding="utf-8")
    _clear_pycache()
    try:
        if subject.read_text(encoding="utf-8") != poisoned:
            results["hard_poison_error"] = "subject on disk is not the hard-poisoned text"
            return {}
        for suite in todo:
            r = _run_suite(suite, known_red.get(suite, ()), stop_first=True)
            r["swallows_subject_failure"] = r["returncode"] != 0
            hard[suite] = r
            print(f"  {suite}: "
                  f"{'REACHES AND SWALLOWS the subjects failure' if r['swallows_subject_failure'] else 'genuinely blind (green under BOTH floors)'}"
                  f" ({r['seconds']}s)", flush=True)
            out_path.write_text(json.dumps(results, indent=2))
    finally:
        subject.write_text(original, encoding="utf-8")
        _clear_pycache()
    return {s: r["swallows_subject_failure"] for s, r in hard.items()}


def _null_round(spec: BatterySpec, results: dict, suites: tuple[str, ...], out_path: Path,
                known_red: dict) -> dict:
    """Which suites redden for a source change that CANNOT change behaviour?

    The poison round proves a suite can go red for this subject at all. It does not prove the
    suite reddens for the RIGHT REASON, and for a subject whose callers read its source text
    those are different questions. A suite that goes red here is grading bytes.

    Returns {suite: grades_text}. Absent key means the round did not run -- UNKNOWN, and every
    consumer below must treat it as unknown rather than as False.
    """
    if spec.null_old is None or spec.null_new is None:
        return {}
    subject = spec.subject_path
    null = results.setdefault("null_round", {})
    original = subject.read_text(encoding="utf-8")
    occurrences = original.count(spec.null_old)
    if occurrences != 1:
        results["null_error"] = f"target present {occurrences} times, expected exactly 1"
        print(f"NULL ROUND: TARGET NOT UNIQUE ({occurrences}) -- text-grading UNKNOWN", flush=True)
        out_path.write_text(json.dumps(results, indent=2))
        return {}
    todo = [s for s in suites if s not in null]
    if not todo:
        return {s: r["grades_text"] for s, r in null.items()}
    print("NULL ROUND (behaviour-preserving source edit -- a red here is a suite grading TEXT)",
          flush=True)
    subject.write_text(original.replace(spec.null_old, spec.null_new), encoding="utf-8")
    _clear_pycache()
    try:
        for suite in todo:
            r = _run_suite(suite, known_red.get(suite, ()), stop_first=True)
            r["grades_text"] = r["returncode"] != 0
            null[suite] = r
            if r["grades_text"]:
                print(f"  {suite}: GRADES THE TEXT -- its kills are not execution evidence "
                      f"({r['seconds']}s) {r['failed'][:2]}", flush=True)
            else:
                print(f"  {suite}: behaviour only ({r['seconds']}s)", flush=True)
            out_path.write_text(json.dumps(results, indent=2))
    finally:
        subject.write_text(original, encoding="utf-8")
        _clear_pycache()
    return {s: r["grades_text"] for s, r in null.items()}


def rows_without_a_caller_verdict(spec: BatterySpec, mutations: dict) -> list[str]:
    """Mutations graded on fewer than ALL the caller suites -- no verdict on the standing question.

    Counted over the CALLER cells, never over `per_suite`. `per_suite` also holds the direct and
    repair columns, so a row that never graded one caller can still carry MORE cells than there
    are callers, and a `len(per_suite) < len(spec.suites)` test would then stay silent about the
    one row with no verdict. That is live on `fuel_mix`: eight callers, one of them never graded
    at 655s a run, two direct columns, nine cells.
    """
    return [m for m, r in mutations.items()
            if len([s for s in r.get("per_suite", {}) if s in spec.suites]) < len(spec.suites)]


def _score(spec: BatterySpec, row: dict, todo: list[str], known_red: dict, reaches: dict,
           grades_text: dict) -> None:
    """One mutation against each outstanding suite, scored as a row rather than a verdict."""
    for suite in todo:
        r = _run_suite(suite, known_red[suite], stop_first=True)
        r["died"] = r["returncode"] != 0
        # A survivor in a suite the poison round could not redden is not evidence about the
        # contract. Stamped on the cell, because a caveat kept only in prose stops travelling with
        # the number the moment anyone reads the JSON.
        r["survived_but_unreachable"] = not r["died"] and reaches.get(suite) is False
        # A kill by a suite that reddens for a behaviour-preserving edit is not evidence the
        # contract is proved -- it may be reading the subject's bytes. `None` where the null
        # round did not run: unknown, never a clean bill.
        r["died_but_grades_text"] = r["died"] and grades_text.get(suite)
        row["per_suite"][suite] = r
        print(f"  {suite}: {'DIED' if r['died'] else 'survived'} "
              f"{'(UNREACHABLE -- proves nothing) ' if r['survived_but_unreachable'] else ''}"
              f"{'(TEXT-GRADER -- may not have run the line) ' if r['died_but_grades_text'] else ''}"
              f"({r['seconds']}s) {r['failed'][:2]}", flush=True)
    # `survived_all` is the PRE-REGISTERED question and its population is the CALLER suites.
    # The repair column and the subject's own direct suites are reported beside it and never
    # folded into it.
    callers = {s: r for s, r in row["per_suite"].items() if s in spec.suites}
    row["survived_all"] = (len(callers) == len(spec.suites)
                           and not any(r["died"] for r in callers.values()))
    row["killed_by"] = [s for s, r in callers.items() if r["died"]]
    # Reported as its own field rather than left to be read off `killed_by`'s absences: a contract
    # proved ONLY by the subject's own tests and a contract proved by nothing are different
    # claims, and `killed_by: []` says both.
    row["killed_by_own_suites_only"] = sorted(
        s for s in spec.scored_outside_the_caller_population
        if row["per_suite"].get(s, {}).get("died")) if not row["killed_by"] else []
    if spec.repair_suite is not None:
        repair = row["per_suite"].get(spec.repair_suite)
        if repair is not None:
            row["caught_by_own_suite"] = repair["died"]


def fingerprint(spec: BatterySpec) -> str:
    """What this run would actually DO, hashed. The resume key, and the default filename.

    THE DEFECT THIS CLOSES, 2026-09-06. `--out` defaulted to a path derived from the subject's
    NAME, and the resume cache was keyed by mutation ID. Every spec in this family numbers its
    mutations `M1`..`M8`, so two specs for one subject collided on both at once. A second lane had
    written its own eight `ops_repo` contracts to the default path; a run of a DIFFERENT eight
    contracts then found every id already present, ran nothing but one outstanding control suite,
    and printed `SURVIVED ALL 3 CALLER SUITES: M1..M8` -- a complete verdict on mutations it had
    never applied, with the other lane's contract TEXT attached to each row, because
    `setdefault` keeps whichever contract string got there first.

    That is precisely the class this instrument exists to find, committed by the instrument: a
    result reported as evidence of running code that no run produced. It hashes the mutations'
    OLD and NEW text rather than their ids, so a spec that changes one character cannot inherit
    a cell scored against the previous one.
    """
    payload = json.dumps({
        "subject": spec.subject,
        "suites": list(spec.suites),
        # The SPLIT is hashed, not just the union: moving a suite from `suites` to `direct_suites`
        # leaves every cell measuring exactly what it measured before and changes what
        # `survived_all` MEANS. A resumed row keeps the verdict it was written with, so a spec
        # that re-splits its population must not be able to inherit one.
        "direct_suites": list(spec.direct_suites),
        "repair_suite": spec.repair_suite,
        "control_suites": list(spec.control_suites),
        # ids INCLUDED, but never alone: a renumbered mutation and a rewritten one are both
        # different work, and neither may adopt the other's cells.
        "mutations": [[mid, old, new] for mid, _contract, old, new in spec.mutations],
        "poison": [spec.poison_old, spec.poison_new],
        "null": [spec.null_old, spec.null_new],
    }, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def run(spec: BatterySpec, argv: list[str] | None = None) -> int:
    fp = fingerprint(spec)
    ap = argparse.ArgumentParser(description=f"contract battery: {spec.subject}")
    # The fingerprint is IN the default filename, so two specs for one subject cannot collide by
    # default at all. The refusal below is still there and is the part that can fail: a reader who
    # passes `--out` explicitly, as both colliding runs did, walks straight past this.
    ap.add_argument("--out", default=f"/var/tmp/{spec.name}_battery_{fp}.json")
    ap.add_argument("--pristine", default=f"/var/tmp/{spec.name}_pristine.py",
                    help="restore source, held OUTSIDE the tree on purpose")
    ap.add_argument("--only", nargs="*", default=None, help="mutation ids to run")
    ap.add_argument("--suites", nargs="*", default=None,
                    help="substring match; a subject with one slow caller suite is worth "
                         "grading and landing on the cheap ones first")
    args = ap.parse_args(argv)
    suites = tuple(s for s in spec.selectable if not args.suites
                   or any(frag in s for frag in args.suites))

    subject = spec.subject_path
    out_path = Path(args.out)
    pristine = Path(args.pristine)
    original = subject.read_text(encoding="utf-8")
    pristine.write_text(original, encoding="utf-8")

    def restore() -> None:
        if subject.read_text(encoding="utf-8") != original:
            subject.write_text(original, encoding="utf-8")
            _clear_pycache()

    atexit.register(restore)
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: sys.exit(130))

    results = json.loads(out_path.read_text()) if out_path.exists() else {}
    stored = results.get("spec_fingerprint")
    if results and stored != fp:
        # FAIL CLOSED, and name the reason. An absent fingerprint is refused as hard as a wrong
        # one: a file written before this check existed cannot say which spec scored it, and
        # "cannot tell" is not "matches". Refusing costs one re-run; resuming costs a published
        # verdict on mutations that were never applied, which is what happened on 2026-09-06.
        print(f"REFUSED: {out_path} was written by a DIFFERENT spec for this subject "
              f"(stored fingerprint {stored!r}, this spec {fp!r}). Its rows are not evidence "
              f"about these mutations and resuming would report them as if they were. "
              f"Use the default --out, or delete that file.", flush=True)
        return 2
    results["spec_fingerprint"] = fp
    results.setdefault("subject", spec.subject)
    results.setdefault("suites", list(spec.suites))

    baseline = _baseline(results, suites, out_path)
    known_red = {s: tuple(baseline[s]["failed"]) for s in suites}
    # BEFORE the mutations, not after: a survivor scored against a suite whose reachability is
    # still unknown has to be re-read once it is, and this battery has already published one
    # column that needed exactly that.
    poison = _poison(spec, results, suites, out_path, known_red)
    reaches = {s: r["reaches_subject"] for s, r in poison.items()}
    # The second floor, over the suites the first one left green. A caller that catches what the
    # first floor raises makes its suite look blind, and blind and swallowing want opposite
    # readings of the same green cell: one says the row proves nothing, the other says the row
    # proves nothing AND the call site cannot propagate a failure of the subject at all.
    swallows = _hard_poison(spec, results, out_path, known_red, reaches)
    for suite, does in swallows.items():
        if does:
            reaches[suite] = True
            results["poison"][suite]["swallows_subject_failure"] = True
    # After the floor and before the mutations: the floor says a suite CAN redden for this
    # subject, the null round says whether it only reddens for BEHAVIOUR.
    grades_text = _null_round(spec, results, suites, out_path, known_red)
    results.setdefault("mutations", {})

    for mid, contract, old, new in spec.mutations:
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
        mutated = original.replace(old, new)
        subject.write_text(mutated, encoding="utf-8")
        _clear_pycache()
        row["target_occurrences"] = occurrences
        print(f"\n{mid}: {contract}", flush=True)
        _score(spec, row, todo, known_red, reaches, grades_text)
        # Asserted AFTER the run as well as before it: a restore racing the suites, or a
        # concurrent lane writing the file, would otherwise leave a green row that was measured
        # against pristine source.
        row["held_through_run"] = subject.read_text(encoding="utf-8") == mutated
        if not row["held_through_run"]:
            print(f"{mid}: SUBJECT DID NOT HOLD THROUGH THE RUN -- row is void", flush=True)
        subject.write_text(original, encoding="utf-8")
        _clear_pycache()
        out_path.write_text(json.dumps(results, indent=2))

    restore()
    survivors = [m for m, r in results["mutations"].items() if r.get("survived_all")]
    partial = rows_without_a_caller_verdict(spec, results["mutations"])
    print(f"\nSURVIVED ALL {len(spec.suites)} CALLER SUITES: {survivors or 'none'}", flush=True)
    own_only = [m for m, r in results["mutations"].items() if r.get("killed_by_own_suites_only")]
    if own_only:
        # `killed_by: []` reads as "nothing proves this" and for these rows it is wrong: something
        # proves them, and it is the subject's own test file rather than any caller.
        print(f"PROVED ONLY BY THE SUBJECT'S OWN SUITES (no caller kills these): {own_only}",
              flush=True)
    if partial:
        # NOT survivors. A mutation graded against a subset of suites has no verdict on the
        # standing prediction, and printing it beside the survivors is how a partial run gets
        # read as a finished one.
        print(f"NOT YET GRADED ON EVERY SUITE (no verdict): {partial}", flush=True)
    blind = [s for s, hit in reaches.items()
             if not hit and s not in spec.control_suites]
    if blind:
        # Printed beside the survivors and not in a footnote: these suites contributed a green
        # cell to every row above and not one of those cells was ever at risk.
        print(f"SUITES THAT NEVER REACH THE SUBJECT (their green cells prove nothing): {blind}",
              flush=True)
        if spec.hard_poison_old is None:
            # An `except Exception` at the call site produces this exact green. Without the
            # second floor "never reached it" and "reached it and caught the failure" are one
            # word, and only the first one is written down.
            print("  -- NO SECOND FLOOR FOR THIS SUBJECT: whether any of those suites in fact "
                  "RUN the call site and catch the subject's failure is UNKNOWN, not ruled out.",
                  flush=True)
    catchers = sorted(s for s, does in swallows.items() if does)
    if catchers:
        results["swallows_subject_failure"] = catchers
        out_path.write_text(json.dumps(results, indent=2))
        print("SUITES THAT RUN THE CALL SITE AND SWALLOW THE SUBJECT'S FAILURE (green under the "
              f"first floor, red under the second -- reached, and no failure can propagate): "
              f"{catchers}", flush=True)
    if "hard_poison_error" in results:
        print(f"SWALLOWING UNKNOWN -- {results['hard_poison_error']}", flush=True)
    # THE FLOOR IS NECESSARY AND NOT SUFFICIENT, measured on subject 6 (`ops_repo`, 2026-09-06).
    # All three of its caller suites reddened under the import-time poison -- and every one of the
    # eight mutations survived all three, because each caller imports the subject at module scope
    # and then patches `commit_and_push` BY NAME in its own namespace. There are three states here
    # and the summary could print only two: never imports it (blind, above); imports it and never
    # executes the contract (this); and executes it. The middle one is the more dangerous, because
    # a blind column at least announces itself as blind while this one reads as the good answer.
    #
    # It was already in the record and unreported: subject 4 (`segment_vocabulary`) carried
    # `tests/simulation/test_population_draw.py` and `tests/sim/test_segment_debt_obligation.py`
    # in exactly this state, graded on eight mutations each, killing nothing.
    #
    # Stamped into the JSON as well as printed -- a caveat kept only in a summary line stops
    # travelling the moment anyone reads the file.
    def _cells(suite: str) -> list[dict]:
        # Only the cells this suite ACTUALLY has. A suite with no graded cell is left out rather
        # than counted as proving nothing: "not yet asked" is not "answered no", and a partial run
        # is exactly when that conflation would be believed.
        return [r["per_suite"][suite] for r in results["mutations"].values()
                if not r.get("error") and suite in r.get("per_suite", {})]

    inert = sorted(s for s in reaches
                   if reaches[s] and s not in spec.control_suites
                   and _cells(s) and not any(c["died"] for c in _cells(s)))
    results["imports_but_proves_nothing"] = inert
    for suite in inert:
        results["poison"][suite]["imports_but_proves_nothing"] = True
    out_path.write_text(json.dumps(results, indent=2))
    if inert:
        print("SUITES THAT REACH THE SUBJECT AND STILL PROVE NOTHING (imported, never executed -- "
              f"the poison floor does NOT cover this): {inert}", flush=True)
    hot_controls = [s for s in spec.control_suites if reaches.get(s)]
    if hot_controls:
        print(f"CONTROL SUITES WENT RED UNDER THE POISON -- the floor did not discriminate and "
              f"the reachability column is VOID: {hot_controls}", flush=True)
    textual = [s for s in suites if grades_text.get(s)]
    if textual:
        print(f"SUITES THAT REDDEN FOR A BEHAVIOUR-PRESERVING EDIT (their kills are not "
              f"execution evidence): {textual}", flush=True)
    elif not grades_text:
        # Said out loud rather than left as a silent absence: no null round ran, so nothing
        # here distinguishes a kill by execution from a kill by reading the source.
        print("NO NULL ROUND FOR THIS SUBJECT -- whether any kill above came from reading the "
              "subject's TEXT rather than running it is UNKNOWN, not ruled out.", flush=True)
    if "null_error" in results:
        print(f"TEXT-GRADING UNKNOWN -- {results['null_error']}", flush=True)
    if "poison_error" in results:
        print(f"REACHABILITY UNKNOWN -- {results['poison_error']}", flush=True)
    return 0
