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

    python3 -m tools.read_instruction_arms <off|register|ceiling> <out.json> [--annualised-advance]
        [--gas-nine-month-floor]

`--annualised-advance` / `--three-read-estimate` (2026-10-22) set `bill_estimate_reads_the_annualised_advance`
on or off the same way and in this process only: `register` with each is the one-variable pair of
`docs/staging/records/WORKER_PREREG_THE_BILL_ESTIMATE_READS_THE_ANNUALISED_ADVANCE_2026-10-22.md`.
With neither, the arm runs the standing policy, which has it ON since the director's ruling of
23 Oct 2026; the payload stamps what the arm RAN, never the flag.

`--gas-nine-month-floor` (2026-10-22) also turns on `bill_estimate_floors_the_gas_advance_at_nine_months`.
It floors the annualised advance, so it is refused when the arm's policy has the advance off.
`register` with and without it (the advance on either way) is the pair of
`docs/staging/records/WORKER_PREREG_THE_GAS_ESTIMATE_FLOORS_THE_ADVANCE_AT_NINE_MONTHS_2026-10-22.md`.
"""
from __future__ import annotations

import argparse
import dataclasses
from datetime import datetime, timezone
from pathlib import Path

ARMS = ("off", "register", "ceiling")


def run_arm(arm: str, out: Path, annualised_advance: bool | None = None,
            gas_nine_month_floor: bool = False) -> Path:
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
    if annualised_advance is not None:
        policy = dataclasses.replace(policy, bill_estimate_reads_the_annualised_advance=annualised_advance)
    if gas_nine_month_floor:
        if not policy.bill_estimate_reads_the_annualised_advance:
            raise SystemExit("REFUSED: --gas-nine-month-floor floors the annualised advance, and this "
                             "arm's policy has the advance off; it would run the control twice")
        policy = dataclasses.replace(policy, bill_estimate_floors_the_gas_advance_at_nine_months=True)
    rp2b.CURRENT_POLICY = policy  # this process only; see the module docstring
    code_commit = _git_commit_hash()
    code_commit_at = datetime.now(timezone.utc)
    with policy_scope(policy):
        raw = main(policy=policy, instructed_read_arm="ceiling" if arm == "ceiling" else "register")
    data = reconcile_and_stamp(extract_report_data(raw), code_commit=code_commit, report_end=None,
                               code_commit_at=code_commit_at)
    data["_read_instruction_arm"] = arm
    data["_bill_estimate_reads_the_annualised_advance"] = policy.bill_estimate_reads_the_annualised_advance
    data["_bill_estimate_floors_the_gas_advance_at_nine_months"] = (
        policy.bill_estimate_floors_the_gas_advance_at_nine_months)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(dump_run_output(data))
    return out


def cli() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("arm", choices=ARMS)
    parser.add_argument("out", type=Path)
    estimate = parser.add_mutually_exclusive_group()
    estimate.add_argument("--annualised-advance", dest="annualised_advance", action="store_true",
                          default=None)
    estimate.add_argument("--three-read-estimate", dest="annualised_advance", action="store_false")
    parser.add_argument("--gas-nine-month-floor", action="store_true")
    args = parser.parse_args()
    print(f"wrote {run_arm(args.arm, args.out, args.annualised_advance, args.gas_nine_month_floor)}")


if __name__ == "__main__":
    cli()
