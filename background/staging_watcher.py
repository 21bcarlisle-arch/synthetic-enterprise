#!/usr/bin/env python3
"""Staging directory watcher — notification only, no automatic execution.

Polls docs/staging/ for new files. When a new file appears, sends an NTFY
notification to skynet-synthetic naming the file (so Rich/Claude know a
staged instruction is waiting for an explicit staging review per CLAUDE.md's
Staging Directory Protocol) and logs the event.

This watcher NEVER reads staged file contents into a prompt, runs commands
based on them, or sends them via tmux send-keys — it only announces that a
new file exists. Processing happens only during an explicit staging review.

Also periodically fetches origin/main and surfaces any new staging files
committed with the [ADVISOR-STAGED] prefix so the strategy advisor can
stage instructions remotely (Remote Staging Bridge).

Also checks, once per poll cycle, whether it's the 1st of the month (UTC)
and a monthly maintenance reminder hasn't been queued yet this month
(docs/operations/MAINTENANCE.md). If due, writes a
docs/staging/maintenance_due_<YYYYMM>.md marker -- picked up by the normal
new-staged-file path above, so it gets NTFY'd and actioned like any other
staged instruction, no separate cron/dispatcher wiring needed.

Logs to docs/observability/staging-watcher-log.md.
Persists the set of already-seen filenames to
background/.staging_watcher_seen.json so restarts don\'t re-notify for files
that arrived in an earlier run. Persists the last month a maintenance
reminder was queued to background/.maintenance_reminder_sent.json.
"""

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path("/home/rich/synthetic-enterprise")
STAGING_DIR = PROJECT_DIR / "docs" / "staging"
STATE_FILE = PROJECT_DIR / "background" / ".staging_watcher_seen.json"
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "staging-watcher-log.md"
POLL_INTERVAL_SECONDS = 30
GIT_PULL_INTERVAL_SECONDS = 180  # check remote every 3 minutes
IGNORED_NAMES = {".gitkeep"}
ADVISOR_PREFIX = "[ADVISOR-STAGED]"
MAINTENANCE_STATE_FILE = PROJECT_DIR / "background" / ".maintenance_reminder_sent.json"
MAINTENANCE_DOC = PROJECT_DIR / "docs" / "operations" / "MAINTENANCE.md"

# Standalone script -- add the repo root so `from background.ntfy_utils
# import ...` works regardless of how it\'s invoked.
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


