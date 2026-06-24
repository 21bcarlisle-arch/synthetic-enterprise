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

PROACTIVE USAGE PAUSE (soft, self-checkpointing — Rich's instruction,
2026-06-13, fixed 2026-06-14): the usage-limit handling above is reactive —
it waits for Claude Code's own "usage limit reached" message, which can land
mid-tool-call and leave a messier resume than a stop at a natural checkpoint
(between sub-phases, after a commit). To avoid that, the watchdog itself
checks usage before sending each autoloop nudge: `check_session_usage()`
sends a standalone `/usage` keystroke to the session (a slash command can
only be recognised when it's the entire input — embedding "run /usage..."
inside a longer instruction, as the original version of this did, is never
executed as a command), captures the pane, parses the "Current session"
percentage and reset time via `parse_usage_pane()`, then dismisses the
dialog with Escape.

If usage is at or above USAGE_PAUSE_THRESHOLD_PCT (90%), the watchdog writes
docs/observability/.usage_pause.json itself (`{"resume_at": "<iso8601>"}`,
computed from the parsed reset time via `_usage_resume_at`) and skips sending
AUTOLOOP_INSTRUCTION for this cycle — Claude's current sub-phase is left to
finish naturally rather than being interrupted. Before sending the next
autoloop nudge, `usage_pause_active()` checks this file: if `resume_at` is
still in the future, the nudge is suppressed entirely (logged once, not every
cycle); once it has passed, the file is deleted, an NTFY is sent, and normal
autoloop resumes — `check_session_usage()` runs again on the next nudge and
will pause again if still >= 90%. This is a soft self-imposed checkpoint
layered in front of the hard usage-limit path above, not a replacement for
it.

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
import secrets
import subprocess
import sys
import time
from collections import deque
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

# This script runs standalone via `python3 background/session_watchdog.py`,
# so `background` isn't on sys.path as a package by default -- add the repo
# root so `from background.ntfy_utils import ...` works regardless of how
# it's invoked.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from background.ntfy_utils import send_ntfy, was_sent_by_us  # noqa: E402
from background.agent_status import update_agent_status  # noqa: E402

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

# --- Two-way NTFY (gate reply actions) ---
#
# See docs/instructions/NTFY_TWO_WAY_PROTOCOL.md. The file API is exposed via
# Tailscale Funnel at this URL (update if `tailscale funnel status` changes —
# e.g. after re-enabling Funnel from scratch).
FUNNEL_BASE_URL = "https://skynet-1.taila062fa.ts.net"

# Single-slot gate id: only one REVIEW_GATE is ever active in this session's
# pane at a time, so a fixed id is sufficient.
GATE_ID = "main"

RESPONSES_DIR = Path(PROJECT_DIR) / "docs" / "staging" / "responses"
GATE_TOKENS_DIR = Path(PROJECT_DIR) / "docs" / "staging" / ".gate_tokens"

# --- Two-way NTFY (inbound command channel) ---
#
# Rich can send a short message from the ntfy app on his phone (the
# built-in publish button -- no staging file needed) for quick questions or
# mid-run steering. Persisted so a watchdog restart doesn't re-relay old
# messages or miss ones sent while the watchdog was briefly down.
NTFY_COMMAND_SINCE_FILE = Path(PROJECT_DIR) / "docs" / "observability" / ".ntfy_command_since.json"

INBOUND_COMMAND_SUFFIX = (
    " [Received via NTFY from Rich's phone -- a short steering message, not "
    "a staged instruction. Reply concisely via NTFY too (python3 -c "
    "\"from background.ntfy_utils import send_ntfy; send_ntfy('<answer>')\" "
    "from the project root) in addition to your normal response -- do NOT "
    "use a raw curl, it won't be recognised as our own message and will be "
    "relayed back as a new inbound command. If this is actually a "
    "substantial multi-step instruction, treat it per the Staging Directory "
    "Protocol instead.]"
)


