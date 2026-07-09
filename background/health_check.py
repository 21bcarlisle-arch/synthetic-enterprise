#!/usr/bin/env python3
"""Autonomous stack health check.

Verifies that every expected background process is running and that the
staging directory is being policed. Sends an NTFY summary. Exits 0 if all
healthy, 1 if any process is missing (so the caller can alert or restart).

Usage:
    python3 background/health_check.py          # print + NTFY on failure only
    python3 background/health_check.py --always # print + NTFY regardless
    python3 background/health_check.py --quiet  # no output, NTFY on failure only
"""

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "health-check-log.md"

sys.path.insert(0, str(PROJECT_DIR))
from background.ntfy_utils import send_ntfy  # noqa: E402

EXPECTED_PANES = {
    "ntfy-responder": "ntfy_responder.py",
    "staging-watcher": "staging_watcher.py",
    "session-watchdog": "session_watchdog.py",
    "supervisor": "supervisor.py",
    "dispatcher": "dispatcher.py",
    "discovery-daemon": "discovery_agent.py",
    "background-worker": "background_worker.py",
    "sim-runner": "sim_runner.py",
    "sanity-daemon": "sanity_daemon.py",
    "deadmans-switch": "deadmans_switch.py",
    "director-comments": "director_comments.py",
    # autonomous-runner deliberately excluded: retired by director decision
    # (docs/staging/AUTONOMOUS_RUNNER_RETIRED.md, 2026-07-07) -- the watchdog-managed
    # interactive session is now the single writer. Its absence is not a fault; do
    # not alert on it. Restart question folds into the next weekly PRIORITIES.md re-rank.
}


def _tmux_panes() -> dict[str, str]:
    """Return {session_name: pane_command} for all running tmux panes."""
    try:
        out = subprocess.check_output(
            ["tmux", "list-panes", "-a", "-F",
             "#{session_name} #{pane_current_command}"],
            text=True, timeout=5,
        )
        result = {}
        for line in out.splitlines():
            parts = line.strip().split(" ", 1)
            if len(parts) == 2:
                result[parts[0]] = parts[1]
        return result
    except Exception:
        return {}


def _running_scripts() -> list[str]:
    """Return list of python script paths currently running as processes."""
    try:
        out = subprocess.check_output(
            ["ps", "aux"], text=True, timeout=5,
        )
        return [line for line in out.splitlines() if "python" in line.lower()]
    except Exception:
        return []


def _check_staging_age() -> str | None:
    """Return warning string if any from_rich_*.md is older than 2 hours unactioned."""
    staging = PROJECT_DIR / "docs" / "staging"
    if not staging.is_dir():
        return None
    now = datetime.now(timezone.utc).timestamp()
    old = []
    for f in staging.glob("from_rich_*.md"):
        age_h = (now - f.stat().st_mtime) / 3600
        if age_h > 2:
            old.append(f"{f.name} ({age_h:.1f}h old)")
    if old:
        return "Unactioned messages: " + ", ".join(old)
    return None


def run_health_check() -> tuple[bool, list[str], list[str]]:
    """
    Returns (all_ok, ok_lines, problem_lines).
    """
    panes = _tmux_panes()
    ps_lines = _running_scripts()

    ok_lines = []
    problem_lines = []

    for session, script in EXPECTED_PANES.items():
        if session in panes:
            ok_lines.append(f"  ✓ {session} (tmux pane present, cmd={panes[session]})")
        elif any(script in line for line in ps_lines):
            ok_lines.append(f"  ✓ {session} (process running, no tmux pane)")
        else:
            problem_lines.append(f"  ✗ {session} — NOT RUNNING ({script})")

    staging_warn = _check_staging_age()
    if staging_warn:
        problem_lines.append(f"  ✗ {staging_warn}")
    else:
        ok_lines.append("  ✓ staging — no stale messages")

    all_ok = len(problem_lines) == 0
    return all_ok, ok_lines, problem_lines


def _log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"\n- [{ts}] {msg}")


def main() -> int:
    always_ntfy = "--always" in sys.argv
    quiet = "--quiet" in sys.argv

    all_ok, ok_lines, problem_lines = run_health_check()

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    status = "OK" if all_ok else "DEGRADED"

    lines = [f"[{ts}] Stack health: {status}"]
    if problem_lines:
        lines += problem_lines
    lines += ok_lines

    report = "\n".join(lines)

    if not quiet:
        print(report)

    _log(f"health={status} problems={len(problem_lines)} ok={len(ok_lines)}")

    if not all_ok:
        send_ntfy(
            f"[HEALTH CHECK] Stack DEGRADED — {len(problem_lines)} problem(s):\n"
            + "\n".join(problem_lines),
            headers={"X-Priority": "4", "X-Tags": "warning"},
        )
    elif always_ntfy:
        send_ntfy(f"[HEALTH CHECK] Stack OK — {len(ok_lines)} processes healthy.")

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
