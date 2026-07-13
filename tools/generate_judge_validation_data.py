#!/usr/bin/env python3
"""Generate site/data/judge_validation.json -- the published metric for
JUDGING_THE_JUDGES.md Part 1 (director P1, 2026-07-13).

Publishes all four judge-validation approaches (outcome correlation, gold set,
consistency, independence) from `background.judge_validation.summary()`, which
reads the real trust ledger and the frozen gold set. This is the site face of
the standing rule: no verdict-producing organ escapes measurement.

DIAGNOSTIC ONLY (Law A): these numbers describe the judges, they never tune them.
"""
import json
from pathlib import Path

from background.judge_validation import summary

PROJECT = Path(__file__).resolve().parent.parent
OUT_PATH = PROJECT / "site" / "data" / "judge_validation.json"


def main():
    data = summary()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    oc = data["outcome_correlation"]["overall"]
    gs = data["gold_set"]
    print(f"Generated {OUT_PATH}")
    print(f"  outcome-correlation: {oc['passes']} PASS verdicts, "
          f"{oc['passes_with_later_defect']} later defective, error_rate={oc['error_rate']}")
    print(f"  gold set: {len(gs['cases'])} director cases; "
          f"rubber-stamp recall={gs['rubber_stamp_baseline']['recall']}, "
          f"oracle recall={gs['oracle_ceiling']['recall']}")


if __name__ == "__main__":
    main()