def generate_gate_token(gate: str) -> str:
    """Create and store a single-use response token for `gate` — mirrors
    background.file_api.generate_gate_token (duplicated, not imported, since
    this script runs standalone via `python3 background/session_watchdog.py`
    and isn't on a package path)."""
    token = secrets.token_urlsafe(16)
    GATE_TOKENS_DIR.mkdir(parents=True, exist_ok=True)
    (GATE_TOKENS_DIR / f"{gate}.token").write_text(token, encoding="utf-8")
    return token


def read_and_clear_response(gate: str) -> dict | None:
    """If Rich has tapped a reply action for `gate` (POST /respond wrote
    docs/staging/responses/<gate>.json), consume and return it. Returns None
    if no response is pending."""
    path = RESPONSES_DIR / f"{gate}.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        path.unlink()
        return None
    path.unlink()
    return data


def _escape_ntfy_action_value(value: str) -> str:
    """ntfy's X-Actions header uses `,` and `;` as field/action separators —
    escape literal backslashes and commas in a field's value (semicolons are
    not expected in our labels/JSON bodies)."""
    return value.replace("\\", "\\\\").replace(",", "\\,")


def _gate_actions_header(gate: str, token: str) -> str:
    """Build the X-Actions header value for a REVIEW_GATE notification: two
    `http` actions (Approve/Hold) that POST a decision + single-use token to
    POST /respond, landing in docs/staging/responses/ for the next autoloop
    cycle to pick up."""
    url = f"{FUNNEL_BASE_URL}/respond"
    decisions = [
        ("Approve, proceed", "Rich approved — proceed autonomously with the plan as discussed."),
        ("Hold", "Rich says hold — do not proceed, wait for further instruction."),
    ]
    actions = []
    for label, decision in decisions:
        body = json.dumps({"gate": gate, "decision": decision, "token": token})
        actions.append(
            f"http, {_escape_ntfy_action_value(label)}, {url}, method=POST, "
            f"headers.Content-Type=application/json, "
            f"body={_escape_ntfy_action_value(body)}, clear=true"
        )
    return "; ".join(actions)


def ntfy_gate(msg: str, gate: str, token: str) -> None:
    """Send a REVIEW_GATE notification with tap-to-reply action buttons (high
    priority + warning tag, same as ntfy(needs_input=True))."""
    send_ntfy(msg, headers={
        "X-Priority": "high",
        "X-Tags": "warning",
        "X-Actions": _gate_actions_header(gate, token),
    })

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
    "Per the Staging Directory Protocol, first check docs/staging/ for any "
    "file not yet in docs/staging/done/ -- staging is pre-approval, action it "
    "now without waiting for confirmation. Only once docs/staging/ is empty, "
    "check docs/instructions/MASTER_BACKLOG.md for the current phase. Proceed "
    "autonomously."
)

# --- Autonomous main loop (between-task continuation) ---
#
# After Claude Code finishes a task and goes idle (sitting at its input
# prompt with nothing further queued), the watchdog nudges it to pick up the
# next item itself — "the missing piece that makes the system fully
# autonomous between sessions" (Rich's instruction). This is separate from
# the crash/usage-limit handling above: the session is healthy and not
# rate-limited, it has simply finished and is waiting for a human prompt
# that, in this autonomous setup, never comes unless Rich is actively
# steering.
#
# AUTOLOOP_IDLE_CHECKS * CHECK_INTERVAL_SECONDS = how long the pane must be
# completely unchanged before it's considered "finished and idle" rather
# than "mid-task, just quiet for a moment" (e.g. a slow test run). 10 minutes
# is conservative — long enough that sending keystrokes won't land in the
# middle of a running command's stdin, and long enough that a "Cogitating"
# extended-thinking stretch with a static spinner (no live elapsed-time
# redraw) doesn't read as a finished/idle session and trigger a
# false-positive autoloop nudge. Previously 5 minutes, raised June 2026 after
# observed false positives during long thinking stretches.
AUTOLOOP_IDLE_CHECKS = 10
MAX_AUTOLOOP_PER_HOUR = 6

