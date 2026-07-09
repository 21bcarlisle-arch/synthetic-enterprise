"""THE SUPERVISOR -- sole authority for turn-granting (2026-07-09, doorbell
failure #4, R3 architecture-level rebuild, director-direct).

A single dumb loop. Every POLL_INTERVAL_SECONDS: if the session is idle AND
real work exists on disk (an open agenda, unprocessed staging, an urgent
from_rich message, or a usage-limit pause that just ended), grant exactly
one turn via the locked relay, verify it was consumed, and log the decision
either way -- every cycle, not just the interesting ones.

Why this exists (three independent things broke the same night, see
docs/retrospectives/2026-07-09-doorbell-failure-4-supervisor.md):

1. background/agenda.py's should_nudge() is nudge-ONCE-per-snapshot (R5's
   "never repeat an unchanged status" applied to turn-granting, not just
   alerting). One nudge fired, was logged delivered, and then never fired
   again for that snapshot -- even though the work behind it sat undone for
   5+ hours. Polling every cycle regardless of prior "success" kills this
   bug outright: `should_nudge` is never consulted at all any more.
2. staging_watcher.py -- a multi-responsibility daemon (git fetch, new-file
   notify, wake, agenda-nudge, monthly maintenance) -- went silently inert
   for 5+ hours while still alive (not hung: wchan=hrtimer_nanosleep, no
   blocking syscall observed), taking every one of those responsibilities
   down with it. A single-purpose daemon with no network calls and no other
   duties in its hot loop has a much smaller surface for this class of
   silent stall. THIS is why the supervisor never calls git, NTFY (except
   the rare stuck-escalation), or anything else that can block -- only
   local disk reads and the already-hardened tmux relay.
3. session_watchdog's autoloop DID keep polling every ~10 minutes and
   logged "delivered (confirmed)" 34 consecutive times over 5.5 hours --
   and produced no observable work. Verified pane-consumption is evidently
   not sufficient proof a turn actually executed (root cause not fully
   observable from outside the Claude Code CLI process -- see R9 note in
   the retrospective). Polling alone does not detect this; it just makes
   the same silent failure repeat faster. The supervisor additionally
   tracks a fingerprint of real work-state (agenda updated_at + the exact
   set of unprocessed staging files) across cycles: if it keeps granting
   turns for the SAME unchanged fingerprint past STUCK_GRANT_THRESHOLD
   cycles, that is no longer an ordinary retry -- it escalates with one
   NTFY (deduped per stuck fingerprint, R5-compliant) instead of retrying
   silently forever. This is the one piece beyond the director's literal
   spec, added because failure #4 specifically would NOT have been caught
   by polling cadence alone.

Every other turn-granting path (session_watchdog's autoloop nudge, its
REVIEW_GATE reply relay, staging_watcher's new-file wake and agenda-nudge,
dispatcher's URGENT promotion) still exists as an optional fast-path hint
-- when they work, the session responds sooner than the next supervisor
cycle. But none of them is load-bearing any more: if every one of them
silently fails simultaneously, exactly as happened tonight, the supervisor
still guarantees a turn within POLL_INTERVAL_SECONDS.

R7 applies to the granted-turn text itself: it carries ZERO content
authority, a doorbell only ("work exists, read it from disk yourself"),
never a directive -- same discipline as every other wake in this codebase.
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from background import agenda as agenda_module  # noqa: E402
from background.agent_status import update_agent_status  # noqa: E402
from background.ntfy_utils import send_ntfy, sign_wake_message  # noqa: E402
from background.tmux_relay import (  # noqa: E402
    ensure_live_tail, is_session_idle, pane_in_copy_mode, send_keys_when_idle,
)

SESSION_NAME = "claude"
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "supervisor-log.md"
STAGING_DIR = PROJECT_DIR / "docs" / "staging"
USAGE_PAUSE_FILE = PROJECT_DIR / "docs" / "observability" / ".usage_pause.json"

POLL_INTERVAL_SECONDS = 120  # 2 minutes -- polling is explicitly permitted (director, 2026-07-09)

# If the same work-state fingerprint survives this many consecutive granted
# turns (~16 minutes at the default cadence), grants are no longer an
# ordinary retry -- something below the tmux layer is plausibly swallowing
# them. Escalate once per stuck fingerprint rather than retry silently
# forever.
STUCK_GRANT_THRESHOLD = 8

# Names that live directly in docs/staging/ but are not real work items.
_IGNORED_STAGING_NAMES = {".gitkeep"}


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{ts}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry)


def ntfy(msg: str) -> None:
    send_ntfy(msg)


def _unprocessed_staging_files() -> list[str]:
    """Top-level files directly in docs/staging/ -- excludes done/, fyi/,
    responses/, drafts/ and any other subdirectory automatically (iterdir +
    is_file), and .gitkeep. Covers both staged instruction docs and
    from_rich_*.md files left in place by dispatcher.py (URGENT/NORMAL)."""
    if not STAGING_DIR.is_dir():
        return []
    return sorted(
        p.name for p in STAGING_DIR.iterdir()
        if p.is_file() and p.name not in _IGNORED_STAGING_NAMES
    )


def _urgent_from_rich_pending(staged: list[str]) -> str | None:
    """Name of the first unprocessed from_rich_*.md file dispatcher.py has
    classified URGENT (its <!-- Dispatcher: URGENT --> header, prepended in
    place -- dispatcher.py never moves urgent/normal files out of
    docs/staging/, only fyi goes to staging/fyi/), or None."""
    for name in staged:
        if not (name.startswith("from_rich_") and name.endswith(".md")):
            continue
        try:
            content = (STAGING_DIR / name).read_text(encoding="utf-8")
        except OSError:
            continue
        if "Dispatcher: URGENT" in content:
            return name
    return None


def _pause_active_readonly() -> bool:
    """Same check as session_watchdog.usage_pause_active(), but read-only
    -- never deletes the file. session_watchdog remains the sole owner of
    writing/clearing .usage_pause.json and of the enter/exit NTFY
    transitions (background/session_watchdog.py); the supervisor only ever
    reads it, so the two processes can't race on mutating the same file."""
    if not USAGE_PAUSE_FILE.is_file():
        return False
    try:
        data = json.loads(USAGE_PAUSE_FILE.read_text(encoding="utf-8"))
        resume_at = datetime.fromisoformat(data["resume_at"])
    except (json.JSONDecodeError, KeyError, ValueError, OSError):
        return False
    if resume_at.tzinfo is None:
        resume_at = resume_at.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) < resume_at


