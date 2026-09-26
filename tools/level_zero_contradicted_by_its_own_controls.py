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
                   that something is unbuilt. Nothing to say. REACHED TWO WAYS since 2026-09-25:
                   by running the set, or -- without spending a run -- because a member of it is
                   recorded RED AT HEAD. See `reds_at_head`; the second route is what makes the
                   rows naming the most controls gradable at all.

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
build wrote SOMETHING in the set. Dating is how that is settled without trusting a commit-message
convention: a control already on disk when the row was minted carries no information about whether
the row's work landed. On the live map the discriminator needs no tuning: SPINE_1's control was
born 2h41m AFTER its row, SITE4's in the SAME COMMIT as its row, and H41's four days before.

AND THE TEST IS "IS ANY OF IT THE ATOM'S OWN", not "is none of it older" -- corrected 2026-09-25
against the live map, where the first spelling refused 28 rows and graded none. An atom that
EXTENDS an existing suite necessarily names a control older than itself, and that is the ordinary
shape rather than the exception: `KNIFE3_wall_crossing_paydown` names twelve, nine born after the
row and three before it because the atom cut into suites that already existed. One predating entry
threw the other nine away. So a row is ungradable for age only when EVERY named control predates it
-- H41's shape, both of its suites older than the row -- and a mixed set is graded on the whole of
itself. Nothing is loosened by that: CONTRADICTED still needs the WHOLE named set to pass, so a
predating control can only ever silence a row and never refuse one.

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

WHICH TREE THE PROBE READS, and it is not the obvious one. OPS11 fires inside the pre-commit gate,
and `surgical_land` runs that gate against THE TREE THE COMMIT WOULD CREATE -- so the staging
directory that decides the refusal is `HEAD`'s, not the working copy's. Until 2026-09-15 this
probe read only the working copy, and in a shared worktree the two routinely disagree: a sibling
lane had moved nine findings into `docs/staging/done/` without committing the move, the working
copy therefore showed `H_harness` clear, the scan printed MOVABLE NOW for `SITE4_ia_register_and_
nav`, and the gate found those nine still live at `HEAD` and refused. Both readings were right
about the tree each looked at, and the reader paid exactly the turn `frozen_by` exists to save.

So the probe reads BOTH and takes the UNION, which is the fail-closed direction stated as a rule:
an uncommitted archival is a discharge that has not happened yet, so trees that DISAGREE mean
frozen, never movable. A finding live only at `HEAD` is printed with that said on its own line,
because `find docs/staging` will not show it and the next reader would otherwise call it a ghost.