# If the visible pane shows either of these, the session needs Rich, not a
# nudge: a REVIEW_GATE is a deliberate stop for human review (per
# CLAUDE.md/MASTER_BACKLOG conventions), and a permission prompt needs a
# human y/n — auto-approving it would defeat the point of never using
# --dangerously-skip-permissions.
#
# KNOWN FALSE POSITIVE (2026-06-13): this plain substring match also fires
# on Claude's own prose when it *reports* a gate it already cleared (e.g.
# "REVIEW_GATE: 4b-5 complete, awaiting Rich's review") — not just on a
# genuine pending stop. Observed back-to-back triggers in
# docs/observability/session-watchdog-log.md around 16:04-16:16 UTC. A
# better check would combine this pattern with the idle-pane check (only
# treat it as a real stop once the pane has also stopped changing for a
# cycle or two), since a genuine REVIEW_GATE stop is by definition idle.
REVIEW_GATE_PATTERN = re.compile(r"REVIEW_GATE", re.IGNORECASE)
PERMISSION_PROMPT_PATTERN = re.compile(
    r"do you want to proceed|\(y/n\)|❯ 1\.", re.IGNORECASE
)

USAGE_PAUSE_THRESHOLD_PCT = 90

USAGE_PAUSE_FILE = Path(f"{PROJECT_DIR}/docs/observability/.usage_pause.json")

# Matches the "Current session" block of `/usage` output, e.g.:
#   Current session · Resets 4:59pm (Europe/London)
#   █████████████████▊
#                                                           33% used
# Captures the reset time, timezone name, and percentage used.
USAGE_PCT_PATTERN = re.compile(
    r"Current session.*?Resets\s+(?P<time>\d{1,2}:\d{2}\s*(?:am|pm))\s*"
    r"\((?P<tz>[^)]+)\).*?(?P<pct>\d{1,3})%\s*used",
    re.IGNORECASE | re.DOTALL,
)

AUTOLOOP_INSTRUCTION = (
    "Per the Staging Directory Protocol, first check docs/staging/ for any "
    "file not yet in docs/staging/done/ -- staging is pre-approval, action it "
    "now without waiting for confirmation, following its own Gate/NTFY "
    "instructions, then move it to docs/staging/done/. Repeat until "
    "docs/staging/ is empty. Only then check docs/instructions/MASTER_BACKLOG.md "
    "for the next incomplete phase or sub-phase and proceed autonomously "
    "following the established REVIEW_GATE/NTFY pattern. If you hit a "
    "REVIEW_GATE or a genuine blocker, stop and state it clearly so Rich can "
    "review."
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
autoloop_times: deque = deque()

# Mutable across main() loop iterations — tracks the autoloop idle
# state-machine. Reset implicitly whenever the pane content changes.
_autoloop_last_pane: str | None = None
_autoloop_idle_streak = 0
_autoloop_waiting_notified = False

# Debounce counter for clearing a gate/permission "waiting" state. A single
# capture where REVIEW_GATE_PATTERN/PERMISSION_PROMPT_PATTERN no longer
# matches isn't enough to conclude the wait is over — tmux's captured
# viewport can shift by a line or two between polls (cursor blink, prompt
# redraw, a status line scrolling the gate text just out of frame) even
# though the session's actual state hasn't changed. Require
# AUTOLOOP_IDLE_CHECKS consecutive non-matching captures before treating the
# wait as resolved, so a momentary capture miss doesn't reset
# _autoloop_waiting_notified and trigger a duplicate notification next time
# the pattern reappears.
_autoloop_gate_clear_streak = 0

# Mutable across main() loop iterations — debounces the "usage pause active"
# log/notify in check_autoloop so it logs once per pause, not every cycle.
_usage_pause_notified = False


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{ts}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry)


def ntfy(msg: str, needs_input: bool = False) -> None:
    """Send an NTFY message.

    needs_input=False (default): "FYI/done" — default priority, checkmark
    tag. needs_input=True: the session is paused waiting on Rich
    (REVIEW_GATE, permission prompt, restart confirmation, etc.) — high
    priority + warning tag, so it stands out on the phone from the routine
    completion pings. See docs/instructions/NTFY_TWO_WAY_PROTOCOL.md.
    """
    priority = "high" if needs_input else "default"
    tags = "warning" if needs_input else "white_check_mark"
    send_ntfy(msg, headers={"X-Priority": priority, "X-Tags": tags})