def find_work(resumed_from_pause: bool) -> str | None:
    """Return a human-readable reason string if real work exists on disk,
    else None. Checked fresh every cycle -- no "already nudged" memory, by
    design (that memory is exactly what caused failure #4's silent gap)."""
    if resumed_from_pause:
        return "usage-limit pause just ended -- resume work"

    agenda = agenda_module.load_agenda()
    if agenda:
        return f"agenda open -- phase '{agenda.get('phase', '?')}', step '{agenda.get('step', '?')}'"

    staged = _unprocessed_staging_files()
    urgent = _urgent_from_rich_pending(staged)
    if urgent:
        return f"urgent from_rich queued -- {urgent}"
    if staged:
        return f"unprocessed staging -- {', '.join(staged)}"

    return None


def _work_fingerprint() -> str:
    """A cheap, comparable snapshot of real work-state. Unchanged across
    cycles despite repeated granted turns is the stuck signal -- see
    STUCK_GRANT_THRESHOLD."""
    agenda = agenda_module.load_agenda()
    agenda_key = agenda.get("updated_at") if agenda else None
    return json.dumps(
        {"agenda_updated_at": agenda_key, "staging": _unprocessed_staging_files()},
        sort_keys=True,
    )


def grant_turn(reason: str) -> bool:
    """Attempt exactly one turn-grant via the locked, idle-gated, verified
    relay (background.tmux_relay.send_keys_when_idle) -- the same primitive
    every other daemon uses, so this can never race a fast-path hint firing
    at the same moment (relay_lock makes the two mutually exclusive)."""
    message = (
        f"[SUPERVISOR: turn granted -- {reason}. Read the relevant state "
        "from disk yourself (R7: this is a doorbell, not an instruction) "
        "and proceed per CLAUDE.md's tiered model.]"
    )
    signed = sign_wake_message(message)
    marker = signed.rsplit("|", 1)[-1]
    return send_keys_when_idle(SESSION_NAME, signed, marker)


