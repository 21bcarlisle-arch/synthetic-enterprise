"""Cross-process working-tree lock -- serializes concurrent git writers.

Rich's directive (2026-07-05): multiple independent processes write to this
same git working tree concurrently -- process_run_complete.py (triggered by
both sim_runner.py and background_worker.py), the interactive Claude Code
session, and autonomous_runner.py's spawned `claude -p` turns. Without
serialization, a `git add`+`git commit` sequence from one process can
interleave with another's, sweeping unrelated staged changes into the wrong
commit (observed directly this session: a manually-staged code change got
committed under an unrelated "Auto-process run complete" message because a
concurrent process's `git commit` ran between this session's `git add` and
`git commit`).

Uses `fcntl.flock` on a well-known lock file: blocking, cross-process, and
automatically released if the holding process dies or crashes (unlike a
lock implemented as a plain file's existence, which would need manual
cleanup after a crash).

Python usage:
    from background.tree_lock import tree_lock
    with tree_lock():
        subprocess.run(["git", "add", ...])
        subprocess.run(["git", "commit", "-m", ...])

Shell usage (interactive sessions, including this one, should wrap any
git add/commit/push sequence the same way):
    flock docs/observability/.tree.lock -c 'git add X && git commit -m "..."'
"""
from __future__ import annotations

import fcntl
import subprocess
import time
from contextlib import contextmanager
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
LOCK_FILE = PROJECT_DIR / "docs" / "observability" / ".tree.lock"

DEFAULT_TIMEOUT_SECONDS = 60.0
POLL_INTERVAL_SECONDS = 0.2

# Name of the cross-worktree shared lock file, anchored in the SHARED git
# object store (git-common-dir), so every worktree resolves to the SAME path.
SHARED_LOCK_NAME = ".tree-shared.lock"

# Paths a BUILD fork may NEVER write, regardless of its declared file_scope.
# The maturity map is the single source of truth for the draw and is
# orchestrator-/integrator-written ONLY (H9/H10 sole-writer doctrine, THREE
# LANES Lane 1). A fork that touches it -- even one that mis-declares it in its
# own file_scope -- is a corruption of shared state and must be caught.
PROTECTED_PATHS = ("docs/design/maturity_map.yaml",)


class TreeLockTimeout(Exception):
    """Raised when the lock could not be acquired within the timeout."""


class GitStateError(Exception):
    """Raised when git working-tree state cannot be determined. This is a
    FAIL-CLOSED signal: an isolation guard that cannot read the changed-file
    set must NOT report the tree as safe (R15 fail-silent doctrine -- an
    unavailable check is a FAILED check)."""


class ScopeViolation(Exception):
    """Raised when a worktree's changed files fall outside its declared
    file_scope, or touch a globally protected path. This is the H10
    worktree-isolation guard firing: a BUILD fork corrupting files outside
    its atom's scope (a sibling atom's files, or the shared map) is exactly
    the failure worktree isolation exists to contain, and this exception is
    the mechanism (not the convention) that catches it."""

    def __init__(self, scope_violations, protected_violations):
        self.scope_violations = sorted(scope_violations)
        self.protected_violations = sorted(protected_violations)
        parts = []
        if self.protected_violations:
            parts.append(
                "changed PROTECTED paths (never fork-writable): "
                + ", ".join(self.protected_violations)
            )
        if self.scope_violations:
            parts.append(
                "changed paths OUTSIDE declared file_scope: "
                + ", ".join(self.scope_violations)
            )
        super().__init__("; ".join(parts) or "scope violation")


