#!/usr/bin/env python3
"""NTFY inbound responder — RETIRED (permanently), 2026-10-15.

The director, 15 Oct 14:08 BST, to his advisor: "Should we not mothball the ntfy alerts? I don't
ever read them. And you can stage so it's redundant." DIRECTOR_STEER_MOTHBALL_NTFY_2026-10-15
item 2 retires the inbound route BY CONSTRUCTION and removes anything that only existed to serve it.

What this daemon was: it polled the shared NTFY topic, wrote each inbound message to
`docs/staging/from_rich_*.md` (redacted by `inbound_secret_redaction`, flood-quarantined, deduped
against replays and against our own sends) and replied with a templated status ack. The last
message it staged was `from_rich_20261006_204456.md`.

What retirement means here, following the `director_comments` tombstone:
  - The poll (`check_once`), the staging writer (`_write_to_staging`), the flood guard, the claim
    ledger and the status reply are DELETED, with the tests that exercised only them. Nothing here
    can fetch a message or attribute text to the director.
  - Its state files (`.ntfy_responder_since.json`, `_seen_hashes.json`, `_rate.json`, the claim
    directory) have no reader or writer.
  - `main()` is a permanent safe no-op. The manifest row is `state: retired` and the unit is gone,
    so a running instance alarms RETIRED_RUNNING; even a bare hand-launch polls nothing.

Director input now arrives through the console and the advisor channel (`advisor_channel.py`).
Reviving an inbound phone route is a fresh director decision and a different module, never a
restart of this one. The code it had is in git history before this tombstone.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "ntfy-responder-log.md"

#: Module-level tombstone marker: the inbound route no longer exists.
RETIRED = True

RETIRED_NOTICE = (
    "The NTFY responder is RETIRED (2026-10-15, the director's mothball steer): no poll, no "
    "staging, no reply. A bare launch exits. Reviving it is a fresh director decision."
)


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{ts}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry)


def main() -> int:
    """Permanent safe no-op. The retired daemon polls nothing and stages nothing."""
    log(RETIRED_NOTICE)
    return 0


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/ntfy_responder.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("ntfy_responder")
    sys.exit(main())
