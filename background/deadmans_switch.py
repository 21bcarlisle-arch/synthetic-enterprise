"""Dead-man's switch -- director-flagged incident, 2026-07-09.

Deliberately OUTSIDE the tmux/supervisor stack. Doorbell failure #5 proved
that stack's own turn-granting detection (is_session_idle()'s pane-content
inspection) can silently misread state for hours while the process stays
"alive" the whole time -- the daemon never crashed, it just kept granting
the wrong verdict. A watchdog built on the SAME pane-inspection primitive
could fail for the exact same underlying reason (a misread of what the
terminal is showing), so this one uses none of it: no tmux capture, no
regex on pane content, no is_session_idle() call anywhere in this file.

Signals used instead -- objective, external, and something a stuck
supervisor cannot itself corrupt:
  - the most recent git commit timestamp (real forward progress, this
    project's own definition of "done" throughout)
  - the most recent modification time across any file in
    docs/observability/ (any daemon actively logging counts as "the
    process tree is alive and doing something," even mid-task with no
    commit yet -- e.g. a multi-hour sim-runner GPU pass)

BLOCKED alert class: if neither signal has moved for
BLOCKED_THRESHOLD_SECONDS AND there is real unprocessed work on disk
(docs/staging/ files not yet in done/), sends one NTFY tagged [BLOCKED] --
visually distinct from routine daemon NTFYs -- and re-escalates on a
slower cadence while the condition persists (not silent forever past the
first alert, not spammy either, matching R5's "never repeat an unchanged
status" applied with a bounded re-alert rather than a single one-shot).
"""
from __future__ import annotations

import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from background.ntfy_utils import send_ntfy  # noqa: E402
from background import action_needed  # noqa: E402

LOG_FILE = PROJECT_DIR / "docs" / "observability" / "deadmans-switch-log.md"
STAGING_DIR = PROJECT_DIR / "docs" / "staging"
OBSERVABILITY_DIR = PROJECT_DIR / "docs" / "observability"

POLL_INTERVAL_SECONDS = 900       # 15 minutes -- a safety net, not a turn-granter
BLOCKED_THRESHOLD_SECONDS = 90 * 60   # 90 minutes of zero activity + queued work = BLOCKED
RE_ESCALATE_SECONDS = 60 * 60         # re-alert hourly while still stuck

_IGNORED_STAGING_NAMES = {".gitkeep"}

_last_escalation_ts: float | None = None


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{ts}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry)


def _last_commit_epoch() -> float:
    """Most recent commit timestamp on the current branch, or 0.0 if git
    isn't available/fails -- fails toward "looks stale," never toward
    silently assuming recent activity that didn't happen."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct"],
            cwd=str(PROJECT_DIR), capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return float(result.stdout.strip())
    except Exception:
        pass
    return 0.0


def _last_observability_write_epoch() -> float:
    """Most recent mtime across any file directly in docs/observability/ --
    any daemon actively logging (sim-runner mid-run, supervisor's own
    per-cycle log line, etc.) counts as evidence the process tree is alive
    and doing something, independent of whether a commit has landed yet."""
    latest = 0.0
    try:
        for p in OBSERVABILITY_DIR.iterdir():
            if p.is_file():
                latest = max(latest, p.stat().st_mtime)
    except OSError:
        pass
    return latest


def last_activity_epoch() -> float:
    return max(_last_commit_epoch(), _last_observability_write_epoch())


def _unprocessed_staging_files() -> list[str]:
    if not STAGING_DIR.is_dir():
        return []
    return sorted(
        p.name for p in STAGING_DIR.iterdir()
        if p.is_file() and p.name not in _IGNORED_STAGING_NAMES
    )


def _reping_open_action_needed_items() -> None:
    """Daily re-ping for anything genuinely waiting on Rich's own input
    (2026-07-11, director rule) -- independent of whether the tmux/
    supervisor stack itself looks stalled (that's the [BLOCKED] class
    below). An item here can sit open for days while everything else runs
    fine; the staging-activity check would never catch that on its own."""
    for entry in action_needed.due_for_reping():
        send_ntfy(action_needed.format_action_needed(
            entry["item_id"], entry["what"], entry["how"], entry["why"],
        ))
        action_needed.register_item(
            entry["item_id"], entry["what"], entry["how"], entry["why"],
        )
        log(f"Re-pinged open action-needed item: {entry['item_id']}")


def run_cycle() -> None:
    global _last_escalation_ts

    _reping_open_action_needed_items()

    staged = _unprocessed_staging_files()
    if not staged:
        log("Clean -- no unprocessed staging files")
        _last_escalation_ts = None
        return

    now = time.time()
    idle_seconds = now - last_activity_epoch()

    if idle_seconds < BLOCKED_THRESHOLD_SECONDS:
        log(
            f"Work queued ({len(staged)} file(s)) but activity recent "
            f"({idle_seconds / 60:.0f}min ago) -- not blocked"
        )
        return

    if _last_escalation_ts is not None and (now - _last_escalation_ts) < RE_ESCALATE_SECONDS:
        log(
            f"BLOCKED (still) -- {idle_seconds / 60:.0f}min idle, {len(staged)} file(s) "
            f"queued -- suppressed (re-alerts hourly)"
        )
        return

    shown = ", ".join(staged[:3]) + ("..." if len(staged) > 3 else "")
    send_ntfy(
        f"[BLOCKED] Dead-man's switch: {idle_seconds / 60:.0f} min with no commit or "
        f"observability-log activity, and {len(staged)} unprocessed staging file(s) "
        f"({shown}). The supervisor/tmux stack may be stuck -- check the session directly."
    )
    log(f"BLOCKED NTFY sent -- {idle_seconds / 60:.0f}min idle, {len(staged)} file(s) queued")
    _last_escalation_ts = now


def main() -> None:
    log("Dead-man's switch started -- independent of tmux/supervisor stack")
    while True:
        try:
            run_cycle()
        except Exception as e:
            log(f"Dead-man's switch cycle error: {e}")
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
