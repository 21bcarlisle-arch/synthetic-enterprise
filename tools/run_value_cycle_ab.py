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
import ast
import bisect
import collections
import importlib
import importlib.util
import json
import math
import random
import statistics
from dataclasses import replace
from datetime import date, datetime, timezone
from pathlib import Path

# THE HOUSEHOLD SIDE (atom `A47`), read here in the HARNESS -- the reporting use R12 protects.
# No company organ, world module or draw may import it, and
# `tests/company/test_household_share_is_not_yet_a_target.py` holds that and names what
# releases it.
from company.analytics.household_value_share import build_household_value_share
from company.policy.decision_policy import (
    CURRENT_POLICY,
    VALUE_ARM_POLICY,
    policy_scope,
)
from company.pricing.value_based_renewal import (
    FLAT_AT_LEVEL,
    FUNNEL_STAGES,
    STAGE_DECLINED,
    STAGE_PRICED,
)
from saas.customer_reaction import _billing_account_id
from saas.tariff_pricing import TARGET_MARGIN_GBP_PER_MWH
from simulation.run_phase4c_on_phase2b import main as run_phase4c

# ONE COUNTERFACTUAL, NOT TWO. The choice of reference (Ofgem cap where published, the pre-2019
# SVT series before it) is argued at length where it is defined; a second copy here would be a
# second thing to keep in step, and the household leg and the ladder's must be one reference or
# their figures cannot be read against each other.
from tools.run_price_ladder import household_side, published_default_tariff

PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_DIR / "docs" / "observability" / "value_cycle_ab.json"
#: The noise-floor mode's own artefact. A SEPARATE file on purpose: it is the error bar ON
#: `value_cycle_ab.json`, and writing it over the thing it qualifies would leave the published
#: split with no reading beside it.
NOISE_FLOOR_OUTPUT_PATH = (
    PROJECT_DIR / "docs" / "observability" / "value_cycle_ab_noise_floor.json")
#: The floor cut in two. A THIRD file, again on purpose: it is the answer to "what would resolve
#: this", it is composed from three floors rather than measured by one, and the site feed reads it
#: to decide whether the remedy sentence beside its refusal is true.
DECOMPOSITION_OUTPUT_PATH = (
    PROJECT_DIR / "docs" / "observability" / "value_cycle_ab_floor_decomposition.json")
#: The coupler's own artefact, and the ONE place the regulated-allowance comparison is
#: computed. Read here, never recomputed -- see `control_credibility`.
ARMS_ARTEFACT = PROJECT_DIR / "docs" / "observability" / "value_based_pricing_arms.json"

#: The share -- of the arm's priced answers, or of the money it moved -- at which a BOUND
#: rather than a customer is the honest subject of this artefact's headline. It is not a
#: target, not a gate, and nothing passes or fails against it (R12): it is the single point at
#: which the sentence `bound_attribution` writes has to change, named here so a reader can
#: disagree with it in one place instead of inferring it from prose.
BOUND_DECIDED_HEADLINE_SHARE = 0.5


#: EVERY CLOCK ANY FIGURE IN THIS ARTEFACT IS STATED ON, each traced to the code that produces
#: it (R14: no financial figure without its clock). Two clocks and no more -- and in particular
#: NOT `banked`, which this world does not have as a distinct reading: `treasury_cash_balance_gbp`
#: is a running total of settled net margin, so `final_treasury - starting_treasury` reproduces
#: the settled net exactly rather than measuring cash arriving on some other date. Publishing a
#: "banked" label here would have been a name for a clock that does not exist.
CLOCK_DEFINITIONS = {
    "settled-realised": (
        "SETTLED, on the world's realised payment behaviour. Summed over "
        "`phase2b.all_records` AS THIS ARTEFACT READS THEM -- i.e. after "
        "`simulation/run_phase4c_on_phase2b.py` has called `apply_emergent_bad_debt` and "
        "`apply_debt_recovery`, which replace the flat-rate provision in each row with the "
        "write-offs and DCA recoveries the arrears model actually produced, and carry the "
        "difference through `treasury_cash_balance_gbp`. This is the SAME sum "
        "`saas/reporting/annual_report.py:921` publishes as `total_net_gbp` in "
        "`docs/reports/run_output_latest.json`, which is the figure the site shows."
    ),
    "settled-provisioned": (
        "SETTLED, on the flat-rate bad-debt PROVISION, and superseded within the same run. "
        "`simulation/run_phase2b.py:2499-2503` sums the same rows at the end of the settlement "
        "loop, before the arrears engine has touched them, so its `bad_debt_gbp` is still "
        "`get_bad_debt_rate()` x billed amount -- a calibrated company assumption, not an "
        "outcome. Published here NAMED rather than dropped, because the run's own summary dict "
        "still carries these scalars and a reader who meets one elsewhere (e.g. "
        "`run_output_latest.json:final_treasury_gbp`) needs to know which figure it is."
    ),
}

#: Which clock each figure a `realised_metrics` block publishes is stated on. Written INTO the
#: block, so it travels with the numbers into the JSON where the reader is, and so `clock_audit`
#: has something in the artefact to read rather than re-deriving from this module -- a check that
#: consulted the code that produced the figure would be R15's tautology pattern.
ARM_FIGURE_CLOCKS = {
    "total_net_gbp": "settled-realised",
    "total_bad_debt_gbp": "settled-realised",
    "final_treasury_gbp": "settled-realised",
    "provisioned_net_gbp": "settled-provisioned",
    "provisioned_bad_debt_gbp": "settled-provisioned",
    "provisioned_final_treasury_gbp": "settled-provisioned",
}


