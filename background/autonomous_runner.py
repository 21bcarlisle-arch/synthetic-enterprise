#!/usr/bin/env python3
"""Autonomous Claude turn runner — replaces the broken tmux keystrokes autoloop.

**THIS MODULE IS RETIRED. IT HAS NOT RUN SINCE 2026-07-08 AND NOTHING LAUNCHES IT.** The fact was
already recorded here, in a parenthesis inside `_pane_content`, ninety lines down. It is at the top
now because on 2026-08-31 the delivery seat read this module's LEDGER
(`docs/observability/autonomous-runner-log.md`), found seventeen "Usage limit active" lines dated
that day, and reported a usage limit to the director. There was no limit and no runner: the lines
were written by `tests/background/test_autonomous_runner.py`, which called the real `log()` at the
real path. 6,421 of that ledger's 27,675 lines are test exhaust. **A retirement recorded where
nobody reads it is not recorded.** The sink that now makes the write impossible is
`tests/production_surface_guard.py`.

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

Runs with --dangerously-skip-permissions (Rich's direct, live confirmation,
2026-07-05, expanding docs/review_gates/SKIP_PERMISSIONS_TIER1.md's original
watchdog-only scope to every session launcher). Same reasoning as the
watchdog: this is a non-interactive, unattended `claude -p` invocation with
no TTY and nobody present to answer a permission prompt -- without the flag,
a turn requiring any tool use beyond the pre-approved allowlist simply stalls
at its first prompt and burns its rate-limited slot for nothing.

Logs to docs/observability/autonomous-runner-log.md.
Turn output appended to docs/observability/autonomous-turn-output.md.
"""

import json
import os
import re
import subprocess
import sys
import time
from collections import deque
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import NamedTuple

PROJECT_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "autonomous-runner-log.md"
TURN_OUTPUT_FILE = PROJECT_DIR / "docs" / "observability" / "autonomous-turn-output.md"
PANE_STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".autonomous_pane_state.json"

SESSION_NAME = "claude"

# Claude Code binary — full path since nvm isn't active in subprocess env
CLAUDE_BIN = Path("/home/rich/.nvm/versions/node/v24.16.0/bin/claude")

# Model routing (2026-07-11, director NTFY, Lane-H): these are supervisor-fired
# micro-turns/status checks (fired when nobody's watching, most cycles find an
# empty queue and go back to sleep) -- routed to the fastest cheap model, not
# the strongest one reserved for build-lane architecture. See CLAUDE.md's model
# routing note for the full task-class mapping.
AUTONOMOUS_TURN_MODEL = "claude-haiku-4-5-20251001"

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
    "If nothing is pending, your job is to ADVANCE THE PROJECT, not fill time. "
    "Read CLAUDE.md's 'five hollow gaps' section — pick the highest-priority gap "
    "that is not yet closed, design the next phase that closes it (or materially "
    "reduces it), write it to docs/staging/drafts/NEXT_PHASE.md, and NTFY Rich: "
    "'Proposed Phase X: <one sentence> — will proceed in 4h unless redirected.' "
    "Do NOT default to reporting backlog refinements (more metrics, deeper CLV "
    "snapshots, forward curve tweaks) unless all five hollow gaps are closed. "
    "Always: run tests before committing, commit with a clear message, push, "
    "and NTFY Rich with what was done."
)

sys.path.insert(0, str(PROJECT_DIR))
from background.agent_status import update_agent_status  # noqa: E402
from background.secrets_location import scrub_model_facing_env  # noqa: E402

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
        # `{SESSION_NAME}:` session-qualified (OPS1_tmux_target_qualification) -- this module is
        # RETIRED (never launched), qualified for hygiene so no reviver inherits the ambiguity.
        ["tmux", "capture-pane", "-t", f"{SESSION_NAME}:", "-p"],
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


_USAGE_LIMIT_PHRASES = (
    "Claude.ai usage limit",
    "usage limit reached",
    "Your Claude.ai Pro",
)

# A real usage-limit message names when it lifts. These are the two shapes Claude Code prints:
# `resets at 6pm`, `Try again at 18:00`, `resets 2026-08-31T18:00`. If NONE of them can be read
# out of the matched line, we cannot tell a live limit from an hours-old one still on screen.
_RESET_PATTERNS = (
    re.compile(r"(?:resets?|try again|again)\s+(?:at\s+)?(\d{1,2}):(\d{2})", re.I),
    re.compile(r"(?:resets?|try again|again)\s+(?:at\s+)?(\d{1,2})\s*([ap])m", re.I),
)


class LimitVerdict(NamedTuple):
    """What the pane says about a usage limit, WITH the evidence for saying it.

    A bare `True` was the whole defect: the caller logged "Usage limit active" and the reader of
    that line — a human, or the delivery seat answering the director — had no way to tell a live
    limit from a phrase sitting in scrollback. A verdict that has to carry its own evidence
    cannot be written down without it.
    """
    limited: bool
    reason: str          # always populated, for BOTH answers: why we are skipping, or why not
    evidence: str = ""   # the matched pane line, verbatim, trimmed


