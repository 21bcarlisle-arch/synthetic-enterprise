"""Trust ledger -- earned autonomy per task class (TRUST_LEDGER_AND_BILLING_CHECK.md
item 1, P1, 2026-07-13, director-raised from a published nine-layer harness article).

Today autonomy is BINARY and STATIC (PROCEED_BY_DEFAULT: proceed unless a
one-way door). The maturity map grades the PRODUCT (atoms); nothing grades
the PROCESS -- which classes of work the builder has statistically earned the
right to do unattended. This module is the thin start: ONE ledger keyed by
task class, real Expert-Hour/evaluator verdicts as its only data source,
autonomy level derived mechanically from the recorded record.

GOODHART SAFEGUARDS (non-negotiable, the article omits these -- enforced
structurally here, not by policy prose the builder could talk itself past):

  1. The grader must be fresh-context and independent. record_verdict()
     REJECTS (raises ValueError) any evaluator_name not in
     INDEPENDENT_EVALUATORS -- a fixed whitelist of this project's own
     already-established fresh-context reviewer identities. The builder
     cannot record its own self-assessment as a verdict; there is no code
     path that accepts one. This whitelist is the "closed at the tool
     level" the staged instruction requires -- extending it is itself a
     real decision (adding a new evaluator identity), not a routine edit.
  2. Pass rates are computed from RECORDED VERDICTS ONLY, never a
     self-reported percentage -- autonomy_level() always re-derives from
     the ledger's own entries, there is no field anywhere for "claimed pass
     rate."
  3. The trust score is a DIAGNOSTIC (Law A) -- autonomy_level() returns a
     descriptive string with a plain-English state, never a signal that
     changes what tools/permissions are actually available (that remains
     PROCEED_BY_DEFAULT's own one-way-door list, untouched by this file).
     The director may override any level at any time (nothing here gates
     that; this module has no enforcement power over the harness, only
     visibility).
  4. Grader-capture tell: rising pass rate with falling defect-discovery is
     evidence of grader capture, not quality -- check_grader_capture_tell()
     flags this pattern explicitly rather than only reporting the raw
     pass rate.

Coherence note (staged instruction, "the same mechanism as (a) the scrutiny
dial (b) DIRECTOR_TWIN's fidelity metric"): this thin start covers ONE
subject (task-class trust) with the identical schema shape the other two
subjects would use (fresh-context verdict -> ledger entry -> derived,
never-self-reported, never-a-target score) -- building all three ledgers
now would be the "big-bang build" this project's own precedent (A2's
"registration + thin-start + pilot") explicitly avoids. Extending to the
other two subjects is real future work, not built here.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

PROJECT_DIR = Path(__file__).resolve().parent.parent
LEDGER_PATH = PROJECT_DIR / "docs" / "observability" / "trust_ledger.json"

# Real, already-established fresh-context reviewer identities this project
# uses today (company/compliance/internal_audit.py's Qwen skeptic pass is
# deliberately NOT included -- that pass is explicitly ADVISORY per its own
# phase-close-checklist wording, not a pass/fail verdict of record). Adding a
# new name here is a real decision (a new evaluator must genuinely be
# fresh-context and independent of the work it grades) -- not a routine data
# edit, which is exactly why this list is a code constant, not a config file
# the builder could edit unnoticed alongside an unrelated commit.
INDEPENDENT_EVALUATORS = frozenset({
    "phase-close-evaluator",   # .claude/agents/phase-close-evaluator.md
    "cold-eyes-walk",          # .claude/skills/cold-eyes-walk/SKILL.md
    "epistemic-verifier",      # .claude/agents/epistemic-verifier.md (mechanical, not judgement -- see class below)
})


class TaskClass(str, Enum):
    """Task classes named directly in the staged instruction's own example
    list. Extending this enum is a real registration decision (a new class
    of work the ledger will track), not routine -- matching how
    DECISION_RIGHTS_REGISTER (company/governance/decision_rights.py) treats
    its own class list as director-owned."""
    BILLING = "billing"
    PRICING = "pricing"
    HARNESS_SUPERVISOR = "harness_supervisor"
    SITE_PRESENTATION = "site_presentation"
    DOCS_DISCOVERY = "docs_discovery"


class Verdict(str, Enum):
    PASS = "pass"
    NEEDS_WORK = "needs_work"


@dataclass(frozen=True)
class TrustLedgerEntry:
    task_class: TaskClass
    verdict: Verdict
    evaluator_name: str
    evaluated_at: str  # ISO date, real evaluation date -- never fabricated
    subject: str  # what was graded (a commit SHA, an atom id, a file) -- real, checkable
    defects_found_post_close: int = 0  # rework discovered AFTER this verdict was recorded
    rework_required: bool = False
    notes: str = ""


def _load_ledger() -> list[dict]:
    if not LEDGER_PATH.exists():
        return []
    try:
        return json.loads(LEDGER_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        return []


def _save_ledger(entries: list[dict]) -> None:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    LEDGER_PATH.write_text(json.dumps(entries, indent=2, sort_keys=True))


def record_verdict(
    task_class: TaskClass,
    verdict: Verdict,
    evaluator_name: str,
    subject: str,
    evaluated_at: Optional[str] = None,
    defects_found_post_close: int = 0,
    rework_required: bool = False,
    notes: str = "",
) -> TrustLedgerEntry:
    """Append one real evaluator verdict to the ledger. Raises ValueError
    if `evaluator_name` is not in INDEPENDENT_EVALUATORS -- this is the
    Goodhart safeguard enforced AT THE TOOL LEVEL: there is no way to call
    this function successfully with a self-reported or non-whitelisted
    grader identity, regardless of what the caller's own prose claims."""
    if evaluator_name not in INDEPENDENT_EVALUATORS:
        raise ValueError(
            f"'{evaluator_name}' is not a recognised independent evaluator "
            f"(INDEPENDENT_EVALUATORS={sorted(INDEPENDENT_EVALUATORS)}) -- "
            "the trust ledger only accepts verdicts from this project's own "
            "established fresh-context reviewers, never a self-reported score."
        )
    entry = TrustLedgerEntry(
        task_class=task_class,
        verdict=verdict,
        evaluator_name=evaluator_name,
        evaluated_at=evaluated_at or datetime.now(timezone.utc).date().isoformat(),
        subject=subject,
        defects_found_post_close=defects_found_post_close,
        rework_required=rework_required,
        notes=notes,
    )
    entries = _load_ledger()
    entries.append({**asdict(entry), "task_class": entry.task_class.value, "verdict": entry.verdict.value})
    _save_ledger(entries)
    return entry