def realised_metrics(result: dict) -> dict:
    """What the WORLD did to one arm's book. Nothing the company believed appears here.

    Every key is an outcome the supplier could only find out by living through the term:
    settled margin, the accounts that actually left, the money that actually failed to arrive.
    `expected_value_gbp` -- the quantity the arm maximises -- is deliberately absent, because a
    comparison that included it would be scoring the arm on its own objective.

    THE NET MARGIN IS SUMMED FROM THE ROWS, NOT READ OFF THE RUN'S SUMMARY, and that is the
    repair of a defect this artefact published (2026-08-28). `phase2b["total_net"]`,
    `["total_bad_debt"]` and `["final_treasury"]` are scalars frozen at
    `simulation/run_phase2b.py:2499-2503`. `simulation/run_phase4c_on_phase2b.py` then mutates
    `phase2b["all_records"]` IN PLACE -- `apply_emergent_bad_debt` replaces the flat-rate
    provision with the arrears model's realised write-offs, `apply_debt_recovery` credits back
    the DCA proceeds, and both carry the delta through the treasury column -- and nothing
    refreshes those three scalars. So the arm block published GBP 113,282.62 of control-arm net
    while `gross_to_net_bridge`, walking the very same list, published GBP 153,244.79: the
    entire GBP 39,962.17 difference is the bad-debt line moving between the two reads, to the
    penny (46,428.5849 provisioned against 6,466.41 realised).

    IT WAS NEVER A SETTLED-VERSUS-BANKED PAIR. Both figures are SETTLED; one is stale. The
    superseded read is kept as `provisioned_*` under its own declared clock rather than deleted,
    because deleting it leaves the next reader who meets `total_net` in a run dict with no way
    to tell which of the two they are holding -- and one of those readers,
    `saas/reporting/annual_report.py:916`, is still publishing it as the site's final treasury
    beside a realised net margin (`WORKER_FINDING_THE_PUBLISHED_TREASURY_IS_ON_A_SUPERSEDED_
    CLOCK_2026-08-28`).
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

    # The same refusal as `figure()`, one level down: an arm with no rows cannot be scored on
    # the realised clock, and a zero-filled block would be indistinguishable from an arm whose
    # world happened to settle to nothing. `_bridge_one_arm` refuses on identical grounds.
    records = phase2b.get("all_records")
    if not isinstance(records, list) or not records:
        raise ValueError(
            "this arm's run carries no `phase2b.all_records`, so its realised net margin "
            "cannot be summed and only the superseded provisioned scalars would remain. "
            "Refusing to report a figure on a clock this run cannot support.")
    realised_net = sum(float(r.get("net_margin_gbp", 0.0) or 0.0) for r in records)
    realised_bad_debt = sum(float(r.get("bad_debt_gbp", 0.0) or 0.0) for r in records)
    realised_treasury = float(records[-1].get("treasury_cash_balance_gbp", 0.0) or 0.0)

    return {
        "total_net_gbp": realised_net,
        # GROSS, and named for it (R14: no financial figure without its basis). This is revenue
        # minus wholesale, before levies, network, capital and bad debt -- the same basis
        # `simulation/portfolio_pnl.py` uses, and NOT the net line above.
        "total_gross_margin_gbp": figure("total_gross"),
        # The line that closed the 2026-08-26 gross-fell-while-net-rose divergence, and it was
        # in the run's output all along, unreported. Publishing gross and net without the
        # deductions between them left a GBP 30,924 gap that had to be recorded as
        # `observed and unexplained` -- see `gross_to_net_bridge` for the full walk.
        "total_capital_cost_gbp": figure("total_capital"),
        "total_bad_debt_gbp": realised_bad_debt,
        "final_treasury_gbp": realised_treasury,
        # THE SUPERSEDED READ, KEPT AND NAMED rather than dropped. See this function's docstring.
        #
        # READ FROM THE `provisioned_` NAMES, not from the bare ones (2026-08-28, second pass).
        # When this block was first written the bare scalars WERE the provisioned reading,
        # because nothing refreshed them. `simulation/settlement_clocks.refresh_settlement_
        # scalars` now re-derives the bare names from the mutated rows and preserves the
        # settlement loop's fold under `provisioned_*`, which is what stops every other consumer
        # reading a stale figure -- and would have silently turned these three labels into a
        # NEW instance of the very class they document, publishing realised figures under a
        # provisioned name. `figure()` still raises on a missing key, so a run that predates the
        # refresh is refused here rather than mislabelled.
        "provisioned_net_gbp": figure("provisioned_total_net"),
        "provisioned_bad_debt_gbp": figure("provisioned_total_bad_debt"),
        "provisioned_final_treasury_gbp": figure("provisioned_final_treasury"),
        "enterprise_value_gbp": ev["enterprise_value_gbp"],
        "account_count": ev["account_count"],
        "churned_accounts": len(phase2b.get("churned_billing_accounts", [])),
        # NOT a realised figure and labelled so: how many renewals the arm priced at all. It is
        # here because a delta of zero has two causes and only this number separates them.
        "renewals_priced_by_the_arm": len(phase2b.get("value_arm_log", [])),
        # THE CLOCK TRAVELS WITH THE FIGURE, in the block, not in a module constant the reader
        # of the JSON never sees. `clock_audit` reads these labels back out of the artefact, so
        # mislabelling one is a detectable act rather than a silent one.
        "clocks": dict(ARM_FIGURE_CLOCKS),
    }


#: The deduction lines that sit BETWEEN `total_gross` and `total_net`, each named with the
#: record fields it is summed from. Electricity and gas book the same economic line under
#: different keys, so both are summed into one bridge line rather than reported as two
#: half-visible ones. Source of truth for the identity: `sim.risk_engine.compute_net_margin`
#: as called from `simulation/hedged_settlement.py` (elec) and `simulation/gas_settlement.py`
#: (gas), plus the bad-debt deduction applied in `simulation/run_phase2b.py`.
GROSS_TO_NET_LINES = (
    ("policy_and_levies_gbp", ("policy_cost_gbp", "gas_policy_cost_gbp"),
     "RO + CfD + CCL + CM + FiT + SoLR mutualisation (elec), CCL + GGL (gas)"),
    ("network_gbp", ("network_cost_gbp", "gas_network_cost_gbp"),
     "DUoS + TNUoS unit charges (elec), transportation + metering (gas)"),
    ("capital_cost_gbp", ("capital_cost_gbp",),
     "cost of collateral, sized once per term and allocated across the periods that settled"),
    ("bad_debt_gbp", ("bad_debt_gbp",),
     "money billed that never arrived, deducted from net in run_phase2b"),
)


def _bridge_one_arm(result: dict) -> dict:
    """Walk ONE arm's settled ledger and sum every line between gross and net.

    From `phase2b.all_records` -- the world's own rows -- and NOT from the run's summary
    totals, because the summary publishes only three of the five lines and the two it omits
    are the two that turned out to matter.

    THE RESIDUAL IS THE CONTROL (R15). This does not assert that the five lines account for
    the whole difference; it computes `net - (gross - deductions)` and publishes it. A cost
    line that exists in the world and is missing from `GROSS_TO_NET_LINES` shows up here as a
    non-zero number instead of being silently absorbed into one of the lines that IS listed --
    which is the difference between a decomposition and a plausible story. A per-line
    `.get(field, 0.0)` would otherwise be exactly the fail-open pattern `realised_metrics`
    already refuses for the top-level figures: elec and gas records genuinely carry different
    key sets, so a missing key cannot be an error at the record level, and the residual is
    where a missing key at the LEDGER level becomes visible.
    """
    records = (result.get("phase2b") or {}).get("all_records")
    if not isinstance(records, list) or not records:
        raise ValueError(
            "this arm's run carries no `phase2b.all_records`, so the gross-to-net bridge "
            "cannot be walked. A zero-filled bridge would be indistinguishable from a run "
            "in which every deduction happened to be zero.")

    lines = {name: 0.0 for name, _fields, _why in GROSS_TO_NET_LINES}
    gross = net = revenue = wholesale = volume_kwh = 0.0
    for record in records:
        if not isinstance(record, dict):
            continue
        gross += float(record.get("margin_gbp", 0.0) or 0.0)
        net += float(record.get("net_margin_gbp", 0.0) or 0.0)
        revenue += float(record.get("revenue_gbp", 0.0) or 0.0)
        wholesale += float(record.get("wholesale_cost_gbp", 0.0) or 0.0)
        volume_kwh += float(record.get("consumption_kwh", 0.0) or 0.0)
        for name, fields, _why in GROSS_TO_NET_LINES:
            for field in fields:
                lines[name] += float(record.get(field, 0.0) or 0.0)

    deductions = sum(lines.values())
    return {
        "records": len(records),
        "gross_margin_gbp": gross,
        **lines,
        "total_deductions_gbp": deductions,
        "net_margin_gbp": net,
        # net MINUS what the five lines predict it should be. Not an error bar: a named hole.
        "unexplained_residual_gbp": net - (gross - deductions),
        # Gross itself splits two ways, and a fall in gross means one of these moved.
        "revenue_gbp": revenue,
        "wholesale_cost_gbp": wholesale,
        "volume_kwh": volume_kwh,
    }


def gross_to_net_bridge(control: dict, value: dict) -> dict:
    """Why net can rise while gross falls -- decomposed into named cost lines, per arm.

    THE DEFECT THIS ANSWERS (2026-08-26, this file's own artefact): the A/B reported gross
    margin FALLING by GBP 14,151 while net margin ROSE by GBP 16,773, and could attribute
    only GBP 2,591 of the GBP 30,924 gap to bad debt. The rest was written down as *observed
    and unexplained*, with volume-lost-to-churn recorded as an INFERRED candidate. It was
    unexplained because the instrument published gross, bad debt and net and nothing in
    between -- three of five lines -- so the two largest terms had nowhere to appear.

    Every line here is a sum over the world's own settled rows, so the sign convention is
    fixed and stated once: each `*_gbp` deduction line is a POSITIVE cost, and its
    contribution to the net delta is MINUS its delta. `net_delta_reconstructed_gbp` adds
    those contributions up; `reconstruction_error_gbp` is what it misses. A decomposition
    that does not close is a decomposition that has not been done, and this says which.

    THE RESIDUAL IS DELIBERATELY NOT A CONTRIBUTION, and the first draft of this function
    had it as one. With the residual in the sum, `reconstructed` reduces algebraically to
    `net_delta` for ANY set of lines whatsoever -- including the empty set -- so
    `reconstruction_closes` was a constant `True` reporting itself as a check. That is R15's
    TAUTOLOGY pattern written into the control built to close an unexplained gap, which
    would have been a fitting way to fail. Excluded, the sum closes only when the named
    lines really are all the lines, and `reconstruction_error_gbp` is exactly the residual
    delta it misses.
    """
    control_side = _bridge_one_arm(control)
    value_side = _bridge_one_arm(value)

    contributions = {
        # Gross carries its own sign: more gross is more net.
        "gross_margin_gbp": value_side["gross_margin_gbp"] - control_side["gross_margin_gbp"],
    }
    for name, _fields, _why in GROSS_TO_NET_LINES:
        # A deduction FALLING is a net gain, hence the inversion, applied once, here.
        contributions[name] = -(value_side[name] - control_side[name])

    net_delta = value_side["net_margin_gbp"] - control_side["net_margin_gbp"]
    reconstructed = sum(contributions.values())
    ranked = sorted(contributions.items(), key=lambda kv: -abs(kv[1]))

    return {
        "what_this_is": (
            "The arithmetic between gross and net, per arm, summed from the world's own "
            "settled records. Answers `gross fell and net rose` with named lines and "
            "figures instead of a candidate list."
        ),
        "clock": "settled-realised",
        "basis": (
            "R14 -- SETTLED-REALISED. Every figure is summed from phase2b.all_records AS THEY "
            "STAND AFTER the arrears engine, which is the same read the arm blocks now use and "
            "the same sum the site publishes. Not billed. Not banked -- this world has no "
            "banked clock; see `clock_definitions`. Until 2026-08-28 the arm blocks read "
            "run_phase2b's frozen pre-arrears scalars instead, so this bridge and the arm block "
            "published two different net margins for the same arm, GBP 39,962.17 apart."
        ),
        "line_definitions": {
            name: {"summed_from": list(fields), "is": why}
            for name, fields, why in GROSS_TO_NET_LINES
        },
        "control_arm": control_side,
        "value_arm": value_side,
        "net_delta_contribution_gbp": dict(ranked),
        "largest_contribution": ranked[0][0] if ranked else None,
        "net_delta_gbp": net_delta,
        "net_delta_reconstructed_gbp": reconstructed,
        # THE CONTROL ON THE CONTROL, and it is NOT a tautology: the residual is excluded
        # from the sum above, so a cost line that exists in the world and is missing from
        # GROSS_TO_NET_LINES lands here as a number rather than being absorbed. If this is
        # not ~0 the lines above do not add up to the headline and the attribution is not to
        # be quoted, whatever it says.
        "reconstruction_error_gbp": reconstructed - net_delta,
        "reconstruction_closes": abs(reconstructed - net_delta) < 0.01,
        "unexplained_residual_delta_gbp": (
            value_side["unexplained_residual_gbp"] - control_side["unexplained_residual_gbp"]),
    }


def churn_volume_attribution(control: dict, value: dict) -> dict:
    """Test the INFERRED candidate: was the gross fall the volume of the extra churned accounts?

    The 2026-08-26 reading offered `volume lost to the two extra churned accounts` as an
    explanation and was careful to label it inferred. This measures it: split BOTH ledgers by
    whether a row's billing account churned in one arm and not the other, and report the
    volume and gross those rows carry. If the differentially-churned accounts hold a small
    share of the gross fall, the candidate is RULED OUT and says so -- which is a finding, not
    a failure. The whole point of writing it down is that it can come back negative.
    """
    def rosters(result):
        return set((result.get("phase2b") or {}).get("churned_billing_accounts") or [])

    control_churned, value_churned = rosters(control), rosters(value)
    differential = sorted(control_churned.symmetric_difference(value_churned))
    differential_set = set(differential)

    def split(result):
        records = (result.get("phase2b") or {}).get("all_records") or []
        buckets = {"differentially_churned": {"gross_gbp": 0.0, "volume_kwh": 0.0},
                   "everyone_else": {"gross_gbp": 0.0, "volume_kwh": 0.0}}
        for record in records:
            if not isinstance(record, dict):
                continue
            customer_id = record.get("customer_id")
            if not isinstance(customer_id, str):
                continue
            key = ("differentially_churned"
                   if _billing_account_id(customer_id) in differential_set
                   else "everyone_else")
            buckets[key]["gross_gbp"] += float(record.get("margin_gbp", 0.0) or 0.0)
            buckets[key]["volume_kwh"] += float(record.get("consumption_kwh", 0.0) or 0.0)
        return buckets

    control_split, value_split = split(control), split(value)
    gross_delta = sum(v["gross_gbp"] for v in value_split.values()) - sum(
        v["gross_gbp"] for v in control_split.values())
    differential_gross_delta = (value_split["differentially_churned"]["gross_gbp"]
                                - control_split["differentially_churned"]["gross_gbp"])
    share = (differential_gross_delta / gross_delta) if gross_delta else None

    return {
        "what_this_is": (
            "Whether the accounts that churned under ONE arm and not the other carry the "
            "gross-margin fall. Measured, so it can rule the candidate out."
        ),
        "differentially_churned_accounts": differential,
        "control_only": sorted(control_churned - value_churned),
        "value_only": sorted(value_churned - control_churned),
        "control_arm": control_split,
        "value_arm": value_split,
        "gross_delta_gbp": gross_delta,
        "gross_delta_from_differentially_churned_gbp": differential_gross_delta,
        "share_of_gross_delta": share,
        "volume_delta_kwh": (
            sum(v["volume_kwh"] for v in value_split.values())
            - sum(v["volume_kwh"] for v in control_split.values())),
    }


def book_identity(result: dict) -> dict:
    """WHICH BOOK this ran on, in the artefact, so the next reader does not infer it from a date.

    `WORKER_FINDING_THE_AB_ARTEFACT_CANNOT_NAME_THE_BOOK_IT_RAN_ON_2026-08-26` is the finding
    this discharges, and it was raised against this file's own output. Two readings three days
    apart were each correct about a book the company no longer had, and in both cases the only
    way to tell was to compare a commit timestamp against a run timestamp by hand. Dual-fuel
    share is here because that is precisely the change that invalidated the previous reading:
    one household is one billing account, so a gas leg moves cost-to-serve, churn and lifetime
    value together.
    """
    records = (result.get("phase2b") or {}).get("all_records") or []
    accounts: dict[str, set] = collections.defaultdict(set)
    for record in records:
        customer_id = record.get("customer_id") if isinstance(record, dict) else None
        if not isinstance(customer_id, str):
            continue
        commodity = record.get("commodity") or "electricity"
        accounts[_billing_account_id(customer_id)].add(commodity)

    # THE POPULATION IS A FREE VARIABLE OF THE RUN, and until now the record of the run did
    # not capture it: the book is resolved at import time from the curriculum file, so a run
    # on the wrong segments produced a clean, complete, entirely plausible artefact -- R15
    # FAIL-OPEN one level up from R14's clock rule. Read from the resolver, never restated
    # here, so this cannot drift from the list the population was actually built with.
    from simulation.live_population import served_segments

    elec = sum(1 for c in accounts.values() if "electricity" in c)
    gas = sum(1 for c in accounts.values() if "gas" in c)
    dual = sum(1 for c in accounts.values() if {"electricity", "gas"} <= c)
    return {
        "served_segments": list(served_segments()),
        "billing_accounts_settled_in_window": len(accounts),
        "with_an_electricity_leg": elec,
        "with_a_gas_leg": gas,
        "dual_fuel": dual,
        "dual_fuel_share_of_accounts": (dual / len(accounts)) if accounts else None,
        "accounts_at_end_of_window": (
            (result.get("enterprise_value") or {}).get("portfolio", {}).get("account_count")),
        # WHAT EACH OF THE TWO COUNTS ABOVE SELECTS (2026-08-29,
        # `docs/design/ACCOUNT_POPULATION_CENSUS_2026-08-29.md`). Naming the RUN was only half
        # the provenance this block was created for: a reader could tell which book a figure
        # described and still not what the number counted, and six different account populations
        # were live across this repository's artefacts at once.
        #
        # AND ONE OF THESE TWO LABELS WAS WRONG. `accounts_at_end_of_window` reads as "the book
        # at the end", which is what a reader would take it for and what its own key says. It is
        # not: it is `enterprise_value.portfolio.account_count`, the VALUED subset — accounts
        # with a renewal point, still on supply, AND with an observed margin. It is smaller than
        # the book at the end by however many accounts could not be valued. The key is left
        # alone because renaming it would void every artefact that already cites it; what it
        # counts is stated here instead.
        "what_each_count_selects": {
            "billing_accounts_settled_in_window": (
                "every billing account with at least one settlement record anywhere in the "
                "window, dual-fuel legs collapsed, ceased or not"
            ),
            "accounts_at_end_of_window": (
                "MISLEADING KEY: not the book at the end. The VALUED subset — accounts with a "
                "renewal point, still on supply at the window's edge, and with an observed "
                "margin. Smaller than the book by the accounts that could not be valued."
            ),
        },
        "why_this_is_here": (
            "So a reader can tell WHICH book a figure describes without diffing a commit "
            "date against a run timestamp -- the defect logged as WORKER_FINDING_THE_AB_"
            "ARTEFACT_CANNOT_NAME_THE_BOOK_IT_RAN_ON_2026-08-26, raised against this file. "
            "The filename is not the control: `value_cycle_ab_resi.json` in fact served "
            "resi AND SME, so the one piece of provenance a reader had was misleading."
        ),
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


def belief_vs_outcome(value: dict) -> dict:
    """Was the arm's advantage INFERENCE, or was it wrong in a profitable direction?

    THE QUESTION THE WHOLE THESIS TURNS ON, and the data for it has been sitting in the run
    since the arm was built. `renewal_rate_chain` logs `believed_p_retain` per priced
    renewal and says in its own comment why: *"Carried so the two can be compared
    afterwards, which is the only way to find out whether this company's beliefs are worth
    acting on."* Nothing ever compared them.

    It matters because of what the 15:20Z run showed. After the segment repair the arm wins
    by GBP 3.08M, and on the I&C branch it believes a large margin will PROBABLY LOSE the
    customer -- P(leave) 0.81 at GBP 46/MWh -- charges it anyway because expected value
    still maximises there, and then mostly does not lose them. Four of five I&C accounts
    stay. An arm that profits because the world is kinder than its model said has not
    demonstrated inference advantage; it has demonstrated a lucky miscalibration, and the
    two produce the same P&L and completely different conclusions.

    THREE THINGS, and they answer different halves of the question:

      * CALIBRATION -- believed retention against realised retention, overall and by
        bucket. A gap here says the belief is systematically wrong and names the direction.
      * DISCRIMINATION -- whether a higher `believed_p_retain` actually corresponds to a
        customer more likely to stay, measured as the rank statistic (AUC) over the priced
        population. This is the half that survives a calibration error: a model can be
        uniformly wrong about the LEVEL and still rank correctly, which is real information.
        0.5 is no information at all.
      * WHERE THE MONEY SAT relative to the belief error -- the realised margin of renewals
        the arm was WRONG about, against those it was right about. If the advantage
        concentrates on the wrong ones, it is luck.

    BOTH SIDES ARE INDEPENDENT (R15). The belief is the company's own logged number; the
    outcome is a COUNT of `event_type == "churned"` in the world's event log at the same
    renewal. Not two readings of one probability -- a forecast and a tally.
    """
    phase2b = value.get("phase2b") or {}
    log = phase2b.get("value_arm_log")
    events = phase2b.get("customer_events")
    if not isinstance(log, list) or not log:
        return {"available": False, "reason": "the value arm priced nothing in this run"}
    if not isinstance(events, list) or not events:
        return {"available": False, "reason": "run publishes no customer_events to score against"}

    # (account, term_start) -> did they leave at THAT renewal. Keyed on the pair because an
    # account renews many times and only one of those decisions is the one being scored.
    outcome = {}
    for event in events:
        if not isinstance(event, dict):
            continue
        key = (event.get("customer_id"), event.get("event_date"))
        if event.get("event_type") == "churned":
            outcome[key] = False           # did NOT retain
        else:
            outcome.setdefault(key, True)  # retained

    scored, unmatched, unmatched_rows = [], 0, []
    for entry in log:
        if not isinstance(entry, dict) or entry.get("declined"):
            continue
        believed = entry.get("believed_p_retain")
        if not isinstance(believed, (int, float)) or isinstance(believed, bool):
            continue
        key = (entry.get("customer_id"), entry.get("term_start"))
        if key not in outcome:
            # NAMED AND SAMPLED, not dropped. An unmatched decision changes the
            # denominator, and a calibration figure whose denominator moved silently is
            # not a measurement -- but a bare COUNT is not much better, because the first
            # live run reported 30 of 58 unmatched and nothing in the artefact could say
            # why. `roll_lifecycle_event` returns None when `home_move_win_rates` has no
            # entry for that renewal month, and that roster's renewal schedule is derived
            # independently (`churn_model._renewal_periods`, acquisition_date + 365n,
            # truncated at the last settled period) from the term list the arm prices off.
            # So the artefact carries a sample and a per-year count, and the next reader
            # gets a hypothesis instead of a hole.
            unmatched += 1
            unmatched_rows.append({"account": key[0], "term_start": key[1]})
            continue
        scored.append({
            "account": entry.get("customer_id"),
            "term_start": entry.get("term_start"),
            "believed_p_retain": float(believed),
            "retained": bool(outcome[key]),
            "chosen_margin_gbp_per_mwh": entry.get("chosen_margin_gbp_per_mwh"),
        })

    if not scored:
        return {"available": False, "reason": "no priced renewal could be matched to an outcome",
                "unmatched_decisions": unmatched}

    believed_mean = sum(r["believed_p_retain"] for r in scored) / len(scored)
    realised_rate = sum(1 for r in scored if r["retained"]) / len(scored)

    # Rank statistic. Ties count a half, so a constant belief scores exactly 0.5 rather
    # than an accident of sort order.
    stayed = [r["believed_p_retain"] for r in scored if r["retained"]]
    left = [r["believed_p_retain"] for r in scored if not r["retained"]]
    if stayed and left:
        wins = sum((s > lo) + 0.5 * (s == lo) for s in stayed for lo in left)
        auc = wins / (len(stayed) * len(left))
    else:
        auc = None

    buckets = collections.defaultdict(lambda: {"n": 0, "retained": 0, "believed": 0.0})
    for row in scored:
        edge = min(int(row["believed_p_retain"] * 5), 4) / 5.0
        b = buckets[edge]
        b["n"] += 1
        b["retained"] += int(row["retained"])
        b["believed"] += row["believed_p_retain"]

    return {
        "available": True,
        "priced_and_scored": len(scored),
        "unmatched_decisions": unmatched,
        # COVERAGE, published beside the statistics rather than left to be divided out.
        # The first live run scored 28 of 58 decisions: the calibration and AUC below
        # therefore describe less than half the arm's answers, and a reader who missed
        # that would take them for the whole book. An unmatched decision is one the arm
        # priced and the world logged no lifecycle event for at that (account, term)
        # -- why that happens for half of them is NOT yet diagnosed, and saying so is
        # the point of this field.
        "scored_share_of_priced": (
            len(scored) / (len(scored) + unmatched) if (len(scored) + unmatched) else None),
        "unmatched_sample": unmatched_rows[:10],
        # THE OTHER HALF OF THE SAME QUESTION (2026-08-27). The unmatched sample has been here
        # since this field was written, and on its own it cannot answer WHY a decision missed:
        # a reader sees six accounts that never match and nothing to compare them against. The
        # matched sample makes the comparison possible in the artefact instead of requiring
        # another run -- which is what it cost to get this far, and the run is a decade sim.
        #
        # Measured on the residential book: the unmatched are the SAME SIX ACCOUNTS every year
        # (C2, C6, C8 in April; C3, C9 in July; C4 in October), and those six are exactly the
        # accounts acquired 2016-04-01 / -07-01 / -10-01 while the matched were acquired
        # 2016-01-01. Whether the arm's `term_start` or the world's `event_date` is the one
        # that drifts is what these two samples together are for -- see
        # docs/staging/done/WORKER_FINDING_THE_RENEWAL_SCHEDULE_WALKS_BACKWARDS_THROUGH_THE_CALENDAR_2026-08-27.md,
        # which measures a 365-day renewal step walking backwards through the calendar and
        # deliberately does NOT claim it is the cause.
        "matched_sample": [
            {"account": r["account"], "term_start": r["term_start"],
             "retained": r["retained"]}
            for r in scored[:10]
        ],
        "unmatched_by_year": dict(sorted(collections.Counter(
            (r["term_start"] or "")[:4] for r in unmatched_rows).items())),
        "unmatched_meaning": (
            "the arm priced this renewal and the world logged no lifecycle event at that "
            "(account, term_start). `simulation/customer_events.roll_lifecycle_event` "
            "returns None when `home_move_win_rates` carries no entry for the renewal "
            "month, and that roster's schedule is derived independently of the term list "
            "the arm prices off -- so these are renewals at which the world rolled NO "
            "churn decision, not renewals whose outcome is unknown. They are excluded "
            "rather than counted as retained: scoring a belief about retention against a "
            "renewal where leaving was impossible would flatter the arm."),
        "mean_believed_p_retain": believed_mean,
        "realised_retention_rate": realised_rate,
        "calibration_error": believed_mean - realised_rate,
        "discrimination_auc": auc,
        "auc_population": {"retained": len(stayed), "left": len(left)},
        "by_believed_bucket": [
            {
                "believed_from": edge,
                "believed_to": round(edge + 0.2, 1),
                "n": b["n"],
                "mean_believed_p_retain": b["believed"] / b["n"],
                "realised_retention_rate": b["retained"] / b["n"],
            }
            for edge, b in sorted(buckets.items())
        ],
        "reading": (
            "`discrimination_auc` at 0.5 means the belief carries NO information about who "
            "stays, and any advantage the arm shows is then a property of its calibration "
            "error rather than of inference -- which is the thesis failing while the P&L "
            "improves. Above 0.5 with a large `calibration_error` means the arm ranks "
            "customers correctly and misjudges the level, which is a different and more "
            "repairable finding. `auc_population` is published because this statistic is "
            "noise when one side is small. READ `scored_share_of_priced` FIRST: these "
            "statistics describe only the decisions that could be matched to an outcome, "
            "and on the first live run that was 28 of 58. R12: diagnostic, never a target."
        ),
    }


# ---------------------------------------------------------------------------
# A48 -- DOES THE METHOD HAVE SKILL? (the mission's own noun, instrumented)
# ---------------------------------------------------------------------------
#
# Director, 2026-08-28: "the enterprise value is the automated method for finding those
# customers, not the book itself." `saas/enterprise_value.py` computes the discounted net
# margin of the BOOK -- correctly, and that is the superseded definition. Nothing in the
# repository measured the METHOD. Frame: `docs/design/A48_MEASURING_THE_METHOD_FRAME.md`.
#
# WHY THIS IS NOT THE AUC ALREADY ABOVE. `belief_vs_outcome.discrimination_auc` asks whether
# the company's belief about CHURN ranks who leaves; it scored 0.4653, below a coin flip. The
# method question is different and can come out either way:
#
#   * rank churn badly and still create value, if the accounts it over-prices are ones where
#     the household keeps enough that the relationship survives anyway;
#   * rank churn WELL and create nothing, if the ranking is used purely to extract -- which is
#     the maximiser behaviour the director's sentence names, and would show as a HIGH churn AUC
#     beside a FLAT joint-value curve.
#
# The second case is the one worth being able to see and no instrument here could.

#: A priced term is 365 days from its start -- `simulation/churn_model._renewal_periods` steps
#: `acquisition_date + 365n`. Named rather than inlined because a settled row falling OUTSIDE
#: every priced term must be excluded, and the boundary is the whole reason it can be.
_TERM_DAYS = 365


def _priced_terms_by_account(log: list) -> dict[str, list[str]]:
    """Billing account -> the term starts the arm actually PRICED, ascending.

    Declines are excluded: a decline leaves the rate untouched, so there is no per-customer
    signal to rank anything by, and scoring one would put the flat rule's constant into a
    population whose whole subject is the arm's own variation.
    """
    terms: dict[str, set] = collections.defaultdict(set)
    for entry in log:
        if not isinstance(entry, dict) or entry.get("declined"):
            continue
        account, term = entry.get("customer_id"), entry.get("term_start")
        if isinstance(account, str) and isinstance(term, str):
            terms[account].add(term)
    return {account: sorted(t) for account, t in terms.items()}


def _term_period_of(terms_by_account: dict[str, list[str]]):
    """A `period_of` key for `build_household_value_share`, grouping by PRICED TERM.

    THE PROBLEM THIS SOLVES, named in the FRAME rather than discovered later. `A47`'s view
    aggregates by customer-YEAR. Decisions are per TERM -- 365 days from an arbitrary start --
    so a term straddles two calendar years for most accounts and a customer-year mixes the tail
    of one priced decision with the head of the next. Attributing a year's joint value to one
    decision would be wrong in a way that is invisible in the output.

    The arm's log is keyed by BILLING ACCOUNT and settled records by CUSTOMER (`C1`, `C1g` are
    two fuel legs of account `C1`), so the record is folded to its account with the same helper
    `saas.clv_model.build_clv` and `_lifetime_by_billing_account` use -- the two must not drift
    into different ideas of one account.

    A row outside every priced term returns None and is EXCLUDED AND COUNTED by the view. That
    is the point of the boundary: settled pounds from a term the arm never priced carry no
    signal, and folding them into the nearest one would put one decision's money against
    another decision's price.
    """
    def period_of(record):
        account = _billing_account_id(record["customer_id"])
        terms = terms_by_account.get(account)
        if not terms:
            return None
        settled = record["settlement_date"]
        index = bisect.bisect_right(terms, settled) - 1
        if index < 0:
            return None
        term = terms[index]
        if (date.fromisoformat(settled) - date.fromisoformat(term)).days >= _TERM_DAYS:
            return None
        return term
    return period_of


def _concordance(points: list[tuple[float, float]]) -> tuple[float | None, int, int]:
    """Does the SIGNAL rank the OUTCOME better than chance? Returns (c, pairs, outcome_ties).

    The rank statistic over all pairs: a pair is CONCORDANT when the higher signal goes with
    the higher outcome. Signal ties count a half, exactly as `discrimination_auc` above handles
    them, which is what makes a CONSTANT signal score exactly 0.5 rather than 1.0 or 0.0 by an
    accident of sort order -- and that is the null this whole figure is read against.

    Pairs tied on the OUTCOME are excluded and counted, never scored: with a continuous
    pounds outcome they should be rare, and if they are common that is a finding about the
    outcome being degenerate rather than a number to divide past.

    Zero comparable pairs returns None, NEVER 0.5. "No information" and "nothing to measure"
    are different statements, and a statistic that reported the null when it had no population
    would be the FAIL-OPEN killer wearing this control's name (R15).
    """
    concordant = signal_ties = comparable = outcome_ties = 0
    for i in range(len(points)):
        signal_i, outcome_i = points[i]
        for j in range(i + 1, len(points)):
            signal_j, outcome_j = points[j]
            if outcome_i == outcome_j:
                outcome_ties += 1
                continue
            comparable += 1
            if signal_i == signal_j:
                signal_ties += 1
            elif (signal_i > signal_j) == (outcome_i > outcome_j):
                concordant += 1
    if not comparable:
        return None, 0, outcome_ties
    return (concordant + 0.5 * signal_ties) / comparable, comparable, outcome_ties


#: Draws in the permutation null. 20,000 puts the Monte-Carlo error on the reported p-value at
#: well under a percentage point, and the whole null costs a fraction of a second at these sizes.
NULL_DRAWS = 20_000
#: FIXED, and published with the result. A seeded permutation is reproducible; an unseeded one
#: would make a published artefact differ from its own re-run for no reason a reader could tell
#: from a real change.
NULL_SEED = 20260828


def concordance_null_spread(points: list[tuple[float, float]], observed,
                            draws: int = NULL_DRAWS, seed: int = NULL_SEED) -> dict:
    """How wide is the null? The point null 0.5 says nothing about SAMPLING.

    WHY THIS EXISTS. The first live reading of `method_skill` was 0.6136 on 12 decisions, published
    beside a null of exactly 0.5 -- which invites "the method has skill" from a figure a RANDOM
    signal reaches about one run in six.

    A PERMUTATION, NOT A CLOSED FORM, AND THE REAL DATA IS WHY. The first version used Kendall's
    untied null variance, `Var(tau) = 2(2n + 5) / (9 n (n - 1))`, and REFUSED when either side
    carried ties because that formula overstates the spread when they do. Its first live
    application refused: the arm priced 25 renewals at 24 distinct margins, so a tied signal pair
    is the NORMAL case here, not the exception. A bound that refuses on the data it was built for
    is not a bound.

    Permuting the observed signal values against the fixed outcomes reproduces the tie structure
    exactly -- the same multiset of signals, so the same ties, in a random order -- and needs no
    formula for it. The untied closed form is kept as an independent CROSS-CHECK in the tests
    (`test_the_permuted_null_matches_the_closed_form_when_there_are_no_ties`), which is what
    stops the permutation being one unverified reading.

    Deterministic by construction: fixed seed, published with the result.
    """
    if observed is None or len(points) < 3:
        return {"available": False,
                "reason": "fewer than three ranked decisions -- there is no sampling distribution"}
    signals = [signal for signal, _ in points]
    outcomes = [outcome for _, outcome in points]
    if len({round(o, 12) for o in outcomes}) < 2:
        return {"available": False,
                "reason": ("every decision shares one outcome, so no permutation of the signal "
                           "can rank anything -- the null is undefined rather than wide")}

    rng = random.Random(seed)
    shuffled = list(signals)
    null = []
    for _ in range(draws):
        rng.shuffle(shuffled)
        value, _pairs, _ties = _concordance(list(zip(shuffled, outcomes)))
        if value is not None:
            null.append(value)
    if len(null) < draws // 2:
        return {"available": False,
                "reason": "more than half the permutations produced no comparable pair"}

    null.sort()
    mean = sum(null) / len(null)
    sd = math.sqrt(sum((x - mean) ** 2 for x in null) / len(null))
    lo = null[int(0.025 * len(null))]
    hi = null[min(len(null) - 1, int(0.975 * len(null)))]
    # Two-sided: how often does a random signal land AT LEAST as far from the null centre?
    reach = sum(1 for x in null if abs(x - mean) >= abs(observed - mean))
    p_two = reach / len(null)
    inside = lo <= observed <= hi
    return {
        "available": True,
        "null_mean": mean,
        "null_sd": sd,
        "null_95_interval": [lo, hi],
        "p_two_sided": p_two,
        "observed_inside_the_null_interval": inside,
        "draws": len(null),
        "seed": seed,
        "signal_ties_in_the_observed_data": sum(
            1 for i in range(len(signals)) for j in range(i + 1, len(signals))
            if signals[i] == signals[j]),
        "method": ("permutation of the observed signal values against the fixed outcomes, {:,} "
                   "draws at seed {} -- reproduces the tie structure exactly, where the untied "
                   "Kendall closed form would overstate the spread".format(len(null), seed)),
        "reading": (
            ("The observed value sits INSIDE the interval a random signal produces, so this run "
             "does not distinguish the method from chance in either direction. That is a "
             "statement about how few decisions there are, not about the method.")
            if inside else
            ("The observed value sits OUTSIDE the interval a random signal produces at this "
             "sample size. Read it with the clustering bound above: the permutation assumes "
             "exchangeable decisions and these are clustered on a handful of accounts, so the "
             "true interval is wider than this one.")),
    }


def method_skill(value: dict) -> dict:
    """A48 L2: does the arm's own per-customer signal rank JOINT value created?

    SIGNAL -- `chosen_margin_gbp_per_mwh`, the margin the arm chose for this customer at this
    renewal. Genuinely per-customer: 24 distinct margins across 25 priced renewals on the
    2026-08-28 run, against the flat rule's single GBP 2.00.

    OUTCOME -- two-sided, and computable only since `A47`:

        joint_value = household_saving_gbp + our_net_margin_gbp
        joint_value_ratio = joint_value / counterfactual_gbp

    Normalised by the counterfactual so a large account does not outrank a small one for being
    large. NET margin, never gross: a contribution margin wearing a net margin's name is the
    defect recorded against `saas/cost_to_serve.py` on 2026-08-17, and it valued the whole book.
    Where the net is unavailable this returns unavailable rather than substituting the gross.

    WHAT IT IS NOT. Not a claim about the COST of finding a customer, and not a claim about
    improvement run over run -- both are named in the FRAME's section 1 and neither is in scope
    at L2. And joint value is a SPLIT of a surplus whose size is not observable to us, not
    value created: `company/analytics/household_value_share.py` says why at length.

    BOTH SIDES ARE INDEPENDENT (R15). The signal is the company's own logged decision; the
    outcome is built from the world's settled records against the published default tariff.
    A price and a consequence, not two readings of one number.
    """
    phase2b = value.get("phase2b") or {}
    log = phase2b.get("value_arm_log")
    records = phase2b.get("all_records")
    if not isinstance(log, list) or not log:
        return {"available": False, "reason": "the value arm priced nothing in this run"}
    if not isinstance(records, list) or not records:
        return {"available": False,
                "reason": "the run carried no settlement records, so no outcome exists"}

    terms_by_account = _priced_terms_by_account(log)
    if not terms_by_account:
        return {"available": False,
                "reason": "the arm declined every renewal, so it emitted no per-customer signal"}

    view = build_household_value_share(
        records,
        svt_rate_for=published_default_tariff,
        period_of=_term_period_of(terms_by_account),
    )

    # FOLD THE FUEL LEGS ONTO THE ACCOUNT THE DECISION WAS MADE FOR. The view keys by the
    # record's own customer (`C1`, `C1g`); the decision is one price for account `C1`. Net
    # margin keeps the view's own rule -- None if ANY leg could not supply one, never a partial
    # sum wearing the whole account-term's name.
    folded: dict[tuple[str, str], dict] = {}
    for (customer_id, term), row in view.by_customer_period.items():
        key = (_billing_account_id(customer_id), term)
        acc = folded.setdefault(key, {"saving": 0.0, "net": 0.0, "counterfactual": 0.0,
                                      "blind": False})
        if row.household_saving_gbp is None or row.our_net_margin_gbp is None:
            acc["blind"] = True
            continue
        acc["saving"] += row.household_saving_gbp
        acc["net"] += row.our_net_margin_gbp
        acc["counterfactual"] += row.counterfactual_gbp

    points, scored_rows, unscorable = [], [], 0
    for entry in log:
        if not isinstance(entry, dict) or entry.get("declined"):
            continue
        signal = entry.get("chosen_margin_gbp_per_mwh")
        if not isinstance(signal, (int, float)) or isinstance(signal, bool):
            unscorable += 1
            continue
        acc = folded.get((entry.get("customer_id"), entry.get("term_start")))
        # A decision with no settled pounds behind it, or whose net margin or counterfactual
        # never resolved, is EXCLUDED AND COUNTED. Scoring it at zero would put a coverage gap
        # into the outcome and the statistic would read it as a real ranking.
        if acc is None or acc["blind"] or acc["counterfactual"] <= 0:
            unscorable += 1
            continue
        ratio = (acc["saving"] + acc["net"]) / acc["counterfactual"]
        points.append((float(signal), ratio))
        scored_rows.append({"account": entry.get("customer_id"),
                            "term_start": entry.get("term_start"),
                            "chosen_margin_gbp_per_mwh": float(signal),
                            "joint_value_ratio": ratio})

    concordance, pairs, outcome_ties = _concordance(points)
    # THE NULL THAT MAKES THE FIGURE READABLE. The flat-rules arm's signal is a CONSTANT -- and
    # its `value_arm_log` is empty by construction, so the null cannot be read off a control
    # run and has to be constructed here: the same code path, the same outcomes, the signal
    # replaced by the flat rule's single margin. Every pair ties on the signal, so it MUST
    # return exactly 0.5. Anything else means the estimator is broken, not that the arm has
    # skill -- which is the only way a reader can tell those two apart.
    null_concordance, _, _ = _concordance(
        [(TARGET_MARGIN_GBP_PER_MWH, outcome) for _, outcome in points])

    accounts = sorted({row["account"] for row in scored_rows})
    return {
        "available": concordance is not None,
        "reason": (None if concordance is not None else
                   "no two scored decisions differed in joint value, so nothing could be ranked"),
        "concordance": concordance,
        # NOT decoration. A constant signal must score exactly 0.5 through this same code, and
        # publishing it beside the estimate is what makes the estimate falsifiable in the file
        # rather than only in the test suite.
        "null_constant_signal_concordance": null_concordance,
        # AND HOW WIDE THAT NULL IS. The point null above proves the estimator is not broken; it
        # says nothing about whether THIS number is distinguishable from a random signal at THIS
        # sample size. Published together because the first live reading (0.6136 on 12 decisions)
        # is a value a random signal reaches 16% of the time.
        "null_spread": concordance_null_spread(points, concordance),
        "signal": "chosen_margin_gbp_per_mwh (the arm's own per-customer decision)",
        "outcome": "(household_saving_gbp + our_net_margin_gbp) / counterfactual_gbp, per priced term",
        "basis": ("settled clock both sides; counterfactual = the published Ofgem default tariff "
                  "cap unit rate for each settlement date, falling back to the pre-2019 SVT "
                  "series for electricity, at this account's own metered volumes (R14)"),
        "decisions_scored": len(points),
        "accounts": len(accounts),
        "decisions_the_outcome_could_not_reach": unscorable,
        "comparable_pairs": pairs,
        "pairs_tied_on_outcome": outcome_ties,
        "settled_rows_outside_every_priced_term": view.records_this_view_could_not_value,
        "scored_sample": scored_rows[:10],
        "bound": (
            "READ THIS BEFORE THE NUMBER. A rank statistic over this few decisions, clustered on "
            "this few accounts, has a wide confidence interval and every account is potentially "
            "influential. This is the same resolution wall that made the 2026-08-28 "
            "chase-on/chase-off comparison unreadable, arriving on a different question. Two "
            "things make it less bad here: the outcome is continuous, so pounds have no 1/17 "
            "quantum and a small effect is small rather than invisible; and every priced "
            "decision with settled pounds behind it contributes, not only the ones the world "
            "rolled an event for. It is still a handful of accounts, and `A46` (book depth) is "
            "upstream of this being worth much -- which remains the director's decision."
        ),
        "reading": (
            "0.5 means the arm's own price carries NO information about whether value was "
            "jointly created -- the method has no skill, whatever the book did. Above 0.5 means "
            "the decisions it priced highest are the ones where household and company came out "
            "ahead together. BELOW 0.5 is the director's own case and the one worth being able "
            "to see: the arm ranks confidently and uses the ranking to EXTRACT, so its most "
            "expensive decisions destroy the relationship. Read it beside "
            "`belief_vs_outcome.discrimination_auc` -- a high churn AUC with a flat curve here "
            "is a maximiser working correctly on a one-sided objective. R12: a DIAGNOSTIC, "
            "never a target; nothing optimises this figure."
        ),
    }


def household_sides(**arms) -> dict:
    """THE HOUSEHOLD'S SIDE OF EACH ARM (atom `A47`; director, 2026-08-28).

    Every other figure in this artefact is OURS -- what each arm earned, what it churned, what it
    priced. This is what the households on that arm's book KEPT: what they would have paid on the
    published default tariff at their own metered volumes, less what they actually paid us. Until
    it landed here the comparison had one column, and the mission's sentence -- value is created
    and THEN shared, so every decision has two sides -- could not be checked in either direction.

    IT IS THE LADDER'S FUNCTION, NOT A SECOND ONE. `tools/run_price_ladder.household_side` already
    computes exactly this from a run result, argues its counterfactual at length and is tested; a
    second implementation here would be a second thing to keep in step, and the two figures would
    drift the first time either was touched. Same reason `published_default_tariff` is imported
    from there rather than restated.

    AN ARM THAT DID NOT RUN IS ABSENT, NEVER A ZERO, and the direction is why this is a function
    rather than a dict comprehension inline. A household saving of GBP 0 is exactly what "we
    charged them the default tariff and shared nothing" produces -- the worst answer this figure
    can return -- so a zero-filled arm would publish that answer as though a pass had measured it.
    The key is simply absent, and every reader of this artefact has to decide what to say about
    that rather than being handed a number.
    """
    return {name: household_side(result)
            for name, result in arms.items() if result is not None}


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


#: What each funnel stage means to a reader who has not read the guards, in the order they fire.
#: Prose lives HERE and the counting lives in `renewal_funnel`, so a stage cannot be described in
#: the artefact without being counted or counted without being described.
FUNNEL_STAGE_MEANINGS: dict[str, str] = {
    "control_arm_no_writer": (
        "the control arm: `renewal_margin_uplift` returns before computing anything under "
        "`flat_rules`, so every renewal the world offered lands here. On the control this is the "
        "WHOLE funnel and that is correct -- it is what makes the world's own renewal count "
        "readable from a run in which the arm priced nothing."),
    "no_locked_rate": (
        "a term with no locked unit rate to move -- a deemed or flex period, priced at "
        "settlement rather than struck. There is no margin here for any arm to choose."),
    "acquisition_term": (
        "term 0. The account had no prior term when this one was struck, so there is nothing "
        "observed to price against (`MIN_TERM_INDEX_FOR_UPLIFT`)."),
    "not_the_arms_commodity": (
        "gas. `UPLIFTABLE_COMMODITY` is electricity: the arm's churn and cost-to-serve inputs "
        "are calibrated on the electricity book and the supplier has never fitted them to gas."),
    "product_not_upliftable": (
        "the term's `tariff_type` is not one this writer prices "
        "(`UPLIFTABLE_TARIFF_TYPES` = fixed, pass_through). READ THE PER-VALUE BREAKDOWN BESIDE "
        "THIS COUNT. A term carrying `None` is a DRAWN account, and the field is unset because "
        "the world has no standard-variable product to set it to -- `build_renewal_schedule` "
        "settles exactly fixed, flex, deemed and pass_through, and SVT exists only as a "
        "comparison benchmark. It is an honest silence about a product the world lacks, NOT a "
        "label someone forgot to write, and the repair is an SVT product in the world rather "
        "than an assignment to this field "
        "(`docs/design/DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md`, settled 2026-08-28)."),
    "no_observed_history": (
        "nothing settled for this account inside the one-year observation window before the "
        "term start, so the arm has no EAC, tenure or current rate to price from."),
    "declined": (
        "the arm RAN and found no margin that survives both the price cap and the churn model's "
        "support bound. A decision, not an omission."),
    "priced": "the arm chose a margin for this renewal. This is `decision_shape.priced`.",
}


def renewal_funnel(result: dict, arm_label: str) -> dict:
    """Every renewal the world offered this arm, and the stage each one stopped at.

    THE DENOMINATOR OF THE HEADLINE, and until 2026-08-28 no artefact carried one. The A/B
    published `decision_shape.priced` = 25 against a book of 210 billing accounts settled in the
    window, and nothing in the file could distinguish "the world offered 25 renewals" from "the
    world offered 1,251 and 1,226 of them were refused by a guard" -- the arm's eligibility guards
    return a 0.0 uplift and the chain logged nothing at all for a renewal it did not price, so a
    missing log line meant three different things at once. R15's fail-silent pattern applied to a
    POPULATION: the reader cannot tell a small experiment from a large one.

    Read off `phase2b.value_arm_funnel_log`, which the rate chain writes ONE row into per call of
    `decide_renewal_rate` -- unconditionally, before the priced/declined branch, so no renewal can
    reach the funnel by one path and miss it by another. The stage keys come from the arm adapter
    (`FUNNEL_STAGES`), never re-derived here: a counter carrying its own copy of the eligibility
    rule is how a funnel comes to report a population its subject does not have.

    `available: False` for a run predating the log rather than a reconstructed count. A funnel
    rebuilt from `basis_risk_terms` plus a guess at each term's product would pass silently on a
    run whose guards had moved, which is precisely the failure this block exists to make loud.

    R12: a diagnostic. Nothing here is a target and no stage count is a thing to improve.
    """
    log = (result.get("phase2b") or {}).get("value_arm_funnel_log")
    if not isinstance(log, list) or not log:
        return {
            "available": False,
            "reason": (
                "this run carries no `value_arm_funnel_log`. The chain has written one since "
                "2026-08-28; a run without it predates the instrumentation and its denominator "
                "is NOT reconstructed here -- see this function's docstring."),
        }
    counts = collections.Counter(row.get("stage") for row in log)
    unknown = sorted(str(s) for s in counts if s not in FUNNEL_STAGES)
    # The one stage whose count is a finding rather than a fact, so it is broken out by the value
    # that caused it. "Six accounts on a variable tariff" and "213 accounts whose product was
    # never labelled" are the same integer and opposite conclusions.
    product_values = collections.Counter(
        repr(row.get("tariff_type")) for row in log
        if row.get("stage") == "product_not_upliftable")
    reached = len(log)
    priced = counts.get(STAGE_PRICED, 0)
    return {
        "available": True,
        "arm": arm_label,
        "what_this_is": (
            "One row per renewal the rate chain saw on this arm, grouped by the stage it stopped "
            "at. `renewals_the_world_offered` is every call of `decide_renewal_rate` "
            "(simulation/run_phase2b.py, inside the chronological term loop) and is therefore "
            "already NET of two world-side exclusions the chain never sees: a term belonging to "
            "an account that had already churned, and a successor term not yet activated by a "
            "home-move win. Both are `continue`s above the call."),
        "renewals_the_world_offered": reached,
        "reached_the_arm_with_an_arm_set": reached - counts.get("control_arm_no_writer", 0),
        "priced": priced,
        "declined": counts.get(STAGE_DECLINED, 0),
        "priced_share_of_renewals_offered": round(priced / reached, 4) if reached else None,
        # THE DROP AT EACH STAGE, in the order the guards fire, each with the count that stopped
        # there and what stopping there means.
        "stages": [
            {
                "stage": stage,
                "count": counts.get(stage, 0),
                "share_of_renewals_offered": (
                    round(counts.get(stage, 0) / reached, 4) if reached else None),
                "means": FUNNEL_STAGE_MEANINGS[stage],
            }
            for stage in FUNNEL_STAGES
        ],
        # Broken out because this stage's count is the artefact's biggest single drop and its
        # MEANING depends entirely on which products are behind it.
        "product_not_upliftable_by_tariff_type": dict(sorted(product_values.items())),
        "accounts_the_arm_priced": sorted({
            row.get("customer_id") for row in log if row.get("stage") == STAGE_PRICED}),
        "accounts_the_world_offered_a_renewal": len({row.get("customer_id") for row in log}),
        # A stage this module does not know about means the adapter grew a guard and this block
        # did not follow it. Named rather than folded into an "other" bucket.
        "unrecognised_stages": unknown,
        "reading": (
            "Read `priced_share_of_renewals_offered` before any per-decision claim in this file. "
            "The stages are the arm's OWN eligibility rule, so a large drop is not automatically "
            "a defect. The drop at `product_not_upliftable` on terms whose tariff_type is `None` "
            "was read as a defect until 2026-08-28 and is NOT one: the field is unset because the "
            "world has no standard-variable product, and setting it to `fixed` was REFUSED -- it "
            "would assert a 100%-fixed domestic book against a published share of roughly one "
            "third, and the only thing it would improve is this experiment's `n` (R13; "
            "`docs/design/DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md`). "
            "SO THE SMALL PRICED SURFACE IS MARKET STRUCTURE, NOT PLUMBING: roughly a third of a "
            "domestic book is on a fixed deal at any time and only that third has a renewal rate "
            "that can be moved. Nor is the current count the right one -- when an honest SVT "
            "product lands, the in-scope surface is on the order of a third of 222 electricity "
            "renewals, and it gets SMALLER as a share of the book, not bigger. This instrument's "
            "power ceiling is a fact about how much of a domestic book per-customer pricing can "
            "legitimately reach. R12: diagnostic, never a target, and specifically NOT a cue to "
            "relax a guard so the experiment gets a bigger n."
        ),
    }


def decision_population(funnels: dict[str, dict]) -> dict:
    """The arms' denominators, side by side, with the mechanism that makes them differ.

    WHY THIS SITS BESIDE THE ADVANTAGE. `arm_identity` guards the POLICY fields -- it fails if the
    two arms differ in anything but `renewal_margin_arm` -- and nothing guarded the decision
    POPULATION. On the 2026-08-27 three-arm run the value arm priced 25 renewals and the level arm
    priced 34, a 36% larger denominator for an arm whose whole design is to price EXACTLY the
    renewals the value arm prices (`renewal_margin_uplift` deliberately does not return early for
    `FLAT_AT_LEVEL`, so it passes every guard the value arm passes). A reader taking a per-decision
    figure from one arm and comparing it with the other is then dividing two different books.

    THE MECHANISM IS SEQUENTIAL-A/B ROSTER DIVERGENCE, and it is legitimate: different prices cause
    different churn, a churned account's remaining terms are skipped by the world before the chain
    is ever called, and so an account that leaves in year two removes every renewal it would have
    presented in years three onward. The eligible pool is small enough that one early departure
    moves the denominator by several decisions. That is not a defect to fix -- suppressing it would
    mean pricing renewals for customers who left -- but it MUST be stated, because it is the reason
    two arms can differ in n without differing in eligibility.

    R12: a diagnostic. The denominators are not to be equalised.
    """
    available = {k: f for k, f in funnels.items() if f.get("available")}
    if len(available) < 2:
        return {
            "available": False,
            "reason": (
                "fewer than two arms carry a funnel, so there are no denominators to compare. "
                "A single arm's count is published in its own `renewal_funnel` block."),
        }
    per_arm = {
        arm: {
            "renewals_the_world_offered": f["renewals_the_world_offered"],
            "priced": f["priced"],
            "declined": f["declined"],
            "accounts_priced": len(f["accounts_the_arm_priced"]),
        }
        for arm, f in available.items()
    }
    priced = {arm: v["priced"] for arm, v in per_arm.items()}
    deciding = {arm: v for arm, v in priced.items() if v}
    spread = (max(deciding.values()) - min(deciding.values())) if len(deciding) > 1 else 0
    smallest = min(deciding.values()) if deciding else 0
    return {
        "available": True,
        "per_arm": per_arm,
        "priced_by_arm": priced,
        "largest_denominator_difference": spread,
        "difference_as_share_of_the_smaller": (
            round(spread / smallest, 4) if smallest else None),
        "the_mechanism": (
            "Sequential A/B roster divergence. The arms are identical in eligibility -- "
            "`renewal_margin_uplift` passes `flat_at_level` through every guard the value arm "
            "passes, so neither arm can see a renewal the other cannot. They differ in WHICH "
            "renewals still exist: a different price changes who churns, `run_phase2b` skips "
            "every remaining term of a churned billing account before the rate chain is called, "
            "and an account that leaves early therefore removes all of its later renewals from "
            "that arm's denominator. `churn_roster_diff` names the accounts."),
        "what_a_reader_must_not_do": (
            "Do not take a per-decision figure from one arm and compare it with a per-decision "
            "figure from another: the denominators above are different books, not the same book "
            "measured twice. Arm-level totals (net margin, treasury, enterprise value) ARE "
            "comparable -- they are sums over the whole run and carry the roster difference "
            "inside them, which is the effect being measured."),
        "why_this_is_not_a_defect": (
            "Equalising the denominators would mean pricing renewals for customers who had "
            "already left, which is not a world any supplier operates in. The difference is the "
            "measurement, not noise in it. R12: diagnostic, never a target."),
    }


def bound_attribution(control: dict, value: dict) -> dict:
    """WHO CHOSE the arm's prices -- the customer, or a bound -- and where the money sits.

    THE HEADLINE SECTION, and the thing `decision_shape` could report but not say. That block
    counts `ceiling_bound` and `extrapolation_bound` honestly and leaves them among fourteen
    other integers, so an artefact in which the lawful price cap set the margin on half the
    arm's answers reads exactly like one in which it set none of them.

    "The advantage must come from INFERENCE, never ACCESS" fails just as completely when the
    advantage comes from a BOUND. A margin set by the ceiling is a margin the arm did not
    choose: lift the ceiling and it would have gone higher, which is precisely what
    `decide_margin` records `ceiling_bound` to answer -- *"DID THE BOUND ACTUALLY DECIDE?
    Answered by asking what the arm would have chosen with the bound lifted, because there is
    no other way to answer it."* This section carries that per-decision answer up to the
    headline and puts the realised money beside it.

    TWO BOUNDS, NAMED APART, because they are opposite findings. The CEILING is the Ofgem
    domestic cap -- an external, lawful constraint a real supplier really has, and a price
    pinned to it says the company's beliefs did not bite before the law did. The SUPPORT bound
    is `max_supported_rate_increase_pct()` -- the frontier of what the churn model has evidence
    for, which is this company's own ignorance and not a fact about the world.

    THE MONEY, not only the count. A bound that decided many cheap answers and no expensive
    ones is a footnote; one that decided the three accounts carrying the delta is the headline.
    Attribution is by BILLING ACCOUNT because that is the unit the realised margin is summed on,
    and an account is counted as bound-decided if ANY of its renewals was -- deliberately the
    inclusive reading, since a single capped renewal fixes the rate that account then pays for
    a whole term.
    """
    log = [e for e in ((value.get("phase2b") or {}).get("value_arm_log") or [])
           if not e.get("declined")]
    if not log:
        return {
            "available": False,
            "why_not": (
                "this arm priced no renewal, so there is no answer to attribute. Expected for "
                "the control arm; on the value arm it means the writer never fired, and "
                "`decision_shape` says the same thing."
            ),
        }

    ceiling = [e for e in log if e.get("ceiling_bound")]
    #: SUPPORT-ONLY, so the two counts do not double-count a decision both bounds reached. The
    #: ceiling is named first because it is the binding one when both apply: the company may
    #: not offer above it whatever its model believes.
    support = [e for e in log if e.get("extrapolation_bound") and not e.get("ceiling_bound")]
    bound_decided = ceiling + support
    freely_chosen = [e for e in log
                     if not e.get("ceiling_bound") and not e.get("extrapolation_bound")]

    def _median(entries: list[dict]) -> float | None:
        margins = sorted(e["chosen_margin_gbp_per_mwh"] for e in entries)
        return round(margins[len(margins) // 2], 2) if margins else None

    control_book, _ = _lifetime_by_billing_account(control)
    value_book, basis = _lifetime_by_billing_account(value)
    bound_accounts = {_billing_account_id(e["customer_id"]) for e in bound_decided
                      if isinstance(e.get("customer_id"), str)}
    net_on_bound = net_elsewhere = abs_on_bound = abs_elsewhere = 0.0
    for account_id in set(control_book) | set(value_book):
        c = (control_book.get(account_id) or {}).get("total")
        v = (value_book.get(account_id) or {}).get("total")
        if c is None and v is None:
            continue
        delta = (v or 0.0) - (c or 0.0)
        if account_id in bound_accounts:
            net_on_bound += delta
            abs_on_bound += abs(delta)
        else:
            net_elsewhere += delta
            abs_elsewhere += abs(delta)
    total_abs = abs_on_bound + abs_elsewhere
    share_of_movement = (abs_on_bound / total_abs) if total_abs else None
    share_of_priced = len(bound_decided) / len(log)

    if not bound_decided:
        decided_by = "the customer"
    elif (share_of_priced >= BOUND_DECIDED_HEADLINE_SHARE
          or (share_of_movement or 0.0) >= BOUND_DECIDED_HEADLINE_SHARE):
        decided_by = "a bound"
    else:
        decided_by = "mixed"

    headline = (
        "{bound} of {priced} priced renewals ({pct:.0%}) had their margin set by a bound rather "
        "than by anything about the customer -- {ceiling} by the lawful price cap and {support} "
        "by the frontier of what the churn model has evidence for. Those decisions sit on "
        "{accounts} billing account(s) carrying {money}of the realised margin movement between "
        "the arms. On this run the arm's answers were decided by {verdict}."
    ).format(
        bound=len(bound_decided), priced=len(log), pct=share_of_priced,
        ceiling=len(ceiling), support=len(support), accounts=len(bound_accounts),
        money=("{:.0%} ".format(share_of_movement) if share_of_movement is not None
               else "an unmeasurable share "),
        verdict=decided_by,
    )

    return {
        "available": True,
        #: THE ONE LINE. Computed from the counts above every time, never stored, so it cannot
        #: describe a previous run.
        "headline": headline,
        "decided_by": decided_by,
        "headline_share_threshold": BOUND_DECIDED_HEADLINE_SHARE,
        "priced": len(log),
        "decided_by_the_lawful_ceiling": len(ceiling),
        "decided_by_the_model_support_bound": len(support),
        "chosen_freely": len(freely_chosen),
        "share_of_priced_decided_by_a_bound": round(share_of_priced, 4),
        #: A CROSS-CHECK BETWEEN TWO FIELDS THAT MUST AGREE and are computed independently:
        #: `ceiling_bound` is the shadow-score answer (what would it have chosen with the cap
        #: lifted), `endpoint_side` is where the winner sat in the allowed set. A ceiling-bound
        #: decision that did NOT sit at the ceiling means the search and the shadow score have
        #: come apart, and that is a defect in `decide_margin` rather than a caveat here.
        "ceiling_bound_and_sat_at_that_end": sum(
            1 for e in ceiling if e.get("endpoint_side") == "ceiling"),
        "median_margin_gbp_per_mwh": {
            "decided_by_the_lawful_ceiling": _median(ceiling),
            "decided_by_the_model_support_bound": _median(support),
            "chosen_freely": _median(freely_chosen),
            "control": TARGET_MARGIN_GBP_PER_MWH,
            "what_the_gap_says": (
                "if the ceiling-decided median sits well above the freely-chosen one, the arm "
                "wanted more than the law allows on exactly the customers it was stopped on, "
                "and the cap -- not the churn belief -- is what held the price down."
            ),
        },
        "realised_margin_movement": {
            "margin_basis": basis,
            "billing_accounts_with_a_bound_decided_renewal": len(bound_accounts),
            "net_delta_gbp_on_those_accounts": net_on_bound,
            "net_delta_gbp_elsewhere": net_elsewhere,
            "absolute_movement_gbp_on_those_accounts": abs_on_bound,
            "absolute_movement_gbp_elsewhere": abs_elsewhere,
            "share_of_absolute_movement_on_those_accounts": (
                round(share_of_movement, 4) if share_of_movement is not None else None),
        },
        "what_would_change_this": (
            "NOT moving the ceiling. A price pinned to the Ofgem cap becomes an inference the "
            "moment the company's own belief turns the expected value over BELOW that cap -- "
            "i.e. when the churn model punishes a supplier-specific rise hard enough that the "
            "optimum is interior for a reason about the customer. Any change to that "
            "sensitivity is a fidelity change: it must cite a published source and be decided "
            "blind to what it does to this delta (R13, R12). If no defensible curve makes the "
            "optimum interior, that is the answer and it belongs here rather than in a moved "
            "bound."
        ),
        "reading": (
            "`decided_by` is a description of THIS run and never a target (R12). \"the "
            "customer\" means no priced answer was bound-decided; \"a bound\" means a bound "
            "decided at least half of the answers or at least half of the money; \"mixed\" is "
            "everything between, and it means the headline must not be attributed to either "
            "without naming which half. A positive delta under \"a bound\" is not a refutation "
            "of value-based pricing -- it is a statement that this run did not test it."
        ),
    }


def _arms_path_label() -> str:
    """The artefact's path as a reader would cite it, without assuming where it lives.

    `Path.relative_to` RAISES on a path outside the repo, and the whole point of a section that
    reports its own source is that the source can be redirected -- by a test, or by a caller
    pointing at a prior snapshot. A message-formatting call that can raise turns an unavailable
    check into a crash, which is a worse answer than either.
    """
    try:
        return str(ARMS_ARTEFACT.relative_to(PROJECT_DIR))
    except ValueError:
        return str(ARMS_ARTEFACT)


def cross_section_reconciliation(shape: dict) -> dict:
    """Why this run's endpoint counts and the coupler's disagree, with both populations named.

    THE READING THAT PROMPTED THIS, on 2026-08-26: the cross-section artefact reported interior
    optima on 255 of 263 accounts while this one reported 20 of 42 priced renewals at the
    ceiling, and the two were taken as contradicting each other. They do not. They are two
    questions put to one module (`company.pricing.value_based_renewal.decide_margin`) over
    different populations under different bounds, and BOTH answers are correct.

    READ, never recomputed -- the same rule `control_credibility` follows and for the same
    reason: two independent computations of one quantity that drift apart is the
    `CLASS_MEASUREMENTS_THAT_MIRROR` shape this project has filed against itself. The coupler
    owns its own population block; this reads it. If that block is absent the artefact is stale,
    and this section says so rather than reconciling against numbers whose meaning it is
    guessing at.
    """
    if not ARMS_ARTEFACT.is_file():
        return {
            "available": False,
            "why_not": (
                "{} has not been generated; run `python3 -m tools.couple_value_based_pricing`. "
                "Until then this run's endpoint counts have nothing to be reconciled against."
            ).format(_arms_path_label()),
        }
    try:
        arms = json.loads(ARMS_ARTEFACT.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {"available": False, "why_not": f"{ARMS_ARTEFACT.name} unreadable: {exc}"}
    population = arms.get("population")
    if not isinstance(population, dict):
        return {
            "available": False,
            "why_not": (
                "{} predates the `population` block, so it does not say which ceiling its "
                "`endpoint_at_ceiling` counts or how many decisions it took per account. "
                "Re-run `python3 -m tools.couple_value_based_pricing`. Reconciling against it "
                "without that block would mean assuming the very thing the two artefacts were "
                "read as disagreeing about."
            ).format(_arms_path_label()),
        }

    return {
        "available": True,
        "read_from": str(_arms_path_label()),
        "why_this_is_here": (
            "Both artefacts publish `endpoint_at_ceiling` and `ceiling_bound` from the same "
            "module, and on 2026-08-26 the two counts were read as contradicting each other. "
            "They are measured over different populations under different ceilings. Neither is "
            "wrong; the names are."
        ),
        "cross_section": {
            "unit": population.get("unit"),
            "as_of_year": population.get("as_of_year"),
            "decisions": population.get("decisions"),
            "distinct_accounts": population.get("distinct_accounts"),
            "lawful_ceiling_passed": population.get("lawful_ceiling_passed"),
            "priced_under_a_lawful_ceiling": population.get("priced_under_a_lawful_ceiling"),
            "endpoint_bound": arms.get("endpoint_bound"),
            "endpoint_at_ceiling": arms.get("endpoint_at_ceiling"),
            "endpoint_at_floor": arms.get("endpoint_at_floor"),
            "extrapolation_bound": arms.get("extrapolation_bound"),
            "what_endpoint_at_ceiling_means": population.get("what_endpoint_at_ceiling_means"),
        },
        "this_run": {
            "unit": "one renewal decision per RENEWAL EVENT the run actually reached",
            "decisions": shape.get("priced"),
            "declined": shape.get("declined"),
            "lawful_ceiling_passed": True,
            "endpoint_bound": shape.get("endpoint_bound"),
            "endpoint_at_ceiling": shape.get("endpoint_at_ceiling"),
            "endpoint_at_floor": shape.get("endpoint_at_floor"),
            "extrapolation_bound": shape.get("extrapolation_bound"),
            "what_endpoint_at_ceiling_means": (
                "the highest margin the Ofgem domestic cap allowed at that term's own cap "
                "window, threaded into the search by `renewal_rate_chain` (8b450a839) rather "
                "than clamped on afterwards."
            ),
        },
        "the_three_differences": [
            {
                "difference": "population",
                "measured": (
                    "{} decision(s) over {} account(s) priced once at {}, against {} renewal "
                    "event(s) this run actually reached across its whole window -- repeat "
                    "visits to a smaller roster, at each term's own rate."
                ).format(population.get("decisions"), population.get("distinct_accounts"),
                         population.get("as_of_year"), shape.get("priced")),
            },
            {
                "difference": "ceiling",
                "measured": (
                    "the cross-section priced {} of {} decision(s) under a lawful ceiling; this "
                    "run priced every one under the domestic cap for its own term. Where no "
                    "ceiling is passed `ceiling_bound` cannot fire at all, so a low ceiling "
                    "count there is not evidence that the cap does not bind."
                ).format(population.get("priced_under_a_lawful_ceiling"),
                         population.get("decisions")),
            },
            {
                "difference": "conditions",
                "measured": (
                    "the cross-section prices every account at one year's rates and one cap "
                    "window; this run prices each renewal at the rate and cap in force when it "
                    "fell, including the 2021-23 crisis window where the base rate is nearest "
                    "the cap and the ceiling therefore binds hardest."
                ),
            },
        ],
        "what_this_does_NOT_reconcile": (
            "Interior on the cross-section and ceiling-bound here are consistent AND both "
            "unflattering: they say the belief's optimum is interior to the model's own support "
            "but lies ABOVE what the company may lawfully charge. The customer-level question "
            "-- does the churn model punish a supplier-specific rise before the law does -- is "
            "open either way. See `bound_attribution.what_would_change_this`."
        ),
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
            ).format(_arms_path_label()),
        }
    try:
        block = json.loads(ARMS_ARTEFACT.read_text(encoding="utf-8"))["average_player"]
    except (OSError, ValueError, KeyError) as exc:
        return {"available": False, "why_not": f"{ARMS_ARTEFACT.name} unreadable: {exc}"}
    if not block.get("available"):
        return {"available": False, "why_not": "the coupler could not score the average player"}
    return {
        "available": True,
        "read_from": str(_arms_path_label()),
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


def level_vs_selection(control_m: dict, value_m: dict, level_m: dict | None,
                       level_gbp_per_mwh: float | None) -> dict:
    """Split the value arm's advantage into the LEVEL it priced at and the SELECTION it made.

    THE QUESTION THIS ANSWERS. The value arm beat flat rules while `discrimination_auc` sat at
    0.4653 -- below a coin flip. An advantage that cannot be attributed to inference has to be
    attributed to something, and what the arm demonstrably did was price HIGH. `flat_at_level`
    applies ONE uplift to EXACTLY the renewals the value arm priced, through the same guards and
    under the same lawful ceiling, so the two arms differ by the CHOOSING and by nothing else.
    The residual `value - level` is what the choosing was worth.

    THE LEVEL IS THE VALUE ARM'S OWN REALISED MEDIAN, READ OFF THE SAME RUN -- never a constant.
    A hardcoded 44.50 would silently answer a question about the book that produced it: the whole
    point of re-running this after the world widens is that the arm's median is free to move, and
    a level pinned to the old book would measure the pin. `level_source` records which run the
    number came from so a reader can check that rather than trust it.

    ONLY REALISED NET IS SCORED HERE, and the enterprise-value reading is deliberately ABSENT
    rather than published beside it as "a second clock" (R14 does not apply -- this is not two
    honest bases disagreeing). `build_enterprise_value` projects CLV from `churn_risk`, the
    company's own belief, and the value arm chooses its margin by maximising expected value under
    `enriched_churn_estimate`. The arm optimises under a model and EV then re-scores the resulting
    book under the same model: R15's TAUTOLOGY pattern, the checked value derived from the source
    it checks. With the scoring belief anti-informative at AUC 0.4653 the value arm is guaranteed
    to look better on EV whether or not its choices were good. Realised net is the only measure in
    this artefact not derived from the company's own beliefs, so it is the verdict.
    """
    if level_m is None:
        return {"available": False,
                "why_not": ("the level arm was not run -- pass --level-arm. Without it the "
                            "artefact cannot say whether the advantage was the level or the "
                            "selection, and must not be read as if it could.")}

    control_net = control_m["total_net_gbp"]
    value_advantage = value_m["total_net_gbp"] - control_net
    level_advantage = level_m["total_net_gbp"] - control_net
    selection_gbp = value_advantage - level_advantage

    # UNDEFINED RATHER THAN INFINITE, and it says which. A share is a fraction OF the value arm's
    # advantage, so an advantage at or near zero has no share -- reporting one would be a divide
    # by a rounding error dressed as a percentage (R15 fail-open: a number that appears whatever
    # the inputs were). The selection figure below stays readable in that case and is reported.
    share = None
    if abs(value_advantage) > 1.0:
        share = level_advantage / value_advantage

    return {
        "available": True,
        "level_gbp_per_mwh": level_gbp_per_mwh,
        "level_source": (
            "the value arm's own realised median margin in THIS run "
            "(`decision_shape.median_margin_gbp_per_mwh`), not a constant"),
        "control_net_gbp": control_net,
        "value_arm_net_gbp": value_m["total_net_gbp"],
        "level_arm_net_gbp": level_m["total_net_gbp"],
        "value_advantage_gbp": value_advantage,
        "level_advantage_gbp": level_advantage,
        # The residual. NEGATIVE means the choosing was worth less than nothing -- an arm that
        # ranks worse than chance cannot select profitably, and that is a RESULT, not a defect
        # to tune away (R12).
        "selection_gbp": selection_gbp,
        "level_share_of_advantage": share,
        "share_undefined_reason": (
            None if share is not None else
            "the value arm's advantage is under GBP 1 -- a share of it would be noise"),
        "clock": "settled-realised",
        "basis": (
            "settled net margin (R14) on the SETTLED-REALISED clock -- `net_margin_gbp` summed "
            "from the world's own settled records after the arrears engine has replaced the "
            "flat-rate provision with realised write-offs and DCA recoveries."
        ),
        # WHY THIS CLOCK AND NOT THE PROVISIONED ONE, stated because the choice moves the answer
        # and must not be made by which one flatters the arm (R12). Three reasons, none of them
        # the size of the result:
        #   1. THE PROVISIONED FIGURE IS A COMPANY BELIEF. Its bad-debt line is
        #      `get_bad_debt_rate()` x billed amount -- a calibrated assumption. This artefact's
        #      own contract is that no figure in it is anything the company believed, so a
        #      provision cannot be the basis a verdict is read off.
        #   2. IT IS THE FIGURE THE COMPANY PUBLISHES. `run_output_latest.json:total_net_gbp`,
        #      the site's headline and every auto-process commit message, is this sum. Scoring
        #      the arms on a basis the business does not report would make the experiment
        #      unreconcilable with the accounts it is supposed to be about.
        #   3. IT IS THE LESS FLATTERING ONE, AND THAT IS RECORDED RATHER THAN QUIETLY BANKED.
        #      On the 2026-08-27 three-arm run the value arm's advantage is GBP 7,366.22 on the
        #      provisioned basis and GBP 4,668.41 on this one -- 37% smaller. Bad debt's own
        #      contribution changes SIGN with the basis: provisioned, the value arm avoids
        #      GBP 2,481.39 of it; realised, it incurs GBP 216.42 MORE. The realised sign is the
        #      one that stands, because the provisioned "saving" is only the flat rate tracking
        #      a smaller billed volume, not a single customer paying who otherwise would not.
        "why_this_clock": (
            "The provisioned clock's bad-debt line is a calibrated company assumption, and this "
            "artefact scores nothing the company believed; the realised clock is also the one "
            "the site publishes. It is the LESS flattering choice -- the value arm's advantage "
            "falls from GBP 7,366.22 to GBP 4,668.41 and bad debt turns from a GBP 2,481.39 "
            "saving into a GBP 216.42 cost -- and it is taken for the two reasons above and not "
            "for its size (R12)."
        ),
        "how_to_read_this": (
            "A share at or above 1.0 means the LEVEL explains all of the advantage and the "
            "SELECTION is worth nothing or less. This is the natural measure of whether widening "
            "the world gave the company something to infer: with a world whose households differ "
            "only by circumstance there is almost nothing for per-customer selection to select "
            "ON, and the level should carry it. A selection still worth less than nothing is a "
            "complete answer and NOT a cue to tune the arm until it wins (R12). The "
            "enterprise-value reading is withheld on purpose -- see this function's docstring."
        ),
    }


#: The figures `clock_audit` treats as a net-margin reading of an arm, and where it finds them.
#: Each entry is (block key, {figure key: arm name}, key holding that block's clock). The arm
#: blocks are not listed here because they carry a per-figure `clocks` map of their own; these
#: are the blocks that publish ONE clock for several figures.
SHARED_CLOCK_NET_FIGURES = (
    ("gross_to_net_bridge",
     {("control_arm", "net_margin_gbp"): "control_arm",
      ("value_arm", "net_margin_gbp"): "value_arm"},
     "clock"),
)
#: The same, for blocks whose net figures sit flat rather than one level down per arm.
FLAT_CLOCK_NET_FIGURES = (
    ("level_vs_selection",
     {"control_net_gbp": "control_arm",
      "value_arm_net_gbp": "value_arm",
      "level_arm_net_gbp": "level_arm"},
     "clock"),
)


def clock_audit(artefact: dict) -> dict:
    """R15 CONTROL: refuse an artefact that publishes two net margins for one arm unlabelled.

    THE DEFECT IT EXISTS FOR, and it is this file's own (2026-08-28). The artefact published
    `control_arm.total_net_gbp` = GBP 113,282.62 and
    `gross_to_net_bridge.control_arm.net_margin_gbp` = GBP 153,244.79 for the SAME arm on the
    SAME run, GBP 39,962.17 apart, with `level_vs_selection.basis` asserting that the arms were
    scored on `net_margin_gbp` from the settled records -- which described the second figure
    while the verdict summed the first. Nothing anywhere fired. A reader who saw GBP 153,245 on
    the site and GBP 113,283 in the experiment had no way to know both described one run.

    WHAT IT ACTUALLY CHECKS, and it is deliberately not "are the numbers equal": two figures MAY
    disagree, if and only if they are declared to be on different clocks. So the control is
    (a) every net figure carries a clock, (b) every clock used is one the artefact defines, and
    (c) any two figures for one arm sharing a clock agree to the penny. Mislabelling
    `provisioned_net_gbp` as `settled-realised` -- the cheapest way to make this go quiet --
    puts two disagreeing figures on one clock and fails (c). Deleting the label fails (a).
    Inventing a clock name fails (b).

    IT READS THE ARTEFACT AND NOTHING ELSE. It does not import `ARM_FIGURE_CLOCKS` or
    `CLOCK_DEFINITIONS` to decide what a figure's clock is, because a check that consults the
    same constant the publisher wrote from is R15's TAUTOLOGY pattern and would pass a run whose
    labels were wrong in exactly the way the module was wrong.

    IT FAILS CLOSED. No `clock_definitions`, no arms, or an arm carrying fewer than two net
    figures all mean the audit had nothing to compare, and an audit with nothing to compare
    reports FAIL, not PASS -- R15's FAIL-OPEN pattern is the one a control like this dies of.
    """
    failures: list[str] = []
    definitions = artefact.get("clock_definitions")
    if not isinstance(definitions, dict) or not definitions:
        failures.append(
            "the artefact declares no `clock_definitions`, so no figure's clock can be "
            "resolved and every label below would be an unchecked string")
        definitions = {}

    # (arm, clock) -> list of (where, value)
    seen: dict[tuple[str, str], list[tuple[str, float]]] = {}
    checked = 0

    def record(arm: str, clock, where: str, value) -> None:
        nonlocal checked
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            failures.append(f"{where} is not a number ({value!r}), so it cannot be reconciled")
            return
        checked += 1
        if not clock:
            failures.append(
                f"{where} publishes a net margin for {arm} with NO declared clock -- the exact "
                "shape this control exists to refuse")
            return
        if clock not in definitions:
            failures.append(
                f"{where} declares clock {clock!r}, which the artefact does not define")
            return
        seen.setdefault((arm, clock), []).append((where, float(value)))

    for arm_key in ("control_arm", "value_arm", "level_arm"):
        block = artefact.get(arm_key)
        if not isinstance(block, dict):
            continue
        clocks = block.get("clocks")
        clocks = clocks if isinstance(clocks, dict) else {}
        for figure_key, value in block.items():
            if not figure_key.endswith("net_gbp"):
                continue
            record(arm_key, clocks.get(figure_key), f"{arm_key}.{figure_key}", value)

    for block_key, figure_map, clock_key in SHARED_CLOCK_NET_FIGURES:
        block = artefact.get(block_key)
        if not isinstance(block, dict):
            continue
        clock = block.get(clock_key)
        for (sub_key, figure_key), arm in figure_map.items():
            sub = block.get(sub_key)
            if isinstance(sub, dict) and figure_key in sub:
                record(arm, clock, f"{block_key}.{sub_key}.{figure_key}", sub[figure_key])

    for block_key, figure_map, clock_key in FLAT_CLOCK_NET_FIGURES:
        block = artefact.get(block_key)
        if not isinstance(block, dict):
            continue
        clock = block.get(clock_key)
        for figure_key, arm in figure_map.items():
            if figure_key in block:
                record(arm, clock, f"{block_key}.{figure_key}", block[figure_key])

    for (arm, clock), entries in sorted(seen.items()):
        values = {round(v, 2) for _where, v in entries}
        if len(values) > 1:
            failures.append(
                "{} publishes {} different net margins on ONE clock ({}): {} -- figures on the "
                "same clock must agree, or one of the labels is false".format(
                    arm, len(values), clock,
                    "; ".join(f"{w} = {v:,.2f}" for w, v in entries)))

    arms_seen = sorted({arm for arm, _clock in seen})
    # ANTI-FAIL-OPEN. An audit that found one figure for an arm compared nothing, and an audit
    # that found no arms at all is not a passing audit -- it is an audit that did not run.
    if not arms_seen:
        failures.append(
            "the audit found no net-margin figure it could place on a defined clock, so it "
            "compared nothing. An audit with nothing to compare is a FAILED audit, not a "
            "passing one")
    for arm in arms_seen:
        count = sum(len(e) for (a, _c), e in seen.items() if a == arm)
        if count < 2:
            failures.append(
                f"{arm} publishes only {count} clocked net-margin figure, so the reconciliation "
                "this control performs did not happen for it")

    return {
        "what_this_refuses": (
            "two net margins published for one arm without a declared clock on each, and two "
            "figures sharing a clock that do not agree. See `clock_audit`'s docstring for the "
            "defect it was built from."
        ),
        "figures_checked": checked,
        "arms_checked": arms_seen,
        "clocks_in_use": sorted({clock for _arm, clock in seen}),
        "passes": not failures,
        "failures": failures,
    }


def run_value_cycle_ab(report_end: str | None = None, level_arm: bool = False) -> dict:
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
    shape = arm_decision_shape(value)

    # THE THIRD ARM, at the value arm's OWN realised median, read off the run just completed.
    # Third and not first because the level is not knowable until the value arm has chosen: this
    # is a comparison against what the arm actually did on THIS book, not against a remembered
    # number from a previous one.
    level = None
    level_m = None
    level_result = None
    level_shape = None
    if level_arm:
        level = shape.get("median_margin_gbp_per_mwh")
        if level is None:
            raise AssertionError(
                "the value arm published no median margin, so there is no level to hold. Running "
                "the third arm at an assumed level would compare the value arm against a number "
                "this run did not produce. Refusing.")
        level_policy = replace(
            CURRENT_POLICY, name="level_arm", renewal_margin_arm=FLAT_AT_LEVEL,
            renewal_margin_flat_level_gbp_per_mwh=float(level))
        with policy_scope(level_policy):
            level_result = run_phase4c(report_end=report_end, policy=level_policy)
        level_m = realised_metrics(level_result)
        # THE POPULATIONS MUST BE THE SAME ONES, and this checks rather than assumes it. The arm
        # exists to price EXACTLY the renewals the value arm priced -- if it priced a different
        # number of them, the residual carries the book as well as the choosing and the split is
        # not readable. It is reported, not raised on: different prices cause different churn, so
        # a small divergence is inherent to any arm comparison in a world where price affects
        # retention (see the finding's own caveat) and suppressing the result would hide it.
        level_shape = arm_decision_shape(level_result)

    # ONE FUNNEL PER ARM THAT ACTUALLY RAN, computed once and used twice below -- as the per-arm
    # block and as the input to the cross-arm denominator comparison. An arm that did not run is
    # ABSENT rather than zero-filled, for the reason `level_arm` above is: a denominator of 0
    # published by a run that never executed the arm is R15's fail-open shape.
    funnels = {
        arm: renewal_funnel(res, arm)
        for arm, res in (
            ("control_arm", control), ("value_arm", value), ("level_arm", level_result))
        if res is not None
    }

    household = household_sides(
        control_arm=control, value_arm=value, level_arm=level_result)

    artefact = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "report_end": report_end,
        # EVERY CLOCK USED IN THIS FILE, defined once and above every figure. `clock_audit`
        # resolves each figure's label against this and refuses a label that is not in it.
        "clock_definitions": dict(CLOCK_DEFINITIONS),
        "what_this_is": (
            "The same book and the same world, run once per pricing arm, scored on what "
            "ACTUALLY happened. No figure here is anything the company believed."
        ),
        # WHICH BOOK. First, because two prior readings of this artefact were correct about a
        # book the company no longer had and neither could say so in its own words.
        "book_identity": {
            "control_arm": book_identity(control),
            "value_arm": book_identity(value),
        },
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
        # Present only when --level-arm ran. Absent rather than zero-filled: a level arm reported
        # as GBP 0 by a run that never executed it is R15's fail-open shape, and this block is
        # the subject of the level-vs-selection verdict below.
        "level_arm": level_m,
        "level_arm_decision_shape": level_shape,
        # WAS THE ADVANTAGE THE LEVEL OR THE SELECTION? The standing measure of whether widening
        # the world gave the company anything to infer -- see `level_vs_selection`.
        "level_vs_selection": level_vs_selection(control_m, value_m, level_m, level),
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
        # WHY the net delta is what it is, line by line. Without this the headline is a result
        # with no mechanism, which is the shape that let a GBP 3.08M figure stand for two days.
        "gross_to_net_bridge": gross_to_net_bridge(control, value),
        "churn_volume_attribution": churn_volume_attribution(control, value),
        "decision_shape": shape,
        # THE DENOMINATOR OF `decision_shape`, and it belongs immediately beside it. Every stage
        # between "the world offered a renewal" and "the arm priced it", per arm, with the drop
        # named -- see `renewal_funnel`. Published for the CONTROL too: the control's funnel is
        # the world's own renewal count, which is the only way to read how much of the book this
        # writer can touch at all.
        "renewal_funnel": funnels,
        # The arms' differing denominators, side by side with the mechanism -- `arm_identity`
        # guards the policy fields and this guards the decision population.
        "decision_population": decision_population(funnels),
        # WHO CHOSE the prices -- the customer or a bound -- as one sentence, above the
        # calibration work, because how well a belief was calibrated is a secondary question
        # on a decision the belief did not make. See `bound_attribution`.
        "bound_attribution": bound_attribution(control, value),
        # Why this run's endpoint counts and the cross-section coupler's disagree, with both
        # populations named. Read from the coupler's artefact, never recomputed.
        "cross_section_reconciliation": cross_section_reconciliation(shape),
        # Was the advantage INFERENCE, or a profitable miscalibration? The two produce the
        # same P&L and completely different conclusions -- see `belief_vs_outcome`.
        "belief_vs_outcome": belief_vs_outcome(value),
        # Does the METHOD have skill -- does the arm's own price rank JOINT value created?
        # The mission's noun, instrumented (atom `A48`). Published directly after
        # `belief_vs_outcome` because the pair is the reading: a high churn AUC beside a flat
        # curve here is a maximiser working correctly on a one-sided objective.
        "method_skill": method_skill(value),
        # WHAT THE HOUSEHOLDS ON EACH ARM'S BOOK KEPT, in pounds, against the published default
        # tariff -- the other side of every net margin above. See `household` where it is built.
        # It is a DIAGNOSTIC (R12) and nothing in the company reads it: the guard is
        # `tests/company/test_household_share_is_not_yet_a_target.py`, which names what releases
        # it (a director decision on the two-sided objective).
        "household_side": household,
        # Names the accounts behind `realised_delta.churned_accounts`. Published
        # beside the delta, never instead of it -- see `churn_roster_diff`.
        "churn_roster_diff": churn_roster_diff(control, value),
        # WHERE the delta comes from, account by account, with its concentration.
        # The roster names who left; this names who MOVED, which is not the same set.
        "margin_movers": margin_movers(control, value),
        "control_credibility": control_credibility(),
        "how_to_read_this": (
            "A positive net-margin delta does NOT establish the thesis on its own. READ "
            "`bound_attribution.headline` FIRST -- it says in one sentence whether the "
            "customer or a bound chose these prices, and an advantage that came from a bound "
            "is no more the company's inference than one that came from access. Then check "
            "three things, all carried above: how many of the arm's answers an endpoint or the "
            "support bound decided rather than the customer (`decision_shape`), how weak the "
            "control is against the regulated allowance (`control_credibility`), and how many "
            "renewals the arm actually priced (`renewals_priced_by_the_arm`) -- a small delta "
            "from an arm that priced almost nothing says nothing about pricing on value. "
            "`renewal_funnel` says WHY that number is what it is, stage by stage, and "
            "`decision_population` says why the arms' denominators differ -- read both before "
            "taking any per-decision figure from this file, and never take one from two arms at "
            "once. A "
            "NEGATIVE delta is a result and not a defect: the arm maximises the company's own "
            "beliefs, so it loses exactly to the degree those beliefs are wrong, and finding "
            "that out is what this experiment is for."
        ),
    }
    # LAST, because it audits the assembled artefact rather than the parts. Published INTO the
    # file so a reader holds the verdict beside the figures it is about; `main` exits non-zero
    # on a failure, so a mislabelled run is loud at the terminal as well as in the JSON.
    artefact["clock_audit"] = clock_audit(artefact)
    return artefact


# ---------------------------------------------------------------------------
# THE NOISE FLOOR -- what does the level/selection split do when ONLY the draw moves?
# ---------------------------------------------------------------------------
#
# WHY THIS IS A COMMITTED MODE AND NOT A SCRATCHPAD. The split above reports `selection_gbp` as a
# difference between two arms over ~30 renewals, and every reading of it so far has assumed the
# difference means something. It cannot be read at all until somebody has measured what the SAME
# comparison does when nothing changes except WHICH households are drawn elastic. That measurement
# existed only as a /tmp script, so no commit reproduced it and nothing tested it -- and the first
# version of it patched a symbol the decision had stopped calling, which made every seed run the
# identical world and returned the most flattering answer available (a noise floor of zero).

#: The module that DRAWS a household's elasticity, and the module whose churn decision READS it.
#: Named as strings, not imported, because the whole point of `resolve_elasticity_symbol` is to
#: resolve the name through the decision's own import rather than pin a second copy of it here.
ELASTICITY_DRAW_MODULE = "simulation.population_draw"
ELASTICITY_DECISION_MODULE = "simulation.customer_events"


def resolve_elasticity_symbol(decision_module: str = ELASTICITY_DECISION_MODULE,
                              draw_module: str = ELASTICITY_DRAW_MODULE) -> str:
    """The elasticity symbol THE CHURN DECISION IMPORTS -- read off the decision's own source.

    A NOISE FLOOR IS A HARNESS KEYED TO A STRUCTURE THAT CAN MOVE, so it must not carry its own
    copy of the name. On 2026-08-27 the decision moved from `price_sensitivity_for_customer` (a
    segment level) to a continuous per-household elasticity; the harness went on patching the old
    name, reached nothing, and reported a spread of zero across seeds -- a plausible number from a
    measurement of nothing, which is R15's FAIL-SILENT shape and worse than a crash.

    So the name is READ, never written down: this parses `decision_module` and returns the single
    name it imports from `draw_module`. A rename that moves both sides is followed automatically;
    a rename that leaves the decision importing something else, or importing nothing from the draw
    module at all, RAISES here rather than silently measuring a disconnected symbol. More than one
    such import is equally refused -- with two candidates this tool cannot know which one the
    decision's price response consumes, and guessing is how the original defect happened.
    """
    spec = importlib.util.find_spec(decision_module)
    if spec is None or not spec.origin:
        raise AssertionError(
            f"cannot locate `{decision_module}` on disk, so the symbol the churn decision imports "
            "cannot be read. Refusing to guess it -- a noise floor patched onto a guessed name is "
            "a measurement of nothing that reports a spread of zero.")
    tree = ast.parse(Path(spec.origin).read_text(encoding="utf-8"))
    names = sorted({
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module == draw_module
        for alias in node.names
    })
    if len(names) != 1:
        raise AssertionError(
            "`{}` imports {} name(s) from `{}` ({}) -- this tool needs EXACTLY one to know which "
            "symbol the price response actually calls. Re-point it deliberately rather than "
            "letting it patch a symbol nothing reads.".format(
                decision_module, len(names), draw_module, names or "none"))
    return names[0]


def _spread(values: list) -> dict:
    """Mean/sd/range over the seeds, with `n` carried so a reader can weigh it."""
    vals = [v for v in values if v is not None]
    if not vals:
        return {"n": 0, "mean": None, "stdev": None, "min": None, "max": None, "range": None,
                "why_empty": "no seed produced this figure"}
    return {
        "n": len(vals),
        "mean": statistics.mean(vals),
        # Population of ONE has no spread -- reported as None, never as 0.0, because a zero here
        # is exactly the reading the disconnected-patch defect produced (R15 fail-open).
        "stdev": statistics.stdev(vals) if len(vals) > 1 else None,
        "min": min(vals),
        "max": max(vals),
        "range": max(vals) - min(vals),
    }


#: The two halves the floor can be cut into, and the one word each cut is named by in the artefact.
#: `only` re-draws the households the arm actually PRICED and holds every other household at the
#: run's own base seed; `except` is its exact mirror. `all` is the undecomposed floor -- the mode
#: every floor before 2026-08-29 ran in, kept as the default so an unqualified call is unchanged.
REDRAW_MODES = ("all", "only", "except")


def priced_accounts_from(artefact: Path) -> list[str]:
    """The households the value arm priced, read off a three-arm artefact's own funnel.

    READ, NEVER WRITTEN DOWN, for the reason `resolve_elasticity_symbol` is: a hand-copied roster
    would go on naming `C1..C9` after the book stopped containing them, and the leg would then
    hold the whole population fixed while reporting a spread of zero for the priced side -- the
    flattering answer, from a measurement of nothing.

    ONE SET FOR BOTH LEGS, TAKEN FROM ONE REFERENCE RUN. The priced roster moves a little with the
    seed (an account that churns earlier stops being offered a renewal), so resolving it per seed
    would make the two legs cut the population along a line that moves between them -- and then
    their variances would not be a decomposition of anything, because the pieces would neither
    partition nor cover. The reference run's roster is used for every seed and every leg, and it
    is written into the artefact so a reader can see WHICH line was cut along.
    """
    data = json.loads(Path(artefact).read_text(encoding="utf-8"))
    funnel = ((data.get("renewal_funnel") or {}).get("value_arm") or {})
    accounts = [a for a in (funnel.get("accounts_the_arm_priced") or []) if isinstance(a, str)]
    if not accounts:
        raise AssertionError(
            "`{}` carries no `renewal_funnel.value_arm.accounts_the_arm_priced`, so there is no "
            "priced roster to cut the floor along. Refusing to fall back to 'everybody' -- that "
            "would silently make the `only` leg the undecomposed floor and the `except` leg a "
            "spread of zero.".format(artefact))
    return sorted(set(accounts))


def noise_floor(seeds: list[int], report_end: str | None = None,
                runner=None, symbol: str | None = None,
                redraw_accounts: list[str] | None = None,
                redraw_mode: str = "all") -> dict:
    """Re-run the whole three-arm A/B once per seed, moving ONLY the elasticity assignment.

    WHAT IS VARIED, AND ONLY THIS. The resolved elasticity symbol is rebound on the draw module so
    every household's elasticity is drawn at `seed` instead of the run's own base seed. The book,
    the weather, the settlement data and the population draw are untouched, so the spread this
    produces is attributable to the assignment and to nothing else.

    AND, SINCE 2026-08-29, TO WHICH HALF OF THE BOOK. `redraw_mode="only"` re-draws just the
    households in `redraw_accounts` -- the ones the arm actually priced -- and passes every other
    household through at the run's own base seed; `"except"` is the mirror. This exists because the
    undecomposed spread has two sources with OPPOSITE remedies, and the page had already published
    one of them as fact. Either the 20 priced households' own elasticity moves the selection figure
    (that shrinks as ~1/sqrt(n) priced, so a larger settled book resolves it) or the other ~2,000
    households' churn cascade lands in the same net (that does not shrink with the priced count at
    all, so a larger book buys nothing). The two legs are a partition of the same call stream, so
    their variances must roughly SUM to the undecomposed one -- and that reconciliation, not the
    two numbers on their own, is what says the split is real rather than two unrelated runs.

    THE HELD-FIXED HALF IS HELD AT `_base_seed`, THE ARGUMENT THE CALLER PASSED -- not at a seed
    written down here. The call site is `customer_events.roll_lifecycle_event`, which passes
    `run_base_seed()`, so passing it straight back through is exactly "this household was not
    re-drawn". Substituting a constant would silently re-draw the held half onto a third world.

    THE LEVEL ARM IS THE RUNNER'S OWN, at the value arm's realised median FOR THAT SEED. This is
    not a detail: the scratchpad version pinned the level at a remembered 44.5 GBP/MWh, which is a
    constant from a book that no longer exists, so it measured the noise floor of a DIFFERENT
    instrument from the one that publishes. Each seed re-reads the median off its own run.

    THE PATCH MUST BE OBSERVED TO FIRE, per seed. A rebind that reaches no call site produces a
    byte-identical world, a spread of exactly zero, and a headline saying the selection leg is
    perfectly stable -- the most flattering possible answer, arrived at by measuring nothing. The
    counter makes that state RAISE. It is the floor on this tool's own subject and the reason the
    R15 mutation (point `symbol` at the retired `price_sensitivity_for_customer`) goes red.

    `runner` is injectable so the control can exercise this loop without three full decade passes.
    """
    if len(seeds) < 2:
        raise AssertionError(
            f"a noise floor needs at least two seeds; got {len(seeds)}. One seed is a run, not a "
            "spread, and reporting it as a floor would understate the error bars to zero.")
    draw = importlib.import_module(ELASTICITY_DRAW_MODULE)
    name = symbol or resolve_elasticity_symbol()
    real = getattr(draw, name, None)
    if real is None:
        raise AssertionError(
            f"`{ELASTICITY_DRAW_MODULE}` has no attribute `{name}` to re-draw. Refusing to run.")

    if redraw_mode not in REDRAW_MODES:
        raise AssertionError(
            "`redraw_mode` must be one of {}; got {!r}.".format(REDRAW_MODES, redraw_mode))
    if redraw_mode != "all" and not redraw_accounts:
        raise AssertionError(
            "`redraw_mode={}` needs the roster it cuts along. Without one, `only` would re-draw "
            "nobody and `except` would re-draw everybody, and BOTH would be published under a "
            "label saying they had been decomposed.".format(redraw_mode))
    scope = frozenset(redraw_accounts or ())

    def _in_redraw_scope(customer_id: str) -> bool:
        """Is THIS household on the side of the cut that gets a new elasticity?"""
        if redraw_mode == "all":
            return True
        return (customer_id in scope) if redraw_mode == "only" else (customer_id not in scope)

    run = runner or (lambda: run_value_cycle_ab(report_end=report_end, level_arm=True))
    rows = []
    for seed in seeds:
        calls = {"n": 0, "redrawn": 0, "held": 0, "ids": set()}

        def patched(customer_id, _base_seed, curriculum=None, _s=int(seed), _r=real, _c=calls):
            _c["n"] += 1
            if not _in_redraw_scope(customer_id):
                _c["held"] += 1
                return _r(customer_id, _base_seed, curriculum)
            _c["redrawn"] += 1
            _c["ids"].add(customer_id)
            return _r(customer_id, _s, curriculum)

        setattr(draw, name, patched)
        try:
            result = run()
        finally:
            setattr(draw, name, real)
        if calls["n"] == 0:
            raise AssertionError(
                "seed {}: the elasticity patch on `{}.{}` was never called, so this run varied "
                "NOTHING and its 'noise floor' would be an artefact reading zero. The churn "
                "decision no longer reaches that symbol -- re-resolve it before trusting any "
                "number here.".format(seed, ELASTICITY_DRAW_MODULE, name))
        # THE SAME FAIL-SILENT GUARD, ONE CUT DOWN. A leg whose scope matches no call site is the
        # identical defect at the level of the roster rather than the symbol: it runs the base
        # world, returns a spread of zero for its half, and the reconciliation then hands the
        # WHOLE variance to the other half -- which is a conclusion, not a measurement. The most
        # likely cause is an id convention mismatch (the funnel names supply points, the draw is
        # called with `household_of(...)`), and that must be loud.
        if calls["redrawn"] == 0:
            raise AssertionError(
                "seed {}: the `{}` leg re-drew NO household -- its {} roster entries matched none "
                "of the {} elasticity calls this run made, so its 'spread' would be zero by "
                "construction. Check the id convention before trusting any decomposition: the "
                "draw is called with `household_of(customer_id)`.".format(
                    seed, redraw_mode, len(scope), calls["n"]))
        if redraw_mode != "all" and calls["held"] == 0:
            raise AssertionError(
                "seed {}: the `{}` leg held NO household fixed, so it is the undecomposed floor "
                "wearing a decomposed label.".format(seed, redraw_mode))
        lvs = result["level_vs_selection"]
        if not lvs.get("available"):
            raise AssertionError(
                "seed {}: the runner produced no level arm ({}), so there is no selection figure "
                "to take a spread of.".format(seed, lvs.get("why_not")))
        rows.append({
            "seed": int(seed),
            "elasticity_draws": calls["n"],
            # THE CUT, MEASURED PER SEED RATHER THAN ASSERTED ONCE. `redrawn + held == draws` is
            # what makes the two legs a partition of one call stream; a reader can check it on
            # every row, and `accounts_redrawn` says how much of the roster the run actually met.
            "elasticity_redrawn": calls["redrawn"],
            "elasticity_held_fixed": calls["held"],
            "accounts_redrawn": len(calls["ids"]),
            # THE CLOCK EVERY FIGURE ON THIS ROW IS ON, carried per seed and reconciled below.
            # Added 2026-08-29: this artefact published four contrasts and no clock, so the page
            # that bounds its headline with them could only say "this floor declares no clock of
            # its own" -- a caveat that could never empty, on a spread that has been on the
            # realised clock since the split was repaired. Taken from the split's own label rather
            # than written down here, for the reason the whole tool exists: the same block was on
            # `settled-provisioned` before that repair, with no change of key or shape.
            "clock": lvs.get("clock"),
            "level_gbp_per_mwh": lvs.get("level_gbp_per_mwh"),
            "value_advantage_gbp": lvs["value_advantage_gbp"],
            "level_advantage_gbp": lvs["level_advantage_gbp"],
            "selection_gbp": lvs["selection_gbp"],
            "level_share_of_advantage": lvs["level_share_of_advantage"],
        })

    selection = _spread([r["selection_gbp"] for r in rows])
    share = _spread([r["level_share_of_advantage"] for r in rows])
    # DISTINGUISHABLE FROM ZERO? The standard error of the mean over `n` seeds, doubled. Stated as
    # a question the reader can re-answer, not as a pass/fail: nothing here gates anything (R12),
    # and a selection leg that is NOT distinguishable is a complete result rather than a defect.
    sem = None
    distinguishable = None
    if selection["stdev"] is not None and selection["n"] > 1:
        sem = selection["stdev"] / math.sqrt(selection["n"])
        distinguishable = abs(selection["mean"]) > 2 * sem
    # ONE CLOCK, OR NO CLOCK -- never the first seed's. A spread taken across rows on different
    # clocks is not a spread of one quantity, and the GBP 39,962.17 bad-debt gap between this
    # run's two clocks is larger than every contrast the spread bounds, so a mixed floor would
    # publish that gap as seed noise. Seeds that declare nothing yield None and the consumer's
    # own "this floor carries no clock" caveat stands; seeds that DISAGREE are refused outright.
    declared = {row.get("clock") for row in rows}
    if len(declared) > 1:
        raise AssertionError(
            "the seeds report {} different clocks ({}), so their spread is not the spread of one "
            "quantity and no error bar can be taken from it".format(
                len(declared), sorted(str(clock) for clock in declared)))
    clock = declared.pop() if declared else None

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "report_end": report_end,
        "what_this_is": (
            "The three-arm A/B re-run once per seed with ONLY the per-household elasticity "
            "assignment re-drawn. The spread below is the error bar on `selection_gbp` -- the "
            "figure the level-vs-selection split publishes."),
        #: DERIVED FROM THE SPLIT'S OWN LABEL, agreed across every seed. A consumer that bounds a
        #: published figure with this spread has to know which clock it is on, and until
        #: 2026-08-29 there was nothing here to read -- so `site/data/value_arms.json` carried a
        #: standing caveat saying so. Never inferred from which block the rows came out of.
        "clock": clock,
        #: WHICH HALF OF THE BOOK THIS FLOOR MOVED. Carried on every floor, `all` included, so a
        #: consumer never has to infer the mode from the presence of a key -- an absent block would
        #: read as "undecomposed" on an old artefact and as "priced-only" on a new one that failed
        #: to write it, and those are opposite readings of the same silence.
        "redraw_scope": {
            "mode": redraw_mode,
            "accounts": sorted(scope),
            "accounts_in_roster": len(scope),
            "means": {
                "all": ("every household re-drawn -- the undecomposed floor, and the only mode "
                        "whose spread bounds the published figure directly"),
                "only": ("ONLY the households the value arm priced were re-drawn; every other "
                         "household kept the run's own base-seed elasticity. This half SHRINKS as "
                         "~1/sqrt(n) with the number of priced decisions, so it is the half a "
                         "larger settled book buys down"),
                "except": ("every household EXCEPT the ones the arm priced was re-drawn. This "
                           "half is the rest of the book's churn cascade landing in the same net "
                           "and it does NOT shrink with the priced count, so it is the floor a "
                           "larger settled book cannot get under"),
            }[redraw_mode],
        },
        "symbol_patched": f"{ELASTICITY_DRAW_MODULE}.{name}",
        "symbol_resolution": (
            "read from `{}`'s own import statement, not written down here, so a rename "
            "disconnects this tool LOUDLY instead of silently returning a spread of zero"
            .format(ELASTICITY_DECISION_MODULE)),
        "seeds": rows,
        "selection_gbp_spread": selection,
        "level_share_spread": share,
        "selection_sem_gbp": sem,
        "selection_distinguishable_from_zero": distinguishable,
        "how_to_read_this": (
            "If the spread is WIDER than the published `selection_gbp`, the level-vs-selection "
            "instrument cannot yet resolve the question being asked of it, and every reading "
            "built on it carries that caveat. That is a finding about the INSTRUMENT and not "
            "about the pricing arm -- it is not a cue to re-run until a seed agrees (R12)."),
    }


# ---------------------------------------------------------------------------
# WHAT WOULD ACTUALLY RESOLVE IT -- the floor cut in two, and the price of each remedy
# ---------------------------------------------------------------------------
#
# `site/data/value_arms.json` publishes a REMEDY beside its refusal: *"What would resolve it is a
# larger SETTLED BOOK -- more renewals actually priced by the arm -- and not more seeds."* The
# second half is arithmetic and safe: re-drawing the dice estimates this spread again, it does not
# shrink it. The FIRST half is a claim about where the spread comes from, and it was published
# before anybody had looked. The undecomposed floor re-draws elasticity for ~2,050 households and
# the arm priced 20 renewals, so the spread has two possible sources with OPPOSITE remedies, and
# the evidence separating them was inside the artefact the same commit tracked.
#
# THE THRESHOLD IS NOT A JUDGEMENT CALL, WHICH IS WHY THIS IS ARITHMETIC AND NOT AN OPINION. Only
# the priced side shrinks with the priced count; the rest of the book's churn cascade is there at
# any book size. So the irreducible floor is the `except` leg's own spread, and a larger book can
# only resolve the contrast if that leg ALONE is smaller than the contrast. Below that share, no
# book this or any world could produce resolves it, and the remedy sentence is false.

#: The rule the page itself applies -- a contrast is resolved when it EXCEEDS the spread of the
#: same contrast (`generate_value_arms_data._resolvable`). Re-stated here rather than imported,
#: because this module may not import the site feed (the dependency runs the other way), and
#: `test_the_decomposition_uses_the_pages_own_resolution_rule` pins the two together.
def _resolves(contrast: float, stdev: float) -> bool:
    return abs(contrast) > stdev


def _num(value):
    """A finite float, or None. `None` is never coerced to zero -- a missing leg is not a leg
    with no spread, and the two readings would license opposite remedies."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value) if math.isfinite(value) else None


