#!/usr/bin/env python3
"""The value cycle's realised A/B: the same book, the same world, once per pricing arm.

REUSE: tools/run_value_cycle_ab.py
CLASS: PATTERN-REUSE
INDEX: searched "arm", "baseline", "counterfactual", "replay", "policy", "ab", "control",
       "frozen". `tools/run_frozen_baseline.py` is the pattern taken WHOLE -- two runs of
       `simulation.run_phase4c_on_phase2b.main()` through the same window, each inside
       `policy_scope(...)` AND passing `policy=`, differing in exactly one policy field, with
       the differing-field set written into the artefact as a provenance fact. Its shape is not
       adapted here, it is followed, including the arm-identity block, because the defect that
       block exists for (`WORKER_FINDING_THE_NAIVE_ARM_KEEPS_THE_LIVE_TONE_2026-08-10`: an arm
       that kept one live field and attributed its effect to the policy change) is exactly the
       defect a pricing A/B is most exposed to.
       `tools/couple_value_based_pricing.py` was read and is NOT this: it compares what the two
       arms would DECIDE on a finished book, and says in its own docstring that the earnings
       comparison is realised and needs two runs. This is those two runs.
       It is a separate module rather than a second mode of `run_frozen_baseline` because that
       file's subject is a FIXED HISTORICAL reference point refreshed weekly by the publish
       path, and this one is an experiment run on demand; folding them would couple a periodic
       artefact's staleness gate to an experiment's cadence.

WHY THIS EXISTS
---------------
Director, 2026-08-26, handing over the last thing he had reserved: *"start the value cycle --
the per-customer decision engine the whole thesis rests on."*

`company/pricing/value_based_renewal.py` closes its own docstring with the reason this file had
to be written before any number could be quoted:

    It does not show that pricing on value earns more. It cannot: the objective is built from
    the company's own beliefs, so scoring the arms on EXPECTED value would let the value arm win
    by construction -- it maximises the very number it would be judged on, which is R15's
    tautology pattern with money in it. The only honest comparison is REALISED: the same book,
    the same world, run once per arm, scored on what actually happened.

So this scores nothing the company believed. Every figure below is what the world did.

WHAT THE ARMS ARE
-----------------
`CURRENT_POLICY` -- today's company, flat GBP 2.00/MWh for every account, whoever they are.
`VALUE_ARM_POLICY` -- the same company with `renewal_margin_arm="value_based"` and NOTHING else
changed; it is built by `dataclasses.replace` for that reason, and the artefact records the
differing-field set so a reader can check rather than trust.

THE THREE THINGS THAT MUST BE READ BESIDE THE SCORE, or the score is not readable. Each is
carried in the artefact rather than left to a commit message:

  1. HOW MUCH OF THE ARM'S ANSWER WAS THE BOUND'S. `max_supported_rate_increase_pct()` trims the
     candidate grid at +83.1% -- the largest single-step domestic move Ofgem's own cap has ever
     published -- and on the first probe over the real book 165 of 263 accounts had candidates
     trimmed. A realised win concentrated in bound-decided accounts is a result about the bound.
  2. HOW WEAK THE CONTROL IS. This company's flat GBP 2.00/MWh is 23.4%-53.6% of the EBIT
     allowance Ofgem grants an efficient supplier (`company/pricing/regulated_average_margin.py`,
     cap period 11a). Beating it is a low bar and the ratio must sit beside any headline.
  3. HOW MANY RENEWALS THE ARM ACTUALLY PRICED. An arm that silently declined 200 of 263
     accounts and a run where it priced them all and agreed with the control produce the same
     flat-looking delta. `value_arm_log` carries one entry per renewal it priced, so the count
     is a measurement rather than an assumption.

Run:  python3 -m tools.run_value_cycle_ab [--end-year 2019]
"""
from __future__ import annotations

import argparse
import collections
import json
from datetime import datetime, timezone
from pathlib import Path

