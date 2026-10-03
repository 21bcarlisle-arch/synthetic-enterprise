"""Finished commits that exist only at a worktree's HEAD -- the work no ref will keep.

SPINE_1 and the monthly prospects existed for hours only at `/var/tmp/se-combo`'s detached HEAD.
They survived because the console seat remembered them. A detached HEAD is held by nothing but the
worktree's own `HEAD` file: reap the worktree and the commits go to the reflog of a directory that
no longer exists. Every other reading in the seat's brief describes the shared tree or origin, so
this population was invisible to all of them.

THE QUESTION IS "IS IT ON ANY REMOTE REF", not "is it on origin/main". A commit pushed to a
branch is kept by that branch whether or not it ever merges, so `rev-list HEAD --not --remotes`
asks exactly the loss question in one call and names every commit it answers for. A local branch
does NOT count as keeping it -- `git worktree remove` leaves the branch, but `git branch -D` from
any lane takes it, and a local branch is the place a fork's salvage commit lands and is forgotten.

FAIL CLOSED. A worktree git cannot read (moved, pruned, a corrupt `.git` file) is a row with
`state: "unknown"` and the reason, never an absent row: an empty list and a reading that failed
are the same shape and opposite in meaning. The whole census is `available: False` when the
worktree list itself cannot be read.

    python3 -m tools.unlanded_worktree_commits          # human list
    python3 -m tools.unlanded_worktree_commits --json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
OWNER_FILE = ".se_worktree_owner"
# Commits NAMED per worktree; the count is always exact. A worktree on an unrelated history would
# otherwise print thousands of rows into a brief that is read whole.
NAMED_PER_WORKTREE = 8


def _git(cwd: Path | str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(cwd), *args],
                          capture_output=True, text=True, timeout=60)


def parse_porcelain(text: str) -> list[dict]:
    """`git worktree list --porcelain` -> [{path, head, branch, locked, lock_reason, prunable}]."""
    rows, cur = [], None
    for line in text.splitlines():
        if line.startswith("worktree "):
            if cur:
                rows.append(cur)
            cur = {"path": line[len("worktree "):], "head": None, "branch": None,
                   "locked": False, "lock_reason": "", "prunable": False}
        elif cur is None:
            continue
        elif line.startswith("HEAD "):
            cur["head"] = line[len("HEAD "):].strip()
        elif line.startswith("branch "):
            cur["branch"] = line[len("branch "):].strip()
        elif line == "locked" or line.startswith("locked "):
            cur["locked"] = True
            cur["lock_reason"] = line[len("locked"):].strip()
        elif line == "prunable" or line.startswith("prunable "):
            cur["prunable"] = True
    if cur:
        rows.append(cur)
    return rows


def _owner(path: Path) -> str | None:
    try:
        return (path / OWNER_FILE).read_text().strip() or None
    except OSError:
        return None


def _assess(root: Path, wt: dict) -> dict:
    path = Path(wt["path"])
    row = {"path": wt["path"], "branch": wt["branch"], "locked": wt["locked"],
           "lock_reason": wt["lock_reason"], "owner": _owner(path), "head": wt["head"]}
    if wt["prunable"] or not path.is_dir():
        return {**row, "state": "unknown", "why": "worktree directory is missing (prunable)"}
    if not wt["head"]:
        return {**row, "state": "unknown", "why": "porcelain gave no HEAD"}
    # Asked of the SHARED repository, by sha: every worktree shares one object store, and asking
    # from inside a broken worktree would fail for the worktree's reason rather than the commit's.
    # `merge-base --is-ancestor HEAD origin/main` (the question `delivery_lane` and
    # `deploy_restart` ask) is the cheap common case, and rev-list below subsumes it.
    count = _git(root, "rev-list", "--count", wt["head"], "--not", "--remotes")
    if count.returncode != 0:
        return {**row, "state": "unknown",
                "why": "rev-list failed: {}".format((count.stderr or "").strip()[:200])}
    n = int(count.stdout.strip() or 0)
    if n == 0:
        return {**row, "state": "kept", "unlanded": 0, "commits": []}
    log = _git(root, "log", "--format=%H%x09%cI%x09%s", "-n", str(NAMED_PER_WORKTREE),
               wt["head"], "--not", "--remotes")
    if log.returncode != 0:
        return {**row, "state": "unknown",
                "why": "log failed: {}".format((log.stderr or "").strip()[:200])}
    commits = []
    for line in log.stdout.splitlines():
        sha, when, subject = (line.split("\t", 2) + ["", ""])[:3]
        commits.append({"sha": sha, "committed": when, "subject": subject})
    return {**row, "state": "at_risk", "unlanded": n, "commits": commits}


def census(root: Path | None = None) -> dict:
    root = Path(root or PROJECT_DIR)
    try:
        proc = _git(root, "worktree", "list", "--porcelain")
    except (OSError, subprocess.SubprocessError) as exc:
        return {"available": False, "why": repr(exc)}
    if proc.returncode != 0:
        return {"available": False,
                "why": "worktree list exited {}: {}".format(proc.returncode,
                                                            (proc.stderr or "").strip()[:200])}
    worktrees = parse_porcelain(proc.stdout)
    if not worktrees:
        return {"available": False, "why": "worktree list returned no worktrees at all"}
    rows = []
    for wt in worktrees:
        try:
            rows.append(_assess(root, wt))
        except (OSError, subprocess.SubprocessError, ValueError) as exc:
            rows.append({"path": wt["path"], "branch": wt["branch"], "locked": wt["locked"],
                         "lock_reason": wt["lock_reason"], "owner": None, "head": wt["head"],
                         "state": "unknown", "why": repr(exc)})
    return {"available": True, "worktrees": len(rows),
            "at_risk": [r for r in rows if r["state"] == "at_risk"],
            "unknown": [r for r in rows if r["state"] == "unknown"]}


def render(c: dict) -> str:
    if not c.get("available"):
        return ("UNLANDED WORKTREE COMMITS COULD NOT BE READ ({}) -- so 'none at risk' is NOT "
                "what this says.".format(c.get("why", "unknown")))
    lines = []
    for r in c["at_risk"]:
        lines.append("  {}  {} commit(s) on no remote ref  {}  owner={}  {}".format(
            r["path"], r["unlanded"],
            "locked({})".format(r["lock_reason"] or "no reason") if r["locked"] else "UNLOCKED",
            r["owner"] or "undeclared", r["branch"] or "detached"))
        for cm in r["commits"]:
            lines.append("      {}  {}  {}".format(cm["sha"][:12], cm["committed"][:16],
                                                    cm["subject"][:100]))
        if r["unlanded"] > len(r["commits"]):
            lines.append("      ... and {} more".format(r["unlanded"] - len(r["commits"])))
    for r in c["unknown"]:
        lines.append("  {}  UNKNOWN -- {}".format(r["path"], r["why"]))
    if not lines:
        return ("NO WORKTREE HOLDS A COMMIT THAT NO REMOTE REF KEEPS. Positively measured: all {} "
                "worktrees read, every HEAD is reachable from a remote ref.".format(c["worktrees"]))
    return ("{} OF {} WORKTREES HOLD COMMITS THAT NO REMOTE REF KEEPS{}. Reaping one of these "
            "worktrees, or deleting its local branch, loses that work; land it or say in the "
            "record that it is disposable:\n\n".format(
                len(c["at_risk"]), c["worktrees"],
                " ({} more could not be read)".format(len(c["unknown"])) if c["unknown"] else "")
            + "\n".join(lines))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    c = census()
    print(json.dumps(c, indent=2) if args.json else render(c))
    return 0 if c.get("available") else 2


if __name__ == "__main__":
    sys.exit(main())
