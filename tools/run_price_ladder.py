#!/usr/bin/env python3
"""The price ladder: the world's switching response and the company's belief, on the same rungs.

REUSE: tools/run_price_ladder.py
CLASS: PATTERN-REUSE
INDEX: searched "ladder", "slope", "dose", "sweep", "arm", "counterfactual", "replay",
       "elasticity". `tools/run_value_cycle_ab.py` is the pattern taken WHOLE -- runs of
       `simulation.run_phase4c_on_phase2b.main()` through one window, each inside
       `policy_scope(...)` AND passing `policy=`, differing in exactly one policy field, with the
       differing-field set written into the artefact as a provenance fact. That file is the TWO-
       POINT version of this experiment and this is the N-point one; it is not folded into it
       because its subject is a P&L delta between two arms on a settled question of which earns
       more, and this one's subject is a SLOPE and reports no P&L headline at all.
       `tools/couple_value_based_pricing.py` was read and is not this: it compares what the arms
       would DECIDE on a finished book and never lets the world answer.

WHY THIS EXISTS
---------------
`docs/design/THE_VALUE_CYCLE_REALISED_AB.md`, 2026-08-27, naming the only design that can
separate the two live explanations of the +GBP 16,773 headline:

    Measure the slope, not the level -- a price ladder. Run the arm at several margin
    multipliers on the same book and the same seeds, and compare the *slope* of believed churn
    against the *slope* of realised churn. Because the roll is fixed per (account, term_start),
    a ladder needs no matched pairs and no distributional assumption: the flip count as a
    function of price is a direct read of the world's curve against the company's. It converts
    an n=4 level comparison into a dose-response with 42 decisions at every rung, and it is the
    only design here that can separate "wrong level" from "wrong reference".

THE QUESTION UNDERNEATH IT is the director's: the advantage must come from INFERENCE and not
from ACCESS. Three ways for it to be hollow had been closed or bounded -- access, the horizon,
the BOUND. The 2026-08-27 section added a fourth that nothing had measured: it can come from
PRICE. If realised non-renewals barely move with price while the company's belief moves steeply,
the arm is not predicting who leaves; it is charging more into a world that does not punish it,
and the headline is a fact about the switching curve.

WHAT MAKES A LADDER WORK WHERE THE 42-RENEWAL COMPARISON DID NOT
---------------------------------------------------------------
`simulation/customer_events.roll_lifecycle_event` draws its dice as
`_random.Random(f"{billing_account}_{term_start_str}").random()` -- seeded on the account and the
term and NOTHING ELSE, so the roll is byte-identical at every rung. An arm can only change an
outcome by moving `effective_p_retain` across that fixed number. So the ladder needs no matched
pairs and no distributional assumption, and the 18 decisions the world rolled no outcome for stop
being a hole in a level comparison: they are simply absent from every rung equally.

THE THREE THINGS THAT MUST BE READ BESIDE THE SLOPE
---------------------------------------------------
  1. THE NULL RUNG. `k=0.0` delivers `flat + 0 x (chosen - flat)` = the flat rule EXACTLY, so
     rung zero must reproduce the flat-rules control arm's churn roster and net margin. It is
     checked here against a real control run, not asserted (R15): a ladder whose null rung differs
     from the control is measuring the multiplier's plumbing, not the world's curve.
  2. THE COMMON POPULATION. A rung that churns an account at its 2017 renewal removes that
     account's 2018 renewal from the book, so the priced set SHRINKS as the ladder rises. A slope
     taken over each rung's own population would be confounded by that attrition. Every slope here
     is taken over decisions priced AND rolled at EVERY rung, and the size of that set and the
     per-rung attrition are published beside it.
  3. WHICH RUNGS THE COMPANY CANNOT PREDICT. Above `max_supported_rate_increase_pct()` the
     believed leg is the company's own extrapolation past the frontier of its evidence. Those
     rungs are still priced -- a ladder ASKS, it does not choose -- but the count is carried per
     rung and a believed slope read across them is an extrapolated slope.

THE OUTPUT IS A MEASUREMENT, NOT A REPAIR (R13). Nothing here changes the company's belief and
nothing changes the world's switching response. Where the arithmetic lands on the world's curve it
is recorded for the curriculum and left there: the baseline world may only change for
fidelity-to-reality reasons decided BLIND to what it does to this delta, and this file knows
exactly what it does to this delta, so it is disqualified from making that decision.

Run:  python3 -m tools.run_price_ladder [--end-year 2019] [--rungs 0,0.5,1,1.5,2]
"""
from __future__ import annotations

import argparse
import collections
import json
import statistics
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

# THE HOUSEHOLD SIDE (atom `A47`). Read here in the HARNESS, which is the
# reporting use R12 protects -- no company organ, world module or draw may
# import it, and `tests/company/test_household_share_is_not_yet_a_target.py`
# holds that and names what releases it.
from company.analytics.household_value_share import build_household_value_share
from company.policy.decision_policy import (
    CURRENT_POLICY,
    VALUE_ARM_POLICY,
    policy_scope,
)
from company.pricing.ofgem_price_cap import get_cap_unit_rate_for_date
from simulation.run_phase4c_on_phase2b import main as run_phase4c
from simulation.svt_rates import get_svt_elec_rate_gbp_per_mwh

PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_DIR / "docs" / "observability" / "value_cycle_price_ladder.json"

#: The rungs. Zero is the null control and is NOT optional -- `main` puts it back if a caller
#: leaves it out, because every slope below is read against a leg whose plumbing it is the only
#: check on. The top rung is deliberately past what the company's churn model has evidence for:
#: the believed slope out there is an extrapolation and the world's answer is not, which is the
#: one region where the two legs can be told apart by something other than their level.
DEFAULT_RUNGS = (0.0, 0.25, 0.5, 1.0, 1.5, 2.0)


def _decisions(result: dict) -> list[dict]:
    """Every renewal the arm actually PRICED in this run -- declines excluded.

    A decline leaves the rate untouched, so it is the flat rule at every rung and carries no
    dose. Counting it would put the same point into every rung and flatten both legs equally,
    which looks like agreement and is arithmetic.
    """
    log = (result.get("phase2b") or {}).get("value_arm_log") or []
    return [e for e in log
            if isinstance(e, dict) and not e.get("declined")
            and isinstance(e.get("believed_p_retain"), (int, float))]


def _outcomes(result: dict) -> dict[tuple, dict]:
    """(account, term_start) -> the world's own lifecycle event at that renewal.

    THE INDEPENDENT LEG (R15). The believed side is the company's logged forecast; this side is
    the world's event log, which carries the roll, the effective retention probability it was
    compared against, and the world's own price position vs the published SVT. Not two readings
    of one probability -- a forecast and a tally.
    """
    events = (result.get("phase2b") or {}).get("customer_events") or []
    out = {}
    for event in events:
        if not isinstance(event, dict):
            continue
        out[(event.get("customer_id"), event.get("event_date"))] = event
    return out


def _svt_position_pct(unit_rate: float | None, term_start: str | None) -> float | None:
    """THE WORLD'S REFERENCE, computed for decisions the world rolled no event for.

    Same source, same key and same arithmetic as
    `simulation/customer_events._price_differential_vs_market` -- deliberately, because a second
    notion of "the market" here would be one name and two numbers. Where the world DID roll an
    event this function's answer is reconciled against the world's own logged
    `price_differential_vs_svt` (see `reference_divergence.svt_reconciliation`), so the reuse is
    checked rather than trusted.

    This is HARNESS code reading a SIM module to MEASURE. It is not a company observable and
    nothing on the company side is given it: whether a supplier can see its own position against
    the published SVT is a question about the world's observables, recorded for the director under
    R13 and not answered by this file.
    """
    if unit_rate is None or not term_start:
        return None
    from simulation.svt_rates import get_svt_elec_rate_gbp_per_mwh

    svt = get_svt_elec_rate_gbp_per_mwh(term_start)
    if not svt or svt <= 0:
        return None
    return 100.0 * (float(unit_rate) - float(svt)) / float(svt)


