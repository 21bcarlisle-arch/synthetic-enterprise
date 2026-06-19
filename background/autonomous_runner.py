#!/usr/bin/env python3
"""Autonomous Claude turn runner — replaces the broken tmux keystrokes autoloop.

Problem with the old approach (session_watchdog sends AUTOLOOP_INSTRUCTION
via tmux send-keys): Claude Code's interactive session receives the keystrokes
but doesn't reliably process them as conversation turns when no human is
actively present. Result: the watchdog logged 38 "autoloop instruction sent"
events over 6+ hours with zero work done.

This script does the same thing properly: when the interactive Claude session
has been idle for IDLE_THRESHOLD_SECONDS (30 min), it runs:

    claude -p "<autonomous prompt>"

This starts a FRESH, non-interactive Claude Code process that:
  - Reads CLAUDE.md and project context
  - Checks docs/staging/ for unactioned files and processes them
  - If staging empty, advances the next backlog item
  - Commits, pushes, NTFYs Rich with results
  - Exits cleanly

Rate-limited to MAX_TURNS_PER_HOUR (2) to avoid excessive token spend.
Doesn't launch a turn if the interactive session is actively changing
(Rich is in conversation) — only fires when the pane has been static for
IDLE_THRESHOLD_SECONDS.

Logs to docs/observability/autonomous-runner-log.md.
Turn output appended to docs/observability/autonomous-turn-output.md.
"""

import json
import subprocess
import sys
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "autonomous-runner-log.md"
TURN_OUTPUT_FILE = PROJECT_DIR / "docs" / "observability" / "autonomous-turn-output.md"
PANE_STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".autonomous_pane_state.json"

SESSION_NAME = "claude"

# Claude Code binary — full path since nvm isn't active in subprocess env
CLAUDE_BIN = Path("/home/rich/.nvm/versions/node/v24.16.0/bin/claude")

POLL_INTERVAL_SECONDS = 120       # check every 2 min
IDLE_THRESHOLD_SECONDS = 30 * 60  # 30 min static pane = session idle
MAX_TURNS_PER_HOUR = 2            # conservative — each turn costs frontier tokens

AUTONOMOUS_PROMPT = (
    "Check docs/staging/ for any unactioned from_rich_*.md or run_complete_*.md "
    "files (anything NOT yet in docs/staging/done/). Process each following the "
    "Staging Directory Protocol — action it, move to docs/staging/done/, commit, "
    "push, NTFY Rich with results. "
    "If staging is empty, check docs/staging/drafts/ for a proposed next phase "
    "and proceed if the 4h opt-out window has passed. "
    "If nothing is pending, advance the highest-priority item in "
    "docs/reports/REPORTING_BACKLOG.md with tests. "
    "Always: run tests before committing, commit with a clear message, push, "
    "and NTFY Rich with what was done. "
    "If you genuinely have nothing to do, NTFY Rich: 'Autonomous turn: staging "
    "empty and no backlog work available — idling.' and exit."
)

sys.path.insert(0, str(PROJECT_DIR))
from background.ntfy_utils import send_ntfy  # noqa: E402

_turn_times: deque = deque()
_active_proc = None


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{ts}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry, flush=True)


def turns_in_last_hour() -> int:
    now = time.time()
    while _turn_times and now - _turn_times[0] > 3600:
        _turn_times.popleft()
    return len(_turn_times)


def _pane_content() -> str:
    result = subprocess.run(
        ["tmux", "capture-pane", "-t", SESSION_NAME, "-p"],
        capture_output=True, text=True,
    )
    return result.stdout if result.returncode == 0 else ""


def idle_seconds() -> float:
    """Seconds since the Claude pane was last observed to change.
    Persisted to a file so restarts of this script don't reset the clock."""
    current = _pane_content()
    now = time.time()

    try:
        if PANE_STATE_FILE.exists():
            data = json.loads(PANE_STATE_FILE.read_text())
            if data.get("content") == current:
                return now - float(data["since"])
            # Content changed — reset
    except Exception:
        pass

    PANE_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    PANE_STATE_FILE.write_text(json.dumps({"content": current, "since": now}))
    return 0.0


def launch_turn() -> None:
    global _active_proc

    if not CLAUDE_BIN.exists():
        log(f"claude binary not found at {CLAUDE_BIN} — cannot launch autonomous turn")
        return

    if _active_proc is not None and _active_proc.poll() is None:
        log("Previous autonomous turn still running — skipping this cycle")
        return

    if turns_in_last_hour() >= MAX_TURNS_PER_HOUR:
        log(f"Rate cap ({MAX_TURNS_PER_HOUR}/hour) — skipping turn")
        return

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    log(f"Launching autonomous turn (claude -p)")
    send_ntfy(f"[AUTO] Starting autonomous Claude turn — session idle 30+ min ({ts})")

    TURN_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TURN_OUTPUT_FILE, "a") as out:
        out.write(f"\n\n---\n# Autonomous turn — {ts}\n\n")

    outfile = open(TURN_OUTPUT_FILE, "a")
    _active_proc = subprocess.Popen(
        [str(CLAUDE_BIN), "-p", AUTONOMOUS_PROMPT],
        cwd=str(PROJECT_DIR),
        stdout=outfile,
        stderr=outfile,
        text=True,
    )
    _turn_times.append(time.time())
    log(f"Autonomous turn launched (pid={_active_proc.pid})")


def main() -> None:
    log("Autonomous runner started")

    while True:
        time.sleep(POLL_INTERVAL_SECONDS)

        try:
            # Reap completed turn
            if _active_proc is not None and _active_proc.poll() is not None:
                rc = _active_proc.returncode
                log(f"Autonomous turn completed (pid={_active_proc.pid}, rc={rc})")
                _active_proc = None

            idle = idle_seconds()

            if idle >= IDLE_THRESHOLD_SECONDS and _active_proc is None:
                log(f"Session idle {idle/60:.0f}min — launching autonomous turn")
                launch_turn()

        except Exception as e:
            log(f"Runner error: {e}")


if __name__ == "__main__":
    main()
