#!/usr/bin/env python3
"""THE STANDING-RED LEDGER'S HISTORICAL REPLAY — the analysis, moved off the supervisor's side.

WHY IT IS HERE AND NOT IN `background/publish_standing_red.py`, WHERE IT WAS WRITTEN
------------------------------------------------------------------------------------
The replay is right to read the log through `commit_refusal_attribution.cycles` — that module
owns the log's vocabulary, and a private reader would drift from the gates it names with the
drift invisible. What it cannot do is hold that import from a module the SUPERVISOR reaches.

`background/publish_scope.py` derives the publish gate's blocking scope by walking the import
graph backwards from the six modules that produce or render a published number. One of those is
`background/process_run_complete.py`. The chain the replay armed, measured on the real graph at
5c7b1d78f:

    background/supervisor.py
        -> background/staging_rooms.py            (the RUNG-1 draw)
        -> background/publish_standing_red.py     (the ledger it draws from)
        -> tools/commit_refusal_attribution.py    (the replay's parser -- THIS EDGE)
        -> background/process_run_complete.py     (a publish-path source)

That put the entire harness self-governance suite back inside the publish gate — the same
defect `background/publish_gate_blocking_read.py` was cut to end in the 2026-08-21 outage, one
import later, and it wedged publishing for 725 minutes.

The cut is at the edge that is actually wrong. The ledger (`record_refusal`, `standing`,
`drawable`) is live supervisor-side machinery and stays there. The replay is an ANALYSIS of that
ledger over a retained log — CLI and test only, reached by no live path — so it belongs on the
analysis side, where importing the publisher's parser costs nothing. Direction reversed: this
module imports the ledger; the ledger no longer imports anything.

THE ONE COST, STATED. `tests/background/test_a_standing_red_becomes_work_instead_of_a_retry.py`
imports this module for the three replay controls, so THAT ONE TEST FILE is now inside the
publish gate's scope — truthfully, since it does exercise the publisher's parser. One test file,
against the dozens the supervisor edge dragged in. If those three controls ever grow slow enough
to matter, split them into their own file rather than reinstating the edge.

REUSE: tools/standing_red_replay.py
CLASS: CUSTOM
INDEX: searched "replay", "standing red", "ledger replay" — the only implementation is the one
       relocated here whole from `background/publish_standing_red.replay`, byte-for-byte in its
       body. Nothing is reimplemented; the module exists to change WHICH SIDE OF THE IMPORT
       GRAPH the analysis sits on, which is a fact about placement and cannot be expressed by
       reusing an existing home (both candidate homes -- the ledger and the parser -- are
       exactly the two ends of the edge being cut).
"""
from __future__ import annotations

import json
from pathlib import Path

from background.publish_standing_red import (
    STANDING_AFTER_CYCLES,
    empty_ledger,
    record_landing,
    record_refusal,
    standing,
)
from tools.commit_refusal_attribution import LANDED, RED_TEST, cycles

DEFAULT_LOG = "docs/observability/sim-runner-log.md"


def replay(log_text: str, *, threshold: int = STANDING_AFTER_CYCLES) -> dict:
    """Run the retained runner log through the ledger and report what it WOULD have escalated.

    Pre-registered before it was written (SEAT_PREREGISTRATION_WHAT_A_STANDING_RED_LEDGER_WOULD_
    HAVE_ESCALATED_OVER_THE_REAL_LOG_2026-09-05.md), with the threshold already fixed, so no
    number below can have been tuned to make the answer flattering.

    It reads the log through `commit_refusal_attribution.cycles`, which is the publisher's OWN
    parser reached through the module that already owns the log's vocabulary. A private reader
    here would drift from the gates it names and the drift would be invisible.

    ONE HONEST LIMIT, stated rather than smoothed. `cycles()` reports `subject: None` -- not an
    empty set -- when the log's retained 40-line window cut above the summary. Those refusals are
    counted in `unknown_subject` and fold NOTHING, so the replay's ages are a LOWER BOUND on what
    the live ledger will see. The live path does not have this limit: it reads both streams in
    full at the moment of refusal, which is exactly the buffer the log truncates.
    """
    ledger, peak, escalations, unknown = empty_ledger(), {}, 0, 0
    discharges, non_empty_discharges, folded_nothing = 0, 0, 0
    for cyc in cycles(log_text):
        if cyc["outcome"] == LANDED:
            if ledger.get("tests"):
                non_empty_discharges += 1
            discharges += 1
            ledger = record_landing(ledger=ledger)
            continue
        if cyc["cause"] == RED_TEST and cyc["subject"] is None:
            unknown += 1
        was = set(standing(ledger, threshold))
        subject = (sorted(cyc["subject"])
                   if cyc["cause"] == RED_TEST and cyc["subject"] else [])
        if not subject:
            folded_nothing += 1
        ledger = record_refusal(subject, ledger=ledger)
        escalations += len(set(standing(ledger, threshold)) - was)
        for node, row in (ledger.get("tests") or {}).items():
            peak[node] = max(peak.get(node, 0), int(row.get("cycles_blocked") or 0))
    return {
        "threshold": threshold,
        "escalated_nodes": sorted(peak, key=lambda n: (-peak[n], n))[:20],
        "escalated_distinct": sum(1 for v in peak.values() if v >= threshold),
        "escalation_events": escalations,
        "worst_cycles_blocked": max(peak.values(), default=0),
        "landings_seen": discharges,
        "landings_that_discharged_something": non_empty_discharges,
        "red_test_refusals_with_no_readable_subject": unknown,
        # A non-test gate refuses without any test returning a verdict, so it HAS no test subject
        # and must fold none. If this is ever zero the parser is finding tests where there are
        # none, which is worse than finding none -- see `record_refusal`.
        "refusals_that_folded_no_subject": folded_nothing,
        "refusals_folded": ledger.get("refusals") or 0,
        "peak": peak,
    }


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(
        description="Replay a retained runner log through the standing-red ledger and print "
                    "what it would have escalated (the pre-registered measurement).")
    ap.add_argument("log", nargs="?", default=DEFAULT_LOG)
    args = ap.parse_args(argv)
    rep = replay(Path(args.log).read_text(errors="replace"))
    nodes = rep.pop("escalated_nodes")
    peak = rep.pop("peak")
    print(json.dumps(rep, indent=2))
    print("\nTop standing reds, by the most cycles they ever stood:")
    for n in nodes:
        print("  {:>3}  {}".format(peak[n], n))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