def _ols_slope(xs: list[float], ys: list[float]) -> dict:
    """Least-squares slope of y on x, with enough beside it to refuse it.

    `r_squared` and `n` are carried because a slope through three points on a saturating curve is
    a summary and not a law, and a reader given only the number would take it for one. R12: a
    diagnostic, never a target.
    """
    n = len(xs)
    if n < 2:
        return {"available": False, "why_not": f"a slope needs two rungs; this has {n}"}
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 1e-12:
        return {"available": False, "why_not": "every rung landed at the same price"}
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx
    intercept = my - slope * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
    return {
        "available": True,
        "slope": slope,
        "intercept": intercept,
        "r_squared": (1.0 - ss_res / ss_tot) if ss_tot > 1e-12 else None,
        "n_rungs": n,
    }


def run_rung(multiplier: float, report_end: str | None) -> dict:
    """One rung: the value arm at `multiplier` of its own uplift, through the whole window.

    TWO PLACES, ONE POLICY. `policy_scope(...)` AND `policy=` both carry it, and
    `run_phase2b.main` refuses a run whose argument and scope disagree -- so a rung cannot be
    produced under one multiplier and scored under another.
    """
    policy = replace(
        VALUE_ARM_POLICY,
        name=f"value_arm_ladder_k{multiplier}",
        renewal_margin_ladder_multiplier=float(multiplier),
    )
    with policy_scope(policy):
        return run_phase4c(report_end=report_end, policy=policy)


def rung_reading(multiplier: float, result: dict) -> dict:
    """What one rung priced, what the company believed about it, and what the world did."""
    decisions = _decisions(result)
    outcomes = _outcomes(result)
    rows = []
    for entry in decisions:
        key = (entry.get("customer_id"), entry.get("term_start"))
        event = outcomes.get(key)
        rate = entry.get("unit_rate_after")
        rows.append({
            "account": key[0],
            "term_start": key[1],
            "margin_gbp_per_mwh": entry.get("chosen_margin_gbp_per_mwh"),
            "uplift_gbp_per_mwh": entry.get("uplift_gbp_per_mwh"),
            "unit_rate_gbp_per_mwh": rate,
            # THE TWO REFERENCES, SIDE BY SIDE, per decision. The company's is a DELTA against
            # this customer's own prior rate; the world's is a LEVEL against the published SVT.
            "rate_increase_pct": entry.get("rate_increase_pct"),
            "rate_vs_svt_pct": _svt_position_pct(rate, key[1]),
            "believed_p_retain": entry.get("believed_p_retain"),
            "believed_p_leave": (
                None if entry.get("believed_p_retain") is None
                else 1.0 - float(entry["believed_p_retain"])),
            "ladder_ceiling_clamped": bool(entry.get("ladder_ceiling_clamped")),
            "ladder_above_support_bound": bool(entry.get("ladder_above_support_bound")),
            # The world's side. `None` where the world rolled no decision at this renewal --
            # named rather than defaulted, because "no decision was rolled" and "they stayed"
            # are different facts and scoring the first as the second flatters the arm.
            "world_rolled": event is not None,
            "left": None if event is None else (event.get("event_type") == "churned"),
            "world_effective_p_retain": (
                None if event is None else event.get("effective_retention_probability")),
            # THE WORLD'S OWN CHURN PROBABILITY AT THIS PRICE, before its retention-offer
            # adjustment. `roll_lifecycle_event`'s own docstring names it "the correct ground
            # truth to compare a company churn estimate against, since the estimate is computed
            # before the company decides whether to make an offer" -- so it is the quantity the
            # believed leg is put beside in `world_curve_vs_belief`, and the post-offer
            # `effective_retention_probability` above is what the fixed roll is actually compared
            # to. Two different questions; both carried, neither substituted for the other.
            "world_realized_p_leave": (
                None if event is None else event.get("realized_churn_probability")),
            "world_roll": None if event is None else event.get("random_roll"),
            "world_price_differential_vs_svt": (
                None if event is None else event.get("price_differential_vs_svt")),
            "world_churn_position_multiplier": (
                None if event is None else event.get("churn_position_multiplier")),
        })

    rolled = [r for r in rows if r["world_rolled"]]
    return {
        "multiplier": multiplier,
        "priced": len(rows),
        "rolled_by_the_world": len(rolled),
        "unrolled": len(rows) - len(rolled),
        "ceiling_clamped": sum(1 for r in rows if r["ladder_ceiling_clamped"]),
        "above_support_bound": sum(1 for r in rows if r["ladder_above_support_bound"]),
        "household_side": household_side(result),
        "decisions": rows,
    }


def published_default_tariff(on_date, commodity: str) -> float | None:
    """The published default tariff for a fuel on a date, in GBP/MWh — one concept, two sources.

    THE BOOK IS DUAL FUEL and the two sources cover different things, so both are needed and
    neither is a substitute for the other:

      * `company/pricing/ofgem_price_cap.py` carries BOTH fuels and begins in 2019, when the
        Default Tariff Cap's published windows begin.
      * `simulation/svt_rates.py` carries ELECTRICITY ONLY and begins in 2016 — the standard
        variable tariff of the pre-cap era, which is what a household's default actually WAS
        before the cap existed.

    Gas before 2019 therefore has no published reference here and returns None, which excludes
    those rows from both sides of the comparison and counts them. That is a real bound on the
    early years and it is reported (`coverage_pct`), not papered over with the electricity rate:
    valuing gas volumes at the electricity tariff overstates the counterfactual roughly
    four-fold, in our favour, which is the defect
    `tests/company/analytics/test_household_value_share.py::test_gas_volumes_are_never_valued_at_the_electricity_tariff`
    exists to make impossible.

    Where both sources cover the same date the two agree by construction -- the cap IS the
    published SVT from 2019 (185.6 in 2019, 283.4 in 2022, both series).
    """
    capped = get_cap_unit_rate_for_date(commodity, on_date)
    if capped is not None:
        return capped
    if commodity == "electricity":
        return get_svt_elec_rate_gbp_per_mwh(on_date.isoformat())
    return None