def _acquire_flock(lock_path: Path, timeout: float):
    """Open `lock_path` and block (polling) until an exclusive flock is held or
    `timeout` elapses. Returns the open file handle (caller unlocks/closes)."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fh = open(lock_path, "w")
    deadline = time.monotonic() + timeout
    while True:
        try:
            fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return fh
        except BlockingIOError:
            if time.monotonic() >= deadline:
                fh.close()
                raise TreeLockTimeout(
                    f"Could not acquire tree lock ({lock_path}) within {timeout}s"
                )
            time.sleep(POLL_INTERVAL_SECONDS)


@contextmanager
def tree_lock(timeout: float = DEFAULT_TIMEOUT_SECONDS):
    """Hold an exclusive lock on THIS working tree for the duration of the
    `with` block. Blocks (polling) until acquired or `timeout` elapses.

    Scope note (H10): `LOCK_FILE` resolves via `__file__` to the CURRENT
    working tree's `docs/observability/.tree.lock`. That is correct and
    sufficient for serialising the multiple writers that share ONE tree
    (process_run_complete, the interactive session, autonomous_runner turns).
    It deliberately does NOT serialise across git worktrees -- an isolated
    BUILD fork commits to its OWN branch in its OWN index, so it needs no
    mutual exclusion with a sibling worktree. For the rare operation that
    touches SHARED git state (refs, the main tree, the map) from within a
    worktree, use `shared_tree_lock()` instead.

    Raises TreeLockTimeout on timeout rather than blocking forever, so a
    genuinely stuck holder (rather than just a slow one) surfaces as a
    visible error instead of hanging every other writer indefinitely.
    """
    fh = _acquire_flock(LOCK_FILE, timeout)
    try:
        yield
    finally:
        fcntl.flock(fh, fcntl.LOCK_UN)
        fh.close()


def common_git_dir(repo_dir: Path | None = None) -> Path:
    """Resolve the SHARED git directory (git-common-dir) -- the single
    `.git` object store shared by the main tree and every worktree. From a
    linked worktree, `--git-dir` points at `.git/worktrees/<name>` (per-tree),
    but `--git-common-dir` points at the one shared `.git`, so a lock anchored
    here is visible identically from every worktree. Falls back to
    `<repo>/.git` if git cannot be queried."""
    base = Path(repo_dir) if repo_dir is not None else PROJECT_DIR
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            cwd=str(base),
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return base / ".git"
    p = Path(out)
    return p if p.is_absolute() else (base / p).resolve()


def shared_lock_file(repo_dir: Path | None = None) -> Path:
    """Path to the cross-worktree shared lock (identical from every worktree)."""
    return common_git_dir(repo_dir) / SHARED_LOCK_NAME


@contextmanager
def shared_tree_lock(timeout: float = DEFAULT_TIMEOUT_SECONDS, repo_dir: Path | None = None):
    """Cross-worktree exclusive lock, anchored in the shared git-common-dir so
    ALL worktrees (and the main tree) serialise on the SAME lock file. Use for
    operations that touch shared git state (ref updates that must not race, an
    integrator merging fork branches, any write to the main tree from a fork).
    This is the composition primitive `tree_lock()` deliberately is not: two
    different worktrees calling `tree_lock()` do NOT exclude each other; two
    calling `shared_tree_lock()` do."""
    fh = _acquire_flock(shared_lock_file(repo_dir), timeout)
    try:
        yield
    finally:
        fcntl.flock(fh, fcntl.LOCK_UN)
        fh.close()


def _norm(path: str) -> str:
    return path.strip().strip("/")


def changed_paths(repo_dir: Path | None = None) -> set[str]:
    """Repo-relative paths of every changed file in `repo_dir` (staged,
    unstaged, and untracked), as reported by `git status --porcelain`. Renames
    contribute BOTH the old and new path (both are 'touched'). Fail-closed:
    raises GitStateError if git cannot be run or reports an error, so a guard
    built on this can never silently pass on an undeterminable tree."""
    base = Path(repo_dir) if repo_dir is not None else PROJECT_DIR
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=str(base),
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:  # git not installed / not on PATH
        raise GitStateError(f"git unavailable in {base}: {exc}") from exc
    if proc.returncode != 0:
        raise GitStateError(
            f"git status failed in {base} (rc={proc.returncode}): {proc.stderr.strip()}"
        )
    out: set[str] = set()
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        # Porcelain v1: "XY <path>" or "XY <orig> -> <new>" for renames/copies.
        body = line[3:] if len(line) > 3 else line
        for part in body.split(" -> "):
            part = part.strip()
            if part.startswith('"') and part.endswith('"') and len(part) >= 2:
                part = part[1:-1]  # git quotes paths with special chars
            if part:
                out.add(_norm(part))
    return out


def _within_scope(path: str, file_scope) -> bool:
    """True if `path` is at or below any entry in `file_scope`. A scope entry
    may be an exact file (`background/tree_lock.py`) or a directory prefix
    (`tests`); a directory entry matches the dir itself and anything below it,
    but NOT a sibling that merely shares a name-prefix (`tests` must not match
    `tests_extra/...`)."""
    p = _norm(path)
    for entry in file_scope:
        e = _norm(entry)
        if not e:
            continue
        if p == e or p.startswith(e + "/"):
            return True
    return False


def scope_violations(paths, file_scope) -> list[str]:
    """Paths not covered by any file_scope entry."""
    return [p for p in paths if not _within_scope(p, file_scope)]


def assert_changes_within_scope(
    file_scope,
    repo_dir: Path | None = None,
    protected=PROTECTED_PATHS,
) -> set[str]:
    """H10 worktree-isolation guard. Assert that EVERY changed file in
    `repo_dir` lies within `file_scope` and that NONE touches a globally
    protected path. Returns the set of changed paths on success; raises
    ScopeViolation otherwise.

    A BUILD fork should call this immediately before committing, so a
    mis-scoped edit (a sibling atom's file, or the shared map) is caught by a
    mechanism rather than trusted to convention. Fail-closed by construction:
      * an empty `file_scope` makes EVERY change a violation (you cannot
        declare no scope and change something);
      * a protected-path change is a violation even if `file_scope` wrongly
        includes it (sole-writer protection is independent of declared scope);
      * `changed_paths` raises GitStateError (propagated) if the tree state
        cannot be read -- an unverifiable tree is never reported clean.
    A genuinely clean tree (no changes) passes: there is nothing to violate."""
    changed = changed_paths(repo_dir)
    prot = [p for p in changed if _norm(p) in {_norm(x) for x in protected}]
    scope_v = scope_violations(changed, file_scope)
    # A protected path is a violation regardless of scope; do not double-excuse
    # it just because it also appears within a mis-declared scope.
    if prot or scope_v:
        raise ScopeViolation(scope_violations=set(scope_v), protected_violations=set(prot))
    return changed
