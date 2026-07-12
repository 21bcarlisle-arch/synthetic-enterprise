#!/usr/bin/env python3
"""Generate site/data/director_twin.json from the real Q&A log
(DIRECTOR_TWIN.md DoD: "Q&A log live in digest + site"). A first, minimal
surface placed on the Journey door (site/project/) alongside the Provisional
Plan panel -- a dedicated top-level "Director door" nav section is
registered as a follow-up, not built in this pass (a site-navigation change
is a more consequential, user-facing decision than bolting a panel onto an
existing page).
"""
import json
from pathlib import Path

from background.director_twin import _read_jsonl, fidelity_metric, TWIN_LOG_PATH, OVERTURNS_LOG_PATH

PROJECT = Path(__file__).resolve().parent.parent
OUT_PATH = PROJECT / "site" / "data" / "director_twin.json"


def main():
    entries = _read_jsonl(TWIN_LOG_PATH)
    overturns = _read_jsonl(OVERTURNS_LOG_PATH)
    overturned_ids = {o["entry_id"] for o in overturns}

    recent = []
    for e in entries[-20:]:
        recent.append({
            "entry_id": e.get("entry_id"),
            "question": e.get("question"),
            "routed_to_director": e.get("routed_to_director"),
            "answer": e.get("answer"),
            "category": e.get("category"),
            "latency_seconds": e.get("latency_seconds"),
            "overturned": e.get("entry_id") in overturned_ids,
        })

    data = {
        "fidelity": fidelity_metric(),
        "recent_qa": list(reversed(recent)),
        "note": ("Builder-facing twin only (DIRECTOR_TWIN.md) -- answers the agent's sequencing/"
                 "scope/design questions from a fixed canon (docs/design/DIRECTOR_CANON.md), cold-eyes "
                 "(separate context), never learning from outcomes (Law B). One-way-door questions "
                 "(above all: the Epoch-4 fitness function) always route here as 'routed_to_director', "
                 "never answered by the twin."),
    }
    OUT_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Generated {OUT_PATH} ({len(recent)} recent entries)")


if __name__ == "__main__":
    main()
