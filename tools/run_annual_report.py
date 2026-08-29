"""Composition root — run the simulated world, then report on it.

WHY THIS FILE EXISTS (KNIFE pass 1, atom `KNIFE1_reporting_cycle`, 2026-08-09)
-----------------------------------------------------------------------------
`saas/reporting/annual_report.py` used to import
`simulation.run_phase4c_on_phase2b.main` at module level so that its CLI could
run the world before rendering it. That was a class-(a) crossing — the
strictly-forbidden direction of the epistemic wall (CLAUDE.md, "Architectural
Laws"): the business layer reaching into the simulated world's run harness. It
also closed a mutual-import cycle, because `run_phase4c_on_phase2b` reached
back for `annual_report.extract_report_data` to reduce its own output.

The coupling was never a *reporting* need. `extract_report_data()` and
`generate_annual_report()` are pure functions over a run-output dict, and the
report module's own docstring has said "this module does not run the
simulation" since Phase 5a. What actually needed both layers was the
COMPOSITION — "produce a world, then describe it" — and a composition root
belongs ABOVE both layers, not inside one of them.

`tools/` is that place. It is neither a company-side nor a SIM-side package
(`tests/architecture/test_epistemic_wall_ratchet.py::WALL_DIRS` walks only
`company/`, `saas/`, `sim/`, `simulation/`), and `tools/run_frozen_baseline.py`
already established the pattern of a harness script importing the run entry
point directly.

Note the shape of the fix, because it is the reusable part: the cut is NOT a
lazy import or an indirection that hides the same edge from the AST walker.
Both reporting modules genuinely no longer name `simulation` at all — importing
`saas.reporting.annual_report` no longer imports the simulation, in a script
context or any other. Laundering an edge through a module the walker does not
walk would have moved the measurement, not the dependency.

WHAT MOVED HERE
---------------
  * `annual_report.main()`'s simulation-running branch (this file's `main()`).
  * `annual_report._run_and_extract()`.
  * `run_phase4c_on_phase2b.save_run_output_json()` and its `_git_commit_hash`
    helper, plus the `RUN_OUTPUT_*` paths they write — the return edge. Saving
    the *reduced report data* is a reporting concern that the run module had
    absorbed; it is the reason the cycle existed at all.

WHAT STAYED
-----------
`python3 -m saas.reporting.annual_report` is still the RENDER-only CLI
(`--from-json` / cached data → markdown), unchanged, because that path never
needed the simulation. Only the run path moved:

    python3 -m tools.run_annual_report [--fast] [--end-year YYYY]
                                       [--save-json PATH] [--output PATH]
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from saas.reporting.annual_report import (
    DEFAULT_REPORT_DATA_PATH,
    DEFAULT_REPORT_PATH,
    LEDGER_LATEST_PATH,
    extract_report_data,
    generate_annual_report,
)
from simulation.run_phase4c_on_phase2b import main as run_phase4c_on_phase2b
from simulation.settlement_clocks import reconcile_published_run_output

# Where a run persists its reduced report data. Moved here from
# `simulation/run_phase4c_on_phase2b.py` with `save_run_output_json()`.
RUN_OUTPUT_LATEST_PATH = Path("docs/reports/run_output_latest.json")
RUN_OUTPUT_VERSIONED_DIR = Path("docs/reports")


def _git_commit_hash() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:
        return "unknown"


def _send_run_complete_ntfy(data: dict, report_path: Path) -> None:
    # Removed: per-run NTFYs from the report run are spam (one run every ~17min).
    # Claude picks up results via run_complete_*.md staging markers instead.
    pass


def _run_and_extract(report_end: str | None = None) -> dict:
    run_output = run_phase4c_on_phase2b(report_end=report_end)
    return extract_report_data(run_output)


def save_run_output_json(run_output: dict) -> tuple[Path, Path]:
    """Reduce `run_output` via `annual_report.extract_report_data()` and
    persist it to `docs/reports/run_output_latest.json` plus a versioned
    copy stamped with the current git commit hash and UTC timestamp.

    Returns (latest_path, versioned_path).
    """
    data = extract_report_data(run_output)

    # THE PAGE MUST ADD UP BEFORE IT IS WRITTEN (2026-08-28, class
    # `figures_on_a_superseded_clock`, R14). `run_output_latest.json` is what
    # `site/data/supplier.json` and `site/data/agent_status.json` are built from, so a figure on
    # a superseded clock leaving this function reaches a reader who can check it with a
    # calculator -- which is exactly what happened: the file published
    # `starting_treasury_gbp + total_net_gbp` GBP 39,962.17 above its own `final_treasury_gbp`
    # for two days. The check lives HERE and not in `saas/reporting/annual_report.py` because
    # `saas/` never imports `simulation/`, and it reads the artefact's own published figures --
    # never the phase2b scalars that produced them, which would be R15's tautology.
    #
    # It RAISES rather than warning. A run that cannot state a consistent treasury has nothing
    # publishable to say about its own solvency, and the failure mode this replaces was two
    # silent days.
    unreconciled = reconcile_published_run_output(data)
    if unreconciled:
        raise ValueError(
            "refusing to publish a run output whose own figures do not reconcile:\n  - "
            + "\n  - ".join(unreconciled)
        )

    commit_hash = _git_commit_hash()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    data["_cache_meta"] = {
        "git_commit": commit_hash,
        "generated_at_utc": timestamp,
    }

    RUN_OUTPUT_VERSIONED_DIR.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2)

    RUN_OUTPUT_LATEST_PATH.write_text(payload)
    versioned_path = RUN_OUTPUT_VERSIONED_DIR / f"run_output_{commit_hash}_{timestamp}.json"
    versioned_path.write_text(payload)

    return RUN_OUTPUT_LATEST_PATH, versioned_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the simulation and generate the annual report from it"
    )
    parser.add_argument("--save-json", type=Path, default=DEFAULT_REPORT_DATA_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument(
        "--end-year",
        type=int,
        default=None,
        metavar="YYYY",
        help="Truncate the simulation window at Dec 31 of this year (e.g. 2020). "
        "Useful for fast iteration on early years without running the full window.",
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Set SIM_FAST_MODE=1: use the deterministic mock risk committee "
        "(no LLM calls). Cuts per-run time from ~hours to ~minutes.",
    )
    args = parser.parse_args()

    if args.fast:
        os.environ["SIM_FAST_MODE"] = "1"
        print("[FAST MODE] SIM_FAST_MODE=1 — deterministic mock committee, no LLM calls.")

    report_end = f"{args.end_year}-12-31" if args.end_year else None
    if report_end:
        print(f"[TRUNCATED] Simulation window truncated to {report_end}.")

    raw_output = run_phase4c_on_phase2b(report_end=report_end)
    data = extract_report_data(raw_output)
    args.save_json.parent.mkdir(parents=True, exist_ok=True)
    args.save_json.write_text(json.dumps(data, indent=2))

    fresh_full_run = not args.fast and not report_end
    if fresh_full_run:
        ledger_events = raw_output.get("ledger_events", [])
        if ledger_events:
            LEDGER_LATEST_PATH.parent.mkdir(parents=True, exist_ok=True)
            LEDGER_LATEST_PATH.write_text(json.dumps(ledger_events, indent=2))
            print(f"Wrote {LEDGER_LATEST_PATH} ({len(ledger_events):,} events)")
        _send_run_complete_ntfy(data, args.output)

    report = generate_annual_report(data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report)
    print(f"Wrote {args.output} ({len(report)} chars, {len(data['years'])} years)")


if __name__ == "__main__":
    main()
