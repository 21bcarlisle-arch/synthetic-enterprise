#!/usr/bin/env python3
"""Claude Code session watchdog — gated restart, no auto-restart without
human confirmation (except usage-limit auto-resume, see below).

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

USAGE-LIMIT AUTO-RESUME (no confirmation gate): a Claude usage-limit message
is a benign, expected, time-boxed condition — not a crash — so it is
exempted from the "YES" gate above (Rich's instruction: don't ask about
paying for more tokens, just wait for the reset and continue). When the
tmux pane shows a usage-limit message (`usage_limit_detected`,
best-effort regex — see its docstring for the wording-uncertainty caveat),
`handle_usage_limit` polls every USAGE_LIMIT_POLL_INTERVAL_SECONDS, nudging
the session with the resume instruction, until the message clears or the
process needs restarting (`restart_claude(resume=True)`, using `claude -c`
to continue the same conversation — still no
--dangerously-skip-permissions). If USAGE_LIMIT_MAX_WAIT_SECONDS passes with
the limit message still showing, this falls back to the normal
confirmation-gated `handle_session_ended` flow — at that point something
other than an ordinary rolling-limit reset is likely going on, and that
case should still involve Rich.

DOWNTIME GPU WORK: when a usage limit pauses the main session,
`handle_usage_limit` also queues DOWNTIME_TASKS into
docs/instructions/background-tasks.md (`queue_downtime_tasks`) — one
forward-prep task (qwen3:14b drafts the next backlog sub-phase) and one
housekeeping/observability task (qwen2.5:7b summarises recent logs). The
independent background-worker tmux session picks these up and writes its
output to docs/observability/background-task-<name>.md as a draft for the
main session to review on resume — never a direct commit. This keeps the
GPU doing useful prep/housekeeping work instead of sitting idle during the
wait (Rich's instruction).

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
import re
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
USAGE_LIMIT_POLL_INTERVAL_SECONDS = 15 * 60  # 15 minutes
USAGE_LIMIT_MAX_WAIT_SECONDS = 6 * 3600  # 6 hours — covers the 5h session limit with margin
NTFY_TOPIC = "skynet-synthetic"
NTFY_PUBLISH_URL = f"https://ntfy.sh/{NTFY_TOPIC}"
NTFY_POLL_URL = f"https://ntfy.sh/{NTFY_TOPIC}/json"
LOG_FILE = Path(f"{PROJECT_DIR}/docs/observability/session-watchdog-log.md")

# Best-effort match for Claude Code's usage-limit message. The exact wording
# is not confirmed against current Claude Code output (no access to a live
# rate-limited session to verify). Deliberately narrower than a bare
# "rate limit" / "5-hour limit" / "weekly limit" match: this session's own
# conversation and source code talk *about* usage limits constantly (this
# very file, this comment included), and capture_pane() would false-positive
# on a generic match of those words scrolling through the pane. Each
# alternative below pairs a limit-type word with "reached"/"will reset" to
# require it look like an actual exhaustion notice, not discussion of one.
# If real messages don't match, tighten/extend this pattern from an observed
# transcript.
USAGE_LIMIT_PATTERN = re.compile(
    r"(usage limit reached|approaching[^\n]*usage limit reached|"
    r"(5-hour|weekly) limit reached|usage limit will reset)",
    re.IGNORECASE,
)

RESUME_INSTRUCTION = (
    "Read CLAUDE.md and STATUS.md. Continue from where the last session ended. "
    "Check docs/instructions/MASTER_BACKLOG.md for the current phase. Proceed autonomously."
)

DOWNTIME_TASKS_FILE = Path(f"{PROJECT_DIR}/docs/instructions/background-tasks.md")

# Tasks queued for the independent background-worker tmux session (local
# Ollama models) while the main session is paused on a usage limit — "GPU
# doing work to minimise downtime" (Rich's instruction). One forward-prep
# (drafting the next backlog sub-phase) and one housekeeping/observability
# task. Both land as draft files under docs/observability/ (via
# run_queued_tasks.py's existing output convention) for the main session to
# review and integrate on resume — never a direct commit.
DOWNTIME_TASKS = [
    {
        "name": "phase4b-4-draft-home-move-win-rate",
        "model": "qwen3:14b",
        "description": (
            "Draft Phase 4b-4 (home move win rate) for the synthetic energy "
            "supplier project, per docs/instructions/MASTER_BACKLOG.md's "
            "Phase 4b section and the pattern established by "
            "saas/churn_model.py and saas/clv_model.py (pure module, plain "
            "dict in/out, no sim/ imports). Output a draft "
            "saas/home_move_win_rate.py module plus a draft "
            "tests/saas/test_home_move_win_rate.py, as markdown code blocks "
            "with file path headers -- this is a first-pass draft for "
            "Claude Code to review and integrate, not a direct commit."
        ),
    },
    {
        "name": "downtime-observability-housekeeping",
        "model": "qwen2.5:7b",
        "description": (
            "Summarise the last 10 entries of "
            "docs/observability/session-watchdog-log.md and "
            "docs/observability/background-worker-log.md into a short "
            "markdown digest (recent restarts, completed background tasks, "
            "any errors) -- a housekeeping/observability catch-up draft for "
            "Claude Code to fold into STATUS.md on resume."
        ),
    },
]

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


def capture_pane() -> str:
    """Currently visible content of the 'claude' pane (the viewport only —
    not scrollback), or "" if the session doesn't exist.

    Deliberately excludes scrollback: a real usage-limit message is part of
    Claude Code's persistent current state, not a one-off line that scrolls
    past. Including scrollback risks matching transient text (e.g. a command
    that echoes the word "limit") rather than an actual live exhaustion
    notice — see USAGE_LIMIT_PATTERN's comment.
    """
    result = subprocess.run(
        ["tmux", "capture-pane", "-t", SESSION_NAME, "-p"],
        capture_output=True, text=True,
    )
    return result.stdout if result.returncode == 0 else ""


def usage_limit_detected(pane_text: str) -> bool:
    """True if `pane_text` looks like a Claude usage-limit message.

    Checked line by line, skipping any line containing `|`, `[`, or `]` —
    source code and regex literals (including USAGE_LIMIT_PATTERN's own
    definition, or this conversation discussing it) commonly contain these
    and would otherwise false-positive; a real UI message is plain prose.

    Best-effort — see USAGE_LIMIT_PATTERN's comment for the
    wording-uncertainty caveat.
    """
    for line in pane_text.splitlines():
        if any(ch in line for ch in "|[]"):
            continue
        if USAGE_LIMIT_PATTERN.search(line):
            return True
    return False


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


def restart_claude(resume: bool = False) -> None:
    """Restart the 'claude' tmux session.

    resume=False (default, crash path): fresh `claude` + RESUME_INSTRUCTION
    (the prior conversation may be in an unknown state).
    resume=True (usage-limit path): `claude -c` to continue the same
    conversation — the session was paused by the limit, not crashed, so
    there's nothing to "resume from CLAUDE.md/STATUS.md" about. Either way,
    --dangerously-skip-permissions is never used.
    """
    if restarts_in_last_hour() >= MAX_RESTARTS_PER_HOUR:
        msg = (f"Session watchdog: restart cap reached "
               f"({MAX_RESTARTS_PER_HOUR}/hour) — manual intervention needed.")
        log(msg)
        ntfy(msg)
        return

    log(f"Restarting Claude Code (normal permissions, no skip flag, resume={resume})")
    subprocess.run(["tmux", "kill-session", "-t", SESSION_NAME], capture_output=True)
    time.sleep(5)

    subprocess.run([
        "tmux", "new-session", "-d", "-s", SESSION_NAME, "-c", PROJECT_DIR
    ])
    time.sleep(3)

    subprocess.run([
        "tmux", "send-keys", "-t", SESSION_NAME,
        "claude -c" if resume else "claude", "Enter"
    ])
    time.sleep(15)

    if not resume:
        subprocess.run([
            "tmux", "send-keys", "-t", SESSION_NAME,
            RESUME_INSTRUCTION, "Enter"
        ])

    restart_times.append(time.time())
    count = restarts_in_last_hour()
    log(f"Claude Code restarted ({count}/{MAX_RESTARTS_PER_HOUR} this hour, resume={resume})")
    ntfy("Claude Code resumed after usage limit." if resume else "Claude Code restarted — session running.")


def queue_downtime_tasks() -> None:
    """Append DOWNTIME_TASKS to the background task queue
    (docs/instructions/background-tasks.md) for the independent
    background-worker tmux session to pick up while the main session is
    paused — "GPU doing work to minimise downtime" (Rich's instruction).

    Idempotent: skips any task whose "### Task: <name>" header already
    appears in the file (queued, running, or done in an earlier episode).
    """
    if not DOWNTIME_TASKS_FILE.exists():
        return
    content = DOWNTIME_TASKS_FILE.read_text()

    new_blocks = [
        f"\n### Task: {task['name']}\n"
        f"Description: {task['description']}\n"
        f"Model: {task['model']}\n"
        for task in DOWNTIME_TASKS
        if f"### Task: {task['name']}" not in content
    ]
    if not new_blocks:
        return

    marker = "## QUEUED\n"
    if marker not in content:
        return
    content = content.replace(marker, marker + "".join(new_blocks), 1)
    DOWNTIME_TASKS_FILE.write_text(content)
    log(f"Queued {len(new_blocks)} downtime task(s) for background worker")


def handle_usage_limit() -> None:
    """Usage-limit auto-resume — no NTFY "YES" gate (see module docstring).

    Queues forward-prep and housekeeping work for the background-worker
    tmux session (`queue_downtime_tasks`), then polls every
    USAGE_LIMIT_POLL_INTERVAL_SECONDS, nudging the session with
    RESUME_INSTRUCTION, until either the usage-limit message clears (session
    resumed in place) or the process has exited (restart with
    `claude -c`). Falls back to the normal confirmation-gated
    handle_session_ended() if USAGE_LIMIT_MAX_WAIT_SECONDS passes with the
    limit message still showing.
    """
    log("Usage-limit message detected — auto-wait (no confirmation required)")
    ntfy("Claude Code usage limit reached — watchdog will auto-resume when it "
         "resets, no action needed.")
    queue_downtime_tasks()

    waited = 0
    while waited < USAGE_LIMIT_MAX_WAIT_SECONDS:
        time.sleep(USAGE_LIMIT_POLL_INTERVAL_SECONDS)
        waited += USAGE_LIMIT_POLL_INTERVAL_SECONDS

        if not session_exists() or not claude_is_running():
            log("Session ended while usage-limited — resuming with `claude -c`")
            restart_claude(resume=True)
            return

        subprocess.run(["tmux", "send-keys", "-t", SESSION_NAME, RESUME_INSTRUCTION, "Enter"])
        time.sleep(5)
        if not usage_limit_detected(capture_pane()):
            log("Usage limit cleared — session resumed in place")
            ntfy("Claude Code usage limit cleared — session resumed automatically.")
            return

    log(f"Usage limit still showing after {USAGE_LIMIT_MAX_WAIT_SECONDS}s — "
        "escalating to normal restart-confirmation flow")
    ntfy("Claude Code usage limit has not cleared after the auto-wait window — "
         "escalating for a manual check.")
    handle_session_ended()


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
    log("Session watchdog started (gated mode — restarts require NTFY YES "
        "confirmation, except usage-limit auto-resume)")
    ntfy("Session watchdog started — monitoring 'claude' tmux session. "
         "Crash restarts require a YES reply (no --dangerously-skip-permissions, "
         f"max {MAX_RESTARTS_PER_HOUR}/hour); usage-limit pauses auto-resume "
         "without confirmation.")
    consecutive_down = 0

    while True:
        time.sleep(CHECK_INTERVAL_SECONDS)
        try:
            if session_exists() and usage_limit_detected(capture_pane()):
                handle_usage_limit()
                consecutive_down = 0
                continue

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
