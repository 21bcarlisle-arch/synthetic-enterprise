"""Sanity/audit finding adjudication ledger (2026-07-11, director-ordered
sanity triage, from_rich_20260711_044314.md/from_rich_20260711_044335.md).

Every population-sanity/internal-audit finding CATEGORY gets a durable state
-- open / adjudicated-real / adjudicated-false-positive -- with the evidence,
who, and when. This is what lets the alert-discipline layer (background/
sanity_daemon.py) distinguish "we've already looked at this and it's a known
false positive, don't alert on it again" or "we've already looked at this and
it's a confirmed real defect being tracked" from a genuinely NEW category or
a STATE CHANGE, instead of re-alerting every cycle on a fresh random subset
of already-known shapes (the root cause of the alarm-fatigue this ledger
exists to fix).

Director's own framing: "did it catch true C6-class defects or cry wolf?" --
adjudication here is deliberately not a rubber stamp. A category can be
confirmed a defect. See docs/design/SANITY_TRIAGE_2026_07_11.md for the
full triage writeup and evidence behind each verdict landed via adjudicate().
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

LEDGER_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "docs" / "observability" / "sanity_adjudication_ledger.json"
)

AdjudicationState = Literal["open", "adjudicated-real", "adjudicated-false-positive"]
_VALID_STATES = {"open", "adjudicated-real", "adjudicated-false-positive"}


def _resolve_path(path: Path | None) -> Path:
    """Looks up LEDGER_PATH from the module namespace at CALL time, not at
    function-definition time -- a plain `path: Path = LEDGER_PATH` default
    argument binds once at import and would silently ignore a test's
    monkeypatch.setattr(sanity_adjudication, "LEDGER_PATH", tmp_path)."""
    return path if path is not None else LEDGER_PATH


def load_ledger(path: Path | None = None) -> dict[str, dict]:
    path = _resolve_path(path)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def save_ledger(ledger: dict[str, dict], path: Path | None = None) -> None:
    path = _resolve_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ledger, indent=2, sort_keys=True))


def adjudicate(
    finding_key: str, state: AdjudicationState, evidence: str, adjudicated_by: str,
    path: Path | None = None, now: str | None = None,
) -> dict:
    """Record (or re-record, e.g. new evidence overturning a prior verdict)
    one finding category's adjudication. Returns the full entry.

    Re-adjudication is a normal, expected operation, not an error -- a
    category correctly marked false-positive today could show a genuinely
    new instance tomorrow that changes the verdict; the ledger keeps only
    the latest state, `adjudicated_at` records when that latest call was
    made, and the caller's own log/finding doc is the durable history of
    *why* it changed."""
    if state not in _VALID_STATES:
        raise ValueError(f"invalid adjudication state: {state!r}")
    ledger = load_ledger(path)
    entry = {
        "finding_key": finding_key,
        "state": state,
        "evidence": evidence,
        "adjudicated_by": adjudicated_by,
        "adjudicated_at": now or datetime.now(timezone.utc).isoformat(),
    }
    ledger[finding_key] = entry
    save_ledger(ledger, path)
    return entry


def get_entry(finding_key: str, path: Path | None = None) -> dict | None:
    return load_ledger(path).get(finding_key)


def get_state(finding_key: str, path: Path | None = None) -> AdjudicationState | None:
    entry = get_entry(finding_key, path)
    return entry.get("state") if entry else None


def is_known(finding_key: str, path: Path | None = None) -> bool:
    """True if this finding key has ANY recorded adjudication (real or
    false-positive) -- the alert-discipline check: a known category recurring
    is a digest line, not a fresh NTFY."""
    return get_state(finding_key, path) is not None


def malformed_entries(path: Path | None = None) -> list[str]:
    """Ledger keys whose row is not a readable adjudication.

    WHY THIS EXISTS, AND WHY IT IS NOT JUST A `.get()` (2026-08-26, R10/R15).
    `record_adjudication` validates `state` against `_VALID_STATES` and cannot
    write a row without one -- but the ledger is a plain JSON file, and a row
    written into it BY HAND bypasses that writer entirely. One did: the
    2026-08-25 Expert-Hour verdict on `EP13_adapter_carbon_intensity` carried
    `verdict`/`fix`/`method`/`independence` and no `state`, and every reader that
    subscripted `e["state"]` raised `KeyError` on it -- taking down the daily
    sanity digest, which is the mechanism that would otherwise have REPORTED the
    problem. The failure silenced its own alarm.

    The readers above now use `.get()`, which keeps one bad row from felling the
    daemon. On its own that is FAIL-OPEN -- a malformed row would simply vanish
    from `open_findings()` and nobody would ever learn it was there. So the
    tolerance is paired with this detector, and a test asserts the REAL ledger
    has none: the row is skipped by the readers and LOUD in the control, rather
    than silently dropped by both.

    Instance repaired in the same pass; this is the class (R10).

    SCOPED TO THE DEFECT, DELIBERATELY. The predicate is "has no readable state",
    NOT "has a state in `_VALID_STATES`". Those are different claims and only the
    first one is this function's business: `_VALID_STATES` holds three values
    while the live ledger carries eight (`open-confirmed-defect`, `fixed`,
    `superseded`, `open-needs-judgement`, `adjudicated-methodology-note` are all
    in real rows written by hand). That gap is a genuine vocabulary drift between
    the writer's contract and the ledger's practice, and deciding which of the
    two is right is an authoring decision, not a repair -- widening the constant
    here to make this control green would be picking that decision by side
    effect. Left QUEUED and named, per SELF-INTERRUPT DISCIPLINE. A control whose
    scope is wider than its claim reds against a later passer-by for a reason its
    docstring never promised, which is how controls get disabled rather than
    fixed.
    """
    bad = []
    for key, entry in load_ledger(path).items():
        if not isinstance(entry, dict):
            bad.append(key)
        elif not isinstance(entry.get("state"), str) or not entry["state"].strip():
            bad.append(key)
    return sorted(bad)


def open_findings(path: Path | None = None) -> list[dict]:
    return [e for e in load_ledger(path).values() if e.get("state") == "open"]


def all_entries(path: Path | None = None) -> list[dict]:
    return list(load_ledger(path).values())