def household_side(result: dict) -> dict:
    """THE OTHER SIDE OF THE SCORE, per rung, in pounds (atom `A47`).

    Every other reading in this file is about US -- what the arm priced, what it
    believed, what the world did to our book. The director's 2026-08-28 mission
    says value is created and THEN SHARED, so a rung has a household side too,
    and until this landed nothing anywhere computed it.

    WHY IT BELONGS ON THE LADDER SPECIFICALLY. The realised roll is binary and
    quantised at 1/17 on the common population, which is why the chase-on/chase-off
    comparison of 2026-08-28 could not resolve a world change
    (`WORKER_FINDING_THE_DEFENDING_MARKET_IS_UNMEASURABLE_ON_SEVENTEEN_DECISIONS`).
    Pounds saved has no quantum: it moves continuously with the rate at every
    rung, for every customer, whether or not anyone rolled. That does not rescue
    the churn comparison -- it is a different question with a different surface,
    and it is stated here as a second reading rather than a substitute.

    IT IS A DIAGNOSTIC AND NOTHING OPTIMISES IT. `tools/` reading this figure is
    the reporting use R12 protects; `tests/company/test_household_share_is_not_yet_a_target.py`
    bars every company organ, world module and draw from importing it, and names
    what releases that.
    """
    records = (result.get("phase2b") or {}).get("all_records") or []
    if not records:
        return {"available": False,
                "reason": "the run carried no settlement records, so no household side exists"}

    # THE COUNTERFACTUAL IS THE PUBLISHED SVT SERIES, NOT THE OFGEM CAP, AND THE CHOICE MATTERS
    # TWICE. (1) COVERAGE: `company/pricing/ofgem_price_cap.py`'s published windows begin in 2019,
    # so a cap counterfactual is blind for the first three years of a 2016-2025 record -- and
    # `--end-year 2019`, the fast iteration mode this ladder is usually run in, would have had
    # almost no comparable periods at all. Caught before running, by asking what the lookup
    # returns at 2016 rather than by reading an empty result afterwards. (2) COMMENSURABILITY:
    # the SVT series is the same reference the world's own churn decision uses
    # (`price_differential_vs_svt` on every lifecycle event), so the household leg and the churn
    # leg are answers about ONE reference rather than two. Where the cap exists the two agree by
    # construction -- the cap IS the SVT from 2019 (185.6 in 2019, 283.4 in 2022, both series).
    view = build_household_value_share(records, svt_rate_for=published_default_tariff)
    p = view.portfolio
    return {
        "available": True,
        "basis": ("settled clock; counterfactual = the published Ofgem default tariff cap "
                  "unit rate for each settlement date, at this customer's own metered volume; "
                  "pounds cover the COMPARABLE periods only (see `coverage_pct`)"),
        # THE PUBLISHED KEYS STILL SAY `customer_years` AND THEY ARE STILL ACCURATE.
        # `A48` generalised the view's grouping to any caller-supplied period; this
        # caller supplies none, so it gets the calendar-year default and its groups
        # ARE customer-years. Renaming the artefact key would have changed a
        # published schema to describe a change this reader did not make.
        "customer_years": view.groups,
        "customer_years_without_any_counterfactual":
            len(view.groups_without_any_counterfactual),
        # Published rather than divided out: a settled book legitimately carries rows this
        # view cannot value, and a reader who cannot see how many is reading a subset.
        "records_this_view_could_not_value": view.records_this_view_could_not_value,
        "coverage_pct": p.coverage_pct,
        "paid_gbp": p.paid_gbp,
        "counterfactual_gbp": p.counterfactual_gbp,
        "household_saving_gbp": p.household_saving_gbp,
        "household_saving_pct_of_counterfactual": p.household_saving_pct_of_counterfactual,
        "our_gross_margin_gbp": p.our_gross_margin_gbp,
        "household_share_of_the_split_pct": p.household_share_of_the_split_pct,
        "what_this_is_not": (
            "NOT value created. Creation is a comparison of COSTS and the counterfactual "
            "supplier's cost is not observable to us; this is how a surplus whose size we "
            "cannot yet measure was SPLIT. Atom A48."),
    }


def null_control_check(rung_zero: dict, control: dict) -> dict:
    """DOES RUNG ZERO REPRODUCE THE CONTROL? The one control this whole file rests on.

    `k=0.0` delivers `flat + 0 x (chosen - flat)`, which is the flat rule to the last decimal, so
    the world it produces must be the flat-rules world: same accounts leaving at the same
    renewals, same net margin. If it is not, the multiplier is doing something other than scaling
    the uplift and every slope below is a reading of that instead of the world's curve.

    It CAN FAIL (R15) and the mutation that makes it fail is the obvious one: change the rung
    parameterisation from `flat + k x (chosen - flat)` to `k x chosen`, and rung zero becomes a
    zero-margin offer that the flat-rules control never made.
    """
    z_events = _outcomes(rung_zero)
    c_events = _outcomes(control)
    z_left = {k for k, e in z_events.items() if e.get("event_type") == "churned"}
    c_left = {k for k, e in c_events.items() if e.get("event_type") == "churned"}
    z_net = (rung_zero.get("phase4c") or {}).get("total_net_margin_gbp")
    c_net = (control.get("phase4c") or {}).get("total_net_margin_gbp")
    if z_net is None or c_net is None:
        z_net = sum(r.get("net_margin_gbp", 0.0)
                    for r in ((rung_zero.get("phase2b") or {}).get("all_records") or []))
        c_net = sum(r.get("net_margin_gbp", 0.0)
                    for r in ((control.get("phase2b") or {}).get("all_records") or []))
    roster_matches = z_left == c_left
    net_matches = abs(float(z_net) - float(c_net)) < 0.01
    return {
        "available": True,
        "churn_roster_matches": roster_matches,
        "net_margin_matches": net_matches,
        "rung_zero_churned": len(z_left),
        "control_churned": len(c_left),
        "only_in_rung_zero": sorted(f"{a}@{t}" for a, t in (z_left - c_left))[:10],
        "only_in_control": sorted(f"{a}@{t}" for a, t in (c_left - z_left))[:10],
        "rung_zero_net_margin_gbp": float(z_net),
        "control_net_margin_gbp": float(c_net),
        "verdict": (
            "rung zero reproduces the flat-rules control exactly, so the multiplier scales the "
            "uplift and nothing else"
            if roster_matches and net_matches else
            "RUNG ZERO DIVERGES FROM THE CONTROL -- the ladder is measuring its own plumbing and "
            "no slope below may be read"
        ),
    }


def _term_start_span(keys) -> list[str] | None:
    """[first year, last year] of a population's term starts, or None if it is empty.

    Published beside every population this file prints. The number that misled two consecutive
    findings was not wrong, it was CONFINED: 16 decisions whose term starts were all 2016-2018,
    read as a fact about a book that ran to 2021. A count cannot show that and a span can.
    """
    years = sorted({str(k[1])[:4] for k in keys})
    return [years[0], years[-1]] if years else None


# The one sentence every reader of a cross-rung intersection has to be handed, published INTO the
# artefact rather than left in this file, because the readers that got it wrong were reading the
# artefact (2026-08-29 finding: the chase comparison asked a fixed-rung question on this set).
_FIXED_RUNG_WARNING = (
    "THIS SET IS FOR THE SLOPE. A slope needs one population along one x-axis, so this is the "
    "decisions priced AND rolled at EVERY rung. It is the WRONG population for any question "
    "asked at a FIXED rung -- a between-arm comparison, a level, a rate at one multiplier -- "
    "because rungs above 1.0 price the book away and the intersection is therefore confined to "
    "the START of the window however long the window is. A fixed-rung question must draw on that "
    "rung's own priced-and-rolled set, published beside each point as "
    "`n_priced_and_rolled_at_this_rung`."
)