def _parse_reset_minutes(line: str, now: datetime | None = None) -> int | None:
    """Minutes from now until the limit lifts, read out of the message itself, or None.

    None is the important return. It means "this line claims a limit and does not say when it
    ends", and the caller treats that as UNVERIFIED — not as a limit.

    `now` IS INJECTABLE BECAUSE THE ANSWER DEPENDS ON IT, and the defect below hid for a day
    behind a test suite that could only see it between midnight and 02:00.
    """
    now = now or datetime.now().astimezone()
    for pattern in _RESET_PATTERNS:
        m = pattern.search(line)
        if not m:
            continue
        try:
            if m.lastindex == 2 and m.group(2).lower() in ("a", "p"):
                hour = int(m.group(1)) % 12 + (12 if m.group(2).lower() == "p" else 0)
                minute = 0
            else:
                hour, minute = int(m.group(1)), int(m.group(2))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                continue
        except (ValueError, IndexError):
            continue
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        # A BARE CLOCK TIME CARRIES NO DATE, so `now.replace()` always builds TODAY's instant and
        # the reading is ambiguous over a 24-hour cycle. THE BRANCH THAT USED TO BE HERE COULD NOT
        # FIRE: read at 01:27, a message printed at 23:27 lands 22 hours in the FUTURE rather than
        # two hours in the past, so `target <= now` was false and the caller was told the limit
        # lifts in 1319 minutes. A limit that had already lifted suppressed every autonomous turn
        # until the text scrolled off the pane — which is the exact defect this whole function was
        # written to end, surviving inside it. (Both arms of that branch returned the same
        # expression, so it read as a decision and was not one.)
        #
        # Resolved by taking the candidate CLOSEST TO NOW among yesterday, today and tomorrow. No
        # threshold is picked and nothing is assumed about how long a limit lasts: it is the only
        # reading of an undated clock time that does not prefer one direction over the other.
        #
        # WHICH WAY IT FAILS, since it must fail somehow: a genuine reset more than twelve hours
        # ahead reads as expired, so the runner RUNS. That is the asymmetry this module already
        # argues for at `usage_limit_verdict` — a false start costs one API call the real limit
        # refuses in a second; a false stop costs every turn until someone notices, and nobody
        # noticed for 54 days.
        target = min(
            (target + timedelta(days=d) for d in (-1, 0, 1)),
            key=lambda t: abs(t - now),
        )
        return int((target - now).total_seconds() // 60)
    return None


def usage_limit_verdict() -> LimitVerdict:
    """Decide whether a usage limit is genuinely active, and say what that rests on.

    WHY THIS IS NOT A BOOLEAN ANY MORE (2026-08-31, director: *"autonomous turns have been
    suppressed on a wrong signal … make it impossible to claim a limit it hasn't verified, and
    where the real signal is unavailable it should run rather than skip — a false stop costs more
    than a false start here"*).

    The old check matched a phrase anywhere in `tmux capture-pane` output and returned True. Three
    things were wrong with that and only the third is obvious:

      1. **A pane is scrollback, not a status line.** A limit message from three hours ago is
         still on screen. The check had no notion of recency at all, so once a limit had EVER been
         shown it read as active until the text scrolled off.
      2. **An unreadable pane and a clean pane gave the same answer.** They still do — and now
         that is deliberate and stated rather than incidental: no evidence means RUN.
      3. **The claim was logged without the evidence for it**, which is how 3,443 skip lines
         became unreadable and how this seat came to report a usage limit to the director that
         did not exist.

    THE RULE: skip ONLY on a matched line that also names a reset time still in the future.
    Everything else runs. A phrase with no reset time is a message we cannot date; a reset time
    in the past is a message we CAN date and it has expired. Both are unverified, and unverified
    runs.
    """
    pane = _pane_content()
    if not pane.strip():
        # THE FAIL-OPEN DIRECTION IS THE CORRECT ONE HERE and it is worth being explicit, because
        # this repo's usual instinct (fail closed) is the opposite. A wrongly-launched turn costs
        # one API call that the real limit would refuse in a second; a wrongly-skipped turn costs
        # every turn until someone notices, and nobody noticed for 54 days.
        return LimitVerdict(False, "no pane content could be read — running rather than skipping")

    for line in pane.splitlines():
        if any(ch in line for ch in "|[]`"):
            continue
        lowered = line.lower()
        if not any(phrase.lower() in lowered for phrase in _USAGE_LIMIT_PHRASES):
            continue
        trimmed = line.strip()[:160]
        minutes = _parse_reset_minutes(line)
        if minutes is None:
            return LimitVerdict(
                False,
                "a usage-limit phrase is on the pane but names no reset time, so it cannot be "
                "dated and may be old scrollback — running rather than skipping",
                trimmed,
            )
        if minutes <= 0:
            return LimitVerdict(
                False,
                f"the usage-limit message on the pane reset {abs(minutes)}min ago — expired, "
                "running rather than skipping",
                trimmed,
            )
        return LimitVerdict(True, f"usage limit lifts in {minutes}min", trimmed)

    return LimitVerdict(False, "pane read, no usage-limit message")


def _usage_limit_active() -> bool:
    """Back-compatible boolean. Prefer `usage_limit_verdict()` — it carries the evidence."""
    return usage_limit_verdict().limited


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

    # THE CLAIM CARRIES ITS PROOF OR IT IS NOT MADE. The old line said "Usage limit active" and
    # nothing else, so a reader could not tell it from a phantom -- and on 2026-08-31 a reader
    # could not, and told the director there was a limit when there was none.
    verdict = usage_limit_verdict()
    if verdict.limited:
        log(f"Usage limit VERIFIED ({verdict.reason}) — skipping autonomous turn. "
            f"Evidence: {verdict.evidence!r}")
        return

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    log(f"Launching autonomous turn (claude -p --model {AUTONOMOUS_TURN_MODEL} --dangerously-skip-permissions)")

    TURN_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TURN_OUTPUT_FILE, "a") as out:
        out.write(f"\n\n---\n# Autonomous turn — {ts}\n\n")

    outfile = open(TURN_OUTPUT_FILE, "a")
    # Go direct to Anthropic — no token-proxy dependency.
    # The proxy is optional monitoring; routing through it was the single
    # point of failure that silently killed all overnight autonomous turns.
    env = os.environ.copy()
    env.pop("ANTHROPIC_BASE_URL", None)
    # Authority gap fix (DIRECTOR_RULING_HMAC_GAP_OPTION_1, 2026-07-23): strip
    # SE_WAKE_HMAC_KEY so this model turn cannot forge a director-signed message.
    scrub_model_facing_env(env)
    # Belt-and-braces (2026-07-11, root-caused live): this Popen's env is a
    # copy of autonomous_runner.py's OWN process environment, not something
    # freshly read from tmux's global environment at spawn time -- if the
    # runner's own long-lived process/pane predates a `tmux set-environment
    # -g DISABLE_AUTOUPDATER 1` (start_worker.sh), it silently inherits the
    # stale value. session_watchdog.py's restart_claude() already sets this
    # explicitly per-launch (its own `-e` flag) rather than trusting
    # inheritance; this closes the same gap here rather than depending on
    # the runner's own process having been started/restarted after the fix.
    env["DISABLE_AUTOUPDATER"] = "1"
    _active_proc = subprocess.Popen(
        [str(CLAUDE_BIN), "-p", "--model", AUTONOMOUS_TURN_MODEL,
         "--dangerously-skip-permissions", AUTONOMOUS_PROMPT],
        cwd=str(PROJECT_DIR),
        stdout=outfile,
        stderr=outfile,
        text=True,
        env=env,
    )
    _turn_times.append(time.time())
    log(f"Autonomous turn launched (pid={_active_proc.pid})")