from company.policy.decision_policy import (
    CURRENT_POLICY,
    VALUE_ARM_POLICY,
    policy_scope,
)
from saas.tariff_pricing import TARGET_MARGIN_GBP_PER_MWH
from simulation.run_phase4c_on_phase2b import main as run_phase4c

PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_DIR / "docs" / "observability" / "value_cycle_ab.json"
#: The coupler's own artefact, and the ONE place the regulated-allowance comparison is
#: computed. Read here, never recomputed -- see `control_credibility`.
ARMS_ARTEFACT = PROJECT_DIR / "docs" / "observability" / "value_based_pricing_arms.json"


def realised_metrics(result: dict) -> dict:
    """What the WORLD did to one arm's book. Nothing the company believed appears here.

    Every key is an outcome the supplier could only find out by living through the term:
    settled margin, the accounts that actually left, the money that actually failed to arrive.
    `expected_value_gbp` -- the quantity the arm maximises -- is deliberately absent, because a
    comparison that included it would be scoring the arm on its own objective.
    """
    phase2b = result["phase2b"]
    ev = result["enterprise_value"]["portfolio"]

    def figure(key: str) -> float:
        """A missing key RAISES rather than defaulting to 0.0.

        THE FIRST RUN OF THIS FILE PROVED WHY (2026-08-26). `total_revenue` is not a key this
        run emits -- the revenue-side figure is `total_gross` -- and a `.get(key, 0.0)` reported
        GBP 0 revenue for BOTH arms, identical, so the delta was a clean zero and nothing looked
        wrong. That is the fail-silent pattern R15 names, in the file whose whole job is to say
        what actually happened. A metric that cannot find its own figure has to say so."""
        if key not in phase2b:
            raise KeyError(
                f"{key!r} is not in this run's output, so the comparison cannot report it. "
                "A zero here would be indistinguishable from a real zero.")
        return phase2b[key]

    return {
        "total_net_gbp": figure("total_net"),
        # GROSS, and named for it (R14: no financial figure without its basis). This is revenue
        # minus wholesale, before levies, network, capital and bad debt -- the same basis
        # `simulation/portfolio_pnl.py` uses, and NOT the net line above.
        "total_gross_margin_gbp": figure("total_gross"),
        "total_bad_debt_gbp": figure("total_bad_debt"),
        "final_treasury_gbp": figure("final_treasury"),
        "enterprise_value_gbp": ev["enterprise_value_gbp"],
        "account_count": ev["account_count"],
        "churned_accounts": len(phase2b.get("churned_billing_accounts", [])),
        # NOT a realised figure and labelled so: how many renewals the arm priced at all. It is
        # here because a delta of zero has two causes and only this number separates them.
        "renewals_priced_by_the_arm": len(phase2b.get("value_arm_log", [])),
    }