def slopes(rungs: list[dict]) -> dict:
    """THE TWO SLOPES, over one population, against one x-axis.

    THE POPULATION IS THE INTERSECTION and that is the whole methodological content of this
    function. A higher rung churns accounts earlier, which deletes their later renewals from the
    book; taking each rung's slope over its own survivors would compare a rung's price effect
    against a different rung's population, and the attrition itself is caused by the treatment.
    So: decisions PRICED and ROLLED at EVERY rung, and the count of what that discarded.

    AND THAT MAKES IT A SELECTION EFFECT IN EVERY OTHER QUESTION ASKED OF IT. The census of
    readers, as of 2026-08-29, with each one's question classified:

    * this function's own slopes and ratios -- CROSS-RUNG, keep: the intersection is what makes
      the x-axis one axis.
    * `world_curve_vs_belief` -- CROSS-RUNG, keep: a per-decision slope over the rungs.
    * this file's CLI table (`main`) -- reads `points` per rung, which is a FIXED-RUNG reading of
      a cross-rung set. Repaired by publishing each rung's own n and term-start span in the same
      row, so the shared `n` can no longer be read as this rung's book.
    * `tools/compare_chase_belief._points` -- FIXED-RUNG (belief ON vs OFF at one multiplier).
      Superseded as the verdict by `per_rung_paired`, which pairs on each rung's own set; the
      intersection table is retained as the exhibit and prints its own confinement.
    * `tools/compare_chase_belief._decisions` -- was FIXED-RUNG (endpoint rungs) on this set AND
      endpoints-only. DELETED 2026-08-29 rather than repaired: `per_decision` cannot carry an
      interior rung, so the question it asked is only answerable from the per-rung join.

    THE X-AXIS IS THE DELIVERED UPLIFT in GBP/MWh -- the actual money added to the customer's
    unit rate at that rung, averaged over the common population. It is used rather than the
    nominal multiplier because a rung clamped by the lawful cap delivers less price than it was
    asked for, and a slope plotted against the ASK would read that clamp as the world refusing to
    respond. The two REFERENCE positions -- the company's `rate_increase_pct` and the world's
    `rate_vs_svt_pct` -- are reported per rung beside it, and the slope is also taken against each
    of them, because Finding 4 of the 2026-08-27 section is that those two disagree and a reader
    who is shown only one cannot see it.
    """
    per_rung_keys = []
    for rung in rungs:
        per_rung_keys.append({
            (d["account"], d["term_start"]) for d in rung["decisions"] if d["world_rolled"]
        })
    if not per_rung_keys:
        return {"available": False, "why_not": "no rungs"}
    common = set.intersection(*per_rung_keys)
    if len(common) < 2:
        return {"available": False, "why_not": (
            f"only {len(common)} decision(s) were priced and rolled at every rung, which is not a "
            "population")}

    common_span = _term_start_span(common)
    points = []
    for index, rung in enumerate(rungs):
        rows = [d for d in rung["decisions"] if (d["account"], d["term_start"]) in common]
        left = [r for r in rows if r["left"]]
        believed = [r["believed_p_leave"] for r in rows if r["believed_p_leave"] is not None]
        inc = [r["rate_increase_pct"] for r in rows if r["rate_increase_pct"] is not None]
        svt = [r["rate_vs_svt_pct"] for r in rows if r["rate_vs_svt_pct"] is not None]
        uplift = [r["uplift_gbp_per_mwh"] for r in rows if r["uplift_gbp_per_mwh"] is not None]
        # THE CONTINUOUS TWIN OF THE BINARY LEG ABOVE. `realised_non_renewal_rate` is a count of
        # flips over `n`, so on this book it can only take the values k/17 and the smallest
        # change it can express is 5.9 percentage points. The world writes its OWN churn
        # probability at the same renewal, before the roll, and that quantity has no quantum.
        # Both are published because they answer different questions -- a non-renewal is a thing
        # that happened and a probability is not -- and the binary one stays the headline.
        world_p = [r["world_realized_p_leave"] for r in rows
                   if r["world_realized_p_leave"] is not None]
        # FAIL CLOSED ON A PARTIAL POPULATION. Averaging whichever rows happen to carry the
        # probability would publish a mean over one population beside a rate over another, and
        # their difference would read as a price effect. Either every row in the common set
        # carries it or the continuous leg says it cannot be read.
        world_p_complete = len(world_p) == len(rows) and bool(rows)
        points.append({
            "multiplier": rung["multiplier"],
            "n": len(rows),
            # THE RUNG'S OWN POPULATION, BESIDE THE SHARED ONE. `n` above is the cross-rung
            # intersection, so it is the same number at every rung; a reader meeting it in a
            # per-rung row reads it as this rung's book, and on the 2021-window founder pair that
            # meant reading 16 decisions confined to 2016-2018 as a fact about 99 spanning
            # 2016-2021. The span is carried too, because the count alone cannot show WHICH years
            # the intersection kept -- and the confinement, not the size, was the defect.
            "n_priced_and_rolled_at_this_rung": len(per_rung_keys[index]),
            "term_starts_at_this_rung": _term_start_span(per_rung_keys[index]),
            "term_starts_in_common": common_span,
            "mean_uplift_gbp_per_mwh": statistics.fmean(uplift) if uplift else None,
            "mean_rate_increase_pct": statistics.fmean(inc) if inc else None,
            "mean_rate_vs_svt_pct": statistics.fmean(svt) if svt else None,
            "realised_non_renewals": len(left),
            "realised_non_renewal_rate": len(left) / len(rows) if rows else None,
            "world_p_leave_mean": statistics.fmean(world_p) if world_p_complete else None,
            "world_p_leave_carried": len(world_p),
            "world_p_leave_why_not": (
                None if world_p_complete else
                f"{len(world_p)} of {len(rows)} decisions in the common population carry the "
                "world's own churn probability, so a mean over them would not be the population "
                "the realised rate beside it counts"),
            "believed_non_renewal_rate": statistics.fmean(believed) if believed else None,
            "believed_non_renewals_expected": (
                statistics.fmean(believed) * len(rows) if believed else None),
            "ceiling_clamped_in_common": sum(1 for r in rows if r["ladder_ceiling_clamped"]),
            "above_support_in_common": sum(1 for r in rows if r["ladder_above_support_bound"]),
        })

    def _pair(x_key: str) -> dict:
        xs, yr, yb = [], [], []
        xw, yw = [], []
        for p in points:
            # The continuous leg is gathered on its OWN axis, not skipped in step with the
            # binary one: a rung whose believed leg is missing still carries a readable world
            # probability, and dropping it would shorten a slope for a reason that has nothing
            # to do with the world.
            if p[x_key] is not None and p["world_p_leave_mean"] is not None:
                xw.append(p[x_key])
                yw.append(p["world_p_leave_mean"])
            if p[x_key] is None or p["realised_non_renewal_rate"] is None:
                continue
            if p["believed_non_renewal_rate"] is None:
                continue
            xs.append(p[x_key])
            yr.append(p["realised_non_renewal_rate"])
            yb.append(p["believed_non_renewal_rate"])
        realised = _ols_slope(xs, yr)
        believed = _ols_slope(xs, yb)
        world_p = _ols_slope(xw, yw)
        ratio = None
        if realised.get("available") and believed.get("available"):
            if abs(believed["slope"]) > 1e-12:
                ratio = realised["slope"] / believed["slope"]
        # The same ratio the binary leg reports, on the quantity that can actually move. Read
        # this one when the two disagree: the binary numerator is a count of flips and the
        # continuous one is not, so a divergence between them is resolution, not physics.
        world_ratio = None
        if world_p.get("available") and believed.get("available"):
            if abs(believed["slope"]) > 1e-12:
                world_ratio = world_p["slope"] / believed["slope"]
        return {
            "x": x_key,
            "realised": realised,
            "believed": believed,
            "realised_over_believed": ratio,
            "world_p_leave": world_p,
            "world_p_leave_over_believed": world_ratio,
        }

    return {
        "available": True,
        "common_population": len(common),
        "common_population_term_starts": common_span,
        "common_population_note": (
            "decisions priced AND rolled by the world at EVERY rung. Rungs above 1.0 churn "
            "accounts earlier, which removes their later renewals from the book, so this set is "
            "smaller than any single rung's -- `per_rung.rolled_by_the_world` shows the "
            "attrition. Every slope here is taken over this one set."
        ),
        "a_fixed_rung_question_may_not_use_this_set": _FIXED_RUNG_WARNING,
        # Every rung's own paired population, published so no figure in this artefact can be read
        # without the n it was taken over standing next to it.
        "per_rung_population": [
            {"multiplier": rung["multiplier"],
             "n_priced_and_rolled": len(keys),
             "n_in_common": len(common),
             "term_starts": _term_start_span(keys)}
            for rung, keys in zip(rungs, per_rung_keys)],
        "points": points,
        "against_delivered_uplift": _pair("mean_uplift_gbp_per_mwh"),
        "against_company_reference": _pair("mean_rate_increase_pct"),
        "against_world_reference": _pair("mean_rate_vs_svt_pct"),
        "how_to_read_this": (
            "`realised_over_believed` near 1.0 on `against_delivered_uplift` means the company's "
            "belief moves with price at the rate the world actually does -- the arm's advantage "
            "is then a claim about WHO leaves and not about how hard price bites. Well below 1.0 "
            "means the company over-predicts the response, so it under-prices relative to what "
            "the world would tolerate and any win is left on the table rather than taken from "
            "the world's softness. Well ABOVE 1.0 is the hollow case the director's question is "
            "about: the world punishes price harder than the company believes, the arm is "
            "charging into a response it cannot see, and the headline is a fact about the "
            "switching curve rather than about inference. R12: a diagnostic, never a target."
        ),
    }


