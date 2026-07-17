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


if __name__ == "__main__":
    import sys
    stamp(sys.argv[1] if len(sys.argv) > 1 else "unknown")
