#!/usr/bin/env python3
"""Which 91 of the campaign's 500 wins get settled — the count cull against a chooser.

WHY THIS EXISTS
---------------
`simulation/net_new_acquisition.settle_within_budget` decides which of the campaign's funnel wins
this machine can afford to settle. Today it is a SYSTEMATIC COUNT CULL: take every 1-in-5.5 of a
year-ordered list, and publish one global inflation factor (`settlement_sample_rate`, ~18.3%) that
turns the settled book back into the commercial one. Every settled account stands for the same
5.46 accounts, whatever kind of home it is.

`tools/demand_vector_coverage` holds a CHOOSER (`choose_for_difference` + `fit_weights`) measured
against random draws on the six demand axes: 1.68x better on worst KS at N=40, 1.31x at N=400,
1.04x at N=4,400. It is deliberately NOT wired into the world's stock, because at 4,400 draws there
is nothing to compress. The settlement sample is 91 of 500 — the size at which it earns something.

THE COMPARISON HAS TO BE MADE ON ONE CANDIDATE LIST AND THAT IS WHY THIS IS A PROBE. Running the
campaign twice puts the seed stream in the comparison and makes any move unattributable. So the
campaign is resolved ONCE, its candidate list is captured, and both selection rules are applied to
those same candidates. The only variable is the rule.

PRE-REGISTERED FIRST, and the predictions are not to be revised after reading the output:
`docs/staging/records/SEAT_PREREGISTRATION_WHAT_CHOOSING_THE_SETTLED_SAMPLE_FOR_DIFFERENCE_MOVES_
2026-09-11.md`. P2 is the one that decides the item: a pure difference-chooser has no reason to
respect the per-year proportionality the cull gets for free, and if the fitted weights cannot
reconstruct it the change is refused.

WHAT A CANDIDATE'S DEMAND VECTOR IS HERE, and how it differs from the coverage tool's
-------------------------------------------------------------------------------------
`demand_vector_coverage` builds its six axes from a NEED row plus a weather cell. A CANDIDATE is
not a NEED row: it is a `SyntheticCustomer` whose `premise.household` was drawn from the fitted
stock joint, so it already carries floor area band, loft, cavity and PV, and it carries the
consumption the funnel actually quoted it on.

So the axes here are the ones a candidate can actually answer, and they are NAMED rather than
inherited, because an axis silently absent is how a sample comes to look better than it is:

    fabric_w_per_k          the dwelling's heat-loss coefficient as built
    floor_area_m2           the dominant term in that coefficient
    insulation_ceiling_w_k  what is LEFT to do — as-built minus fully retrofitted. The mission's
                            own quantity: the size of the intervention we could actually sell.
    solar_aperture_m2       what a PV or glazing story would be sized against
    internal_gain_kw        occupancy-driven demand, which the fabric terms do not carry
    eac_kwh                 the consumption the company quoted on — the one OBSERVABLE axis here

WEATHER IS DELIBERATELY NOT AN AXIS. The coverage tool varies the weather cell because it is
sampling the country; the campaign's candidates are what they are and their sites came with them.
Adding a weather axis would make the chooser spend its budget separating two identical houses in
different counties, which is not the difference this sample exists to carry.

THE HONEST GAP: `has_mains_gas_supply` and heating fuel are carried as the chooser's `fuel`
argument rather than as an axis, exactly as `choose_for_difference` intends — the minority fuel's
tail is not the population's tail, and the canon says those are different customers.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ARTEFACT = pathlib.Path("docs/observability/settlement_choice_probe.json")

#: The axes a candidate can answer. Order is load-bearing: it is the column order of `values`.
#:
#: TWO AXES WERE REMOVED FROM THIS TUPLE AFTER MEASURING THE FIRST CAPTURE, and the removal is a
#: mechanism correction made before any selection rule was compared, not a set fitted to an answer.
#: On the shipped 500 candidates, `solar_aperture_m2 / floor_area_m2` takes exactly ONE distinct
#: value (0.05775) and `internal_gain_kw / floor_area_m2` exactly one (0.004): both are floor area
#: rescaled, r = 1.0000 to four places, because `fabric_parameters` derives all three from the same
#: area. Left in, the z-scored clustering would have counted floor area THREE TIMES and spent the
#: sample separating large homes from small ones on a space that said nothing else.
#:
#: THIS IS THE SAME DEFECT AS `SEAT_FINDING_TWO_AXES_OF_THE_DEMAND_VECTOR_ARE_THE_SAME_AXIS_
#: 2026-09-08`, one module over and found the same way — by printing the numbers at real inputs
#: before shipping the formula, which is why that rule exists.
#:
#: `fabric_w_per_k` and `insulation_ceiling_w_k` correlate at 0.974 and BOTH ARE KEPT. They are not
#: the same axis: the ceiling is a DIFFERENCE of two fabrics, it has real zeros (a dwelling with
#: loft and cavity already done has nothing cheap left), and it is the mission's own quantity —
#: what a household could still be sold. A 0.974 correlation is a near-duplicate; a ratio with one
#: distinct value is an identity, and only the identity is disqualifying.
CANDIDATE_AXES = (
    "fabric_w_per_k",
    "floor_area_m2",
    "insulation_ceiling_w_k",
    "eac_kwh",
)

#: Kept in the artefact because they are cheap and a later reader may want them, but NOT chosen
#: over. Named here so their absence from `CANDIDATE_AXES` is a decision on the record rather than
#: an omission a reader has to notice.
DERIVED_FROM_FLOOR_AREA = ("solar_aperture_m2", "internal_gain_kw")


def capture_candidates(seed: int) -> list[dict]:
    """Resolve the live campaign ONCE and return its candidate list, one dict per funnel win.

    The capture is a monkeypatch on `settle_within_budget` rather than a new parameter on
    `plan_growth_campaign`. A parameter would be production machinery that exists to watch the
    work; the patch is a probe technique that leaves the shipped path exactly as it is, and it
    delegates so the run still resolves normally and the captured list is the one the run used.
    """
    from simulation import live_population as lp
    from simulation import net_new_acquisition as nna

    captured: list = []
    real = nna.settle_within_budget

    def spy(candidates, **kwargs):
        captured.append(list(candidates))
        return real(candidates, **kwargs)

    nna.settle_within_budget = spy
    try:
        lp._campaign(lp._pre_growth_book(seed), seed)
    finally:
        nna.settle_within_budget = real

    if not captured:
        raise RuntimeError(
            "the campaign resolved without reaching the settlement pass -- nothing to compare. "
            "Either the pass moved or the memo returned a cached run; clear `_CAMPAIGN_MEMO`."
        )
    # THE LAST ONE, not the first: if the memo is cold the pass runs once, and if a future caller
    # ever resolves twice the list the published run used is the one that ran last.
    return [_describe(year, prospect, in_market, cost_cy)
            for year, prospect, in_market, cost_cy in captured[-1]]


def _describe(year, prospect, in_market, cost_cy) -> dict:
    """One candidate, flattened to what the comparison needs and nothing else."""
    from simulation import fabric_physics as fp
    from simulation.household import InsulationLevel

    premise = getattr(prospect, "premise", None)
    household = getattr(premise, "household", None)

    row = {
        "year": int(year),
        "customer_id": prospect.customer_id,
        "in_market": in_market.isoformat(),
        "cost_cy": float(cost_cy),
        "eac_kwh": float(prospect.eac_kwh),
        "segment": prospect.segment,
    }

    # A NON-DOMESTIC WIN HAS NO FABRIC AND THAT IS A REAL ANSWER, not a zero. `fabric_parameters`
    # raises on a commercial property type by design, and a zero here would put every SME at the
    # origin of the space and make them look like each other and like nothing else.
    if household is None or not household.is_residential:
        row["fabric"] = None
        row["fuel"] = prospect.commodity if hasattr(prospect, "commodity") else "?"
        return row

    built = fp.fabric_parameters(household)
    retrofitted = fp.fabric_parameters(
        _with_insulation(household, InsulationLevel.FULL)
    )
    row["fabric"] = {
        "fabric_w_per_k": built.fabric_w_per_k,
        "floor_area_m2": built.floor_area_m2,
        # WHAT IS LEFT TO DO, and it is a DIFFERENCE of two fabrics rather than the fabric itself,
        # for the reason `demand_vector_coverage._fabric_for` gives: a dwelling that already has
        # loft and cavity has had the cheap measures, and crediting it the full retrofit is how a
        # sample ranks two very different customers identically.
        "insulation_ceiling_w_k": max(
            0.0, built.fabric_w_per_k - retrofitted.fabric_w_per_k
        ),
        "solar_aperture_m2": built.solar_aperture_m2,
        "internal_gain_kw": built.internal_gain_kw,
    }
    row["fuel"] = "gas" if household.is_gas_heated else "other"
    row["floor_area_band"] = household.floor_area_band
    row["has_loft_insulation"] = household.has_loft_insulation
    row["has_cavity_wall_insulation"] = household.has_cavity_wall_insulation
    row["has_solar"] = household.has_solar
    return row


def _with_insulation(household, level):
    """The same dwelling with the remaining measures taken."""
    import dataclasses

    return dataclasses.replace(household, insulation=level)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=int, default=20260724,
                        help="the run's base seed; the live default is the shipped one")
    parser.add_argument("--out", type=pathlib.Path, default=ARTEFACT)
    args = parser.parse_args(argv)

    rows = capture_candidates(args.seed)
    residential = [r for r in rows if r.get("fabric")]
    payload = {
        "seed": args.seed,
        "candidates": len(rows),
        "residential_candidates": len(residential),
        "axes": list(CANDIDATE_AXES),
        "rows": rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"captured {len(rows)} candidates ({len(residential)} residential) -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