def session_exists() -> bool:
    return subprocess.run(
        ["tmux", "has-session", "-t", SESSION_NAME],
        capture_output=True,
    ).returncode == 0


def claude_is_running() -> bool:
    # Primary check: is `claude` or `node` the foreground command in the tmux pane?
    result = subprocess.run(
        ["tmux", "list-panes", "-t", SESSION_NAME, "-F", "#{pane_current_command}"],
        capture_output=True, text=True,
    )
    output = result.stdout.lower()
    if "claude" in output or "node" in output:
        return True
    # Fallback: a live `claude` process running outside the tmux pane (e.g. desktop/web app).
    # pgrep -x matches the process name exactly to avoid false positives from scripts.
    pgrep = subprocess.run(["pgrep", "-x", "claude"], capture_output=True)
    return pgrep.returncode == 0


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


def autoloop_sends_in_last_hour() -> int:
    now = time.time()
    while autoloop_times and now - autoloop_times[0] > 3600:
        autoloop_times.popleft()
    return len(autoloop_times)


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


def _load_command_since() -> float:
    """Last-seen timestamp for the inbound NTFY command poller, persisted
    across watchdog restarts. Defaults to "now" on first run, so a fresh
    watchdog doesn't replay the topic's entire history."""
    if NTFY_COMMAND_SINCE_FILE.is_file():
        try:
            return json.loads(NTFY_COMMAND_SINCE_FILE.read_text(encoding="utf-8"))["since"]
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
    return time.time()


def _save_command_since(since: float) -> None:
    NTFY_COMMAND_SINCE_FILE.parent.mkdir(parents=True, exist_ok=True)
    NTFY_COMMAND_SINCE_FILE.write_text(json.dumps({"since": since}), encoding="utf-8")


def _relay_inbound_command(message: str) -> None:
    """Type `message` (plus INBOUND_COMMAND_SUFFIX) into the 'claude' tmux
    session as a new chat input, so Claude picks it up and replies via NTFY
    per the suffix's instruction. Claude Code queues input typed while busy,
    so this is safe whether the session is idle or mid-task."""
    log(f"Inbound NTFY command from Rich: {message!r} — relaying to session")
    subprocess.run([
        "tmux", "send-keys", "-t", SESSION_NAME, message + INBOUND_COMMAND_SUFFIX, "Enter"
    ])


def check_inbound_commands(pane_text: str, since: float) -> float:
    """Poll the NTFY topic for messages posted after `since` that we didn't
    send ourselves (`was_sent_by_us`), and relay each as a new chat input to
    the 'claude' session (see `_relay_inbound_command`).

    If a permission prompt is currently visible, relaying is deferred --
    typing arbitrary text could be misread as a y/n response -- and `since`
    is left at the point just before the first deferred message, so it (and
    anything after it) is retried next cycle once the prompt clears.

    Returns the new watermark to persist via `_save_command_since`.
    """
    try:
        response = requests.get(
            NTFY_POLL_URL, params={"poll": "1", "since": int(since)}, timeout=10,
        )
    except requests.RequestException as e:
        log(f"Inbound command poll error: {e}")
        return since

    latest = since
    for line in response.text.splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue

        if record.get("event") != "message":
            continue
        msg_time = record.get("time", 0)
        if msg_time <= since:
            continue
        if was_sent_by_us(record.get("id")):
            latest = max(latest, msg_time)
            continue

        message = record.get("message", "").strip()
        if not message:
            latest = max(latest, msg_time)
            continue

        if PERMISSION_PROMPT_PATTERN.search(pane_text):
            log("Inbound NTFY command received but a permission prompt is "
                "showing — deferring to next cycle")
            return latest

        if message.strip().lower() == "/usage":
            _handle_usage_command()
        else:
            _relay_inbound_command(message)
        latest = max(latest, msg_time)

    return latest


