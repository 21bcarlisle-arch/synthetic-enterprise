"""Get a worktree's GATED landing onto `origin/main`, or refuse with a named cause.

`tools/surgical_land` works from a `git worktree` since 2026-08-31 (`178bf5a56`) — and the probe
that proved it also showed something the design had not predicted: **a worktree land commits to the
worktree's own DETACHED HEAD, and `main` is untouched.** That is the good kind of isolation. It also
means integration is a second, separate step, and until now that step was a hand-rolled sequence of
git commands.

WHY IT HAS TO BE A TOOL AND NOT A HABIT. It has been run by hand twice, correctly, and hand-rolled
git on a shared tree is exactly where `git stash` nearly swallowed another lane's parked work on the
morning of 2026-08-31. An unattended writer running a remembered sequence is that near-miss with
nobody watching.

THE FOUR REFUSALS, and each is a way the hand-rolled version could go wrong:

  * **not gated** — the commit must carry a `surgical_land` receipt and `--verify` must pass. This
    is the load-bearing one: it makes "only gated commits reach `main`" a property of the route
    rather than of the caller's discipline. A commit made any other way cannot be promoted here.
  * **not a fast-forward** — `origin/main` moved under the landing. Refuse; the caller re-gates on
    the new base, which is what `surgical_land --attempts` already does one layer down. Never
    `--force`, ever: the whole point is that a second writer cannot overwrite the first.
  * **dirty worktree** — uncommitted work in the worktree means the landing is not the whole of
    what the writer did, and promoting it would publish half a change.
  * **duplicated work** — another live claim holds paths this landing moves. See
    `seat_work_in_hand.refuse_if_duplicated`.

WHAT IT NEVER TOUCHES: the shared working tree. It pushes from the worktree to the remote and
stops. Whoever owns the shared tree fast-forwards on their own schedule, or does not; either way
this cannot write there, which is the property that makes it safe to run unattended.

Usage:
    python3 -m tools.promote_worktree_landing <worktree-path> [--dry-run]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT))

REMOTE = "origin"
BRANCH = "main"


class PromotionRefused(RuntimeError):
    """The landing may not be promoted. The message always names which condition failed."""


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True, timeout=300,
    )


def _git_out(cwd: Path, *args: str) -> str:
    r = _git(cwd, *args)
    if r.returncode != 0:
        raise PromotionRefused(
            f"git {' '.join(args)} failed rc={r.returncode}: {r.stderr.strip()[-300:]}"
        )
    return r.stdout.strip()


def landed_commit(worktree: Path) -> str:
    """The worktree's HEAD — the commit being promoted."""
    return _git_out(worktree, "rev-parse", "HEAD")


def _refuse_if_dirty(worktree: Path) -> None:
    """Tracked changes only. Untracked files are the machine's data overlay and are not a landing.

    A dirty tracked file means the writer left work uncommitted, so the commit being promoted is
    not the whole of what it did — and promoting half a change is the wedge shape in miniature.
    """
    dirty = _git_out(worktree, "status", "--porcelain", "--untracked-files=no")
    if dirty:
        raise PromotionRefused(
            "the worktree has uncommitted tracked changes, so this landing is not the whole of "
            f"what was done:\n{dirty[:600]}"
        )


def _refuse_if_ungated(worktree: Path, commit: str) -> None:
    """The commit must carry a `surgical_land` receipt that verifies.

    THIS IS THE ONE THAT MATTERS. Everything else here is hygiene; this is what makes "only gated
    commits reach `main`" a property of the ROUTE. A commit made with a hand-rolled `git commit`,
    or with `--no-verify`, has no receipt and cannot be promoted — so the wall is enforced at the
    place work leaves the machine rather than trusted at the place it was made.
    """
    proc = subprocess.run(
        [sys.executable, "-m", "tools.surgical_land", "--verify", commit],
        cwd=str(worktree), capture_output=True, text=True, timeout=300,
    )
    if proc.returncode != 0:
        raise PromotionRefused(
            f"{commit[:9]} carries no verifying surgical_land receipt, so it was not gated:\n"
            f"{(proc.stdout + proc.stderr).strip()[-400:]}\n"
            "Only gated commits are promotable. Re-land it through the door."
        )


