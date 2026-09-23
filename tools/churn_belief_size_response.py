#!/usr/bin/env python3
"""Does the company's churn belief distinguish households by size, where the world's does?

REUSE: tools/churn_belief_size_response.py
CLASS: SUBSYSTEM
INDEX: searched "churn", "belief", "size", "eac", "consumption", "bill_stress", "heterogeneity",
       "response", "sweep", "multiplier". Four neighbours were read and none is this:
       `tools/renewal_rule_price_response.py` sweeps one input at a time and reports whether the
       PRICE moves; it already lists `eac_kwh` as an input that reaches the price, and that row is
       true through the VOLUME channel of the value objective -- it says nothing about whether the
       CHURN BELIEF hears consumption, which is the question here, and its own docstring disclaims
       book frequency outright ("establishes reachability ... and never frequency").
       `tools/measure_churn_heterogeneity.py` measures the WORLD's per-household hazard as a rank
       statistic (AUC against a within-year null); it grades ordering skill, not whether a term
       exists, and cannot express "flat in this dimension by construction".
       `tools/inside_the_renewal_rule.py::does_size_carry_it` splits belief ERROR by an EAC median
       inside one price band -- a different quantity (error, not response) on a different
       population (the top tercile). `company/analytics/counterfactual_retention.py` scores offers
       against a fixed effectiveness assumption and never touches consumption.
EVALUATED: no library. The knee is found by bisection over a monotone pure function -- eight lines
       -- and the book half is a histogram. scipy.optimize.brentq was considered and rejected: the
       function is piecewise-linear with an exactly-flat left arm, so a root-finder on the
       derivative has no sign change to bracket and bisection on "has the value moved at all"
       is both simpler and the thing actually being asked.
REJECTED: scipy.optimize -- no sign change to bracket on a flat arm; would report the tolerance.

WHY IT EXISTS
-------------
Lane 0 delivery, 2026-09-22: `enriched_churn_estimate(250, 280, 3, eac, segment="resi")` returns
0.166000 for eac in {1500, 3100, 6000, 12000} -- byte-identical -- and 0.436833 at 25000, while
the world's `churn_position_multiplier` runs 1.288 to 11.120 across domestic bills of GBP 600 to
8,000. The item asked three things: where the step is and what makes it, how the real book falls
either side of it, and a published statement of whether the company's belief carries information
in the dimension the world is most sensitive to.

WHAT PRODUCES THE STEP, AND IT IS NOT A BAND WHOSE EDGES ARE WRONG
------------------------------------------------------------------
`estimate_churn_probability` touches `annual_consumption_kwh` in exactly one place:

    prev_annual_bill_gbp = old_rate_gbp_per_mwh * annual_consumption_kwh / 1000.0
    bill_stress = bill_stress_sens * max(0.0, prev_annual_bill_gbp / bill_stress_threshold - 1.0)

That `max(0.0, ...)` is the whole finding. Below the threshold the term is not small, it is
**identically absent**, so the partial derivative of the belief with respect to consumption is
exactly zero there. Three readings were available and only one survives:

  * NOT saturation. The estimate moves freely with price at every consumption, which is what the
    drawn item established by sweeping the offer; a saturated term would flatten both axes.
  * NOT a band whose edges are wrong. Calling it a mis-placed edge implies a tuning fix, and that
    is the flattering reading. `bill_stress` is a FINANCIAL-DISTRESS term -- the module docstring
    says so: *"a customer who spent GBP 11,000/year last year at crisis prices is under more
    financial stress than rate % alone shows"*. Distress above a threshold is a different quantity
    from household size, and the model has no size term at all. Moving the edge would not give it
    one; it would only move where distress starts.
  * NOT an equivalence. The world genuinely responds to size across this book (see `partition`),
    so the flatness is a real difference the belief cannot express, not two routes to one answer.

So: **an absent term**, and the module carries a distress term that happens to take consumption as
its input. The threshold's own position is unsourced -- reported as a field here rather than
repaired, because the knee's position is not what this measures and a number invented to fill a
slot is a finding to file, not a value to re-pick.

THAT WAS TRUE WHEN IT WAS WRITTEN AND IT IS FALSE NOW. 2026-09-23, kept beside itself
--------------------------------------------------------------------------------------
`fc390b918` -- *"the churn belief hears household size now, on a published basis"* -- gave
`estimate_churn_probability` a SECOND route from consumption to the belief: a size term scaling
the rate response by the household's own consumption against the published Ofgem TDCV Medium
band. Everything above is a correct account of the belief as it stood, and the paragraph is kept
rather than overwritten because the prediction it contains is what the landing refuted, and a
prediction quietly revised after its answer is known is not evidence of anything.

What is true now, measured rather than reasoned about, and the working is in the artefact:

  * **There is no knee.** The belief responds to consumption from the first metered kWh at every
    probe rate. `knee_kwh` returns the bottom of its bracket -- the instrument going blind, not a
    knee at 1 kWh -- and `response_breakpoints_kwh` is what answers the question now.
  * **The finding MOVED; it did not close.** This bullet said until 2026-09-23 that which of
    those two it was "depends on a term that is not committed yet" -- the `BILL_STRESS_MAX_RATIO`
    ceiling, then sitting in another lane's working copy of `company/crm/churn_model.py`, with
    which `bill_stress` stops growing and the belief flattens above the higher of the two
    ceilings, and without which `bill_stress` grows unbounded and the belief responds until
    saturation. `3b01193a8` landed it, so the ambiguity is spent: the two trees are one tree and
    the ceilinged reading is the only one there is. The belief is deaf to household size for a
    handful of DOMESTIC legs and they are the BIGGEST households on the book -- deaf across the
    top of it where it used to be deaf across the bottom. **The count is deliberately not written
    here.** It is a property of the book the run reads and it moved 7 -> 10 on the arms' book
    between two runs a day apart with nothing about the model changing; `reading()` composes the
    deafness clause from the per-run census for the same reason, and an earlier draft of this
    file hard-coded the ceilinged version while the ceiling was uncommitted and would have
    published a sentence true of no commit.
  * **The asymmetry did NOT invert, and I predicted that it had.** Written here because the
    prediction was made in this file before `partition` was re-run and the run refuted it.
    `the_belief_varies_where_the_world_does_not` is still `True`: `bill_stress` still reaches SME,
    the world's `bill_scale_for` still returns `None` off-domestic, and neither of those is what
    `fc390b918` touched. What actually changed is weaker and is the accurate claim -- the belief
    now varies with size in the domestic segment TOO, so that field is no longer the sharp
    "exactly where the world does not" it was published as. It is a true statement about SME that
    used to also be an exhaustive one and is not any more. The sentence the page renders no longer
    makes the exhaustive claim; the field keeps reporting its own live value.

The BILL_STRESS paragraph above still describes `bill_stress`, which is untouched by the landing.
What changed is that it is no longer the only thing the belief hears consumption through, which
is why a probe built to find its knee can no longer see it.

WHAT CHANGED UNDER THAT SENTENCE, 2026-09-22, and it is corrected here beside itself rather than
over it. This paragraph used to ground the field on `BILL_STRESS_THRESHOLD_GBP` being "on this
repo's own no-origin debt list (`tools/domain_constant_origins --list`)". **It is no longer on that
list**, so that ground is gone -- but the FIELD's verdict is unchanged, because what the constant
now carries is a NAMED GAP and not a source. The pass that went looking found that no published
source gives a bill level at which GB domestic switching activity rises, and that the closest one
refutes the SHAPE: Ofgem/BMG *Understanding Consumers' Energy Tariff Choices* (n=3,235, Mar-Apr
2024) puts the SPEND-to-switching correlation at -0.07 to +0.05. So "unsourced" is still the right
word for the LEVEL and 3,000 was deliberately not re-picked. Reading, and the seven places searched
first: `docs/market_research/is_there_a_bill_level_at_which_switching_rises.md`.

THE KNEE IS IN POUNDS, NOT KILOWATT-HOURS, AND THAT MATTERS
------------------------------------------------------------
The drawn item read the step as sitting "somewhere above 12,000 kWh". 12,000 kWh is where it sits
*at an old rate of GBP 250/MWh only*: the threshold is GBP 3,000 of PREVIOUS ANNUAL BILL, so the
kWh location moves with price -- 20,250 kWh at GBP 150/MWh, 7,750 at GBP 400/MWh. A control keyed
to 12,000 kWh would go red the next time the price deck moves and green while the mechanism rotted.
`knee` is therefore DERIVED by bisection from the estimator itself at each probe rate, and the
constant is reported beside it as a cross-check rather than as the answer.

WHICH BOOK THE DISTRIBUTION DESCRIBES, AND HOW THE 154-ACCOUNT ONE WAS FINALLY REACHED
---------------------------------------------------------------------------------------
The item asked for the EAC distribution of the 154 settled billing accounts behind
`site/data/value_arms.json`. The first pass of this module recorded that as NOT ESTABLISHED, on
the ground that the per-account rows are not persisted and reconstructing them means re-running
the arms. **That premise was wrong, and it was wrong in the cheap direction: the rows are
persisted, in git.** `site/data/customers.json` is one row per billing account, it is regenerated
each run, and the run artefact records the commit the arms were drawn at
(`producing_commit.commit`). `git show <that commit>:site/data/customers.json` is the book itself.
No re-run, and no reconstruction -- the bytes the run was reading.

IT IS RECONCILED BEFORE IT IS BELIEVED, and the reconciliation is the control. A commit-pinned
blob is only the right book if it IS the right book, and "the roster at the commit the code was
bound at" is an inference, not an observation. So `arms_book` checks the four counts the run
independently recorded in `book_identity` -- accounts, electricity legs, gas legs, dual fuel --
against the four counts computed from the blob, and REFUSES with the mismatching field named if
any disagree. All four agree exactly (154 / 136 / 90 / 72), which is what makes this the arms'
own book rather than a roster of about the right size. The book at HEAD has drifted to 164
accounts and 244 legs since, so the check is not decorative: pointing this at the current file
would have silently measured a different population, which is precisely the failure the first
pass was being careful about.

Both distributions are published. `book` is the tree's current book; `arms_book` is the one the
published arms were scored over, and it is the one the page quotes.

R12: diagnostic, never a target. This measures whether a belief carries information in a
dimension; it is not an instruction to make it vary, and nothing here should be read as one. The
epistemic wall is untouched either way -- a real supplier meters its own customers, and the
world's own `churn_position_multiplier` says so in terms: *"consumption is OBSERVABLE to a
supplier, so unlike the hidden sensitivity axis it is something the company can legitimately act
on."*
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from company.crm.churn_model import (
    BILL_STRESS_SENSITIVITY,
    BILL_STRESS_THRESHOLD_GBP,
    estimate_churn_probability,
)
from company.crm.enriched_churn_estimate import enriched_churn_estimate
from simulation.market_switching_propensity import bill_scale_for, churn_position_multiplier
from tools.couple_value_based_pricing import BILLS_PER_YEAR, BOOK_PATH

PROJECT = Path(__file__).resolve().parent.parent
DEFAULT_ARTEFACT = PROJECT / "docs" / "observability" / "churn_belief_size_response.json"

#: The price differential the world's multiplier is read at. 12% is the drawn item's own probe and
#: is kept so this artefact and the item's four lines describe one reading. It is a PROBE POSITION,
#: not a claim about what this company charges -- every figure keyed to it says so.
PROBE_DIFFERENTIAL_PCT: float = 0.12

#: The rates the knee is derived at. Three, spanning the deck this book was actually billed
#: across, because the whole point of deriving is that one rate cannot show the knee is in pounds.
PROBE_RATES_GBP_PER_MWH: tuple[float, ...] = (150.0, 250.0, 400.0)

#: Where to stop bisecting for the knee, in kWh. One kWh is far below any bill this resolves.
_KNEE_TOLERANCE_KWH: float = 1.0


def knee_kwh(old_rate_gbp_per_mwh: float, *, segment: str = "resi",
             fuel: str = "electricity", hi_kwh: float = 500_000.0) -> float | None:
    """The consumption at which the belief FIRST MOVES, found from the estimator, not asserted.

    Bisection on "is the estimate still equal to its value at zero consumption". Returns None when
    the estimate never moves across the whole bracket -- which is the correct answer for a segment
    with the bill-stress sensitivity switched off (I&C), and is a reachable branch rather than a
    defensive one: `IC_BILL_STRESS_SENSITIVITY` is 0.0.

    THIS PROBE WENT BLIND ON 2026-09-23 AND ITS ANSWER MUST NOT BE READ AS A KNEE. Said here, at
    the function, because the number it returns is still a float and still looks like one. It asks
    "where does the belief FIRST depart from its value at zero consumption", which located
    `bill_stress`'s knee only while `bill_stress` was the ONLY route from consumption to the
    belief. `fc390b918` added a second, sourced route -- a size term on the rate response -- so the
    belief now departs from flat at the bottom of any bracket and this returns
    `_KNEE_TOLERANCE_KWH` at every rate. That is not "the knee moved to 1 kWh"; it is this
    instrument no longer being able to see a knee at all. `response_breakpoints_kwh` is what
    answers the original question now, because a kink is still a kink once the arm below it stops
    being flat -- and `knee()` reports both so the blindness is on the artefact rather than in a
    reader's head.
    """
    rate = float(old_rate_gbp_per_mwh)
    offer = rate * 1.12

    def p(kwh: float) -> float:
        return estimate_churn_probability(rate, offer, 3.0, kwh, fuel=fuel, segment=segment)

    flat = p(0.0)
    if p(hi_kwh) == flat:
        return None
    lo, hi = 0.0, hi_kwh
    while hi - lo > _KNEE_TOLERANCE_KWH:
        mid = (lo + hi) / 2.0
        if p(mid) == flat:
            lo = mid
        else:
            hi = mid
    return hi


#: The finite-difference step the slope is read at, in kWh, and the grid the scan walks. The belief
#: is piecewise-LINEAR in consumption -- every term it reads consumption through is a ratio, a
#: `max` or a `min` -- so a slope read anywhere inside a piece is the whole piece's slope and the
#: only question is whether the grid can straddle two breakpoints at once. The narrowest gap any
#: probe rate produces is 1,500 kWh (400 GBP/MWh: the bill knee at 7,500 and its ceiling at 8,500),
#: six grid steps, so it cannot.
_SLOPE_PROBE_KWH: float = 1.0
_BREAKPOINT_SCAN_KWH: float = 250.0
#: Two slopes count as one slope below this. Read against the live values rather than picked: the
#: slopes this separates are 0.0 and 0.0125-0.0717 per 1,000 kWh, nine orders of magnitude clear.
_SLOPE_EQUAL: float = 1e-12

#: WHERE THE PIECEWISE-LINEAR ASSUMPTION STOPS HOLDING, AND THIS IS A REAL BOUND ON THE
#: INSTRUMENT RATHER THAN A DEFENSIVE CAP. `_saturate_churn_probability` is a SMOOTH function, not
#: a hard clamp, so once a belief is large enough to be inside it the composition is CURVED and
#: every grid step registers a fresh slope change. Measured, not reasoned about: at HEAD's model,
#: probing 250 GBP/MWh past ~33,400 kWh yields 68 "breakpoints" in a row, one per grid step, all
#: of them the curve and none of them a term switching. A scan that reported those would publish
#: an instrument artefact as a property of the belief.
#:
#: FOUR IS THE HONEST CEILING: the belief has at most three terms that can kink in consumption
#: (the size term's cap, `bill_stress`'s knee, and its own ceiling where one is configured), so a
#: FOURTH is already evidence the scan has walked into the curve. `knee()` reports whether the cap
#: bound, so a reader is never shown a truncated list as though it were complete.
_MAX_BREAKPOINTS: int = 4


def response_breakpoints_kwh(old_rate_gbp_per_mwh: float, *, segment: str = "resi",
                             fuel: str = "electricity", lo_kwh: float = 1.0,
                             hi_kwh: float = 50_000.0) -> list[float]:
    """Every consumption at which the belief's RESPONSE to consumption changes, in order.

    WHY THIS REPLACES `knee_kwh` AS THE INSTRUMENT AND NOT AS A SECOND OPINION. The question this
    module exists to answer -- "does the belief distinguish households by size, and where does that
    stop" -- was answerable by bisecting on "has the value moved at all" only while the belief had
    exactly one consumption term with a flat arm underneath it. It has three routes now, and a
    departure-from-flat probe answers about whichever starts lowest while saying nothing about the
    other two. A KINK is what a term switching on or saturating actually is, and a kink survives
    having a sloped arm underneath it, so this asks the same question of a belief that changed
    shape rather than a different question of the same belief.

    IT FINDS SATURATIONS AS WELL AS SWITCH-ONS, DELIBERATELY. A breakpoint where the slope drops to
    zero is the belief going deaf to size above that consumption, which is the same defect the old
    reading named and it is now at the TOP of the book rather than the bottom. Reporting only
    switch-ons would publish the flattering half.

    Returns [] when the belief is linear in consumption across the whole bracket -- reachable, and
    it is what a segment with no size term and no bill stress returns (`SME`, I&C).

    THE SCAN STARTS ABOVE ZERO AND THE REASON IS NOT TIDINESS. `estimate_churn_probability` guards
    its size term with `annual_consumption_kwh > 0` and hands the zero case an UNSCALED 1.0, on
    purpose -- "an account with no consumption on record gets the unscaled response rather than a
    guessed one". That is a genuine discontinuity at exactly 0, and a scan whose left edge is 0
    straddles it and reports a breakpoint at 1 kWh at every rate. It is real and it is not a size
    response: it separates KNOWN-AND-TINY from NOT-KNOWN, which is a different question from the
    one this asks. Starting at `lo_kwh` reports the belief's response over consumptions the company
    has actually metered, and the zero branch is controlled where it belongs, in the churn model's
    own tests.
    """
    rate = float(old_rate_gbp_per_mwh)
    offer = rate * 1.12

    def slope(kwh: float) -> float:
        here = estimate_churn_probability(
            rate, offer, 3.0, kwh, fuel=fuel, segment=segment)
        there = estimate_churn_probability(
            rate, offer, 3.0, kwh + _SLOPE_PROBE_KWH, fuel=fuel, segment=segment)
        return (there - here) / _SLOPE_PROBE_KWH

    found: list[float] = []
    left, left_slope = float(lo_kwh), slope(float(lo_kwh))
    probe = float(lo_kwh) + _BREAKPOINT_SCAN_KWH
    while probe <= hi_kwh and len(found) < _MAX_BREAKPOINTS:
        here_slope = slope(probe)
        if abs(here_slope - left_slope) > _SLOPE_EQUAL:
            lo, hi = left, probe
            while hi - lo > _KNEE_TOLERANCE_KWH:
                mid = (lo + hi) / 2.0
                if abs(slope(mid) - left_slope) <= _SLOPE_EQUAL:
                    lo = mid
                else:
                    hi = mid
            found.append(round(hi, 1))
            left_slope = here_slope
        left = probe
        probe += _BREAKPOINT_SCAN_KWH
    return found


def knee() -> dict:
    """Where the belief's response to household size starts, stops and saturates, at each rate.

    RE-DERIVED 2026-09-23, AND THE ANSWER INVERTED RATHER THAN THE QUESTION CHANGING. What this
    returned until today was the position of a single step and a verdict that the step was at a
    fixed BILL and a moving kWh. `fc390b918` landed a sourced size term on the rate response, so
    there is no single step any more: the belief responds to consumption from the first metered
    kWh, and what it does instead is go DEAF above a saturation this reports. The module's question
    -- does the belief distinguish households by size, where the world's does -- is unchanged, so
    the instrument is re-derived to keep answering it and not re-pointed at something easier.

    THE OLD FIELDS ARE WITHDRAWN BY NAME, NOT DELETED. `the_knee_is_a_bill_not_a_consumption` and
    `kwh_spread_across_the_probe_rates` were the framing every rendered sentence rested on, and a
    consumer that stops finding them can tell "this measurement was withdrawn and here is what
    replaced it" from "the artefact is malformed" only if the withdrawal says so in the artefact.
    They carry `None` and a reason rather than a number that would still parse.
    """
    rows = []
    for rate in PROBE_RATES_GBP_PER_MWH:
        breaks = response_breakpoints_kwh(rate)
        first_move = knee_kwh(rate)
        # A FLAT BAND IS NOT A DEAF EDGE, AND THE FIRST DRAFT OF THIS CONFLATED THEM. It walked
        # the breakpoints from the top and took the first one with a zero slope above it, which
        # at HEAD's model returns the size term's cap (9,999 kWh) -- and the belief starts
        # responding again 2,000 kWh higher when `bill_stress` switches on. "Stops responding
        # above 9,999 kWh" would have been published, and it is false: what sits there is a flat
        # BAND between two terms, not the end of the belief's hearing. Caught by running the
        # producer against HEAD as well as against the working tree and reading the sentence.
        #
        # SO THE EDGE IS TERMINAL BY CONSTRUCTION: only the LAST breakpoint can be one, and only
        # when the belief never moves again above it. When the scan hit its cap the list is
        # truncated and the last entry is not known to be last, so no edge is claimed.
        deaf_above = None
        if breaks and len(breaks) < _MAX_BREAKPOINTS:
            offer = rate * 1.12
            top = breaks[-1]
            probes = [top + step for step in (10.0, 100.0, 1_000.0, 5_000.0)]
            flat_above = all(
                estimate_churn_probability(rate, offer, 3.0, kwh)
                == estimate_churn_probability(rate, offer, 3.0, top + 1.0)
                for kwh in probes)
            if flat_above:
                deaf_above = top
        rows.append({
            "old_rate_gbp_per_mwh": rate,
            "response_breakpoints_kwh": breaks,
            "the_belief_goes_deaf_to_size_above_kwh": deaf_above,
            "the_deaf_edge_as_a_bill_gbp": (
                None if deaf_above is None else round(rate * deaf_above / 1000.0, 1)),
            "first_departure_from_flat_kwh": (
                None if first_move is None else round(first_move, 1)),
        })
    deaf = [r["the_belief_goes_deaf_to_size_above_kwh"] for r in rows
            if r["the_belief_goes_deaf_to_size_above_kwh"]]
    return {
        "available": bool(rows),
        "by_rate": rows,
        # THE PROPERTY, ANSWERED, NOT ASSUMED EITHER WAY. This is the field a control keys to, and
        # it is written so that it can say YES again: if the size term were removed the belief
        # would be flat below a knee once more and this would return True without an edit.
        "the_belief_is_flat_below_a_knee": all(
            r["first_departure_from_flat_kwh"] is not None
            and r["first_departure_from_flat_kwh"] > _KNEE_TOLERANCE_KWH * 2.0
            for r in rows),
        "the_belief_goes_deaf_above_a_saturation": bool(deaf) and len(deaf) == len(rows),
        # WHERE THE DEAFNESS SITS IN kWh ACROSS THE DECK. The old `kwh_spread` asked this of the
        # switch-ON edge; the same question of the switch-OFF edge is what is load-bearing now,
        # and it is still the test of whether the edge is a consumption or a price artefact.
        "deaf_edge_kwh_spread_across_the_probe_rates": (
            None if len(deaf) < 2 else round(max(deaf) / min(deaf), 2)),
        "the_knee_is_a_bill_not_a_consumption": None,
        "kwh_spread_across_the_probe_rates": None,
        "what_was_withdrawn_and_why": (
            "WITHDRAWN 2026-09-23, not failed. `the_knee_is_a_bill_not_a_consumption` and "
            "`kwh_spread_across_the_probe_rates` both described a single step at which the "
            "belief's response to household size BEGAN, and there is no such step any more: "
            "`fc390b918` gave `estimate_churn_probability` a size term sourced to Ofgem/BMG "
            "*Understanding Consumers' Energy Tariff Choices*, so the belief responds to "
            "consumption from the first metered kWh at every rate. The probe that found the old "
            "step, `knee_kwh`, now returns the bottom of its bracket at every rate -- which is "
            "the instrument going blind, NOT the knee moving to 1 kWh. What replaced them is "
            "`response_breakpoints_kwh` and `the_belief_goes_deaf_to_size_above_kwh`: "
            "`bill_stress` and its published ceiling are both still in the model and both still "
            "make kinks, so the same question is still answerable -- it is asked of a kink now "
            "rather than of a departure from flat."),
        "declared_threshold_gbp": BILL_STRESS_THRESHOLD_GBP,
        "declared_sensitivity": BILL_STRESS_SENSITIVITY,
        # NOT ESTABLISHED, AND THAT IS STILL THE VERDICT — but as of 2026-09-22 it is a verdict
        # with a reason rather than the absence of one, so this sentence changed and the door leg
        # over it was re-derived rather than re-pointed. What the page must not do is let a reader
        # take 3,000 as established; what it now also does is say what the looking FOUND.
        "the_thresholds_own_origin": (
            "NOT ESTABLISHED, and now for a stated reason rather than for none. No published "
            "source gives a bill level at which GB domestic switching activity rises: Ofgem "
            "publishes switching cut seven ways -- tariff type, payment method, supplier size, "
            "debt, bill difficulty, satisfaction and prior switching -- and never by bill size. "
            "What IS established refutes the SHAPE rather than the level. Ofgem/BMG "
            "\"Understanding Consumers' Energy Tariff Choices\" (n=3,235, fieldwork Mar-Apr 2024) "
            "puts the correlation between a household's energy SPEND and its switching propensity "
            "at -0.07 to +0.05, a band that does not clear zero in either direction, and reports "
            "that spending has \"a very limited impact on how consumers evaluate prospective "
            "deals\". A knee asserts the strongest available form of dependence on that variable "
            "-- identically absent below, rising above -- and the closest published source puts "
            "the dependence at approximately none. So the term selects on CONSUMPTION, not "
            "distress, which is why its position in kWh moves 4.1x across the price record with "
            "nothing about any household changing. 3,000 stands as a NAMED GAP, not re-picked: "
            "every candidate would be chosen for how many of this book's legs it puts either side "
            "of it, which is goal-seeking against a published figure. The working, and the seven "
            "places searched first, are in "
            "docs/market_research/is_there_a_bill_level_at_which_switching_rises.md."),
        "what_the_term_is": (
            "A SOURCED SIZE TERM WITH A CEILING, where until 2026-09-23 there was no size term at "
            "all. `estimate_churn_probability` now reads consumption twice. First through "
            "`size_scale = min(own_kwh / reference_kwh, MAX_SIZE_SCALE)`, which multiplies the "
            "RATE RESPONSE -- the same percentage is worth more pounds to a bigger household, "
            "which Ofgem/BMG \"Understanding Consumers' Energy Tariff Choices\" (n=3,235) "
            "establishes positively, and the reference is the published Ofgem TDCV Medium band "
            "rather than a picked number. Second through `bill_stress`, unchanged and still "
            "identically zero below its declared threshold and now CEILINGED above it: "
            "`bill_stress = min(sens * max(0, prev_annual_bill / threshold - 1), base_rate * "
            "(BILL_STRESS_MAX_RATIO - 1))`, where `BILL_STRESS_MAX_RATIO` is Ofgem CIM wave 6 "
            "Table 56's arrears-banner switching rate over the population rate -- the only "
            "published measurement of distress-driven switching, and a bound on a term whose "
            "SHAPE the same evidence refutes. So the belief is no longer flat in household size, "
            "and the defect the old reading named has MOVED rather than closed: `size_scale` "
            "saturates at MAX_SIZE_SCALE and `bill_stress` saturates at that ceiling, so above "
            "the top of those two the derivative returns to exactly zero. The belief is now deaf "
            "to size at the TOP of this book instead of across the bottom of it, and that is a "
            "smaller population and a different remedy."),
    }


def _leg_rows(book: dict) -> list[dict]:
    """Each supply leg's annual consumption and an UPPER BOUND on the bill the model reads.

    THE BOUND IS DELIBERATE AND ITS DIRECTION IS THE FAIL-CLOSED ONE. The model's input is
    `old_rate * eac / 1000` where `old_rate` is the realised rate with the STANDING CHARGE taken
    back out (`value_based_renewal._observed_renewal_history`), and this feed does not separate
    the standing charge from revenue. Taking the whole bill therefore OVERSTATES the model's
    input, which can only move legs INTO the above-knee set. The load-bearing claim here is the
    count BELOW the knee, so overstating is the direction that cannot flatter it.
    """
    rows = []
    for customer in book.get("customers") or []:
        segment = customer.get("segment")
        for fuel, leg in (customer.get("legs") or {}).items():
            if not leg.get("cid"):
                continue
            years = max(1.0, float(leg.get("bill_count") or 0.0) / BILLS_PER_YEAR)
            kwh = float(leg.get("total_kwh") or 0.0) / years
            if kwh <= 0.0:
                continue
            revenue = float(leg.get("revenue_gbp") or 0.0) / years
            rate = float(leg.get("avg_effective_rate_gbp_per_mwh") or 0.0)
            rows.append({
                "cid": leg["cid"], "segment": segment, "fuel": fuel,
                "annual_kwh": kwh,
                "bill_upper_bound_gbp": max(revenue, rate * kwh / 1000.0),
            })
    return rows


def _household_bills(book: dict) -> dict:
    """cid -> the household's whole annual spend across its legs.

    Deliberately NOT imported from `couple_value_based_pricing._household_annual_bill_gbp`
    despite computing the same thing: that function drops a household whose legs carry no revenue
    (absent rather than zero, for a reason its own docstring gives), and a census that must count
    every leg on one side of a line or the other cannot silently lose one. The difference is
    reported as `households_without_a_bill` rather than hidden.
    """
    out: dict[str, float] = {}
    for customer in book.get("customers") or []:
        legs = [leg for leg in (customer.get("legs") or {}).values() if leg.get("cid")]
        total = 0.0
        for leg in legs:
            years = max(1.0, float(leg.get("bill_count") or 0.0) / BILLS_PER_YEAR)
            total += float(leg.get("revenue_gbp") or 0.0) / years
        for leg in legs:
            out[leg["cid"]] = total
    return out


def _quantiles(values: list[float]) -> dict:
    ordered = sorted(values)
    if not ordered:
        return {}
    at = lambda q: ordered[int(q * (len(ordered) - 1))]  # noqa: E731
    return {"min": round(ordered[0], 1), "p10": round(at(0.10), 1), "p50": round(at(0.50), 1),
            "p90": round(at(0.90), 1), "max": round(ordered[-1], 1)}


def partition(below_kwh: float = 3_000.0, above_kwh: float = 25_000.0,
              old_rate: float = 250.0) -> dict:
    """The belief and the world, at one household below the knee and one above it.

    THE WHOLE PARTITION IN ONE PLACE, because a reading that only shows the flat arm is
    indistinguishable from an instrument that reports "flat" for everything. Both arms, both
    sides, and the world beside the belief at each.
    """
    offer = old_rate * 1.12

    def row(kwh: float, segment: str) -> dict:
        bill = old_rate * kwh / 1000.0
        return {
            "annual_kwh": kwh, "segment": segment,
            "prev_annual_bill_gbp": round(bill, 2),
            "company_belief": round(enriched_churn_estimate(
                old_rate, offer, 3.0, kwh, segment=segment), 6),
            "world_multiplier": round(churn_position_multiplier(
                PROBE_DIFFERENTIAL_PCT, bill_scale_for(segment, bill)), 6),
            "world_reads_this_households_own_bill": bill_scale_for(segment, bill) is not None,
        }

    resi_below, resi_above = row(below_kwh, "resi"), row(above_kwh, "resi")
    sme_below, sme_above = row(below_kwh, "SME"), row(above_kwh, "SME")
    return {
        "available": True,
        "probed_at_old_rate_gbp_per_mwh": old_rate,
        "probed_at_price_differential_pct": PROBE_DIFFERENTIAL_PCT,
        "resi": {"below_the_knee": resi_below, "above_the_knee": resi_above,
                 "belief_moves": resi_below["company_belief"] != resi_above["company_belief"],
                 "world_moves": resi_below["world_multiplier"] != resi_above["world_multiplier"]},
        "sme": {"below_the_knee": sme_below, "above_the_knee": sme_above,
                "belief_moves": sme_below["company_belief"] != sme_above["company_belief"],
                "world_moves": sme_below["world_multiplier"] != sme_above["world_multiplier"]},
        # THE FINDING IN ONE LINE, AND IT IS SHARPER THAN "THE BELIEF IS FLAT". The world scales
        # by the household's OWN bill for domestic supply only; `bill_scale_for` returns None for
        # every non-domestic segment, so the world is flat in size there BY CONSTRUCTION and says
        # why (a domestic switching curve ran 599x past its evidence on an industrial site). The
        # company's belief is the mirror image of that: deaf to size exactly where the world
        # listens hardest, and the one segment where it does vary is the one the world ignores.
        "the_belief_varies_where_the_world_does_not": (
            sme_below["company_belief"] != sme_above["company_belief"]
            and sme_below["world_multiplier"] == sme_above["world_multiplier"]),
    }


def _legs_the_belief_is_deaf_to(rows: list[dict]) -> dict:
    """How many of this book's legs the belief CANNOT hear the size of, each at its OWN rate.

    THE DIRECT SUCCESSOR TO `legs_below_the_knee`, AND THE COUNT IT REPLACES IS THE SAME CLAIM.
    "The belief is flat in household size for N of this book's M legs" is what this module has
    always published; until 2026-09-23 the N could be got from a single knee bill because there
    was a single knee. There is not one now -- the saturation that makes the belief deaf sits at a
    different consumption at every rate (the bill-stress ceiling moves with the price deck, the
    size ceiling does not) -- so the only honest way to count is to ask the estimator itself, once
    per leg, at the rate that leg was actually billed at.

    ASKED AS A DERIVATIVE, NOT AS A COMPARISON AGAINST AN EDGE. `belief(kwh + 1) == belief(kwh)`
    is the property the sentence claims; deriving each leg's edge and then comparing would put a
    second implementation of the saturation rule here, which is the VAT-rule shape CLAUDE.md names.
    """
    deaf, heard = [], 0
    for r in rows:
        if r["annual_kwh"] <= 0:
            continue
        rate = r["bill_upper_bound_gbp"] / r["annual_kwh"] * 1000.0
        if rate <= 0:
            continue
        offer, kwh = rate * 1.12, r["annual_kwh"]
        here = estimate_churn_probability(
            rate, offer, 3.0, kwh, fuel=r["fuel"], segment=r["segment"])
        there = estimate_churn_probability(
            rate, offer, 3.0, kwh + 1.0, fuel=r["fuel"], segment=r["segment"])
        if here == there:
            deaf.append(r)
        else:
            heard += 1
    return {
        "legs_graded": heard + len(deaf),
        "legs_the_belief_hears": heard,
        "legs_the_belief_is_deaf_to": len(deaf),
        "share_the_belief_hears": (
            round(heard / (heard + len(deaf)), 4) if (heard + len(deaf)) else None),
        "deaf_leg_annual_kwh": _quantiles([r["annual_kwh"] for r in deaf]),
        # THE FLAG MEANS WHAT THE SENTENCE SAYS, WHICH IT DID NOT ON ITS FIRST DRAFT. It was
        # `min(deaf) > p50`, and the words it licenses are "the largest households on the book" --
        # a set sitting anywhere in the upper half clears that test while containing none of the
        # biggest accounts. Measured at HEAD's model the deaf set is a flat BAND at 10,000-12,000
        # kWh on a book whose largest leg is 40,654, and the old flag called it "the largest".
        # The claim is now what it says: the deaf set reaches the top of the book.
        "the_deaf_legs_are_the_BIGGEST": bool(deaf) and max(
            r["annual_kwh"] for r in deaf) >= max(
                r["annual_kwh"] for r in rows if r["annual_kwh"] > 0),
        "the_deaf_legs": [
            {"cid": r["cid"], "segment": r["segment"], "fuel": r["fuel"],
             "annual_kwh": round(r["annual_kwh"], 0),
             "bill_upper_bound_gbp": round(r["bill_upper_bound_gbp"], 0)}
            for r in sorted(deaf, key=lambda x: -x["annual_kwh"])],
        "each_leg_at_its_own_rate": (
            "Each leg is probed at the rate it was billed at (its own revenue over its own kWh), "
            "not at a common probe rate. The bill-stress ceiling that makes the belief deaf sits "
            "at a consumption set by the price deck, so a common rate would put the whole book on "
            "one side of an edge no household is actually on."),
    }


def book_distribution(book: dict, knee_bill_gbp: float) -> dict:
    """How many of this book's legs sit either side of the knee, and the world's spread over it."""
    rows = _leg_rows(book)
    bills = _household_bills(book)
    above = [r for r in rows if r["bill_upper_bound_gbp"] > knee_bill_gbp]
    below = [r for r in rows if r["bill_upper_bound_gbp"] <= knee_bill_gbp]
    multipliers = []
    no_bill = 0
    for r in rows:
        household = bills.get(r["cid"])
        if not household:
            no_bill += 1
            continue
        multipliers.append(churn_position_multiplier(
            PROBE_DIFFERENTIAL_PCT, bill_scale_for(r["segment"], household)))
    by_segment = {}
    for segment in sorted({r["segment"] for r in rows if r["segment"]}):
        seg_rows = [r for r in rows if r["segment"] == segment]
        by_segment[segment] = {
            "legs": len(seg_rows),
            "above_the_knee": sum(1 for r in seg_rows
                                  if r["bill_upper_bound_gbp"] > knee_bill_gbp),
            "world_reads_their_own_bill": bill_scale_for(segment, 1000.0) is not None,
        }
    return {
        "available": bool(rows),
        "source": str(BOOK_PATH.relative_to(PROJECT)),
        "billing_accounts": len(book.get("customers") or []),
        "supply_legs": len(rows),
        "legs_above_the_knee": len(above),
        "legs_below_the_knee": len(below),
        "share_below_the_knee": round(len(below) / len(rows), 4) if rows else None,
        "households_without_a_bill": no_bill,
        "knee_used_gbp": round(knee_bill_gbp, 1),
        "leg_annual_bill_gbp": _quantiles([r["bill_upper_bound_gbp"] for r in rows]),
        "leg_annual_kwh": _quantiles([r["annual_kwh"] for r in rows]),
        "world_multiplier_over_this_book": _quantiles(multipliers),
        "world_multiplier_spread": (
            round(max(multipliers) / min(multipliers), 2) if multipliers else None),
        "by_segment": by_segment,
        # THE COUNT THE PUBLISHED SENTENCE IS MADE OF, from 2026-09-23. `legs_below_the_knee`
        # above is still computed and still true of the bill-stress threshold, but it is no
        # longer the count of legs whose size the belief cannot hear -- that is this block.
        "size_deafness": _legs_the_belief_is_deaf_to(rows),
        "the_legs_above_the_knee": [
            {"cid": r["cid"], "segment": r["segment"], "fuel": r["fuel"],
             "annual_kwh": round(r["annual_kwh"], 0),
             "bill_upper_bound_gbp": round(r["bill_upper_bound_gbp"], 0)}
            for r in sorted(above, key=lambda x: -x["bill_upper_bound_gbp"])],
        "bill_is_an_upper_bound": (
            "Each leg's bill here is its whole annual revenue, standing charge included; the "
            "model's own input takes the standing charge back out. So this OVERSTATES the model's "
            "input and can only move legs INTO the above-knee set -- the claim that "
            "{} legs sit below it is safe in the direction it is made.".format(len(below))),
        "population_is_not_the_published_arms_book": (
            "THIS IS THE BOOK THE TREE HOLDS NOW, NOT THE ONE THE PUBLISHED ARMS WERE SCORED "
            "OVER. The arms' own book is measured separately in `arms_book`, read from this same "
            "file at the commit the run recorded, and it is the one the page quotes. Keep both: "
            "the two populations differ (164 accounts here against 154 there), so a single figure "
            "would have to pick one silently."),
    }


#: The four counts the AB run recorded about its own book, which `arms_book` reconciles the
#: commit-pinned roster against before believing it is that book. Named here rather than inline
#: because the whole weight of the arms-book claim rests on this list being the FULL set of
#: independent counts the run published -- a subset would be a weaker check wearing the same name.
_BOOK_IDENTITY_COUNTS: tuple[tuple[str, str], ...] = (
    ("billing_accounts_settled_in_window", "billing_accounts"),
    ("with_an_electricity_leg", "with_an_electricity_leg"),
    ("with_a_gas_leg", "with_a_gas_leg"),
    ("dual_fuel", "dual_fuel"),
)


def _roster_counts(book: dict) -> dict:
    """The four `book_identity` counts, recomputed from a roster blob."""
    customers = book.get("customers") or []

    def _has(customer: dict, fuel: str) -> bool:
        return bool(((customer.get("legs") or {}).get(fuel) or {}).get("cid"))

    return {
        "billing_accounts": len(customers),
        "with_an_electricity_leg": sum(1 for c in customers if _has(c, "electricity")),
        "with_a_gas_leg": sum(1 for c in customers if _has(c, "gas")),
        "dual_fuel": sum(1 for c in customers
                         if _has(c, "electricity") and _has(c, "gas")),
    }


def _roster_at_commit(commit: str) -> dict | None:
    """`site/data/customers.json` as it stood at `commit`, or None if git cannot supply it.

    READ-ONLY BY CONSTRUCTION -- `git show` of a blob touches neither the index nor the worktree,
    which is what makes this safe to call from a generator that several lanes run concurrently.
    """
    try:
        raw = subprocess.run(
            ["git", "show", "{}:{}".format(commit, BOOK_PATH.relative_to(PROJECT).as_posix())],
            cwd=PROJECT, capture_output=True, text=True, timeout=60, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    if raw.returncode != 0 or not raw.stdout.strip():
        return None
    try:
        return json.loads(raw.stdout)
    except json.JSONDecodeError:
        return None


def arms_book(knee_bill_gbp: float) -> dict:
    """How the 154 accounts the PUBLISHED arms were scored over fall either side of the knee.

    FAILS CLOSED, and every refusal names the field that caused it. The chain has four places it
    can break -- no run artefact, no recorded commit, git cannot produce the blob, or the blob
    disagrees with the run's own counts -- and a reader who cannot tell which one fired is being
    handed an absence dressed as a measurement.

    THE RECONCILIATION IS NOT A FORMALITY. `producing_commit.commit` is the commit the run's
    Python modules were bound at, which is an excellent reason to believe the roster at that
    commit is the run's roster and is not an observation of it. The run separately published four
    counts about its own book; recomputing those four from the blob and requiring all four to
    agree is what turns the inference into evidence. They do agree (154 / 136 / 90 / 72) against a
    current book of 164 / 146 / 98 / 80, so the check distinguishes the two populations it exists
    to distinguish.
    """
    from tools.generate_value_arms_data import THREE_ARM_PATH

    def _refuse(why: str) -> dict:
        return {"available": False, "unavailable_because": why}

    if not THREE_ARM_PATH.exists():
        return _refuse(
            "no run artefact at `{}`, so which book the published arms were scored over is not "
            "recorded anywhere this can read".format(THREE_ARM_PATH.relative_to(PROJECT)))
    try:
        run = json.loads(THREE_ARM_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return _refuse("the run artefact could not be read ({})".format(exc.__class__.__name__))

    commit = ((run.get("producing_commit") or {}).get("commit") or "").strip()
    if not commit:
        return _refuse(
            "the run artefact records no `producing_commit.commit`, so there is no commit to read "
            "the book at -- the run did not say which code drew it")

    identity = (run.get("book_identity") or {}).get("control_arm") or {}
    missing = [field for field, _ in _BOOK_IDENTITY_COUNTS if identity.get(field) is None]
    if missing:
        return _refuse(
            "the run recorded no {} for its own book, so the roster at {} cannot be reconciled "
            "against it and would be believed on the commit alone".format(
                ", ".join("`{}`".format(f) for f in missing), commit[:9]))

    roster = _roster_at_commit(commit)
    if roster is None:
        return _refuse(
            "git could not produce `{}` at {} -- the commit is not in this tree, or the file did "
            "not exist there".format(BOOK_PATH.relative_to(PROJECT), commit[:9]))

    counts = _roster_counts(roster)
    disagreed = [
        {"field": field, "the_run_recorded": identity[field], "the_roster_holds": counts[key]}
        for field, key in _BOOK_IDENTITY_COUNTS if int(identity[field]) != counts[key]
    ]
    if disagreed:
        return _refuse(
            "the roster at {} is NOT the book the arms ran on: {}. Refused rather than published, "
            "because a population that is merely about the right size would answer this question "
            "about a different set of households.".format(
                commit[:9],
                "; ".join("`{}` run={} roster={}".format(
                    d["field"], d["the_run_recorded"], d["the_roster_holds"]) for d in disagreed)))

    dist = book_distribution(roster, knee_bill_gbp)
    dist.pop("population_is_not_the_published_arms_book", None)
    dist["source"] = "{} at {}".format(BOOK_PATH.relative_to(PROJECT), commit[:9])
    dist["identified_by"] = {
        "producing_commit": commit,
        "reconciled_counts": [
            {"field": field, "value": identity[field]} for field, _ in _BOOK_IDENTITY_COUNTS],
        "all_four_agree": True,
        "why_all_four": (
            "The commit alone would only establish which CODE ran. These four counts were "
            "published by the run about its own book and recomputed here from the blob; all four "
            "agreeing is what makes this the arms' population rather than a roster of about the "
            "right size. The book at HEAD fails this check on every one of them."),
    }
    return dist


def report(book: dict) -> dict:
    """Every reading, each carrying its own refusal rather than an absence."""
    k = knee()
    # THE BILL THE BOOK IS CUT AT IS THE DECLARED THRESHOLD, AND FROM 2026-09-23 ONLY THAT.
    # It used to prefer a knee bill derived from the estimator, which was the better source while
    # the estimator had a knee to derive. It has none now, and the derived column collapsed to
    # 0.1-0.4 -- so preferring it would cut this book at forty pence and report every leg above
    # the knee, a figure that would still render. `legs_below_the_knee` is a statement about
    # `bill_stress`'s declared threshold and is labelled as one; the count the published sentence
    # rests on is `size_deafness`, which asks the estimator per leg and needs no cut at all.
    knee_bill = k["declared_threshold_gbp"]
    part = partition()
    dist = book_distribution(book, knee_bill)
    arms = arms_book(knee_bill)
    return {
        "what_this_is": (
            "Whether the company's per-customer churn belief carries information in the dimension "
            "the world's churn response is most sensitive to -- household size -- and how this "
            "book's own accounts fall either side of the point where it starts to."),
        "what_this_cannot_say": (
            "It does not price the gap. It says whether the belief can express a difference the "
            "world makes, not what failing to express it costs, and no figure here is a target."),
        "knee": k,
        "partition": part,
        "book": dist,
        "arms_book": arms,
        "which_book_the_reading_quotes": (
            "`arms_book` when it is available -- the 154 accounts the published arms were scored "
            "over, which is the population the page's selection leg is a statement about. `book` "
            "is the tree's book today and is kept beside it because the two differ."),
        "reading": _reading(k, part, dist, arms),
        "not_a_target": (
            "R12. A belief that does not vary in a dimension is a diagnostic about the belief. "
            "Nothing here instructs the company to make it vary, and the epistemic wall is "
            "untouched either way: a supplier meters its own customers, which is why the world's "
            "own `churn_position_multiplier` calls consumption something the company can "
            "legitimately act on."),
    }


def _reading(k: dict, part: dict, dist: dict, arms: dict | None = None) -> str:
    if not (k.get("available") and dist.get("available")):
        return ("REFUSED: the knee or the book could not be established, so no statement about "
                "whether the belief distinguishes this book's households is made.")
    # THE ARMS' BOOK WHEN IT IS THERE, and the tree's when it is not. The page hangs this sentence
    # beside a selection leg measured over the 154-account book, so quoting the 164-account one
    # would answer a question about a different set of households in the same words. The fallback
    # is not silent: `which_book_the_reading_quotes` says which, and `arms_book` names why it
    # refused.
    quoted, which = ((arms, "the 154-account book the published arms were scored over")
                     if (arms or {}).get("available")
                     else (dist, "the book this tree holds today"))
    deafness = quoted.get("size_deafness") or {}
    at_250 = next((r for r in k["by_rate"] if r["old_rate_gbp_per_mwh"] == 250.0), {})
    # THE SENTENCE IS CORRECTED BESIDE ITS OWN PREDECESSOR, 2026-09-23. What stood here said the
    # belief was FLAT in household size for the great majority of this book, below a knee at a
    # declared bill. That was measured correctly and it is now false: `fc390b918` landed a size
    # term sourced to the same survey the world's own multiplier cites. The finding has not
    # closed, it has MOVED -- to the top of the book, where both of the belief's consumption
    # terms are saturated -- and the sentence says which way it moved rather than dropping the
    # old claim silently, because a reader who met the old one is owed that.
    # THE SENTENCE IS COMPOSED FROM WHAT WAS MEASURED, NOT FROM A NARRATIVE ABOUT THE MODEL.
    # Learned the expensive way on 2026-09-23: the first draft of this hard-coded "both terms
    # that read consumption are ceilinged", which is a true sentence about the shared working
    # tree and a FALSE one about every commit, because the `bill_stress` ceiling it names is
    # another lane's uncommitted edit. A reading that asserts a mechanism it did not measure
    # publishes whichever tree the author happened to run in. The deafness clause therefore
    # appears only when the census actually found deaf legs, and the edge clause only when an
    # edge was found -- both of which are `None` at HEAD and present with that lane's ceiling.
    deaf_n = deafness.get("legs_the_belief_is_deaf_to") or 0
    deaf_kwh = at_250.get("the_belief_goes_deaf_to_size_above_kwh")
    common = (
        "The company's churn belief HEARS household size for {heard} of this book's {graded} "
        "supply legs. That is an inversion of what this measurement published until 2026-09-23, "
        "and the landing that caused it is `fc390b918`: `estimate_churn_probability` gained a "
        "size term scaling the rate response by the household's own consumption against the "
        "published Ofgem TDCV Medium band, on the same Ofgem/BMG survey the world's own "
        "multiplier cites. Before it the belief returned one number across a six-fold span of "
        "household size. Over this book the world's own churn multiplier spans {world}x."
    ).format(heard=deafness.get("legs_the_belief_hears"),
             graded=deafness.get("legs_graded"),
             world=quoted.get("world_multiplier_spread"))
    if deaf_n:
        tail = (
            " It is still deaf to size for {deaf} of them, so the defect has MOVED rather than "
            "closed.".format(deaf=deaf_n)
            + (" Those {deaf} reach the largest households on the book, where a per-customer "
               "belief has the most to win and the least room left to express it.".format(
                   deaf=deaf_n)
               if deafness.get("the_deaf_legs_are_the_BIGGEST") else
               " They sit in a flat BAND rather than at the top of the book -- between the size "
               "term's cap and the consumption at which `bill_stress` switches on -- so this is "
               "a gap in the middle of the belief's range and not the end of its hearing.")
            + (" At GBP 250/MWh the belief stops responding above {kwh} kWh, and that edge moves "
               "{spread}x in kWh across the rate deck this book was billed at.".format(
                   kwh=deaf_kwh, spread=k.get("deaf_edge_kwh_spread_across_the_probe_rates"))
               if deaf_kwh and k.get("deaf_edge_kwh_spread_across_the_probe_rates") else ""))
    else:
        tail = (
            " No leg on this book is one the belief cannot hear the size of -- the flat arm this "
            "measurement was built to report is gone rather than moved. What is NOT established "
            "here is whether the belief's response is the right SIZE: this counts legs where the "
            "derivative is non-zero, which is a weaker claim than matching the world's "
            "{world}x, and no figure here licenses the stronger one.".format(
                world=quoted.get("world_multiplier_spread")))
    return ("Measured over {}. ".format(which) + common + tail
            + " This does not price that gap and is not an instruction to close it.")


def generate(out_path: Path | None = None) -> dict:
    book = json.loads(BOOK_PATH.read_text(encoding="utf-8"))
    data = report(book)
    dest = DEFAULT_ARTEFACT if out_path is None else out_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    return data


if __name__ == "__main__":
    _ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    _ap.add_argument("--out", type=Path, default=None, help="where to write the artefact")
    _args = _ap.parse_args()
    print(generate(_args.out)["reading"])
