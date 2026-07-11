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
    return entry["state"] if entry else None


def is_known(finding_key: str, path: Path | None = None) -> bool:
    """True if this finding key has ANY recorded adjudication (real or
    false-positive) -- the alert-discipline check: a known category recurring
    is a digest line, not a fresh NTFY."""
    return get_state(finding_key, path) is not None


def open_findings(path: Path | None = None) -> list[dict]:
    return [e for e in load_ledger(path).values() if e["state"] == "open"]


def all_entries(path: Path | None = None) -> list[dict]:
    return list(load_ledger(path).values())