#: What a DRAWN household's id starts with (`population_draw` mints `SYN-{year}-{i:03d}`). Used
#: only to tell a drawn account from the hand-authored static roster, which is the difference
#: between "grow the book" being a lever and being a way of making the floor worse.
DRAWN_ACCOUNT_PREFIX = "SYN-"

#: The candidate priced-side shares the price table is printed at. A LADDER RATHER THAN A POINT,
#: because at three seeds the measured share is imprecise enough that a reader needs to see how
#: sharply the answer turns on it -- and because the table was printed at these inputs BEFORE the
#: legs that measure the share had finished, which is the only order in which a prediction is one.
_PRICE_TABLE_SHARES = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99)


def remedy_price_table(total_variance: float, contrast: float, priced: int,
                       priced_share_of_renewals: float | None,
                       shares=_PRICE_TABLE_SHARES) -> list[dict]:
    """What a larger settled book would COST, at each candidate split of the floor.

    sd(n)^2 = (1-share)*V + share*V*(priced/n). The first term is the rest of the book's cascade
    and is constant in n; the second is the priced households' own draw and falls as 1/n. Solving
    sd(n) = |contrast| gives the priced decisions needed, and the row is UNREACHABLE where the
    constant term alone already exceeds the contrast -- which is not an edge case but the answer
    over most of this table's range.

    `renewals_the_world_must_offer` scales by the funnel's OWN priced share and is the loosest
    figure here: it assumes the funnel's composition holds as the book grows, and
    `where_the_priced_decisions_come_from` is why that assumption needs reading before the column
    is used. It is published anyway, because a remedy priced only in decisions is one a reader
    cannot convert into a decision about this world.
    """
    rows = []
    for share in shares:
        irreducible = (1.0 - share) * total_variance
        headroom = contrast * contrast - irreducible
        row = {
            "priced_share_of_variance": share,
            "irreducible_sd_gbp": math.sqrt(irreducible),
            "priced_decisions_needed": None,
            "times_this_book": None,
            "renewals_the_world_must_offer": None,
        }
        if headroom > 0:
            needed = math.ceil(priced * share * total_variance / headroom)
            row["priced_decisions_needed"] = needed
            row["times_this_book"] = needed / priced if priced else None
            if priced_share_of_renewals:
                row["renewals_the_world_must_offer"] = math.ceil(needed / priced_share_of_renewals)
        rows.append(row)
    return rows