def household_saving_curve(rungs: list[dict]) -> dict:
    """What the ladder costs the households on it — the second, continuous surface.

    THE ARGUMENT FOR THIS EXISTING (atom `A47`, and the negative result of
    2026-08-28 that motivated it). The realised churn leg is 17 binary decisions
    on the common population, so its smallest expressible move is 5.9 percentage
    points; a chase-on/chase-off comparison could not resolve a world change that
    the unit tests prove is there. Pounds kept by households has no such quantum.
    Every customer contributes at every rung whether or not anyone rolled, so
    this leg answers "what does the ladder do to the people on it" with a
    resolution the churn leg cannot reach.

    WHAT IT IS NOT. It is not a better measure of the same thing. Churn asks who
    left; this asks what those who stayed kept. A ladder can be invisible on the
    first and enormous on the second, and that combination is not a contradiction
    — it is the exact shape of a supplier raising prices on a book that has
    nowhere to go, which is the case a one-sided score cannot see at all.
    """
    xs, ys, out = [], [], []
    for rung in rungs:
        side = rung.get("household_side") or {}
        if not side.get("available") or side.get("household_saving_gbp") is None:
            continue
        priced = [d for d in rung.get("decisions", [])
                  if isinstance(d.get("uplift_gbp_per_mwh"), (int, float))]
        if not priced:
            continue
        mean_uplift = statistics.fmean(float(d["uplift_gbp_per_mwh"]) for d in priced)
        xs.append(mean_uplift)
        ys.append(float(side["household_saving_gbp"]))
        out.append({
            "multiplier": rung["multiplier"],
            "mean_uplift_gbp_per_mwh": mean_uplift,
            "household_saving_gbp": side["household_saving_gbp"],
            "household_saving_pct_of_counterfactual":
                side.get("household_saving_pct_of_counterfactual"),
            "our_gross_margin_gbp": side.get("our_gross_margin_gbp"),
            "household_share_of_the_split_pct":
                side.get("household_share_of_the_split_pct"),
        })

    if len(out) < 2:
        return {"available": False,
                "reason": ("fewer than two rungs carry a household side, so no curve exists -- "
                           "stated rather than returned as a flat line"),
                "rungs_with_a_household_side": len(out)}

    return {
        "available": True,
        "rungs": out,
        "gbp_saved_per_gbp_per_mwh_of_uplift": _ols_slope(xs, ys),
        "how_to_read_this": (
            "The slope is pounds of household saving gained (positive) or lost (negative) per "
            "£1/MWh of margin uplift, across the ladder. It is a DIAGNOSTIC: nothing optimises "
            "it, and half of the two-sided objective is not the objective until the director "
            "decides it is (R13)."),
    }


def world_curve_vs_belief(rungs: list[dict]) -> dict:
    """THE SAME COMPARISON AT FULL POWER: the world's own churn probability against the company's,
    per decision, over the same rungs.

    WHY THIS EXISTS BESIDE THE FLIP COUNT. `slopes` answers the question the direction asked --
    realised non-renewals against price -- and it is the honest headline, because a non-renewal is
    a thing that happened and a probability is not. But a flip count over N decisions can only take
    N+1 values, so on this book the realised leg moves in steps of 1/6 and a slope through six such
    steps is chunky in a way no amount of care recovers. That coarseness is the 2026-08-27
    section's own verdict: "the sample cannot separate them, effective n is 4".

    The world writes its OWN probability into the event log at every renewal it rolls. Comparing
    the two probability CURVES is the same question with the sampling noise taken out: the roll is
    fixed per (account, term_start), so a decision's curve is measured against itself at six
    prices and the comparison is PAIRED -- no matched pairs to find, no population to balance, no
    distributional assumption. The n stops being the flip count and becomes decisions x rungs.

    IT IS NOT A COMPANY OBSERVABLE AND NOTHING HERE HANDS IT TO ONE. `realized_churn_probability`
    is SIM ground truth read by the HARNESS to score a belief -- the coupled-triad's "the gap is
    the score", the same thing `churn_estimate_error_pct` already does one renewal at a time. What
    is new is only that it is now read as a FUNCTION OF PRICE.

    THE PER-DECISION RATIO IS THE ANSWER and the pooled one is the cross-check. Pooling slopes
    across decisions weights by whichever account happens to have the widest price range, which is
    an artefact of what the arm chose to charge; the median of the per-decision ratios is not.
    Both are published, and if they disagree the pooled one is the one to distrust.
    """
    per_rung = []
    for rung in rungs:
        per_rung.append({(d["account"], d["term_start"]): d for d in rung["decisions"]
                         if d["world_rolled"] and d["world_realized_p_leave"] is not None
                         and d["believed_p_leave"] is not None
                         and d["uplift_gbp_per_mwh"] is not None})
    if len(per_rung) < 2:
        return {"available": False, "why_not": "a curve needs at least two rungs"}
    common = set.intersection(*[set(m) for m in per_rung])
    if not common:
        return {"available": False, "why_not": (
            "no decision was priced and rolled with a world probability at every rung")}

    rows, ratios, over, under = [], [], 0, 0
    for key in sorted(common):
        xs = [m[key]["uplift_gbp_per_mwh"] for m in per_rung]
        world = _ols_slope(xs, [float(m[key]["world_realized_p_leave"]) for m in per_rung])
        belief = _ols_slope(xs, [float(m[key]["believed_p_leave"]) for m in per_rung])
        ratio = None
        if world.get("available") and belief.get("available") and abs(belief["slope"]) > 1e-12:
            ratio = world["slope"] / belief["slope"]
            ratios.append(ratio)
            if ratio < 1.0:
                over += 1     # the company believes price bites HARDER than it does
            else:
                under += 1
        rows.append({
            "account": key[0],
            "term_start": key[1],
            "price_range_gbp_per_mwh": max(xs) - min(xs),
            "world_p_leave_slope_per_gbp_per_mwh": world.get("slope"),
            "believed_p_leave_slope_per_gbp_per_mwh": belief.get("slope"),
            "world_over_believed": ratio,
            "world_p_leave_at_lowest_rung": float(per_rung[0][key]["world_realized_p_leave"]),
            "world_p_leave_at_highest_rung": float(per_rung[-1][key]["world_realized_p_leave"]),
            "believed_p_leave_at_lowest_rung": float(per_rung[0][key]["believed_p_leave"]),
            "believed_p_leave_at_highest_rung": float(per_rung[-1][key]["believed_p_leave"]),
        })

    pooled_x = [d["uplift_gbp_per_mwh"] for m in per_rung for d in m.values()
                if (d["account"], d["term_start"]) in common]
    pooled_w = [float(d["world_realized_p_leave"]) for m in per_rung for d in m.values()
                if (d["account"], d["term_start"]) in common]
    pooled_b = [float(d["believed_p_leave"]) for m in per_rung for d in m.values()
                if (d["account"], d["term_start"]) in common]
    pooled_world, pooled_belief = _ols_slope(pooled_x, pooled_w), _ols_slope(pooled_x, pooled_b)
    pooled_ratio = None
    if (pooled_world.get("available") and pooled_belief.get("available")
            and abs(pooled_belief["slope"]) > 1e-12):
        pooled_ratio = pooled_world["slope"] / pooled_belief["slope"]

    return {
        "available": True,
        "decisions": len(common),
        "term_starts_in_common": _term_start_span(common),
        "observations": len(common) * len(per_rung),
        # THE SAME CONFINEMENT, IN THE SAME PLACE. The per-decision slopes below are a cross-rung
        # question and the intersection is right for them. `per_decision`'s ROWS are not: they
        # carry each decision's lowest and highest rung, so a reader taking a between-arm
        # difference off `..._at_lowest_rung` is asking a fixed-rung question on this set, and
        # `tools/compare_chase_belief` did exactly that until 2026-08-29.
        "a_fixed_rung_question_may_not_use_this_set": _FIXED_RUNG_WARNING,
        "per_rung_population": [
            {"multiplier": rung["multiplier"],
             "n_priced_rolled_and_believed": len(keys),
             "n_in_common": len(common),
             "term_starts": _term_start_span(keys)}
            for rung, keys in zip(rungs, per_rung)],
        "median_world_over_believed": statistics.median(ratios) if ratios else None,
        "mean_world_over_believed": statistics.fmean(ratios) if ratios else None,
        "decisions_where_the_company_over_predicts_the_response": over,
        "decisions_where_the_company_under_predicts_the_response": under,
        "pooled": {
            "world": pooled_world, "believed": pooled_belief, "world_over_believed": pooled_ratio,
            "caveat": (
                "pooled across decisions, so it is weighted by whichever account the arm happened "
                "to price over the widest range. `median_world_over_believed` is not; where the "
                "two disagree, distrust this one."),
        },
        "per_decision": rows,
        # THE INDEPENDENCE CLAIM, made explicitly because a reader who checks the imports will
        # find the shape that looks exactly like R15's tautology and deserves the answer here
        # rather than after raising it.
        "independence": {
            "the_suspicion": (
                "`simulation/customer_events.py:29` imports "
                "`company.crm.churn_model.estimate_churn_probability` -- the very function the "
                "believed leg below is built from. If the world's churn probability were computed "
                "with it, this comparison would be one model against itself and a ratio near 1.0 "
                "would be arithmetic."),
            "the_answer": (
                "It is not. That import feeds ONE thing -- `company_churn_estimate`, the "
                "company's own logged forecast at line 267, which this file does not read. The "
                "world's `realized_churn_probability` is `1 - effective_p_retain_pre_offer` "
                "(line 278), built from `saas.churn_model.build_churn_risk` and "
                "`saas.home_move_win_rate.build_home_move_win_rates`, then the passive cap, "
                "`market_switching_multiplier`, `churn_position_multiplier` on the SVT position, "
                "income stress and satisfaction. No term of it is `estimate_churn_probability`."),
            "held_by": "tests/simulation/test_churn_ceiling.py and the wall scans; and by the two "
                       "legs disagreeing on this book, which a shared source could not do.",
        },
        "how_to_read_this": (
            "BELOW 1.0 means the company believes price bites HARDER than the world makes it "
            "bite. That is the opposite of the hollow case: an arm that over-estimates the "
            "switching response prices BELOW what the world would tolerate, so its advantage "
            "cannot be coming from a world too soft to punish it -- it is leaving money on the "
            "table, not taking it from a forgiving curve. ABOVE 1.0 is the hollow case the "
            "director's question is about: the world punishes harder than the company can see, "
            "the arm is charging into a response it does not model, and any win is a fact about "
            "the switching curve. Near 1.0 means the two agree about HOW HARD price bites, and "
            "the arm's advantage is then a claim about WHO leaves -- which is inference, and is "
            "the thesis. R12: a diagnostic, never a target."
        ),
    }


