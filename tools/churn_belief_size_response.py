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
its input. The threshold's own position is unsourced -- `BILL_STRESS_THRESHOLD_GBP` is on this
repo's own no-origin debt list (`tools/domain_constant_origins --list`), and the docstring's
"the threshold where empirically customers start actively switching" cites nothing. That is
reported as a field here rather than repaired: the knee's position is not what this measures, and
a number invented to fill a slot is a finding to file, not a value to re-pick.

THE KNEE IS IN POUNDS, NOT KILOWATT-HOURS, AND THAT MATTERS
------------------------------------------------------------
The drawn item read the step as sitting "somewhere above 12,000 kWh". 12,000 kWh is where it sits
*at an old rate of GBP 250/MWh only*: the threshold is GBP 3,000 of PREVIOUS ANNUAL BILL, so the
kWh location moves with price -- 20,250 kWh at GBP 150/MWh, 7,750 at GBP 400/MWh. A control keyed
to 12,000 kWh would go red the next time the price deck moves and green while the mechanism rotted.
`knee` is therefore DERIVED by bisection from the estimator itself at each probe rate, and the
constant is reported beside it as a cross-check rather than as the answer.

WHICH BOOK THE DISTRIBUTION DESCRIBES, AND THE ONE THING THAT COULD NOT BE ESTABLISHED
---------------------------------------------------------------------------------------
The item asked for the EAC distribution of the 154 settled billing accounts behind
`site/data/value_arms.json`. **Those per-account rows are not persisted anywhere on disk.**
`value_cycle_ab_s1_three_arm_20260918.json` carries `book_identity` COUNTS and names
`phase2b.all_records` only inside prose; the records themselves are not written out, and
reconstructing them means re-running the arms. So the distribution here is measured on the book
this tree actually holds per-account -- `site/data/customers.json`, 164 accounts -- and the
artefact says so in `book.population_is_not_the_published_arms_book`. That difference is not
cosmetic and is not smoothed over: `generate_value_arms_data` already refuses to bound the 09-18
arms with a 164-account family for exactly this reason. What is claimed is a statement about THIS
book; whether the 154-account book differed in this dimension is recorded as not established.

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


def knee() -> dict:
    """Where the step is, derived at each probe rate, in pounds and in kilowatt-hours."""
    rows = []
    for rate in PROBE_RATES_GBP_PER_MWH:
        kwh = knee_kwh(rate)
        rows.append({
            "old_rate_gbp_per_mwh": rate,
            "knee_kwh": None if kwh is None else round(kwh, 1),
            # THE SAME KNEE IN THE UNITS THE MECHANISM IS ACTUALLY IN. If these agree across the
            # rates and the kWh column does not, the knee is a bill and not a consumption.
            "knee_prev_annual_bill_gbp": None if kwh is None else round(rate * kwh / 1000.0, 1),
        })
    bills = [r["knee_prev_annual_bill_gbp"] for r in rows if r["knee_prev_annual_bill_gbp"]]
    kwhs = [r["knee_kwh"] for r in rows if r["knee_kwh"]]
    return {
        "available": bool(bills),
        "by_rate": rows,
        # THE PROPERTY, NOT TODAY'S ANSWER. "The knee is at a fixed BILL and a moving kWh" is what
        # makes this a step in the wrong dimension to be a size term, and it is what the control
        # keys to -- not the literal 3,000 or the literal 12,000.
        "the_knee_is_a_bill_not_a_consumption": (
            bool(bills) and max(bills) - min(bills) <= 2.0 * BILL_STRESS_THRESHOLD_GBP / 100.0
            and len(set(kwhs)) == len(kwhs)),
        "kwh_spread_across_the_probe_rates": (
            None if len(kwhs) < 2 else round(max(kwhs) / min(kwhs), 2)),
        "declared_threshold_gbp": BILL_STRESS_THRESHOLD_GBP,
        "declared_sensitivity": BILL_STRESS_SENSITIVITY,
        "the_thresholds_own_origin": (
            "NOT ESTABLISHED. `BILL_STRESS_THRESHOLD_GBP` appears in "
            "`tools.domain_constant_origins --list`, i.e. this repository's own register of domain "
            "constants carrying no origin, and `churn_model`'s docstring justifies it as \"the "
            "threshold where empirically customers start actively switching\" without citing what "
            "established that. Reported, not repaired: the knee's POSITION is not what this "
            "measures, and re-picking an unsourced number would replace one invention with "
            "another."),
        "what_the_term_is": (
            "An absent term below the knee, not a band with wrong edges and not saturation. "
            "`bill_stress = sens * max(0, prev_annual_bill / threshold - 1)` is the ONLY place "
            "`estimate_churn_probability` reads consumption, and below the threshold `max` returns "
            "exactly 0.0, so d(belief)/d(consumption) is exactly zero. The term models financial "
            "DISTRESS at a large bill; household SIZE has no term in this model at any value."),
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
            "NOT THE 154 ACCOUNTS BEHIND `site/data/value_arms.json`. Those per-account rows are "
            "not persisted: `value_cycle_ab_s1_three_arm_20260918.json` carries `book_identity` "
            "counts and mentions `phase2b.all_records` only inside prose, so reconstructing them "
            "means re-running the arms. This is the book this tree holds per-account, and whether "
            "the 154-account book fell differently against the knee is NOT ESTABLISHED."),
    }


