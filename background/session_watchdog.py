#!/usr/bin/env python3
"""Claude Code session watchdog — gated restart, no auto-restart without
human confirmation (except usage-limit auto-resume, see below).

Monitors the 'claude' tmux session. When Claude Code is no longer running
(token limit, crash, or completion):
  1. Sends an NTFY alert asking Rich to reply "YES" to restart.
  2. Polls the shared NTFY topic (SE_NTFY_TOPIC, see ntfy_utils.py) every 60
     seconds for up to 4 hours, looking for a reply containing "YES".
  3. If "YES" is seen (and the restart cap below isn't exceeded), restarts
     the 'claude' tmux session with `--dangerously-skip-permissions` (Rich's
     direct, live confirmation, 2026-07-05 -- see
     docs/review_gates/SKIP_PERMISSIONS_TIER1.md for the full timeline).
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
process needs restarting (`restart_claude(resume=True)`, resuming the
DEDICATED worker session WORKER_SESSION_ID -- never `claude -c`, which would
latch the director's console conversation -- with --dangerously-skip-permissions per
the 2026-07-05 confirmation above). If USAGE_LIMIT_MAX_WAIT_SECONDS passes with
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

PROACTIVE USAGE PAUSE — RETIRED (2026-07-15, pull-loop migration): the soft
self-checkpointing pause drove a standalone `/usage` slash-command KEYSTROKE
into the pane once per idle cycle (check_session_usage/parse_usage_pane), then
wrote docs/observability/.usage_pause.json at >= 90%. /usage polling is
eliminated (DIRECTOR_ANSWERS_C7 #3) and NOTHING may type into the pane, so all
three functions are deleted. The HARD usage-limit path above (reactive,
read-only detection via usage_limit_detected on the pane capture -> process-
level handle_usage_limit) remains as the tripwire. usage_pause_active() still
reads/expires the pause file the SESSION itself writes (read-only here).

TURN-GRANTING was never this function's job (retired 2026-07-09, doorbell
failure #4). PULL-LOOP MIGRATION (2026-07-15): check_autoloop() no longer
types ANYTHING into the pane at all — the REVIEW_GATE-reply relay is deleted
(the director answers a gate at his own console; the machine never types his
decision back in). What remains is read-only idle detection + a NOTIFY so the
director knows the console wants him. Turn delivery is the pull-loop Stop
hook's job (.claude/hooks/pull_next_work.py).

KNOWN LIMITATION — "verified sender": even after the 2026-07-08 topic
rotation to a secret value (docs/staging/NTFY_CHANNEL_HARDENING.md), ntfy.sh
topics are unauthenticated by design -- knowing the topic name is sufficient
to publish. There is no cryptographic way to verify who posted a "YES" reply
(or, as of 2026-07-05, a claimed skip-permissions confirmation -- one such
message was received and independently identified as unreliable: it
asserted something demonstrably false about the running system, see
docs/review_gates/SKIP_PERMISSIONS_TIER1.md). Since restart now runs with
--dangerously-skip-permissions, a spoofed "YES" reply on this channel would
bring back a fully unattended, no-prompt session -- a materially
higher-stakes failure mode than before this change. This tradeoff was made
deliberately, with that risk stated plainly, not overlooked -- the topic
rotation raises the bar (no longer publishable by anyone who reads the
public repo) but does not eliminate this limitation, which is why the
authentication convention (CLAUDE.md: only a live in-conversation turn or
Rich clearing a gate file himself authorizes safety-control changes) exists
as the real control, not the topic secrecy alone.

Logs to docs/observability/session-watchdog-log.md.
"""

import glob
import json
import os
import re
import secrets
import signal
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
from background.ntfy_utils import (  # noqa: E402
    NTFY_AUTH_TOKEN,
    NTFY_TOPIC,
    send_ntfy,
    was_sent_by_us,
)
from background.agent_status import update_agent_status  # noqa: E402
# PULL-LOOP MIGRATION (2026-07-15, STAGING_PULL_LOOP_RESCOPE.md + DIRECTOR_
# ANSWERS_C7.md): the watchdog is now PROCESS-LEVEL ONLY. It may SPAWN/RESTART a
# DEAD session (tmux new-session / launching a claude process -- a process op,
# kept) but it may NEVER type keystrokes into a LIVE one. Every send_keys /
# send_keys_when_idle / read_slash_dialog_when_idle import is deleted along with
# the inbound-NTFY relay, the REVIEW_GATE reply relay, the usage-limit in-place
# resume nudge, and the /usage slash-command polling. Inbound human steering
# reaches the session via STAGING (ntfy_responder writes from_rich_*.md) + the
# pull-loop draw; the pane is the director's console only.
from background.health_check import run_health_check  # noqa: E402
from background import console_sanctity  # noqa: E402  (G-L1 console-sanctity marker)

SESSION_NAME = "claude"
PROJECT_DIR = "/home/rich/synthetic-enterprise"
# 2026-07-13, director-decided live in-console: every judgment failure this
# weekend was a MAIN-SESSION failure (map "exhausted" misread, a tautological
# self-refill draw, tree-safety conflated with serialism) while the BUILD
# agents (interface-steward/saas-engineer/sim-engineer, per MODEL_SELECTION_
# POLICY.md) were already on Opus. The main interactive session -- the one
# actually doing FRAME/DISCOVER-tier judgment work, epoch framing, and
# root-cause diagnosis -- was still on Sonnet. Switched to match: same model
# ID as background/director_twin.py::TWIN_MODEL, for the same reason (the
# work this session actually does is judgment-tier, not volume-tier).
MAIN_SESSION_MODEL = "claude-opus-4-8"

