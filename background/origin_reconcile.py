#!/usr/bin/env python3
"""Close the fork with origin automatically, in an isolated worktree, never in the shared tree.

WHY (director, 2026-09-02): *"One cause may be mine: I staged a document at 07:45Z, which moved
origin ahead of your local HEAD, and your origin-ahead guard then refuses your commit until you
pull. If that's what's happening, make the pull automatic rather than a refusal — a staged document
arriving should never block your landing."*

It is what was happening, from the machine's own record:

    docs/observability/.last_publish_cause.json
    {"cause": "behind_origin", "evidence": "origin/main is 1 commit(s) AHEAD of HEAD ..."}

The site had been stale for 3.2 hours and five landings sat local-only, all on that one condition.

THE REFUSAL IS RIGHT AND IS NOT WHAT CHANGES. `process_run_complete._divergence_refusal` argues its
case and the case holds:

    "The only sanctioned reconciliation is `surgical_land --merge origin/main`, which gates the
     whole tree and takes longer than a publish cycle; and there are routinely three lanes with
     uncommitted work in this tree. A daemon that merged unattended would be deciding, every twelve
     minutes, to move other people's work."

Both halves are true **of the shared working tree**, and the shared tree is the only place either
objection applies. Measured the same morning: 57 index entries belonging to another lane. A `git
merge` there would have swept every one.

SO THE MERGE HAPPENS SOMEWHERE ELSE. A throwaway worktree has its OWN index, so the two objections
dissolve rather than being overridden:

  * *"deciding to move other people's work"* — impossible: this never opens the shared index and
    never writes the shared tree. It is the same property `promote_worktree_landing` is built on.
  * *"takes longer than a publish cycle"* — true, and it is why this is NOT inline in the publish
    path. It runs on the deadman's cadence, so by the time the publish cycle looks, the fork is
    already closed and the refusal it kept has nothing left to refuse.

CONFLICT IS STILL A JUDGEMENT AND STILL REFUSES. `surgical_land --merge` refuses on conflict, and
that refusal is inherited here deliberately: a disjoint fast-forward is mechanical, and resolving
two lanes' edits to one file is not something to do unattended. The refusal names the paths so the
next reader starts from the answer. That split — automate the mechanical case, keep the judgement —
is the whole design.

WHAT IT CANNOT DO. It cannot fast-forward the shared tree past uncommitted work, and it does not
try: it asks git for `--ff-only` and lets git's own refusal stand. A shared tree that will not
advance is REPORTED, never forced.

## AND THE SENTENCE THAT USED TO END THAT PARAGRAPH WAS FALSE, AT A COST OF 29 COMMITS

It said *"and the fork stays closed on origin either way."* It does not. This ran on the deadman
cadence from 15:47 to 19:01 on 2026-09-02 and put **29 consecutive empty merges** on origin, one
every 6m20s, while reporting `RECONCILED` every time. The mechanism, exactly:

  1. another lane held two files staged, and origin had landed its own version of them;
  2. so `git merge --ff-only` refused, correctly, and the shared tree stayed at its old HEAD;
  3. reconcile merged origin into that stale HEAD in the worktree and pushed -- a commit whose
     tree was byte-identical to its second parent, carrying nothing;
  4. origin advanced by one, the shared tree did not, so the next cadence read BEHIND again --
     one deeper than before -- and the loop had no terminating condition by construction.

The refusal it existed to clear is the one it manufactured: the gate's log at 18:02 reads
*"origin/main is 30 commit(s) AHEAD of HEAD ... would widen the fork by one more"*, refusing the
provenance banner on a fork this module had built commit by commit. Publishing was down thirteen
hours behind it. Director: *"Cure became the next cause."*

THREE RULES CAME OUT OF IT, and each is a branch below rather than a comment:

  * **A MERGE REQUIRES SOMETHING OF OURS.** If `ahead == 0` there is nothing to contribute, so the
    only honest action is to advance -- fast-forward or report `NOT_ADVANCED` -- and never to
    commit. This alone would have prevented every one of the 29.
  * **NEVER WHILE A GATE IS RUNNING** (`gate_is_running`): moving origin under a live gate spends
    the run and refuses it at the last step.
  * **RE-READ THE SUBJECT AFTER ACTING.** `RECONCILED` is now claimed only when the shared tree is
    observed level with origin afterwards. The old version put "shared tree NOT advanced" in a
    detail string that nothing read, and returned success beside it.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
REMOTE = "origin"
BRANCH = "main"

#: Where the reconciliation worktree is built. `/var/tmp`, on real disk, for the reason
#: `head_green_census` already gives about its own subject: `/tmp` here is a tmpfs, and a
#: ~130 MB checkout there is RAM.
WORKTREE = Path(os.environ.get("SE_RECONCILE_WORKTREE", "/var/tmp/se-origin-reconcile"))

#: Long enough for the full gate the merge runs (nine gates, a test selection, the site lane —
#: CLAUDE.md's own "commits take more than ten minutes"), short enough that a wedged merge frees
#: the next cadence rather than sitting forever.
MERGE_TIMEOUT_SECONDS = 25 * 60

#: How long the advance waits for the shared tree lock before giving the cadence back. A REFUSAL,
#: not a wait: the reconciler runs every 5 minutes, so a missed window costs one cadence, while a
#: reconciler blocked on a lock is one that is not there when its window opens.
ADVANCE_LOCK_TIMEOUT_SECONDS = 30

LEVEL = "LEVEL"
RECONCILED = "RECONCILED"
PUSHED = "PUSHED"
FAST_FORWARDED = "FAST_FORWARDED"
NOT_ADVANCED = "NOT_ADVANCED"
GATE_RUNNING = "GATE_RUNNING"
REFUSED_CONFLICT = "REFUSED_CONFLICT"
REFUSED_GATE = "REFUSED_GATE"

#: The merge gated clean and then origin moved before the push landed, so the push was refused as a
#: non-fast-forward and the whole gate was spent for nothing. REPORTED APART FROM `ERROR` BECAUSE IT
#: IS CLEARED APART: this one needs no attention at all -- the next cadence re-fetches, re-merges on
#: the new base and gates again -- while an `ERROR` push is a reconciler that cannot push and stays
#: broken until someone looks. Folded together they were indistinguishable in the record, so a
#: benign self-healing race read exactly like a dead reconciler (measured 2026-09-05, and the reason
#: this status exists).
#:
#: THE MODULE ALREADY GUARDS THIS RACE IN THE OTHER DIRECTION. `gate_is_running` carries the
#: director's 2026-09-02 rule verbatim -- never move origin under a running gate, because "the whole
#: run is spent and discarded" -- which protects the PUBLISH gate from this module. Nothing
#: protected this module from anyone else, and `surgical_land --attempts` cannot: it re-gates when
#: HEAD moves under the gate, and in a fresh isolated worktree nothing else moves HEAD. The race
#: that actually happens is `origin/main` advancing between the merge and the push.
#:
#: STILL NOT RETRIED IN-PROCESS, deliberately. A retry would have to re-merge and re-gate against
#: the new base -- the full cost again, inside a cadence that is about to do exactly that anyway --
#: and this is the module that once manufactured 29 commits in three and a quarter hours by looping
#: on its own output. Naming the outcome is the whole repair; spinning on it is the defect it would
#: reintroduce.
REFUSED_RACE = "REFUSED_RACE"

#: The two ways a shared tree refuses to advance. They are reported apart because they are cleared
#: apart -- one is a lane's uncommitted work, the other is usually a byte-identical twin of a file
#: origin is adding, and telling a reader "dirty" for both sends them down the wrong one.
#: Where a refreshed rival working copy's own bytes go before they are overwritten, mirrored from
#: `tools.refresh_to_head.PRESERVED_PREFIX` so a refusal can name the ref without importing it.
REFRESH_PRESERVED_PREFIX = "refs/preserved/refresh-to-head/"

#: THE SLUG CARRIES THE HEAD SHA AND THAT IS NOT DECORATION. `git update-ref` REPLACES a ref, so a
#: fixed slug would make each advance's preservation delete the previous one's -- the bytes go
#: unreachable and the `git log --all -S` route this tool advertises stops finding them, silently
#: and only for the runs nobody has needed yet. Keyed to the commit the copy was superseded by.
REFRESH_SLUG_STEM = "origin-reconcile-"

#: Where an UNTRACKED orphan draft's bytes go before it is removed. HELD APART FROM
#: `REFRESH_PRESERVED_PREFIX` on purpose: a refreshed tracked copy is recoverable from `git log
#: --all -S` OR from `git checkout HEAD -- <path>`, while an orphan's bytes exist in exactly one
#: place and nowhere else. A reader who found both classes under one ref would have no way to tell
#: which of their files still has a second home.
ORPHAN_PRESERVED_PREFIX = "refs/preserved/origin-reconcile-orphan/"

FF_MODIFIED = "modified here, and origin changes it too"
FF_UNTRACKED = "untracked here, and origin adds its own copy"
UNREADABLE = "UNREADABLE"
ERROR = "ERROR"

#: The gate's own lock. `background/process_run_complete.py` holds it for the whole publish
#: pipeline -- report regeneration, the site build and a scoped suite, five to twenty-five minutes.
RUN_LOCK_FILE = PROJECT_DIR / "docs" / "observability" / ".process_run_complete.lock"


def _git(cwd: Path, *args: str, timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True,
                          timeout=timeout)


def _paths(project: Path, *args: str) -> list[str] | None:
    """A `-z` path list from git, or `None` if git would not answer. Never a partial list."""
    try:
        res = _git(project, *args)
    except (OSError, subprocess.SubprocessError):
        return None
    if res.returncode != 0:
        return None
    return [p for p in (res.stdout or "").split("\0") if p]


def _arriving_paths(project: Path) -> list[str] | None:
    """Which paths the merge with origin would have to WRITE. Not which paths differ.

    THE DEFECT THIS EXISTS FOR (2026-09-10, measured; fixed 2026-09-11). This was
    `git diff --name-only HEAD origin/main`, which is the SYMMETRIC DIFFERENCE OF TWO ENDPOINT
    TREES -- it answers *which paths differ between HEAD and origin/main*. That is a proxy, and it
    is wrong in one direction: a path HEAD DELETED and origin still carries differs between the
    endpoints, so it was reported as arriving, but the merge result also lacks it, so git writes
    nothing there and it blocks nothing.

    It cost a permanent wedge, not a cosmetic one. `e4aa02359` deliberately took
    `docs/observability/head_red_observed.json` and `docs/staging/reference/HEAD_RED_REGISTER.md`
    out of the index while leaving them on disk (so a clean checkout inherits no machine night),
    and origin had not touched either since the merge base. Both were therefore reported as
    untracked blockers, for ever: the census producer rewrites both on every run, so they
    re-diverge from origin's base copy within minutes of any clearing, and an all-or-nothing
    clearing rule fed a self-regenerating false positive has no exit. The gap went 4 -> 9 -> 12 ->
    15 across one day with the same complaint every five minutes.

    Keyed to the PROPERTY and not to today's answer, which is the whole argument for the narrowing:
    if the merge result differs from HEAD at a path, git must write that path; if it does not
    differ, git writes nothing there. Note that this holds on a CONFLICTED merge too -- a conflicted
    path's merge-result blob holds git's markers, which differ from HEAD, so it is still reported.
    That is the poison leg in
    `tests/background/test_the_blocking_test_asked_which_paths_differ_not_which_the_merge_writes.py`.

    IT CANNOT HIDE A TRUE POSITIVE BY CONSTRUCTION, and that argument -- not the fact that it
    clears today's two -- is what it is keyed to. In the genuine fast-forward case HEAD is an
    ancestor, the merge result IS `origin/main`, and the behaviour is unchanged; the narrowing
    bites only on the diverged case, which is the case the old question was wrong in.

    FAILS TOWARD THE OLD, WIDER ANSWER rather than toward `None`. If `merge-tree --write-tree` is
    unavailable or will not answer, the endpoint diff is restored -- it OVER-reports, so an
    unreadable merge costs a false refusal a reader can clear by hand, where `None` would put the
    caller into "I could not look" and stop it naming any path at all.
    """
    merged = _git(project, "merge-tree", "--write-tree", "HEAD",
                  "{}/{}".format(REMOTE, BRANCH))
    # rc=1 IS A CONFLICT AND STILL WRITES A TREE -- only rc>1 is a failure to answer. The tree oid
    # is the first line; on conflict the lines after it are the conflicted entries and the messages.
    tree = merged.stdout.splitlines()[0].strip() if merged.stdout.strip() else ""
    if merged.returncode > 1 or not tree:
        return _paths(project, "diff", "--name-only", "-z", "HEAD",
                      "{}/{}".format(REMOTE, BRANCH))
    return _paths(project, "diff", "--name-only", "-z", "HEAD", tree)


def paths_blocking_fast_forward(project: Path | None = None) -> list[dict] | None:
    """Which local paths stop `merge --ff-only origin/main`, and which KIND each one is.

    A REFUSAL THAT NAMES NO CAUSE COSTS A WHOLE ORIENTATION (delivery queue, 2026-09-04): *"a
    permanently dirty shared tree can never fast-forward, and `origin_reconcile` correctly declines
    to force it while reporting a verdict that names no cause a reader can act on."* `NOT_ADVANCED`
    said how far behind the tree was and repeated git's first line; the reader then had to
    rediscover, by hand, which two paths were holding it -- and did, three separate times.

    THE TWO KINDS NEED DIFFERENT PEOPLE, which is why the kind is reported and not just the path:

      * `FF_MODIFIED` -- a tracked file this tree has edited that origin also changed. USUALLY, not
        always, a lane's uncommitted work: `tools/isolate_hunks.py --survey` is how that lane lands
        its hunks without waiting. But this kind is the OTHER kind's twin whenever somebody has run
        `git add` -- a byte-identical staging note that was staged rather than left untracked is
        classified here, and four of the five `FF_MODIFIED` paths holding the live tree on
        2026-09-05 hashed equal to origin. Reading this sentence as a verdict on the INSTANCE cost
        22 commits of divergence; `identical_tracked_twins` now asks each one.
      * `FF_UNTRACKED` -- an untracked file here that origin ADDS. Usually byte-identical, and then
        nobody's work is at stake at all: `git hash-object` against `git rev-parse
        origin/main:<path>` settles it in one command.

    Reads the `origin/main` ref as it already stands; it does NOT fetch, because every caller here
    has just been through `commits_behind`, which does. `None` means git would not answer, and it
    is deliberately distinct from `[]` -- "nothing collides" is a finding, "I could not look" is
    not, and a verdict that renders them the same is how a fail-open reads as a clean bill.
    """
    project = project or PROJECT_DIR
    incoming = _arriving_paths(project)
    modified = _paths(project, "diff", "--name-only", "-z", "HEAD")
    untracked = _paths(project, "ls-files", "--others", "--exclude-standard", "-z")
    if incoming is None or modified is None or untracked is None:
        return None
    arriving = set(incoming)
    blocking = [{"path": p, "kind": FF_MODIFIED} for p in sorted(arriving.intersection(modified))]
    blocking += [{"path": p, "kind": FF_UNTRACKED} for p in sorted(arriving.intersection(untracked))]
    return blocking


def _split_generated(modified: list[str]) -> tuple[list[str], list[str], str]:
    """Split modified blockers into a PRODUCER'S OUTPUT and a lane's actual work.

    THE THIRD KIND (delivery seat, 2026-09-09). `paths_blocking_fast_forward` names two kinds and
    `_landing_clause` gives each a step. Both steps assume the modified bytes are somebody's WORK,
    so the first thing the refusal says about a modified path is how to LAND it. On 2026-09-09 the
    one path holding the whole shared tree behind origin was `site/data/value_arms.json` -- the
    proof page's feed, written by a publisher, not by a person. Its local bytes were generated at
    04:25:38Z; origin's at 05:11:32Z. Landing the local ones, which is what this refusal advises
    first and in the most detail, would have re-published the "IN THE WORLD AS IT IS NOW" headline
    that origin's own commit `77d92e0d1` had just been written to DELETE. The remedy pointed at the
    one action that undoes another lane's fix.

    A GENERATED PATH IS NEVER A LANDING. Its bytes are a photograph of a run, so "whose work is
    this" has no answer and the question that does have one -- which run is later -- is settled by
    the fast-forward plus the next regeneration. Reverting is not a loss here, which is exactly
    what makes it the cheap move and exactly what the old text talked the reader out of.

    THE ORACLE ALREADY EXISTED. `tools/file_scope_generated_paths.generated_artefacts()` derives
    the set (176 members on 2026-09-09) for a different gate; 71 of the 658 modified paths in the
    live shared tree are in it, so this is a class and not one file.

    TWO ORACLES, UNIONED, BECAUSE ONE OF THEM CANNOT SEE ITS OWN CLASS (delivery seat, 2026-09-15).
    `generated_artefacts` is keyed to generated TREES, so a producer's output living in an AUTHORED
    tree is invisible to it by construction. `docs/design/orphan_baseline.json` -- written by
    `tools/orphan_ratchet.py --freeze`, a photograph of a scan -- is exactly that, and on 2026-09-15
    it was the single path holding the shared tree behind origin while this function called it
    authored and the refusal led with the landing recipe. Landing that photograph drops whatever
    rows origin's later freeze recorded: the same defect as `value_arms.json`, through the one door
    the tree-keyed oracle has no way to watch. `written_artefacts` is keyed to the WRITE SITE
    instead, so it finds that class; neither oracle subsumes the other, so the union is both.

    FAIL-SOFT, DELIBERATELY, AND THIS IS THE ONE PLACE THAT IS RIGHT. Everywhere else in this
    repository an oracle that cannot answer must fail CLOSED. Here the output is REMEDY PROSE, not
    a gate: raising would turn "I cannot classify these paths" into "the tree may not advance",
    which is strictly worse than the refusal we already print. So an unavailable oracle returns
    every path as authored AND the reason, and `_landing_clause` prints that reason -- an unsplit
    list that SAYS it is unsplit, never one that is silently indistinguishable from a clean split.

    AND A HALF-ANSWER SAYS WHICH HALF. With two oracles there is a third state the old two-valued
    note could not express: one answered and one did not, so the split is real but INCOMPLETE. The
    note is composed here, where which-one-failed is known, rather than reconstructed downstream
    from a reason string -- a reader told "UNSPLIT" about a list that was in fact half-split would
    check paths that were already classified and trust the ones that were not.
    """
    import tools.file_scope_generated_paths as oracle  # module, so a test can patch either half

    known: set[str] = set()
    unavailable: list[str] = []
    for name in ("generated_artefacts", "written_artefacts"):
        try:
            known |= {str(p) for p in getattr(oracle, name)()}
        except Exception as exc:  # oracle unavailable -- say so, do not guess and do not block
            unavailable.append("{}: {}: {}".format(name, type(exc).__name__, exc))
    if len(unavailable) == 2:
        return [], list(modified), (
            "NOTE: the generated-path oracles could not be asked ({}), so the {} modified path(s) "
            "above are UNSPLIT -- check by hand whether any is a producer's output before landing "
            "it".format("; ".join(unavailable), len(modified)))
    note = ""
    if unavailable:
        note = (
            "NOTE: only one of the two generated-path oracles could be asked ({}), so the split "
            "above is PARTIAL: a producer's output only the missing oracle would have recognised "
            "is listed as this tree's work -- check by hand before landing it".format(
                "; ".join(unavailable)))
    generated = [p for p in modified if p in known]
    authored = [p for p in modified if p not in known]
    return generated, authored, note


def _landing_clause(blocking: list[dict]) -> str:
    """The step that clears the named paths, per KIND, and the property that makes it the step.

    THE REFUSAL HAD THE WHOLE ANSWER IN IT AND STOPPED ONE STEP SHORT OF STATING IT (delivery
    seat, 2026-09-08, `SEAT_FINDING_THE_PUBLISHERS_OWN_REMEDY_CANNOT_CLEAR_ITS_OWN_REFUSAL...`).
    `process_run_complete` writes *"Reconcile first: `python3 -m background.origin_reconcile`"*
    into every `behind_origin` `cause_evidence`, and on a tree held by paths that are NOT
    byte-identical to origin's the only possible answer to that command is a second refusal. The
    publisher's failure count went 24, 25, 29 across three directions that each named it. Every
    reader of that state file was being routed to a command cited as clearing what it cannot.

    SO THE REMEDY IS NOT "RUN RECONCILE" -- it is *land or revert the blocking paths, THEN run
    reconcile*, and this module already enumerates those paths by name one sentence earlier.

    KEYED TO THE PROPERTY AND NOT TO A COMMAND LIST. The reason a landing clears the refusal is
    that `advance_shared_tree` removes a blocking path only when its bytes ALREADY equal what
    origin brings; landing makes them equal. That sentence is what stops the next reader
    re-running this module and expecting a different verdict, so it is stated rather than implied.

    PER KIND, BECAUSE THE TWO KINDS TAKE DIFFERENT DOORS -- `paths_blocking_fast_forward`'s own
    docstring says so, and a reader with only untracked blockers who is sent to `isolate_hunks`
    has been given the same dead end in a longer sentence.
    """
    modified = [b["path"] for b in blocking if b.get("kind") == FF_MODIFIED]
    untracked = [b["path"] for b in blocking if b.get("kind") == FF_UNTRACKED]
    generated, authored, oracle_failed = _split_generated(modified)
    steps = []
    if generated:
        steps.append(
            "the {} GENERATED path(s) ({}) are a PRODUCER'S OUTPUT, not work -- do NOT land them: "
            "their bytes are exhaust from a run this tree has already superseded, and landing "
            "them re-publishes whatever the producer last wrote over what origin brings. Clear "
            "them with `git show HEAD:<path> > <path>`, then let the fast-forward install "
            "origin's copy and the producer regenerate".format(
                len(generated), ", ".join(generated[:3]) + ("..." if len(generated) > 3 else "")))
    if authored:
        steps.append(
            "the {} MODIFIED path(s) are this tree's uncommitted work and clear by LANDING or "
            "reverting them here -- `python3 tools/isolate_hunks.py --survey <path>` lists the "
            "hunks and `python3 -m tools.surgical_land --content <path>=<isolated> <path>` lands "
            "your bytes without swapping the shared worktree".format(len(authored)))
    if oracle_failed and modified:
        # Composed by `_split_generated`, which is the only place that knows WHICH oracle was
        # missing and therefore what the reader may and may not trust about the split above.
        steps.append(oracle_failed)
    if untracked:
        # THE TWO DOORS ARE NOT SYMMETRIC AND SAYING SO IS THE WHOLE REPAIR. `FF_UNTRACKED` MEANS
        # ORIGIN ALREADY BRINGS A COPY -- that is the kind's definition, not a likelihood -- so
        # "land it" REPLACES origin's file rather than adding one, and an orphan draft left in a
        # shared tree is routinely the OLDER of the two. Measured 2026-09-24 on the live wedge: of
        # the three untracked blockers this refusal named, two were superseded drafts of documents
        # origin already carried, and landing either would have reverted a landed correction --
        # one of which existed solely to retract its own earlier recommendation. Removing is the
        # door that cannot lose, because `clear_untracked_twins` writes the bytes to a preserved
        # ref first; landing is the door that needs a direction established.
        steps.append(
            "the {} UNTRACKED path(s) are orphan drafts of files ORIGIN ALREADY BRINGS, so landing "
            "one REPLACES origin's copy rather than adding a file and an orphan is routinely the "
            "OLDER of the two -- establish the direction first (`git diff <(git show "
            "origin/main:<path>) <path>`) and land only a copy that is genuinely AHEAD. Removing "
            "is the lossless door: the bytes go to `{}` before they are cleared".format(
                len(untracked), ORPHAN_PRESERVED_PREFIX))
    if not steps:
        # A kind this function does not know about. Say so rather than printing a remedy that was
        # chosen for a different shape -- an unrecognised kind with a confident step attached is
        # how a reader is sent somewhere worse than nowhere.
        return ("This module clears a blocking path only when its bytes ALREADY equal what origin "
                "brings, and none of these paths is a kind it knows how to name a step for.")
    return ("THE STEP IS TO LAND OR REVERT THOSE PATHS, NOT TO RE-RUN THIS MODULE: it clears a "
            "blocking path only when the path's bytes ALREADY equal what origin brings, so a "
            "second run on this tree returns this same refusal. Specifically, {}. Then re-run "
            "`python3 -m background.origin_reconcile`.".format("; and ".join(steps)))