def _run(cmd: list[str], timeout: int = 30) -> tuple[int, str, str]:
    """Run a subprocess and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd, capture_output=True, text=True,
        cwd=str(PROJECT_DIR), timeout=timeout,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def _extract_advisor_staging_files(since_ref: str) -> list[str]:
    """Return staging filenames added/changed in ADVISOR-STAGED commits since since_ref on origin/main.

    Returns empty list if no advisor commits or on any error.
    """
    # Get commit subjects from new remote commits
    rc, out, _ = _run(["git", "log", since_ref + "..origin/main", "--pretty=format:%s"])
    if rc != 0 or not out:
        return []
    subjects = out.splitlines()
    if not any(ADVISOR_PREFIX in s for s in subjects):
        return []

    # Get files changed in those commits under docs/staging/ (non-done/)
    rc2, out2, _ = _run([
        "git", "diff", "--name-only", since_ref, "origin/main", "--", "docs/staging/",
    ])
    if rc2 != 0:
        return []

    results = []
    for path in out2.splitlines():
        name = Path(path).name
        parent = str(Path(path).parent)
        # Only files directly in docs/staging/ (not done/)
        if parent == "docs/staging" and name not in IGNORED_NAMES:
            results.append(name)
    return results


def check_remote(seen: set[str]) -> set[str]:
    """Fetch origin/main and surface any new advisor-staged files into local staging.

    Returns updated seen set. On any subprocess error, logs and returns seen unchanged.
    """
    rc, _, err = _run(["git", "fetch", "origin", "main"])
    if rc != 0:
        log(f"git fetch failed (network?): {err[:80]}")
        return seen

    # What\'s the local HEAD?
    rc2, local_head, _ = _run(["git", "rev-parse", "HEAD"])
    if rc2 != 0:
        return seen

    # Any new commits on origin/main?
    rc3, new_count, _ = _run(["git", "rev-list", "--count", local_head + "..origin/main"])
    if rc3 != 0 or not new_count or new_count == "0":
        return seen  # already up to date

    log(f"Remote has {new_count} new commit(s) — scanning for advisor-staged files")

    advisor_files = _extract_advisor_staging_files(local_head)
    if not advisor_files:
        log("No [ADVISOR-STAGED] commits in new remote work — skipping")
        return seen

    # Extract each advisor-staged file from remote and write locally
    for name in advisor_files:
        remote_path = "docs/staging/" + name
        local_path = STAGING_DIR / name
        if local_path.exists():
            continue  # already present
        rc4, content, err4 = _run(["git", "show", "origin/main:" + remote_path])
        if rc4 != 0:
            log(f"Could not extract {name} from origin/main: {err4[:60]}")
            continue
        local_path.write_text(content)
        log(f"Remote staging bridge: extracted {name} from advisor commit")

    return seen  # check_once will pick up new files on next poll


def _load_maintenance_state() -> str:
    """Return the last "YYYY-MM" a maintenance reminder was queued, or "" if none."""
    if MAINTENANCE_STATE_FILE.exists():
        try:
            return json.loads(MAINTENANCE_STATE_FILE.read_text()).get("last_sent_month", "")
        except (json.JSONDecodeError, Exception):
            return ""
    return ""


def _save_maintenance_state(month: str) -> None:
    MAINTENANCE_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    MAINTENANCE_STATE_FILE.write_text(json.dumps({"last_sent_month": month}))


def check_monthly_maintenance(now: datetime) -> None:
    """On the 1st of the month (UTC), queue a maintenance_due marker in
    docs/staging/ if one hasn\'t already been queued this month. The marker
    is picked up by check_once() like any other new staged file, so it gets
    NTFY\'d and actioned through the normal staging flow.
    """
    if now.day != 1:
        return
    month_key = now.strftime("%Y-%m")
    if _load_maintenance_state() == month_key:
        return

    marker = STAGING_DIR / f"maintenance_due_{now.strftime('%Y%m')}.md"
    if not marker.exists():
        STAGING_DIR.mkdir(parents=True, exist_ok=True)
        marker.write_text(
            f"[MAINTENANCE] Monthly maintenance due for {month_key}.\n\n"
            f"Run the checklist in docs/operations/MAINTENANCE.md and log the "
            f"result in docs/operations/maintenance-log.md.\n"
        )
        log(f"Queued monthly maintenance reminder: {marker.name}")
    _save_maintenance_state(month_key)


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
        # First run: seed with whatever\'s already there so we don\'t notify
        # about a backlog that predates the watcher.
        seen = current_files()
        save_seen(seen)
        log(f"Staging watcher started — seeded with {len(seen)} existing file(s), no notification sent for these")
    else:
        log("Staging watcher started — resuming from saved state")

    update_agent_status(
        "staging-watcher", status="idle",
        last_action="Watcher started",
        role="Monitors docs/staging/ for new files; NTFY on new items; git fetch origin every 3min for [ADVISOR-STAGED] commits",
        produces="NTFY notifications on new staging files",
    )

    last_remote_check = 0.0

    while True:
        now = time.monotonic()

        # Heartbeat at top of every cycle
        try:
            update_agent_status("staging-watcher", status="idle", last_action=f"Heartbeat — {len(seen)} files tracked")
        except Exception:
            pass

        # Periodic remote check (every GIT_PULL_INTERVAL_SECONDS)
        if now - last_remote_check >= GIT_PULL_INTERVAL_SECONDS:
            try:
                seen = check_remote(seen)
                last_remote_check = now
            except Exception as e:
                log(f"Remote check error: {e}")
                last_remote_check = now  # back off even on error

        try:
            check_monthly_maintenance(datetime.now(timezone.utc))
        except Exception as e:
            log(f"Monthly maintenance check error: {e}")

        try:
            seen = check_once(seen)
        except Exception as e:
            log(f"Watcher error: {e}")
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
