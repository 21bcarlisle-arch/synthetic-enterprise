"""Open-question register — DIRECTOR_RULING_NO_QUESTION_LEFT_UNANSWERED 2026-07-28, deliverable 1.

THE BUG (ruling §0): when a ruling is consumed its *work items* are minted and tracked, but its
*questions evaporate* — nothing treats a question as an item that must be closed. This is the exact
sibling of the named-but-unminted finding (`primary_state_scan.named_but_unminted`), applied to
QUESTIONS instead of WORK.

THE DECISION (ruling §1): a question posed in a director ruling/steer is a FIRST-CLASS open item —
enumerable, tracked, answered. **It must be impossible to archive a ruling as consumed while it
carries an unanswered question, enforced MECHANICALLY** (the archive-block gate,
`tools/ruling_archive_question_gate.py`, reads this module).

DESIGN (ruling §2, "the mechanism is yours"):

  EXTRACTION — a ruling carries questions in ONE of two AUTHORITATIVE forms, and ONLY these two:
    (a) an explicit enumerated block under a heading naming the register/questions — "Seed the
        register with these" / "## QUESTIONS" — each numbered/bulleted item is a question;
    (b) a `?`-terminated sentence inside the **DECISION** section only.
  Prose questions ELSEWHERE (rhetorical framing in a PROBLEM/PREAMBLE section — "an explicit block?
  a parser? a convention?", "why am I the bottleneck?") are NOT obligations and are NOT captured.
  This is the §2-requested rhetorical-vs-obligation split. When genuinely ambiguous the mechanism
  defaults to TRACKED (fail-closed toward the ruling's intent) and lets a cheap close-with-reason
  ("the question is wrong, because…") discharge a false positive — the asymmetry the ruling names.

  TRACKING — questions are DERIVED from PRIMARY state (the ruling bodies themselves), never from a
  hand-maintained list that could drift from the rulings. The register file
  (`docs/observability/open_question_register.json`) holds only DISPOSITIONS keyed by question — a
  question with no disposition is `open` (silent — the failure the ruling forbids). This mirrors the
  LAW-C discipline of `named_but_unminted`: derive the SET from primary state, store only the human
  judgement (the answer) separately, so the set can never silently omit a real question.

  AGEING/ESCALATION — a question's age is read from its source ruling's date (filename `_YYYY-MM-DD`);
  the daily note (`daily_self_note.open_question_line`) surfaces the count + the OLDEST open one, the
  same way it surfaces named-but-unminted work.

CLOSURE (ruling §1): an answer may be "I don't know" / "not yet measurable" / "the question is wrong,
because…" — ALL THREE close a question (statuses `unknown`/`not_measurable`/`wrong`). "carried with a
reason" is NON-SILENT but NOT closed — it still blocks archival (the ruling archives only when the
question is actually answered, not merely acknowledged). `open` (no disposition at all) is the silent
state the ruling exists to eliminate.

INDEPENDENCE / FAIL-SAFE (R15): this module imports NOTHING from `supervisor.py`. FAIL-SAFE DIRECTION
differs by consumer and is the caller's to choose — this module reports the honest set and never
fabricates: a ruling with an unreadable body contributes no questions (it cannot INVENT one), and a
missing/corrupt register means every extracted question is `open` (the SAFE direction for the archive
gate: unknown disposition ⇒ blocks archival, never silently unblocks it — an unavailable answer is a
FAILED answer, R15).
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
STAGING_DIR = PROJECT_DIR / "docs" / "staging"
IN_PROGRESS_DIR = STAGING_DIR / "in_progress"
REGISTER_PATH = PROJECT_DIR / "docs" / "observability" / "open_question_register.json"

# A ruling/steer, by filename convention OR content header (R7: content is the primary signal).
# Kept identical to supervisor / primary_state_scan so the three can never disagree.
_RULING_STEER_PREFIXES = ("DIRECTOR_RULING_", "DIRECTOR_STEER_", "ADVISOR_STEER_")
_RULING_STEER_HEADER_RE = re.compile(r"\[[A-Z0-9 _-]*(?:RULING|STEER)\]", re.IGNORECASE)

# EXTRACTION FORM (a): a heading whose text names the register/questions — "Seed the register with
# these", "## QUESTIONS", "## Open questions". Captures the block body until the next heading.
_QUESTION_BLOCK_RE = re.compile(
    r"^#{1,6}[^\n]*\b(?:seed the register|open questions?|questions?)\b[^\n]*\n(.*?)(?=\n#{1,6}\s|\Z)",
    re.IGNORECASE | re.DOTALL | re.MULTILINE,
)
# A numbered ("1." / "1)") or bulleted ("-"/"*") item line inside a block (first line = the question).
_ITEM_LINE_RE = re.compile(r"^\s*(?:\d+[.)]|[-*])\s+(.+?)\s*$", re.MULTILINE)

# EXTRACTION FORM (b): the DECISION section only. `?`-terminated sentences inside it are obligations.
_DECISION_BLOCK_RE = re.compile(
    r"^#{1,6}[^\n]*\bDECISION\b[^\n]*\n(.*?)(?=\n#{1,6}\s|\Z)",
    re.IGNORECASE | re.DOTALL | re.MULTILINE,
)
# A sentence ending in '?'. Greedy-but-bounded: from a sentence boundary / start up to the '?'.
_QUESTION_SENTENCE_RE = re.compile(r"([^.!?\n][^.!?\n]*?\?)")

# Disposition statuses that CLOSE a question (unblock archival). "carried" is deliberately NOT here:
# it is non-silent but unanswered, so it still blocks. Absent disposition == "open" (silent).
CLOSING_STATUSES = frozenset({"answered", "unknown", "not_measurable", "wrong"})
_NONSILENT_STATUSES = CLOSING_STATUSES | frozenset({"carried"})
_ALL_STATUSES = _NONSILENT_STATUSES | frozenset({"open"})

_RULING_DATE_RE = re.compile(r"_(\d{4}-\d{2}-\d{2})")
_HEAD_BYTES = 600


def _normalize(text: str) -> str:
    """Strip markdown emphasis/code, collapse whitespace, lowercase — for a STABLE question key that
    survives cosmetic edits (bolding, backticks, re-wrapping) but not a genuine wording change."""
    t = re.sub(r"[*`_]", "", text or "")
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t


def question_key(ruling_name: str, question_text: str) -> str:
    """Stable 12-char id for a (ruling, question) pair. Same ruling + same normalized question ⇒
    same key, so a disposition recorded once keeps applying across cosmetic re-wordings of the doc."""
    h = hashlib.sha1(f"{ruling_name}\n{_normalize(question_text)}".encode("utf-8"))
    return h.hexdigest()[:12]


def _is_ruling_or_steer(name: str, head: str) -> bool:
    return name.startswith(_RULING_STEER_PREFIXES) or bool(_RULING_STEER_HEADER_RE.search(head))


def _ruling_date(name: str) -> str | None:
    m = _RULING_DATE_RE.search(name or "")
    return m.group(1) if m else None


def extract_questions(body: str) -> list[str]:
    """The questions a ruling body poses, per the two AUTHORITATIVE forms (see module docstring).

    Returns de-duplicated raw question strings (markdown preserved for display, truncated). Order:
    block items first (their numbered order), then DECISION `?`-sentences. FAIL-SAFE: a body with no
    such block and no DECISION `?`-sentence yields [] — this module never fabricates a question, so a
    rhetorical-only ruling contributes none (the correct answer, not a false alarm)."""
    if not body:
        return []
    seen: set[str] = set()
    out: list[str] = []

    def _add(raw: str) -> None:
        s = re.sub(r"\s+", " ", (raw or "")).strip()
        if not s:
            return
        norm = _normalize(s)
        if norm in seen:
            return
        seen.add(norm)
        out.append((s[:200] + "…") if len(s) > 201 else s)

    # FORM (a): explicit register/questions block(s).
    for bm in _QUESTION_BLOCK_RE.finditer(body):
        for im in _ITEM_LINE_RE.finditer(bm.group(1)):
            _add(im.group(1))

    # FORM (b): `?`-terminated sentences inside the DECISION section only.
    for dm in _DECISION_BLOCK_RE.finditer(body):
        for qm in _QUESTION_SENTENCE_RE.finditer(dm.group(1)):
            _add(qm.group(1))

    return out


def load_dispositions(register_path: Path | None = None) -> dict[str, dict]:
    """The disposition map keyed by question_key. FAIL-SAFE toward BLOCKING (R15): an unreadable /
    corrupt register returns {} so EVERY extracted question falls through to `open` — the archive
    gate then refuses (unknown disposition never silently unblocks). It NEVER raises."""
    p = register_path or REGISTER_PATH
    try:
        data = json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    disp = data.get("dispositions") if isinstance(data, dict) else None
    return disp if isinstance(disp, dict) else {}


def _row(ruling_name: str, question: str, dispositions: dict[str, dict]) -> dict:
    key = question_key(ruling_name, question)
    rec = dispositions.get(key) or {}
    status = rec.get("status") if isinstance(rec, dict) else None
    if status not in _ALL_STATUSES:
        status = "open"  # absent / malformed disposition ⇒ silent (blocks archival)
    return {
        "ruling": ruling_name,
        "date": _ruling_date(ruling_name),
        "question": question,
        "key": key,
        "status": status,
        "disposition": (rec.get("disposition") if isinstance(rec, dict) else None) or "",
        "silent": status == "open",
        "blocks_archive": status not in CLOSING_STATUSES,
    }


def _iter_ruling_bodies(*dirs: Path):
    """(name, body) for every readable [DIRECTOR-RULING]/[STEER] *.md directly in each dir. Fail-safe:
    an unreadable dir/file is skipped (never crashes the caller's cycle)."""
    for d in dirs:
        try:
            files = sorted(Path(d).glob("*.md"))
        except OSError:
            continue
        for p in files:
            try:
                body = p.read_text(encoding="utf-8")
            except OSError:
                continue
            if _is_ruling_or_steer(p.name, body[:_HEAD_BYTES]):
                yield p.name, body


def all_tracked_questions(
    staging_dir: Path | None = None,
    in_progress_dir: Path | None = None,
    register_path: Path | None = None,
) -> list[dict]:
    """Every question extracted from every ACTIVE ruling (staging root + in_progress; NOT done/ —
    a ruling in done/ is discharged), each merged with its disposition. Sorted (date, ruling, key).

    LAW-C independence: reads ONLY the ruling bodies (primary state) + the disposition register;
    imports nothing from the tick. The question SET is derived, never hand-listed, so it cannot
    silently omit a real question. Returns [] on an unreadable staging tree (never fabricates)."""
    sroot = staging_dir or STAGING_DIR
    sip = in_progress_dir or IN_PROGRESS_DIR
    dispositions = load_dispositions(register_path)
    rows: list[dict] = []
    for name, body in _iter_ruling_bodies(sroot, sip):
        for q in extract_questions(body):
            rows.append(_row(name, q, dispositions))
    rows.sort(key=lambda r: (r["date"] or "9999-99-99", r["ruling"], r["key"]))
    return rows


def open_questions(
    staging_dir: Path | None = None,
    in_progress_dir: Path | None = None,
    register_path: Path | None = None,
) -> list[dict]:
    """The subset of `all_tracked_questions` that BLOCKS archival — status ∉ CLOSING_STATUSES
    (i.e. `open` or `carried`). This is the enumeration the daily note surfaces and the acceptance
    test turns on: empty ⇔ no active ruling carries an unanswered question."""
    return [r for r in all_tracked_questions(staging_dir, in_progress_dir, register_path)
            if r["blocks_archive"]]


def blocking_questions_for_ruling(
    ruling_name: str,
    body: str,
    register_path: Path | None = None,
) -> list[dict]:
    """The blocking (open/carried) questions a SINGLE ruling body carries, given the current
    dispositions. The archive-block gate calls this on a ruling being moved to done/. FAIL-SAFE
    toward blocking: an unknown disposition ⇒ `open` ⇒ blocking (R15: an unavailable answer is a
    FAILED answer — never silently unblock an archival)."""
    dispositions = load_dispositions(register_path)
    out: list[dict] = []
    for q in extract_questions(body):
        r = _row(ruling_name, q, dispositions)
        if r["blocks_archive"]:
            out.append(r)
    return out
