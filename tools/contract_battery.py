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
import fcntl
import hashlib
import json
import os
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

#: THE SAME REDS, KEPT APART. `_FAILED` unions pytest's two red words on purpose -- both are
#: reds and both must be deselected from the baseline -- and that union is what made `died`
#: unable to say what it had measured.
#:
#: MEASURED 2026-09-06 on `grid_intensity_fuel_mix`: rows M3, M4, M7, M9 and M10 all came back
#: DIED against `tests/tools/test_grid_intensity_feed_and_explore_carbon.py`, and all five named
#: the SAME node. Every one was `ERROR at setup` -- a module-scoped fixture that publishes off
#: the real caches raising before a single control body ran -- so five different contracts were
#: scored by one shared fixture and no control asserted anything about any of them. `-x` names
#: only the first red, so the log read exactly like five contracts being proved.
#:
#: An ERROR is still a red and still a kill; what it is not is EVIDENCE THAT A CONTROL FIRED.
#: This is a RESULT field, not a spec field: it is not in the hashed payload and adding it moves
#: no fingerprint in the family.
_ERRORED = re.compile(r"^ERROR\s+(\S+)", re.MULTILINE)

#: THE OTHER HALF OF THE SAME DOOR. `died_by_setup_error_only` watches ERROR-at-setup, where no
#: control body ran at all. A wrong-class exception raised INSIDE a control body -- before it
#: reaches any assertion -- is a FAILED, so it clears that stamp and the cell reads as a control
#: firing when none did.
#:
#: MEASURED 2026-09-06 on `grid_intensity_fuel_mix` row M10 at fingerprint `aa5ce7785789`: DIED,
#: `died_by_setup_error_only` FALSE, `errored` EMPTY, naming a control -- and BOTH control bodies
#: were red on `AttributeError: 'list' object has no attribute 'items'` from
#: `sim/elexon_fuel_outturn.py:845`, before either asserted anything. This is the family's known
#: weak spot: M2/M11 and M10/M14/M15 exist BECAUSE a wrong-type substitution reddens a suite on
#: the type system rather than on the property.
#:
#: WHY NO EXTRA PASS. The claim this work was drawn on said the class "is not in that output at
#: all" and that the round therefore had to change. Measured, it is not so: `-rfE` already prints
#: `FAILED <node> - <Class>: <message>`. What removes it is TERMINAL WIDTH -- pytest truncates the
#: summary line to `COLUMNS`, which defaults to 80 when the output is captured, and every node id
#: in this repository is longer than 80 characters on its own. So the class was being printed and
#: then cut off, and the fix is to stop capturing at 80. `_WIDE_COLUMNS` below is that fix, and it
#: costs nothing: no second pytest pass, which matters on a family whose slowest cell is 655s.
#:
#: A RESULT field, not a spec field: not in the hashed payload, so it moves no fingerprint.
_RED_DETAIL = re.compile(r"^(?:FAILED|ERROR)\s+(\S+)(?:\s+-\s+(.*?))?\s*$", re.MULTILINE)

#: Wide enough that no node id in this repository plus its exception class can be truncated. The
#: longest test path here is ~140 characters; 1,000 leaves the class intact with room to spare.
_WIDE_COLUMNS = "1000"

#: pytest's rewritten bare `assert x == y` prints as `assert x == y` with no class name at all.
_BARE_ASSERT = re.compile(r"^assert(\s|$)")

#: The classes that mean A CONTROL REACHED ITS VERDICT. `AssertionError` is an assert with a
#: message; `Failed` is `pytest.fail(...)` and `pytest.raises(...)` not raising -- both are the
#: control refusing on purpose. Every other class is the body dying before it could judge.
_CONTROL_FIRED = frozenset({"AssertionError", "Failed"})

#: `Name:` or a bare `Name` at the head of the summary detail.
_RED_CLASS = re.compile(r"^([A-Za-z_][\w.]*)\s*(?::|$)")


