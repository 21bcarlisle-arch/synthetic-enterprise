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

PROJECT_DIR = Path(__file__).resolve().parent.parent
STAGING_DIR = PROJECT_DIR / "docs" / "staging"
IN_PROGRESS_DIR = STAGING_DIR / "in_progress"
DONE_DIR = STAGING_DIR / "done"

# The marker a planner mint carries when it is drawable-now (vs blocked). Same string the
# supervisor draw and the deadman's blocked-mint reader key on -- kept in sync by being the
# ONE documented convention (project_r17_tick_never_rests): a parked mint MUST carry
# `<!-- SUPERVISOR_DRAW: self-drawable|blocked -->` or it is invisible.
_SELF_DRAWABLE_RE = re.compile(r"SUPERVISOR_DRAW:\s*self-drawable", re.IGNORECASE)
_BLOCKED_RE = re.compile(r"SUPERVISOR_DRAW:\s*blocked", re.IGNORECASE)
_MINT_GLOB = "PLANNER_MINTED_*.md"

#: THE WHOLE DOCUMENT, AND NOT A PREFIX OF IT. This read was bounded to the first 600 bytes,
#: because "the marker lives in the doc's leading HTML comment" -- which was true when it was
#: written and stopped being true as ticks prepended their notes above it.
#:
#: MEASURED 2026-09-02: `PLANNER_MINTED_reversibility_action_and_act_2026-07-29.md` carries
#: `<!-- SUPERVISOR_DRAW: self-drawable -->` at character **3513**, behind 3.5 KB of accreted tick
#: history. So this scan could not see it; and `_open_blocked_mints`, which is this function's
#: COMPLEMENT, therefore counted it as BLOCKED. The mint's block was dissolved on 2026-08-03 -- the
#: file says so in its own text -- and it has been alarming as blocked, and invisible as drawable,
#: for a month. Nobody drew it from either direction.
#:
#: A control keyed to a POSITION goes quiet, not loud, when the thing moves past it, and widening
#: the number would only move the date of the next failure. There is no cost to reading the file:
#: these are a handful of documents of a few KB each.
#:
#: FAIL-CLOSED ON AMBIGUITY, matching `staging_disposition.selfdrawable_mint_in_progress`: a
#: blocked marker anywhere PARKS the mint even if a self-drawable marker is also present. A
#: whole-document scan can meet a token quoted inside a historical note, and parking on a
#: contradiction is the safe direction -- an over-reported drawable item is drawn and found done,
#: an under-reported block is work nobody does.


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
        if _SELF_DRAWABLE_RE.search(body) and not _BLOCKED_RE.search(body):
            out.append((f.name, _title(body, f.name)))
    return out


# =============================================================================
# §5 (DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE 2026-07-27, as RESTATED by the
# amendment): "everything named-and-not-done must be ENUMERABLE and CHECKABLE, so
# that 'no below-target work anywhere' can be verified against reality rather than
# asserted." One wall (LAW C): derive from PRIMARY state -- the rulings/steers
# themselves and the staging tree -- NEVER from the tick's own enumeration.
#
# The §0 root cause this closes: the tick asserted "no below-target work anywhere"
# while THREE named items (merit-order reconstruction, the DD seasonal cash-flow
# FRAME, the site evidence pages) sat in ratified rulings, NEVER minted into an atom.
# `drawable_undrawn_mints` above cannot see them -- it scans EXISTING mint docs; a
# deliverable that was never minted has no mint doc to scan. This derivation reads
# the rulings' WORK THIS CREATES blocks directly and diffs them against the mints
# that cover them, so the never-minted residue becomes visible.
#
# INDEPENDENCE (the module invariant, R15): NO import from supervisor.py. The
# WORK-THIS-CREATES parser below is a DELIBERATE re-implementation of supervisor's
# `work_this_creates_deliverables` (§4) -- importing it would execute supervisor's
# draw logic and break the "second, independent source" guarantee this whole file
# exists to provide. A drift-guard test asserts the two parsers agree on fixtures so
# they cannot silently diverge (test imports both; this module imports neither).
# =============================================================================

