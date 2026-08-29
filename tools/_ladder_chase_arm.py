"""Run ONE arm of the chase-on/chase-off ladder pair, in its own process.

Separate process per arm, not a loop: `aggression()` reads a module-level path and the two arms
need different ones, so running them in one interpreter would make the second arm's world depend
on whether the first had already imported anything. The override is asserted to have TAKEN before
the run starts -- an override that silently failed would report the chase as costing nothing,
which is the fail-silent shape that turns the whole comparison into a confident null.

Usage: python3 -m tools._ladder_chase_arm <on|off> <out.json> [end_year]

THE WINDOW IS AN ARGUMENT BECAUSE THE WINDOW WAS THE ANSWER. The 2026-08-28 pair ran `--end-year
2019` and the derived competitive-pressure channel moved at one rung in four. The reason was not
weak evidence: `CompetitivePressureLedger._closed_window` reads years STRICTLY EARLIER than the
renewal being priced, so a departure in the final year of the window is never priced against and
buys nothing. The chase's extra departures fell in 2019. Running the same pair with a later
`end_year` is therefore not "more data" -- it is the one declared change that lets the evidence
already being generated reach a decision.

IT ALSO WRITES A PER-YEAR LEDGER CENSUS beside the artefact (`<out>.ledger_census.json`), one
entry per run in the arm (the flat-rules control first, then each rung in order). Without it the
reader can see that a rung moved but not WHERE the evidence was available and where it was
wasted, and "the count did not cross" is indistinguishable from "the count crossed in a year
nothing is priced after". It reads the real ledger objects the run accumulated -- it does not
synthesise a count -- and it is a diagnostic wrapper in `tools/`, so nothing the company reads
changes.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

#: The source the two arms must agree on. A chase pair claims "one tree, identical seeds, ONE
#: declared parameter differing" -- and when the arms run SEQUENTIALLY (they must: the ladder
#: retains every rung's settlement records, so two arms at once exhaust the guest) another lane
#: can land work between them. Then the pair is a comparison of two trees wearing one label, and
#: nothing in the artefacts would say so. Recorded per arm; `compare_chase_belief` refuses a pair
#: whose fingerprints differ.
_TREE_SUBJECT = (
    "simulation/run_phase2b.py",
    "simulation/customer_events.py",
    "simulation/competitor_reference.py",
    "simulation/live_population.py",
    "simulation/net_new_acquisition.py",
    "company/crm/competitive_pressure.py",
    "company/crm/churn_model.py",
    "company/crm/market_conditions.py",
    "company/pricing/value_based_renewal.py",
    "tools/run_price_ladder.py",
    "docs/design/FOUNDER_BOOK.yaml",
    "docs/design/COMPETITOR_AGGRESSION.yaml",
)


def _tree_fingerprint() -> dict:
    """What this arm actually ran against -- the WORKING TREE, not HEAD.

    HEAD alone would be a lie on a shared worktree: every run here happens over other lanes'
    uncommitted work, and it is the bytes on disk that decide the result.
    """
    digest = hashlib.sha256()
    missing = []
    for rel in _TREE_SUBJECT:
        path = REPO / rel
        if not path.exists():
            missing.append(rel)
            continue
        digest.update(rel.encode())
        digest.update(path.read_bytes())
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    return {"head": head, "subject_sha256": digest.hexdigest(), "missing": missing,
            "files": list(_TREE_SUBJECT)}


def main() -> int:
    arm, out = sys.argv[1], sys.argv[2]
    end_year = sys.argv[3] if len(sys.argv) > 3 else "2019"

    import simulation.competitor_reference as cr

    if arm == "off":
        cr.AGGRESSION_PATH = REPO / "docs" / "observability" / "aggression_chase_off.yaml"

    chase = cr.aggression()["chase_per_quarter"]
    expected = 0.0 if arm == "off" else 0.5
    if chase != expected:
        print(f"REFUSED: arm={arm} expected chase_per_quarter={expected}, got {chase}")
        return 2
    print(f"[{arm}] chase_per_quarter={chase} CONFIRMED before the run, window ends {end_year}")

    fingerprint_before = _tree_fingerprint()
    print(f"[{arm}] tree {fingerprint_before['head'][:9]} "
          f"subject {fingerprint_before['subject_sha256'][:12]}")

    import simulation.run_phase2b as rp2b

    census: list[dict] = []
    # `run_phase2b` did `from ... import pressure_ledger_scope`, so the name is bound in ITS
    # module namespace -- patching the definition site would be read past by the caller.
    original_scope = rp2b.pressure_ledger_scope

    @contextlib.contextmanager
    def observing_scope(ledger=None):
        with original_scope(ledger) as active:
            try:
                yield active
            finally:
                census.append({
                    "armed": active.loss_reporting_armed,
                    "decisions_by_year": dict(sorted(active.decisions_by_year.items())),
                    "predicted_losses_by_year": {
                        y: round(v, 4) for y, v in sorted(active.expected_by_year.items())},
                    "realised_losses_by_year": dict(sorted(active.losses_by_year.items())),
                })

    rp2b.pressure_ledger_scope = observing_scope

    from tools.run_price_ladder import main as ladder_main

    rungs = "0,0.5,1,2"
    rc = ladder_main(
        ["--end-year", end_year, "--rungs", rungs, "--out", out]) or 0

    census_path = Path(out).with_suffix(".ledger_census.json")
    census_path.write_text(json.dumps({
        "arm": arm,
        "chase_per_quarter": chase,
        "end_year": end_year,
        "rungs": [float(x) for x in rungs.split(",")],
        "tree_before": fingerprint_before,
        # Taken AFTER the run as well: an arm that took 25 minutes can be overtaken mid-run by a
        # lane landing work, and only the pair of fingerprints can say the arm saw one tree.
        "tree_after": _tree_fingerprint(),
        "run_order": "flat-rules control, then rungs 0.0, 0.5, 1.0, 2.0",
        "why_the_last_year_is_dead": (
            "the ledger reads years strictly earlier than the renewal being priced, so a "
            "departure in the final year of the window is never evidence for anything"),
        "runs": census,
    }, indent=2), encoding="utf-8")
    print(f"[{arm}] ledger census -> {census_path} ({len(census)} run(s))")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