def _red_class(detail: str | None) -> str | None:
    """The exception class behind one red, or `None` where the line could not say.

    `None` IS NOT A CLEAN BILL. It is "the output did not carry the class", and every stamp built
    on it fails closed to `None` rather than to the flattering `False`.
    """
    if not detail:
        return None
    if _BARE_ASSERT.match(detail):
        return "AssertionError"
    matched = _RED_CLASS.match(detail)
    return matched.group(1) if matched else None


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
    #: The same exclusion at the NODE grain: individual tests, inside a file that is otherwise a
    #: genuine caller suite, whose subject is THIS module. Deselected from every caller column.
    #:
    #: `direct_suites` assumes a file is all one thing. `direction` is the subject that showed it
    #: need not be. All four of its caller columns import `background.direction` at module level
    #: and all four are legitimately the dedicated suite of a module that calls it -- so the
    #: file-grain question has no honest answer there, and `b3938b313` correctly shipped no gate
    #: on "imports the subject". Asked per TEST it is decidable and was decided by AST census:
    #: 23 tests across three of those files assert against `d.focus_multiplier`, `d.validate`,
    #: `d.wrong_rows` and `d.focus_weights` and never call the module their file is named for,
    #: while `test_EXPIRED_direction_offers_NOTHING` in the same file calls `dl.` and is a real
    #: caller test. Both live in `test_delivery_lane.py`; no file-level split can keep both.
    #:
    #: WHY THE COST OF GETTING THIS WRONG IS ASYMMETRIC, and why it is a declared list rather
    #: than the census run live: over-declaring hides real caller evidence and inflates the
    #: survivor count, which is the flattering direction. The list is fixed in the spec so it is
    #: reviewable beside the contracts it changes the meaning of, and the census that produced it
    #: is `SEAT_PREREG_WHETHER_ANY_TEST_WHOSE_SUBJECT_IS_A_CALLER_PROVES_ANY_DIRECTION_CONTRACT_2026-09-06.md`.
    direct_nodes: tuple[str, ...] = field(default_factory=tuple)
    #: THE THIRD ANSWER, and the case `direct_nodes` alone has to guess at.
    #:
    #: A node that asserts on the subject's API AND on a caller's, in one body. Kept in the run,
    #: flagged on the row, never counted as proof either way.
    #: `test_EXPIRED_direction_offers_NOTHING` asserts `d.unreachable_focus(...) == []` and
    #: `dl.next_item(...) is None` two lines apart -- so calling it a caller test understates it
    #: and deselecting it as the subject's own discards real caller evidence. Neither is right,
    #: and every published defect this sweep has found came from an instrument that picked a side.
    #: A row whose only caller kill lands here gets `killed_by_a_mixed_test` and no verdict.
    mixed_nodes: tuple[str, ...] = field(default_factory=tuple)
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

    def deselect_for(self, suite: str, known_red: tuple[str, ...] = ()) -> tuple[str, ...]:
        """What this suite runs WITHOUT: its baseline reds, plus -- for a CALLER column only --
        the tests in it whose subject is the module under mutation.

        The direct and repair columns keep their `direct_nodes`: those columns exist to report
        what the subject's OWN tests prove, so deselecting the subject's own tests from them
        would empty exactly the thing they measure.
        """
        nodes = self.direct_nodes if suite in self.suites else ()
        return tuple(known_red) + tuple(n for n in nodes if n.split("::")[0] == suite)

    def is_mixed(self, suite: str, node_id: str) -> bool:
        """Did this failure land on a node declared as asserting on BOTH sides.

        Matched on the un-parametrised id: `--deselect` and `failed` disagree about brackets, and
        a comparison that missed every parametrised test would leave the flag silently off for the
        commonest shape in this tree.
        """
        bare = node_id.partition("[")[0]
        return any(m.partition("[")[0] == bare for m in self.mixed_nodes
                   if m.split("::")[0] == suite)

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
    # COLUMNS IS LOAD-BEARING, not cosmetic. Captured output has no tty, so pytest truncates its
    # short summary to 80 columns and every node id here is longer than that on its own -- which
    # silently deletes the ` - <Class>: <message>` tail that `_red_class` reads.
    env = {**os.environ, "COLUMNS": _WIDE_COLUMNS}
    proc = subprocess.run(cmd, cwd=PROJECT, capture_output=True, text=True, env=env)
    out = proc.stdout + proc.stderr
    # Last writer wins per node, which is what we want: one node reported twice is reported the
    # same way twice, and a `None` detail never overwrites a class we already parsed.
    red_classes: dict[str, str | None] = {}
    for node, detail in _RED_DETAIL.findall(out):
        found = _red_class(detail)
        if found is not None or node not in red_classes:
            red_classes[node] = found
    return {
        "suite": suite,
        "returncode": proc.returncode,
        "failed": sorted(set(_FAILED.findall(out))),
        "errored": sorted(set(_ERRORED.findall(out))),
        "red_classes": dict(sorted(red_classes.items())),
        "seconds": round(time.time() - started, 1),
        # SQUEEZED, because `COLUMNS` above pads pytest's progress and banner lines out to its
        # full width -- and unsqueezed those three lines are ~3kB of spaces in every cell of
        # every results file. The content is unchanged; only runs of padding are collapsed.
        "tail": [re.sub(r"\s{3,}", "  ", line) for line in out.strip().splitlines()[-3:]],
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
            # THE SAME DESELECTION THE MUTATION ROUNDS WILL USE, and the round is worthless
            # without it. The floor must measure the population that is actually going to be
            # scored: a caller column whose only direction-reaching tests are `direct_nodes`
            # would otherwise be stamped `reaches` on the strength of tests no later round runs,
            # and every survivor it went on to report would read as UNPROVED when the honest
            # reading is UNREACHABLE -- the exact confusion this floor exists to prevent, let in
            # through the floor itself.
            r = _run_suite(suite, spec.deselect_for(suite, known_red.get(suite, ())),
                           stop_first=True)
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
            r = _run_suite(suite, spec.deselect_for(suite, known_red.get(suite, ())),
                           stop_first=True)
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
            r = _run_suite(suite, spec.deselect_for(suite, known_red.get(suite, ())),
                           stop_first=True)
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


def population_drift(spec: BatterySpec) -> str:
    """Does the spec's declared node list still match what the tree says. `""` when it does.

    WHY A DECLARED LIST NEEDS THIS AT ALL. `direct_nodes` is fixed in the spec so it is reviewable
    beside the contracts whose meaning it changes -- which is right, and is exactly what makes it
    rot. A test renamed, added, or turned from caller to subject leaves the spec still declaring
    yesterday's census while `survived_all` goes on reducing over a population that no longer
    exists, and nothing anywhere notices. `tools/subject_asserting_tests` is the census that
    produced the list; this is the check that it still describes the tree.

    BOTH DIRECTIONS, and the second is the one that would go unquestioned. Under-declaring lets
    the subject grade itself, which is the flattering error. Over-declaring deselects genuine
    caller tests and reports "no caller kills" about a population the run hollowed out itself --
    still a finding the instrument produced rather than the tree, and unflattering enough that
    nobody would challenge it.
    """
    from tools.subject_asserting_tests import census

    for suite in spec.suites:
        report = census(spec.subject, suite)
        declared = {n.split("::", 1)[1] for n in spec.direct_nodes
                    if n.split("::")[0] == suite}
        declared_mixed = {n.split("::", 1)[1] for n in spec.mixed_nodes
                          if n.split("::")[0] == suite}
        found = set(report.subject)
        if found - declared:
            return (f"{suite}: {sorted(found - declared)} assert on {spec.subject}'s own API and "
                    f"are NOT declared, so their kills would be published as caller evidence.")
        if declared - found:
            return (f"{suite}: {sorted(declared - found)} are declared and deselected but the "
                    f"census does not find them asserting on {spec.subject} -- real caller tests "
                    f"are being removed from the population.")
        if set(report.mixed) - declared_mixed:
            return (f"{suite}: {sorted(set(report.mixed) - declared_mixed)} assert on the subject "
                    f"AND on a caller in one body and are not declared, so their kills would "
                    f"enter `killed_by` with nothing marking them unattributable.")
    return ""


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


def _no_verdict_was_reached(r: dict) -> bool | None:
    """Did this kill come only from control bodies that died before asserting anything?

    THREE-VALUED, and the third value is the point. `None` means the run did not say what class
    the red was, which is not evidence that a control fired -- `False` there would be the
    flattering answer and the one a reader cannot tell from a real verdict.

    Scoped to reds that RAN A BODY (`failed` minus `errored`). A setup error never entered a body,
    so it is `died_by_setup_error_only`'s subject and not this one's, and a row cannot be stamped
    by both. A cell whose kill was entirely setup errors is `False` here, correctly: nothing is
    being said about bodies, because there were none.
    """
    # `r["died"]`, not `r.get("died")`: a cell without it is malformed, and a missing key must
    # raise rather than resolve to the flattering "no, nothing to say here".
    if not r["died"]:
        return False
    body_reds = set(r.get("failed") or ()) - set(r.get("errored") or ())
    if not body_reds:
        return False
    classes = [(r.get("red_classes") or {}).get(node) for node in body_reds]
    if any(cls in _CONTROL_FIRED for cls in classes):
        return False        # a control reached its verdict; the kill is evidence.
    if any(cls is None for cls in classes):
        return None         # the output did not carry the class. Fail closed.
    return True


def _score(spec: BatterySpec, row: dict, todo: list[str], known_red: dict, reaches: dict,
           grades_text: dict) -> None:
    """One mutation against each outstanding suite, scored as a row rather than a verdict."""
    for suite in todo:
        r = _run_suite(suite, spec.deselect_for(suite, known_red[suite]), stop_first=True)
        r["died"] = r["returncode"] != 0
        # A survivor in a suite the poison round could not redden is not evidence about the
        # contract. Stamped on the cell, because a caveat kept only in prose stops travelling with
        # the number the moment anyone reads the JSON.
        r["survived_but_unreachable"] = not r["died"] and reaches.get(suite) is False
        # A kill by a suite that reddens for a behaviour-preserving edit is not evidence the
        # contract is proved -- it may be reading the subject's bytes. `None` where the null
        # round did not run: unknown, never a clean bill.
        r["died_but_grades_text"] = r["died"] and grades_text.get(suite)
        # EVERY RED WAS A SETUP ERROR, so no control body executed and this kill grades a
        # fixture rather than the contract. Stamped on the cell for the same reason the two
        # above are: the caveat has to travel with the number, and `-x` shows only the first
        # red so the log cannot show it.
        r["died_by_setup_error_only"] = bool(
            r["died"] and r["failed"] and set(r["failed"]) == set(r["errored"]))
        # THE SAME DOOR ONE ROOM OVER. Every red that RAN A BODY died on a class that is not an
        # assertion, so the bodies executed and none of them ever reached a verdict -- the kill
        # grades the type system, not the contract. Disjoint from the stamp above by construction:
        # that one is about reds with no body at all, this one only looks at reds that had one.
        r["died_by_wrong_class_in_a_control_body"] = _no_verdict_was_reached(r)
        row["per_suite"][suite] = r
        print(f"  {suite}: {'DIED' if r['died'] else 'survived'} "
              f"{'(UNREACHABLE -- proves nothing) ' if r['survived_but_unreachable'] else ''}"
              f"{'(TEXT-GRADER -- may not have run the line) ' if r['died_but_grades_text'] else ''}"
              f"{'(SETUP ERROR -- no control body ran) ' if r['died_by_setup_error_only'] else ''}"
              f"{'(WRONG CLASS -- the body ran and never asserted) ' if r['died_by_wrong_class_in_a_control_body'] else ''}"
              f"{'(CLASS UNREADABLE -- cannot say a control fired) ' if r['died_by_wrong_class_in_a_control_body'] is None else ''}"
              f"({r['seconds']}s) {r['failed'][:2]}", flush=True)
    # `survived_all` is the PRE-REGISTERED question and its population is the CALLER suites.
    # The repair column and the subject's own direct suites are reported beside it and never
    # folded into it.
    callers = {s: r for s, r in row["per_suite"].items() if s in spec.suites}
    # THREE states, and the expression here wrote two of them. `len(callers) == len(spec.suites)
    # and not any(died)` is False both for a row graded on every caller that one of them KILLED --
    # a verdict, and the contract is proved -- and for a row that was never graded on some caller
    # at all, which is no verdict about anything. `None` for the second, because JSON `null` is
    # the one value a reader cannot mistake for an answer while `false` is the flattering one.
    #
    # LIVE, AND ON THIS SUBJECT. All eleven `fuel_mix` rows read `survived_all: false` at
    # fingerprint 95c9da4db380 because `tests/tools/test_ep13_embedded_generation_bound.py` costs
    # 605s a round and was excluded from the run -- so eleven rows said "proved" for a reason
    # unrelated to any contract. The summary line already printed NOT YET GRADED ON EVERY SUITE
    # honestly; only the JSON lied, and the JSON is what outlives the run.
    row["survived_all"] = (None if len(callers) < len(spec.suites)
                           else not any(r["died"] for r in callers.values()))
    # Named rather than left to be derived, because a `null` that does not say WHICH caller is
    # missing sends the reader back to diff two suite lists by hand. Always written, empty when
    # the row has a verdict: an absent key and "nothing missing" must not look the same.
    row["ungraded_callers"] = sorted(s for s in spec.suites if s not in callers)
    row["killed_by"] = [s for s, r in callers.items() if r["died"]]
    # THE THIRD ANSWER. A caller cell that died on a node asserting on the subject AND on a caller
    # is not a caller kill and is not a survival. `-x` makes this readable but not conclusive: it
    # names the FIRST failure only, so a caller test later in the file may also have failed and
    # would never appear. Reported as its own field for exactly that reason -- the row is
    # INDETERMINATE, and the one thing that must not happen is for it to be counted as proof.
    row["killed_by_a_mixed_test"] = sorted(
        s for s, r in callers.items()
        if r["died"] and any(spec.is_mixed(s, n) for n in r.get("failed", ())))
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
        # ...and the NODE-grain half of the same split, for the identical reason: declaring one
        # more test as the subject's own leaves `suites` and `direct_suites` both untouched,
        # changes no cell's measurement, and changes what every `survived_all` in the file means.
        "direct_nodes": list(spec.direct_nodes),
        "mixed_nodes": list(spec.mixed_nodes),
        "repair_suite": spec.repair_suite,
        "control_suites": list(spec.control_suites),
        # ids INCLUDED, but never alone: a renumbered mutation and a rewritten one are both
        # different work, and neither may adopt the other's cells.
        "mutations": [[mid, old, new] for mid, _contract, old, new in spec.mutations],
        "poison": [spec.poison_old, spec.poison_new],
        "null": [spec.null_old, spec.null_new],
    }, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def lock_path(out_path: Path) -> Path:
    """The claim file beside a results file. One per results file, never per spec."""
    return out_path.with_name(out_path.name + ".lock")


