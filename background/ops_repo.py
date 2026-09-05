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

THE REFUSAL IS HERE, AT THE CHOKE POINT, AND UNTIL 2026-09-05 IT WAS NOT.
Three callers converged onto `commit_and_push`. Two of them -- `ntfy_mirror.py`
and `director_input_log.py` -- hand-rolled the SAME refusal at their own call
site (`os.environ.get("PYTEST_CURRENT_TEST") is not None`, a silent no-op).
`backup_company_data.py` never had one: `backup_once()` reaches this function
with nothing between a test process and `git push origin main` on the private
repo, and it escaped only because its four tests all happen to patch
`commit_and_push` by name. That is discipline at every call site, which is what
R10 says a class fix replaces -- and the class was open for the caller nobody
remembered.

So the refusal moved to the write, exactly as `background/live_ledger_guard.py`
argues for the observability ledgers, and it CALLS that module's
`in_test_process()` rather than copying the callers' spelling. The hand-rolled
copies are strictly weaker: `PYTEST_CURRENT_TEST` is unset during collection
and at module import, so a push at import time walks past both of them.
`in_test_process()` ORs that signal with `"pytest" in sys.modules` and fails
closed. There is deliberately no env-var override -- that is a fail-open door
set by exactly the process that must not have it.

`live_ledger_guard` itself cannot cover this: its subject is derived as "any
path under <PROJECT_DIR>/docs/observability", and OPS_REPO_DIR is a different
repository outside the project directory entirely. The primitive is shared; the
subject is not.
"""
from __future__ import annotations

import fcntl
import subprocess
import time
from contextlib import contextmanager
from pathlib import Path

from background.live_ledger_guard import in_test_process

OPS_REPO_DIR = Path.home() / "synthetic-enterprise-ops"
_LOCK_FILE = OPS_REPO_DIR / ".ops.lock"

DEFAULT_TIMEOUT_SECONDS = 60.0
POLL_INTERVAL_SECONDS = 0.2


class OpsLockTimeout(Exception):
    pass


class OpsRepoWriteUnderTest(RuntimeError):
    """A test process tried to commit and push to the private ops repo.

    Its own type, for the same reason `LiveLedgerWriteUnderTest` has one: a
    caller that wraps this fail-safe can still tell "the harness stopped me
    publishing to the real repo" apart from "the write itself broke"."""


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
    a caller doing multiple related writes can batch them under one lock.

    REFUSES under a test process -- see the module docstring. This is the first
    statement in the function on purpose: a refusal placed after the `git add`
    would already have staged a test's bytes in the real repo."""
    if in_test_process():
        raise OpsRepoWriteUnderTest(
            f"commit_and_push refused: this is a test process and {OPS_REPO_DIR} "
            "is the REAL private ops repo, which this would commit and push to "
            "origin/main. Patch `commit_and_push` in the module under test, or "
            "point OPS_REPO_DIR at a tmp_path clone. There is no env-var "
            f"override by design. (refused paths: {relpaths}, message: {message!r})"
        )
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