def main() -> None:
    global _active_proc
    log("Autonomous runner started")
    update_agent_status(
        "autonomous-runner", status="idle",
        last_action="Runner started",
        role="Runs scheduled Claude Code sessions for background work when session is idle",
        produces="CC session activity, phase completions",
    )

    while True:
        time.sleep(POLL_INTERVAL_SECONDS)

        try:
            # Reap completed turn
            if _active_proc is not None and _active_proc.poll() is not None:
                rc = _active_proc.returncode
                # If the turn failed with a connectivity error, remove it from
                # the rate-cap window so the cap isn't burned on API downtime.
                if rc != 0:
                    try:
                        tail = TURN_OUTPUT_FILE.read_text(encoding="utf-8").rsplit("---\n", 1)[-1]
                        if "ConnectionRefused" in tail or "Unable to connect" in tail:
                            if _turn_times:
                                _turn_times.pop()
                            log(f"Autonomous turn failed — API unreachable (rc={rc}); rate-cap slot refunded")
                            _active_proc = None
                            update_agent_status("autonomous-runner", status="idle",
                                                last_action="API unreachable — backing off")
                            continue
                    except Exception:
                        pass
                log(f"Autonomous turn completed (pid={_active_proc.pid}, rc={rc})")
                update_agent_status("autonomous-runner", status="idle", last_action=f"Turn completed (rc={rc})")
                _active_proc = None
            elif _active_proc is not None:
                update_agent_status("autonomous-runner", status="working", last_action="Autonomous turn running")
            else:
                update_agent_status("autonomous-runner", status="idle", last_action="Polling — idle", is_heartbeat=True)

            idle = idle_seconds()

            if idle >= IDLE_THRESHOLD_SECONDS and _active_proc is None:
                log(f"Session idle {idle/60:.0f}min — launching autonomous turn")
                launch_turn()

        except Exception as e:
            log(f"Runner error: {e}")


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/autonomous_runner.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("autonomous_runner")
    main()