def arm_decision_shape(result: dict) -> dict:
    """How the arm's own answers were distributed, and how much of that was the BOUND's.

    Read off `value_arm_log`, which the chain writes one entry per priced renewal. Empty for the
    control arm by construction -- that emptiness is the check that the control really was the
    control, and it is asserted rather than assumed.
    """
    log = result["phase2b"].get("value_arm_log", [])
    if not log:
        return {"priced": 0, "note": "this arm priced no renewal -- expected for the control"}
    margins = [e["chosen_margin_gbp_per_mwh"] for e in log]
    counts = collections.Counter(round(m, 2) for m in margins)
    modal_share = counts.most_common(1)[0][1] / len(margins)
    return {
        "priced": len(log),
        "distinct_margins": len(counts),
        # THE CONCENTRATION IS THE HONESTY CHECK on "per customer". A grid that returns one of
        # its own rungs for most of the book is a rule wearing a decision's clothes; this number
        # was 72% before the coarse-bracket-plus-refinement rebuild and 1.9% after.
        "modal_margin_share_of_book": round(modal_share, 4),
        "median_margin_gbp_per_mwh": round(sorted(margins)[len(margins) // 2], 2),
        "control_margin_gbp_per_mwh": TARGET_MARGIN_GBP_PER_MWH,
        # CAVEAT 1: how many answers an endpoint decided rather than the customer.
        "endpoint_bound": sum(1 for e in log if e.get("endpoint_bound")),
        "endpoint_at_ceiling": sum(1 for e in log if e.get("endpoint_side") == "ceiling"),
        "endpoint_at_floor": sum(1 for e in log if e.get("endpoint_side") == "floor"),
        "withheld": sum(1 for e in log if e.get("withheld_reason")),
        "clamped_by_the_price_cap": sum(
            1 for e in log if e.get("unit_rate_contracted") is not None
            and e["unit_rate_contracted"] < e["unit_rate_after"] - 1e-9),
    }


def control_credibility() -> dict:
    """CAVEAT 2, READ rather than recomputed: what an efficient supplier is allowed to earn.

    `average_player_margin` is a PER-CUSTOMER allowance -- it needs that customer's bill and its
    annual consumption -- so turning it into one number for the book means running it over every
    account and taking a median. `tools/couple_value_based_pricing.py` already does exactly that
    and publishes the result, so this reads its artefact instead of computing a second median
    from a second population. Two independent computations of one quantity that drift apart is
    the `CLASS_MEASUREMENTS_THAT_MIRROR` shape this project has filed against itself before; the
    fix is one owner, not two careful copies.

    Returns `available: False` WITH ITS REASON rather than omitting the caveat, because a
    headline that quietly drops its own caveat is worse than one that says the caveat is missing.
    """
    if not ARMS_ARTEFACT.is_file():
        return {
            "available": False,
            "why_not": (
                "{} has not been generated; run `python3 -m tools.couple_value_based_pricing` "
                "to produce the regulated-allowance comparison this caveat quotes."
            ).format(ARMS_ARTEFACT.relative_to(PROJECT_DIR)),
        }
    try:
        block = json.loads(ARMS_ARTEFACT.read_text(encoding="utf-8"))["average_player"]
    except (OSError, ValueError, KeyError) as exc:
        return {"available": False, "why_not": f"{ARMS_ARTEFACT.name} unreadable: {exc}"}
    if not block.get("available"):
        return {"available": False, "why_not": "the coupler could not score the average player"}
    return {
        "available": True,
        "read_from": str(ARMS_ARTEFACT.relative_to(PROJECT_DIR)),
        "source": block.get("source"),
        "accounts_scored": block.get("accounts_scored"),
        "regulated_allowance_median_gbp_per_mwh": [
            block.get("median_gbp_per_mwh_low"), block.get("median_gbp_per_mwh_high")],
        "control_gbp_per_mwh": TARGET_MARGIN_GBP_PER_MWH,
        "control_as_share_of_allowance": [
            block.get("flat_rule_as_share_of_average_high"),
            block.get("flat_rule_as_share_of_average_low")],
        "what_it_means": (
            "The control this experiment scores the value arm against is this company's own "
            "flat rule. It sits well below what the regulator allows an efficient supplier to "
            "earn, so beating it demonstrates the control's weakness at least as much as the "
            "arm's strength. Read the delta with this ratio beside it."
        ),
    }


def run_value_cycle_ab(report_end: str | None = None) -> dict:
    """Run the same window under both pricing arms and return the realised comparison.

    Both arms enter `policy_scope(...)` AND pass `policy=`, which is not belt-and-braces: the
    argument covers every field a consumer is handed, the scope covers the fields resolved
    without one -- and this arm's field is resolved without one, from inside the renewal rate
    chain. `run_phase2b.main` refuses a run whose argument and scope disagree, so a chimera
    cannot be produced silently.

    THE CONTROL ARM RUNS FIRST AND ITS EMPTINESS IS CHECKED. If `value_arm_log` is non-empty
    under `CURRENT_POLICY` then the writer is not a no-op, the two arms differ by two things
    rather than one, and every number below is uninterpretable -- so it raises rather than
    reporting a delta it cannot attribute.
    """
    with policy_scope(CURRENT_POLICY):
        control = run_phase4c(report_end=report_end, policy=CURRENT_POLICY)
    if control["phase2b"].get("value_arm_log"):
        raise AssertionError(
            "the CONTROL arm priced {} renewal(s) with the value arm -- the writer is not a "
            "no-op under flat_rules, so this comparison would attribute two variables to one "
            "policy field. Refusing to report it.".format(
                len(control["phase2b"]["value_arm_log"])))

    with policy_scope(VALUE_ARM_POLICY):
        value = run_phase4c(report_end=report_end, policy=VALUE_ARM_POLICY)

    control_m = realised_metrics(control)
    value_m = realised_metrics(value)
    delta_net = value_m["total_net_gbp"] - control_m["total_net_gbp"]

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "report_end": report_end,
        "what_this_is": (
            "The same book and the same world, run once per pricing arm, scored on what "
            "ACTUALLY happened. No figure here is anything the company believed."
        ),
        "arm_identity": {
            "differing_fields": sorted(
                f for f in CURRENT_POLICY.__dataclass_fields__
                if getattr(CURRENT_POLICY, f) != getattr(VALUE_ARM_POLICY, f)
            ),
            "why_it_matters": (
                "`name` and `renewal_margin_arm` are the only two, and `name` does not reach a "
                "decision. Any third field here means the delta below carries an uncontrolled "
                "variable, which is the defect WORKER_FINDING_THE_NAIVE_ARM_KEEPS_THE_LIVE_TONE"
                "_2026-08-10 recorded on the sibling comparison."
            ),
        },
        "control_arm": control_m,
        "value_arm": value_m,
        "realised_delta": {
            "net_margin_gbp": delta_net,
            "enterprise_value_gbp": (
                value_m["enterprise_value_gbp"] - control_m["enterprise_value_gbp"]),
            "accounts_at_end": value_m["account_count"] - control_m["account_count"],
            "churned_accounts": value_m["churned_accounts"] - control_m["churned_accounts"],
            "gross_margin_gbp": (
                value_m["total_gross_margin_gbp"] - control_m["total_gross_margin_gbp"]),
            "bad_debt_gbp": value_m["total_bad_debt_gbp"] - control_m["total_bad_debt_gbp"],
        },
        "decision_shape": arm_decision_shape(value),
        "control_credibility": control_credibility(),
        "how_to_read_this": (
            "A positive net-margin delta does NOT establish the thesis on its own. Check three "
            "things first, all carried above: how many of the arm's answers an endpoint or the "
            "support bound decided rather than the customer (`decision_shape`), how weak the "
            "control is against the regulated allowance (`control_credibility`), and how many "
            "renewals the arm actually priced (`renewals_priced_by_the_arm`) -- a small delta "
            "from an arm that priced almost nothing says nothing about pricing on value. A "
            "NEGATIVE delta is a result and not a defect: the arm maximises the company's own "
            "beliefs, so it loses exactly to the degree those beliefs are wrong, and finding "
            "that out is what this experiment is for."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--end-year", help="truncate the window, e.g. 2019 (faster iteration)")
    ap.add_argument("--out", type=Path, default=OUTPUT_PATH)
    args = ap.parse_args(argv)
    report_end = f"{args.end_year}-12-31" if args.end_year else None

    result = run_value_cycle_ab(report_end=report_end)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")

    d = result["realised_delta"]
    shape = result["decision_shape"]
    print("value cycle A/B -- REALISED, {} window".format(report_end or "full"))
    print("  net margin      {:+,.0f} GBP".format(d["net_margin_gbp"]))
    print("  enterprise val  {:+,.0f} GBP".format(d["enterprise_value_gbp"]))
    print("  accounts at end {:+d}   churned {:+d}".format(
        d["accounts_at_end"], d["churned_accounts"]))
    print("  arm priced {} renewal(s), {} distinct margins, {} endpoint-bound".format(
        shape.get("priced", 0), shape.get("distinct_margins", 0),
        shape.get("endpoint_bound", 0)))
    print("  wrote {}".format(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
