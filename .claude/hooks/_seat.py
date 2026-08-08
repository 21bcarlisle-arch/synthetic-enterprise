#!/usr/bin/env python3
"""Seat identity for .claude/hooks/ -- "whose hands is this hook in?".

.claude/hooks/ is committed to the repo, so EVERY Claude Code session on this
repo executes these hooks -- including foreign cloud sessions that are NOT the
resident worker seat CLAUDE.md describes. Several of these hooks are the
resident seat's own machinery (presence stamping, director-input logging,
the pull-loop work draw): running them from a foreign sandbox is a defect --
it dirties the resident seat's state files, logs to its private ops repo, and
(the dangerous case) consumes its instruction channel via pull_next_work.py.

`is_resident_seat()` is the structural discriminator. Guarded hooks call it as
their FIRST act and make themselves provably inert (exit 0, no output, no
writes) when it returns False, so a foreign session runs them as no-ops while
the resident seat is unaffected.

Resident detection -- zero setup required on the resident machine:
    ~/.config/synthetic-enterprise/.env.ntfy exists ONLY on the resident seat
    (it holds the seat's NTFY secrets; it is gitignored and predates this
    change -- see background/secrets_location.py). Its presence is therefore a
    reliable "this is the resident machine" marker with nothing new to install.

Override (for tests and emergencies), wins over the file check:
    SE_SEAT=resident  -> force resident (guarded hooks run)
    SE_SEAT=foreign   -> force foreign  (guarded hooks stay inert)
    any other / unset -> fall back to the marker-file check above.

Deliberately dependency-free (stdlib only, no repo imports, no subprocess) so
importing it can never itself be a side effect and never drags a heavy or
failing dependency into a hook's first line. Home is resolved at CALL time, so
a test that monkeypatches HOME controls the result.
"""
from __future__ import annotations

import os
from pathlib import Path

# The resident-only marker: the seat's NTFY secret file, out of the working
# tree (Option 2 floor, 2026-07-11) and gitignored. Present iff resident.
_MARKER_RELATIVE = (".config", "synthetic-enterprise", ".env.ntfy")


def resident_marker_path() -> Path:
    """Absolute path to the resident-only marker file (resolved against the
    current HOME at call time, so HOME monkeypatching works in tests)."""
    return Path.home().joinpath(*_MARKER_RELATIVE)


def is_resident_seat() -> bool:
    """True iff this process is running in the resident worker seat.

    The SE_SEAT env override wins over the file check (tests/emergencies);
    any value other than the two recognised ones falls through to the marker.
    Never raises: an unreadable/odd HOME degrades to False (foreign), the safe
    direction -- a foreign session staying inert can never damage the resident
    seat's state, whereas a wrong "resident" could.
    """
    override = os.environ.get("SE_SEAT")
    if override == "resident":
        return True
    if override == "foreign":
        return False
    try:
        return resident_marker_path().is_file()
    except OSError:
        return False