def _handle_usage_command() -> None:
    """Handle an inbound "/usage" command from Rich's phone directly,
    without relaying it to Claude.

    Relaying "/usage" (the way every other inbound command is relayed, via
    `_relay_inbound_command`) doesn't work: a slash command is only
    recognised when it's the *entire* input, and the relay always appends
    INBOUND_COMMAND_SUFFIX — so Claude received literal text "/usage [...]"
    that it could only guess about, producing exactly the "wildly
    overestimating" answers Rich flagged. Instead, reuse
    `check_session_usage()` (the same standalone-/usage + parse mechanism
    the soft 90% self-pause already relies on) and reply with the real
    figure directly.

    If the dialog doesn't render in time (e.g. the session is mid-task and
    the keystrokes were queued rather than executed), reports that plainly
    rather than a guess.
    """
    usage = check_session_usage()
    if usage is None:
        send_ntfy(
            "Couldn't read /usage just now (session may be mid-task) — try again in a moment."
        )
        return
    pct, reset_time, tz_name = usage
    send_ntfy(f"Usage: {pct}% of current session window used, resets {reset_time} {tz_name}.")


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
               f"({MAX_RESTARTS_PER_HOUR}/hour) — pausing 60 min before resuming.")
        log(msg)
        ntfy(msg, needs_input=True)
        # Sleep before returning so the main loop doesn't immediately re-trigger
        # and spam NTFY with repeated "session ended" messages.
        time.sleep(3600)
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
         "escalating for a manual check.", needs_input=True)
    handle_session_ended()


def parse_usage_pane(pane_text: str) -> tuple[int, str, str] | None:
    """Parse the "Current session" block of `/usage` output from `pane_text`.

    Returns (pct_used, reset_time, tz_name) — e.g. (33, "4:59pm",
    "Europe/London") — or None if the pane doesn't contain a recognisable
    /usage block (e.g. the dialog hasn't rendered yet)."""
    m = USAGE_PCT_PATTERN.search(pane_text)
    if not m:
        return None
    return int(m["pct"]), m["time"].strip(), m["tz"].strip()


def _usage_resume_at(reset_time: str, tz_name: str) -> str:
    """Convert a `/usage` reset time (e.g. "4:59pm") and IANA timezone name
    (e.g. "Europe/London") into a UTC ISO8601 timestamp, assuming the reset
    is the next occurrence of that time (today if still in the future,
    otherwise tomorrow)."""
    tz = ZoneInfo(tz_name)
    now_local = datetime.now(tz)
    reset_t = datetime.strptime(reset_time.lower().replace(" ", ""), "%I:%M%p").time()
    resume_local = datetime.combine(now_local.date(), reset_t, tzinfo=tz)
    if resume_local <= now_local:
        resume_local += timedelta(days=1)
    return resume_local.astimezone(timezone.utc).isoformat()


def check_session_usage() -> tuple[int, str, str] | None:
    """Send a standalone `/usage` command to the session, capture the
    resulting dialog, dismiss it, and parse the "Current session" block.

    Returns (pct_used, reset_time, tz_name), or None if the output couldn't
    be parsed (e.g. the dialog didn't render within the wait — treated as
    "unknown, don't pause" by callers).
    """
    subprocess.run(["tmux", "send-keys", "-t", SESSION_NAME, "/usage", "Enter"])
    time.sleep(2)
    pane_text = capture_pane()
    subprocess.run(["tmux", "send-keys", "-t", SESSION_NAME, "Escape"])
    return parse_usage_pane(pane_text)


def usage_pause_active() -> bool:
    """True if docs/observability/.usage_pause.json exists and its
    "resume_at" timestamp (ISO8601, written by Claude itself per
    USAGE_PAUSE_CHECK_INSTRUCTION) is still in the future.

    A malformed file is logged and removed (treated as "not paused"). Once
    `resume_at` has passed, the file is deleted and an NTFY sent — the next
    autoloop nudge proceeds normally, and its USAGE_PAUSE_CHECK_INSTRUCTION
    prefix will re-check /usage and pause again if still >= threshold.
    """
    if not USAGE_PAUSE_FILE.is_file():
        return False

    try:
        data = json.loads(USAGE_PAUSE_FILE.read_text(encoding="utf-8"))
        resume_at = datetime.fromisoformat(data["resume_at"])
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        log(f"Malformed usage-pause file ({e}) — clearing and resuming autoloop")
        USAGE_PAUSE_FILE.unlink()
        return False

    if resume_at.tzinfo is None:
        resume_at = resume_at.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) < resume_at:
        return True

    log(f"Usage pause window ended (resume_at={data['resume_at']}) — resuming autoloop")
    USAGE_PAUSE_FILE.unlink()
    return False