# Mirrors supervisor._WORK_THIS_CREATES_RE / _DELIVERABLE_LINE_RE exactly (drift-guarded).
_WORK_THIS_CREATES_RE = re.compile(
    r"^#{1,6}\s*WORK\s+THIS\s+CREATES\b[^\n]*\n(.*?)(?=\n#{1,6}\s|\Z)",
    re.IGNORECASE | re.DOTALL | re.MULTILINE,
)
_DELIVERABLE_LINE_RE = re.compile(r"^\s*(?:\d+[.)]|[-*])\s+(.+?)\s*$", re.MULTILINE)
# Mirrors supervisor._DIRECTOR_RULING_STEER_HEADER_RE + the filename-prefix convention.
_RULING_STEER_HEADER_RE = re.compile(r"\[[A-Z0-9 _-]*(?:RULING|STEER)\]", re.IGNORECASE)
_RULING_STEER_PREFIXES = ("DIRECTOR_RULING_", "DIRECTOR_STEER_", "ADVISOR_STEER_")

# COVERAGE SIGNAL 1 -- a PLANNER_MINTED doc's `Source: <ruling>.md, deliverable N` line.
_SOURCE_DELIVERABLE_RE = re.compile(r"deliverable\s*\*{0,2}\s*(\d+)", re.IGNORECASE)
# COVERAGE SIGNAL 2 -- the machine-authored MINT COVERAGE MAP banner in a ruling's
# leading HTML comment: `[N] ... (MINTED:|LANDED|ALREADY COVERED|COVERED|DONE)`.
_COVERAGE_MAP_ENTRY_RE = re.compile(r"\[(\d+)\]\s*(.*?)(?=\n\s*\[\d+\]|\Z)", re.DOTALL)
_COVERAGE_KEYWORDS = ("MINTED", "LANDED", "COVERED", "DONE", "DISCHARGED")
_LEADING_COMMENT_RE = re.compile(r"<!--(.*?)-->", re.DOTALL)


def _work_this_creates_deliverables(text: str) -> list[str]:
    """Independent re-implementation of supervisor.work_this_creates_deliverables (§4). [] means
    NO block (the §4 defect signal, never fabricated). Drift-guarded against the original by test."""
    m = _WORK_THIS_CREATES_RE.search(text or "")
    if not m:
        return []
    out: list[str] = []
    for dm in _DELIVERABLE_LINE_RE.finditer(m.group(1)):
        s = re.sub(r"[*`]", "", dm.group(1)).strip()
        if s:
            out.append((s[:200] + "…") if len(s) > 201 else s)
    return out


def _is_ruling_or_steer(name: str, head: str) -> bool:
    """A [DIRECTOR-RULING]/[STEER] doc, by filename prefix OR content header (R7: content primary)."""
    return name.startswith(_RULING_STEER_PREFIXES) or bool(_RULING_STEER_HEADER_RE.search(head))


def _covered_indices_from_body(text: str) -> set[int]:
    """Deliverable indices a ruling's OWN machine-authored MINT COVERAGE MAP banner marks covered
    (LANDED/MINTED/COVERED/DONE) -- the case of a deliverable finished as landed code with no mint
    doc of its own (e.g. §2 of the WORK_DEFINITION ruling). Scoped to the leading HTML comment so a
    stray `[N]` in prose can't trigger it. SCOPE HONESTY (R9): this trusts the machine-authored
    banner; a LYING banner is out of scope here (that is the banner's own control, not this scan).
    The §0 failure class is caught regardless -- a never-minted item has NEITHER a mint doc NOR a
    coverage-map entry, so signal-1 AND signal-2 both stay silent and it lands in the residue."""
    m = _LEADING_COMMENT_RE.search(text or "")
    if not m:
        return set()
    covered: set[int] = set()
    for em in _COVERAGE_MAP_ENTRY_RE.finditer(m.group(1)):
        entry = em.group(2).upper()
        if any(k in entry for k in _COVERAGE_KEYWORDS):
            covered.add(int(em.group(1)))
    return covered