# Dedicated autonomous-worker conversation id. The worker is ALWAYS launched/resumed
# against THIS specific id -- never `claude -c` (continue-most-recent). `-c` resumes
# whatever conversation was newest, which during a supervised bring-up is the DIRECTOR'S
# live console conversation: on 2026-07-17 the cold-start worker came up as a clone of the
# director's supervision session (same context, would double-act). Resuming a fixed,
# dedicated id makes that structurally impossible. Stored as a readable repo constant
# (mandate 5312e043/0d53fe55: behaviour-determining state lives in the readable repo, so
# the system is reconstructable on a fresh machine -- where this id simply doesn't exist
# yet, so first launch CREATES it via --session-id and every restart RESUMES it).
WORKER_SESSION_ID = "22080be5-e19e-4099-a007-d71c3a6e7845"
CHECK_INTERVAL_SECONDS = 60
CONFIRM_POLL_INTERVAL_SECONDS = 60
CONFIRM_TIMEOUT_SECONDS = 4 * 3600  # 4 hours
MAX_RESTARTS_PER_HOUR = 3
# Post-restart DEGRADED page is debounced + rate-limited (2026-07-16): during a
# restart storm the daemon-health page must not fire on every restart, and a
# TRANSIENT post-respawn race (old process still terminating -> momentarily two
# interactive sessions -> "MULTIPLE sessions") must not page at all. Re-check after
# this delay and page only PERSISTENT problems, at most once per cooldown.
DEGRADED_RECHECK_DELAY_SECONDS = 12
DEGRADED_NTFY_COOLDOWN_SECONDS = 60 * 60
_last_degraded_ntfy_at = 0.0
USAGE_LIMIT_POLL_INTERVAL_SECONDS = 15 * 60  # 15 minutes
USAGE_LIMIT_MAX_WAIT_SECONDS = 6 * 3600  # 6 hours — covers the 5h session limit with margin
# NTFY_TOPIC now sourced from ntfy_utils (single source of truth, itself
# reading the secret SE_NTFY_TOPIC env var -- 2026-07-08 rotation,
# docs/staging/NTFY_CHANNEL_HARDENING.md). This used to be a second
# hardcoded copy of the topic name here; removed to close that duplication.

# API connectivity check — run before any CC restart attempt.
# WSL2 can silently lose its virtual network adapter (Windows power events,
# driver updates), dropping the outbound route to api.anthropic.com without
# killing the tmux session. Without this check, the watchdog loops at its
# MAX_RESTARTS_PER_HOUR cap indefinitely — pausing an hour between batches of
# 3 failed restarts rather than waiting for the network to come back.
API_HEALTH_CHECK_URL = "https://api.anthropic.com"
# Exponential backoff delays before each successive connectivity retry.
# After the sequence is exhausted, retries continue every API_DOWN_STEADY_INTERVAL_SECONDS.
API_DOWN_BACKOFF_SECONDS = [60, 120, 300]   # 1min, 2min, 5min
API_DOWN_STEADY_INTERVAL_SECONDS = 600       # 10min indefinitely
API_DOWN_NTFY_INTERVAL_SECONDS = 3600        # NTFY every hour while still down
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
    "Session resuming after crash or usage-limit reset. Run this recovery "
    "checklist in order before doing anything else:\n\n"
    "1. GIT STATUS: run `git status` and `git diff --stat HEAD`. If there are "
    "uncommitted changes, determine which phase they belong to and whether the "
    "work is complete or mid-flight.\n\n"
    "2. COMPLETE CHECKS on any in-progress work: run "
    "`python3 -m tools.epistemic_verifier` (must PASS before any commit). "
    "Run `SIM_FAST_MODE=1 python3 -m pytest tests/ -x -q --tb=short "
    "--ignore=tests/simulation/test_run_phase2b.py "
    "--ignore=tests/simulation/test_run_phase2b_event_log.py "
    "--ignore=tests/simulation/test_run_phase4c_on_phase2b.py "
    "--ignore=tests/simulation/test_phase40a_pass_through.py "
    "--ignore=tests/simulation/test_phase40b_gas_pass_through.py "
    "--ignore=tests/simulation/test_phase40c_deemed_rate.py "
    "--ignore=tests/simulation/test_phase41a_flex.py "
    "--ignore=tests/simulation/test_phase24a_ic_customer.py` "
    "to confirm tests pass.\n\n"
    "3. FIX ROOT CAUSES: if the verifier or tests fail, fix the violations "
    "before committing — do not advance the project until checks pass.\n\n"
    "4. COMMIT any completed in-progress work with a clear message.\n\n"
    "5. CHECK docs/staging/ for any file not yet in docs/staging/done/ — "
    "staging is pre-approval, action immediately without waiting for "
    "confirmation.\n\n"
    "6. ADVANCE THE PROJECT: once staging is clear and all checks pass, draw "
    "the next work from the current priority authority — docs/PRIORITIES.md (the "
    "sole ranked queue, P-1) and the maturity-map self-refill draw "
    "(background/supervisor.py::find_work) — NOT the retired MASTER_BACKLOG.md. "
    "Proceed autonomously; do not wait for confirmation. NTFY Rich only on a real "
    "transition/blocker (R5), not as a routine start ping."
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
# false-positive nudge. Previously 5 minutes, raised June 2026 after
# observed false positives during long thinking stretches. Still used to
# gate REVIEW_GATE-reply relay and permission-prompt detection below
# (turn-granting for open work is background/supervisor.py's job now).
AUTOLOOP_IDLE_CHECKS = 10

# If the visible pane shows either of these, the session needs Rich, not a
# nudge: a REVIEW_GATE is a deliberate stop for human review (per
# CLAUDE.md/MASTER_BACKLOG conventions). Watchdog-launched sessions run with
# --dangerously-skip-permissions (2026-07-05), so this pattern shouldn't
# normally fire from that path -- kept as defence in depth (e.g. a manually
# started session without the flag, or an unexpected prompt type).
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