def check_autoloop(pane_text: str) -> None:
    """Autonomous main-loop nudge — see the "Autonomous main loop" section
    of this module's constants for the rationale.

    State machine over successive calls (one per CHECK_INTERVAL_SECONDS,
    pane content from `capture_pane()`):
      - Pane changed from the previous call: idle streak resets — still
        mid-task. Any prior "waiting on Rich" state is cleared once the pane
        has been changing for AUTOLOOP_IDLE_CHECKS consecutive polls.
      - Pane unchanged for AUTOLOOP_IDLE_CHECKS consecutive calls: a genuine
        stop, not mid-task quiet. Then:
          - REVIEW_GATE or a permission prompt visible: NTFY once (not every
            check) that the session needs Rich, and do nothing further.
          - Otherwise: send AUTOLOOP_INSTRUCTION (subject to
            MAX_AUTOLOOP_PER_HOUR) and NTFY a milestone message.

    REVIEW_GATE_PATTERN/PERMISSION_PROMPT_PATTERN are deliberately only
    checked once the pane is idle. Checking them unconditionally on every
    poll (regardless of pane activity) caused a real incident: Claude's own
    prose routinely *mentions* "REVIEW_GATE" while actively working (e.g.
    discussing a staged instruction's gate requirements), and if that text
    sat in the captured pane tail, the old code treated it as a deliberate
    stop on every single poll — returning early before ever reaching the
    idle/nudge logic. That suppressed AUTOLOOP_INSTRUCTION (and the soft
    90%-usage self-check that used to be prefixed onto it) for hours while
    Claude kept working, until the hard usage-limit path caught it at 100%
    instead of the soft check catching it at 90%. Gating these patterns on
    idle means an actively-changing pane never triggers them.
    """
    global _autoloop_last_pane, _autoloop_idle_streak, _autoloop_waiting_notified
    global _autoloop_gate_clear_streak, _usage_pause_notified

    if usage_pause_active():
        if not _usage_pause_notified:
            log("Usage pause active (docs/observability/.usage_pause.json) — "
                "autoloop continuation suppressed until session reset")
            _usage_pause_notified = True
        return
    _usage_pause_notified = False

    if pane_text != _autoloop_last_pane:
        _autoloop_last_pane = pane_text
        _autoloop_idle_streak = 0
        if _autoloop_waiting_notified:
            _autoloop_gate_clear_streak += 1
            if _autoloop_gate_clear_streak >= AUTOLOOP_IDLE_CHECKS:
                _autoloop_waiting_notified = False
                _autoloop_gate_clear_streak = 0
        return

    _autoloop_idle_streak += 1
    if _autoloop_idle_streak < AUTOLOOP_IDLE_CHECKS:
        return

    _autoloop_gate_clear_streak = 0

    if REVIEW_GATE_PATTERN.search(pane_text):
        response = read_and_clear_response(GATE_ID)
        if response is not None:
            decision = response.get("decision", "")
            log(f"Gate reply received via NTFY action: {decision!r} — relaying to session")
            subprocess.run(["tmux", "send-keys", "-t", SESSION_NAME, decision, "Enter"])
            ntfy(f"Got it — relayed to the session: {decision}")
            _autoloop_waiting_notified = False
            _autoloop_idle_streak = 0
            return

        if not _autoloop_waiting_notified:
            log("REVIEW_GATE visible — waiting for Rich, autoloop paused")
            token = generate_gate_token(GATE_ID)
            ntfy_gate(
                "Claude Code is waiting at a REVIEW_GATE — tap to respond, "
                "or check the session when you have a moment.",
                GATE_ID, token,
            )
            _autoloop_waiting_notified = True
        return

    if PERMISSION_PROMPT_PATTERN.search(pane_text):
        if not _autoloop_waiting_notified:
            log("Permission prompt visible — waiting for Rich, autoloop paused")
            ntfy("Claude Code is waiting on a permission prompt — check the "
                 "session when you have a moment.", needs_input=True)
            _autoloop_waiting_notified = True
        return

    _autoloop_idle_streak = 0

    if autoloop_sends_in_last_hour() >= MAX_AUTOLOOP_PER_HOUR:
        if not _autoloop_waiting_notified:
            log(f"Autoloop cap reached ({MAX_AUTOLOOP_PER_HOUR}/hour) — pausing")
            ntfy(f"Claude Code autoloop cap reached ({MAX_AUTOLOOP_PER_HOUR}/hour) "
                 "— pausing autonomous continuation, check the session.", needs_input=True)
            _autoloop_waiting_notified = True
        return

    usage = check_session_usage()
    if usage is not None:
        pct, reset_time, tz_name = usage
        if pct >= USAGE_PAUSE_THRESHOLD_PCT:
            resume_at = _usage_resume_at(reset_time, tz_name)
            USAGE_PAUSE_FILE.parent.mkdir(parents=True, exist_ok=True)
            USAGE_PAUSE_FILE.write_text(
                json.dumps({"resume_at": resume_at}), encoding="utf-8"
            )
            log(f"Session usage at {pct}% (>= {USAGE_PAUSE_THRESHOLD_PCT}%) — "
                f"writing usage pause until {resume_at}, holding off the "
                "autoloop nudge this cycle")
            _autoloop_waiting_notified = False
            _autoloop_idle_streak = 0
            return

    _autoloop_waiting_notified = False
    log("Session idle — sending autoloop continuation instruction")
    subprocess.run(["tmux", "send-keys", "-t", SESSION_NAME, AUTOLOOP_INSTRUCTION, "Enter"])
    autoloop_times.append(time.time())