def _iter_docs(*dirs: Path):
    """(name, body) for every readable *.md directly in each dir. Fail-safe: unreadable skipped."""
    for d in dirs:
        try:
            files = sorted(Path(d).glob("*.md"))
        except OSError:
            continue
        for p in files:
            try:
                yield p.name, p.read_text(encoding="utf-8")
            except OSError:
                continue


def _minted_deliverables(ruling_names: set[str], *mint_dirs: Path) -> set[tuple[str, int]]:
    """COVERAGE SIGNAL 1: (ruling_name, deliverable_index) pairs claimed by a PLANNER_MINTED doc's
    `Source:` line. A mint doc references exactly one ruling + one deliverable; we key off its
    Source line only (not prose) so a deliverable number mentioned elsewhere can't over-cover."""
    covered: set[tuple[str, int]] = set()
    for name, body in _iter_docs(*mint_dirs):
        if not name.startswith(_MINT_GLOB.split("*")[0]):
            continue
        for line in body.splitlines():
            if "source:" not in line.lower():
                continue
            dm = _SOURCE_DELIVERABLE_RE.search(line)
            if not dm:
                continue
            idx = int(dm.group(1))
            for rn in ruling_names:
                if rn in line:
                    covered.add((rn, idx))
    return covered


def named_but_unminted(
    staging_dir: Path | None = None,
    in_progress_dir: Path | None = None,
    done_dir: Path | None = None,
) -> list[dict]:
    """§5's FIRST OUTPUT (RESTATED): the current NAMED-BUT-UNMINTED set, derived from PRIMARY state.

    For every staged/in_progress [DIRECTOR-RULING]/[STEER] carrying a WORK THIS CREATES block, each
    named deliverable is either COVERED or it is RESIDUE (named, not done). A deliverable is COVERED
    when EITHER (signal 1) a PLANNER_MINTED_* doc -- in the staging root, in_progress/, or done/ --
    names the ruling + that deliverable index on its `Source:` line, OR (signal 2) the ruling's own
    machine-authored MINT COVERAGE MAP banner marks that index LANDED/MINTED/COVERED/DONE (the
    landed-as-code-without-a-mint-doc case). The residue is everything neither signal covers -- the
    §0 failure class, where a ruling names work that was never minted into an atom AND never landed.

    Returns a list of {ruling, index, deliverable} dicts, sorted (ruling, index). Empty list == the
    checkable proof that no named deliverable sits unminted. LAW C: reads ONLY the rulings and the
    staging tree (primary state); it takes NO tick/enumeration/idle argument, so it cannot be a
    restatement of the tick's own belief. FAIL-SAFE: an unreadable dir yields no residue from it (it
    can never FABRICATE unminted work), matching this module's positive-detection contract.

    Rulings in done/ are EXCLUDED as sources: a ruling archived to done/ is fully discharged, so its
    deliverables are no longer 'not done'. done/ IS still scanned as a mint-COVERAGE source (a mint
    that landed and was archived still counts as coverage)."""
    sroot = staging_dir or STAGING_DIR
    sip = in_progress_dir or IN_PROGRESS_DIR
    sdone = done_dir or DONE_DIR

    # 1. Gather ruling/steer SOURCES from the root + in_progress (NOT done -- discharged there).
    rulings: dict[str, str] = {}  # name -> body
    for name, body in _iter_docs(sroot, sip):
        if _is_ruling_or_steer(name, body[:600]):
            rulings[name] = body
    if not rulings:
        return []

    # 2. COVERAGE SIGNAL 1: mint-doc Source references, scanning root + in_progress + done.
    minted = _minted_deliverables(set(rulings), sroot, sip, sdone)

    # 3. Diff each ruling's deliverables against coverage; emit the residue.
    residue: list[dict] = []
    for name in sorted(rulings):
        body = rulings[name]
        deliverables = _work_this_creates_deliverables(body)
        body_covered = _covered_indices_from_body(body)  # SIGNAL 2
        for i, text in enumerate(deliverables, start=1):
            if (name, i) in minted or i in body_covered:
                continue
            residue.append({"ruling": name, "index": i, "deliverable": text})
    return residue