# Indicates CC exited so fast that RESUME_INSTRUCTION ran as shell commands.
# Pattern: -sh: N: N.: not found (numbered list items treated as shell commands)
_QUICK_EXIT_PATTERN = re.compile(r"-sh:\s*\d+:\s*\d+\.\s*:\s*not found")
_CRASH_SIGNALS = re.compile(
    r"(Traceback|Error:|fatal:|Killed|Segmentation fault|SIGSEGV)",
    re.IGNORECASE,
)
_last_exit_ntfy_state: str | None = None

# Debounces the "claude binary not found" NTFY in restart_claude() so a
# persistently broken nvm install doesn't send a fresh NTFY every time the
# main loop notices the session is still down (R5: NTFYs fire on state
# transitions only, never repeat an unchanged status). Reset to False once
# the binary resolves again, so recovery is reported too.
_binary_missing_ntfy_sent = False


def classify_exit(pane_text: str) -> tuple[str, str]:
    """Classify why the session ended from pane content.
    Returns (reason, detail).
    reason: usage_limit | quick_exit | crash | completion | unknown
    quick_exit: CC exited immediately on startup (RESUME_INSTRUCTION ran as shell cmds)
    """
    if usage_limit_detected(pane_text):
        return "usage_limit", ""
    if _QUICK_EXIT_PATTERN.search(pane_text):
        return "quick_exit", "CC exited before accepting input (likely usage/rate limit)"
    tail_lines = [l.strip() for l in pane_text.splitlines()[-10:] if l.strip()]
    tail = " | ".join(tail_lines[-5:])
    if _CRASH_SIGNALS.search("\n".join(tail_lines)):
        return "crash", tail[:200]
    return "completion", tail[:100]

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

# Mutable across main() loop iterations — tracks the idle state-machine
# that gates REVIEW_GATE-reply relay and permission-prompt detection.
# Reset implicitly whenever the pane content changes.
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


def interactive_claude_pids() -> list[int]:
    """PIDs of INTERACTIVE main Claude Code sessions -- the auto-resumed pane process
    (`claude --dangerously-skip-permissions ... -c <resume>`), EXCLUDING headless
    `claude -p` build-executor turns and node/MCP helpers. The single-session invariant
    keys on the PROCESS, not the tmux session: a Jul-15 crash-recovery ghost survived a
    FULL DAY (spamming the director every gate cycle) because session_exists() checks the
    tmux SESSION, and kill-session leaves an orphaned claude PROCESS alive (2026-07-16)."""
    from pathlib import Path as _P
    pids: list[int] = []
    for entry in _P("/proc").iterdir() if _P("/proc").is_dir() else []:
        if not entry.name.isdigit():
            continue
        try:
            argv = (entry / "cmdline").read_bytes().split(b"\x00")
        except OSError:
            continue
        argv = [a.decode("utf-8", "replace") for a in argv if a]
        if not argv:
            continue
        # argv[0] must BE the claude binary -- excludes the `tmux new-session ... claude`
        # LAUNCHER (argv[0]=="tmux") that merely mentions claude in its args, which was
        # false-counted as a second session (2026-07-16 mis-page "MULTIPLE sessions").
        exe = argv[0].rsplit("/", 1)[-1]
        if exe not in ("claude", "node") or not exe:
            continue
        joined = " ".join(argv)
        if "--dangerously-skip-permissions" not in joined:
            continue  # not a launched Claude Code session
        if "-p" in argv or "--print" in argv:
            continue  # a headless build-executor turn, not an interactive session
        pids.append(int(entry.name))
    return pids


def _live_tmux_pane_pids() -> set[int]:
    """Every pid that is the foreground process of a LIVE tmux pane, across ALL
    sessions (not just the watchdog's own SESSION_NAME). Used to tell an orphaned
    GHOST (its tmux session was killed, no pane backs it any more -> reap) from a
    genuinely-live session the director is using (managed OR a console `tmux
    new-session` + claude he typed himself -> NEVER touch it). Empty set if tmux
    is unreachable -- which makes reap fail SAFE (see reap_orphan_...)."""
    result = subprocess.run(
        ["tmux", "list-panes", "-a", "-F", "#{pane_pid}"],
        capture_output=True, text=True,
    )
    if getattr(result, "returncode", 1) != 0:
        return set()
    pids: set[int] = set()
    for line in (getattr(result, "stdout", "") or "").split():
        try:
            pids.add(int(line))
        except ValueError:
            pass
    return pids


def _ppid_of(pid: int) -> int | None:
    """Parent pid of `pid` from /proc/<pid>/status, or None if unreadable."""
    try:
        for line in (Path("/proc") / str(pid) / "status").read_text().splitlines():
            if line.startswith("PPid:"):
                return int(line.split()[1])
    except (OSError, ValueError, IndexError):
        pass
    return None


def _is_backed_by_live_pane(pid: int, pane_pids: set[int], _max_hops: int = 32) -> bool:
    """True if `pid` (or any ancestor within _max_hops) is a live tmux pane process.
    Our daemon/console sessions launch `claude` as the pane command directly, so
    pane_pid == the claude pid in the common case; the ancestor walk covers a
    shell-wrapped launch too. An orphaned ghost traces up to pid 1/0, never a pane."""
    cur: int | None = pid
    for _ in range(_max_hops):
        if cur is None or cur <= 1:
            return False
        if cur in pane_pids:
            return True
        cur = _ppid_of(cur)
    return False