def reference_divergence(rungs: list[dict]) -> dict:
    """THE TWO PRICE REFERENCES, counted against each other on the same decisions.

    Finding 4 of the 2026-08-27 section: the company keys on a DELTA against the customer's own
    prior rate (`company/crm/churn_model.py:305`) and the world keys on a LEVEL against the
    published SVT (`simulation/customer_events.py:67`). Those are different questions and they
    disagree in both directions. It took an inversion in a four-row bucket table to detect. Here
    it is as a count.

    `svt_reconciliation` is the R15 half: where the world rolled an event it logged its OWN
    `price_differential_vs_svt`, so this file's independently-computed `rate_vs_svt_pct` can be
    checked against it rather than trusted. Two readings of one quantity that agree is evidence
    the join is right; a disagreement means the harness is scoring a different price from the one
    the world charged, which is the defect the 2026-08-26 ceiling repair closed on the other side.
    """
    rows = [d for rung in rungs for d in rung["decisions"]]
    both = [r for r in rows
            if r["rate_increase_pct"] is not None and r["rate_vs_svt_pct"] is not None]
    if not both:
        return {"available": False, "why_not": "no decision carries both references"}

    sign_disagree = [r for r in both
                     if (r["rate_increase_pct"] > 0) != (r["rate_vs_svt_pct"] > 0)]
    # Cheap and dear in the company's frame vs the world's, as the two named tails.
    company_says_rise_world_says_cheap = [
        r for r in both if r["rate_increase_pct"] > 10.0 and r["rate_vs_svt_pct"] < 0.0]
    company_says_flat_world_says_dear = [
        r for r in both if abs(r["rate_increase_pct"]) < 10.0 and r["rate_vs_svt_pct"] > 20.0]

    recon = [r for r in both if r["world_price_differential_vs_svt"] is not None]
    worst = 0.0
    for r in recon:
        worst = max(worst, abs(r["rate_vs_svt_pct"] - 100.0 * float(
            r["world_price_differential_vs_svt"])))

    return {
        "available": True,
        "decisions_with_both_references": len(both),
        "sign_disagreements": len(sign_disagree),
        "sign_disagreement_share": len(sign_disagree) / len(both),
        "company_says_rise_world_says_below_svt": len(company_says_rise_world_says_cheap),
        "company_says_flat_world_says_30pct_dear": len(company_says_flat_world_says_dear),
        "mean_rate_increase_pct": statistics.fmean(r["rate_increase_pct"] for r in both),
        "mean_rate_vs_svt_pct": statistics.fmean(r["rate_vs_svt_pct"] for r in both),
        "svt_reconciliation": {
            "decisions_the_world_also_priced": len(recon),
            "largest_absolute_gap_pct_points": worst,
            "agrees": worst < 0.05,
            "meaning": (
                "this file's `rate_vs_svt_pct` against the world's own logged "
                "`price_differential_vs_svt` at the same renewal. Agreement means the harness is "
                "scoring the rate the customer was actually charged; a gap means it is not, and "
                "no reference comparison above may be read."
            ),
        },
        "sample": [
            {k: r[k] for k in ("account", "term_start", "rate_increase_pct", "rate_vs_svt_pct",
                               "believed_p_leave", "left")}
            for r in sorted(both, key=lambda r: r["rate_vs_svt_pct"] - r["rate_increase_pct"])[:8]
        ],
    }


