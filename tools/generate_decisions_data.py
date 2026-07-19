#!/usr/bin/env python3
"""Generate site/data/decisions.json -- the Journey door's Decisions tab.

Director console 2026-07-19, gate-after model item 6: "observability is now
load-bearing and part of every turn's definition-of-done" -- the decision
ledger (`background/decision_log.py`, MAKE_IT_STICK.md item 3: "hook-written,
not discipline-written: what, why, confidence, how to reverse") is a healthy
backend with NOTHING on the site rendering it. This closes that gap.

This is a pure RENDERING of the real append-only ledger at
docs/observability/decision_log.jsonl (via `background.decision_log.
read_decision_log()`) -- never an author, never a curated subset (SITE
CONSTITUTION rule: the site renders reality, it doesn't select a flattering
slice of it).

Fail-closed (R15 FAIL-OPEN killer pattern): a missing or empty ledger emits
`available: false` with `count: 0` and an empty `decisions` list, so the door
can render a visible "no decisions logged" state -- never a silently-blank
section that reads as "everything is fine, nothing to see."
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT))  # so `background.*` imports resolve when run directly

from background.decision_log import DECISION_LOG_PATH, read_decision_log  # noqa: E402

OUTPUT_PATH = PROJECT / "site" / "data" / "decisions.json"
SOURCE_REL = "docs/observability/decision_log.jsonl"


def derive_decisions(
    log_path: Path | None = None,
    now: datetime | None = None,
) -> dict:
    """Assemble the Decisions-tab payload from the real decision ledger.

    `log_path` is injectable (defaulting to the live ledger) so an R15
    independence test can point it at a mutated fixture and assert the
    emitted JSON follows -- proving this is a rendering, not a relocated
    hardcode. Entries are newest-first (the ledger itself is append-only,
    oldest-first on disk).
    """
    log_path = Path(log_path) if log_path is not None else DECISION_LOG_PATH
    entries = read_decision_log() if log_path == DECISION_LOG_PATH else _read_log(log_path)

    now = now or datetime.now(timezone.utc)
    generated_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    if not entries:
        return {
            "generated_at": generated_at,
            "source": SOURCE_REL,
            "available": False,
            "count": 0,
            "decisions": [],
            "note": "no decisions logged -- the ledger is empty or missing",
        }

    decisions = [
        {
            "timestamp": e.get("timestamp"),
            "what": e.get("what"),
            "why": e.get("why"),
            "how_to_reverse": e.get("how_to_reverse"),
            "reversible": e.get("reversible"),
            "confidence": e.get("confidence"),
        }
        for e in entries
    ]
    # Newest first: the ledger is append-only oldest-first, so reverse it.
    decisions = list(reversed(decisions))

    return {
        "generated_at": generated_at,
        "source": SOURCE_REL,
        "available": True,
        "count": len(decisions),
        "decisions": decisions,
    }


def _read_log(path: Path) -> list[dict]:
    """Same parse as `background.decision_log.read_decision_log`, but against
    an injectable path -- used only by the R15 independence test fixture."""
    if not path.exists():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def main() -> None:
    data = derive_decisions()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(data, indent=2) + "\n")
    print(
        f"Wrote {OUTPUT_PATH.relative_to(PROJECT)}: "
        f"available={data['available']}, count={data['count']}"
    )


if __name__ == "__main__":
    main()