def reap_orphan_interactive_claude(exclude: set[int] | None = None) -> list[int]:
    """SIGTERM only ORPHANED interactive Claude session processes -- a ghost whose
    tmux session was killed but whose `claude` PROCESS survived (how the Jul-15
    ghost spammed the director for a full day). Called on the respawn path so the
    singleton invariant covers the crash-recovery / usage-reset route.

    NEVER kills a session the director is actually using. Two INDEPENDENT reasons
    to spare, checked in order; a pid is reaped only if BOTH fail to protect it:
      1. G-L1 CONSOLE SANCTITY (positive, tmux-independent): a pid registered in
         the console-sanctity marker (`console_sanctity.is_sanctified`) is spared
         unconditionally -- the check reads only /proc + the registry file, so it
         holds even when tmux is unreachable, the exact gap the old inference-only
         exemption could not cover (the blackout's exit-143 console kill).
      2. LIVE TMUX PANE (inference, retained as a redundant belt): a process
         backed by a live tmux pane is spared. Kept until every console-launch
         path registers via the sanctioned launcher (background/console.sh);
         retiring it before then would risk the very console-kill G-L1 prevents.

    Returns the reaped pids. Fails SAFE: for a NON-sanctified pid, if tmux is
    unreachable (empty pane set) we cannot prove it is a ghost, so we do not reap
    it -- a lingering ghost is far less harmful than killing a live session."""
    exclude = exclude or set()
    pane_pids = _live_tmux_pane_pids()
    reaped: list[int] = []
    spared_sanctified: list[int] = []
    spared_live: list[int] = []
    for pid in interactive_claude_pids():
        if pid in exclude or pid == os.getpid():
            continue
        # (1) G-L1: sanctified console -- never reaped, independent of tmux.
        if console_sanctity.is_sanctified(pid):
            spared_sanctified.append(pid)
            continue
        # (2) fail-safe: without the pane list we cannot prove a ghost -> do not reap.
        if not pane_pids:
            spared_live.append(pid)
            continue
        # (2) inference belt: a live pane-backed session is spared.
        if _is_backed_by_live_pane(pid, pane_pids):
            spared_live.append(pid)
            continue
        try:
            os.kill(pid, signal.SIGTERM)
            reaped.append(pid)
        except OSError:
            pass
    _sanct = f"; spared {len(spared_sanctified)} SANCTIFIED console(s): {spared_sanctified}" if spared_sanctified else ""
    _live = f"; spared {len(spared_live)} pane-backed/fail-safe session(s): {spared_live}" if spared_live else ""
    if reaped:
        log(f"Reaped {len(reaped)} ORPHAN interactive-claude ghost(s) on respawn: {reaped}"
            + _sanct + _live + " (singleton invariant; sanctified consoles never killed)")
    elif spared_sanctified or spared_live:
        log(f"Reap found no orphans{_sanct}{_live}")
    return reaped


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
    _auth = {"Authorization": f"Bearer {NTFY_AUTH_TOKEN}"} if NTFY_AUTH_TOKEN else {}
    try:
        response = requests.get(
            NTFY_POLL_URL,
            params={"poll": "1", "since": int(since)},
            headers=_auth,
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


def check_api_reachable() -> bool:
    """Return True if api.anthropic.com responds to an HTTP request (any status
    code), False if the connection is refused or times out."""
    try:
        requests.get(API_HEALTH_CHECK_URL, timeout=10)
        return True
    except requests.RequestException:
        return False


def wait_for_api_connectivity() -> None:
    """Block until api.anthropic.com is reachable, using exponential backoff.

    Sequence: 1min → 2min → 5min → then every 10min indefinitely.
    NTFYs Rich on first failure and every hour it stays down.
    Never gives up — returns only when the API is reachable again.
    """
    if check_api_reachable():
        return  # common path — no delays

    down_since = datetime.now(timezone.utc)
    down_since_str = down_since.strftime("%H:%M UTC")
    msg = f"CC down — API unreachable since {down_since_str}, retrying with backoff (1m/2m/5m/10m)"
    log(msg)
    ntfy(msg, needs_input=True)
    last_ntfy_time = time.time()
    attempt = 0

    while True:
        if attempt < len(API_DOWN_BACKOFF_SECONDS):
            sleep_secs = API_DOWN_BACKOFF_SECONDS[attempt]
        else:
            sleep_secs = API_DOWN_STEADY_INTERVAL_SECONDS
        attempt += 1
        log(f"API unreachable — waiting {sleep_secs}s before retry #{attempt}")
        time.sleep(sleep_secs)

        if check_api_reachable():
            elapsed_min = int((time.time() - down_since.timestamp()) / 60)
            log(f"API connectivity restored after {elapsed_min}min — proceeding")
            ntfy(f"API connectivity restored after {elapsed_min}min — restarting Claude Code.")
            return

        if time.time() - last_ntfy_time >= API_DOWN_NTFY_INTERVAL_SECONDS:
            elapsed_min = int((time.time() - down_since.timestamp()) / 60)
            msg = (f"CC still down — API unreachable for {elapsed_min}min "
                   f"(since {down_since_str}), retrying every 10min")
            log(msg)
            ntfy(msg, needs_input=True)
            last_ntfy_time = time.time()


CLAUDE_LAUNCH_TIMEOUT_SECONDS = 60
CLAUDE_LAUNCH_POLL_INTERVAL_SECONDS = 2

# See WATCHDOG_NO_SENDKEYS.md (2026-07-04): `bash -lc 'which claude'` returns
# EMPTY on this machine -- nvm only initialises PATH in an INTERACTIVE shell
# (its .bashrc guard exits early for non-interactive shells), so the previous
# `bash -l` launch shell never actually had `claude` on PATH. Resolve the
# absolute binary path directly from the nvm install tree instead.
CLAUDE_NVM_GLOB = str(Path.home() / ".nvm" / "versions" / "node" / "*" / "bin" / "claude")


def resolve_claude_binary() -> str | None:
    """Resolve the absolute path to the `claude` binary via its nvm install
    location, or None if not found.

    Re-resolved on every call (not cached) so a node version upgrade that
    moves the install path doesn't strand the watchdog on a stale one. If
    more than one version is installed, picks the lexicographically last
    match (highest version number, since nvm dirs are named `vX.Y.Z`).
    """
    matches = sorted(glob.glob(CLAUDE_NVM_GLOB))
    return matches[-1] if matches else None


def wait_for_claude_launch(timeout_seconds: int = CLAUDE_LAUNCH_TIMEOUT_SECONDS) -> bool:
    """Poll the freshly-launched pane until `claude_is_running()` is true, or
    `timeout_seconds` elapses.

    Replaces a fixed `time.sleep(15)` guess with an actual check of the
    pane's foreground command -- see WATCHDOG_LAUNCH_RACE.md (2026-07-04):
    the previous fixed sleep sent RESUME_INSTRUCTION regardless of whether
    `claude` had actually started, so on a slow or failed launch the
    instruction's numbered list landed in a bare shell and was executed line
    by line as shell commands (`-sh: 2: Session: not found`, etc.), which
    then looped through the restart cap without ever surfacing the real
    launch failure.
    """
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if claude_is_running():
            return True
        time.sleep(CLAUDE_LAUNCH_POLL_INTERVAL_SECONDS)
    return claude_is_running()


def _worker_session_exists() -> bool:
    """True if the dedicated worker conversation (WORKER_SESSION_ID) already exists
    on this machine, so we RESUME it rather than trying to CREATE it again. The id is
    unique, so scanning every project dir is unambiguous (avoids reproducing Claude
    Code's cwd path-mangling here). Missing dir / unreadable -> False (fresh create)."""
    base = Path.home() / ".claude" / "projects"
    try:
        if not base.is_dir():
            return False
        for d in base.iterdir():
            if (d / f"{WORKER_SESSION_ID}.jsonl").exists():
                return True
    except OSError:
        pass
    return False


def _worker_claude_argv(claude_bin: str) -> list[str]:
    """The claude launch argv for the autonomous worker -- targeting the dedicated
    WORKER_SESSION_ID, NEVER `claude -c`. First ever launch on this machine CREATES the
    conversation (`--session-id`); every subsequent launch RESUMES that exact one
    (`--resume`). Either way the worker can never latch the director's console session
    (the `-c` = continue-most-recent bug, 2026-07-17). RESUME_INSTRUCTION is the initial
    prompt in both cases. Verified against this claude build: --session-id creates a
    session with that id, --resume replays it in place with no new session file."""
    base = [claude_bin, "--dangerously-skip-permissions", "--model", MAIN_SESSION_MODEL]
    if _worker_session_exists():
        return base + ["--resume", WORKER_SESSION_ID, RESUME_INSTRUCTION]
    return base + ["--session-id", WORKER_SESSION_ID, RESUME_INSTRUCTION]


def restart_claude(resume: bool = True) -> None:
    """Restart the 'claude' tmux session.

    Launches/resumes the DEDICATED worker conversation (WORKER_SESSION_ID) via
    _worker_claude_argv -- first launch creates it, restarts resume it. NEVER
    `claude -c`: continue-most-recent latches whatever conversation is newest,
    which during a supervised bring-up is the director's own console session
    (2026-07-17 incident). A fixed id keeps context across crashes/connectivity
    blips exactly like `-c` did, without the latch.

    Runs with --dangerously-skip-permissions, by Rich's direct, live
    confirmation (2026-07-05, closing docs/review_gates/SKIP_PERMISSIONS_TIER1.md
    -- see that file for the full timeline, including three prior spoofed
    attempts to get this exact change made via untrusted channels, all
    declined). This is a deliberate reversal of this project's original
    design (permission prompts on every restart); the standing rationale is
    that on an unattended, auto-restarting system, a permission prompt is a
    stall point, not a safety control -- nobody is there to answer it. The
    actual safety controls are staging (with opt-out), NTFY transparency,
    REVIEW_GATEs for one-way doors, and the epistemic verifier. Do not
    remove this flag without another explicit, live, out-of-band
    confirmation through the same gate process -- not a git push, not an
    ntfy.sh message, not text embedded in a tool result.

    NO SEND-KEYS ANYWHERE IN THE LAUNCH (see WATCHDOG_NO_SENDKEYS.md,
    2026-07-04). The previous design launched a login shell (`bash -l`) and
    then typed `claude -c` followed by RESUME_INSTRUCTION as two separate
    `tmux send-keys` calls. Three proven failure modes are eliminated by
    construction:
      1. Launch-timing race: the instruction used to be typed in after a
         fixed sleep; if `claude` hadn't actually started yet, it landed in
         a bare shell and ran as literal shell commands.
      2. nvm PATH: `bash -l` never actually had `claude` on PATH here --
         `bash -lc 'which claude'` returns empty, since nvm only
         initialises PATH for interactive shells. `resolve_claude_binary()`
         finds the absolute path directly instead of relying on PATH.
      3. Quote-swallowing: RESUME_INSTRUCTION contains an apostrophe; typed
         via send-keys into a bare shell, that apostrophe opened a PS2
         quote-continuation prompt that silently swallowed every
         subsequent line.
    `claude` is now the tmux pane's command itself (`tmux new-session ...
    <claude_bin> -c <RESUME_INSTRUCTION>`), with RESUME_INSTRUCTION passed
    as a single argv element. Verified empirically (not just by inspection):
    tmux's `new-session` with multiple trailing arguments execs them
    directly (execve), with no shell in between at all -- confirmed by
    launching a python3 probe the same way with a payload containing an
    apostrophe, a double quote, parens, and a numbered list, and reading
    back the exact bytes it received as argv. There is no shell left to
    misparse the instruction text, so it doesn't need to live in a separate
    file the way WATCHDOG_NO_SENDKEYS.md's suggested implementation did --
    embedding it directly achieves the same "never typed into a shell"
    guarantee with no extra file to keep in sync.
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

    wait_for_api_connectivity()

    global _binary_missing_ntfy_sent
    claude_bin = resolve_claude_binary()
    if claude_bin is None:
        msg = (f"Claude binary not found under {CLAUDE_NVM_GLOB} -- cannot "
               "restart. Check the nvm install.")
        log(msg)
        if not _binary_missing_ntfy_sent:
            ntfy(msg, needs_input=True)
            _binary_missing_ntfy_sent = True
        restart_times.append(time.time())
        return
    _binary_missing_ntfy_sent = False

    _mode = "resume" if _worker_session_exists() else "create"
    log(f"Restarting Claude Code (--dangerously-skip-permissions per "
        f"2026-07-05 director confirmation, direct launch via {claude_bin}, "
        f"dedicated worker session {WORKER_SESSION_ID} [{_mode}], no `claude -c`, "
        f"no send-keys, DISABLE_AUTOUPDATER=1)")
    subprocess.run(["tmux", "kill-session", "-t", SESSION_NAME], capture_output=True)
    # Singleton on the RESPAWN path (2026-07-16): kill-session removes the tmux session
    # but can leave an orphaned claude PROCESS alive (how the Jul-15 ghost survived a
    # day). Reap any interactive-claude orphan before spawning the replacement, so at
    # most one interactive session ever exists.
    reap_orphan_interactive_claude()
    time.sleep(5)

    # DISABLE_AUTOUPDATER=1 (2026-07-08, Rich's direct instruction): the npm
    # global install here isn't writable, so claude's background auto-update
    # check fails every launch (harmless, but noise) and can't actually
    # update anything -- pointless to attempt on every unattended restart.
    # Set via tmux's -e (session-scoped env, supported tmux >=3.2) rather than
    # this script's own os.environ, so it applies only to the spawned Claude
    # Code session, not to session_watchdog.py itself or anything else it
    # launches. Sanctioned update path is now manual -- see MAINTENANCE.md.
    subprocess.run(
        ["tmux", "new-session", "-d", "-s", SESSION_NAME, "-c", PROJECT_DIR,
         "-e", "DISABLE_AUTOUPDATER=1"]
        + _worker_claude_argv(claude_bin)
    )

    if not wait_for_claude_launch():
        pane_text = capture_pane()
        last_lines = " | ".join(
            ln.strip() for ln in pane_text.splitlines()[-30:] if ln.strip()
        )
        log(f"Claude Code did not come up within {CLAUDE_LAUNCH_TIMEOUT_SECONDS}s of "
            f"launch — pane: {last_lines[:800]}")
        ntfy(
            f"CC failed to launch (still not running {CLAUDE_LAUNCH_TIMEOUT_SECONDS}s "
            f"after direct launch) — pane: {last_lines[:500]}",
            needs_input=True,
        )
        # Count against the restart cap so a persistently broken launch backs
        # off (60min pause) instead of retrying every cycle indefinitely.
        # One alert, no retry loop -- the next `main()` cycle will notice the
        # session is still down and call restart_claude() again on its own
        # schedule; this function does not loop internally.
        restart_times.append(time.time())
        return

    restart_times.append(time.time())
    count = restarts_in_last_hour()
    log(f"Claude Code restarted ({count}/{MAX_RESTARTS_PER_HOUR} this hour, "
        f"direct launch, dedicated worker session {WORKER_SESSION_ID}, no send-keys)")
    _verify_daemon_set_after_restart()


def _verify_daemon_set_after_restart() -> None:
    """Daemon-liveness startup invariant (2026-07-13, director-requested
    live in-console: "after any session restart, verify the full daemon
    set and alarm if any are missing"). A tmux `kill-session`/`new-session`
    cycle only ever touches the `claude` session itself -- every OTHER
    daemon (supervisor, staging-watcher, sanity-daemon, etc.) lives in its
    own separate tmux session and is untouched by this restart -- but
    "should be unaffected" is exactly the kind of claim MAKE_IT_STICK says
    must be a mechanism, not a remembered assumption: if the underlying
    event that killed the `claude` session (a host reboot, an OOM kill, a
    manual `tmux kill-server`) took other sessions down with it too, this
    is the one place that would otherwise go unnoticed until something
    downstream (no self-refill, no staging processing) is missed by a
    human. Reuses background/health_check.py's own EXPECTED_PANES set and
    run_health_check() directly (no new daemon-list to keep in sync) --
    logs the result either way, NTFYs only on a genuine miss (never a
    routine "all healthy" alert, matching this project's own noise
    discipline)."""
    global _last_degraded_ntfy_at
    try:
        all_ok, ok_lines, problem_lines = run_health_check()
    except Exception as exc:
        log(f"Post-restart daemon health check itself failed to run: {exc}")
        return
    if all_ok:
        log(f"Post-restart daemon health check: OK ({len(ok_lines)} checks healthy)")
        return

    # DEBOUNCE (2026-07-16): a freshly-restarted session races with the just-reaped
    # old process and with daemons still coming up. Re-check after a short delay and
    # keep ONLY problems present in BOTH passes -- a transient (e.g. a momentary
    # second interactive session while the old one terminates) drops out and never
    # pages. This is what turned a real ghost into a full DAY of "MULTIPLE sessions"
    # DEGRADED pages; the orphan reap kills the ghost, this stops the transient race
    # from paging even so.
    time.sleep(DEGRADED_RECHECK_DELAY_SECONDS)
    try:
        all_ok2, _ok2, problem_lines2 = run_health_check()
    except Exception as exc:
        log(f"Post-restart daemon health re-check failed to run: {exc}")
        return
    if all_ok2:
        log("Post-restart daemon health check: transient DEGRADED cleared on re-check "
            f"(first pass flagged {len(problem_lines)}, re-check clean) -- not paging.")
        return
    persistent = [p for p in problem_lines2 if p in set(problem_lines)]
    if not persistent:
        log("Post-restart daemon health check: DEGRADED problems all transient (differed "
            f"between passes: {problem_lines} vs {problem_lines2}) -- not paging.")
        return

    log(f"Post-restart daemon health check: DEGRADED -- {len(persistent)} persistent "
        "problem(s): " + "; ".join(persistent))
    # RATE-LIMIT (2026-07-16): at most one DEGRADED page per cooldown, so a restart
    # storm cannot become a page storm. Logged every time; paged sparingly.
    now = time.time()
    if now - _last_degraded_ntfy_at < DEGRADED_NTFY_COOLDOWN_SECONDS:
        log("DEGRADED page suppressed by cooldown "
            f"({(now - _last_degraded_ntfy_at) / 60:.0f}min since last, "
            f"cooldown {DEGRADED_NTFY_COOLDOWN_SECONDS // 60}min) -- logged only.")
        return
    _last_degraded_ntfy_at = now
    ntfy(
        "Post-restart daemon health check: DEGRADED after a Claude Code "
        f"session restart -- {len(persistent)} persistent problem(s):\n"
        + "\n".join(persistent),
        needs_input=True,
    )


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
    """Usage-limit auto-resume — PROCESS-LEVEL ONLY (pull-loop migration,
    2026-07-15). No NTFY "YES" gate (see module docstring).

    Queues forward-prep/housekeeping work for the background-worker session
    (`queue_downtime_tasks`), then polls every USAGE_LIMIT_POLL_INTERVAL_SECONDS
    until EITHER the usage-limit message clears on its own (the session was
    still alive and its window reset — nothing to do) OR the process has exited
    (RESTART via restart_claude -- resumes the dedicated worker session, a process
    op — allowed). If the limit is still
    showing after USAGE_LIMIT_MAX_WAIT_SECONDS, escalate to the normal
    confirmation-gated handle_session_ended().

    The old in-place RESUME_INSTRUCTION keystroke nudge into the live pane is
    DELETED (keystroke injection is banned). The watchdog never types into a
    live session; it only ever RESPAWNS a dead one."""
    log("Usage-limit message detected — auto-wait (process-level only, no pane injection)")
    queue_downtime_tasks()

    waited = 0
    while waited < USAGE_LIMIT_MAX_WAIT_SECONDS:
        time.sleep(USAGE_LIMIT_POLL_INTERVAL_SECONDS)
        waited += USAGE_LIMIT_POLL_INTERVAL_SECONDS

        if not session_exists() or not claude_is_running():
            log("Session ended while usage-limited — resuming the dedicated worker session")
            restart_claude(resume=True)
            return

        # No keystroke nudge into the live pane. Just re-read (read-only) whether
        # the limit has cleared; if the window reset in place, the session
        # resumes itself and the pull-loop draws its next work at the next
        # boundary.
        if not usage_limit_detected(capture_pane()):
            log("Usage limit cleared — session resumed in place")
            return

    log(f"Usage limit still showing after {USAGE_LIMIT_MAX_WAIT_SECONDS}s — "
        "escalating to normal restart-confirmation flow")
    ntfy("Claude Code usage limit has not cleared after the auto-wait window — "
         "escalating for a manual check.", needs_input=True)
    handle_session_ended()


# PULL-LOOP MIGRATION (2026-07-15): parse_usage_pane / _usage_resume_at /
# check_session_usage are DELETED. All three existed to drive the `/usage`
# slash-command injection (read_slash_dialog_when_idle typed "/usage" into the
# pane) for the proactive 90%-usage self-pause. /usage polling is eliminated
# (DIRECTOR_ANSWERS_C7 #3). The HARD usage-limit path (usage_limit_detected on
# the read-only pane capture -> handle_usage_limit, process-level) remains as
# the tripwire; usage_pause_active() below still reads the pause file the
# session itself writes.


def usage_pause_active() -> bool:
    """True if docs/observability/.usage_pause.json exists and its
    "resume_at" timestamp (ISO8601, written by Claude itself per
    USAGE_PAUSE_CHECK_INSTRUCTION) is still in the future.

    A malformed file is logged and removed (treated as "not paused"). Once
    `resume_at` has passed, the file is deleted and an NTFY sent (2026-07-09,
    doorbell failure #4: "usage-limit pause and resume become ntfy
    transitions so the director never has to guess") -- the supervisor
    (background/supervisor.py) reads this same file read-only and resumes
    granting turns normally once it's gone.
    """
    if not USAGE_PAUSE_FILE.is_file():
        return False

    try:
        data = json.loads(USAGE_PAUSE_FILE.read_text(encoding="utf-8"))
        resume_at = datetime.fromisoformat(data["resume_at"])
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        log(f"Malformed usage-pause file ({e}) — clearing, treating as not paused")
        USAGE_PAUSE_FILE.unlink()
        return False

    if resume_at.tzinfo is None:
        resume_at = resume_at.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) < resume_at:
        return True

    log(f"Usage pause window ended (resume_at={data['resume_at']})")
    ntfy("Claude Code usage pause window ended — resuming normally.")
    USAGE_PAUSE_FILE.unlink()
    return False


def check_autoloop(pane_text: str) -> None:
    """Idle-state machine that NOTIFIES Rich when the session is genuinely
    stopped at a REVIEW_GATE or a permission prompt. PULL-LOOP MIGRATION
    (2026-07-15): it NO LONGER types anything into the pane. The REVIEW_GATE
    reply relay is deleted (gate decisions are the director's at his console;
    the machine never types his answer back in for him), and the proactive
    /usage self-pause is deleted (/usage polling eliminated, DIRECTOR_ANSWERS_C7
    #3). What remains is pure read-only detection + an NTFY so the director
    knows the console wants him. Turn-granting was never this function's job.

    State machine over successive calls (one per CHECK_INTERVAL_SECONDS,
    pane content from `capture_pane()`):
      - Pane changed from the previous call: idle streak resets — still
        mid-task. Any prior "waiting on Rich" state is cleared once the pane
        has been changing for AUTOLOOP_IDLE_CHECKS consecutive polls.
      - Pane unchanged for AUTOLOOP_IDLE_CHECKS consecutive calls: a genuine
        stop. If a REVIEW_GATE or permission prompt is visible, NTFY once.

    REVIEW_GATE_PATTERN/PERMISSION_PROMPT_PATTERN are deliberately only
    checked once the pane is idle — Claude's own prose routinely *mentions*
    "REVIEW_GATE" while actively working, and gating on idle means an
    actively-changing pane never false-triggers.
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
        # NOTIFY ONLY -- the director answers the gate at his own console. The
        # machine never types his decision back into the pane (keystroke
        # injection is banned).
        if not _autoloop_waiting_notified:
            log("REVIEW_GATE visible — waiting for Rich (director answers at the console)")
            token = generate_gate_token(GATE_ID)
            ntfy_gate(
                "Claude Code is waiting at a REVIEW_GATE — check the session "
                "when you have a moment.",
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
    _autoloop_waiting_notified = False


def handle_session_ended(pane_text: str = "") -> None:
    global _last_exit_ntfy_state
    reason, detail = classify_exit(pane_text)
    log(f"Session ended — reason: {reason} | {detail[:100] if detail else 'clean exit'}")

    if reason in ("usage_limit", "quick_exit"):
        if reason == "quick_exit":
            msg = ("CC exited immediately on startup (likely usage/rate limit) — "
                   "waiting 30min before retry.")
        else:
            msg = "CC usage limit — auto-resuming after 30min wait."
        if _last_exit_ntfy_state not in ("usage_limit", "quick_exit"):
            ntfy(msg)
            _last_exit_ntfy_state = reason
        else:
            log(f"Deduped NTFY — still in {_last_exit_ntfy_state} state")
        time.sleep(30 * 60)
        _last_exit_ntfy_state = None
        restart_claude(resume=True)
    elif reason == "crash":
        crash_msg = (f"CC crashed — restarting. Last: {detail[:100]}"
                     if detail else "CC crashed — restarting.")
        # R5 transition-only dedup (2026-07-16): a crash LOOP must page once, not on
        # every restart. Only page when we weren't already in the crash state; a clean
        # recovery resets _last_exit_ntfy_state, so a genuinely new crash after recovery
        # still pages. Mirrors the usage_limit/quick_exit dedup above.
        if _last_exit_ntfy_state != "crash":
            ntfy(crash_msg, needs_input=True)
        else:
            log(f"Deduped crash NTFY — still in crash state: {detail[:80]}")
        _last_exit_ntfy_state = "crash"
        restart_claude()
    else:
        log("Session ended (completion/unknown) — restarting without NTFY")
        _last_exit_ntfy_state = "completion"
        restart_claude()


def main() -> None:
    global _last_exit_ntfy_state
    log("Session watchdog started (PROCESS-LEVEL ONLY — spawns/restarts a DEAD "
        f"session, never types into a LIVE one; auto-restart, no YES gate, max "
        f"{MAX_RESTARTS_PER_HOUR}/hr); idle-gate active "
        f"(idle {AUTOLOOP_IDLE_CHECKS * CHECK_INTERVAL_SECONDS}s -> REVIEW_GATE/"
        "permission-prompt NOTIFY only)")
    # Startup NTFY suppressed — logged locally; Rich flagged this as noise (2026-06-25).
    update_agent_status(
        "session-watchdog", status="running",
        last_action="Watchdog started",
        role="Monitors Claude Code session; RESTARTS a dead session (process op); NOTIFIES on REVIEW_GATE/permission-prompt (no pane injection)",
        produces="docs/observability/session-watchdog-log.md, process restarts",
    )
    consecutive_down = 0

    while True:
        time.sleep(CHECK_INTERVAL_SECONDS)
        try:
            if not session_exists() or not claude_is_running():
                # Claude Code may have exited after displaying a usage-limit
                # message and returning to the shell (foreground = bash, not
                # claude). Check the pane before counting this as a crash.
                pane_text = capture_pane()
                if usage_limit_detected(pane_text):
                    handle_usage_limit()
                    consecutive_down = 0
                    continue
                consecutive_down += 1
                log(f"Claude Code not detected (check {consecutive_down}/2)")
                update_agent_status("session-watchdog", status="idle",
                                    last_action=f"CC not detected (check {consecutive_down}/2)")
                if consecutive_down >= 2:
                    # Log the last visible pane so we can diagnose why it died.
                    last_lines = " | ".join(
                        ln.strip() for ln in pane_text.splitlines()[-5:] if ln.strip()
                    )
                    if last_lines:
                        log(f"Pane at death: {last_lines[:300]}")
                    handle_session_ended(pane_text=pane_text)
                    consecutive_down = 0
                continue

            consecutive_down = 0
            # A confirmed-alive session RESOLVES any prior exit state, so a later crash
            # is a real transition and pages again (paired with the crash-dedup in
            # handle_session_ended; without this reset a one-time crash would mute every
            # future crash page). Only clears a "crash"/"completion" latch, never an
            # active usage-limit wait (that path sleeps inside handle_session_ended).
            if _last_exit_ntfy_state in ("crash", "completion"):
                _last_exit_ntfy_state = None
            update_agent_status("session-watchdog", status="idle", last_action="Session alive check passed")
            pane_text = capture_pane()

            # PULL-LOOP MIGRATION (2026-07-15): the inbound-NTFY-command relay
            # into the live pane is deleted. Inbound human steering arrives via
            # STAGING (ntfy_responder writes from_rich_*.md) + the pull-loop
            # draw; the watchdog never types it into the console.

            if usage_limit_detected(pane_text):
                handle_usage_limit()
                continue

            check_autoloop(pane_text)
        except Exception as e:
            log(f"Watchdog error: {e}")


if __name__ == "__main__":
    main()
