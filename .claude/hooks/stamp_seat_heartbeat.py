#!/usr/bin/env python3
"""PreToolUse hook -- the HARNESS stamps that the interactive seat is alive.

Director, 2026-08-24: *"nothing notices it has stopped ... I shouldn't be the mechanism that
spots a stall."* `background/seat_continuity.py` carries the full reasoning; the two things
worth repeating at the write site are why this is a hook and not a call the session makes, and
what it is not allowed to be evidence of.

WHY A HOOK. The sibling mechanism, `seat_work_in_hand.claim()`, has to be CALLED by the
session — an exhortation wearing a mechanism's clothes, and a session that dies before
remembering to claim leaves nothing behind at all. A PreToolUse hook fires on every tool call
whether or not the session remembers anything, and a session that has stopped cannot keep it
warm. That is the property a self-written heartbeat does not have.

WHAT IT IS NEVER EVIDENCE OF. Progress. `seat_work_in_hand`'s docstring rejects a seat-written
heartbeat as the tautology R15 names first, and that objection is about progress and still
stands: nothing here says work advanced, and the claim deadline still decides that from commits
touching the claimed paths. This says one thing — the seat ran a tool just now.

Never blocks, never errors into the session, never prints: any failure is swallowed and the
tool call proceeds untouched (exit 0, no output). A watcher that can break the thing it watches
is worse than no watcher.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _seat import is_resident_seat  # noqa: E402


def main() -> int:
    # Seat guard FIRST, exactly like the sibling hooks: .claude/hooks/ is committed, so every
    # session on this repo runs it, and a foreign sandbox stamping the resident seat's
    # heartbeat would keep a dead seat looking alive from another machine — the one failure
    # this mechanism must not have.
    if not is_resident_seat():
        return 0
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        payload = {}

    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
        from background.seat_continuity import note_activity

        note_activity(
            str(payload.get("tool_name") or "?"),
            session_id=str(payload.get("session_id") or ""),
        )
    except Exception:  # noqa: BLE001 - see the module docstring: never break the session
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