def claim_the_results_file(out_path: Path) -> tuple[object | None, str]:
    """Take an exclusive claim on `out_path`, or say who holds it. `(handle, held_by)`.

    THE DEFECT THIS CLOSES, 2026-09-06. `fingerprint` closed the two-SPEC collision: two different
    specs for one subject can no longer share a results file, because the hash of the work is in
    the default filename and a mismatched file is refused. It does nothing at all about the case
    it is structurally unable to see -- the SAME spec run twice. Identical spec, identical hash,
    identical `/var/tmp` path, nothing tree-scoped anywhere in it, and no lock of any kind. Two
    working trees running the same battery read the file once at the top and write it whole from
    memory at thirteen sites, so the loser's cells are silently adopted and then overwritten, and
    the survivor prints a verdict compiled from both runs' rows. **A fingerprint is the identity
    of the WORK, not of the RUN**, and the collision this instrument published on 2026-09-06 was
    a verdict no single run produced.

    Found by near-miss: a re-run was already in flight from the shared tree and this seat was one
    command from starting a second one.

    WHY `flock` AND NOT A PID FILE. A battery gets killed -- `pkill -f` on it matches the calling
    shell, which is why the pristine copy lives outside the tree at all. A pid file left by a
    killed run locks the instrument out until someone deletes it by hand, and the habit that
    grows from that is deleting the lock, which is the same as not having one. The kernel drops
    an `flock` when the holder's descriptor closes, including on `SIGKILL`, so there is no stale
    state to reason about and no reason to ever bypass it.

    The identity written INTO the file is for the refusal message only. It is never read to
    decide anything: the lock decides, and a claim whose text went missing is still a claim.
    """
    lock = lock_path(out_path)
    lock.parent.mkdir(parents=True, exist_ok=True)
    # "a+", never "w": opening to CONTEST a claim must not truncate the holder's identity, and
    # the contender opens this same path before it knows whether it has lost.
    handle = lock.open("a+", encoding="utf-8")
    try:
        # LOCK_NB is not an optimisation. A blocking acquire turns "another run holds this" from
        # a refusal that names its reason into a wait with no output, and this instrument is
        # routinely started, forgotten and reaped -- a battery that hangs silently at the top
        # reads exactly like a battery that is working. It was also measured: the mutation that
        # drops LOCK_NB does not redden the control, it HANGS it, taking the restore with it.
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        handle.seek(0)
        held_by = handle.read().strip() or "a run that recorded no identity"
        handle.close()
        return None, held_by
    handle.seek(0)
    handle.truncate()
    handle.write(json.dumps({"pid": os.getpid(), "tree": str(PROJECT),
                             "since": time.strftime("%Y-%m-%dT%H:%M:%S")}))
    handle.flush()
    return handle, ""


