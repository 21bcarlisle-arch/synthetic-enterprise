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
from saas.customer_reaction import _billing_account_id
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


#: R14 -- the two bases an account's realised margin can be stated on, named where they
#: are used rather than left for a reader to infer from a key.
SETTLED_BASIS = ("net_margin_gbp summed from the world's own settled records "
                 "(phase2b.all_records) -- after wholesale, levies, network, capital and "
                 "bad debt, BEFORE cost-to-serve")
REPORTED_BASIS = ("net_margin_after_cost_to_serve_gbp from the reporting layer's "
                  "per_customer_lifetime -- after cost-to-serve as well")


def _lifetime_by_billing_account(result: dict) -> tuple[dict, str]:
    """Realised whole-life margin per BILLING ACCOUNT, with the basis it is stated on.

    THREE LOOKUPS BEFORE THIS ONE WORKED, and each wrong turn was caught by a control
    declaring a blank rather than a zero (2026-08-26). `per_customer_lifetime` is not in
    the run at all: `saas/reporting/annual_report.py` BUILDS it, so it exists in the
    published artefact and never in the in-memory result an A/B holds. It is also keyed
    by CUSTOMER (`C1`, `C1g`) where `churned_billing_accounts` is keyed by BILLING
    ACCOUNT (`C1`, `C1_2`).

    So the primary source is the one the reporting layer itself aggregates from -- the
    world's settled records -- which is strictly better for a harness: it is what
    actually happened, not a renderer's derivation of it, and it is available without
    invoking the reporting layer inside an experiment. `per_customer_lifetime` is still
    preferred WHEN PRESENT, because an artefact-driven caller has the richer
    after-cost-to-serve basis, and the basis is returned rather than assumed.

    Dual-fuel legs are folded with the same helper `saas.clv_model.build_clv` uses, so
    the two cannot drift into different ideas of one account. A billing account with no
    records behind it (`C1_2`, a secondary account the household register does not carry)
    stays `None` -- genuinely unvalued, and saying so is what surfaced all three lookup
    faults instead of writing four real customers off as worthless.
    """
    merged: dict[str, dict] = {}

    reported = result.get("per_customer_lifetime")
    if not isinstance(reported, dict) or not reported:
        reported = (result.get("phase2b") or {}).get("per_customer_lifetime")
    if isinstance(reported, dict) and reported:
        for customer_id, entry in reported.items():
            if not isinstance(entry, dict):
                continue
            account_id = _billing_account_id(customer_id)
            figure = entry.get("net_margin_after_cost_to_serve_gbp")
            row = merged.setdefault(
                account_id, {"segment": entry.get("segment"), "total": None})
            if isinstance(figure, (int, float)) and not isinstance(figure, bool):
                row["total"] = (row["total"] or 0.0) + float(figure)
            if row["segment"] is None:
                row["segment"] = entry.get("segment")
        return merged, REPORTED_BASIS

    records = (result.get("phase2b") or {}).get("all_records")
    if not isinstance(records, list):
        return {}, SETTLED_BASIS
    for record in records:
        if not isinstance(record, dict):
            continue
        customer_id = record.get("customer_id")
        if not isinstance(customer_id, str):
            continue
        account_id = _billing_account_id(customer_id)
        figure = record.get("net_margin_gbp")
        row = merged.setdefault(
            account_id, {"segment": record.get("segment"), "total": None})
        if isinstance(figure, (int, float)) and not isinstance(figure, bool):
            row["total"] = (row["total"] or 0.0) + float(figure)
        if row["segment"] is None:
            row["segment"] = record.get("segment")
    return merged, SETTLED_BASIS


