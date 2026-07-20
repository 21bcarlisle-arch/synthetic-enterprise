"""Canonical staging-disposition detection — the ONE definition of the mis-park anti-pattern
(2026-07-20). Used by BOTH the supervisor draw (`_real_staged_instructions` → the tick SEES and
SELF-RECOVERS mis-parked actionable work) AND the deadman `[BLOCKED]` net (→ it also pages fast).
Single source of truth so the self-recovery and the alarm can never disagree.

WHY THIS EXISTS — the 2026-07-20 3-hour silent stall. `docs/staging/in_progress/` is ONLY for items
BLOCKED on a wall (a genuinely-open sub-item + what unblocks it); it is deliberately EXCLUDED from the
supervisor draw AND (before this) from the deadman queued-work scan. A worker tick consumed two
director steers and PARKED them there declaring their open sub-items "authorised NOW" — actionable
work, not blocked — which it never executed. The draw could not see it (in_progress/ excluded) and the
tick rested over it; nothing paged for 3h except the weak commit-clock STALL. Making the tick itself
DRAW such work (this module, wired into the draw) is the durable fix: it self-recovers instead of
relying on an alarm plus a human.

THE ANTI-PATTERN IS WORKER-LEGIBLE — it keys on the workers' OWN disposition-banner language, not a
fuzzy read of arbitrary prose:
  - a WORKER-written disposition banner (`[IN-PROGRESS DISPOSITION ...]`), AND
  - an actionable-now marker (the worker itself declared the open sub-item doable NOW).
NOT flagged: director-parked multi-part items (no worker banner) and genuinely-blocked worker parks
(a real wall — "awaiting director", "director-reserved", not "authorised NOW"). So a legitimately
parked-blocked item (e.g. a done analysis whose only remainder is a director [ACT]) stays quiet.
"""
from __future__ import annotations

from pathlib import Path

# The worker-written disposition banner (lower-cased match). Director-authored staged docs do not
# carry this — it is written by a worker tick when it parks a multi-part item.
WORKER_DISPOSITION_BANNER = "[in-progress disposition"

# Markers by which a worker itself declared the open sub-item ACTIONABLE NOW (not blocked). If a
# worker wrote one of these AND then parked the doc, the work is mis-parked (invisible but doable).
ACTIONABLE_NOW_MARKERS = (
    "authorised now", "authorized now",
    "discover/frame, authorised", "discover/frame, authorized",
    "discover-workable", "workable now", "actionable now",
)

_HEAD_CHARS = 1500  # the banner/disposition sits at the very top of the doc


def misparked_actionable_in_progress(in_progress_dir: Path) -> list[str]:
    """Basenames of in_progress/ docs a worker mis-parked as blocked when their open sub-item is
    actionable NOW. Report-only; NEVER raises (a detection must not crash the draw or the deadman)."""
    try:
        if not in_progress_dir.is_dir():
            return []
        candidates = sorted(in_progress_dir.glob("*.md"))
    except OSError:
        return []
    out: list[str] = []
    for p in candidates:
        try:
            head = p.read_text(encoding="utf-8", errors="replace")[:_HEAD_CHARS].lower()
        except OSError:
            continue
        if WORKER_DISPOSITION_BANNER in head and any(m in head for m in ACTIONABLE_NOW_MARKERS):
            out.append(p.name)
    return out