def release_the_results_file(handle: object) -> None:
    """Drop the claim. Explicit rather than left to process exit: several batteries run in one
    pytest process, and a claim held to exit would refuse every one after the first.

    The `LOCK_UN` is belt to `close()`'s braces and MEASURED to be an equivalence -- deleting it
    survives the battery over this control, because the kernel drops an `flock` when the
    descriptor closes. What is NOT redundant is doing either one in a `finally`: on a clean
    return the refcount would close the handle anyway, but a run that RAISES puts its frame, and
    this handle in it, on a traceback the reporting layer holds. The run that most needs the
    re-run to be possible is the one that would otherwise lock it out.
    """
    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    handle.close()


def _the_kernel_names_the_holder(handle: object) -> str:
    """Who holds the `flock` on this handle's inode, asked of `/proc/locks`. `""` when it cannot say.

    NOT a second store. The subject is a source file, so there is nowhere to write an identity
    record the way `claim_the_results_file` writes one beside the results file -- and inventing a
    sidecar for it would be two stores for one claim, which is a shape that can disagree with
    itself. The kernel's lock table cannot disagree with the lock, because it IS the lock.

    It can decline to answer: a filesystem that reports no inode, a format change, no `/proc`. That
    is reported as `""` and the refusal then says plainly that the holder could not be named,
    rather than guessing. An unavailable check must report itself unavailable.
    """
    try:
        st = os.fstat(handle.fileno())
        want = f"{os.major(st.st_dev):02x}:{os.minor(st.st_dev):02x}:{st.st_ino}"
        rows = Path("/proc/locks").read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""
    for row in rows:
        fields = row.split()
        # A BLOCKED WAITER is printed as `1: -> FLOCK ...`, one field wider than a holder. Nobody
        # waits on this lock while LOCK_NB stands, but a parser that silently misreads a row is
        # how "cannot tell" becomes permanent without anyone noticing.
        if len(fields) > 1 and fields[1] == "->":
            fields = fields[:1] + fields[2:]
        if len(fields) >= 6 and fields[1] == "FLOCK" and fields[5] == want:
            return f"pid {fields[4]}"
    return ""


