"""Run one arm of the per-customer switches against flat in the published run, to a named run output.

REUSE: tools/per_customer_switch_arms.py
CLASS: CUSTOM
INDEX: searched "per customer arms", "flat supplier arm", "policy arm run output". `tools/
       read_instruction_arms.py` is the template and is followed line for line; it flips one field
       and names its arms for that field. `tools/run_value_cycle_ab.py` hard-codes CURRENT_POLICY as
       its control and keeps a summary. `tools/save_on_loss_notice_arms.py` flips the save alone.
       None runs FLAT_SUPPLIER_POLICY or the three switches together to a whole run output.

ARMS (pre-registered in `docs/staging/records/
SEAT_PREREG_THE_PER_CUSTOMER_SWITCHES_ON_TOGETHER_AGAINST_FLAT_2026-10-21.md`):
  * `current` -- CURRENT_POLICY, unchanged. The control at this commit.
  * `all_on`  -- CURRENT_POLICY with C34 at the renewal roll, C35's rise through it, and the save
                 deciding per household, all on.
  * `flat`    -- FLAT_SUPPLIER_POLICY: no targeted retention, one framing, one tone.
  * `all_on_ending_term` -- `all_on` with the renewal churn belief conditioned on the term now
                 ending (`renewal_belief_by_ending_term`), the arm the record's section 10 names.
  * `all_on_save_odds` -- `all_on_ending_term` with the retention guard weighing the company's own
                 save rate per ending-term type (`retention_weighs_save_odds`), section 13.

As in the read-instruction arms, the policy is also bound to `run_phase2b.CURRENT_POLICY`, so a
consumer that rebuilds with no policy in hand sees the arm and not the standing one. This process
only; `company/policy/decision_policy.py` is not touched.

`extract_report_data` keeps neither the renewal desk's decisions nor the save log, so both are
carried across from the raw phase 2b result under their own names: they are what "decisions taken by kind"
is counted from.

    python3 -m tools.per_customer_switch_arms <current|all_on|flat|all_on_ending_term|all_on_save_odds> <out.json>
"""
from __future__ import annotations

import argparse
import dataclasses
from datetime import datetime, timezone
from pathlib import Path

ARMS = ("current", "all_on", "flat", "all_on_ending_term", "all_on_save_odds")
ALL_ON_FIELDS = ("next_best_action_decides_at_renewal", "next_best_action_shares_by_retention_rise",
                 "save_offer_decides_per_household")
ENDING_TERM_FIELDS = ALL_ON_FIELDS + ("renewal_belief_by_ending_term",)
SAVE_ODDS_FIELDS = ENDING_TERM_FIELDS + ("retention_weighs_save_odds",)
CARRIED_RAW_KEYS = ("next_best_action_renewal_log", "next_best_action_legs_without_contribution",
                    "save_on_loss_notice_log")


def arm_policy(arm: str):
    from company.policy.decision_policy import CURRENT_POLICY, FLAT_SUPPLIER_POLICY

    if arm == "current":
        return CURRENT_POLICY
    if arm == "all_on":
        return dataclasses.replace(CURRENT_POLICY, name="per_customer_all_on",
                                   **{f: True for f in ALL_ON_FIELDS})
    if arm == "all_on_ending_term":
        return dataclasses.replace(CURRENT_POLICY, name="per_customer_all_on_ending_term",
                                   **{f: True for f in ENDING_TERM_FIELDS})
    if arm == "all_on_save_odds":
        return dataclasses.replace(CURRENT_POLICY, name="per_customer_all_on_save_odds",
                                   **{f: True for f in SAVE_ODDS_FIELDS})
    if arm == "flat":
        return FLAT_SUPPLIER_POLICY
    raise SystemExit(f"REFUSED: arm {arm!r} is not one of {ARMS}")


def run_arm(arm: str, out: Path) -> Path:
    policy = arm_policy(arm)
    import simulation.run_phase2b as rp2b
    from company.policy.decision_policy import policy_scope
    from simulation.run_phase4c_on_phase2b import main
    from tools.run_annual_report import (
        _git_commit_hash,
        dump_run_output,
        extract_report_data,
        reconcile_and_stamp,
    )

    rp2b.CURRENT_POLICY = policy  # this process only; see the module docstring
    code_commit = _git_commit_hash()
    code_commit_at = datetime.now(timezone.utc)
    with policy_scope(policy):
        raw = main(policy=policy)
    data = reconcile_and_stamp(extract_report_data(raw), code_commit=code_commit, report_end=None,
                               code_commit_at=code_commit_at)
    for key in CARRIED_RAW_KEYS:
        if key in raw["phase2b"]:
            data[key] = raw["phase2b"][key]
    data["_per_customer_switch_arm"] = arm
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
