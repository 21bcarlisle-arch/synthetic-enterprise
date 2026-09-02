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
advance is REPORTED, never forced, and the fork stays closed on origin either way.
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
REFUSED_CONFLICT = "REFUSED_CONFLICT"
REFUSED_GATE = "REFUSED_GATE"
UNREADABLE = "UNREADABLE"
ERROR = "ERROR"


def _git(cwd: Path, *args: str, timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True,
                          timeout=timeout)


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


def reconcile(project: Path | None = None, *, worktree: Path | None = None,
              behind_fn=None, runner=None, pusher=None,
              make_worktree=None, drop_worktree=None) -> dict:
    """Close the fork with origin, or say exactly why it stayed open. Never raises.

    Returns {"status", "detail", "behind", "pushed"}. Fully injectable, because every one of its
    real steps is destructive-adjacent and none of them belongs in a test.
    """
    project = project or PROJECT_DIR
    worktree = worktree or WORKTREE
    behind = (behind_fn or commits_behind)(project)

    if behind is None:
        return {"status": UNREADABLE, "behind": None, "pushed": False,
                "detail": "origin is unreadable, so whether a fork exists cannot be established -- "
                          "not acting on a state that was not observed"}
    if behind == 0:
        return {"status": LEVEL, "behind": 0, "pushed": False,
                "detail": "origin/main is not ahead; nothing to reconcile"}

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
        shared = ("shared tree fast-forwarded" if ff.returncode == 0 else
                  "shared tree NOT advanced (git refused, which is the safety net rather than a "
                  "failure): {}".format((ff.stderr or ff.stdout or "").strip()[:200]))
        return {"status": RECONCILED, "behind": behind, "pushed": True,
                "detail": "merged {} commit(s) from origin in an isolated worktree, gated, and "
                          "pushed; {}".format(behind, shared)}
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
    return 0 if result["status"] in (LEVEL, RECONCILED) else 1


if __name__ == "__main__":
    sys.exit(main())
