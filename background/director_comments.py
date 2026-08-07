"""Director per-page comment channel — RETIRED (permanently), 2026-07-24.

DIRECTOR RULING — DIRECTOR_RULING_RETIRE_PAGE_COMMENT_CHANNEL_2026-07-24.md,
answering the [ACT] "retire vs redesign the page-comment authority path".
Director's word: "Retire."

The PIN-authenticated page-comment channel is decommissioned as a
director-authority path, PERMANENTLY — not locked pending redesign. Rationale on
the record: a web form that stages content as the director's voice was the
weakest link in the authority model and ran unnoticed for a week
(DIRECTOR_SECURITY_COMMENT_CHANNEL_INCIDENT_2026-07-24.md); the advisor bridge
and the (pending) signed-NTFY path supersede it.

What retirement means in THIS module (ruling point 1):
  - The intake authority path (`_write_comment_to_staging`) is DELETED. There is
    no code here that can stage a comment or attribute anything to the director.
  - The poll (`check_once`) and the parser (`parse_comment_submission`) are
    DELETED. This daemon fetches nothing and validates nothing.
  - `main()` is a permanent SAFE NO-OP: it logs the retirement and exits 0. The
    manifest marks this `state: retired` with no systemd unit generated, so it is
    never started; but even a bare hand-launch runs no intake — matching the
    autonomous-runner / executor-daemon retired-daemon "safe no-op" pattern.

Reconciler (ruling point 2): the manifest entry is `retired`, so the reconciler
treats a not-running observation as the EXPECTED state (no MISSING drift alarm),
and a `retired`+running observation alarms RETIRED_RUNNING — a self-healing
reconciler can never silently resurrect a retired authority path.

History preserved (ruling point 3): the from_rich_comment_* artifacts in
docs/staging/done/ stay as record. Retirement removes the channel, not the
archive.

Future (ruling point 4): if page comments ever return as a convenience, they
return in a clearly NON-AUTHORITY namespace as unauthenticated suggestions,
actionable only after confirmation through the bridge or a signed director
channel — a fresh director decision and a DIFFERENT module, never a restart of
this one. Reviving THIS authority path requires an explicit director ruling.

Synthetic-marker class stands (ruling point 5): test/synthetic inputs carry an
unmistakable marker and cannot occupy an authority namespace.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "director-comments-log.md"

RETIRED = True  # module-level tombstone marker: the authority path no longer exists.

RETIRED_NOTICE = (
    "director-comments is RETIRED (2026-07-24 director ruling). No intake, no poll, no "
    "parser, no staging path. A bare launch is a safe no-op that exits. Reviving the "
    "authority path is a fresh director decision, never a restart."
)


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{ts}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry)


def main() -> int:
    """Permanent safe no-op. The retired daemon stages nothing and polls nothing."""
    log(RETIRED_NOTICE)
    return 0


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/director_comments.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("director_comments")
    sys.exit(main())