def unmatched_diagnosis(rung: dict, result: dict) -> dict:
    """THE 18-UNMATCHED HOLE, answered per account rather than counted.

    The direction: *"either close the 18-unmatched hole or state per account why no decision was
    rolled."* This states it. `roll_lifecycle_event` returns `None` -- and so logs no event at all
    -- when `build_home_move_win_rates` carries no row whose `renewal_period` equals the term's
    month for that billing account. The arm prices off the CONTRACT TERM LIST and that roster
    derives its schedule INDEPENDENTLY (`churn_model._renewal_periods`), so the two can simply
    name different months for the same account.

    So for each unpriced-outcome decision this reports the renewal months the world DID roll for
    that account. A reader can then see, per account, whether the world rolled at a different
    month (a schedule mismatch) or never rolled for that account at all (a roster absence). That
    is the diagnosis the previous artefact's `unmatched_meaning` offered as a hypothesis.

    IT IS A DIAGNOSIS AND NOT A REPAIR. Reconciling the two schedules changes which renewals the
    world rolls, which is a change to the baseline world and therefore R13's -- decided blind to
    what it does to any delta, and not this file's to make.
    """
    outcomes = _outcomes(result)
    by_account = collections.defaultdict(list)
    for account, term in outcomes:
        by_account[account].append(term)
    unmatched = [d for d in rung["decisions"] if not d["world_rolled"]]
    rows = []
    for d in unmatched:
        world_terms = sorted(by_account.get(d["account"], []))
        priced_month = (d["term_start"] or "")[:7]
        same_month = [t for t in world_terms if t[:7] == priced_month]
        rows.append({
            "account": d["account"],
            "priced_term_start": d["term_start"],
            "world_rolled_renewals_for_this_account": world_terms,
            "why_no_decision_was_rolled": (
                # SCOPED TO THE WINDOW, because the answer is not the same sentence on a
                # truncated run as on a full one: an account whose only world renewal falls after
                # `report_end` reads here as "never rolled" and is in fact "rolled later". The
                # window is named in the artefact's `report_end` and the claim is made against it.
                "the world rolled no lifecycle event for this billing account at ANY renewal "
                "INSIDE THIS WINDOW, so `build_home_move_win_rates` carries no row for it here"
                if not world_terms else
                "the world's renewal roster for this account names {} -- none of them the month "
                "the arm priced ({}), so `build_home_move_win_rates` has no row at that "
                "`renewal_period` and `roll_lifecycle_event` returned None".format(
                    ", ".join(world_terms), priced_month)
                if not same_month else
                "the world DID roll at this month ({}) but under a different event_date, so the "
                "(account, term_start) join missed -- a key defect, not a roster one".format(
                    ", ".join(same_month))
            ),
        })
    schedule_mismatch = sum(1 for r in rows if r["world_rolled_renewals_for_this_account"])
    # DECISIONS AND ACCOUNTS ARE DIFFERENT DENOMINATORS and conflating them overstates the hole.
    # Six accounts renewing three times each is eighteen unmatched decisions and SIX absences to
    # explain; a reader shown only "18" reads eighteen separate defects.
    silent_accounts = {r["account"] for r in rows if not r["world_rolled_renewals_for_this_account"]}
    mismatch_accounts = {r["account"] for r in rows if r["world_rolled_renewals_for_this_account"]}
    return {
        "available": True,
        "unmatched_decisions": len(rows),
        "unmatched_accounts": len(silent_accounts | mismatch_accounts),
        "decisions_the_world_never_rolled_for_this_account_in_window": len(rows) - schedule_mismatch,
        "accounts_the_world_never_rolled_at_all_in_window": len(silent_accounts),
        "accounts_the_world_never_rolled_at_all_in_window_named": sorted(silent_accounts),
        "decisions_whose_world_schedule_names_other_months": schedule_mismatch,
        "accounts_whose_world_schedule_names_other_months": len(mismatch_accounts),
        "per_decision": rows,
        "disposition": (
            "STATED, NOT CLOSED. Closing it means reconciling the arm's contract term list with "
            "`churn_model._renewal_periods`, which changes which renewals the world rolls a churn "
            "decision at -- a change to the baseline world, decided under R13 blind to its effect "
            "on any company delta, and recorded for the curriculum rather than made here. It does "
            "NOT bound this ladder: the roll is fixed per (account, term_start), so an unrolled "
            "decision is absent from every rung equally and the slope is taken over the "
            "intersection."
        ),
    }