def churn_roster_diff(control: dict, value: dict) -> dict:
    """WHICH accounts the two arms lost differently, named, with what each was worth.

    THE AGGREGATE WAS NOT ENOUGH, and the 12:35Z run is why. It reported the arm giving
    up GBP 123,006 of gross margin on THREE extra churns -- GBP 41,000 each, against a
    domestic book whose whole-life margin averages ~GBP 420. Three domestic customers
    cannot cost that, so either the delta is carried by a handful of large accounts or
    the churn count is not the mechanism at all; and with aggregates alone the artefact
    could not tell those apart. A delta driven by three accounts out of 263 must name
    them, because "the value arm loses" is a portfolio claim and three accounts are not
    a portfolio.

    Both sides come from `churned_billing_accounts` -- the WORLD's own roster, written
    when a churn event actually fires -- and the value is
    `per_customer_lifetime[...]['net_margin_after_cost_to_serve_gbp']`, the same
    realised, settled figure `tools/couple_clv.py` grades against. Neither is anything
    the company believed.

    `only_in_value` is the interesting side: accounts the value arm drove away that the
    control kept. `only_in_control` is published beside it because an arm that loses
    three and SAVES two is a different animal from one that loses three, and the net
    count alone hides the difference.
    """
    def roster(result: dict) -> set:
        churned = result["phase2b"].get("churned_billing_accounts")
        if not isinstance(churned, list):
            # R15 FAIL-OPEN: an absent roster is not an empty one. Reporting "no
            # accounts differ" from a missing field would be the most reassuring
            # wrong answer this artefact could carry.
            return None
        return {a for a in churned if isinstance(a, str)}

    control_churned, value_churned = roster(control), roster(value)
    if control_churned is None or value_churned is None:
        return {"available": False,
                "reason": "a run published no churned_billing_accounts roster"}

    lifetimes, basis = _lifetime_by_billing_account(value)
    control_lifetimes, control_basis = _lifetime_by_billing_account(control)

    def describe(account_id: str, source: dict) -> dict:
        entry = source.get(account_id) or {}
        return {
            "account": account_id,
            "segment": entry.get("segment"),
            "realised_lifetime_margin_gbp": entry.get("total"),
        }

    only_value = sorted(value_churned - control_churned)
    only_control = sorted(control_churned - value_churned)
    lost = [describe(a, lifetimes) for a in only_value]
    saved = [describe(a, control_lifetimes) for a in only_control]

    def figures_of(rows):
        return [r["realised_lifetime_margin_gbp"] for r in rows
                if r["realised_lifetime_margin_gbp"] is not None]

    # A ZERO HERE MUST MEAN "NOTHING DIFFERED", AND NOTHING ELSE. The per-account rows
    # above already declare a blank correctly; it is the aggregation that used to
    # collapse those blanks to 0.0, and the 13:58Z run did exactly that -- five named
    # accounts, every figure null, every total 0.0. That run was superseded by 14:25Z
    # before it was ever committed, so the ONLY surviving evidence of the defect is this
    # control: the artefact in origin has never shown it, which is precisely why the
    # fault could outlive the run that revealed it. That is the fourth R15 shape: the
    # verdict was a CONSTANT no run could move. It is also the most reassuring wrong
    # answer available, because `reading` below tells the reader to divide
    # `largest_single_difference_gbp` into the headline delta, and a fabricated 0.0
    # divides to "no concentration" -- i.e. "the loss is a portfolio property", the one
    # conclusion this artefact was built to be able to REFUSE.
    def total(rows):
        if not rows:
            return 0.0          # honest: the sum over an empty set of differences
        figures = figures_of(rows)
        return sum(figures) if figures else None

    def largest_single(rows):
        if not rows:
            return 0.0
        figures = figures_of(rows)
        return max(abs(f) for f in figures) if figures else None

    # Published because a PARTIAL blank makes the totals a FLOOR, not a measurement, and
    # a floor that does not say so is read as a measurement.
    def coverage(rows):
        return {"accounts": len(rows), "valued": len(figures_of(rows))}

    return {
        "available": True,
        "churned_under_both": len(control_churned & value_churned),
        "margin_basis": basis,
        "only_in_value_arm": lost,
        "only_in_control_arm": saved,
        "only_in_value_arm_realised_gbp": total(lost),
        "only_in_control_arm_realised_gbp": total(saved),
        "largest_single_difference_gbp": largest_single(lost + saved),
        "realised_coverage": {
            "only_in_value_arm": coverage(lost),
            "only_in_control_arm": coverage(saved),
        },
        "reading": (
            "If `largest_single_difference_gbp` is a large share of "
            "`realised_delta.gross_margin_gbp`, the headline is a statement about ONE "
            "decision and n=1 is not a thesis -- read it as a case study and say so. "
            "The realised figures are whole-life and come from the arm's own run, so "
            "an account present in both rosters is not compared here at all: only the "
            "accounts the two arms treated DIFFERENTLY appear. A total of null means "
            "accounts differed but NONE could be valued -- that is an unavailable "
            "measurement, and it must never be read as zero concentration; check "
            "`realised_coverage`, and where `valued` is short of `accounts` the totals "
            "are a FLOOR. Only an empty roster side legitimately totals 0.0. R12: "
            "diagnostic, never a target."
        ),
    }


