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

LEVEL = "LEVEL"
RECONCILED = "RECONCILED"
PUSHED = "PUSHED"
FAST_FORWARDED = "FAST_FORWARDED"
NOT_ADVANCED = "NOT_ADVANCED"
GATE_RUNNING = "GATE_RUNNING"
REFUSED_CONFLICT = "REFUSED_CONFLICT"
REFUSED_GATE = "REFUSED_GATE"
UNREADABLE = "UNREADABLE"
ERROR = "ERROR"

#: The gate's own lock. `background/process_run_complete.py` holds it for the whole publish
#: pipeline -- report regeneration, the site build and a scoped suite, five to twenty-five minutes.
RUN_LOCK_FILE = PROJECT_DIR / "docs" / "observability" / ".process_run_complete.lock"


def _git(cwd: Path, *args: str, timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True,
                          timeout=timeout)


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
    """A worktree at local HEAD, owner-marked so nothing sweeps it mid-merge."""
    try:
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
              make_worktree=None, drop_worktree=None, gate_fn=None) -> dict:
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
            return {"status": ERROR, "behind": 0, "pushed": False,
                    "detail": "local is {} commit(s) ahead and the push was rejected: {}".format(
                        ahead, (pushed.stderr or pushed.stdout or "").strip()[:300])}
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
        ff = _git(project, "merge", "--ff-only", "{}/{}".format(REMOTE, BRANCH))
        if ff.returncode == 0:
            return {"status": FAST_FORWARDED, "behind": behind, "pushed": False,
                    "detail": "fast-forwarded {} commit(s) from origin; nothing of ours needed "
                              "landing, so no commit was made and origin was not touched".format(
                                  behind)}
        return {"status": NOT_ADVANCED, "behind": behind, "pushed": False,
                "detail": "origin is {} commit(s) ahead, this machine has NOTHING to land, and the "
                          "shared tree will not fast-forward: {}. Nothing was committed and "
                          "nothing was pushed -- a merge with no work of ours in it would only "
                          "widen the fork it claims to close. The tree advances when the lane "
                          "holding those files lands or reverts them.".format(
                              behind, (ff.stderr or ff.stdout or "").strip()[:200])}

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
            return {"status": ERROR, "behind": behind, "pushed": False,
                    "detail": "merge gated clean but the push was rejected: {}".format(
                        (pushed.stderr or pushed.stdout or "").strip()[:300])}

        ff = _git(project, "merge", "--ff-only", "{}/{}".format(REMOTE, BRANCH))

        # THE STATUS MUST DESCRIBE THE SUBJECT, NOT THE STEPS. The first version returned
        # RECONCILED whenever the merge and the push succeeded, and put "shared tree NOT advanced"
        # in the DETAIL, where nothing read it. So it reported success 29 times running while the
        # fork it was reconciling grew by one each time. A control that does not re-read its
        # subject after acting cannot tell "I fixed it" from "I did the steps".
        still_behind, _ = (state_fn or fork_state)(project)
        if still_behind:
            return {"status": NOT_ADVANCED, "behind": still_behind, "pushed": True,
                    "detail": "the merge gated clean and was pushed, but the shared tree did NOT "
                              "advance and is still {} commit(s) behind: {}. This is NOT a closed "
                              "fork -- origin moved and this tree did not, which is precisely the "
                              "state that loops if it is retried on a cadence.".format(
                                  still_behind, (ff.stderr or ff.stdout or "").strip()[:200])}
        return {"status": RECONCILED, "behind": behind, "pushed": True,
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
