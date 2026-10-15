#!/usr/bin/env python3
"""Message dispatcher — RETIRED (permanently), 2026-10-15.

The director, 15 Oct 14:08 BST, to his advisor: "Should we not mothball the ntfy alerts? I don't
ever read them. And you can stage so it's redundant." DIRECTOR_STEER_MOTHBALL_NTFY_2026-10-15
item 2 retires the inbound route BY CONSTRUCTION and removes anything that only existed to serve it.

What this daemon was: it classified each `docs/staging/from_rich_*.md` the NTFY responder wrote as
URGENT or NORMAL by keyword, prepended a header and sent a high-priority NTFY for URGENT. The
responder is retired, so nothing writes `from_rich_*.md` and there is nothing to classify.

What retirement means here, following the `director_comments` tombstone:
  - The poll (`check_once`), the classifier, the router and the seen-map loader are DELETED, with
    the tests that exercised only them. `.dispatcher_seen.json` has no reader or writer.
  - The supervisor's "urgent from_rich queued" branch, which read this daemon's URGENT header, is
    deleted with it.
  - `main()` is a permanent safe no-op. The manifest row is `state: retired` and the unit is gone,
    so a running instance alarms RETIRED_RUNNING; even a bare hand-launch polls nothing.

Reviving it is a fresh director decision, never a restart. The code it had is in git history
before this tombstone.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "dispatcher-log.md"

#: Module-level tombstone marker: the inbound route no longer exists.
RETIRED = True

RETIRED_NOTICE = (
    "The dispatcher is RETIRED (2026-10-15, the director's mothball steer): no poll, no "
    "classification, no routing. A bare launch exits. Reviving it is a fresh director decision."
)


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{ts}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry)


def main() -> int:
    """Permanent safe no-op. The retired daemon polls nothing and classifies nothing."""
    log(RETIRED_NOTICE)
    return 0


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/dispatcher.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("dispatcher")
    sys.exit(main())
