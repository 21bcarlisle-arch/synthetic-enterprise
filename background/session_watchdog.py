#!/usr/bin/env python3
"""Claude Code session watchdog — gated restart, no auto-restart without
human confirmation.

Monitors the 'claude' tmux session. When Claude Code is no longer running
(token limit, crash, or completion):
  1. Sends an NTFY alert asking Rich to reply "YES" to restart.
  2. Polls the NTFY topic (https://ntfy.sh/skynet-synthetic) every 60 seconds
     for up to 4 hours, looking for a reply containing "YES".
  3. If "YES" is seen (and the restart cap below isn't exceeded), restarts
     the 'claude' tmux session with plain `claude` — NOT
     `--dangerously-skip-permissions`. Normal tool-permission prompts apply
     to the restarted session exactly as they would to any session.
  4. If 4 hours pass with no "YES", the watchdog logs that the confirmation
     window expired and returns to monitoring — no restart happens.

Safety cap: at most MAX_RESTARTS_PER_HOUR restarts, regardless of how many
"YES" confirmations arrive.

KNOWN LIMITATION — "verified sender": https://ntfy.sh/skynet-synthetic is a
public, unauthenticated topic. There is no cryptographic way to verify who
posted a "YES" reply; this is a best-effort keyword match on messages
received after the alert was sent, documented here rather than overstated.
Because the restart never uses --dangerously-skip-permissions, the worst
case of a spoofed "YES" is an idle Claude Code session sitting at a normal
permission prompt — not an unattended-autonomous session.

Logs to docs/observability/session-watchdog-log.md.
"""

import json
import subprocess
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

import requests

SESSION_NAME = "claude"
PROJECT_DIR = "/home/rich/synthetic-enterprise"
CHECK_INTERVAL_SECONDS = 60
CONFIRM_POLL_INTERVAL_SECONDS = 60
CONFIRM_TIMEOUT_SECONDS = 4 * 3600  # 4 hours
MAX_RESTARTS_PER_HOUR = 3
NTFY_TOPIC = "skynet-synthetic"
NTFY_PUBLISH_URL = f"https://ntfy.sh/{NTFY_TOPIC}"
NTFY_POLL_URL = f"https://ntfy.sh/{NTFY_TOPIC}/json"
LOG_FILE = Path(f"{PROJECT_DIR}/docs/observability/session-watchdog-log.md")

RESUME_INSTRUCTION = (
    "Read CLAUDE.md and STATUS.md. Continue from where the last session ended. "
    "Check docs/instructions/MASTER_BACKLOG.md for the current phase. Proceed autonomously."
)

restart_times: deque = deque()


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{ts}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry)


def ntfy(msg: str) -> None:
    subprocess.run(
        ["curl", "-s", "-d", msg, NTFY_PUBLISH_URL],
        capture_output=True,
    )


def session_exists() -> bool:
    return subprocess.run(
        ["tmux", "has-session", "-t", SESSION_NAME],
        capture_output=True,
    ).returncode == 0


def claude_is_running() -> bool:
    result = subprocess.run(
        ["tmux", "list-panes", "-t", SESSION_NAME, "-F", "#{pane_current_command}"],
        capture_output=True, text=True,
    )
    output = result.stdout.lower()
    return "claude" in output or "node" in output


def restarts_in_last_hour() -> int:
    now = time.time()
    while restart_times and now - restart_times[0] > 3600:
        restart_times.popleft()
    return len(restart_times)


def _is_yes_reply(record: dict, since: float) -> bool:
    """True if `record` (one parsed NTFY JSON-poll line) is a message event
    posted after `since` (unix timestamp) whose body contains "yes"."""
    if record.get("event") != "message":
        return False
    if record.get("time", 0) <= since:
        return False
    return "yes" in record.get("message", "").lower()


def _poll_for_yes_reply(since: float) -> bool:
    """Single poll of the NTFY topic for a "YES" reply posted after `since`."""
    try:
        response = requests.get(
            NTFY_POLL_URL,
            params={"poll": "1", "since": int(since)},
            timeout=10,
        )
        for line in response.text.splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            if _is_yes_reply(record, since):
                return True
    except (requests.RequestException, json.JSONDecodeError) as e:
        log(f"Confirmation poll error: {e}")
    return False


def wait_for_restart_confirmation(since: float) -> bool:
    """Poll the NTFY topic for a reply containing "YES" posted after `since`
    (a unix timestamp). Returns True if found within CONFIRM_TIMEOUT_SECONDS,
    False on timeout."""
    deadline = since + CONFIRM_TIMEOUT_SECONDS
    while time.time() < deadline:
        time.sleep(CONFIRM_POLL_INTERVAL_SECONDS)
        if _poll_for_yes_reply(since):
            return True
    return False


def restart_claude() -> None:
    if restarts_in_last_hour() >= MAX_RESTARTS_PER_HOUR:
        msg = (f"Session watchdog: restart cap reached "
               f"({MAX_RESTARTS_PER_HOUR}/hour) — manual intervention needed.")
        log(msg)
        ntfy(msg)
        return

    log("Restart confirmed — restarting Claude Code (normal permissions, no skip flag)")
    subprocess.run(["tmux", "kill-session", "-t", SESSION_NAME], capture_output=True)
    time.sleep(5)

    subprocess.run([
        "tmux", "new-session", "-d", "-s", SESSION_NAME, "-c", PROJECT_DIR
    ])
    time.sleep(3)

    subprocess.run([
        "tmux", "send-keys", "-t", SESSION_NAME,
        "claude", "Enter"
    ])
    time.sleep(15)

    subprocess.run([
        "tmux", "send-keys", "-t", SESSION_NAME,
        RESUME_INSTRUCTION, "Enter"
    ])

    restart_times.append(time.time())
    count = restarts_in_last_hour()
    log(f"Claude Code restarted ({count}/{MAX_RESTARTS_PER_HOUR} this hour)")
    ntfy("Claude Code restarted — session running.")


def handle_session_ended() -> None:
    alert_time = time.time()
    log("Claude Code session ended — sending restart-confirmation request")
    ntfy("Claude Code session ended — reply YES to this notification to restart.")

    confirmed = wait_for_restart_confirmation(alert_time)
    if not confirmed:
        log("Confirmation window expired (4h) — no restart. Resuming monitoring.")
        ntfy("Session watchdog: no restart confirmation received within 4 hours — "
              "session left stopped.")
        return

    log("Restart confirmation ('YES') received")
    restart_claude()


def main() -> None:
    log("Session watchdog started (gated mode — restarts require NTFY YES confirmation)")
    ntfy("Session watchdog started — monitoring 'claude' tmux session. "
         "Restarts require a YES reply, no --dangerously-skip-permissions, max "
         f"{MAX_RESTARTS_PER_HOUR} restarts/hour.")
    consecutive_down = 0

    while True:
        time.sleep(CHECK_INTERVAL_SECONDS)
        try:
            if not session_exists() or not claude_is_running():
                consecutive_down += 1
                log(f"Claude Code not detected (check {consecutive_down}/2)")
                if consecutive_down >= 2:
                    handle_session_ended()
                    consecutive_down = 0
            else:
                consecutive_down = 0
        except Exception as e:
            log(f"Watchdog error: {e}")


if __name__ == "__main__":
    main()
