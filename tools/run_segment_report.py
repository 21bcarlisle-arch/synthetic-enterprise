"""Composition root — run the segment simulation, then report on it.

Companion to `tools/run_annual_report.py`, same cut, same reason (KNIFE pass 1,
atom `KNIFE1_reporting_cycle`, 2026-08-09). `saas/reporting/segment_report.py`
imported `simulation.run_segments.main` inside its CLI: a class-(a) crossing —
the business layer running the simulated world. The import was function-local,
which hid nothing: the epistemic-wall ratchet's AST walker sees lazy imports
exactly as it sees module-level ones, and listed the edge alongside the
module-level one in `annual_report`.

`extract_segment_data()` and `generate_segment_report()` are pure functions over
a run-output dict. Only the composition needed both layers, so the composition
moved above both.

`python3 -m saas.reporting.segment_report --from-json PATH` is still the
RENDER-only CLI. The run path is here:

    python3 -m tools.run_segment_report [--save-json PATH] [--output PATH]
                                        [--end-year YYYY]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from saas.reporting.segment_report import (
    DEFAULT_REPORT_PATH,
    extract_segment_data,
    generate_segment_report,
)
from tools.run_segments import main as run_segments


def _save_json(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Run output saved → {path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the segment simulation and generate its portfolio annual report"
    )
    parser.add_argument("--save-json", metavar="PATH", help="save run output for re-use")
    parser.add_argument("--output", metavar="PATH", default=str(DEFAULT_REPORT_PATH))
    parser.add_argument("--end-year", metavar="YYYY", help="truncate report at this year")
    args = parser.parse_args()

    print("Running segment simulation…")
    run_output = run_segments()

    if args.save_json:
        _save_json(run_output, Path(args.save_json))

    data = extract_segment_data(run_output)
    report = generate_segment_report(data, end_year=args.end_year)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report)
    print(f"Segment report written → {out_path}")


if __name__ == "__main__":
    main()
