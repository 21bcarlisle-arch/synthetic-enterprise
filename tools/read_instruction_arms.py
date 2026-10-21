"""Run one arm of the SLC 21B.4 read instruction in the published run, to a named run output.

REUSE: tools/read_instruction_arms.py
CLASS: CUSTOM
INDEX: searched "instructed read arm", "run output arms", "save run output". `tools/run_annual_report`
       is the publishing path and its `reconcile_and_stamp` / `dump_run_output` are REUSED, not
       paralleled; what it cannot do is turn the switch on or write anywhere but the published
       paths. `tools/move_with_us_arms.py` is the arms template; it keeps a summary, and the
       instrument here (`tools.closing_estimate_run_money --read-duty`) needs the whole run output.

ARMS (pre-registered in `docs/staging/records/
WORKER_PREREG_THE_READ_INSTRUCTION_ON_A_PUBLISHED_RUN_AT_BOTH_ACCESS_ENDS_2026-10-18.md`):
  * `off`      -- the standing policy, unchanged. The one-variable control at this commit.
  * `register` -- `instruct_reads_in_billing_run=True`, the no-access end: while
                  `q6_read_visit_access_failure_rate` is null the visit finds no access.
  * `ceiling`  -- the same policy, and every instructed visit reads. A bound, never published.

THE SWITCH IS TURNED ON IN `run_phase2b.CURRENT_POLICY`, not only handed to `main`: the DD review and
the collection book's stop notice rebuild bills with no policy and take the standing one's switch
(`run_phase4c_on_phase2b.read_instruction_request`). This process only; the default in
`company/policy/decision_policy.py` is not touched.

    python3 -m tools.read_instruction_arms <off|register|ceiling> <out.json>
"""
from __future__ import annotations

import argparse
import dataclasses
from datetime import datetime, timezone
from pathlib import Path

ARMS = ("off", "register", "ceiling")


def run_arm(arm: str, out: Path) -> Path:
    if arm not in ARMS:
        raise SystemExit(f"REFUSED: arm {arm!r} is not one of {ARMS}")
    import simulation.run_phase2b as rp2b
    from company.policy.decision_policy import policy_scope
    from simulation.run_phase4c_on_phase2b import main

    # The publishing path's own reduction, taken through it: the run output is the bytes a publish
    # writes, and a report module is a rendering nothing else imports.
    from tools.run_annual_report import (
        _git_commit_hash,
        dump_run_output,
        extract_report_data,
        reconcile_and_stamp,
    )

    policy = dataclasses.replace(rp2b.CURRENT_POLICY, instruct_reads_in_billing_run=(arm != "off"))
    rp2b.CURRENT_POLICY = policy  # this process only; see the module docstring
    code_commit = _git_commit_hash()
    code_commit_at = datetime.now(timezone.utc)
    with policy_scope(policy):
        raw = main(policy=policy, instructed_read_arm="ceiling" if arm == "ceiling" else "register")
    data = reconcile_and_stamp(extract_report_data(raw), code_commit=code_commit, report_end=None,
                               code_commit_at=code_commit_at)
    data["_read_instruction_arm"] = arm
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(dump_run_output(data))
    return out


def cli() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("arm", choices=ARMS)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    print(f"wrote {run_arm(args.arm, args.out)}")


if __name__ == "__main__":
    cli()
