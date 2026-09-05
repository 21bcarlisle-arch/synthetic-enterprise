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
    incoming = _paths(project, "diff", "--name-only", "-z", "HEAD",
                      "{}/{}".format(REMOTE, BRANCH))
    modified = _paths(project, "diff", "--name-only", "-z", "HEAD")
    untracked = _paths(project, "ls-files", "--others", "--exclude-standard", "-z")
    if incoming is None or modified is None or untracked is None:
        return None
    arriving = set(incoming)
    blocking = [{"path": p, "kind": FF_MODIFIED} for p in sorted(arriving.intersection(modified))]
    blocking += [{"path": p, "kind": FF_UNTRACKED} for p in sorted(arriving.intersection(untracked))]
    return blocking


def _blocking_clause(blocking: list[dict] | None) -> str:
    """The named cause, rendered ahead of git's own words rather than after them."""
    if blocking is None:
        return ("The paths refusing the advance could NOT be established, so this names the fork "
                "and not its cause.")
    if not blocking:
        return ("NOTHING local collides with what origin brings, so the refusal is not a "
                "dirty-tree collision and git's own words are the whole of the cause.")
    listed = blocking[:12]
    dropped = len(blocking) - len(listed)
    return "Refused by {} path(s): {}{}.".format(
        len(blocking),
        "; ".join("{} ({})".format(b["path"], b["kind"]) for b in listed),
        " -- and {} further path(s) not listed here".format(dropped) if dropped else "")


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


def advance_shared_tree(project: Path | None = None, *, blockers_fn=None, twins_fn=None,
                        tracked_twins_fn=None, ff_fn=None, remover=None, restorer=None,
                        locker=None, ahead_fn=None) -> dict:
    """Fast-forward the shared tree onto `origin/main`, clearing byte-identical twins of BOTH kinds.

    Returns `{"advanced": bool, "cleared": list[str], "reason": str}`. `advanced` is claimed only
    when git itself reported the fast-forward, never inferred from the absence of an error.

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
    (`unlink` for untracked, `restore_tracked_twin` for tracked), and the length comparison is over
    the union, so one genuinely dirty path still refuses everything -- which is what
    `background/process_run_complete.py`, the fifth path, correctly did.

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
    if len(resolvable) != len(blocking):
        held = [b["path"] for b in blocking if b["path"] not in set(resolvable)]
        return {"advanced": False, "cleared": [],
                "reason": "{} of {} blocking path(s) are NOT byte-identical to what origin brings, "
                          "so clearing the {} that are would delete files and still not advance. "
                          "Nothing was removed. Held by: {}".format(
                              len(held), len(blocking), len(resolvable), "; ".join(held[:12]))}

    try:
        from background.tree_lock import TreeLockTimeout, tree_lock
    except ImportError as exc:
        return {"advanced": False, "cleared": [],
                "reason": "the tree lock could not be imported ({}), and the shared tree is never "
                          "written without it".format(exc)}
    _remove = remover or (lambda p: (project / p).unlink())
    _restore = restorer or (lambda p: restore_tracked_twin(project, p))
    _lock = locker or (lambda: tree_lock(timeout=ADVANCE_LOCK_TIMEOUT_SECONDS))
    tracked_set = set(tracked)
    try:
        with _lock():
            cleared = []
            for path in resolvable:
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
                "reason": "cleared {} path(s) whose bytes origin already held at the same path "
                          "({} tracked, {} untracked), then fast-forwarded -- every one is back on "
                          "disk, tracked, with identical content: {}".format(
                              len(cleared), len(tracked_set), len(cleared) - len(tracked_set),
                              "; ".join(cleared[:12]))}
    # THE TWINS ARE NOT RESTORED HERE, AND THAT IS DELIBERATE. Their content is on origin by the
    # hash equality that selected them, so `git checkout origin/main -- <path>` returns any of them
    # exactly; re-writing them from a second guess at what they held would be this module inventing
    # bytes. The reason names them so the next reader has the command's arguments already.
    return {"advanced": False, "cleared": cleared,
            "reason": "removed {} byte-identical twin(s) and git STILL refused the fast-forward, "
                      "which means the cause was not the collision this cleared. Recover any of "
                      "them with `git checkout {}/{} -- <path>`: {}. git: {}".format(
                          len(cleared), REMOTE, BRANCH, "; ".join(cleared[:12]),
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
        return {"status": NOT_ADVANCED, "behind": behind, "pushed": False,
                "blocking_paths": blocking, "cleared_paths": adv["cleared"],
                "detail": "origin is {} commit(s) ahead, this machine has NOTHING to land, and the "
                          "shared tree will not fast-forward. {} Nothing was committed and "
                          "nothing was pushed -- a merge with no work of ours in it would only "
                          "widen the fork it claims to close. The tree advances when the lane "
                          "holding those paths lands or reverts them. advance: {}".format(
                              behind, _blocking_clause(blocking), adv["reason"])}

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
        still_behind, _ = (state_fn or fork_state)(project)
        if still_behind:
            blocking = (blockers_fn or paths_blocking_fast_forward)(project)
            return {"status": NOT_ADVANCED, "behind": still_behind, "pushed": True,
                    "blocking_paths": blocking, "cleared_paths": adv["cleared"],
                    "detail": "the merge gated clean and was pushed, but the shared tree did NOT "
                              "advance and is still {} commit(s) behind. {} This is NOT a closed "
                              "fork -- origin moved and this tree did not, which is precisely the "
                              "state that loops if it is retried on a cadence. advance: {}".format(
                                  still_behind, _blocking_clause(blocking), adv["reason"])}
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
    if args.check:
        behind = commits_behind()
        print(json.dumps({"behind": behind}))
        return 1 if behind else 0
    result = reconcile()
    print(json.dumps(result, indent=2) if args.json
          else "{}: {}".format(result["status"], result["detail"]))
    return 0 if result["status"] in (LEVEL, RECONCILED, PUSHED) else 1


if __name__ == "__main__":
    sys.exit(main())