def _blocking_clause(blocking: list[dict] | None, ahead: int | None) -> str:
    """The named cause, rendered ahead of git's own words rather than after them.

    THE LANDING STEP IS ATTACHED ONLY TO THE LEG THAT NAMED PATHS. "I could not look" and
    "nothing collides" are not refusals a landing clears, and a remedy printed under either would
    read as a diagnosis this module never made.

    `ahead` IS REQUIRED, AND THAT IS THE REPAIR RATHER THAN A STYLE CHOICE. `advance_shared_tree`
    learned on 2026-09-05 that divergence is not a collision and that on a diverged tree NO
    working-tree path is the cause -- and it learned it for ITSELF. This renderer, which is what
    every reader and every daemon log line actually gets, was never told, and neither was
    `process_run_complete._refused_advance_cause` beside it. One rule, three implementations, the
    fix landed in one: the shape CLAUDE.md names as this project's most expensive recurring defect.

    MEASURED ON THE LIVE SHARED TREE 2026-09-24 at `ahead = 10, behind = 9`. This clause said
    *"Refused by 4 path(s) ... THE STEP IS TO LAND OR REVERT THOSE PATHS"* while
    `advance_shared_tree`, asked about the same tree in the same second, said *"No working-tree
    path is the cause and clearing twins would delete files and still not advance."* The delivery
    seat was then commissioned, in those words, to clear three of those paths -- a deletion bought
    for no advance, which is the one shape this module exists not to reach.

    SO A DEFAULT WOULD HAVE BEEN THE DEFECT UNDER A NEW NAME. An optional `ahead=None` keeps every
    existing caller compiling and keeps every existing caller wrong, and the only callers to get
    the repair would be the ones that already knew to ask. Required means a caller that has not
    put this question to git cannot render this sentence at all.

    `None` (git would not answer) is NOT folded into `0`. "I could not tell whether these paths
    are the cause" and "these paths ARE the cause" are different statements, and the landing
    remedy belongs only under the second.
    """
    if blocking is None:
        return ("The paths refusing the advance could NOT be established, so this names the fork "
                "and not its cause.")
    if not blocking:
        return ("NOTHING local collides with what origin brings, so the refusal is not a "
                "dirty-tree collision and git's own words are the whole of the cause.")
    listed = blocking[:12]
    dropped = len(blocking) - len(listed)
    named = "{} path(s): {}{}".format(
        len(blocking),
        "; ".join("{} ({})".format(b["path"], b["kind"]) for b in listed),
        " -- and {} further path(s) not listed here".format(dropped) if dropped else "")
    if ahead is None:
        return ("Whether this tree has DIVERGED could NOT be established, so whether any of these "
                "paths is the cause is unestablished and no landing step is named. {} collide(s) "
                "with what origin brings: {}.".format(len(blocking), named))
    if ahead:
        return ("This tree has DIVERGED -- {} local commit(s) that {}/{} does not have -- so NO "
                "working-tree path is the cause and landing or reverting these would advance "
                "nothing. {} collide(s) with what origin brings, listed only so they are not "
                "mistaken for it: {}. The fork closes by landing those commits on origin (the "
                "reconciler's own merge leg, `python3 -m background.origin_reconcile`), never by "
                "clearing paths here.".format(ahead, REMOTE, BRANCH, len(blocking), named))
    return "Refused by {}. {}".format(named, _landing_clause(blocking))


