"""Open-agenda continuation marker (docs/staging/TURN_CONTINUATION_AND_PHASE3_GO.md,
Deliverable 1a, 2026-07-08).

Lets the current Claude Code session record "I have open phase work" to a
small on-disk marker. background/supervisor.py (2026-07-09, doorbell
failure #4, R3 architecture rebuild) is the sole authority that reads this
marker and grants a turn when it's open -- see that module's docstring.
Clearing the agenda (phase closes, or nothing left to continue) means
silence: no open work, no turns, no burn.

RETIRED 2026-07-09: this module used to also own a nudge-once-per-snapshot
mechanism (should_nudge()/record_nudged(), called from staging_watcher.py's
poll loop) implementing R5's "never repeat an unchanged status" applied to
turn-granting. That was the direct cause of doorbell failure #4: one nudge
fired for the 2026-07-08 22:47 UTC agenda snapshot, was logged delivered,
and then -- because should_nudge() would never return that exact snapshot
again -- never fired again, even though the work behind it sat undone for
5+ hours. Removed rather than patched (R3): background/supervisor.py
re-reads load_agenda() from scratch every 2-minute cycle with no "already
nudged" memory at all, so this failure mode cannot recur here.

R7 still applies to anything derived from this marker: it carries ZERO
content authority -- a doorbell only ("open agenda exists, read state from
disk"), never a directive. The receiving session must re-derive what to do
from PRIORITIES.md / the relevant design doc / this file's own recorded
state, not trust any nudge/grant text verbatim.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

PROJECT_DIR = Path(__file__).resolve().parent.parent
AGENDA_FILE = PROJECT_DIR / "background" / ".open_agenda.json"


def set_agenda(phase: str, step: str, next_action: str) -> None:
    """Record that phase work is open. Call at the start of (or during) a
    long phase, and again whenever the current step changes."""
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


def load_agenda() -> Optional[dict]:
    if not AGENDA_FILE.exists():
        return None
    try:
        return json.loads(AGENDA_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return None
