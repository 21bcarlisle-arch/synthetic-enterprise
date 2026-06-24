#!/usr/bin/env python3
"""Staging directory watcher — notification only, no automatic execution.

Polls docs/staging/ for new files. When a new file appears, sends an NTFY
notification to skynet-synthetic naming the file (so Rich/Claude know a
staged instruction is waiting for an explicit staging review per CLAUDE.md's
Staging Directory Protocol) and logs the event.

This watcher NEVER reads staged file contents into a prompt, runs commands
based on them, or sends them via tmux send-keys — it only announces that a
new file exists. Processing happens only during an explicit staging review.

Logs to docs/observability/staging-watcher-log.md.
Persists the set of already-seen filenames to
background/.staging_watcher_seen.json so restarts don't re-notify for files
that arrived in an earlier run.
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path("/home/rich/synthetic-enterprise")
STAGING_DIR = PROJECT_DIR / "docs" / "staging"
STATE_FILE = PROJECT_DIR / "background" / ".staging_watcher_seen.json"
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "staging-watcher-log.md"
POLL_INTERVAL_SECONDS = 30
IGNORED_NAMES = {".gitkeep"}

# Standalone script -- add the repo root so `from background.ntfy_utils
# import ...` works regardless of how it's invoked.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from background.ntfy_utils import send_ntfy  # noqa: E402
from background.agent_status import update_agent_status  # noqa: E402


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{ts}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry)


def ntfy(msg: str) -> None:
    send_ntfy(msg)


def current_files() -> set[str]:
    if not STAGING_DIR.is_dir():
        return set()
    return {p.name for p in STAGING_DIR.iterdir() if p.is_file() and p.name not in IGNORED_NAMES}


def load_seen() -> set[str]:
    if STATE_FILE.exists():
        return set(json.loads(STATE_FILE.read_text()))
    return None


def save_seen(seen: set[str]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(sorted(seen)))


def check_once(seen: set[str]) -> set[str]:
    """Check docs/staging/ once. Notifies (filename only) for any file not in
    `seen`, logs each notification, and returns the updated seen set.

    NTFY-originated files (from_rich_*.md) are silently added to seen without
    sending a notification — the ntfy_responder already acked those messages.
    """
    files = current_files()
    new_files = sorted(files - seen)
    for name in new_files:
        if name.startswith("from_rich_") and name.endswith(".md"):
            log(f"Silently registered NTFY-originated file: {name} (no staging notification)")
        elif name.startswith("run_complete_") and name.endswith(".md"):
            log(f"Silently registered sim run marker: {name} (Claude polls staging, no notification needed)")
        else:
            msg = f"New staged instruction: {name} — pending explicit staging review"
            ntfy(msg)
            log(f"Notified: {name}")
    if new_files:
        seen = files
        save_seen(seen)
    return seen


def main() -> None:
    seen = load_seen()
    if seen is None:
        # First run: seed with whatever's already there so we don't notify
        # about a backlog that predates the watcher.
        seen = current_files()
        save_seen(seen)
        log(f"Staging watcher started — seeded with {len(seen)} existing file(s), no notification sent for these")
    else:
        log("Staging watcher started — resuming from saved state")

    update_agent_status(
        "staging-watcher", status="idle",
        last_action="Watcher started",
        role="Monitors docs/staging/ for new files; sends NTFY to alert CC",
        produces="NTFY notifications on new staging files",
    )

    while True:
        # Heartbeat at top of every cycle — independent of check_once success/failure
        try:
            update_agent_status("staging-watcher", status="idle", last_action=f"Heartbeat — {len(seen)} files tracked")
        except Exception:
            pass
        try:
            seen = check_once(seen)
        except Exception as e:
            log(f"Watcher error: {e}")
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