def _blob_here(project: Path, path: str) -> str | None:
    """The hash of the working-tree bytes at `path`, or None if git would not hash them."""
    try:
        res = _git(project, "hash-object", "--", path)
    except (OSError, subprocess.SubprocessError):
        return None
    return (res.stdout or "").strip() or None if res.returncode == 0 else None


def _blob_on_origin(project: Path, path: str) -> str | None:
    """The hash `origin/main` holds at `path`, or None if it holds nothing there."""
    try:
        res = _git(project, "rev-parse", "{}/{}:{}".format(REMOTE, BRANCH, path))
    except (OSError, subprocess.SubprocessError):
        return None
    return (res.stdout or "").strip() or None if res.returncode == 0 else None


def _blob_in_head(project: Path, path: str) -> str | None:
    """The hash `HEAD` holds at `path`, or None if HEAD holds nothing there.

    The discriminator between the two shapes an `FF_MODIFIED` twin arrives in, and they need
    different commands to clear: a path HEAD knows is restored to HEAD's copy, a path HEAD has
    never seen is a STAGED ADD and has to leave the index entirely.
    """
    try:
        res = _git(project, "rev-parse", "HEAD:{}".format(path))
    except (OSError, subprocess.SubprocessError):
        return None
    return (res.stdout or "").strip() or None if res.returncode == 0 else None


def identical_tracked_twins(project: Path | None = None,
                            blocking: list[dict] | None = None) -> list[str] | None:
    """Of the `FF_MODIFIED` paths blocking the advance, those whose bytes ALREADY equal origin's.

    THE UNTRACKED SWEEP IS DEFEATED BY `git add`, AND NOTHING NOTICED FOR 22 COMMITS. Measured on
    the live shared tree 2026-09-05: fourteen paths held the fast-forward, nine untracked and five
    tracked. `identical_untracked_twins` matched all nine — and the all-or-nothing property then
    correctly cleared none of them, because five `FF_MODIFIED` paths stood. **Four of those five
    hashed EQUAL to origin's blob at the same path.** Two were staging notes another lane had
    `git add`-ed, one was a test file, and one was this module's own source: origin's copy of it,
    already on disk, classified as a lane's uncommitted work because the index had seen it.

    So thirteen of the fourteen blockers were files about to be replaced by themselves, the sweep
    built for exactly that sentence saw nine, and a byte-identical twin's fate depended on whether
    anybody had happened to stage it. `paths_blocking_fast_forward` says `FF_UNTRACKED` is *"usually
    byte-identical"* and says of `FF_MODIFIED` that it *"belongs to whichever lane is holding it"* —
    true of the kind, and not true of the instance, which is the whole defect.

    THE SAFETY ARGUMENT IS THE SIBLING'S, UNCHANGED. If the working-tree bytes at `P` equal origin's
    blob at `P`, that content is already ON origin: returning `P` to HEAD cannot lose it, and the
    very fast-forward this unblocks writes those same bytes back to that same path. What the tree
    holds at `P` before and after is identical. Anything that does NOT hash-match is a lane's real
    work and stays refused — `background/process_run_complete.py` was the fifth path, carried 58
    lines origin has never seen, and is exactly the judgement this must not automate.

    THE COMPARISON IS AGAINST THE WORKING TREE, NOT THE INDEX, and they are not the same file. Of
    the four twins measured, one was unstaged (index at HEAD, worktree at origin) and three were
    staged. The fast-forward refuses on what it would overwrite on disk, so disk is the subject.

    `None` (git would not answer) is kept distinct from `[]` (nothing matched), for the reason the
    sibling gives: a caller that cannot tell them apart would discard on an unread state.
    """
    project = project or PROJECT_DIR
    if blocking is None:
        return None
    twins = []
    for entry in blocking:
        if entry.get("kind") != FF_MODIFIED:
            continue
        path = entry["path"]
        here, theirs = _blob_here(project, path), _blob_on_origin(project, path)
        if here is None or theirs is None:
            return None
        if here == theirs:
            twins.append(path)
    return sorted(twins)


def restore_tracked_twin(project: Path | None = None, path: str = "") -> str | None:
    """Return one hash-proven `FF_MODIFIED` twin to what HEAD holds. `None` on success, else why not.

    NOT A DELETION, AND NOT THE SIBLING'S `unlink` EITHER. An untracked twin is cleared by removing
    it; a tracked one has an index entry, and removing the file leaves that entry behind and the
    fast-forward still refused. Two shapes, discriminated by `_blob_in_head`:

      * HEAD holds the path — `git checkout HEAD -- <path>` puts index and worktree back to HEAD's
        copy. The fast-forward then writes origin's copy, which is the bytes that were there.
      * HEAD has never seen it (a staged ADD) — there is no HEAD copy to restore to, so the entry
        leaves the index and the file leaves the disk, and the fast-forward adds it as origin's.

    THE ONE CASE THIS IS NOT SAFE IN IS THE ONE IT IS NEVER CALLED IN. `git checkout HEAD -- <path>`
    over a path a lane is holding dirty would destroy that lane's work, which is why the caller only
    reaches here for paths `identical_tracked_twins` has hash-proven against origin. The recovery,
    if it is ever needed, is the sibling's: `git checkout origin/main -- <path>` returns any of them
    exactly, because that is where the bytes were read from.
    """
    project = project or PROJECT_DIR
    in_head = _blob_in_head(project, path)
    try:
        if in_head is not None:
            res = _git(project, "checkout", "HEAD", "--", path)
            if res.returncode != 0:
                return (res.stderr or res.stdout or "").strip()[:200] or "git checkout refused"
            return None
        res = _git(project, "rm", "--cached", "--quiet", "--", path)
        if res.returncode != 0:
            return (res.stderr or res.stdout or "").strip()[:200] or "git rm --cached refused"
        (project / path).unlink(missing_ok=True)
    except (OSError, subprocess.SubprocessError) as exc:
        return "{}: {}".format(type(exc).__name__, exc)
    return None


def identical_untracked_twins(project: Path | None = None,
                              blocking: list[dict] | None = None) -> list[str] | None:
    """Of the paths blocking the advance, those whose bytes ALREADY equal what origin brings.

    THE SENTENCE THIS ACTS ON WAS ALREADY IN `paths_blocking_fast_forward`, AND ONLY A READER COULD
    ACT ON IT: *"`FF_UNTRACKED` -- an untracked file here that origin ADDS. Usually byte-identical,
    and then nobody's work is at stake at all: `git hash-object` against `git rev-parse
    origin/main:<path>` settles it in one command."* It settled it for a human and for nothing else,
    so the advance kept refusing on files whose content it was about to write back unchanged.

    Measured 2026-09-04 on the live shared tree: of the two paths holding the fast-forward,
    `...SEND_ONCE_MEMORY...md` hashed `792088eca` on disk and `792088eca` on origin. Identical. Git
    refuses that fast-forward anyway -- correctly, because it will not clobber an untracked file --
    and the refusal was protecting a file from being replaced by itself.

    WHY HASH EQUALITY IS THE WHOLE SAFETY ARGUMENT. If the bytes at `P` equal origin's blob at `P`,
    the content is already ON origin: removing the local copy cannot lose it, and the very
    fast-forward this unblocks writes those same bytes back to that same path. The file goes from
    untracked to tracked and its content never changes. Anything that does NOT hash-match is a
    lane's real work and stays refused -- that judgement is not what this automates.

    `None` (git would not answer) is kept distinct from `[]` (nothing matched) all the way up: a
    caller that cannot tell them apart would delete on an unread state.
    """
    project = project or PROJECT_DIR
    if blocking is None:
        return None
    twins = []
    for entry in blocking:
        if entry.get("kind") != FF_UNTRACKED:
            continue
        path = entry["path"]
        here, theirs = _blob_here(project, path), _blob_on_origin(project, path)
        if here is None or theirs is None:
            return None
        if here == theirs:
            twins.append(path)
    return sorted(twins)


def stale_copy_verdicts(project: Path | None = None,
                        paths: list[str] | None = None) -> dict[str, tuple[bool, str]] | None:
    """For each path, `(is_refreshable, why)` judged against ORIGIN's blob. `None` if unreadable.

    THE THIRD CLASS, AND IT IS THE ONE THAT REFILLS THE QUEUE ONCE PER LANDING. The two twin
    sweeps beside this one clear a path whose bytes ALREADY equal origin's. That proof is
    unavailable for the blocker this tree actually grows: `tools/surgical_land --content` does not
    write the working tree -- deliberately, because that is what makes it safe on a file two lanes
    hold -- so EVERY correct landing through that door leaves a working copy strictly behind its
    own commit, and the next fast-forward refuses on it. Clearing that by hand is what was done on
    2026-09-15, and the list refilled in three hours. A refusal whose remedy is provable and which
    nothing automatically applies, standing in front of a queue that refills once per landing, is a
    wedge with no exit.

    THE PROOF IS `tools/refresh_to_head.py`'s, ENTIRE, AND IT IS NOT RE-CUT HERE. Its three
    conjunctive preconditions are exactly what "this costs the holding lane nothing" means:
    the copy supplies no NAME the judgement tree lacks (computed over both blobs, never asserted);
    `stale_copy_refusal.judge` HAS a complaint about it (without which this is `git checkout` with
    a nicer name, which is a wall here); and the bytes reach a `refs/preserved/*` commit whose
    advertised `git log --all -S` recovery is RUN before a byte is destroyed.

    ASKED AGAINST `origin/main` AND NOT AGAINST HEAD. The caller has already established
    `ahead == 0`, so HEAD is an ancestor of origin and is exactly the stale base
    `stale_copy_refusal`'s own banner warns its verdicts are unsafe against. A copy superseded by a
    landing that reached origin but not yet this HEAD reads as an ORDINARY EDIT against HEAD and is
    refused -- the wrong answer, arrived at honestly, which is the shape that survives review.

    THE REFUSAL REASON IS CARRIED, NOT DISCARDED. Every path this cannot prove is residue the
    caller must refuse on, and it must refuse BY NAME with the reason attached: "not byte-identical
    to origin" was the whole of what the old refusal could say, and it is true of a path that is
    holder work and of a path nobody has a reader for alike.
    """
    project = project or PROJECT_DIR
    if paths is None:
        return None
    if not paths:
        return {}
    try:
        from tools.refresh_to_head import REFRESHABLE, judge_copy
    except ImportError as exc:
        # FAIL-CLOSED, and it reads as a refusal for every path rather than as an empty result:
        # `{}` here would mean "nothing is refreshable", which is what a caller acts on.
        return {p: (False, "the stale-copy judgement could not be imported ({}), so whether this "
                           "copy costs its lane anything is UNESTABLISHED".format(exc))
                for p in paths}
    verdicts = {}
    for path in sorted(set(paths)):
        try:
            verdict = judge_copy(project, path, base="{}/{}".format(REMOTE, BRANCH))
        except Exception as exc:  # noqa: BLE001 -- an unread judgement is a refusal, never a pass
            verdicts[path] = (False, "the stale-copy judgement raised {}: {}".format(
                type(exc).__name__, exc))
            continue
        verdicts[path] = (verdict.state == REFRESHABLE, verdict.reason)
    return verdicts