def handle_session_ended() -> None:
    alert_time = time.time()
    log("Claude Code session ended — sending restart-confirmation request")
    ntfy("Claude Code session ended — reply YES to this notification to restart.", needs_input=True)

    confirmed = wait_for_restart_confirmation(alert_time)
    if not confirmed:
        log("Confirmation window expired (4h) — no restart. Resuming monitoring.")
        ntfy("Session watchdog: no restart confirmation received within 4 hours — "
              "session left stopped.", needs_input=True)
        return

    log("Restart confirmation ('YES') received")
    restart_claude()


def main() -> None:
    log("Session watchdog started (gated mode — restarts require NTFY YES "
        "confirmation, except usage-limit auto-resume); autoloop active "
        f"(idle {AUTOLOOP_IDLE_CHECKS * CHECK_INTERVAL_SECONDS}s -> continue, "
        "REVIEW_GATE/permission prompts pause for Rich)")
    ntfy(f"Session watchdog started — autoloop active, crash restarts need YES (max {MAX_RESTARTS_PER_HOUR}/hr).")
    update_agent_status(
        "session-watchdog", status="running",
        last_action="Watchdog started",
        role="Monitors Claude Code session; sends autoloop pings; handles REVIEW_GATE",
        produces="docs/observability/session-watchdog-log.md, tmux autoloop pings",
    )
    consecutive_down = 0
    command_since = _load_command_since()

    while True:
        time.sleep(CHECK_INTERVAL_SECONDS)
        try:
            if not session_exists() or not claude_is_running():
                consecutive_down += 1
                log(f"Claude Code not detected (check {consecutive_down}/2)")
                update_agent_status("session-watchdog", status="idle",
                                    last_action=f"CC not detected (check {consecutive_down}/2)")
                if consecutive_down >= 2:
                    handle_session_ended()
                    consecutive_down = 0
                continue

            consecutive_down = 0
            update_agent_status("session-watchdog", status="idle", last_action="Session alive check passed")
            pane_text = capture_pane()

            new_command_since = check_inbound_commands(pane_text, command_since)
            if new_command_since != command_since:
                command_since = new_command_since
                _save_command_since(command_since)

            if usage_limit_detected(pane_text):
                handle_usage_limit()
                continue

            check_autoloop(pane_text)
        except Exception as e:
            log(f"Watchdog error: {e}")


if __name__ == "__main__":
    main()