def where_the_priced_decisions_come_from(three_arm: dict) -> dict:
    """WHICH accounts the arm priced, and therefore what "a larger settled book" would have to mean.

    THE COLUMN THIS EXISTS TO STOP BEING MISREAD. "More renewals actually priced by the arm" reads
    as a book-SIZE lever, and the funnel says it may not be one. If every priced decision belongs
    to the hand-authored static roster and none to a drawn household, then growing the drawn book
    adds renewals to `product_not_upliftable` and households to the churn cascade -- it enlarges
    the half of the floor that does not shrink while adding nothing to the half that does, which
    makes the comparison WORSE and not better. Derived from the roster's own ids, never asserted.
    """
    funnel = ((three_arm.get("renewal_funnel") or {}).get("value_arm") or {})
    priced_accounts = [a for a in (funnel.get("accounts_the_arm_priced") or [])
                       if isinstance(a, str)]
    drawn = [a for a in priced_accounts if a.startswith(DRAWN_ACCOUNT_PREFIX)]
    return {
        "accounts_the_arm_priced": priced_accounts,
        "of_those_drawn": len(drawn),
        "of_those_static_roster": len(priced_accounts) - len(drawn),
        "reading": (
            "Every priced decision on this run belongs to the hand-authored static roster; not one "
            "belongs to a drawn household. So 'a larger settled book' cannot mean a larger DRAWN "
            "book: the drawn households' renewals all stop at `product_not_upliftable` because "
            "the world has no standard-variable product for them to be on, and adding more of "
            "them enlarges the churn cascade -- the half of the floor no book size shrinks -- "
            "while adding no priced decisions at all. The lever is a PRODUCT, not a size."
            if priced_accounts and not drawn else
            "{} of the {} accounts the arm priced are drawn households, so a larger drawn book "
            "does reach this arm.".format(len(drawn), len(priced_accounts))),
    }