def refresh_slug(project: Path | None = None) -> str:
    """`origin-reconcile-<head sha>`, so one advance's preservation cannot replace another's."""
    project = project or PROJECT_DIR
    try:
        res = _git(project, "rev-parse", "--short", "HEAD")
        head = (res.stdout or "").strip() if res.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        head = ""
    return REFRESH_SLUG_STEM + (head or "unknown-head")


def refresh_stale_copies(project: Path | None = None, paths: list[str] | None = None,
                         slug: str | None = None) -> str | None:
    """Write HEAD's bytes over the proven-stale copies, preserving them first. `None` on success.

    A THIN SEAM ON PURPOSE. Everything that decides is `refresh_to_head.refresh`'s, including the
    preservation and the verified recovery route; this exists so the caller has one call to make
    under the tree lock and one failure string to report. It re-runs the judgement rather than
    trusting the survey the caller already took, because the tree is shared and minutes may have
    passed -- a second lane's edit arriving between the survey and the write turns a proven-lossless
    refresh into the deletion this whole module refuses to make.
    """
    project = project or PROJECT_DIR
    if not paths:
        return None
    try:
        from tools.refresh_to_head import RefreshError, refresh
    except ImportError as exc:
        return "the stale-copy refresh could not be imported: {}".format(exc)
    try:
        rc, text = refresh(project, sorted(set(paths)), slug or refresh_slug(project), write=True,
                           base="{}/{}".format(REMOTE, BRANCH))
    except RefreshError as exc:
        return "refresh-to-head refused mid-move and wrote nothing: {}".format(exc)
    except (OSError, subprocess.SubprocessError) as exc:
        return "refresh-to-head failed: {}: {}".format(type(exc).__name__, exc)
    if rc != 0:
        return "refresh-to-head refused and wrote nothing: {}".format(
            " ".join(text.split())[:300])
    return None


def _origin_text(project: Path, path: str) -> bytes | None:
    """What `origin/main` holds at `path`, as bytes, or `None` if it would not answer."""
    try:
        res = subprocess.run(["git", "show", "{}/{}:{}".format(REMOTE, BRANCH, path)],
                             cwd=str(project), capture_output=True, check=False, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return res.stdout if res.returncode == 0 else None


def _orphan_probe(local: bytes, theirs: bytes) -> str | None:
    """The longest non-trivial line the local copy has and origin's copy does not.

    REUSED, NOT RE-CUT: `tools.refresh_to_head._trivial` is the repo's existing rule for "a line
    too common to identify a commit", and a second opinion on what counts as trivial would make
    two preservations searchable by different rules. If it cannot be imported there is no probe
    rather than a home-made one -- `None` is a stated limit on the recovery route, and a weaker
    probe that silently found the wrong commit would not be.
    """
    try:
        from tools.refresh_to_head import _trivial
    except ImportError:
        return None
    try:
        mine = local.decode("utf-8").splitlines()
        yours = set(theirs.decode("utf-8").splitlines())
    except UnicodeDecodeError:
        return None
    unique = [ln for ln in mine if ln not in yours and not _trivial(ln)]
    return max(unique, key=len) if unique else None


def generated_output_verdicts(project: Path | None = None,
                              paths: list[str] | None = None) -> dict[str, tuple[bool, str]] | None:
    """For each TRACKED blocker, `(is_producer_output, why)`. `None` if the oracles would not answer.

    THE FIFTH CLASS, AND IT IS THE ONE THE PUBLISHER MINTS AGAINST ITSELF EVERY TICK. The four
    classes beside this one each prove the local bytes are safe by reading them: hash-equal to
    origin (the two twin sweeps), strictly superseded by origin (`stale_copy_verdicts`), or carried
    onto a ref first (`untracked_orphan_verdicts`). A producer's output defeats all four at once. It
    is never hash-equal, because the producer rewrote it after the last landing and will rewrite it
    again on the next tick. And `stale_copy_verdicts` cannot reach it either, for a reason that has
    nothing to do with its content: `refresh_to_head` reads Python, so every `.json` feed and every
    `.md` document it is asked about comes back *"this control has no reader for .json files, so it
    CANNOT establish that the copy has nothing to lose"* -- fail-closed, correctly, on a question
    that was never answerable in that language.

    SO THE PATH IS PERMANENTLY UNRESOLVABLE AND THE ALL-OR-NOTHING RULE MAKES IT FATAL TO EVERY
    OTHER CLASS. Measured on the live shared tree 2026-09-18, 7.8 days into the seventh publish
    stretch with `last_clean_publish: null` and 74 episode failures: eleven paths held the advance,
    six of them untracked twins the sweep had already proven lossless, and `site/data/value_arms.json`
    -- the arms producer's own feed, rewritten 01:24 that morning -- was one of the four that held
    them hostage. The reconciler had merged and pushed from its isolated worktree on the cadence all
    week, so origin kept moving while the shared tree could not follow, and each cadence re-opened
    the fork the last one closed. That is the loop, and the exhaust is inside it.

    THE MODULE ALREADY ASSERTED THIS, IN PROSE, AND NEVER ACTED ON IT. `_split_generated` asks the
    same two oracles a few hundred lines above and `_landing_clause` prints the answer to a human:
    *"the GENERATED path(s) are a PRODUCER'S OUTPUT, not work -- do NOT land them"*. The refusal
    that then holds the tree says it cannot establish whether that same path is one lane's work.
    Both sentences are in the same refusal, about the same path, and only one of them is acted on.
    This closes that gap rather than adding a reader: the oracle that knows is the one already
    imported.

    THE SAFETY ARGUMENT IS THE TWIN'S, ON DIFFERENT GROUND. For a twin the claim is *these bytes are
    already on origin*; here it is *these bytes are not authored at all*. A generated artefact is a
    photograph of a run, re-derivable by running its producer, and the very next tick rewrites it
    regardless of what this does. Restoring it to HEAD therefore costs no lane anything the tick
    would not have destroyed anyway -- and the act is the twin's own `restore_tracked_twin`, so the
    fast-forward writes origin's bytes over it a moment later.

    BOTH ORACLES MUST ANSWER, AND UNAVAILABLE IS A REFUSAL -- WHICH IS THE OPPOSITE OF
    `_split_generated`'S RULE AND DELIBERATELY SO. There the output is remedy prose and failing soft
    costs a reader a hand-check; here the output decides whether a file is written over, so an
    unasked oracle must never read as "not generated" (which is merely a refusal) NOR as "generated"
    (which is a deletion bought on an unread state). `None` is returned for the whole batch, and
    `advance_shared_tree` turns that into the same refusal every other unreadable comparison gets.

    A PATH THE ORACLES DO NOT KNOW IS AUTHORED WORK AND STAYS REFUSED, which is what
    `tests/background/test_process_run_complete.py` and `tests/tools/test_fold_noise_floor_family.py`
    correctly did on that same tree -- both carried test functions origin has never seen, and
    neither is this cadence's judgement to make.
    """
    project = project or PROJECT_DIR
    if not paths:
        return {}
    import tools.file_scope_generated_paths as oracle  # module, so a test can patch either half

    known: set[str] = set()
    for name in ("generated_artefacts", "written_artefacts"):
        try:
            known |= {str(p) for p in getattr(oracle, name)()}
        except Exception:  # noqa: BLE001 - an unasked oracle never decides a write; see docstring
            return None
    verdicts: dict[str, tuple[bool, str]] = {}
    for path in paths:
        if path not in known:
            verdicts[path] = (False, (
                "neither generated-path oracle knows this path, so it is this tree's own authored "
                "work and no producer can be asked to re-derive it"))
            continue
        # THE BLOB IS ASKED FOR, NOT ASSUMED. `restore_tracked_twin` writes HEAD's bytes, so a path
        # HEAD does not hold would be un-restorable and the advance would refuse a second time on a
        # file this had already reported as cleared.
        if _blob_in_head(project, path) is None:
            verdicts[path] = (False, (
                "a producer's output, but HEAD holds no blob at this path, so there are no bytes "
                "to restore it to and clearing it here would refuse again at the advance"))
            continue
        verdicts[path] = (True, (
            "a PRODUCER'S OUTPUT, not any lane's work -- re-derivable by running its producer, and "
            "rewritten by the next tick whatever happens here, so restoring it to HEAD for the "
            "fast-forward to overwrite costs nothing that was authored"))
    return verdicts


def untracked_orphan_verdicts(project: Path | None = None,
                              paths: list[str] | None = None) -> dict[str, tuple[bool, str]] | None:
    """For each UNTRACKED blocker, `(is_preservable, why)`. `None` if git would not answer.

    THE FOURTH CLASS, AND IT IS THE ONE EVERY CORRECT LANDING MINTS. The three classes beside this
    one all rest on a proof that the local bytes are already somewhere: hash-equal to origin
    (twins), or strictly superseded by origin (`stale_copy_verdicts`). An UNTRACKED file whose path
    origin ADDS has neither proof available and cannot: `refresh_to_head.judge_copy` needs HEAD's
    blob as a base and HEAD has none, and `preserve` refuses a path that is not in HEAD. So
    `advance_shared_tree` subtracted untracked non-twins from its candidates entirely, and a blocker
    in this class held the shared tree behind origin for as long as nobody cleared it by hand.

    IT IS NOT RARE AND IT IS NOT A RACE -- IT IS WHAT LANDING A STAGING DOCUMENT DOES. A seat
    writes `docs/staging/X.md` in the shared tree (untracked), then lands it through
    `surgical_land --content` from an isolated worktree, which by design does not write the shared
    working tree. The landed copy is routinely EDITED in the act of landing -- the document gains
    its own "DONE, landed with this finding" paragraph -- so the copy origin adds is not the copy
    on disk here, the twin sweep cannot match it, and the orphan wedges the next fast-forward.
    Measured on the live shared tree 2026-09-17: `origin/main` carried a 9,846-byte copy of
    `SEAT_RESULT_THE_PUBLISHED_EIGHTEEN_POOLS_TWO_VALUE_ARMS...` landed at 22:49 in `471dfd417`,
    this tree held the 8,906-byte draft the same seat wrote at 22:36, and that one file was one of
    the two paths holding a checkout five commits behind while the publisher recorded
    `last_clean_publish: null` and a wedge 7.68 days old.

    THE LOSSLESSNESS HERE IS MANUFACTURED, NOT PROVEN, AND THAT IS THE WHOLE DIFFERENCE. There is
    no argument that these bytes are already safe -- they are on no branch, which is what UNTRACKED
    means. So this verdict does not claim they cost nothing; it claims only that they can be READ,
    and the caller MUST commit them to a ref and verify the advertised recovery route reaches them
    before it removes one. A `True` here that the caller acted on without preserving would be the
    deletion this module exists not to make.

    WHY THAT IS ENOUGH HERE AND IS NOT ENOUGH FOR THE TRACKED HOLDER WORK BESIDE IT. A path origin
    is ADDING is a path where two authors have written the same document and one of them has
    landed. The unlanded copy could not reach that path without a merge in any case, and its bytes
    come back in one command. Tracked holder work -- a lane's edit to a file that already exists --
    stays refused, because there the working copy is the only form the work has and the lane is
    mid-turn on it; that class is landed, never displaced, and `stale_copy_verdicts` keeps saying
    so by name.
    """
    project = project or PROJECT_DIR
    if paths is None:
        return None
    if not paths:
        return {}
    verdicts: dict[str, tuple[bool, str]] = {}
    for path in sorted(set(paths)):
        theirs = _origin_text(project, path)
        if theirs is None:
            verdicts[path] = (False, "{}/{} holds nothing readable at this path, so what the "
                                     "advance would put here is UNESTABLISHED".format(
                                         REMOTE, BRANCH))
            continue
        try:
            local = (project / path).read_bytes()
        except OSError as exc:
            verdicts[path] = (False, "the working copy could not be read ({}), so its bytes could "
                                     "not be preserved and it is never removed".format(exc))
            continue
        if local == theirs:
            # The twin sweep owns this shape and clears it without preserving anything. Reaching
            # here means the sweep was not asked, and a second, weaker route to the same act is
            # how two mechanisms drift apart.
            verdicts[path] = (False, "byte-identical to what origin brings -- this is the twin "
                                     "sweep's path, not this one's")
            continue
        verdicts[path] = (True, "an untracked draft of a document origin ADDS at the same path; "
                                "its {} byte(s) are on no branch, so they are preserved on a ref "
                                "and the recovery route is verified BEFORE it is removed".format(
                                    len(local)))
    return verdicts


def preserve_untracked_orphans(project: Path | None = None, paths: list[str] | None = None,
                               slug: str | None = None) -> tuple[str | None, str]:
    """Commit the untracked orphans' CURRENT bytes onto a ref. `(commit, "")` or `(None, why not)`.

    THE IDIOM IS `refresh_to_head.preserve`'s AND SO IS THE VERIFICATION -- what could not be
    reused is the one line that refuses a path HEAD does not carry, which is every path here. The
    tree is HEAD's with these paths ADDED through a throwaway `GIT_INDEX_FILE`, so the holder's
    real index is untouched, and the parent is HEAD, so the commit's own diff is exactly the bytes
    about to be destroyed -- which is what `git log --all -S` searches.

    NOTHING IS REPORTED AS PRESERVED THAT WAS NOT PROVEN TO COME BACK. Both legs of
    `verify_recoverable` run here, per path: the blob under the commit must hash to what is on disk
    right now, and the advertised `git log --all -S` lookup must actually FIND the commit. A
    preservation the advertised search cannot reach is a preservation in name only, and the
    difference is invisible until somebody needs it.

    A PATH WITH NO LINE ORIGIN LACKS GETS NO `-S` PROBE AND SAYS SO. That is the strict-subset
    draft -- the safest member of the class, since every line of it is on origin already -- and
    printing a search command that would find nothing would be worse than naming none.
    """
    project = project or PROJECT_DIR
    if not paths:
        return None, "nothing to preserve"
    slug = slug or refresh_slug(project)
    ref = ORPHAN_PRESERVED_PREFIX + slug
    try:
        head = _git(project, "rev-parse", "HEAD")
        if head.returncode != 0:
            return None, "HEAD could not be read, so nothing was preserved and nothing removed"
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, GIT_INDEX_FILE=str(Path(tmp) / "index"))
            read = subprocess.run(["git", "read-tree", "HEAD"], cwd=str(project), env=env,
                                  capture_output=True, text=True, check=False, timeout=120)
            if read.returncode != 0:
                return None, "the throwaway index could not be built ({}), so nothing was " \
                             "preserved".format((read.stderr or "").strip()[:160])
            for path in paths:
                blob = _git(project, "hash-object", "-w", "--", path)
                if blob.returncode != 0:
                    return None, "{} could not be written to the object store ({}), so nothing " \
                                 "was preserved and nothing removed".format(
                                     path, (blob.stderr or "").strip()[:160])
                add = subprocess.run(
                    ["git", "update-index", "--add", "--cacheinfo",
                     "100644,{},{}".format((blob.stdout or "").strip(), path)],
                    cwd=str(project), env=env, capture_output=True, text=True, check=False,
                    timeout=120)
                if add.returncode != 0:
                    return None, "{} could not be added to the throwaway index ({}), so nothing " \
                                 "was preserved".format(path, (add.stderr or "").strip()[:160])
            written = subprocess.run(["git", "write-tree"], cwd=str(project), env=env,
                                     capture_output=True, text=True, check=False, timeout=120)
            if written.returncode != 0:
                return None, "the preservation tree could not be written ({}), so nothing was " \
                             "preserved".format((written.stderr or "").strip()[:160])
        made = _git(project, "commit-tree", (written.stdout or "").strip(),
                    "-p", (head.stdout or "").strip(),
                    "-m", "preserved untracked shared-tree drafts before origin-reconcile "
                          "cleared them for the fast-forward: {}".format(", ".join(paths)))
        if made.returncode != 0:
            return None, "the preservation commit could not be made ({}), so nothing was " \
                         "removed".format((made.stderr or "").strip()[:160])
        commit = (made.stdout or "").strip()
        updated = _git(project, "update-ref", ref, commit)
        if updated.returncode != 0:
            return None, "the preservation ref {} could not be moved ({}), so the commit is " \
                         "unreachable and nothing was removed".format(
                             ref, (updated.stderr or "").strip()[:160])
    except (OSError, subprocess.SubprocessError) as exc:
        return None, "the preservation raised {}: {} -- nothing was removed".format(
            type(exc).__name__, exc)

    try:
        from tools.refresh_to_head import RefreshError, verify_recoverable
    except ImportError as exc:
        return None, "the preservation could not be VERIFIED ({}), and an unverified preservation " \
                     "is not one -- nothing was removed".format(exc)
    for path in paths:
        try:
            local = (project / path).read_bytes()
            theirs = _origin_text(project, path) or b""
            verify_recoverable(project, commit, path, local, _orphan_probe(local, theirs))
        except (RefreshError, OSError) as exc:
            return None, "the preserved bytes for {} did not come back ({}), so nothing was " \
                         "removed".format(path, " ".join(str(exc).split())[:200])
    return commit, ""


