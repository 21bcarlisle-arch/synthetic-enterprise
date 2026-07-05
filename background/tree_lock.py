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
import time
from contextlib import contextmanager
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
LOCK_FILE = PROJECT_DIR / "docs" / "observability" / ".tree.lock"

DEFAULT_TIMEOUT_SECONDS = 60.0
POLL_INTERVAL_SECONDS = 0.2


class TreeLockTimeout(Exception):
    """Raised when the lock could not be acquired within the timeout."""


@contextmanager
def tree_lock(timeout: float = DEFAULT_TIMEOUT_SECONDS):
    """Hold an exclusive lock on the working tree for the duration of the
    `with` block. Blocks (polling) until acquired or `timeout` elapses.

    Raises TreeLockTimeout on timeout rather than blocking forever, so a
    genuinely stuck holder (rather than just a slow one) surfaces as a
    visible error instead of hanging every other writer indefinitely.
    """
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    fh = open(LOCK_FILE, "w")
    deadline = time.monotonic() + timeout
    try:
        while True:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise TreeLockTimeout(
                        f"Could not acquire tree lock ({LOCK_FILE}) within {timeout}s"
                    )
                time.sleep(POLL_INTERVAL_SECONDS)
        yield
    finally:
        fcntl.flock(fh, fcntl.LOCK_UN)
        fh.close()
