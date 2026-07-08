"""Open-agenda continuation marker (docs/staging/TURN_CONTINUATION_AND_PHASE3_GO.md,
Deliverable 1a, 2026-07-08).

Turns end; nothing previously granted the next one once a genuinely new
staged file wasn't the trigger -- staging_watcher.py's wake fires only for
new staged files, by design (see its own module docstring). This module
lets the current Claude Code session record "I have open phase work" to a
small on-disk marker; staging_watcher.py's EXISTING poll loop (no new
process, no new polling) checks this marker each cycle and, if items are
open AND the marker has sat untouched long enough to presume the session
idle (not mid-turn), injects one signed continue-nudge -- the same
sign_wake_message + send_keys pattern already used for new-staged-file
wakes. Clearing the agenda (phase closes, or nothing left to continue)
means silence: no open work, no turns, no burn.

Nudge-once discipline (R5: "never repeat an unchanged status"): a given
agenda snapshot (identified by its own `updated_at`) is nudged at most
once. If the session doesn't wake and clear/advance the agenda, no repeat
spam follows -- the session must update the agenda (proving it's alive and
working) for a fresh nudge to become eligible again.

R7 applies to the nudge text itself: it carries ZERO content authority --
a doorbell only ("open agenda exists, read state from disk"), never a
directive. The receiving session must re-derive what to do from
PRIORITIES.md / the relevant design doc / this file's own recorded state,
not trust the nudge text.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

PROJECT_DIR = Path(__file__).resolve().parent.parent
AGENDA_FILE = PROJECT_DIR / "background" / ".open_agenda.json"
NUDGE_STATE_FILE = PROJECT_DIR / "background" / ".agenda_last_nudge.json"

# How long the agenda must sit untouched before the session is presumed
# idle (not mid-turn) and a continue-nudge becomes eligible.
IDLE_THRESHOLD_SECONDS = 600  # 10 minutes


def set_agenda(phase: str, step: str, next_action: str) -> None:
    """Record that phase work is open. Call at the start of (or during) a
    long phase, and again whenever the current step changes -- each call
    resets the idle clock, since it proves the session is actively working."""
    AGENDA_FILE.parent.mkdir(parents=True, exist_ok=True)
    AGENDA_FILE.write_text(json.dumps({
        "phase": phase,
        "step": step,
        "next_action": next_action,
        "updated_at": time.time(),
    }, indent=2))


def clear_agenda() -> None:
    """Record that no phase work is open (phase closed / turn cleanly
    finished with nothing left to continue)."""
    if AGENDA_FILE.exists():
        AGENDA_FILE.unlink()
    if NUDGE_STATE_FILE.exists():
        NUDGE_STATE_FILE.unlink()


def load_agenda() -> Optional[dict]:
    if not AGENDA_FILE.exists():
        return None
    try:
        return json.loads(AGENDA_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def is_stale_enough_to_nudge(agenda: dict, now: Optional[float] = None) -> bool:
    """True if the agenda has sat untouched long enough that the session is
    presumed idle (not mid-turn) and a continue-nudge is warranted."""
    now = now if now is not None else time.time()
    updated_at = agenda.get("updated_at", 0)
    return (now - updated_at) >= IDLE_THRESHOLD_SECONDS


def _load_last_nudged_at() -> Optional[float]:
    if not NUDGE_STATE_FILE.exists():
        return None
    try:
        return json.loads(NUDGE_STATE_FILE.read_text()).get("nudged_agenda_updated_at")
    except (json.JSONDecodeError, OSError):
        return None


def _save_last_nudged_at(updated_at: float) -> None:
    NUDGE_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    NUDGE_STATE_FILE.write_text(json.dumps({"nudged_agenda_updated_at": updated_at}))


def should_nudge(now: Optional[float] = None) -> Optional[dict]:
    """Return the agenda dict if a continue-nudge is due right now (open,
    stale, and not already nudged for this exact agenda snapshot), else
    None. Does not itself record the nudge -- call record_nudged() after
    actually sending it, so a failed send can be retried next cycle."""
    agenda = load_agenda()
    if not agenda:
        return None
    if not is_stale_enough_to_nudge(agenda, now):
        return None
    updated_at = agenda.get("updated_at", 0)
    if _load_last_nudged_at() == updated_at:
        return None
    return agenda


def record_nudged(agenda: dict) -> None:
    _save_last_nudged_at(agenda.get("updated_at", 0))