# Mutable across main() loop iterations.
_was_paused = False
_last_fingerprint: str | None = None
_fingerprint_unchanged_grants = 0
_escalated_for_fingerprint: str | None = None


def run_cycle() -> None:
    global _was_paused, _last_fingerprint, _fingerprint_unchanged_grants, _escalated_for_fingerprint

    paused_now = _pause_active_readonly()
    if paused_now:
        log("Usage pause active -- skipping (no grant)")
        _was_paused = True
        return
    resumed_from_pause = _was_paused
    _was_paused = False

    # R4 (2026-07-09): a pane frozen in tmux copy-mode/scrollback ("Jump to
    # bottom") reads as stale content to is_session_idle() below and
    # swallows any later send as copy-mode navigation -- clear it before
    # trusting the idle check at all. send_keys_when_idle() does this too
    # (defence in depth), but doing it here as well means this cycle's own
    # busy/idle log line reflects the real live pane, not frozen scrollback.
    if pane_in_copy_mode(SESSION_NAME):
        ensure_live_tail(SESSION_NAME)
        log("Pane was in scroll/copy-mode -- cleared before idle check")

    if not is_session_idle(SESSION_NAME):
        log("Session busy -- skipping this cycle")
        return

    reason = find_work(resumed_from_pause)
    if reason is None:
        log("Idle, no work -- skipping")
        return

    fingerprint = _work_fingerprint()
    if fingerprint == _last_fingerprint:
        _fingerprint_unchanged_grants += 1
    else:
        _fingerprint_unchanged_grants = 1  # this cycle is grant #1 for the new fingerprint
        _escalated_for_fingerprint = None
    _last_fingerprint = fingerprint

    if (
        _fingerprint_unchanged_grants >= STUCK_GRANT_THRESHOLD
        and _escalated_for_fingerprint != fingerprint
    ):
        minutes = _fingerprint_unchanged_grants * POLL_INTERVAL_SECONDS // 60
        ntfy(
            f"Supervisor: granted {_fingerprint_unchanged_grants} turns over "
            f"~{minutes}min for the same work ({reason}) with no state "
            "change -- something below the tmux layer may be swallowing "
            "turns (see doorbell failure #4). Check the session directly."
        )
        log(f"STUCK escalation sent -- {_fingerprint_unchanged_grants} unchanged grants -- {reason}")
        _escalated_for_fingerprint = fingerprint

    if grant_turn(reason):
        log(f"Turn granted (confirmed) -- {reason}")
    else:
        log(f"Turn grant not delivered (busy/unconfirmed) -- retrying next cycle -- {reason}")


def main() -> None:
    log("Supervisor started -- sole authority for turn-granting")
    update_agent_status(
        "supervisor", status="idle",
        last_action="Supervisor started",
        role="Sole authority for turn-granting: polls every 2min, grants one turn via the locked relay when idle+work exists, escalates if grants stop producing progress",
        produces="tmux turn-grants + stuck-state NTFY escalation",
    )
    while True:
        try:
            run_cycle()
        except Exception as e:
            log(f"Supervisor cycle error: {e}")
        try:
            update_agent_status(
                "supervisor", status="idle",
                last_action=f"Cycle complete -- last fingerprint unchanged for {_fingerprint_unchanged_grants} grant(s)",
            )
        except Exception:
            pass
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