def entries_for_class(task_class: TaskClass) -> list[dict]:
    return [e for e in _load_ledger() if e.get("task_class") == task_class.value]


def autonomy_level(task_class: TaskClass, window: int = 10, earn_threshold: float = 0.8) -> str:
    """Diagnostic only (Law A) -- describes the record, changes nothing
    about what tools/permissions are actually available (PROCEED_BY_DEFAULT's
    one-way-door list is untouched by this module). Looks at the most
    recent `window` verdicts for this class:
      - fewer than 3 recorded verdicts: 'insufficient_data' (never claim
        earned autonomy from a thin record -- R12-style anti-goal-seek
        applied to this metric too).
      - pass rate >= earn_threshold: 'earned'.
      - otherwise: 'under_review' -- automatically, the moment the record
        says so, with no separate revocation decision required (the
        staged instruction's own 'auto-revoked when quality slips')."""
    recent = entries_for_class(task_class)[-window:]
    if len(recent) < 3:
        return "insufficient_data"
    pass_rate = sum(1 for e in recent if e["verdict"] == Verdict.PASS.value) / len(recent)
    return "earned" if pass_rate >= earn_threshold else "under_review"


def check_grader_capture_tell(task_class: TaskClass, window: int = 10) -> Optional[str]:
    """The one tell the staged instruction names explicitly: rising pass
    rate with FALLING defect-discovery is evidence of grader capture, not
    quality -- comparing the first and second half of the recent window.
    Returns a warning string if the tell is present, else None. Needs at
    least 4 entries to split meaningfully."""
    recent = entries_for_class(task_class)[-window:]
    if len(recent) < 4:
        return None
    mid = len(recent) // 2
    first_half, second_half = recent[:mid], recent[mid:]

    def _pass_rate(batch):
        return sum(1 for e in batch if e["verdict"] == Verdict.PASS.value) / len(batch)

    def _avg_defects(batch):
        return sum(e.get("defects_found_post_close", 0) for e in batch) / len(batch)

    pass_rising = _pass_rate(second_half) > _pass_rate(first_half)
    defects_falling = _avg_defects(second_half) < _avg_defects(first_half)
    if pass_rising and defects_falling and _avg_defects(first_half) > 0:
        return (
            f"GRADER CAPTURE TELL for {task_class.value}: pass rate rose "
            f"({_pass_rate(first_half):.0%} -> {_pass_rate(second_half):.0%}) while "
            f"post-close defect discovery fell ({_avg_defects(first_half):.2f} -> "
            f"{_avg_defects(second_half):.2f} per verdict) -- investigate the grader, "
            "not just the record."
        )
    return None