def advance_shared_tree(project: Path | None = None, *, blockers_fn=None, twins_fn=None,
                        tracked_twins_fn=None, ff_fn=None, remover=None, restorer=None,
                        locker=None, ahead_fn=None, stale_fn=None, refresher=None,
                        orphans_fn=None, preserver=None, generated_fn=None) -> dict:
    """Fast-forward the shared tree onto `origin/main`, clearing every blocker it can prove lossless.

    Returns `{"advanced": bool, "cleared": list[str], "reason": str}`. `advanced` is claimed only
    when git itself reported the fast-forward, never inferred from the absence of an error.

    FOUR CLASSES, AND THE LAST TWO ARE THE ONES THE QUEUE REFILLS WITH. Two are byte-identical
    twins proven by hash against origin's blob (untracked, cleared by `unlink`; tracked, cleared by
    `restore_tracked_twin`). The third is a rival working copy origin strictly supersedes, proven by
    `tools/refresh_to_head.py`'s three conjunctive preconditions and cleared by writing HEAD's bytes
    over it after preserving its own -- see `stale_copy_verdicts`. The fourth is an UNTRACKED draft
    of a document origin ADDS at the same path, which has no HEAD blob for either of those proofs to
    stand on and was subtracted out of the candidate set entirely until 2026-09-17; it is cleared
    only after its bytes reach a ref whose recovery route has been RUN -- see
    `untracked_orphan_verdicts`. The fifth, added 2026-09-18, is a PRODUCER'S OWN OUTPUT: never
    hash-equal because its producer rewrites it every tick, and invisible to the stale judgement
    because `refresh_to_head` reads Python and a `.json` feed is not Python -- so it was permanently
    unresolvable and, under the all-or-nothing rule below, fatal to every other class beside it. See
    `generated_output_verdicts`. All five are resolvable; a blocker in none of them refuses
    everything, by name and with its reason attached.

    THE THREE THAT PROVE AND THE ONE THAT MANUFACTURES. Classes one to three each rest on an
    argument that the bytes are already safe somewhere. The fourth cannot: untracked means on no
    branch. So its safety is BUILT rather than found -- preserved, verified, then removed -- and the
    ordering below is load-bearing, not tidy: the preservation runs first inside the lock and a
    failure there is a refusal that has touched nothing.

    THE LOOP THIS EXISTS TO BREAK, measured over 24h to 2026-09-04 from the deadman's own log: the
    reconciler reached a window on 129 of 165 cadences (`GATE_RUNNING` only 36), gated its merge
    clean, pushed it, and then could not advance the shared tree -- `NOT_ADVANCED`, on untracked
    staging notes that origin was adding its own copy of. So origin moved, this tree did not, the
    publish path read BEHIND and dropped a completed cycle, and the next cadence started one deeper.
    The stand-down for the gate was never the binding constraint; this was.

    ALL-OR-NOTHING, AND THAT IS A SAFETY PROPERTY, NOT TIDINESS. Nothing is touched unless clearing
    the twins would leave the fast-forward with nothing else to refuse on. A tree holding one
    NON-TWIN path cannot fast-forward however many identical files are cleared, so clearing them
    there would be a deletion bought for no advance -- the one shape in which this could actually
    cost someone something.

    THAT SENTENCE WAS FALSE FOR ONE CAUSE, AND IT IS THE CAUSE THE LIVE TREE HAD ON 2026-09-05.
    "Nothing else to refuse on" was only ever tested against the DIRTY-TREE collisions
    `paths_blocking_fast_forward` enumerates. A tree that has diverged -- local commits origin does
    not have -- cannot fast-forward for a reason no working-tree path can express, and git says so
    in words this module never read: *"Diverging branches can't be fast-forwarded"*. Measured here
    that day: `behind 32, ahead 5`, and `paths_blocking_fast_forward` still answered with 18 paths,
    none of which was the cause. Had those 18 all hashed equal to origin -- the state the twin sweep
    exists to reach, and the one it was about to be handed -- this would have taken the tree lock,
    unlinked the untracked twins, restored the tracked ones, and then failed the second `--ff-only`
    exactly as before. A deletion bought for no advance: the named worst case, reached through the
    door the guard was not watching.

    SO DIVERGENCE IS ASKED FIRST, AND IT IS ASKED OF GIT, NOT OF THE TREE. `commits_ahead` is the
    same seam `reconcile` already trusts to decide whether a merge is legitimate at all. Unreadable
    is a REFUSAL, like every other comparison here: a file is never deleted on a question that was
    not answered.

    THE WINDOW IS REAL AND IT IS MINUTES WIDE. `reconcile` reads `ahead` once at the top, then
    merges, gates and pushes before calling this -- and several sessions and daemons commit into
    this one tree throughout. The tree that was level when `reconcile` looked is routinely diverged
    by the time the advance runs, so this is not a guard against a hypothetical.

    AND THE SET IT IS ALL-OR-NOTHING OVER GREW ON 2026-09-05. It used to be the untracked twins
    alone, so a tracked blocker was fatal to the whole attempt whatever its content -- and four of
    the five tracked blockers on the live tree that day were byte-identical to origin, holding nine
    untracked twins hostage behind them. `identical_tracked_twins` carries that measurement. Both
    kinds are now proven the same way (hash against origin's blob) and cleared differently
    (`unlink` for untracked, `restore_tracked_twin` for tracked), and the comparison is over
    the union, so one genuinely dirty path still refuses everything -- which is what
    `background/process_run_complete.py`, the fifth path, correctly did.

    AND THE TWO SIDES OF THAT COMPARISON WERE DIFFERENT DOMAINS UNTIL 2026-09-09. `resolvable` is a
    deduplicated set of PATHS; `blocking` is a list of (path, kind) ENTRIES, and ONE PATH CAN BE
    BOTH KINDS AT ONCE -- a staged deletion whose file is still on disk is reported by `git diff
    --name-only HEAD` (worktree differs from HEAD) *and* by `git ls-files --others` (the index has
    no entry for it). Comparing `len(resolvable) != len(blocking)` then counted that single path
    twice on one side and once on the other, and refused an advance its own rule permitted.

    THE TELL WAS IN THE REFUSAL'S OWN WORDS and no reader had cause to disbelieve it: *"0 of 2
    blocking path(s) are NOT byte-identical to what origin brings, so clearing the 1 that are would
    delete files and still not advance. Held by: "* -- zero held, and a refusal anyway. Measured on
    the live shared tree 2026-09-09, where it had held the tree 2 commits behind origin and
    `.publish_gate_state.json` recorded `last_clean_publish: null` with `wedge_since` 32 hours old.
    The arithmetic was the wedge; the tree's bytes at the one blocking path were already EXACTLY
    origin's blob.

    SO THE COMPARISON IS OVER PATH SETS ON BOTH SIDES, and it is expressed as "which paths are
    held" rather than as two lengths. A refusal that can name nothing it is holding is not a
    refusal, and stating it that way makes the domain error unrepresentable rather than merely
    fixed -- `held` is now the thing tested, and it is the thing reported.

    THE REMOVAL AND THE ADVANCE ARE UNDER ONE TREE LOCK. Between them the tree is missing files it
    is about to be given back; another writer landing in that window would see a tree that never
    legitimately existed. Losing the lock is a refusal, not a wait -- the next cadence is 5 minutes
    away and a reconciler that blocks on a lock is a reconciler that misses its window.
    """
    project = project or PROJECT_DIR
    _ff = ff_fn or (lambda: _git(project, "merge", "--ff-only",
                                 "{}/{}".format(REMOTE, BRANCH)))

    first = _ff()
    if first.returncode == 0:
        return {"advanced": True, "cleared": [],
                "reason": "fast-forwarded onto {}/{} with nothing in the way".format(
                    REMOTE, BRANCH)}

    # BEFORE ANY PATH IS JUDGED, ASK WHETHER A FAST-FORWARD WAS POSSIBLE AT ALL. Divergence is not
    # a collision and no amount of clearing addresses it, so this has to come ahead of the twin
    # comparison rather than beside it -- the blocking set is non-empty on a diverged tree too, and
    # it names paths that are not the cause.
    ahead = (ahead_fn or commits_ahead)(project)
    if ahead is None:
        return {"advanced": False, "cleared": [],
                "reason": "git refused the fast-forward and whether this tree holds commits origin "
                          "does NOT could not be established, so nothing was cleared -- a file is "
                          "never deleted on a question that was not answered"}
    if ahead:
        return {"advanced": False, "cleared": [],
                "reason": "git refused the fast-forward because this tree has DIVERGED -- {} local "
                          "commit(s) that {}/{} does not have. No working-tree path is the cause "
                          "and clearing twins would delete files and still not advance, so nothing "
                          "was touched. The fork closes by landing those commits on origin (the "
                          "reconciler's own merge leg, `python3 -m background.origin_reconcile`), "
                          "never by clearing paths here. git: {}".format(
                              ahead, REMOTE, BRANCH,
                              (first.stderr or first.stdout or "").strip()[:200])}

    blocking = (blockers_fn or paths_blocking_fast_forward)(project)
    if blocking is None:
        return {"advanced": False, "cleared": [],
                "reason": "git refused the fast-forward and the paths holding it could NOT be "
                          "established, so nothing was removed on a state nobody read"}
    if not blocking:
        return {"advanced": False, "cleared": [],
                "reason": "git refused the fast-forward and NOTHING local collides with what "
                          "origin brings, so the cause is not a dirty-tree collision and removing "
                          "files would not address it: {}".format(
                              (first.stderr or first.stdout or "").strip()[:200])}

    twins = (twins_fn or identical_untracked_twins)(project, blocking)
    tracked = (tracked_twins_fn or identical_tracked_twins)(project, blocking)
    if twins is None or tracked is None:
        return {"advanced": False, "cleared": [],
                "reason": "whether the blocking paths match origin byte for byte could not be "
                          "established, so nothing was removed -- a file is never deleted on an "
                          "unread comparison"}
    resolvable = sorted(set(twins) | set(tracked))
    # BOTH SIDES ARE PATH SETS. `blocking` carries one ENTRY PER (path, kind) and a single path can
    # hold both kinds at once -- a staged deletion whose file is still on disk is `FF_MODIFIED` and
    # `FF_UNTRACKED` together. Comparing lengths counted it twice against a deduplicated union and
    # refused with an EMPTY held list, which is the 2026-09-09 wedge. What refuses is a path nobody
    # hash-proved, so that is what is computed and what is reported.
    blocked_paths = {b["path"] for b in blocking}
    # THE THIRD CLASS IS ASKED ONLY OF WHAT THE TWO HASH PROOFS COULD NOT TAKE, and only of paths
    # git already TRACKS. An untracked path is not a rival working copy of anything -- HEAD holds
    # no bytes to write over it -- and asking the stale-copy judgement about one gets a `NO_BASE`
    # refusal that reads like a verdict.
    untracked_only = {b["path"] for b in blocking if b.get("kind") == FF_UNTRACKED} - {
        b["path"] for b in blocking if b.get("kind") == FF_MODIFIED}
    candidates = sorted(blocked_paths - set(resolvable) - untracked_only)
    verdicts = (stale_fn or stale_copy_verdicts)(project, candidates)
    if verdicts is None:
        return {"advanced": False, "cleared": [],
                "reason": "whether the remaining blocking paths are copies origin strictly "
                          "supersedes could not be established, so nothing was touched -- a file "
                          "is never written over on an unread comparison"}
    stale = sorted(p for p, (ok, _) in verdicts.items() if ok)
    # THE FIFTH CLASS, ASKED ONLY OF THE TRACKED BLOCKERS THE STALE JUDGEMENT COULD NOT TAKE --
    # which, for a `.json` feed or a `.md` document, is EVERY one of them, because
    # `refresh_to_head` reads Python and returns "no reader for this file type" rather than a
    # verdict. That refusal is right and is not what changes; what changes is that a path it cannot
    # read is no longer the end of the enquiry when a producer's output is what it is.
    gen_verdicts = (generated_fn or generated_output_verdicts)(
        project, sorted(p for p in candidates if p not in set(stale)))
    if gen_verdicts is None:
        return {"advanced": False, "cleared": [],
                "reason": "whether the remaining blocking paths are a producer's own output could "
                          "not be established (a generated-path oracle would not answer), so "
                          "nothing was touched -- a file is never written over on an unread "
                          "classification"}
    generated = sorted(p for p, (ok, _) in gen_verdicts.items() if ok)
    # THE FOURTH CLASS, ASKED ONLY OF WHAT THE OTHER THREE LEFT. An untracked path origin ADDS has
    # no HEAD blob, so neither hash proof nor `refresh_to_head`'s judgement can reach it, and until
    # 2026-09-17 it was subtracted out of the candidate set and held the tree indefinitely. Its
    # losslessness is MANUFACTURED below -- preserved on a ref, recovery verified -- not asserted
    # here, so this list is only ever the set the preservation is attempted over.
    orphan_verdicts = (orphans_fn or untracked_orphan_verdicts)(
        project, sorted(untracked_only - set(resolvable)))
    if orphan_verdicts is None:
        return {"advanced": False, "cleared": [],
                "reason": "whether the untracked blocking paths could be preserved was not "
                          "established, so nothing was touched -- a file is never removed on an "
                          "unread comparison"}
    orphans = sorted(p for p, (ok, _) in orphan_verdicts.items() if ok)
    resolvable = sorted(set(resolvable) | set(stale) | set(generated) | set(orphans))
    held = sorted(blocked_paths - set(resolvable))
    if held:
        # KEYED TO THE PROPERTY AND NOT TO TODAY'S PATHS: what reaches this list is a blocker NO
        # available proof could show costs its holding lane nothing -- neither hash equality with
        # origin nor `refresh_to_head`'s three conjunctive preconditions. The per-path reason is
        # carried through because "not byte-identical to origin" is equally true of holder work
        # nobody may touch and of a file this tree has no reader for, and those want opposite acts.
        named = []
        for path in held[:12]:
            why = (verdicts.get(path) or gen_verdicts.get(path) or orphan_verdicts.get(path)
                   or (False, "not byte-identical to what origin brings"))[1]
            named.append("{} -- {}".format(path, " ".join(str(why).split())[:220]))
        return {"advanced": False, "cleared": [],
                "reason": "{} of {} blocking path(s) could NOT be proven lossless, so clearing the "
                          "{} that could would touch files and still not advance. Nothing was "
                          "written. Held by: {}".format(
                              len(held), len(blocked_paths), len(resolvable), "; ".join(named))}

    try:
        from background.tree_lock import TreeLockTimeout, tree_lock
    except ImportError as exc:
        return {"advanced": False, "cleared": [],
                "reason": "the tree lock could not be imported ({}), and the shared tree is never "
                          "written without it".format(exc)}
    _remove = remover or (lambda p: (project / p).unlink())
    _restore = restorer or (lambda p: restore_tracked_twin(project, p))
    _lock = locker or (lambda: tree_lock(timeout=ADVANCE_LOCK_TIMEOUT_SECONDS))
    # READ ONCE, BEFORE THE ADVANCE. `refresh_slug` is keyed to HEAD, and HEAD MOVES three lines
    # below: a reason that recomputed it after the fast-forward would name a ref that does not
    # exist, which is worse than naming none -- the reader would search for it and conclude the
    # bytes were never preserved.
    slug = refresh_slug(project)
    _refresh = refresher or (lambda p: refresh_stale_copies(project, p, slug))
    _preserve = preserver or (lambda p: preserve_untracked_orphans(project, p, slug))
    # A GENERATED BLOCKER IS CLEARED BY THE TRACKED TWIN'S ACT, because the act is what the two
    # share and the PROOF is what differs: both are tracked paths restored to HEAD's bytes for the
    # fast-forward to overwrite, one proven lossless by hashing against origin and the other by
    # being nobody's work. Folding it into `tracked_set` here, rather than giving it a fourth
    # branch in the loop below, keeps the acts at three and the grounds at five.
    tracked_set, stale_set, orphan_set = (
        set(tracked) | set(generated), set(stale), set(orphans))
    orphan_commit = ""
    try:
        with _lock():
            # THE PRESERVATION GOES FIRST OF ALL, because it is the only thing standing between the
            # orphans and a deletion nothing can undo. It is all-or-nothing with itself and it
            # VERIFIES the recovery route before returning, so reaching the next line means every
            # orphan's bytes are on a ref and have been read back out of it.
            if orphan_set:
                orphan_commit, failure = _preserve(sorted(orphan_set))
                if failure:
                    return {"advanced": False, "cleared": [],
                            "reason": "the {} untracked orphan draft(s) could not be PRESERVED, so "
                                      "nothing was removed and the advance was not attempted -- "
                                      "bytes that are on no branch are never destroyed on a "
                                      "preservation that did not verify: {}".format(
                                          len(orphan_set), failure)}
            # THE REFRESH GOES NEXT AND IT IS ALL-OR-NOTHING WITH ITSELF. `refresh_to_head`
            # writes nothing unless every path it is handed is refreshable, so a failure here has
            # touched no byte and the twins beside it are still on disk untouched.
            if stale_set:
                failure = _refresh(sorted(stale_set))
                if failure:
                    return {"advanced": False, "cleared": [],
                            "reason": "the {} stale working copy/copies origin supersedes could "
                                      "not be refreshed, so nothing was touched and the advance "
                                      "was not attempted: {}".format(len(stale_set), failure)}
            cleared = []
            for path in resolvable:
                if path in stale_set:
                    # Already written above, and by a different act: a rival copy is REPLACED by
                    # HEAD's bytes, not removed and not restored from the index.
                    cleared.append(path)
                    continue
                # The two kinds are cleared by different acts and the difference is not cosmetic:
                # `unlink` on a path with an index entry leaves that entry behind, and the
                # fast-forward stays refused on a file that is no longer even on disk.
                try:
                    if path in tracked_set:
                        failure = _restore(path)
                    else:
                        _remove(path)
                        failure = None
                except OSError as exc:
                    failure = str(exc)
                if failure:
                    return {"advanced": False, "cleared": cleared,
                            "reason": "clearing the byte-identical twin {} failed ({}), so the "
                                      "advance was not attempted; {} earlier twin(s) were already "
                                      "cleared and origin holds every one of them".format(
                                          path, failure, len(cleared))}
                cleared.append(path)
            second = _ff()
    except TreeLockTimeout as exc:
        return {"advanced": False, "cleared": [],
                "reason": "another writer held the tree lock ({}), so nothing was removed and "
                          "nothing was moved; the next cadence tries again".format(exc)}

    if second.returncode == 0:
        return {"advanced": True, "cleared": cleared,
                "reason": "cleared {} blocking path(s) ({} tracked twin(s), {} untracked twin(s), "
                          "{} stale copy/copies origin supersedes, preserved at {}{}; {} untracked "
                          "orphan draft(s), preserved at {}{} as {}), then fast-forwarded -- every "
                          "one is on disk, tracked, holding origin's bytes: {}".format(
                              len(cleared), len(tracked_set),
                              len(cleared) - len(tracked_set) - len(stale_set) - len(orphan_set),
                              len(stale_set), REFRESH_PRESERVED_PREFIX, slug,
                              len(orphan_set), ORPHAN_PRESERVED_PREFIX, slug,
                              (orphan_commit or "-")[:9],
                              "; ".join(cleared[:12]))}
    # THE TWINS ARE NOT RESTORED HERE, AND THAT IS DELIBERATE. Their content is on origin by the
    # hash equality that selected them, so `git checkout origin/main -- <path>` returns any of them
    # exactly; re-writing them from a second guess at what they held would be this module inventing
    # bytes. The reason names them so the next reader has the command's arguments already.
    # THE STALE COPIES ARE NAMED APART FROM THE TWINS, because their recovery route is NOT the
    # twins'. A twin's bytes are on origin by the hash equality that selected it, so
    # `git checkout origin/main -- <path>` returns it exactly. A refreshed rival copy's own bytes
    # are on NO branch: the only thing that holds them is the preserved commit, and a reason that
    # sent the reader to origin for them would be sending them to bytes that were never theirs.
    return {"advanced": False, "cleared": cleared,
            "reason": "cleared {} blocking path(s) and git STILL refused the fast-forward, which "
                      "means the cause was not the collision this cleared. Recover a twin with "
                      "`git checkout {}/{} -- <path>`: {}.{}{} git: {}".format(
                          len(cleared), REMOTE, BRANCH, "; ".join(sorted(
                              set(cleared) - stale_set - orphan_set)[:12]),
                          (" The {} refreshed rival copy/copies ({}) are on NO branch and come "
                           "back only from {}{}.".format(
                               len(stale_set), "; ".join(sorted(stale_set)[:12]),
                               REFRESH_PRESERVED_PREFIX, slug)) if stale_set else "",
                          (" The {} untracked orphan draft(s) ({}) are on NO branch and come back "
                           "only from {}{} ({}).".format(
                               len(orphan_set), "; ".join(sorted(orphan_set)[:12]),
                               ORPHAN_PRESERVED_PREFIX, slug,
                               (orphan_commit or "-")[:9])) if orphan_set else "",
                          (second.stderr or second.stdout or "").strip()[:200])}


