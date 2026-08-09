"""Booted-SHA stamping (OPS1 sub-step 5 — deployment-by-construction, G-D1/G-D3).

docs/design/OPERATIONAL_LAYER_DESIGN.md §2.2. Each systemd daemon stamps the git HEAD it BOOTED
from (as its unit's ExecStartPre); the reconciler compares the stamp against current HEAD, so a
daemon running STALE code is flagged by construction. This GENERALISES the prior stale-detection
(health_check.stale_daemon_sessions was mtime-of-the-daemon's-OWN-top-level-script only): a boot
SHA older than HEAD means stale no matter WHICH file changed — including an imported module the
daemon depends on, the gap the mtime check silently missed.

The stamp is written by the systemd unit (declared in generate_units.py, committed IaC) — NO
daemon source is touched. The boot record is runtime state (gitignored, like a pidfile); the
MECHANISM (stamper + unit ExecStartPre + reconcile) is committed.
"""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
BOOT_DIR = _REPO / "docs" / "observability" / ".daemon_boot"


def current_head() -> str | None:
    """The repo's current HEAD SHA, or None if git is unavailable (never raises)."""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO, text=True, timeout=5
        ).strip() or None
    except Exception:
        return None


def stamp(session: str) -> None:
    """Record the HEAD this daemon booted from. Runs as the unit's ExecStartPre (prefixed `-`
    there, so a stamp failure never blocks the daemon). Never raises."""
    sha = current_head()
    try:
        BOOT_DIR.mkdir(parents=True, exist_ok=True)
        (BOOT_DIR / f"{session}.json").write_text(
            json.dumps({"session": session, "sha": sha, "ts": time.time()})
        )
    except Exception:
        pass


def read_boot_sha(session: str) -> str | None:
    """The SHA a daemon booted from (last stamp), or None if never stamped/unreadable."""
    try:
        return json.loads((BOOT_DIR / f"{session}.json").read_text()).get("sha")
    except Exception:
        return None


def changed_paths_since(sha: str) -> set[str] | None:
    """Repo-relative paths that differ between `sha` and the CURRENT WORKING TREE, or None if
    the SHA is unknown to git / git is unavailable.

    Working tree, not HEAD: a daemon loads files off the disk it booted from, so an UNCOMMITTED
    edit to a module it imports is genuinely code the daemon does not have — that is exactly the
    caller/callee split (`sim_runner.py` argv) that ran for ten hours on 2026-08-09.

    None means UNRESOLVED, which callers must treat as a failed check (R15 fail-silent), never as
    an empty diff — an unanswerable question is not a green answer.
    """
    if not sha:
        return None
    try:
        r = subprocess.run(["git", "diff", "--name-only", sha, "--"],
                           cwd=_REPO, capture_output=True, text=True, timeout=30)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    return {line.strip() for line in (r.stdout or "").splitlines() if line.strip()}


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/boot_sha.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("boot_sha")
    import sys
    stamp(sys.argv[1] if len(sys.argv) > 1 else "unknown")
