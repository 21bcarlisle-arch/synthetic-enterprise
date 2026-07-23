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


# ---------------------------------------------------------------------------
# The 20:00Z parked-CAMPAIGN blind spot (2026-07-23 NIGHT_ENFORCEMENT ruling ADDENDUM).
#
# A SECOND way the in_progress/ blind spot swallows drawable work, distinct from the worker-mispark
# net above. At 20:00Z a DIRECTOR-authored campaign continuation doc (DIRECTOR_CAMPAIGN_SITE_MODEL_
# SPINE) with an OPEN, explicitly PROCEED-ABLE sub-item (§B, marked "[proceed-able now]") was parked
# into in_progress/. It carries no worker `[IN-PROGRESS DISPOSITION` banner, so the net above misses
# it; its open items are NOT in CAMPAIGN_REGISTER.yaml (SITE_V5 there is `closed`), so
# `_open_campaign_draw` misses it too. The draw saw "nothing drawable" and the tick idled 56+ min
# beside an open campaign -- the system filed its own to-do list into its own blind spot.
#
# Director's named failing test (addendum): "parked-campaign-with-open-items must be drawable ...
# either the classifier reads open items wherever they are parked, or open campaign items are never
# parked into the excluded directory -- pick the mechanism, prove it both ways." MECHANISM (option a):
# the classifier READS the parked doc's OWN language -- a campaign doc that declares a remaining
# sub-item PROCEED-ABLE NOW has drawable work hidden -> surface it so the draw self-recovers.
#
# SELF-TERMINATING (no 2-min re-grant churn -- the anti-pattern CLAUDE.md warns of): a surfaced doc
# leaves the set the moment EITHER the work lands and the doc is archived out of in_progress/, OR the
# campaign is reconciled into an OPEN CAMPAIGN_REGISTER.yaml entry that references it (then the
# register draws it, not this net). A genuinely fully-blocked park carries NO proceed-able marker and
# stays quiet -- so the invariant also FORCES park-honesty: declare a sub-item proceed-able => it gets
# drawn; if it is really blocked, say so (don't claim proceed-able) and it stays parked.

# Positive-sense phrases by which a doc declares a remaining sub-item DRAWABLE NOW. A fully-blocked
# park ("awaiting director", "director-reserved", "cannot land until") carries none of these.
CAMPAIGN_DRAWABLE_MARKERS = (
    "proceed-able", "proceedable",
    "may now proceed",
    "drawable now",
)


def _open_campaign_referenced_docs(register_path: Path) -> set[str]:
    """Basenames referenced by any OPEN campaign in CAMPAIGN_REGISTER.yaml (its ruling/doc/source/dod
    string fields). Such a doc is already drawn via the register, so this net must not double-surface
    it. Fail-open: any read/parse error -> empty set (never suppress a real find on a bad register)."""
    try:
        import yaml  # local import: a detection must never hard-fail the draw on an import error
        doc = yaml.safe_load(register_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return set()
    out: set[str] = set()
    for camp in (doc.get("campaigns") or []):
        if not isinstance(camp, dict):
            continue
        if str(camp.get("status", "")).strip().lower() != "open":
            continue
        for v in camp.values():
            if isinstance(v, str) and v.strip():
                out.add(Path(v.strip()).name)
    return out


def misparked_open_campaign_in_progress(
    in_progress_dir: Path, register_path: Path | None = None
) -> list[str]:
    """Basenames of in_progress/ CAMPAIGN docs that declare a remaining sub-item PROCEED-ABLE NOW
    (drawable work parked in the excluded dir) and are NOT already tracked by an OPEN campaign in the
    register. Whole-doc scan (a campaign's proceed-able §B sits well past the head). Report-only;
    NEVER raises (a detection must not crash the draw or the deadman)."""
    try:
        if not in_progress_dir.is_dir():
            return []
        candidates = sorted(in_progress_dir.glob("*.md"))
    except OSError:
        return []
    tracked = _open_campaign_referenced_docs(register_path) if register_path else set()
    out: list[str] = []
    for p in candidates:
        if p.name in tracked:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace").lower()
        except OSError:
            continue
        # "is a campaign" keys on the FILENAME or the TITLE/intro (first 200 chars), NOT anywhere in
        # the body -- else any director doc that merely mentions "campaign authority" in prose false-
        # fires. Director campaign docs are named DIRECTOR_CAMPAIGN_* / titled "# ... campaign ...".
        # The proceed-able marker is matched over the WHOLE doc (a campaign's §B sits deep in the body).
        is_campaign = "campaign" in p.name.lower() or "campaign" in text[:200]
        if is_campaign and any(m in text for m in CAMPAIGN_DRAWABLE_MARKERS):
            out.append(p.name)
    return out
