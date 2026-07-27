"""LAW C (DIRECTOR_RULING_FAILURE_BIAS_LAWS 2026-07-27) -- the INDEPENDENT primary-state read.

LAW C, verbatim: *"The watchdog and the daily note derive their verdict from PRIMARY state --
the actual contents of `in_progress/`, the campaign registers, the defect ledger, the maturity
map -- never from the tick's published enumeration. Two sources that can disagree, so a false
claim in one is visible from the other."*

This module is that SECOND, independent source. It reads DISK directly and imports NOTHING from
`supervisor.py` / `find_work` -- so a bug in the tick's own `_is_drained_and_gated()` enumeration
(source A) is contradicted by this scan (source B). The 42h EIGHTH-CLASS stall had exactly ONE
source: the deadman's proven-rest fold trusted the supervisor's `_is_drained_and_gated()` verdict,
and the daily note reported that verdict's STATUS. LAW C severs both couplings by adding this
independent read that neither the supervisor nor the daily note can corrupt.

SCOPE HONESTY (R9): the concrete, currently-UNCOVERED gap this scan closes is the SELF-DRAWABLE
mint parked in `in_progress/`. The deadman's own `_open_blocked_mints()` deliberately EXCLUDES
self-drawable mints (they are "the tick's job to draw, not a blocker") -- so a self-drawable mint
the draw fails to pick up is invisible to every existing deadman tier until the 6h hard cap. That
is the exact silence LAW C forbids. Broader primary-source independence (open campaign items,
unresolved defect-ledger rows, drawable maturity atoms) is still read only THROUGH the supervisor's
own drained check today; making those independent too is a named LAW-C follow-on, not built here --
this file does not pretend to cover them.

INDEPENDENCE (R15): no supervisor import anywhere in this file. FAIL-SAFE DIRECTION: an unreadable
directory / file yields [] -- this scan's job is the POSITIVE detection of drawable work the
enumeration may have missed, so a read error here never *silences* a real alarm (the deadman's own
git-commit-clock tiers remain the independent backstop); it simply cannot ADD a page it cannot
substantiate. It never fabricates work that is not on disk.
"""
from __future__ import annotations

import re
from pathlib import Path

# The marker a planner mint carries when it is drawable-now (vs blocked). Same string the
# supervisor draw and the deadman's blocked-mint reader key on -- kept in sync by being the
# ONE documented convention (project_r17_tick_never_rests): a parked mint MUST carry
# `<!-- SUPERVISOR_DRAW: self-drawable|blocked -->` or it is invisible.
_SELF_DRAWABLE_RE = re.compile(r"SUPERVISOR_DRAW:\s*self-drawable")
_MINT_GLOB = "PLANNER_MINTED_*.md"
_HEAD_BYTES = 600  # the marker lives in the doc's leading HTML comment; bounded read


def _title(body: str, fallback: str) -> str:
    """First markdown H1 (or the fallback filename) -- a short human label for the page."""
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip()[:120]
    return fallback


def drawable_undrawn_mints(in_progress_dir: Path) -> list[tuple[str, str]]:
    """(filename, title) for every SELF-DRAWABLE PLANNER_MINTED_* mint parked in `in_progress/`.

    This is the COMPLEMENT of the deadman's `_open_blocked_mints()` (which returns the BLOCKED
    ones and excludes these). A self-drawable mint sitting here is work the tick is supposed to
    DRAW; its continued presence -- read directly off disk, independent of any tick verdict -- is
    the LAW-C signal that the enumeration's "empty / rest-legitimate" claim may be false.

    Never raises: an unreadable dir / file is skipped (fail toward "cannot add", never a crash of
    the caller's cycle -- the deadman and the daily note both depend on this returning cleanly)."""
    out: list[tuple[str, str]] = []
    try:
        files = sorted(in_progress_dir.glob(_MINT_GLOB))
    except OSError:
        return []
    for f in files:
        try:
            body = f.read_text(encoding="utf-8")
        except OSError:
            continue
        if _SELF_DRAWABLE_RE.search(body[:_HEAD_BYTES]):
            out.append((f.name, _title(body, f.name)))
    return out