def claim_the_subject_file(subject: Path) -> tuple[object | None, str]:
    """Take an exclusive claim on the SUBJECT, or say who holds it. `(handle, held_by)`.

    THE SECOND RESOURCE, AND THE SECOND SCOPE, 2026-09-06. `claim_the_results_file` guards a
    global `/var/tmp` path shared across working trees. The subject is the other resource and it
    is per-tree: every battery PATCHES IT IN PLACE and restores it at the end, so two runs over
    one subject interleave a mutation of one with the restore of the other, and each grades cells
    against a file the other wrote.

    The results lock cannot cover it, and correctly does not try. Two runs collide on the subject
    while their results files differ whenever the fingerprints differ -- two specs for one subject
    -- and, live today rather than latent, whenever a reader takes the results refusal's own
    documented escape: *"or pass a --out of your own"*. Follow that advice in the tree the other
    run is already grading and both runs write one source file, each holding a claim on a results
    file nobody is contesting.

    It was never unguarded, but the guard was `held_through_run`, which VOIDS a row whose subject
    did not hold. That is detection after the fact: the cost is a whole battery run discarded,
    where a refusal costs a wait. A control that can only report the damage is not the control.

    WHY THE SUBJECT ITSELF AND NOT A LOCK FILE BESIDE IT. Two reasons, and the first is the
    finding that produced this work: the design this repairs had a fail-open branch in it that its
    author did not see. A lock on a DERIVED path is open to exactly that -- any future caller that
    derives the name a hair differently (an unresolved symlink, a relative path, a `--subject`
    override) takes an uncontested claim on a name nobody else uses and proceeds. The inode cannot
    be derived wrongly, because it is not derived. The second: the tree-scoping falls out for free.
    Two worktrees hold two inodes for one repo path, and that is precisely the scope wanted -- a
    per-tree file, unlike the results file, is not contended across trees at all.

    `"r"`, and not a mode that could truncate: `flock` places no requirement on the open mode, and
    a claim that could damage its own subject on the way to being refused is worse than no claim.
    The mutation writes that follow open their own descriptor and truncate in place, which leaves
    the inode -- and so this claim -- exactly where it was.

    KNOWN LIMIT, stated rather than guarded: a claim follows the inode, so a `git` operation that
    REPLACES the subject by rename mid-run leaves this holding an unlinked file. That run's rows
    are void for a much louder reason than the lock, and `held_through_run` is what catches it.
    """
    # LOCK_NB for the reason `claim_the_results_file` gives at length, and it earns it twice here:
    # a battery is routinely started, backgrounded and forgotten, so a blocking acquire at the top
    # is silence that reads exactly like grading.
    handle = subject.open("r", encoding="utf-8")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        held_by = _the_kernel_names_the_holder(handle) or "a run the kernel would not name"
        handle.close()
        return None, held_by
    return handle, ""