def commits_ahead(project: Path | None = None) -> int | None:
    """How many commits local HEAD is AHEAD of `origin/main`. None if it cannot be established.

    THE OTHER HALF OF THE FORK, AND I SHIPPED THIS MODULE WITHOUT IT (2026-09-02). The director's
    complaint was *"landed in the tree, reported as landed, not pushed"* — and the first version of
    this reconciler only closed the BEHIND direction. Its own landing then sat unpushed, which is
    the same defect reproduced inside the fix for it, found by running the verification step that
    the same finding says I should have been running all along.

    Nothing else pushes a `surgical_land` landing. The publish path pushes its OWN commits and
    carries whatever else is on the branch, so a landing reaches origin only when a publish happens
    to follow it — and a blocked publish path means no landing ever leaves the machine. Reconcile
    has to mean BOTH directions or it does not mean agreement.
    """
    project = project or PROJECT_DIR
    try:
        counted = _git(project, "rev-list", "--count", "{}/{}..HEAD".format(REMOTE, BRANCH))
        if counted.returncode != 0:
            return None
        return int((counted.stdout or "").strip())
    except (ValueError, OSError, subprocess.SubprocessError):
        return None


def commits_behind(project: Path | None = None) -> int | None:
    """How many commits `origin/main` is AHEAD of local HEAD. None if it cannot be established.

    Fetches first: the whole question is about a ref that moves under us. `None` is a distinct
    answer from `0` and every caller treats it as "do not act", because a reconciler that cannot
    read origin must not decide anything about it.
    """
    project = project or PROJECT_DIR
    try:
        if _git(project, "fetch", REMOTE, BRANCH, "--quiet").returncode != 0:
            return None
        counted = _git(project, "rev-list", "--count", "HEAD..{}/{}".format(REMOTE, BRANCH))
        if counted.returncode != 0:
            return None
        return int((counted.stdout or "").strip())
    except (ValueError, OSError, subprocess.SubprocessError):
        return None