def decompose_floor(undecomposed: dict, priced_only: dict, priced_except: dict,
                    three_arm: dict) -> dict:
    """Split the selection floor into the priced households' half and the rest of the book's.

    THE RECONCILIATION IS THE CONTROL, not the two numbers. Two legs run separately could differ
    for any reason -- a different roster, a different window, a runner that drifted between them.
    What says they are a decomposition of ONE quantity is that their variances roughly SUM to the
    undecomposed one, because they partition the same call stream. That ratio is published whether
    it is flattering or not, and a reader who does not like it can stop reading here.

    AND ITS PRECISION IS PUBLISHED WITH IT. Every leg here is three seeds, so each variance carries
    two degrees of freedom and a 90% interval spanning roughly a sixth to nine times the truth.
    That is wide enough that this decomposition can say which half DOMINATES only when the split is
    lopsided, and `share_is_decisive` says whether it was. A borderline split is reported as
    borderline; it is not rounded into a verdict.
    """
    def _variance(floor: dict):
        vals = [_num(row.get("selection_gbp")) for row in (floor.get("seeds") or [])]
        vals = [v for v in vals if v is not None]
        return (statistics.variance(vals) if len(vals) > 1 else None), len(vals)

    def _mode(floor: dict):
        return ((floor or {}).get("redraw_scope") or {}).get("mode")

    # THE TWO HALVES MUST NAME THEMSELVES. `only` and `except` are never inferred from a filename
    # or from an absent key: a leg run in the wrong mode and read as the other one hands the whole
    # variance to the wrong side, which is a conclusion rather than a measurement.
    for expected, floor in (("only", priced_only), ("except", priced_except)):
        if _mode(floor) != expected:
            return {"available": False,
                    "why_not": ("expected a floor with `redraw_scope.mode == {!r}` and got {!r}; "
                                "refusing to decompose legs that do not name their own half"
                                .format(expected, _mode(floor)))}
    # THE UNDECOMPOSED LEG MAY PREDATE THE KEY, AND ONLY THAT LEG. Every floor run before
    # 2026-08-29 re-drew the whole book because no other mode existed, so a missing `redraw_scope`
    # on this slot is provably `all` rather than ambiguous -- and this slot is used for ONE thing,
    # the reconciliation check, never for the split itself. A leg that names a different mode is
    # still refused.
    if _mode(undecomposed) not in (None, "all"):
        return {"available": False,
                "why_not": ("the undecomposed slot carries a floor in `{}` mode, which is one of "
                            "the halves and not the whole".format(_mode(undecomposed)))}
    seed_sets = [tuple(sorted(int(r["seed"]) for r in (f.get("seeds") or [])))
                 for f in (undecomposed, priced_only, priced_except)]
    if len(set(seed_sets)) != 1:
        return {"available": False,
                "why_not": ("the three legs ran on different seeds ({}), so their variances are "
                            "not three readings of one quantity and their difference is not a "
                            "decomposition".format(seed_sets))}

    v_all, n_seeds = _variance(undecomposed)
    v_only, _ = _variance(priced_only)
    v_except, _ = _variance(priced_except)
    if None in (v_all, v_only, v_except) or v_only + v_except <= 0:
        return {"available": False,
                "why_not": "a leg produced no selection spread, so there is nothing to split"}

    split = (three_arm.get("level_vs_selection") or {})
    contrast = _num(split.get("selection_gbp"))
    funnel = ((three_arm.get("renewal_funnel") or {}).get("value_arm") or {})
    priced = funnel.get("priced")
    offered = funnel.get("renewals_the_world_offered")
    if contrast is None or not isinstance(priced, int) or priced <= 0:
        return {"available": False,
                "why_not": ("the three-arm run carries no selection contrast or no priced count, "
                            "so there is no figure to price a remedy against")}

    # THE IRREDUCIBLE FLOOR IS MEASURED, NOT SCALED. It is the `except` leg's own spread and
    # nothing else: the rest of the book's churn cascade landing in the same net, present at any
    # priced count because none of it is priced. Rescaling it onto `v_all`'s total was the first
    # draft here and it is worse -- it borrows a third leg's sampling error into the one figure the
    # verdict turns on, to buy nothing. `v_all` is used for the reconciliation check and for that
    # alone, which is what makes the check a check.
    total = v_only + v_except
    priced_share = v_only / total
    reconciliation = total / v_all
    irreducible_sd = math.sqrt(v_except)
    resolvable_at_any_book = _resolves(contrast, irreducible_sd)

    decisions_needed = None
    if resolvable_at_any_book:
        # sd(n)^2 = V_except + V_only * (priced / n)  ->  solve sd(n) = |contrast|.
        # The priced half shrinks as 1/n because it is a mean over n independent draws; the other
        # half is a constant in n. Both halves are held at the values THIS book measured, so this
        # is a first-order price and not a forecast -- the contrast itself would move too.
        decisions_needed = math.ceil(
            priced * v_only / (contrast * contrast - v_except))

    return {
        "available": True,
        "what_this_is": (
            "The selection-figure noise floor cut into the half that a larger settled book buys "
            "down and the half it cannot touch, from two extra floor legs that partition one "
            "call stream, plus what each remedy would cost."),
        "seeds": n_seeds,
        "contrast_gbp": contrast,
        "priced_decisions": priced,
        "renewals_offered": offered,
        "undecomposed_sd_gbp": math.sqrt(v_all),
        "priced_side_sd_gbp": math.sqrt(v_only),
        "rest_of_book_sd_gbp": math.sqrt(v_except),
        "priced_share_of_variance": priced_share,
        "reconciliation_ratio": reconciliation,
        "reconciliation_reading": (
            "The two legs' variances sum to {:.2f}x the undecomposed one. They partition the same "
            "call stream, so the honest expectation is 1.0; at {} seeds each variance carries "
            "{} degrees of freedom, and a ratio anywhere between roughly 0.3 and 3 is what that "
            "sample size alone produces. A ratio outside that is evidence the legs are not two "
            "halves of one thing.".format(reconciliation, n_seeds, n_seeds - 1)),
        #: THE SHARE ABOVE WHICH THE PAGE'S REMEDY IS TRUE, derived from the page's own rule and
        #: nothing else: the rest-of-book half alone must come in under the contrast.
        "share_at_which_a_bigger_book_could_resolve_it": (
            1.0 - (contrast * contrast) / total if total > 0 else None),
        #: AT THREE SEEDS THIS CAN ONLY CALL A LOPSIDED SPLIT. A share whose own interval straddles
        #: the threshold above is reported as undecided, and the consumer states no remedy at all.
        "share_is_decisive": (
            abs(priced_share - (1.0 - (contrast * contrast) / total)) > 0.15
            if total > 0 else False),
        "irreducible_sd_gbp": irreducible_sd,
        "larger_settled_book_would_resolve_it": resolvable_at_any_book,
        "priced_decisions_needed": decisions_needed,
        #: THE SAME ARITHMETIC ACROSS EVERY CANDIDATE SPLIT, so a reader can see how sharply the
        #: verdict turns on a share measured at three seeds -- and check the one row the legs
        #: landed on against the nine they did not.
        "remedy_price_table": remedy_price_table(
            total, contrast, priced, funnel.get("priced_share_of_renewals_offered")),
        "where_the_priced_decisions_come_from": where_the_priced_decisions_come_from(three_arm),
        "how_to_read_this": (
            "`larger_settled_book_would_resolve_it` is the page's remedy sentence, as arithmetic. "
            "False means the rest of the book's churn cascade alone is wider than the contrast, so "
            "NO book resolves this comparison and the remedy is not a smaller version of the same "
            "thing -- it is a different instrument. That is a finding about the instrument and it "
            "belongs on the surface (R12), not in a footnote."),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--end-year", help="truncate the window, e.g. 2019 (faster iteration)")
    ap.add_argument("--out", type=Path, default=OUTPUT_PATH)
    ap.add_argument(
        "--level-arm", action="store_true",
        help=("also run `flat_at_level` at the value arm's own realised median, splitting the "
              "advantage into the LEVEL and the SELECTION. Costs a third full pass."))
    ap.add_argument(
        "--noise-floor-seeds",
        help=("NOISE FLOOR mode: comma-separated seeds, e.g. 11111,22222,33333. Re-runs the whole "
              "three-arm A/B once per seed with ONLY the per-household elasticity assignment "
              "re-drawn, and reports the spread in `selection_gbp` and `level_share_of_advantage` "
              "-- the error bar on the level-vs-selection split. Costs 3 full passes PER SEED."))
    ap.add_argument(
        "--redraw-mode", choices=REDRAW_MODES, default="all",
        help=("which half of the book the noise floor re-draws. `only` = just the households the "
              "arm priced; `except` = everybody else; `all` (default) = the undecomposed floor. "
              "The two halves partition one call stream, so their variances should sum to the "
              "`all` variance -- run all three and check, or the split is two unrelated runs."))
    ap.add_argument(
        "--decompose", nargs=4, metavar=("ALL_FLOOR", "ONLY_FLOOR", "EXCEPT_FLOOR", "THREE_ARM"),
        type=Path,
        help=("DECOMPOSE mode: read three floors already run (`all`, `only`, `except`) and the "
              "three-arm run they bound, and write the split of the selection floor into the half "
              "a larger settled book buys down and the half it cannot. Runs nothing."))
    ap.add_argument(
        "--redraw-accounts-from", type=Path, default=ARMS_ARTEFACT.parent / "value_cycle_ab.json",
        help=("the three-arm artefact whose `renewal_funnel.value_arm.accounts_the_arm_priced` "
              "names the priced roster the cut is made along. Read, never hand-written."))
    args = ap.parse_args(argv)
    report_end = f"{args.end_year}-12-31" if args.end_year else None

    if args.decompose:
        legs = [json.loads(p.read_text(encoding="utf-8")) for p in args.decompose]
        split = decompose_floor(*legs)
        out = args.out if args.out != OUTPUT_PATH else DECOMPOSITION_OUTPUT_PATH
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(split, indent=2), encoding="utf-8")
        if not split["available"]:
            print("floor decomposition UNAVAILABLE: {}".format(split["why_not"]))
            print("  wrote {}".format(out))
            return 1
        print("value cycle A/B -- SELECTION FLOOR DECOMPOSITION over {} seeds".format(
            split["seeds"]))
        print("  contrast                    {:+,.2f} GBP over {} priced decisions".format(
            split["contrast_gbp"], split["priced_decisions"]))
        print("  undecomposed floor (sd)     {:,.2f} GBP".format(split["undecomposed_sd_gbp"]))
        print("  priced households' half     {:,.2f} GBP".format(split["priced_side_sd_gbp"]))
        print("  rest of the book's half     {:,.2f} GBP".format(split["rest_of_book_sd_gbp"]))
        print("  RECONCILIATION              {:.2f}x (the two halves against the whole; 1.0 is "
              "the honest expectation)".format(split["reconciliation_ratio"]))
        print("  priced share of variance    {:.1%}  (decisive at this n? {})".format(
            split["priced_share_of_variance"], "yes" if split["share_is_decisive"] else "NO"))
        print("  a bigger book resolves it above a priced share of {:.1%}".format(
            split["share_at_which_a_bigger_book_could_resolve_it"]))
        print("  irreducible floor           {:,.2f} GBP -- what no book gets under".format(
            split["irreducible_sd_gbp"]))
        print("  WOULD A LARGER SETTLED BOOK RESOLVE IT?  {}".format(
            "yes -- at {:,} priced decisions ({:.1f}x this book's {})".format(
                split["priced_decisions_needed"],
                split["priced_decisions_needed"] / split["priced_decisions"],
                split["priced_decisions"])
            if split["larger_settled_book_would_resolve_it"] else
            "NO -- the rest of the book's cascade alone is wider than the contrast"))
        print("  wrote {}".format(out))
        return 0

    if args.noise_floor_seeds:
        seeds = [int(s) for s in args.noise_floor_seeds.split(",") if s.strip()]
        accounts = (None if args.redraw_mode == "all"
                    else priced_accounts_from(args.redraw_accounts_from))
        floor = noise_floor(seeds, report_end=report_end,
                            redraw_accounts=accounts, redraw_mode=args.redraw_mode)
        out = args.out if args.out != OUTPUT_PATH else NOISE_FLOOR_OUTPUT_PATH
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(floor, indent=2), encoding="utf-8")
        sel = floor["selection_gbp_spread"]
        shr = floor["level_share_spread"]
        print("value cycle A/B -- NOISE FLOOR over {} seed(s), {} window".format(
            sel["n"], report_end or "full"))
        print("  patched         {}".format(floor["symbol_patched"]))
        print("  redraw mode     {}  ({} account(s) in the roster)".format(
            floor["redraw_scope"]["mode"], floor["redraw_scope"]["accounts_in_roster"]))
        for row in floor["seeds"]:
            print("    seed {:<8} selection {:+,.2f} GBP   level share {}   "
                  "({} draws: {} re-drawn / {} held)".format(
                      row["seed"], row["selection_gbp"],
                      "{:.1%}".format(row["level_share_of_advantage"])
                      if row["level_share_of_advantage"] is not None else "undefined",
                      row["elasticity_draws"], row["elasticity_redrawn"],
                      row["elasticity_held_fixed"]))
        print("  selection_gbp   mean {:+,.2f}  sd {}  range {:,.2f} ({:+,.2f} .. {:+,.2f})".format(
            sel["mean"], "{:,.2f}".format(sel["stdev"]) if sel["stdev"] is not None else "n/a",
            sel["range"], sel["min"], sel["max"]))
        if shr["mean"] is not None:
            print("  level share     mean {:.1%}  range {:.1%} .. {:.1%}".format(
                shr["mean"], shr["min"], shr["max"]))
        print("  DISTINGUISHABLE FROM ZERO?  {}".format(
            {True: "yes", False: "NO -- the selection leg is inside its own noise",
             None: "unknown"}[floor["selection_distinguishable_from_zero"]]))
        print("  wrote {}".format(out))
        return 0

    result = run_value_cycle_ab(report_end=report_end, level_arm=args.level_arm)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")

    d = result["realised_delta"]
    shape = result["decision_shape"]
    book = result["book_identity"]["control_arm"]
    bridge = result["gross_to_net_bridge"]
    print("value cycle A/B -- REALISED, {} window".format(report_end or "full"))
    print("  book            {} accounts, {} dual fuel ({:.1%})".format(
        book["billing_accounts_settled_in_window"], book["dual_fuel"],
        book["dual_fuel_share_of_accounts"] or 0.0))
    print("  net margin      {:+,.0f} GBP".format(d["net_margin_gbp"]))
    print("  enterprise val  {:+,.0f} GBP".format(d["enterprise_value_gbp"]))
    print("  accounts at end {:+d}   churned {:+d}".format(
        d["accounts_at_end"], d["churned_accounts"]))
    print("  gross-to-net    {} (largest term {:+,.0f} GBP), closes={}".format(
        bridge["largest_contribution"],
        bridge["net_delta_contribution_gbp"].get(bridge["largest_contribution"], 0.0),
        bridge["reconstruction_closes"]))
    print("  arm priced {} renewal(s), {} distinct margins, {} endpoint-bound".format(
        shape.get("priced", 0), shape.get("distinct_margins", 0),
        shape.get("endpoint_bound", 0)))
    # THE HEADLINE ON THE TERMINAL TOO, not only in the file. A caller who reads the printed
    # net-margin delta and stops is exactly the reader this section was written for.
    bound = result["bound_attribution"]
    print("  WHO CHOSE   {}".format(
        bound["headline"] if bound.get("available") else bound.get("why_not")))
    lvs = result["level_vs_selection"]
    if lvs.get("available"):
        share = lvs["level_share_of_advantage"]
        print("  LEVEL vs SELECTION  level @{:,.2f} GBP/MWh -> {:+,.2f}; "
              "value -> {:+,.2f}; selection {:+,.2f} GBP; level share {}".format(
                  lvs["level_gbp_per_mwh"], lvs["level_advantage_gbp"],
                  lvs["value_advantage_gbp"], lvs["selection_gbp"],
                  "{:.1%}".format(share) if share is not None else "undefined"))
    print("  wrote {}".format(args.out))
    # THE CONTROL IS LOUD AND IT DECIDES THE EXIT CODE. The file is written first on purpose: a
    # three-arm run costs three full passes, and throwing the evidence away over a label would
    # make the honest response to this control "stop running it".
    audit = result["clock_audit"]
    if not audit["passes"]:
        print("  CLOCK AUDIT  FAILED -- this artefact publishes net margins it cannot reconcile:")
        for failure in audit["failures"]:
            print("    - {}".format(failure))
        return 1
    print("  clock audit     PASS ({} figures, {} arms, clocks {})".format(
        audit["figures_checked"], len(audit["arms_checked"]),
        ", ".join(audit["clocks_in_use"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