def report(book: dict) -> dict:
    """Every reading, each carrying its own refusal rather than an absence."""
    k = knee()
    knee_bill = k["declared_threshold_gbp"]
    derived = [r["knee_prev_annual_bill_gbp"] for r in k["by_rate"]
               if r["knee_prev_annual_bill_gbp"]]
    if derived:
        knee_bill = min(derived)
    part = partition()
    dist = book_distribution(book, knee_bill)
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
        "reading": _reading(k, part, dist),
        "not_a_target": (
            "R12. A belief that does not vary in a dimension is a diagnostic about the belief. "
            "Nothing here instructs the company to make it vary, and the epistemic wall is "
            "untouched either way: a supplier meters its own customers, which is why the world's "
            "own `churn_position_multiplier` calls consumption something the company can "
            "legitimately act on."),
    }


def _reading(k: dict, part: dict, dist: dict) -> str:
    if not (k.get("available") and dist.get("available")):
        return ("REFUSED: the knee or the book could not be established, so no statement about "
                "whether the belief distinguishes this book's households is made.")
    resi = dist["by_segment"].get("resi") or {}
    flat = (resi.get("legs") or 0) - (resi.get("above_the_knee") or 0)
    return (
        "The company's churn belief is FLAT in household size for {flat} of this book's {legs} "
        "domestic supply legs. Consumption reaches `estimate_churn_probability` through one term, "
        "`bill_stress`, which is identically zero below GBP {knee:.0f} of previous annual bill -- "
        "an absent term, not saturation and not a mis-placed band edge, because the estimate still "
        "moves freely with price at every consumption. The knee is a BILL: at GBP 250/MWh it falls "
        "at {kwh:.0f} kWh and it moves {spread}x in kWh across the rate deck this book was billed "
        "at. Over the same book the world's own churn multiplier spans {world}x, because it scales "
        "the price differential by each household's OWN annual spend. And the asymmetry is exact: "
        "the world reads a household's own bill for domestic supply only, so the one segment where "
        "the company's belief DOES vary with size is the segment where the world's does not. "
        "A per-customer belief that is constant in the dimension the world reacts to is a flat "
        "rule wearing a per-customer name in that dimension -- which is the baseline the thesis "
        "has to beat. This does not price that gap and is not an instruction to close it."
    ).format(
        flat=flat, legs=resi.get("legs"),
        knee=dist["knee_used_gbp"],
        kwh=next((r["knee_kwh"] for r in k["by_rate"]
                  if r["old_rate_gbp_per_mwh"] == 250.0 and r["knee_kwh"]), float("nan")),
        spread=k.get("kwh_spread_across_the_probe_rates"),
        world=dist.get("world_multiplier_spread"),
    )


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
