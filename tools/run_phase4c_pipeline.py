"""Standalone CLI for the combined Phase 2b+4b+4c pipeline.

Moved out of `simulation/run_phase4c_on_phase2b.py`'s `if __name__ ==
"__main__"` block (KNIFE pass 1, atom `KNIFE1_reporting_cycle`, 2026-08-09).

That block was a COMPOSITION, not a simulation: it ran the world, reduced the
result through `saas.reporting.annual_report.extract_report_data()`, and wrote
the `run_pending_*` / `run_complete_*` staging markers the publishing loop acts
on. Reducing a run through the report's extractor is what forced
`simulation.run_phase4c_on_phase2b -> saas.reporting.annual_report`, the return
edge that closed the reporting import cycle — the lazy import there carried a
comment naming the cycle it was working around. Removing the cycle removes the
need for the workaround.

`simulation/run_phase4c_on_phase2b.py` is now a pure library: `main()` runs the
pipeline and returns its output dict, and the module has no CLI. It does still
import 14 company-side packages directly — class-(b) crossings that KNIFE
passes 2 and 3 own. This pass removed the `saas.reporting` edge only, because
that is the one that closed the CYCLE.

    python3 -m tools.run_phase4c_pipeline [--save-json]

`save_run_output_json()` itself lives in `tools/run_annual_report.py` alongside
the rest of the run-and-report composition; this CLI calls it.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from simulation.run_phase4c_on_phase2b import main
from tools.run_annual_report import save_run_output_json


def cli() -> None:
    parser = argparse.ArgumentParser(description="Run the combined Phase 2b+4b+4c pipeline")
    parser.add_argument(
        "--save-json", action="store_true",
        help="Persist the reduced report data to docs/reports/run_output_latest.json "
        "plus a versioned copy stamped with the git commit hash and timestamp",
    )
    args = parser.parse_args()

    _staging_dir = Path("docs/staging")
    _staging_dir.mkdir(parents=True, exist_ok=True)
    _run_ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    _pending_marker = _staging_dir / f"run_pending_{_run_ts}.md"
    _pending_marker.write_text(
        f"# Run in progress — action required on completion\n\n"
        f"Started: {_run_ts}\n\n"
        "When this run finishes: regenerate the annual report (`make report` or "
        "`python3 -m saas.reporting.annual_report --from-json docs/reports/run_output_latest.json`), "
        "update LATEST.md with key figures, commit, push to GitHub, and send NTFY digest.\n\n"
        "Delete this file once done.\n"
    )

    try:
        output = main()

        if args.save_json:
            latest_path, versioned_path = save_run_output_json(output)
            print(f"\nSaved report data to {latest_path} and {versioned_path}")

        # Write a completion marker so the next session knows results are ready to publish
        _complete_marker = _staging_dir / f"run_complete_{_run_ts}.md"
        _complete_marker.write_text(
            f"# Run complete — publish results\n\n"
            f"Completed: {datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}\n"
            f"Output: {latest_path if args.save_json else 'not saved (no --save-json)'}\n\n"
            "Action: regenerate annual report, update LATEST.md, commit, push, send NTFY.\n\n"
            "Delete this file once done.\n"
        )
        _pending_marker.unlink(missing_ok=True)

    except Exception as exc:
        import traceback

        from background.ntfy_utils import send_ntfy
        err_summary = f"{type(exc).__name__}: {exc}"
        send_ntfy(
            f"Run FAILED at save/extract step: {err_summary}\n"
            "Sim itself may have completed — check phase*_run.log",
            headers={"X-Priority": "5", "X-Tags": "rotating_light"},
        )
        traceback.print_exc()
        raise


if __name__ == "__main__":
    cli()
