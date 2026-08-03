"""Advisor-restart-ruling stall detector -- HX2 event E4.

Source: `docs/staging/done/DIRECTOR_RULING_HARNESS_EXIT_CRITERION_RATIFIED_2026-07-27.md`
§3 event 4: "An advisor ruling whose purpose is restarting stalled work. This one binds
the advisor: if the machine has to be doorbelled awake by a staged document, the counter
resets." Real fixture pair (both required by the exit criteria's own "benign look-alike"
demand -- a legitimate DECISION-class touch must NOT trip the detector for a
STALL-class one):

  - FIRES: `docs/staging/done/R3_WORK_GRANTING_REDESIGN.md` (2026-07-12) -- a real,
    staged-by-advisor redesign order whose own text is an incident report: "The director
    is hand-typing 'self-refill next atom' into the console -- he is manually performing
    the supervisor's core function. That is the harness failing at its one job." Its
    purpose is unambiguously restarting stalled work.
  - MUST STAY SILENT: `docs/staging/done/DIRECTOR_RULING_HARNESS_EXIT_CRITERION_RATIFIED_
    2026-07-27.md` -- the very ruling THIS ATOM (HX2) was minted from. Its own text is a
    RATIFICATION of a proposal, not a restart -- but it is the hardest possible test case,
    because §3 of that document *quotes*, verbatim, "hand-typing", "granted a turn at the
    terminal", "could not... recover" and "doorbell" while DESCRIBING the stall-class
    taxonomy. A naive keyword match on any of those phrases fires on this document too
    (verified: `grep -ni` against the real file matches all four). That is the actual
    trap this module is built to avoid, not a hypothetical.

DISCRIMINATOR (why the ratification does not fire): R3 reports a LIVE, FIRST-PERSON
observed failure under its own "## The observed failure" / "## Root cause" headings --
the structural signature of an incident report, not a decision. The ratification's
headings are "1. RATIFIED as proposed", "2. Two decisions attached", "3. Returned as a
PROBLEM", "4. Coherence requirements", "5. One question owed back", "WORK THIS CREATES"
-- the structural signature of a decision document. This module keys on that STRUCTURAL
distinction (an "observed failure" / "root cause" heading actually present in the body)
rather than surface keyword overlap, which the real fixture pair proves is NOT
discriminating on its own.

SCOPE NOTE: this reads staged/archived instruction documents broadly (not only the
`[DIRECTOR-RULING]`/`[STEER]` bracket-tag convention `supervisor._is_ruling_or_steer`
uses for BUILD-draw purposes) -- the director's own framing ("an advisor ruling", "a
staged document") is about the DOCUMENT'S PURPOSE, not its filename convention, and R3
itself carries no bracket tag. `classify_ruling_restart_class` is the pure, directly
testable core; `advisor_restart_ruling_active` is the thin directory-scanning wrapper.
"""
from __future__ import annotations

import re
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_STAGING_ROOT = PROJECT_DIR / "docs" / "staging"

# A genuine incident-report structural marker: a heading naming the OBSERVED FAILURE or
# its ROOT CAUSE as the document's own subject matter (R3's real headings, matched
# case-insensitively so a close paraphrase still counts).
_INCIDENT_HEADING_RE = re.compile(
    r"^#{1,6}\s*(?:the\s+)?observed\s+failure\b|^#{1,6}\s*root\s+cause\b",
    re.IGNORECASE | re.MULTILINE,
)

# Explicit restart/rescue vocabulary -- necessary but NOT sufficient on its own (the
# ratification fixture matches several of these while describing the taxonomy, not
# reporting a live incident -- see module docstring).
_RESTART_VOCAB_RE = re.compile(
    r"hand[- ]typ(?:ing|ed)|manually perform(?:ing|ed)?\s+the\s+supervisor|"
    r"granted\s+a\s+turn\s+at\s+the\s+terminal|could\s+not\s+(?:otherwise\s+)?recover|"
    r"silently\s+wedged|doorbelled?\s+awake|the\s+harness\s+failing\s+at\s+its\s+one\s+job",
    re.IGNORECASE,
)


def classify_ruling_restart_class(text: str) -> bool:
    """True iff `text` is a RESTART-class document: it both (a) uses restart/rescue
    vocabulary AND (b) reports that vocabulary under its own genuine incident-report
    structure (an "observed failure"/"root cause" heading), rather than merely
    discussing or quoting the taxonomy (as a ratification of a stall-detection proposal
    legitimately does). Pure function -- no disk I/O -- so it is directly unit-testable
    against the two real fixtures without touching the filesystem."""
    if not text:
        return False
    return bool(_RESTART_VOCAB_RE.search(text)) and bool(_INCIDENT_HEADING_RE.search(text))


def advisor_restart_ruling_active(staging_root: Path | None = None) -> str | None:
    """Scan the staging ROOT (the same scope `supervisor._unconsumed_director_ruling_or_
    steer` uses for freshly-arrived, not-yet-archived instructions -- a doc that has
    already been actioned into `done/`/`in_progress/`/`fyi/`/`drafts/` is no longer 'a
    staged document the machine had to be doorbelled awake by' in the present tense) for
    a RESTART-class document. Returns a stall-class message naming the first match, else
    None. Fail-safe: an unreadable staging dir/file is skipped, never raised -- a
    monitoring read failure here must not manufacture a phantom stall (mirrors
    `supervisor._unconsumed_director_ruling_or_steer`'s own convention)."""
    root = staging_root or DEFAULT_STAGING_ROOT
    try:
        candidates = sorted(p for p in Path(root).glob("*.md") if p.is_file())
    except OSError:
        return None
    for p in candidates:
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        if classify_ruling_restart_class(text):
            return (
                "ADVISOR RESTART RULING (HX2 E4): staged document '{}' reports a live "
                "observed-failure/root-cause incident using restart/rescue vocabulary -- "
                "its purpose is restarting stalled work, not a routine decision. Per §4 "
                "of the coherence ruling this binds the advisor equally: the counter "
                "resets.".format(p.name)
            )
    return None