def margin_movers(control: dict, value: dict, top: int = 15) -> dict:
    """WHERE the realised margin delta actually comes from, account by account.

    THE CHURN ROSTER WAS NOT ENOUGH EITHER, and this is the second thing the 12:35Z run
    forced. That run gave up GBP 123,006 of gross margin, and the roster named only four
    extra churns whose whole-life revenue under the control totals ~GBP 69,000 -- less
    than the delta, and an account that churns EARLY loses only the part of that it had
    not yet earned. So the delta is not the churns, and with churn counts alone the
    artefact could neither say that nor say what it is instead.

    `concentration` is the number this exists to publish: the share of the total absolute
    movement carried by the top few accounts. A delta spread thinly across 200 customers
    is a portfolio result and supports a portfolio claim. A delta carried by three is a
    case study wearing a portfolio's clothes, and the two must not read the same.

    Both sides are realised, settled, whole-life margin from each arm's OWN run. An
    account that churned under one arm still appears -- its margin simply stopped
    earlier, which is the point.
    """
    control_book, control_basis = _lifetime_by_billing_account(control)
    value_book, basis = _lifetime_by_billing_account(value)
    if not control_book and not value_book:
        return {"available": False, "reason": "neither arm published per_customer_lifetime"}

    rows = []
    for account_id in sorted(set(control_book) | set(value_book)):
        c = (control_book.get(account_id) or {}).get("total")
        v = (value_book.get(account_id) or {}).get("total")
        if c is None and v is None:
            continue
        rows.append({
            "account": account_id,
            "segment": (value_book.get(account_id) or control_book.get(account_id)
                        or {}).get("segment"),
            "control_gbp": c,
            "value_arm_gbp": v,
            "delta_gbp": (v or 0.0) - (c or 0.0),
        })

    ranked = sorted(rows, key=lambda r: -abs(r["delta_gbp"]))
    total_abs = sum(abs(r["delta_gbp"]) for r in rows)
    top_abs = sum(abs(r["delta_gbp"]) for r in ranked[:top])
    net = sum(r["delta_gbp"] for r in rows)

    return {
        "available": True,
        "accounts_compared": len(rows),
        "margin_basis": basis,
        "accounts_that_moved": sum(1 for r in rows if r["delta_gbp"]),
        "net_delta_gbp": net,
        "total_absolute_movement_gbp": total_abs,
        "top_n": top,
        "concentration_top_n_share_of_absolute_movement": (
            top_abs / total_abs if total_abs else None),
        "biggest_movers": ranked[:top],
        "reading": (
            "`concentration_top_n_share_of_absolute_movement` near 1.0 means a handful "
            "of accounts ARE the headline and it should be read as a case study, not a "
            "portfolio result. Spread thin, the portfolio claim stands. Note that "
            "`net_delta_gbp` is the NET-of-all-costs line and will not equal "
            "`realised_delta.gross_margin_gbp`, which is a different basis (R14) -- "
            "they are here to be compared in SHAPE, not summed. R12: diagnostic, never "
            "a target."
        ),
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
    # DECLINES ARE DECISIONS AND ARE COUNTED APART FROM PRICES. `decide_margin` refuses a renewal
    # where no candidate margin survives BOTH the price cap and the churn model's support bound
    # -- at a high enough base rate there is no offer this company can lawfully make and honestly
    # predict. The first ten-year A/B died on exactly that (`C_IC3`, 2021, base GBP 251.45), and
    # the three-year window never reached a rate high enough to produce one. A run where the arm
    # declined a fifth of the book is not the same experiment as one where it priced it all, and
    # only this split says which happened.
    declined = [e for e in log if e.get("declined")]
    priced_entries = [e for e in log if not e.get("declined")]
    if not priced_entries:
        return {"priced": 0, "declined": len(declined),
                "note": "the arm ran and declined every renewal it saw -- no lawful, predictable "
                        "offer existed anywhere on this book"}
    log = priced_entries
    margins = [e["chosen_margin_gbp_per_mwh"] for e in log]
    counts = collections.Counter(round(m, 2) for m in margins)
    modal_share = counts.most_common(1)[0][1] / len(margins)
    return {
        "priced": len(log),
        "declined": len(declined),
        "declined_share_of_renewals_seen": round(len(declined) / (len(log) + len(declined)), 4),
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
        # WHICH bound ended the interval the answer sat at, read from the decision rather than
        # reconstructed from the rate. Until 2026-08-26 neither could be counted here: the chain
        # passed the arm no ceiling, so `ceiling_bound` was structurally False on the only path a
        # run uses, and the cap arrived afterwards as a clamp instead. See `decided_by`.
        "ceiling_bound": sum(1 for e in log if e.get("ceiling_bound")),
        "extrapolation_bound": sum(1 for e in log if e.get("extrapolation_bound")),
        # THIS SHOULD NOW BE ZERO FOR EVERY RENEWAL THE ARM PRICED, and it is a control rather
        # than a statistic. The arm searches under the same cap writer 4 applies, so a priced
        # renewal that the cap still clamped means the two have come apart -- either the ceiling
        # stopped being threaded through or the two reads of it disagree. A nonzero count here is
        # the finding, not a caveat: it says the published `believed_p_retain` is a belief about a
        # price the customer was not charged.
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
        # Names the accounts behind `realised_delta.churned_accounts`. Published
        # beside the delta, never instead of it -- see `churn_roster_diff`.
        "churn_roster_diff": churn_roster_diff(control, value),
        # WHERE the delta comes from, account by account, with its concentration.
        # The roster names who left; this names who MOVED, which is not the same set.
        "margin_movers": margin_movers(control, value),
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
