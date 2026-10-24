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
  * `flat`    -- FLAT_SUPPLIER_POLICY: no targeted retention, one framing (the tone is current's since
                 2026-10-24: the payment truth reads none).
  * `all_on_ending_term` -- `all_on` with the renewal churn belief conditioned on the term now
                 ending (`renewal_belief_by_ending_term`), the arm the record's section 10 names.
  * `all_on_save_odds` -- `all_on_ending_term` with the retention guard weighing the company's own
                 save rate per ending-term type (`retention_weighs_save_odds`), section 13.
  * `all_on_save_odds_holdout` -- `all_on_save_odds` with that save rate learned against the
                 company's own holdout (`retention_save_rate_learned_against_holdout`), section 15.
  * `all_on_save_odds_lower_bound` -- `all_on_save_odds_holdout` with the guard offering only where
                 the save rate's lower bound pays (`retention_offers_on_the_save_rate_lower_bound`),
                 section 16.

THE OFFERS' MONEY, BY WHAT EACH OFFER CHANGED (section 15). Every output carries
`retention_offer_money_by_channel`: the offers that changed a departure, the offers that changed a
stayer's tariff (section 13's parity channel), and those that changed neither, each with its count
and the offer cost the guard booked. Read off the world's own answer at the full and offered rate
(`retention_offer_channel_log`), harness-side. By M2 only the first can be value created.

As in the read-instruction arms, the policy is also bound to `run_phase2b.CURRENT_POLICY`, so a
consumer that rebuilds with no policy in hand sees the arm and not the standing one. This process
only; `company/policy/decision_policy.py` is not touched.

`extract_report_data` keeps neither the renewal desk's decisions nor the save log, so both are
carried across from the raw phase 2b result under their own names: they are what "decisions taken by kind"
is counted from.

DICE SEEDS (section 14). `--dice-seed N` re-draws the two kinds of dice a retention offer's money
can move through: every household's renewal roll (`customer_events.churn_roll_for_renewal`, the
departure the offer acts on) and every payment draw (`grade_world_debt_against_ofgem.dice_seeded`).
The book, the elasticities and the SVT-inertia roll are held. `retention_offer` and `run_phase2b`
import the roll BY NAME, so every binding is replaced: patching only the module would let the offer
answer read the base roll while the renewal it answers read the seeded one. A seed whose renewal or
payment dice reached no draw is refused rather than written as a second seed; that would be the
default world.

    python3 -m tools.per_customer_switch_arms <arm> <out.json> [--dice-seed N]