def release_the_subject_file(handle: object) -> None:
    """Drop the claim on the subject. In a `finally`, for `release_the_results_file`'s reason:
    a run that RAISES leaves its frame, and this handle in it, alive on the traceback the
    reporting layer holds, so the run that most needs a re-run to be possible is the one that
    would otherwise lock the subject out. The clean-exit path is done for us by refcounting and
    proves nothing about this line.
    """
    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    handle.close()


def run(spec: BatterySpec, argv: list[str] | None = None) -> int:
    """Parse, take the exclusive claims on the results file AND the subject, and grade under both.

    Both claims are taken BEFORE the subject is read or the pristine copy is written, so a refused
    run has touched nothing: the losing run of a pair must not leave a pristine copy of a source
    the winner may have mutated at the moment it read it.

    TWO RESOURCES AT TWO SCOPES, so two claims -- the results file globally, the subject per tree.
    Neither implies the other in either direction, which is the whole reason the first one alone
    left the collision open. `LOCK_NB` on both means the order below cannot deadlock: a run that
    cannot have the second gives the first back and says so.
    """
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
    out_path = Path(args.out)
    handle, held_by = claim_the_results_file(out_path)
    if handle is None:
        # A DIFFERENT refusal from the fingerprint's, and a different exit code, because it has a
        # different remedy: that one says delete the file or use the default, this one says wait.
        print(f"REFUSED: {out_path} is already held by a battery run in flight ({held_by}). "
              f"This spec and that one are the same work, so the fingerprint cannot tell them "
              f"apart -- and two runs sharing one results file adopt and overwrite each other's "
              f"cells, publishing a verdict neither of them produced. Wait for it, or pass a "
              f"--out of your own.", flush=True)
        return 3
    try:
        subject_handle, subject_held_by = claim_the_subject_file(spec.subject_path)
        if subject_handle is None:
            # A THIRD refusal and a third exit code, because the remedy is a third thing again.
            # The fingerprint's says use a different file; the results lock's says wait or use a
            # --out of your own; this one says that a --out of your own is exactly what will NOT
            # help, because the contended thing is the source.
            print(f"REFUSED: {spec.subject} is already being mutated by a battery run in this "
                  f"tree ({subject_held_by}). Every battery patches its subject IN PLACE and "
                  f"restores it at the end, so two runs over one subject grade cells against a "
                  f"file the other wrote and each undoes the other's mutations. A --out of your "
                  f"own does NOT make this safe -- the results file is not what you are sharing. "
                  f"Wait for that run, or grade from a separate worktree.", flush=True)
            return 4
        try:
            return _grade_under_the_claim(spec, args, fp, out_path)
        finally:
            release_the_subject_file(subject_handle)
    finally:
        release_the_results_file(handle)