def run_price_ladder(rungs: tuple[float, ...], report_end: str | None = None) -> dict:
    """Every rung, plus the flat-rules control the null rung is checked against."""
    with policy_scope(CURRENT_POLICY):
        control = run_phase4c(report_end=report_end, policy=CURRENT_POLICY)
    if (control["phase2b"] or {}).get("value_arm_log"):
        raise AssertionError(
            "the CONTROL arm priced {} renewal(s) with the value arm -- the writer is not a no-op "
            "under flat_rules, so the null-rung check below would compare two arms rather than "
            "one arm against itself. Refusing to report it.".format(
                len(control["phase2b"]["value_arm_log"])))

    readings, raw = [], {}
    for k in rungs:
        result = run_rung(k, report_end)
        raw[k] = result
        readings.append(rung_reading(k, result))

    zero = next((k for k in rungs if abs(k) < 1e-12), None)
    null = (null_control_check(raw[zero], control) if zero is not None
            else {"available": False, "why_not": (
                "no zero rung was run, so nothing checks that the multiplier scales the uplift "
                "and only the uplift")})

    base = next((r for r in readings if abs(r["multiplier"] - 1.0) < 1e-12), readings[-1])
    base_raw = raw[base["multiplier"]]

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "report_end": report_end,
        "rungs": list(rungs),
        "what_this_is": (
            "The value arm re-run over the same book and the same seeds at several fixed "
            "multiples of its own chosen uplift, with the world's realised non-renewals and the "
            "company's own believed non-renewals published against the same prices. THE OUTPUT "
            "IS A MEASUREMENT: nothing about the company's belief or the world's switching "
            "response is changed by it."
        ),
        "arm_identity": {
            "differing_fields_vs_control": sorted(
                f for f in CURRENT_POLICY.__dataclass_fields__
                if getattr(CURRENT_POLICY, f) != getattr(VALUE_ARM_POLICY, f)
            ),
            "ladder_field": "renewal_margin_ladder_multiplier",
            "why_it_matters": (
                "A rung differs from the control in `renewal_margin_arm`, "
                "`renewal_margin_ladder_multiplier` and `name`, and `name` does not reach a "
                "decision. Any FOURTH field here means a rung carries an uncontrolled variable."
            ),
        },
        # FIRST, because every slope below is unreadable if it fails.
        "null_rung_check": null,
        "per_rung": [{k: v for k, v in r.items() if k != "decisions"} for r in readings],
        "slopes": slopes(readings),
        # The same comparison with the sampling noise taken out -- read AFTER `slopes`, never
        # instead of it: a non-renewal is a thing that happened and a probability is not.
        "world_curve_vs_belief": world_curve_vs_belief(readings),
        "household_saving_curve": household_saving_curve(readings),
        "reference_divergence": reference_divergence(readings),
        "unmatched_diagnosis": unmatched_diagnosis(base, base_raw),
        "belief_source": (
            "`believed_p_retain` is the value arm's own logged forecast at the rung's delivered "
            "price -- `company/pricing/value_based_renewal.decide_margin` scores the RUNG, not "
            "the unscaled choice, so the believed leg and the realised leg are the same price. "
            "The chain is `enriched_churn_estimate` -> "
            "`company/crm/churn_model.estimate_churn_probability` for the rate leg, maxed with "
            "the payment-behaviour leg and scaled by the company's market-conditions multiplier."
        ),
        "decisions": {str(r["multiplier"]): r["decisions"] for r in readings},
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--end-year", help="truncate the window, e.g. 2019 (faster iteration)")
    ap.add_argument("--rungs", help="comma-separated multipliers, e.g. 0,0.5,1,2")
    ap.add_argument("--out", type=Path, default=OUTPUT_PATH)
    args = ap.parse_args(argv)
    report_end = f"{args.end_year}-12-31" if args.end_year else None
    if args.rungs:
        rungs = tuple(sorted({float(x) for x in args.rungs.split(",") if x.strip()}))
    else:
        rungs = DEFAULT_RUNGS
    if not any(abs(k) < 1e-12 for k in rungs):
        # THE NULL RUNG IS NOT OPTIONAL. It is the only check that the multiplier scales the
        # uplift and nothing else, so a caller who leaves it out gets it back rather than a
        # ladder with no control under it.
        rungs = tuple(sorted(rungs + (0.0,)))

    result = run_price_ladder(rungs, report_end=report_end)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")

    null = result["null_rung_check"]
    print("price ladder -- {} window, rungs {}".format(report_end or "full", list(rungs)))
    print("  NULL RUNG   {}".format(null.get("verdict") or null.get("why_not")))
    s = result["slopes"]
    if s.get("available"):
        span = s.get("common_population_term_starts")
        print("  common population {} decision(s) priced and rolled at every rung{}".format(
            s["common_population"],
            "" if not span else f", term starts {span[0]}-{span[1]}"))
        # THE TWO POPULATIONS, IN EVERY ROW. `n` is the same at every rung by construction, and
        # printing only it is how a set confined to the first years of the window gets read as
        # the book. `own n` is the rung's own priced-and-rolled count and `own years` its span;
        # where they diverge, no figure in this row may be quoted as a fact about the book.
        print("  {:>6} {:>10} {:>12} {:>12} {:>10} {:>10} {:>10} | {:>6} {:>9}".format(
            "k", "uplift", "vs own rate", "vs SVT", "realised", "world p", "believed",
            "own n", "own years"))
        for p in s["points"]:
            own_span = p.get("term_starts_at_this_rung")
            print("  {:>6} {:>10} {:>12} {:>12} {:>10} {:>10} {:>10} | {:>6} {:>9}".format(
                p["multiplier"],
                "n/a" if p["mean_uplift_gbp_per_mwh"] is None
                else f"{p['mean_uplift_gbp_per_mwh']:.2f}",
                "n/a" if p["mean_rate_increase_pct"] is None
                else f"{p['mean_rate_increase_pct']:+.1f}%",
                "n/a" if p["mean_rate_vs_svt_pct"] is None
                else f"{p['mean_rate_vs_svt_pct']:+.1f}%",
                "{}/{} {:.3f}".format(p["realised_non_renewals"], p["n"],
                                      p["realised_non_renewal_rate"] or 0.0),
                "n/a" if p["world_p_leave_mean"] is None
                else f"{p['world_p_leave_mean']:.4f}",
                "n/a" if p["believed_non_renewal_rate"] is None
                else f"{p['believed_non_renewal_rate']:.3f}",
                p.get("n_priced_and_rolled_at_this_rung", "n/a"),
                "n/a" if not own_span else f"{own_span[0]}-{own_span[1]}"))
        # The binary leg's own quantum, printed beside the slopes it bounds, so a reader cannot
        # take a movement smaller than one account for a measurement.
        n_common = s["common_population"]
        print("  the realised leg moves in steps of 1/{} = {:.4f}; the world-p leg has no "
              "quantum".format(n_common, 1.0 / n_common if n_common else float("nan")))
        # Printed, not only written to JSON: the two readers that took a fixed-rung question off
        # this table were reading the output, not the artefact (2026-08-29).
        print("  every figure in the table above is over the COMMON population. A question asked "
              "at ONE rung must use that rung's own n and years, on the right.")
        for axis in ("against_delivered_uplift", "against_company_reference",
                     "against_world_reference"):
            pair = s[axis]
            r, b, w = pair["realised"], pair["believed"], pair["world_p_leave"]
            print("  slope on {:<26} realised {:>12}  world p {:>12}  believed {:>12}  "
                  "ratio r/b {:>7}  w/b {}".format(
                      axis,
                      f"{r['slope']:+.6f}" if r.get("available") else "n/a",
                      f"{w['slope']:+.6f}" if w.get("available") else "n/a",
                      f"{b['slope']:+.6f}" if b.get("available") else "n/a",
                      "n/a" if pair["realised_over_believed"] is None
                      else f"{pair['realised_over_believed']:+.3f}",
                      "n/a" if pair["world_p_leave_over_believed"] is None
                      else f"{pair['world_p_leave_over_believed']:+.3f}"))
    else:
        print("  slopes unavailable: {}".format(s.get("why_not")))

    # THE HOUSEHOLD SIDE, PRINTED. A figure that only reaches a JSON file is half-delivered:
    # every reading above is about what the ladder did to US, and the mission says a decision
    # has two sides, so the other one belongs in the same summary rather than a level down.
    h = result.get("household_saving_curve") or {}
    print("\nHOUSEHOLD SIDE (diagnostic; nothing optimises it -- see A47)")
    if not h.get("available"):
        print("  unavailable: {}".format(h.get("reason")))
    else:
        print("  {:>6} {:>10} {:>14} {:>12} {:>14} {:>12}".format(
            "k", "uplift", "household kept", "of cfact", "we kept gross", "hh share"))
        for row in h["rungs"]:
            pct = row.get("household_saving_pct_of_counterfactual")
            share = row.get("household_share_of_the_split_pct")
            print("  {:>6} {:>10} {:>14} {:>12} {:>14} {:>12}".format(
                row["multiplier"],
                f"{row['mean_uplift_gbp_per_mwh']:.2f}",
                f"GBP {row['household_saving_gbp']:,.0f}",
                "n/a" if pct is None else f"{pct:+.2f}%",
                f"GBP {row['our_gross_margin_gbp']:,.0f}",
                "n/a" if share is None else f"{share:+.1f}%"))
        slope = h["gbp_saved_per_gbp_per_mwh_of_uplift"]
        print("  slope {:<32} {} GBP of household saving per GBP/MWh of uplift".format(
            "", f"{slope['slope']:+.2f}" if slope.get("available") else "n/a"))
    wc = result["world_curve_vs_belief"]
    if wc.get("available"):
        print("  world curve vs belief: {} decision(s) x {} rung(s) = {} paired observation(s)"
              .format(wc["decisions"], wc["observations"] // max(wc["decisions"], 1),
                      wc["observations"]))
        print("    median world/believed slope ratio {}  (pooled {})".format(
            "n/a" if wc["median_world_over_believed"] is None
            else f"{wc['median_world_over_believed']:.3f}",
            "n/a" if wc["pooled"]["world_over_believed"] is None
            else f"{wc['pooled']['world_over_believed']:.3f}"))
        print("    company OVER-predicts the response on {} decision(s), UNDER on {}".format(
            wc["decisions_where_the_company_over_predicts_the_response"],
            wc["decisions_where_the_company_under_predicts_the_response"]))
    else:
        print("  world curve vs belief unavailable: {}".format(wc.get("why_not")))
    rd = result["reference_divergence"]
    if rd.get("available"):
        print("  references  {} of {} decisions disagree in SIGN (company mean {:+.1f}%, "
              "world mean {:+.1f}%)".format(
                  rd["sign_disagreements"], rd["decisions_with_both_references"],
                  rd["mean_rate_increase_pct"], rd["mean_rate_vs_svt_pct"]))
        print("  SVT recon   agrees={} (largest gap {:.4f} pp)".format(
            rd["svt_reconciliation"]["agrees"],
            rd["svt_reconciliation"]["largest_absolute_gap_pct_points"]))
    ud = result["unmatched_diagnosis"]
    print("  unmatched   {} decision(s) on {} account(s): {} account(s) the world never rolled "
          "at all in this window ({}), {} whose world schedule names other months".format(
              ud["unmatched_decisions"], ud["unmatched_accounts"],
              ud["accounts_the_world_never_rolled_at_all_in_window"],
              ", ".join(ud["accounts_the_world_never_rolled_at_all_in_window_named"]) or "none",
              ud["accounts_whose_world_schedule_names_other_months"]))
    print("  wrote {}".format(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