"""
from __future__ import annotations

import argparse
import contextlib
import dataclasses
import random
from datetime import datetime, timezone
from pathlib import Path

ARMS = ("current", "all_on", "flat", "all_on_ending_term", "all_on_save_odds",
        "all_on_save_odds_holdout", "all_on_save_odds_lower_bound")
ALL_ON_FIELDS = ("next_best_action_decides_at_renewal", "next_best_action_shares_by_retention_rise",
                 "save_offer_decides_per_household")
ENDING_TERM_FIELDS = ALL_ON_FIELDS + ("renewal_belief_by_ending_term",)
SAVE_ODDS_FIELDS = ENDING_TERM_FIELDS + ("retention_weighs_save_odds",)
SAVE_HOLDOUT_FIELDS = SAVE_ODDS_FIELDS + ("retention_save_rate_learned_against_holdout",)
LOWER_BOUND_FIELDS = SAVE_HOLDOUT_FIELDS + ("retention_offers_on_the_save_rate_lower_bound",)
CARRIED_RAW_KEYS = ("next_best_action_renewal_log", "next_best_action_legs_without_contribution",
                    "save_on_loss_notice_log", "retention_offer_channel_log",
                    "retention_save_holdout_log", "retention_save_rate_lower_bound_log")
OFFER_CHANNELS = ("changed_a_departure", "changed_a_stayers_tariff", "changed_neither")


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
    if arm == "all_on_save_odds_holdout":
        return dataclasses.replace(CURRENT_POLICY, name="per_customer_all_on_save_odds_holdout",
                                   **{f: True for f in SAVE_HOLDOUT_FIELDS})
    if arm == "all_on_save_odds_lower_bound":
        return dataclasses.replace(CURRENT_POLICY, name="per_customer_all_on_save_odds_lower_bound",
                                   **{f: True for f in LOWER_BOUND_FIELDS})
    if arm == "flat":
        return FLAT_SUPPLIER_POLICY
    raise SystemExit(f"REFUSED: arm {arm!r} is not one of {ARMS}")


class renewal_dice_seeded:
    """Re-draw every renewal roll under `seed`, on every binding; restore on exit.

    The bindings are FOUND, not listed: every loaded module whose `churn_roll_for_renewal` is the
    real function. `run_phase2b` and `retention_offer` both import it by name, and a hand list
    written on 2026-10-22 already missed `run_phase2b`. A module imported after entry reads the
    patched attribute of `customer_events`, as `coin_drawn_decision_set` does inside its functions.
    The prefix `dice{seed}_` keeps a re-drawn roll off the base stream of an account whose name
    happens to start with the seed. `calls` counts per binding."""

    def __init__(self, seed: int):
        self.seed = seed
        self.calls: dict[str, int] = {}

    def __enter__(self):
        import sys

        import simulation.customer_events as ce

        real = ce.churn_roll_for_renewal
        self._saved = [(m, real) for m in list(sys.modules.values())
                       if getattr(m, "__dict__", {}).get("churn_roll_for_renewal") is real]
        for module, _ in self._saved:
            self.calls[module.__name__] = 0

            def seeded(billing_account, term_start_str, _name=module.__name__):
                self.calls[_name] += 1
                return random.Random(f"dice{self.seed}_{billing_account}_{term_start_str}").random()

            module.churn_roll_for_renewal = seeded
        return self

    def __exit__(self, *exc):
        for module, real in self._saved:
            module.churn_roll_for_renewal = real
        return False


def dice_refusal(seed: int, renewal_calls: dict, payment_calls: int, offers: int) -> str | None:
    """Why a seeded run must not be written as a seed, or None. The offer binding is owed a call
    only where an offer was made: flat makes none, and its zero is the right answer there."""
    if renewal_calls.get("simulation.customer_events", 0) == 0:
        return f"dice seed {seed} reached no renewal roll; the departures are the default world's"
    if offers and renewal_calls.get("simulation.retention_offer", 0) == 0:
        return (f"dice seed {seed}: {offers} offers were answered and none read the seeded roll, so "
                "each offer answered a different departure from the one its renewal rolled")
    if payment_calls == 0:
        return f"dice seed {seed} reached no payment draw; the bad debt is the default world's"
    return None


def offer_money_by_channel(channel_log) -> dict:
    """Offers, households and booked offer cost per channel. A channel absent from the log reads
    zero, never missing: flat makes no offers, and its zeros are the answer."""
    out = {c: {"offers": 0, "households": set(), "offer_cost_gbp": 0.0} for c in OFFER_CHANNELS}
    for row in channel_log or ():
        bucket = out[row["channel"]]
        bucket["offers"] += 1
        bucket["households"].add(row["customer_id"])
        bucket["offer_cost_gbp"] += row.get("retention_cost_gbp") or 0.0
    return {c: {"offers": b["offers"], "households": len(b["households"]),
                "offer_cost_gbp": round(b["offer_cost_gbp"], 2)} for c, b in out.items()}


def run_arm(arm: str, out: Path, dice_seed: int | None = None) -> Path:
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
    if dice_seed is None:
        renewal = payment = contextlib.nullcontext()
    else:
        from tools.grade_world_debt_against_ofgem import dice_seeded

        renewal, payment = renewal_dice_seeded(dice_seed), dice_seeded(dice_seed)
    with policy_scope(policy), renewal, payment:
        raw = main(policy=policy)
    if dice_seed is not None:
        offers = len(raw["phase2b"].get("retention_log") or ())
        refusal = dice_refusal(dice_seed, renewal.calls, payment.calls, offers)
        if refusal:
            raise SystemExit(f"REFUSED: {refusal}")
    data = reconcile_and_stamp(extract_report_data(raw), code_commit=code_commit, report_end=None,
                               code_commit_at=code_commit_at)
    for key in CARRIED_RAW_KEYS:
        if key in raw["phase2b"]:
            data[key] = raw["phase2b"][key]
    data["_per_customer_switch_arm"] = arm
    data["retention_offer_money_by_channel"] = offer_money_by_channel(
        raw["phase2b"].get("retention_offer_channel_log"))
    if dice_seed is not None:
        data["_dice_seed"] = {"seed": dice_seed, "renewal_roll_calls": renewal.calls,
                              "payment_draw_calls": payment.calls}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(dump_run_output(data))
    return out


def cli() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("arm", choices=ARMS)
    parser.add_argument("out", type=Path)
    parser.add_argument("--dice-seed", type=int, default=None)
    args = parser.parse_args()
    print(f"wrote {run_arm(args.arm, args.out, dice_seed=args.dice_seed)}")


if __name__ == "__main__":
    cli()