def _refuse_if_not_fast_forward(worktree: Path, commit: str) -> str:
    """`origin/main` must be an ancestor of the landing. Never force, ever.

    A landing built on a base the remote has moved past would, if forced, silently drop whatever
    moved. Refusing sends the caller back to re-gate on the new base — which is what
    `surgical_land --attempts` already does one layer down, and the same answer for the same
    reason.
    """
    _git_out(worktree, "fetch", "--quiet", REMOTE)
    remote_head = _git_out(worktree, "rev-parse", f"{REMOTE}/{BRANCH}")
    if remote_head == commit:
        raise PromotionRefused(
            f"{REMOTE}/{BRANCH} is already at {commit[:9]}: there is nothing to promote."
        )
    ancestor = _git(worktree, "merge-base", "--is-ancestor", remote_head, commit)
    if ancestor.returncode != 0:
        behind = _git_out(worktree, "rev-list", "--count", f"{commit}..{remote_head}")
        raise PromotionRefused(
            f"{REMOTE}/{BRANCH} has moved to {remote_head[:9]} — {behind} commit(s) this landing "
            "does not contain, so promoting it is not a fast-forward. Re-gate on the new base and "
            "land again. This route never forces."
        )
    return remote_head


def _refuse_if_duplicated(worktree: Path, commit: str, *, work_id: str | None) -> list[str]:
    """No other live claim may hold the paths this landing moves.

    The paths are read from the COMMIT rather than taken from the caller, so a writer cannot
    under-declare its scope to slip past the check.
    """
    from background.seat_work_in_hand import refuse_if_duplicated

    paths = [p for p in _git_out(
        worktree, "show", "--pretty=format:", "--name-only", commit
    ).splitlines() if p.strip()]
    refuse_if_duplicated(paths, exclude=work_id)
    return paths


def promote(worktree: Path, *, work_id: str | None = None, dry_run: bool = False) -> dict:
    """Run every refusal, then push. Returns what happened.

    ORDER IS CHEAPEST-AND-MOST-LOCAL FIRST: a dirty tree and a missing receipt are answerable
    without touching the network, so a writer that is going to be refused finds out before a fetch.
    """
    worktree = worktree.resolve()
    if not (worktree / ".git").exists():
        raise PromotionRefused(f"{worktree} is not a git worktree")

    commit = landed_commit(worktree)
    # ALREADY-THERE FIRST, and against the LOCAL remote ref so it costs no network. A worktree
    # sitting on `origin/main` has nothing to promote, and saying so is clearer than any of the
    # refusals below — the exercise that built this tool hit the ungated message instead and it
    # read as a defect in the commit rather than as "there is no work here".
    local_remote = _git(worktree, "rev-parse", f"{REMOTE}/{BRANCH}")
    if local_remote.returncode == 0 and local_remote.stdout.strip() == commit:
        raise PromotionRefused(
            f"the worktree is at {REMOTE}/{BRANCH} ({commit[:9]}) and has landed nothing: "
            "there is no work here to promote."
        )
    _refuse_if_dirty(worktree)
    _refuse_if_ungated(worktree, commit)
    paths = _refuse_if_duplicated(worktree, commit, work_id=work_id)
    remote_head = _refuse_if_not_fast_forward(worktree, commit)

    if dry_run:
        return {"commit": commit, "would_push": True, "paths": paths,
                "from": remote_head, "pushed": False}

    _git_out(worktree, "push", REMOTE, f"HEAD:{BRANCH}")
    now = _git_out(worktree, "rev-parse", f"{REMOTE}/{BRANCH}")
    if now != commit:
        raise PromotionRefused(
            f"push reported success but {REMOTE}/{BRANCH} is {now[:9]}, not {commit[:9]}. "
            "Verified rather than assumed — 'in the tree' and 'on origin' are different claims."
        )
    return {"commit": commit, "paths": paths, "from": remote_head, "pushed": True}


def main(argv=None) -> int:  # pragma: no cover - operator surface
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("worktree", help="path to the worktree holding the gated landing")
    ap.add_argument("--work-id", default=None,
                    help="this writer's own claim id, so its own claim is not read as a clash")
    ap.add_argument("--dry-run", action="store_true", help="run every refusal, push nothing")
    args = ap.parse_args(argv)
    try:
        result = promote(Path(args.worktree), work_id=args.work_id, dry_run=args.dry_run)
    except PromotionRefused as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    verb = "would promote" if args.dry_run else "promoted"
    print(f"{verb} {result['commit'][:9]} -> {REMOTE}/{BRANCH} "
          f"({len(result['paths'])} path(s), from {result['from'][:9]})")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
