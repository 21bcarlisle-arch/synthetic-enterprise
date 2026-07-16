"""The decision log — writes itself, not discipline-written (MAKE_IT_STICK.md
item 3: "hook-written, not discipline-written: what, why, confidence, how to
reverse. Surfaced in digest + Director door.").

Mechanism, not memory: `decide()` is the ONE call site that both classifies
an action against the one-way-door predicate (background/one_way_door.py)
AND writes the log entry as a side effect of that same call -- there is
nothing separate to remember. A caller who runs every non-trivial choice
through `decide()` gets logging for free; a caller who doesn't is the thing
the decay audit (CLAUDE.md, epoch boundaries) is meant to catch.

Storage: append-only JSONL at docs/observability/decision_log.jsonl, same
convention as the project's other observability logs (lane_hook_denials.jsonl,
test_execution_log.jsonl) -- one line per entry, never rewritten in place.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from background.one_way_door import OneWayDoorCategory, OneWayDoorVerdict, classify_action

PROJECT_DIR = Path(__file__).resolve().parent.parent
DECISION_LOG_PATH = PROJECT_DIR / "docs" / "observability" / "decision_log.jsonl"


def log_decision(
    what: str,
    why: str,
    how_to_reverse: str,
    *,
    reversible: bool = True,
    confidence: str = "confident",
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Low-level append. Prefer `decide()` below for real call sites --
    this is exposed directly for the rare case where the one-way-door check
    already happened elsewhere (e.g. an explicit_category was pre-decided)
    and only the logging is needed."""
    entry = {
        "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
        "what": what,
        "why": why,
        "how_to_reverse": how_to_reverse,
        "reversible": reversible,
        "confidence": confidence,
    }
    DECISION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DECISION_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")
    return entry


def decide(
    what: str,
    why: str,
    how_to_reverse: str = "git revert the commit(s); atoms/levels re-rank on the next self-refill draw",
    *,
    uncertain: bool = False,
    explicit_category: OneWayDoorCategory | None = None,
) -> OneWayDoorVerdict:
    """THE call site: classify `what` against the one-way-door predicate,
    and if it is NOT a one-way door, log it automatically and return the
    verdict so the caller can proceed. If it IS a one-way door, the verdict
    is returned WITHOUT logging a proceed-entry -- the caller must escalate
    (to the director, or the twin once built), never act on it."""
    verdict = classify_action(what, explicit_category=explicit_category, uncertain=uncertain)
    if not verdict.is_one_way_door:
        # ONE_WAY_DOOR_DEFAULTS_TO_ACT.md rule 2: an ambiguous-reversible proceed (the caller
        # was unsure but nothing provably matched a wall) is still recorded -- flagged as such
        # so the audit trail distinguishes it from a plainly-clear reversible action.
        confidence = "ambiguous_reversible" if verdict.ambiguous_reversible_proceed else "confident"
        log_decision(what, why, how_to_reverse, reversible=True, confidence=confidence)
    return verdict


def read_decision_log() -> list[dict[str, Any]]:
    if not DECISION_LOG_PATH.exists():
        return []
    entries = []
    for line in DECISION_LOG_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def count_since(since_iso: str) -> int:
    """Anti-decay metric input: how many decisions logged since a given
    ISO timestamp -- used for the digest's decision-volume line."""
    since_dt = datetime.fromisoformat(since_iso)
    count = 0
    for entry in read_decision_log():
        try:
            entry_dt = datetime.fromisoformat(entry["timestamp"])
        except (KeyError, ValueError):
            continue
        if entry_dt >= since_dt:
            count += 1
    return count