def _fresh_worktree(project: Path, path: Path) -> tuple[bool, str]:
    """A worktree at local HEAD, owner-marked so nothing sweeps it mid-merge.

    AND IT ASKS THE MARKER BEFORE IT REMOVES, which is the leg that was missing (2026-09-04). The
    marker below exists so `fork_salvage` and `fork_reconciler` do not sweep a merge in progress —
    and this function, which owns the only path either of them would sweep, did not read it. So the
    ONE mechanism `WORKTREE` is not protected from is a second copy of this module: every reconciler
    shares one fixed path, nothing here takes a lock, and `gate_is_running` answers about the
    PUBLISH gate, never about another reconciler.

    REPRODUCED ON REAL DISK, not argued. At 2026-09-04 23:39Z the deadman's reconcile was ~40s into
    `surgical_land --merge` in `/var/tmp/se-origin-reconcile`; a seat ran `python3 -m
    background.origin_reconcile` — which is the command `_divergence_refusal` PRINTS to every reader
    of a publish refusal — and this function force-removed and recreated that directory under the
    running merge's cwd. Measured 3 minutes later: the marker held the second (by then killed) pid
    while the deadman's merge was still executing against a tree rebuilt beneath it.

    A REFUSAL AND NEVER A WAIT. `reconcile` renders this as ERROR with the reason attached, and the
    deadman comes back in five minutes; blocking here would hold the cadence for up to
    `MERGE_TIMEOUT_SECONDS`. The two legs of `worktree_is_live` are what make refusing safe rather
    than permanent — a killed reconciler's marker fails the pid check, so nothing wedges on a crash.
    """
    try:
        from background.seat_executor import worktree_is_live
        if path.exists() and worktree_is_live(path):
            return False, ("another writer holds {} (owner marker live, or the worktree is "
                           "git-locked), so removing it would rebuild the tree under a merge that "
                           "is already running -- refusing rather than waiting, because the "
                           "cadence returns in minutes and a held cadence is a reconciler that is "
                           "not there when its window opens".format(path))
        if path.exists():
            _git(project, "worktree", "remove", "--force", str(path))
        _git(project, "worktree", "prune")
        added = _git(project, "worktree", "add", "--detach", "-q", str(path), "HEAD")
        if added.returncode != 0:
            return False, (added.stderr or added.stdout or "worktree add failed").strip()[:300]
        # DECLARE IT IN USE. `fork_reconciler`'s reaper is armed and on the deadman cycle now, and
        # `fork_salvage` sweeps dirty worktrees; a merge in progress is exactly the state both are
        # built to clean up after. The marker is the one sanctioned way to say "a writer is here",
        # and it carries a lease, so an abandoned reconciliation frees itself.
        try:
            from background.seat_executor import OWNER_MARKER
            (path / OWNER_MARKER).write_text(str(os.getpid()) + "\n")
        except Exception:  # noqa: BLE001 - a marker that cannot be written costs a race, not the merge
            pass
        return True, ""
    except (OSError, subprocess.SubprocessError) as exc:
        return False, "{}: {}".format(type(exc).__name__, exc)


def _drop_worktree(project: Path, path: Path) -> None:
    try:
        (path / ".se_worktree_owner").unlink(missing_ok=True)
        _git(project, "worktree", "remove", "--force", str(path))
        _git(project, "worktree", "prune")
    except (OSError, subprocess.SubprocessError):
        pass


def _classify_merge_failure(output: str) -> tuple[str, str]:
    """Which refusal the gated merge door gave. The two mean different things to a reader.

    Conflict is a JUDGEMENT — two lanes edited one file and someone has to choose. A red gate is a
    DEFECT — the merged tree does not pass, and merging it would publish a regression. Neither is
    retried, and telling them apart is what makes the report actionable rather than a stack trace.
    """
    if "MERGE CONFLICT" in output:
        return REFUSED_CONFLICT, output.split("MERGE CONFLICT", 1)[1].strip()[:400]
    if "GATE RED" in output:
        return REFUSED_GATE, output.split("GATE RED", 1)[1].strip()[:400]
    return ERROR, output.strip()[-400:]


def _classify_push_failure(output: str) -> tuple[str, str]:
    """Which refusal the push gave — a race we lost, or a push that genuinely failed.

    THE SAME DISTINCTION `_classify_merge_failure` DRAWS, one step later, and for the same reason:
    the two are cleared apart, so folding them into one `ERROR` sends a reader down the wrong one.
    A lost race clears itself on the next cadence; a broken push does not clear at all.

    KEYED TO GIT'S OWN WORDS FOR THE CONDITION, not to the exit code, because every push failure
    shares the exit code. Both spellings are matched: `[rejected] ... (non-fast-forward)` is what
    the ref line says, and `(fetch first)` is what it says when the remote has commits we have not
    fetched — the same race, reported differently depending on whether the ref was stale locally.

    FAILS TOWARD `ERROR`, which is the pessimistic side: an unrecognised push failure is called a
    real fault and gets looked at. The cost of that direction is a glance; the cost of the other is
    a genuinely broken reconciler filed as a benign race and never read again.
    """
    lowered = output.lower()
    if "non-fast-forward" in lowered or "fetch first" in lowered:
        return REFUSED_RACE, (
            "the merge gated clean and origin moved before the push landed, so it was refused as a "
            "non-fast-forward and the gate was spent. NOTHING IS OWED: the next cadence re-fetches, "
            "re-merges on the new base and gates again. git said: {}".format(output.strip()[:300]))
    return ERROR, "merge gated clean but the push was rejected: {}".format(output.strip()[:300])


def fork_state(project: Path | None = None) -> tuple[int | None, int | None]:
    """`(behind, ahead)` in one call — the module's ONE window onto the world.

    ONE SEAM SO A PIN CANNOT GO PARTIAL (2026-09-02). `reconcile` first read only `commits_behind`,
    and `tests/background/conftest.py` pinned exactly that, correctly. Adding `commits_ahead` an
    hour later made the pin cover half the rung's live reads, and the other half went straight back
    to asking git about a remote — 28 assertions in `test_deadmans_switch.py` red again, for the
    second time, on the same cause.

    A pin against a list of functions is fail-open on the next function. A pin against one seam is
    not, and any future world-read added here has to come through this door or be a new seam that
    is visible as one.
    """
    project = project or PROJECT_DIR
    return commits_behind(project), commits_ahead(project)


def gate_is_running(project: Path | None = None) -> bool:
    """True while `process_run_complete` holds its run lock -- the publish gate is mid-flight.

    NEVER MOVE ORIGIN UNDER A RUNNING GATE (director, 2026-09-02). The gate builds a checkout,
    runs a scoped suite for five to twenty-five minutes, and then asks whether it may commit. A
    push that lands while it runs turns a green gate into a non-fast-forward refusal at the last
    step, so the whole run is spent and discarded -- and on a cadence, spent and discarded every
    time.

    Probed by trying the lock rather than by reading a pid, because the lock is what the gate
    itself contends on and a pid file can outlive its process. The hold is microseconds between
    acquiring and releasing; a gate that tried to start inside that window would skip its marker,
    which `background_worker.process_leftover_run_markers()` sweeps up by design. Opened `a` and
    not `w`: the gate opens it `w`, and a probe must not truncate the thing it is inspecting.

    Fails toward TRUE -- "a gate may be running" -- on any error. Refusing to act on an unreadable
    lock costs one cadence; acting on it costs a gate run.
    """
    import fcntl

    path = (project or PROJECT_DIR) / "docs" / "observability" / ".process_run_complete.lock"
    try:
        if not path.exists():
            return False
        with open(path, "a") as fh:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return True
            fcntl.flock(fh, fcntl.LOCK_UN)
        return False
    except OSError:
        return True