def _grade_under_the_claim(spec: BatterySpec, args: argparse.Namespace, fp: str,
                           out_path: Path) -> int:
    """The battery proper. Only ever called with this process holding `out_path`'s claim."""
    suites = tuple(s for s in spec.selectable if not args.suites
                   or any(frag in s for frag in args.suites))

    subject = spec.subject_path
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

    drift = population_drift(spec)
    if drift:
        # FAIL CLOSED, BEFORE THE BASELINE, and not left to the control that also checks this.
        # A test can be deselected, skipped, or simply not run; a battery run cannot, and this is
        # the moment the declaration actually shrinks a real population. A verdict reduced over a
        # population that has drifted from the tree is the defect the node grain exists to
        # correct, and publishing one from the instrument that finds it is how `ops_repo`'s eight
        # never-applied survivals reached a document.
        print(f"REFUSED: {spec.name}'s caller population has drifted from the tree. "
              f"{drift} Re-run `python3 -m tools.subject_asserting_tests --spec {spec.name}` "
              f"and update the spec; every caller cell below it would be scored over a "
              f"population this spec no longer describes.", flush=True)
        return 2

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
    indeterminate = [m for m, r in results["mutations"].items()
                     if r.get("killed_by_a_mixed_test")
                     and not (set(r.get("killed_by", [])) - set(r["killed_by_a_mixed_test"]))]
    if indeterminate:
        # Printed beside the survivors and NOT among them. These rows' only caller kill landed on
        # a node that asserts on the subject and on a caller in one body; the cell cannot say which
        # assert fired, so the row has no caller verdict either way.
        print(f"NO CALLER VERDICT -- only kill is a MIXED test (subject + caller in one body): "
              f"{indeterminate}", flush=True)
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
