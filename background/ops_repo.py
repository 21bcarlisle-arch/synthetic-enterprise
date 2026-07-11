"""Shared helpers for writing to the PRIVATE synthetic-enterprise-ops repo.

docs/staging/in_progress/DIRECTOR_INPUT_LOG.md's PRIVACY AMENDMENT
(2026-07-11): message-traffic mirrors (the ntfy mirror, the new director
input log) relocate to a separate private repo, cloned locally at
OPS_REPO_DIR, rather than committed into this (public) repo. Push access
confirmed live via `gh api repos/21bcarlisle-arch/synthetic-enterprise-ops`
(admin+push, 2026-07-11) before this module was written.

Not the same lock as background/tree_lock.py -- that lock protects THIS
repo's working tree; writes here touch a different repo/directory entirely,
so a separate lock file (scoped to the ops checkout itself) is correct, not
redundant.
"""
from __future__ import annotations

import fcntl
import subprocess
import time
from contextlib import contextmanager
from pathlib import Path

OPS_REPO_DIR = Path.home() / "synthetic-enterprise-ops"
_LOCK_FILE = OPS_REPO_DIR / ".ops.lock"

DEFAULT_TIMEOUT_SECONDS = 60.0
POLL_INTERVAL_SECONDS = 0.2


class OpsLockTimeout(Exception):
    pass


@contextmanager
def ops_tree_lock(timeout: float = DEFAULT_TIMEOUT_SECONDS):
    OPS_REPO_DIR.mkdir(parents=True, exist_ok=True)
    fh = open(_LOCK_FILE, "w")
    deadline = time.monotonic() + timeout
    try:
        while True:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise OpsLockTimeout(
                        f"Could not acquire ops-repo lock ({_LOCK_FILE}) within {timeout}s"
                    )
                time.sleep(POLL_INTERVAL_SECONDS)
        yield
    finally:
        fcntl.flock(fh, fcntl.LOCK_UN)
        fh.close()


def commit_and_push(relpaths: list[str], message: str) -> None:
    """Stage `relpaths` (relative to OPS_REPO_DIR), commit, and push to
    origin/main. No-ops cleanly if there's nothing to commit (repeated
    identical writes, e.g. in tests that don't mutate content). Caller must
    hold ops_tree_lock() -- this function does not acquire it itself, so
    a caller doing multiple related writes can batch them under one lock."""
    subprocess.run(
        ["git", "-C", str(OPS_REPO_DIR), "add", *relpaths], check=True,
    )
    result = subprocess.run(
        ["git", "-C", str(OPS_REPO_DIR), "commit", "-m", message],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        if "nothing to commit" in result.stdout or "nothing to commit" in result.stderr:
            return
        raise RuntimeError(
            f"ops repo commit failed: stdout={result.stdout!r} stderr={result.stderr!r}"
        )
    subprocess.run(
        ["git", "-C", str(OPS_REPO_DIR), "push", "origin", "main"], check=True,
    )