def shared_tree(start: Path | None = None) -> Path | None:
    """The MAIN worktree of this repository — the tree the publisher actually runs from.

    WHY THIS IS NOT `PROJECT_DIR` (2026-09-08, Lane 0). `PROJECT_DIR` is
    `Path(__file__).resolve().parent.parent`, so it is whichever tree the module was IMPORTED from.
    That is the shared tree only when the caller happens to be running there. The delivery seat's
    executor is instructed to work in an isolated linked worktree, and the publisher writes
    `python3 -m background.origin_reconcile` into its own `cause_evidence` as the remedy for
    `behind_origin` — so the seat runs the remedy from the worktree, and every leg of this module
    then asks its question of the wrong tree.

    MEASURED, not reasoned about. At 2026-09-08T22:30Z, from `/var/tmp/se-seat-executor`:
    `commits_behind()` returned **0** and `reconcile()` returned `LEVEL: local and origin/main
    agree; nothing to reconcile` with exit code 0, while the shared tree
    `/home/rich/synthetic-enterprise` was **2 commits behind** origin/main and the publisher running
    from it had `last_clean_publish: null` and 30 consecutive failures. The remedy reported success
    about a tree nothing publishes from.

    IT IS NOT ONLY THE LEVEL CHECK. `reconcile` threads `project` into `fork_state`,
    `gate_is_running` and `advance_shared_tree` alike, so from a linked worktree the gate-lock guard
    reads a lock file at the wrong path (`docs/observability/.process_run_complete.lock` under the
    worktree, which no gate ever writes) and reads "no gate running" while one holds the real lock.
    Fixing the SUBJECT at the entry point fixes every leg at once; that is why this is resolved here
    and not by patching the level comparison.

    FAILS CLOSED. `None` when the main worktree cannot be established, because this module's whole
    discipline is "not acting on a state that was not observed" — and a fallback to `PROJECT_DIR`
    would silently restore the defect on exactly the machines where git could not answer. `main`
    refuses with the cause named rather than reconciling something it could not identify.
    """
    # `start` IS INJECTABLE so this can be asserted on a real main-plus-linked pair in a tmp repo.
    # Called with the default in production and with a built linked worktree in its control: pinning
    # it to `PROJECT_DIR` made the only available subject "whichever tree pytest runs in", so the
    # control would have been vacuous in the shared tree and informative only by accident elsewhere.
    res = _git(start or PROJECT_DIR, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if res.returncode != 0:
        return None
    common = Path((res.stdout or "").strip())
    # `--git-common-dir` is the MAIN worktree's `.git`, from any linked worktree or from the main
    # tree itself. Its parent is the tree. A bare repository has no worktree to reconcile.
    return common.parent if common.name == ".git" and common.parent.is_dir() else None


def reconcile(project: Path | None = None, *, worktree: Path | None = None,
              state_fn=None, behind_fn=None, ahead_fn=None, runner=None, pusher=None,
              make_worktree=None, drop_worktree=None, gate_fn=None, blockers_fn=None,
              advance_fn=None) -> dict:
    """Close the fork with origin, or say exactly why it stayed open. Never raises.

    Returns {"status", "detail", "behind", "pushed"}. Fully injectable, because every one of its
    real steps is destructive-adjacent and none of them belongs in a test.
    """
    project = project or PROJECT_DIR
    worktree = worktree or WORKTREE
    # `behind_fn`/`ahead_fn` stay as per-leg overrides for the tests that pin one direction; the
    # DEFAULT goes through the single seam, which is the thing a fixture pins.
    _behind, _ahead = (state_fn or fork_state)(project)
    behind = behind_fn(project) if behind_fn else _behind

    if behind is None:
        return {"status": UNREADABLE, "behind": None, "pushed": False,
                "detail": "origin is unreadable, so whether a fork exists cannot be established -- "
                          "not acting on a state that was not observed"}
    # NOT BEHIND IS NOT THE SAME AS AGREEING. Local may be AHEAD, and nothing else on this
    # machine pushes a gated landing -- see `commits_ahead`. Read unconditionally now, because
    # AHEAD is what decides whether a merge is legitimate at all (see below).
    ahead = ahead_fn(project) if ahead_fn else _ahead
    if ahead is None:
        return {"status": UNREADABLE, "behind": behind, "pushed": False,
                "detail": "how far LOCAL is ahead could not be established -- not acting on a "
                          "state that was not observed"}
    if behind == 0 and ahead == 0:
        return {"status": LEVEL, "behind": 0, "pushed": False,
                "detail": "local and origin/main agree; nothing to reconcile"}

    # NEVER WHILE A GATE IS RUNNING. Everything below either moves origin or moves the shared
    # tree, and both invalidate a gate that is mid-flight against them.
    if (gate_fn or gate_is_running)(project):
        return {"status": GATE_RUNNING, "behind": behind, "pushed": False,
                "detail": "the publish gate holds its run lock, so origin and the shared tree are "
                          "left exactly where it found them; reconciling under a running gate "
                          "spends the whole run and refuses it at the last step"}

    if behind == 0:
        pushed = (pusher or _push)(project)
        if pushed.returncode != 0:
            # AND THE SAME RACE AT THE OTHER PUSH SITE. This leg pushes gated landings that were
            # sitting local-only, and origin can move under it exactly as it can under the merge
            # leg below -- `behind == 0` was read before the push, not during it. Classified through
            # the SAME helper rather than a second hand-rolled string test beside it: the module's
            # own history is a repair made at one of two sites and not the other, and a branch that
            # hand-rolls what a helper centralises regresses every repair the helper holds.
            status, detail = _classify_push_failure(
                (pushed.stderr or "") + (pushed.stdout or ""))
            return {"status": status, "behind": 0, "pushed": False,
                    "detail": "local is {} commit(s) ahead. {}".format(ahead, detail)}
        return {"status": PUSHED, "behind": 0, "pushed": True,
                "detail": "pushed {} gated landing(s) that were sitting local-only".format(ahead)}

    if ahead == 0:
        # NOTHING OF OURS TO LAND, SO THERE IS NOTHING TO MERGE. This is the branch that did not
        # exist, and its absence ran a loop for three and a quarter hours (2026-09-02).
        #
        # A merge here builds a commit whose tree is ALREADY origin's -- the second parent's, byte
        # for byte -- so it changes no content and exists only to move a ref. Pushing it moves
        # origin forward by one; the shared tree stays where it was, because it is dirty and git
        # rightly refuses to fast-forward over 554 modified files; so the next cadence reads
        # BEHIND again, one deeper, and does it all over. 29 commits, one every 6m20s, and the
        # condition it was built to clear was the condition it was manufacturing. Directly: the
        # gate's own log read *"origin/main is 30 commit(s) AHEAD of HEAD ... would widen the fork
        # by one more"* -- refusing the provenance banner on a fork this module had made.
        #
        # The only honest move when we have nothing to contribute is to ADVANCE, not to commit.
        adv = (advance_fn or advance_shared_tree)(project)
        if adv["advanced"]:
            return {"status": FAST_FORWARDED, "behind": behind, "pushed": False,
                    "cleared_paths": adv["cleared"],
                    "detail": "fast-forwarded {} commit(s) from origin; nothing of ours needed "
                              "landing, so no commit was made and origin was not touched. "
                              "{}".format(behind, adv["reason"])}
        blocking = (blockers_fn or paths_blocking_fast_forward)(project)
        # RE-ASKED, NOT REUSED FROM LINE ~1591. The window between that read and this one is the
        # one `advance_shared_tree` documents as minutes wide -- several sessions commit into this
        # tree throughout -- and the sentence being rendered is a claim about NOW. The old text
        # ended "the tree advances when the lane holding those paths lands or reverts them", which
        # is false of a fork and is the instruction the 2026-09-24 seat was handed.
        return {"status": NOT_ADVANCED, "behind": behind, "pushed": False,
                "blocking_paths": blocking, "cleared_paths": adv["cleared"],
                "detail": "origin is {} commit(s) ahead, this machine has NOTHING to land, and the "
                          "shared tree will not fast-forward. {} Nothing was committed and "
                          "nothing was pushed -- a merge with no work of ours in it would only "
                          "widen the fork it claims to close. advance: {}".format(
                              behind,
                              _blocking_clause(blocking, (ahead_fn or commits_ahead)(project)),
                              adv["reason"])}

    ok, why = (make_worktree or _fresh_worktree)(project, worktree)
    if not ok:
        return {"status": ERROR, "behind": behind, "pushed": False,
                "detail": "could not build an isolated worktree: {}".format(why)}
    try:
        # THE SANCTIONED DOOR, RUN INSIDE THE ISOLATION. `surgical_land --merge` gates the tree the
        # merge would create and refuses on conflict; both properties are inherited rather than
        # reimplemented, so this module adds isolation and a caller, and no new way to commit.
        merge = (runner or _run_merge)(worktree)
        if merge.returncode != 0:
            status, detail = _classify_merge_failure((merge.stdout or "") + (merge.stderr or ""))
            return {"status": status, "behind": behind, "pushed": False, "detail": detail}

        pushed = (pusher or _push)(worktree)
        if pushed.returncode != 0:
            status, detail = _classify_push_failure(
                (pushed.stderr or "") + (pushed.stdout or ""))
            return {"status": status, "behind": behind, "pushed": False, "detail": detail}

        # THE SAME ADVANCE THE `ahead == 0` LEG USES, not a second hand-rolled `--ff-only` beside
        # it. This is the leg the 24h measurement caught failing most often: the merge gates clean
        # and pushes, and then the shared tree will not take what was just pushed because an
        # untracked staging note is sitting on the path origin adds. Copying the old one-liner here
        # would have left this leg refusing on twins that the other leg had learned to clear.
        adv = (advance_fn or advance_shared_tree)(project)

        # THE STATUS MUST DESCRIBE THE SUBJECT, NOT THE STEPS. The first version returned
        # RECONCILED whenever the merge and the push succeeded, and put "shared tree NOT advanced"
        # in the DETAIL, where nothing read it. So it reported success 29 times running while the
        # fork it was reconciling grew by one each time. A control that does not re-read its
        # subject after acting cannot tell "I fixed it" from "I did the steps".
        # THE AHEAD COUNT WAS ALREADY HERE AND WAS BEING THROWN AWAY. `fork_state` returns both
        # directions; this leg read the pair and discarded the one that decides whether any path
        # below is the cause at all. It is the same post-push re-read the comment above argues for,
        # so no extra git call buys it.
        still_behind, still_ahead = (state_fn or fork_state)(project)
        if still_behind:
            blocking = (blockers_fn or paths_blocking_fast_forward)(project)
            return {"status": NOT_ADVANCED, "behind": still_behind, "pushed": True,
                    "blocking_paths": blocking, "cleared_paths": adv["cleared"],
                    "detail": "the merge gated clean and was pushed, but the shared tree did NOT "
                              "advance and is still {} commit(s) behind. {} This is NOT a closed "
                              "fork -- origin moved and this tree did not, which is precisely the "
                              "state that loops if it is retried on a cadence. advance: {}".format(
                                  still_behind, _blocking_clause(blocking, still_ahead),
                                  adv["reason"])}
        return {"status": RECONCILED, "behind": behind, "pushed": True,
                "cleared_paths": adv["cleared"],
                "detail": "merged {} commit(s) from origin in an isolated worktree, gated, pushed, "
                          "and the shared tree is level with origin -- re-read after the fact, not "
                          "assumed from the steps succeeding".format(behind)}
    except Exception as exc:  # noqa: BLE001 - a reconciler that raises takes the cadence down
        return {"status": ERROR, "behind": behind, "pushed": False,
                "detail": "{}: {}".format(type(exc).__name__, str(exc)[:300])}
    finally:
        (drop_worktree or _drop_worktree)(project, worktree)


def _run_merge(worktree: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "tools.surgical_land", "--merge",
         "{}/{}".format(REMOTE, BRANCH), "-m", _MERGE_MESSAGE],
        cwd=str(worktree), capture_output=True, text=True, timeout=MERGE_TIMEOUT_SECONDS,
        env=dict(os.environ, PYTHONPATH=str(PROJECT_DIR)))


def _push(worktree: Path) -> subprocess.CompletedProcess:
    return _git(worktree, "push", REMOTE, "HEAD:{}".format(BRANCH))


_MERGE_MESSAGE = (
    "merge origin/main: automatic reconciliation in an isolated worktree\n\n"
    "Closed by `background/origin_reconcile` on the deadman cadence, because a fork with origin "
    "blocks every landing AND the publish path -- and a document staged by the director is enough "
    "to open one.\n\n"
    "Done in a throwaway worktree with its own index, so the objection the publish path's own "
    "refusal raises (a daemon merging unattended would move other lanes' uncommitted work) cannot "
    "apply: the shared tree is never opened. Gated by `surgical_land --merge` like any other "
    "commit; a CONFLICT still refuses, because resolving two lanes' edits to one file is a "
    "judgement and not a cadence.\n"
)


def main(argv=None) -> int:
    import argparse
    import json
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check", action="store_true", help="report the fork, reconcile nothing")
    args = ap.parse_args(argv)
    # THE SUBJECT IS THE SHARED TREE, WHEREVER THIS WAS INVOKED FROM. Resolved once, here, and
    # passed down: every leg below takes `project` and each would otherwise inherit the importing
    # worktree. See `shared_tree` for the measurement that made this a defect rather than a tidy-up.
    subject = shared_tree()
    if subject is None:
        print("UNREADABLE: the main worktree could not be established from git, so no tree was "
              "reconciled -- this is refused rather than defaulted, because defaulting reconciles "
              "whichever tree this module was imported from")
        return 1
    if args.check:
        behind = commits_behind(subject)
        print(json.dumps({"behind": behind, "subject": str(subject)}))
        return 1 if behind else 0
    result = reconcile(subject)
    print(json.dumps(result, indent=2) if args.json
          else "{}: {}".format(result["status"], result["detail"]))
    return 0 if result["status"] in (LEVEL, RECONCILED, PUSHED) else 1


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/origin_reconcile.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("origin_reconcile")
    sys.exit(main())