A ROW NAMING A SUITE THAT IS ALREADY RED AT HEAD DOES NOT NEED ITS RUN, and until 2026-09-25
this instrument was bounded by COST rather than by evidence because of it. Production caps each
atom at sixty seconds (`background/delivery_seat._LEVEL_ZERO_TIMEOUT_S`, deliberately -- the
orientation's brief has to arrive) and `KNIFE3_wall_crossing_paydown`'s twelve suites cost 1078s
and 2.44 GB, so the rows naming the MOST controls were exactly the ones that could never be
weighed: the pass returned population 28 and graded 0. CONTRADICTED needs the whole named set to
pass, so a set holding a test red at HEAD cannot reach it whatever the run costs -- and the
expensive row is the likeliest to hold one. The register is read for that, the row resolves to
SILENT, and no run is spent. It is the predating-control leg's argument again: this can only ever
SILENCE a row and can never be the thing that refuses one, so nothing is loosened.

IT FAILS CLOSED ON THE REGISTER ITSELF. Unobserved, undated or older than a week and the row
falls through to the run exactly as before. The observation store is UNTRACKED machine state, so
in an isolated worktree or a `git archive` extract it is simply absent and every row fails closed
-- which is the honest answer there and not a degradation, because "I could not look" must never
be readable as "nothing is red". One missing file must not be able to silence a whole partition.

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
import io
import json
import subprocess
import sys
import tarfile
import tempfile
import time
from datetime import datetime, timezone
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
CONTROL_PREDATES_ROW = ("names ONLY controls that were already on disk, and passing, before "
                        "the row was")
PROVENANCE_UNKNOWN = "the age of the row or of its named controls could not be established"
RUN_UNAVAILABLE = "the named controls could not be run to a verdict"
BUDGET_EXHAUSTED = "the run budget was spent before this row was reached"

#: WHY A ROW CANNOT BE GRADED, which is a different question from the reason above and the one
#: the census could not answer for twelve briefs. NO_CONTROL_NAMED and NAMED_CONTROL_ABSENT are
#: shapes of the row's `file_scope`; these are states of the WORK, and the repairs do not overlap.
#: A row honestly unbuilt and a row whose pointer rotted were counted as one number, and that
#: number then did not move -- which read as a stuck census rather than as a mixed class.
#:
#: A row may carry MORE THAN ONE, and `ungradable_causes` returns a list for that reason: `A51`
#: has a subject path that moved AND names a control nobody wrote, and a single primary cause
#: would send the reader to repoint the pointer and call the row repaired. A mixed class is
#: resolved by its sub-breakdown or refused, never summarised whole.
POINTER_ROT = "a named path is absent here and git knows it, so the pointer rotted"
CONTROL_NEVER_WRITTEN = "the subject is on disk and the control that would grade it was never written"
HONESTLY_UNBUILT = "no named file exists, so the row is RIGHT to read zero and owes no repair"
NAMES_ONLY_A_SCOPE = ("the row's control evidence is a DIRECTORY and not a file, so no file-level "
                      "evidence exists either way")
#: A SEVENTH CAUSE, and it was carved out of `CONTROL_NEVER_WRITTEN` on 2026-09-25 because that
#: class was a mixed one and the larger half of it was being told the wrong thing.
#:
#: `CONTROL_NEVER_WRITTEN` is published -- in its own string above, and in the table in
#: `docs/staging/done/WORKER_RESULT_THE_THIRTY_ONE_UNGRADABLE_ROWS_ARE_FIVE_CAUSES...` -- as
#: "path absent AND unknown to git, subject on disk". Measured against the live map on 2026-09-25:
#: SIXTEEN of the 28 candidate rows carried it, and only TWO of those sixteen had an absent path at
#: all. The other fourteen reached it through the `elif not controls` leg, where nothing is absent
#: and NOTHING WAS MEASURED about whether a control exists -- the row simply does not name one.
#:
#: WHY THAT MATTERS AND IS NOT A NAMING QUIBBLE. "never written" is a claim about the WORK, and the
#: repair it prints tells the reader to write the named control. For these rows there is no named
#: control to write, so the instruction is unfollowable; worse, the claim may be false in the
#: direction that hides landed work. This module's own docstring records the shape: `PB4` and `PB6`
#: are rows whose build DID write a control, under a name the row does not cite. A row that names
#: no control cannot tell those two worlds apart, and saying "never written" picks one of them
#: without looking. "We cannot tell from this row" is the result, and it belongs on the surface.
CONTROL_UNNAMED = ("the row names no control at all, so whether one was ever written is not a "
                   "question this row can answer")
#: AN EIGHTH CAUSE, and it is the SUBJECT-SIDE twin of `CONTROL_NEVER_WRITTEN`, added 2026-09-25
#: because its absence was what let `NOTHING_IN_THE_ROW` publish a false sentence.
#:
#: A path can be absent for three reasons and this module already named two of them: git knows it
#: (`POINTER_ROT`) and git cannot be asked (`CAUSE_UNDECIDABLE`). The third -- absent, and git has
#: never heard of it -- was reported only when the path was a CONTROL, or when EVERY named file was
#: absent (`HONESTLY_UNBUILT`). A row naming one subject that was never written alongside another
#: that was fell through every branch to `NOTHING_IN_THE_ROW`, whose text reads *"every named path
#: is on disk"*. It was not, and the reader was told the refusal lived in the pass and to go and
#: re-run rather than to look at the row.
SUBJECT_NEVER_WRITTEN = ("a named subject is absent and git has never known it, so part of what "
                         "the row claims to cover was never built")
#: A NINTH AND A TENTH CAUSE, added 2026-09-26, and they split the one instruction in this module
#: that named a relation the repository does not record.
#:
#: `CONTROL_PREDATES_ROW` prints TWO exits -- *"repoint the row at a control this atom's own build
#: wrote, OR leave the row at zero because it is right"* -- and gives the reader nothing to decide
#: between them with. MEASURED 2026-09-26 over the eight live members: two different proxies for
#: "a control this atom's own build wrote" answered 4-of-8 and 8-of-8 over the SAME eight rows.
#: The first grepped commit messages for the atom id, which matches `NEXT:` trailers, claim ids and
#: map-diff prose -- it offered `test_surgical_land_rederives_on_merge.py` as W2_18's own control.
#: The second joined on "a commit that touched a named subject and created a test", which a
#: long-lived subject like `simulation/population_draw.py` makes true of nearly everything. There
#: is no third, better proxy waiting to be found: the tree records no link from an atom to the
#: commits that built it, so "which control did this atom's build write" is not a question the
#: repository can answer, and the flattering answer is the cheap one to reach.
#:
#: WHAT THE TREE *CAN* ANSWER is the subject's age, by the same oracle that dates the controls --
#: and that decides WHICH EXIT the row is owed, which is the part the reader actually cannot see:
#:
#:   * every named subject predates the row too -> the atom EXTENDS code that already had
#:     controls. Its own build has written none because, at level 0, its own build has not
#:     happened. There is nothing to repoint AT, and the only way to follow the repoint exit is to
#:     invent a filename -- the same unfollowable instruction `H40` and `H48` were refused on.
#:   * a named subject was born AFTER the row -> the atom's build did land new subject code and
#:     cited no control for it, so a control may well exist under a name the row never used. That
#:     is the `PB4`/`PB6` shape, and here the repoint exit is genuinely owed.
#:
#: The split is keyed to the PROPERTY and not to today's eight rows: it stops being true of a row
#: on the commit that lands that row's first atom-own control, which is exactly when it should.
EXTENDS_WORK_OLDER_THAN_ITSELF = (
    "every named control AND every named subject was on disk before the row was, so this atom "
    "extends existing work and its own build has written no control to point at")
BUILD_LANDED_A_SUBJECT_AND_CITED_NO_CONTROL = (
    "every named control predates the row but a named subject does not, so this atom's build "
    "landed code and cited no control for it")
CAUSE_UNDECIDABLE = "git could not be asked whether the absent path ever existed"
#: The row is not the problem. Every path it names is here and one of them is a runnable control,
#: so no edit to `file_scope` would change the verdict -- the refusal came from the PASS (a
#: timeout, a spent budget, a control older than the row).
#:
#: THIS USED TO BE AN EMPTY LIST, and the emptiness was argued for in `assess` as the honest
#: answer because those states "say something about the pass, not about the state of the work".
#: That was half right and the half it got wrong was expensive: "the pass, not the row" IS a
#: cause, and returning nothing made five of the thirty ungradable rows invisible to any consumer
#: that groups by cause -- a fail-silent in the very control built to end an undifferentiated
#: count. A partition with a hole is not a partition. (Measured 2026-09-16: D27, D9, KNIFE3, H41
#: and W2_31 carried no cause at all.)
NOTHING_IN_THE_ROW = ("every named path is on disk and one of them is a runnable control, so the "
                      "refusal came from the pass and not from the row")

#: What each cause instructs. Kept beside the cause rather than written at the call site, because
#: the pair is the whole point: a cause without its repair is the undifferentiated count again.
CAUSE_REPAIR = {
    POINTER_ROT: "repoint `file_scope` at where the path lives now -- `git log --all -- <path>`",
    CONTROL_NEVER_WRITTEN: "write the named control and prove it can fail; until then the row "
                           "is ungradable and that is the honest reading, not a defect",
    CONTROL_UNNAMED: "name the control this atom's build writes. Do NOT write one before asking "
                     "whether it exists: `git log --all --oneline -- <subject>` finds the commits "
                     "that touched the subject, and a control under a name the row never cited is "
                     "the shape PB4 and PB6 were. Nothing here is a verdict about the work yet",
    HONESTLY_UNBUILT: "nothing to repair in the row -- build the atom, or close it",
    SUBJECT_NEVER_WRITTEN: "build this part of the atom, or drop the path from `file_scope`. Do "
                           "NOT repoint it -- unlike a rotted pointer there is no earlier name "
                           "to repoint at, and git is the witness for that",
    NAMES_ONLY_A_SCOPE: "name the FILES this atom writes, not the directory they live in",
    CAUSE_UNDECIDABLE: "classify this row in a tree that has commit history",
    NOTHING_IN_THE_ROW: "re-run this row ALONE (`--atom <id>`) and read its reason line -- do not "
                        "edit `file_scope`, because nothing in it is wrong",
    EXTENDS_WORK_OLDER_THAN_ITSELF:
        "nothing to repoint at, and do NOT invent a control name to move the count -- the row's "
        "`file_scope` is right and the atom is unbuilt. Build it, or close it. The named suite "
        "becomes evidence the moment this atom's build adds a case to it",
    BUILD_LANDED_A_SUBJECT_AND_CITED_NO_CONTROL:
        "ask `git log --all --oneline -- <the subject born after the row>` for the commits that "
        "landed it and name the control they wrote. If they wrote none, that is the finding -- "
        "say so in the row rather than repointing it at an older suite",
}

#: The one cause that asks for no work. Named here rather than at each reader, because "which of
#: these is not a defect" is a judgement the module that defines the vocabulary owes its
#: consumers -- a caller left to decide it will decide differently from the next caller.
#: `EXTENDS_WORK_OLDER_THAN_ITSELF` joins it 2026-09-26 on the same evidence `HONESTLY_UNBUILT`
#: holds it on: the repair these rows owe is a BUILD, and their `file_scope` has been measured
#: correct rather than assumed so. This is a count moving DOWN on a widened claim, which is the
#: shape to distrust -- the guard against it is that the claim is self-clearing and falsifiable,
#: not that it is modest. It is false the moment a subject younger than the row appears in the
#: row, and the sibling cause below then fires instead.
CAUSES_OWING_NO_REPAIR = frozenset({HONESTLY_UNBUILT, EXTENDS_WORK_OLDER_THAN_ITSELF})

#: Stands in the `frozen_by` list when the lane's blockers could not be read. A string, in the
#: same list as the real finding names, so no caller can treat "unknown" as "clear" by looking
#: only at emptiness -- the shape that reads a not-found as a valid extreme.
BLOCKERS_UNREADABLE = "the lane's blocking findings could not be read"

#: Said on the blocker's own line when it is live at `HEAD` and archived only in the working copy.
#: Without it the reader greps `docs/staging/`, finds nothing, and files the blocker as a ghost --
#: which is the same trap as verifying a surviving copy with `find` and never asking git.
ARCHIVED_ONLY_IN_THE_WORKING_TREE = (
    "  -- live at HEAD, archived only in the working tree: an uncommitted archival is a "
    "discharge that has not happened")

#: Both halves of the map. A row minted into the live half and later closed keeps its ORIGINAL
#: minting commit only if both are searched, and dating it from the close would make every closed
#: row look younger than the controls its own build wrote.
MAP_PATHS = ("docs/design/maturity_map.yaml", "docs/design/maturity_map_closed.yaml")


#: How long the HEAD-red observation may go unrefreshed before it stops being evidence about
#: HEAD. NOT A CHOSEN NUMBER: `background/head-green-census.timer` is `OnCalendar=*-*-* 03:30:00`
#: with `Persistent=true`, so a healthy store gains one run per day and a box that was off
#: overnight still measures when it comes back. Seven missed runs is therefore not a late census,
#: it is a store nothing is writing -- and the only reading of it that cannot come out as
#: "HEAD is green" when we do not know.
#:
#: WHY THE BOUND IS LOOSE RATHER THAN TIGHT, said because the opposite looks safer and is not.
#: This leg can only SILENCE a row. Tightening it to one day would fail closed on every ordinary
#: day the census slipped -- measured 2026-09-25, the last recorded run was 2026-09-23T04:31 and
#: a 24h bound would have made the whole mechanism inert on the day it landed. A screen that is
#: unsatisfiable exactly when its subject is worst is this project's fourth control-failure
#: class; see `docs/staging/` on the RUNG-1 publisher.
REGISTER_STALE_AFTER_S = 7 * 24 * 60 * 60

#: Why the register could not be used. Each one means the SAME thing to `assess` -- run the
#: suites, exactly as before this leg existed -- but they are named apart because they send a
#: reader to three different places: a missing daemon, a wedged one, and a corrupt store.
REGISTER_UNOBSERVED = ("no census run is recorded in the HEAD-red observation store, so nothing "
                       "is known about what is red at HEAD")
REGISTER_UNDATED = "the last recorded census run carries no readable timestamp"
REGISTER_STALE = ("the last recorded census run is {age_h:.0f}h old, past the {bound_h:.0f}h "
                  "bound, so what it saw may have been fixed since")


def reds_at_head(controls: list[str], root: Path = ROOT, load=None,
                 now: float | None = None) -> tuple[list[str], str | None]:
    """`(red node ids that live in `controls`, why the register is unusable or None)`.

    WHY THIS READS THE STORE AND NOT `HEAD_RED_REGISTER.md`, which is the artefact the work item
    names. The register document IS that store rendered -- `head_red_register.render` writes it
    on every census run -- so a second parser of the rendering is a second reading of one fact,
    and this repository's own rule (`_lane_blockers`, below, makes the same argument for OPS11)
    is that the shared mechanism is called rather than re-read. It is not hypothetical here:
    measured 2026-09-25, the committed register says 41 red at `f705248ae` and the live store
    says 37 at `8f315e53f`. A markdown parser would have silenced rows on four tests that are
    green, and been unable to say which reading was current.

    REDNESS IS THE OBSERVATION, NOT `owed()`. `owed` subtracts the tests a person has ACCEPTED in
    `head_red_baseline.json`, and acceptance is a decision about whether we still owe work -- an
    accepted red is red. The question here is only "can this named set all pass", and it cannot
    while any member fails, forgiven or not.

    THE UNUSABLE REASON IS NOT FOLDED INTO AN EMPTY LIST. "No reds in this set" and "I could not
    look" are the two answers that are both empty and mean opposite things, which is the shape
    `head_red_register.observation_state` was extracted to end. A caller that read only the list
    would treat an absent store as a clean bill of health for every row at once -- one paragraph
    retiring the whole register, which is the disposition that file refuses by design.
    """
    from background import head_red_register as hrr  # local: keeps import cost off callers

    #: Derived from the store's own declaration rather than spelled again here, so a store that
    #: moves takes this probe with it. `load_observed`'s legacy fallback is deliberately not
    #: reached: it only fires when the live store is unreadable, and that is the case this leg
    #: must fail closed on anyway.
    rel = hrr.OBSERVED_PATH.relative_to(hrr.PROJECT_DIR)
    store = (load or hrr.load_observed)(Path(root) / rel)

    if hrr.observation_state(store) == hrr.UNOBSERVED:
        return [], REGISTER_UNOBSERVED

    # `isinstance` ON EVERY ROW, and it is not defensive noise. This probe runs inside the
    # delivery seat's orientation, and an AttributeError raised on a malformed row here does not
    # fail closed -- it propagates out of `assess` and takes the whole pass down, so a corrupt
    # untracked JSON file would cost the brief. A row that is not a mapping is a row that says
    # nothing, which is UNDATED (for the run) and not-red (for a test): both fall through to the
    # run, which is the same answer every other unusable state gets.
    last = (store.get("runs") or [])[-1]
    stamp = _run_epoch(last.get("at") if isinstance(last, dict) else None)
    if stamp is None:
        return [], REGISTER_UNDATED
    age = (time.time() if now is None else now) - stamp
    if age > REGISTER_STALE_AFTER_S:
        return [], REGISTER_STALE.format(age_h=age / 3600.0,
                                         bound_h=REGISTER_STALE_AFTER_S / 3600.0)

    wanted = set(controls)
    tests = store.get("tests")
    return sorted(node for node, row in (tests if isinstance(tests, dict) else {}).items()
                  if isinstance(row, dict) and row.get("currently_red")
                  and str(node).split("::", 1)[0] in wanted), None


def _run_epoch(stamp) -> float | None:
    """Unix time of an ISO-8601 run stamp, or None. None is "I cannot date this", never now."""
    if not isinstance(stamp, str) or not stamp.strip():
        return None
    try:
        parsed = datetime.fromisoformat(stamp.strip())
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.timestamp()


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


def _is_declared_directory(rel: str, root: Path) -> bool:
    """Whether the row named a DIRECTORY rather than a file.

    A trailing slash counts even when the directory is gone, because the row's own syntax is the
    claim being read -- resolving it only against disk would reclassify `docs/staging/records/`
    as a rotted file pointer the day the directory empties.
    """
    return rel.endswith("/") or (root / rel).is_dir()


def _is_a_control_scope(rel: str, root: Path) -> bool:
    """Whether this named directory is a place controls LIVE -- measured, not matched on a prefix.

    A `test_*.py` anywhere beneath it. `tests/harness` qualifies and `docs/market_research/` does
    not, without either being named here: a literal `tests/` would be a bound keyed to today's
    layout, and this project has paid for that shape often enough to stop writing it.

    ABSENT OR EMPTY IS FALSE, deliberately, and the direction is the honest one. A row naming a
    test directory that holds nothing has not shown where its evidence lives either -- it is
    `CONTROL_UNNAMED`, whose repair says to go and look, rather than `NAMES_ONLY_A_SCOPE`, whose
    repair says to name a file in a directory that has none.

    `rglob` is short-circuited on the first hit, so `tests/` costs one directory read and not a
    walk of the suite -- this runs inside the delivery seat's orientation, over every candidate
    row, and a full walk per directory would be paid 28 times for one boolean.
    """
    here = root / rel
    if not here.is_dir():
        return False
    return next(here.rglob("test_*.py"), None) is not None


def _path_known_to_git(rel: str, root: Path = ROOT) -> bool | None:
    """Did this path EVER exist on any ref here? `True`/`False`, or `None` for "cannot ask".

    `--all`, not `HEAD`: a control written on a lane branch that never merged did exist, and
    calling it never-written would send a reader to write a file that is already somewhere.

    None is the fail-closed answer and is never folded into False. "Never written" is the cause
    that tells a reader to sit down and write a test; producing it out of a missing `.git` --
    which is what a `git archive` extract is -- would manufacture that instruction from nothing.
    """
    try:
        r = subprocess.run(["git", "log", "--all", "--format=%H", "-1", "--", rel],
                           cwd=str(root), capture_output=True, text=True, timeout=60)
    except Exception:  # noqa: BLE001 -- no git binary, no history, no answer
        return None
    if r.returncode != 0:
        return None
    return bool(r.stdout.strip())


def ungradable_causes(atom: dict, root: Path = ROOT, known=_path_known_to_git,
                      ages=None) -> list[dict]:
    """Why this row cannot be graded, as `[{cause, paths, repair}, ...]`, possibly several.

    THE SPLIT THIS EXISTS TO MAKE. The census reported thirty-one ungradable rows under four
    reasons, all four of which describe the SHAPE of `file_scope` and none of which says what to
    do. Three rows sharing "names a control file that is not on disk" had three different causes
    and three different repairs -- one pointer to repoint, one control to write, one atom that is
    simply unbuilt and correctly reading zero. Counting those as one number is why the count did
    not move for twelve briefs: two thirds of it was never a defect.

    WHY IT IS COMPUTED AND NOT A FIELD IN THE ROW. A hand-written `cause:` in the map is pinned
    to today's answer -- it stays "unbuilt" through the build that fixes it and stays
    "pointer rot" after the repoint. The rot this very function detects is a map field that
    stopped matching the tree. Deriving it every pass is the only version that cannot go stale.

    ORDER IS REPAIR ORDER, not severity: a rotted pointer is fixed first because every later
    question is asked of paths the row got wrong.
    """
    scope = [str(e) for e in (atom.get("file_scope") or [])] if isinstance(
        atom.get("file_scope"), list) else []
    controls = named_controls(atom)
    dirs = [rel for rel in scope if _is_declared_directory(rel, root)]
    files = [rel for rel in scope if rel not in dirs]
    absent = [rel for rel in files if not (root / rel).exists()]

    rotted, never, unknown = [], [], []
    for rel in absent:
        answer = known(rel, root)
        (rotted if answer else never if answer is False else unknown).append(rel)

    out: list[dict] = []
    if rotted:
        out.append({"cause": POINTER_ROT, "paths": rotted, "repair": CAUSE_REPAIR[POINTER_ROT]})
    if unknown:
        out.append({"cause": CAUSE_UNDECIDABLE, "paths": unknown,
                    "repair": CAUSE_REPAIR[CAUSE_UNDECIDABLE]})

    if not files:
        # Directories only, or nothing named at all. A directory is not evidence in either
        # direction -- `tests/` exists in every tree, built or not -- so calling this row unbuilt
        # would be a claim nothing measured.
        out.append({"cause": NAMES_ONLY_A_SCOPE, "paths": dirs,
                    "repair": CAUSE_REPAIR[NAMES_ONLY_A_SCOPE]})
        return out

    on_disk = [rel for rel in files if (root / rel).exists()]
    subject_on_disk = [rel for rel in on_disk if rel not in controls]
    if not on_disk and not (rotted or unknown):
        # NOTHING THE ROW NAMES IS HERE, and nothing the row names was mislaid -- it was never
        # written. The atom is unbuilt and its zero is the true answer: this is the part of the
        # census that was never a defect and was being counted as one.
        #
        # THE GUARD ASKS `on_disk`, NOT `subject_on_disk`, AND THAT IS THE 2026-09-25 NARROWING.
        # It used to ask whether any named SUBJECT was here, where subject means "a named file
        # that is not a control". A row whose only non-directory entries ARE controls therefore
        # had an empty subject list however many of those controls were sitting on disk and
        # passing -- and was told "no named file exists, so the row is RIGHT to read zero", the
        # one verdict in this partition meaning "never a defect", on a sentence the tree
        # contradicts. Latent when it was found: both live members (`G14`, `G15`) genuinely have
        # nothing on disk, and the only route into the false branch was the controls-only
        # repoint the census's own `NAMES_ONLY_A_SCOPE` repair prescribes. A row naming an
        # existing control is not unbuilt -- it has a runnable control and belongs in the legs
        # below. Written up in `docs/staging/`, in the finding whose name begins
        # `SEAT_FINDING_THE_PRESCRIBED_REPOINT_WOULD_SILENCE_FOUR_ROWS`.
        #
        # THE ROT GATE IS WHY THIS IS NOT ONE LINE. "Unbuilt" is a claim about work, and it may
        # only be made of paths the row gets right. With a rotted pointer in the set, the subject
        # may be on disk under the name the row has stopped using, and "right to read zero" would
        # then be exactly backwards. The control question below is NOT gated the same way: it
        # asks about a different path, and a mislaid subject says nothing about whether the test
        # was ever written. (`A51` is that row: one pointer to repoint AND one control to write.)
        out.append({"cause": HONESTLY_UNBUILT, "paths": sorted(files),
                    "repair": CAUSE_REPAIR[HONESTLY_UNBUILT]})
        return out

    never_subjects = [rel for rel in never if rel not in controls]
    if never_subjects:
        # SUBJECT BEFORE CONTROL, same reason the rot gate runs first: every later question is
        # asked of what the row claims to cover, and this says part of that claim is unbuilt.
        # Reaching here means at least one named file IS on disk -- the all-absent row returned
        # `HONESTLY_UNBUILT` above and owes no repair. This one does.
        out.append({"cause": SUBJECT_NEVER_WRITTEN, "paths": sorted(never_subjects),
                    "repair": CAUSE_REPAIR[SUBJECT_NEVER_WRITTEN]})

    never_controls = [rel for rel in controls if rel in never]
    if never_controls:
        out.append({"cause": CONTROL_NEVER_WRITTEN, "paths": never_controls,
                    "repair": CAUSE_REPAIR[CONTROL_NEVER_WRITTEN]})
    elif not controls:
        # THE ROW NAMES NO CONTROL, and until 2026-09-25 this was the same cause as the branch
        # above -- fourteen of the sixteen live members of `CONTROL_NEVER_WRITTEN` came through
        # here, where nothing is absent and nothing was measured. See `CONTROL_UNNAMED`.
        #
        # AND THE DIRECTORY CASE IS SPLIT OFF FIRST, because the row that names `tests/harness`
        # is not the row that names nothing: it says where its evidence lives and stops one level
        # short of the file. `NAMES_ONLY_A_SCOPE` used to be reachable only through `if not files`
        # above -- EVERY entry a directory -- which is a condition keyed to the rest of the row
        # rather than to the property it is describing. `W2_non_dd_miss_vocabulary` names three
        # subject files AND `tests/company/crm` AND `tests/harness`, and it was being told to
        # write a control that is almost certainly already inside one of them.
        #
        # A CONTROL SCOPE IS MEASURED, NOT MATCHED ON `tests/`. The property is "controls live
        # here", so it is asked of the tree: a `test_*.py` anywhere under the directory. That
        # keeps `docs/market_research/`, `company/billing/` and `site/data/` -- the other
        # directories these rows name -- out of it without a path literal that would need
        # maintaining the day the test root moves.
        scopes = [rel for rel in dirs if _is_a_control_scope(rel, root)]
        if scopes:
            out.append({"cause": NAMES_ONLY_A_SCOPE, "paths": scopes,
                        "repair": CAUSE_REPAIR[NAMES_ONLY_A_SCOPE]})
        else:
            # REAL PATHS, not the `"(file_scope names no test_*.py)"` placeholder this used to
            # carry. A non-path in a `paths` field is a path-shaped token a reader will try to
            # open, and these are the paths the repair actually sends them to `git log`.
            out.append({"cause": CONTROL_UNNAMED, "paths": sorted(subject_on_disk),
                        "repair": CAUSE_REPAIR[CONTROL_UNNAMED]})
    # AND THE PARTITION IS CLOSED HERE. Reaching this line with nothing found means every path
    # the row names is on disk and at least one is a runnable control -- true BY CONSTRUCTION
    # since 2026-09-25 and not before: an absent path now leaves a cause behind it whichever of
    # the three ways it is absent (`POINTER_ROT`, `CAUSE_UNDECIDABLE`, `SUBJECT_NEVER_WRITTEN`,
    # or `CONTROL_NEVER_WRITTEN`), so `out` cannot be empty while this claim is false -- there is no edit to the
    # row that would help, which is itself the answer and not the absence of one. Returning `[]`
    # for it is what made five rows invisible to every consumer that groups by cause; see
    # NOTHING_IN_THE_ROW. The test is `if not out`, deliberately, and not a re-derivation of the
    # conditions above: a second spelling of "none of the other branches fired" is the shape that
    # drifts away from the branches it is describing and reopens the hole.
    if not out and controls:
        # THE AGE SPLIT, AND IT RUNS ONLY WHEN NOTHING ELSE IS WRONG WITH THE ROW. Gated on
        # `not out` for the same reason the rot gate runs first: with an absent path still
        # unaccounted for, "every named subject predates the row" is a claim about a set the row
        # got wrong. Gated on `controls` because a row naming none has already been answered by
        # `CONTROL_UNNAMED`, and asking a dating question of an empty set returns "nothing
        # predates" -- a not-found read as a verdict.
        ages = ages or controls_older_than_the_row
        predating, undatable = ages(atom.get("id", ""), controls, root)
        if predating and not undatable and not [c for c in controls if c not in predating]:
            # EVERY named control is older than the row. The pass reports this as
            # CONTROL_PREDATES_ROW and prints two exits; which one is owed is decided here, on
            # the subjects' dates, because that is the only part of the question the tree
            # records. See the cause constants for the two proxies that were measured and
            # discarded.
            subj_predating, subj_undatable = ages(atom.get("id", ""), subject_on_disk, root)
            younger = [rel for rel in subject_on_disk
                       if rel not in subj_predating and rel not in subj_undatable]
            if subj_undatable:
                out.append({"cause": CAUSE_UNDECIDABLE, "paths": sorted(subj_undatable),
                            "repair": CAUSE_REPAIR[CAUSE_UNDECIDABLE]})
            elif younger:
                out.append({"cause": BUILD_LANDED_A_SUBJECT_AND_CITED_NO_CONTROL,
                            "paths": sorted(younger),
                            "repair": CAUSE_REPAIR[BUILD_LANDED_A_SUBJECT_AND_CITED_NO_CONTROL]})
            else:
                out.append({"cause": EXTENDS_WORK_OLDER_THAN_ITSELF,
                            "paths": sorted(predating),
                            "repair": CAUSE_REPAIR[EXTENDS_WORK_OLDER_THAN_ITSELF]})
    if not out:
        out.append({"cause": NOTHING_IN_THE_ROW, "paths": controls,
                    "repair": CAUSE_REPAIR[NOTHING_IN_THE_ROW]})
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


def _head_staging_root(repo: Path, dest: Path) -> Path:
    """`HEAD`'s `docs/staging/` on disk under `dest`, so the shared mechanism can read it.

    Extracted rather than parsed out of `git cat-file`, because the whole point is to hand the
    committed documents to the SAME `lane_blockers` the working copy goes through. A failure here
    raises, and `frozen_by` turns that into BLOCKERS_UNREADABLE -- frozen, never movable.
    """
    tar = subprocess.run(["git", "-C", str(repo), "archive", "HEAD", "docs/staging"],
                         capture_output=True, check=True)
    with tarfile.open(fileobj=io.BytesIO(tar.stdout)) as archive:
        archive.extractall(dest, filter="data")
    return dest / "docs" / "staging"


def _lane_blockers(lane: str, root: Path | None = None) -> list[str]:
    """The live BLOCKING findings holding `lane`, by document name, over BOTH trees.

    CALLS THE SHARED MECHANISM rather than re-reading the staging directory: `lane_blockers` is
    the same function OPS11 refuses with, so this cannot report a lane clear that the recorder
    then refuses. A second reading of the severity index here is how one control comes to
    disagree with the control it is describing.

    It is called TWICE, on the working copy and on `HEAD`'s staging, and the union is returned:
    see the header on which tree the refusal is actually evaluated against. `root` exists so a
    test can hand this a repository where the two trees are made to disagree on purpose; `None`
    means the live tree, and takes the defaults so the working-copy half stays byte-identical to
    what OPS11 itself reads.
    """
    from background.gate_authorization import lane_blockers  # local: keeps import cost off callers
    if root is None:
        repo, working = ROOT, lane_blockers(lane)
    else:
        repo = Path(root)
        working = lane_blockers(lane, staging_root=repo / "docs" / "staging", repo_root=repo)
    here = {b.finding for b in working}
    with tempfile.TemporaryDirectory(prefix="level-zero-head-staging-") as tmp:
        committed = {b.finding for b in lane_blockers(
            lane, staging_root=_head_staging_root(repo, Path(tmp)), repo_root=repo)}
    return [name if name in here else name + ARCHIVED_ONLY_IN_THE_WORKING_TREE
            for name in sorted(here | committed)]


def frozen_by(lane, blockers_for=_lane_blockers) -> list[str]:
    """Why a level raise on this lane would be refused today, or `[]` if it would not be.

    A row with no lane at all is UNREADABLE, not clear: OPS11 resolves the lane from the atom
    itself, so a missing one means the refusal cannot be predicted, and predicting "movable" is
    the answer that wastes the reader's turn. EITHER tree failing to read is the same answer --
    the probe reads both (see the header) and a lane it could only half-read is not a clear lane.
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
           blockers_for=_lane_blockers,
           causes=ungradable_causes,
           red_at_head=reds_at_head) -> tuple[list[dict], list[dict]]:
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

    `red_at_head` IS ASKED BEFORE THE BUDGET, not after, and the order is the whole economy: a
    row that needs no run must not be denied one by a budget it was never going to spend. See
    `reds_at_head` for why an unusable register falls through to the run instead of silencing.
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
            # BOTH BRANCHES, because the one-branch version sent a reader at a premise the tree
            # refutes. "Repoint at the control that exists" is right for PB4 and PB6 -- a build
            # that landed and wrote a differently-named file -- and wrong for PB5, whose named
            # path is a control its build has not written yet. A lane-0 item was drawn on the
            # single instruction and spent a turn discovering that PB5 has no control to point at:
            # measured 2026-09-06, no test on disk asserts the pounds/percent scale on the company
            # side, and the row is correctly at zero.
            ungradable.append({"id": aid, "reason": NAMED_CONTROL_ABSENT, "paths": absent,
                               "detail": "which of those it is, is answered on the CAUSE line "
                                         "below -- `ungradable_causes` asks git whether the path "
                                         "ever existed, so the reader is no longer the one who "
                                         "has to check"})
            continue
        # Dating runs BEFORE the budget check and before the run: it costs a fraction of a second
        # against pytest's seconds-to-minutes, and a set that cannot be evidence about this atom
        # should not spend the pass's budget proving it passes.
        predating, undatable = ages(aid, controls, root)
        # WHAT MAKES THE SET EVIDENCE IS THAT SOMETHING IN IT IS THE ATOM'S OWN, not that
        # nothing in it is older. Until 2026-09-25 a single predating entry refused the whole
        # row, and on the live map that is the normal shape for an atom that EXTENDS an existing
        # suite rather than writing a new one: `KNIFE3_wall_crossing_paydown` names twelve
        # controls, NINE of them born after the row and three -- the ruff ratchet, the wall
        # ratchet, the renewals routing -- born before it because they already existed and the
        # atom cut into them. Two of those three were last edited by commits whose subject line
        # reads "KNIFE3 step 3" and "KNIFE3 B7". Refusing there did not protect anything: it
        # discarded nine controls this atom's own build wrote because three of its twelve
        # predate, and it is why the pass returned 28 rows and graded none.
        #
        # THE VERDICT IS NOT LOOSENED BY THIS, and that is the leg to keep hold of. CONTRADICTED
        # still requires the WHOLE named set to pass, predating entries included, so an older
        # control can only ever SILENCE a row -- it can never be the thing that refuses one. The
        # fail-closed direction is therefore unchanged: a row with no atom-own control at all is
        # still ungradable entire, which is H41's shape (both its named suites predate it) and
        # the one the module docstring works through.
        # `undatable` is NOT subtracted here, and that is measured rather than argued: the
        # `if undatable:` leg below fires on ANY undatable entry, so subtracting them
        # changes no verdict this module can reach. The mutation that removed the term was
        # green -- an equivalence, not a missing test -- so the term is gone and the
        # provenance leg keeps the property on its own.
        atom_own = [p for p in controls if p not in predating]
        if predating and not atom_own:
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
        # THE EXPENSIVE RUN IS SKIPPABLE FOR EXACTLY THE ROWS TOO EXPENSIVE TO RUN, and that
        # coincidence is what makes this leg worth having rather than a cleverness. CONTRADICTED
        # requires the WHOLE named set to pass, so a set holding a test that is red at HEAD
        # cannot reach it -- and the rows naming the most suites are both the likeliest to hold
        # one and the certain to blow the budget. Measured 2026-09-25: production caps each atom
        # at 60s (`background/delivery_seat._LEVEL_ZERO_TIMEOUT_S`, deliberately, so the
        # orientation's brief arrives) while `KNIFE3_wall_crossing_paydown`'s twelve suites cost
        # 1078s and 2.44 GB. It was discharged BY HAND this way and came back SILENT: 2 of its
        # 224 tests have been on the register for 19 consecutive census runs since 2026-09-02.
        #
        # THIS IS AN ECONOMY, NOT A LOOSENING, and it is the same leg the predating-control rule
        # above keeps hold of: it can only ever SILENCE a row and can never be the thing that
        # refuses one. A row it silences is not ungraded -- we have EVIDENCE its named set does
        # not all pass, which is precisely the silent verdict this module defines, reached from
        # the register instead of from a runner.
        #
        # AND IT FAILS CLOSED ON THE REGISTER, which is the half that is not free. An unusable
        # register falls through to the run exactly as before this leg existed, because the
        # alternative -- treating "I could not look" as "nothing is red" would be harmless, but
        # treating it as "everything might be red" would let one missing file silence the whole
        # partition. The reason is carried rather than discarded so `main` can print WHICH of the
        # two silences a row got.
        reds, register_unusable = red_at_head(controls, root)
        if reds and register_unusable is None:
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
    # Every ungradable row is asked WHY, uniformly -- not only the two shapes that need it.
    # Special-casing which reasons get asked would put the split back under a hand-maintained
    # list of reasons, which is the shape that rotted.
    #
    # CORRECTION, 2026-09-16, beside the claim it replaces. This comment used to say the
    # instrument states (budget spent, runner unavailable, control predates the row) return no
    # cause and that the emptiness was the honest answer. It is not: an empty list is not a
    # reading, and a consumer grouping by cause drops the row entirely. Those rows now carry
    # NOTHING_IN_THE_ROW, which says the same thing as a fact the reader can act on -- the
    # refusal is in the pass, so do not go and edit the row. `ungradable_causes` is total.
    by_id = {a.get("id"): a for a in atoms}
    for u in ungradable:
        u["causes"] = causes(by_id.get(u["id"], {}), root)
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

    # THE DENOMINATOR, and why `contradicted: 0` may not be published without it. Measured on the
    # live map 2026-09-25: 28 rows in the partition, 28 of them UNGRADABLE, 0 graded -- and the
    # only numbers on either surface were `{"contradicted": 0, "ungradable": 28}`. The delivery
    # seat read that `0` as evidence the map was honest, twice, in two findings eight days apart,
    # and neither asked how many rows had been weighed. `0 of 0 graded` and `0 of 28 graded` are
    # different facts and the surface printed the same number for both.
    #
    # Counted through `is_candidate`, which is the same predicate `assess` filters on: the
    # partition has one spelling, so a change to who is graded cannot leave the denominator
    # describing the old population. And counted by MEMBERSHIP rather than by subtraction, so a
    # caller that hands `main` verdicts about rows outside the partition (the tests do) can never
    # drive this negative.
    #
    # The EXIT CODE deliberately does not move. "Cannot grade this row" is argued in the module
    # docstring as a finding about the row and not a verdict about the work, and the one caller
    # this has is an orientation whose brief must arrive. Fail-closed here is a claim on the
    # SURFACE -- "cannot tell" said out loud, in the place the misread happened -- not a refusal.
    population = [a for a in atoms if is_candidate(a)]
    ungraded_ids = {u.get("id") for u in ungradable}
    graded = sum(1 for a in population if a.get("id") not in ungraded_ids)

    # WHICH SILENCE A SILENT ROW GOT, because the module has two of them now and they carry
    # opposite instructions: "the runner said no" is the map and the controls agreeing, while
    # "a named control is red at HEAD" is a row that is silent because something ELSE is broken,
    # and the thing to do about it is on the HEAD-red register rather than in this row.
    #
    # RE-DERIVED HERE RATHER THAN CHANNELLED OUT OF `assess`, and the reason is the twenty-one
    # call sites that unpack its two-tuple. Re-derivation is the shape that drifts, so it is the
    # SAME function over the SAME inputs -- `reds_at_head(controls, root)` is pure, reads one
    # JSON file, and takes no argument `assess` had and this does not. It can therefore differ
    # from the pass only if the store changed underneath, which is a fact about the store and
    # not a disagreement between two readings.
    #
    # Rows in neither verdict list ONLY: a row that was ungradable for an absent control never
    # reached this leg, and printing "silenced by a red" over it would name the wrong cause.
    decided = ungraded_ids | {c.get("id") for c in contradicted}
    silenced = []
    for atom in population:
        if atom.get("id") in decided:
            continue
        reds, unusable = reds_at_head(named_controls(atom))
        if reds and unusable is None:
            silenced.append({"id": atom.get("id"), "reds": reds})

    if args.json:
        json.dump({"contradicted": contradicted, "ungradable": ungradable,
                   "silenced_by_a_red_at_head": silenced,
                   "population": len(population), "graded": graded}, sys.stdout, indent=2)
        sys.stdout.write("\n")

    if silenced and not args.json:
        sys.stderr.write(
            "\n[level-zero] {} row(s) are SILENT because a control their own row names is RED "
            "AT HEAD. The named set cannot all pass, so no run was spent proving it. These rows "
            "are GRADED -- the evidence is on the HEAD-red register, not in a pytest run -- and "
            "the work they point at is that register, not this row.\n".format(len(silenced)))
        for s in silenced:
            sys.stderr.write("  {}\n".format(s["id"]))
            for node in s["reds"]:
                sys.stderr.write("      RED AT HEAD: {}\n".format(node))

    if population and not args.json:
        if graded:
            sys.stderr.write(
                "\n[level-zero] {} of {} row(s) in the partition were GRADED; {} could not "
                "be.\n".format(graded, len(population), len(ungradable)))
        else:
            sys.stderr.write(
                "\n[level-zero] ⚠ NOTHING WAS GRADED. All {} row(s) in the partition are "
                "ungradable, so this pass weighed no evidence: a count of 0 contradicted rows "
                "here is NOT a verdict about the map, it is \"cannot tell\".\n".format(
                    len(population)))

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
            # The cause and its repair, never the cause alone: the reason line above is what the
            # census could already say, and saying it louder is what it did for twelve briefs.
            for c in u.get("causes") or []:
                sys.stderr.write("      CAUSE: {}\n".format(c["cause"]))
                for p in c["paths"]:
                    sys.stderr.write("        {}\n".format(p))
                sys.stderr.write("        REPAIR: {}\n".format(c["repair"]))

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
