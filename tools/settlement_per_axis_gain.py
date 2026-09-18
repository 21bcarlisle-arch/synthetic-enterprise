#!/usr/bin/env python3
"""WHERE the chooser's gain sits — per axis — against the systematic cull, on one candidate list.

WHY THIS EXISTS
---------------
`SEAT_RESULT_THE_SETTLED_BOOK_IS_CHOSEN_AND_WEIGHTED_2026-09-11.md` published **worst-axis** KS:
0.12798 culled against 0.08241 chosen, a factor of 1.553. That single scalar graded P1 and it is
the right instrument for P1 — "is the chosen sample closer to the population" is a question about
the worst column.

It is the wrong instrument for a different prediction that was filed at the same time. §A of
`SEAT_PREREGISTRATION_WHAT_CHOOSING_THE_SETTLED_SAMPLE_FOR_DIFFERENCE_MOVES_2026-09-11.md` also
predicted *"the gain is concentrated on the fabric axes rather than on cost"* — a claim about the
PROFILE across columns, which a maximum over those columns cannot answer either way.
`SEAT_RESULT_SECTION_A_..._REGRADED_AGAINST_ITS_OWN_NUMBERING_2026-09-15.md` recorded that clause
as **UNGRADEABLE** rather than inferring a verdict from the worst axis, and named the per-axis run
as unrun work. This is that run.

Pre-registered before it was run, with the grading rule and the kill lines fixed in advance:
`docs/staging/records/SEAT_PREREG_WHERE_THE_CHOOSERS_GAIN_SITS_PER_AXIS_AND_WHETHER_SECTION_AS_P1B_
HOLDS_2026-09-15.md`.

HOW THE ARMS ARE MADE, AND WHY NO SELECTION LOGIC IS REPLICATED HERE
--------------------------------------------------------------------
The campaign is resolved ONCE and its candidate list captured at `settle_within_budget`'s own
boundary, because running the campaign twice puts the seed stream in the comparison and makes any
move unattributable. Both arms then call the **shipped** `settle_within_budget` on that one list:

    ARM A   `choose_settled_sample` patched to return `None` -- exactly the refusal the shipped
            fallback exists for, so the systematic `int((i+1)*r) > int(i*r)` cull runs
    ARM B   unpatched: the shipped path, `fit_weights(groups=candidate_years)`
    ARM B0  `fit_weights` forced to `groups=None` -- the PRE-REPAIR fit, before P3 made the
            year marginal a constraint rather than an axis

**Nothing here re-implements the cull or the chooser.** Settled positions are recovered from the
returned `winners` by OBJECT IDENTITY against the candidate list. A harness that replicated the
selection rule would be measuring its own copy of it, and the copy is what goes stale.

WHAT THE SELF-CHECK IS FOR
--------------------------
`--check` refuses unless the arms reproduce the scalars filed FOR THIS WORLD. A per-axis reading
from a harness that cannot reproduce the number it claims to decompose is a different measurement
wearing that number's name, and the disagreement would be the finding.

Which record that is comes from the world's own two digests, never from "the newest one" -- see
`FILED_RECORDS`. A world with no filed evidence refuses and says so; it does not fall back.

USAGE
-----
    python3 -m tools.settlement_per_axis_gain --seed 42
    python3 -m tools.settlement_per_axis_gain --seed 42 --out docs/observability/<file>.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

#: EVIDENCE IS GRADED ONLY AGAINST THE WORLD IT WAS MEASURED IN. That is the 2026-09-16 repair and
#: it is a change of SHAPE, not of tolerance.
#:
#: What was here was one filed record, from
#: `SEAT_RESULT_THE_SETTLED_BOOK_IS_CHOSEN_AND_WEIGHTED_2026-09-11.md` at base `3957ba848`, seed 42.
#: It stopped reproducing on 2026-09-15 and the cause was established rather than suspected:
#: `0d86d6dfe` -- "the world's homes are drawn from the fitted joint now" -- is not an ancestor of
#: that base and reached this tree through the fork-closing merge `2212d0eed`. The FUNNEL is
#: identical (502 candidates, the cull settles the same 90 at the same 1195.3895 cy); the HOMES are
#: not (105 distinct fabric vectors against the filed 109). A KS over the fabric axes is a statistic
#: about the homes, so the refusal was correct and was never a tolerance to widen.
#:
#: **But a correct refusal left the claim ungradable for five days**, and the director's Stage 1 ask
#: is that the sample EARN ITS PLACE on the settlement selection -- which it cannot do while the
#: only evidence that could grade it describes a world nobody runs. Re-pointing the single record at
#: today's numbers would have re-created the same staleness the next time the stock moves, and a
#: control keyed to today's answer goes red when the code becomes more honest.
#:
#: So the record is keyed to its WORLD. Each entry carries the two digests that say which world it
#: was measured in, and `_filed_for_this_world` grades against the entry whose world is live. A
#: stock change now produces "this world has no filed evidence -- re-file" rather than five numbers
#: that read as the method disagreeing with itself. The 09-11 entry is KEPT, not replaced: a
#: prediction and the result that refuted it belong beside each other.
FILED_RECORDS = (
    {
        "filed": "2026-09-11",
        "base": "3957ba848",
        "source": "SEAT_RESULT_THE_SETTLED_BOOK_IS_CHOSEN_AND_WEIGHTED_2026-09-11.md",
        "world": {
            "level_digest": "39a192ce04c1eda8",
            #: NOT unknown and not unstamped: the home-stock digest post-dates this evidence, so
            #: there was no field to fill. The mismatch against this entry was established by
            #: CAUSE on 2026-09-15 (the fitted-joint draw is absent from its base), which is
            #: strictly stronger than a digest comparison and is why this entry can still be
            #: reasoned about. It can never MATCH a live world, which is correct -- a `None` here
            #: must not be read as "matches anything".
            "home_digest": None,
            "home_digest_absent_because":
                "simulation/world_home_identity post-dates this evidence; the world mismatch is "
                "established by cause (0d86d6dfe is not an ancestor of 3957ba848), not by digest",
        },
        "scalars": {
            "cull_settled": 90,
            #: Filed at ONE DECIMAL, so it is compared at one decimal. Comparing 1195.3895 against
            #: a figure that was rounded before it was written down manufactures a disagreement,
            #: and a refusal that names a non-disagreement beside a real one devalues the real one.
            "cull_cy": 1195.4,
            "chosen_settled": 84,
            "chosen_cy": 1197.0,
            "worst_ks_cull": 0.12798,
            "worst_ks_chosen": 0.08241,
            "ratio": 1.553,
        },
    },
    {
        "filed": "2026-09-16",
        "base": "HEAD at the fitted-joint stock (0d86d6dfe, merged 2212d0eed)",
        "source": "SEAT_RESULT_THE_SAMPLE_EARNS_ITS_PLACE_ON_THE_SETTLEMENT_SELECTION_2026-09-16.md",
        "world": {
            "level_digest": "39a192ce04c1eda8",
            "home_digest": "35f8efe8ff02f245",
        },
        #: Measured, not predicted, and this entry says so rather than dressing a re-file as a
        #: forecast. The PREDICTION it grades is §A's P1b, filed 2026-09-11 and unchanged: that
        #: choosing-and-weighting beats the count cull on the worst fabric axis. P1b HOLDS here,
        #: by more than it held on the world it was filed against (1.66x against 1.55x).
        "scalars": {
            "cull_settled": 90,
            "cull_cy": 1195.4,
            "chosen_settled": 83,
            "chosen_cy": 1199.2,
            "worst_ks_cull": 0.09765,
            "worst_ks_chosen": 0.05878,
            "ratio": 1.6613,
        },
    },
)


#: What a reader of the refusal needs when the world MATCHED an entry and the numbers still moved.
#: That is the strictly worse case: the world is the one this evidence was measured in, so the
#: disagreement is about the METHOD or the funnel, and neither is a tolerance to widen.
_STALE_ENTRY_CAUSE = (
    "The filed record for THIS world did not reproduce. The world digests match, so this is not "
    "the 2026-09-15 stale-base shape -- something in the funnel, the chooser or the capture moved "
    "under evidence measured in this same world. Do not widen a tolerance and do not re-file over "
    "it: find what moved first, because a re-file here would erase the only record that can show "
    "it moved."
)


def _filed_for_this_world() -> tuple[dict | None, str]:
    """(the filed record measured in the LIVE world, why there is none). Exactly one is non-empty.

    FAILS CLOSED, and the direction matters. An unreadable digest returns no record and says which
    digest it could not read -- it does NOT fall through to the newest entry, because "I could not
    tell which world this is" and "this is the world that entry was measured in" are different
    states and collapsing them is how a figure from one world comes to bound a figure from another.
    """
    try:
        from simulation.departure_level_anchor import world_level_identity
        from simulation.world_home_identity import home_stock_identity
        live = {"level_digest": world_level_identity().get("digest"),
                "home_digest": home_stock_identity().get("digest")}
    except Exception as exc:  # noqa: BLE001 -- cannot establish, never "fine"
        return None, (f"the live world could not be identified ({exc}), so no filed evidence can "
                      "be matched to it and nothing is graded")
    missing = [k for k, v in live.items() if not v]
    if missing:
        return None, (f"the live world's {', '.join(missing)} could not be read, so no filed "
                      "evidence can be matched to it and nothing is graded")
    for record in FILED_RECORDS:
        w = record["world"]
        if w["level_digest"] == live["level_digest"] and w["home_digest"] == live["home_digest"]:
            return record, ""
    return None, (
        f"no filed evidence was measured in this world (level {live['level_digest']}, "
        f"homes {live['home_digest']}). The filed entries are "
        + "; ".join(f"{r['filed']} at level {r['world']['level_digest']}, homes "
                    f"{r['world']['home_digest']}" for r in FILED_RECORDS)
        + ". Re-file by running this tool and writing its profile into a dated SEAT_RESULT -- do "
          "NOT widen a tolerance, and do not re-point an existing entry: the entry and the world "
          "it was measured in are one fact.")

#: §A's P1b names "floor area, heat-loss coefficient, remaining insulation ceiling". The third is
#: not an axis and never was -- it belongs to `settlement_choice_probe`'s six-axis draft. The
#: fabric set graded here is the three PHYSICAL axes; §A's named-and-existing pair is reported
#: beside it so the verdict can be read either way. Pre-committed, not chosen after the numbers.
FABRIC_AXES = ("floor_area_m2", "fabric_w_per_k", "raw_infiltration_ach")
FABRIC_AXES_AS_NAMED_BY_SECTION_A = ("floor_area_m2", "fabric_w_per_k")
COST_AXIS = "customer_years"

ARTEFACT = pathlib.Path("docs/observability/settlement_per_axis_gain.json")


def capture(seed: int):
    """Resolve the live campaign ONCE; return its candidate list and the selector's own kwargs.

    The kwargs matter as much as the list: `customer_year_budget` and `committed_cy` are what the
    budget guard acts on, and an arm run under a different ceiling is not the same arm.
    """
    from simulation import live_population as lp
    from simulation import net_new_acquisition as nna

    seen: list = []
    real = nna.settle_within_budget

    def spy(candidates, **kwargs):
        seen.append((list(candidates), dict(kwargs)))
        return real(candidates, **kwargs)

    nna.settle_within_budget = spy
    try:
        lp._campaign(lp._pre_growth_book(seed), seed)
    finally:
        nna.settle_within_budget = real

    if not seen:
        raise RuntimeError(
            "the campaign resolved without reaching the settlement pass -- nothing to compare. "
            "Either the pass moved or `_CAMPAIGN_MEMO` returned a cached run.")
    # The LAST resolution, for the same reason `settlement_choice_probe` takes it: if a future
    # caller ever resolves twice, the list the published run used is the one that ran last.
    return seen[-1]


def _run_arm(candidates, kwargs, *, cull: bool = False, groups: bool = True) -> dict:
    """One arm, through the SHIPPED selector, with exactly one thing patched.

    Returns the settled positions (by identity against `candidates`) and their weights.
    """
    from simulation import net_new_acquisition as nna
    from simulation import settlement_choice as sc
    from tools import demand_vector_coverage as dvc

    real_choose = sc.choose_settled_sample
    real_fit = dvc.fit_weights
    if cull:
        sc.choose_settled_sample = lambda *a, **k: None
    elif not groups:
        # THE PRE-REPAIR FIT. `choose_settled_sample` imports `fit_weights` from this module at
        # call time, so forcing the keyword here is what "before §B's P3 repair" means without
        # editing the shipped call. `groups` is dropped, not set to something else.
        def no_groups(values, chosen, reference, **k):
            k.pop("groups", None)
            return real_fit(values, chosen, reference, **k)
        dvc.fit_weights = no_groups
    try:
        out = nna.settle_within_budget(candidates, **kwargs)
    finally:
        sc.choose_settled_sample = real_choose
        dvc.fit_weights = real_fit

    # POSITIONS BY OBJECT IDENTITY, so no selection logic is replicated. The prospect objects in
    # `winners` ARE the ones in `candidates`; matching on a value would risk two candidates with
    # identical fabric colliding, which this population has (109 distinct vectors in 502 rows).
    at = {id(prospect): i for i, (_y, prospect, _d, _cy) in enumerate(candidates)}
    if len(at) != len(candidates):
        raise RuntimeError("two candidates share one prospect object -- identity cannot address "
                           "the selection and this harness must not guess which was settled")
    positions = [at[id(prospect)] for prospect, _in_market in out["winners"]]
    return {
        "selection": out["selection"],
        "choice_refusal": out["choice_refusal"],
        "settled": len(positions),
        "committed_cy": round(float(out["committed_cy"]), 4),
        "positions": positions,
        "weights": [float(w) for w in out["settlement_weights"]],
    }


def _ks_by_axis(vectors, arm) -> dict:
    """Per-axis weighted KS of this arm's settled sample against the FULL candidate population.

    Same function and same reference the filed 1.553x came from -- `accepts_weighted` over a
    `_Reference` built on every candidate, not on the arm.
    """
    import numpy as np

    from simulation.settlement_choice import CHOICE_AXES
    from tools.demand_vector_coverage import _Reference, accepts_weighted

    values = np.asarray(vectors, dtype=float)
    reference = _Reference(values, CHOICE_AXES)
    verdict = accepts_weighted(values[arm["positions"]], np.asarray(arm["weights"], dtype=float),
                               reference)
    return {axis: float(verdict[axis]["d"]) for axis in CHOICE_AXES} | {
        "JOINT": float(verdict["JOINT"]["d"])}


def estimator_error(vectors, arm) -> dict:
    """How wrong the BOOK'S OWN AVERAGE is, per axis, when estimated from this arm.

    WHY THIS EXISTS BESIDE THE KS (2026-09-18). KS answers "is the settled sample's DISTRIBUTION
    closer to the population's", and P1b holds on it at 1.66x. That is not the claim the sample has
    to earn. The settled book is the population every published figure is summed over -- margin,
    carbon, the intervention ranking -- and what those figures inherit is the sample's ERROR ON THE
    MEAN, not its distributional distance. A sample can be distributionally closer and still
    estimate the average worse, because KS is driven by the worst point of the CDF and a mean is
    driven by the tails' mass.

    So this reports, per axis, the weighted mean the arm would have you believe against the
    population's own, as a signed percentage. Signed on purpose: a book that is 3% too leaky and one
    that is 3% too tight are different errors with different consequences for a gas-heated book, and
    an absolute value would report them as the same.

    It is deliberately NOT a demand figure. Turning each candidate into annual kWh means a trace per
    candidate, and the axes ARE the demand model's inputs -- `fabric_w_per_k` and
    `raw_infiltration_ach` are what the heat loss is computed from. Estimating the inputs badly is
    what makes the outputs wrong, and this measures the inputs without inventing a demand model
    beside the one that ships.
    """
    import numpy as np

    from simulation.settlement_choice import CHOICE_AXES

    values = np.asarray(vectors, dtype=float)
    weights = np.asarray(arm["weights"], dtype=float)
    settled = values[arm["positions"]]
    if weights.sum() <= 0:
        raise ValueError("this arm carries no weight at all; nothing can be estimated from it")

    out = {}
    for index, axis in enumerate(CHOICE_AXES):
        population_mean = float(values[:, index].mean())
        arm_mean = float(np.average(settled[:, index], weights=weights))
        out[axis] = {
            "population_mean": round(population_mean, 4),
            "arm_mean": round(arm_mean, 4),
            "signed_error_pct": (None if population_mean == 0 else
                                 round((arm_mean - population_mean) / population_mean * 100.0, 3)),
        }
    return out


def estimator_verdict(err_cull: dict, err_chosen: dict) -> dict:
    """Does choosing estimate the book's own averages better than counting does, axis by axis?

    STATED AS A COUNT OF AXES, not as a mean of ratios. Averaging per-axis ratios would let one
    axis with a near-zero denominator carry the verdict, which is the "two true numbers whose ratio
    is not a quantity" shape this project keeps finding.
    """
    from simulation.settlement_choice import CHOICE_AXES

    per_axis = {}
    for axis in CHOICE_AXES:
        cull = err_cull[axis]["signed_error_pct"]
        chosen = err_chosen[axis]["signed_error_pct"]
        if cull is None or chosen is None:
            per_axis[axis] = {"verdict": "NOT GRADED: the population mean is zero on this axis"}
            continue
        per_axis[axis] = {
            "cull_error_pct": cull,
            "chosen_error_pct": chosen,
            "closer": "chosen" if abs(chosen) < abs(cull) else "cull",
            "shrink_factor": (round(abs(cull) / abs(chosen), 3) if chosen != 0 else float("inf")),
        }
    graded = [a for a in CHOICE_AXES if "closer" in per_axis[a]]
    won = [a for a in graded if per_axis[a]["closer"] == "chosen"]
    return {
        "per_axis": per_axis,
        "axes_graded": len(graded),
        "axes_where_choosing_estimates_better": len(won),
        "axes_won": won,
        # THE HONEST HEADLINE. "Better on most axes" is not "better", and a book is summed over all
        # of them at once, so a split is reported as a split rather than resolved by majority.
        "verdict": ("CHOOSING ESTIMATES THE BOOK BETTER" if len(won) == len(graded) and graded else
                    "COUNTING ESTIMATES THE BOOK BETTER" if not won and graded else
                    f"SPLIT -- choosing wins {len(won)} of {len(graded)} axes"),
    }


def grade(ks_cull: dict, ks_chosen: dict) -> dict:
    """§A's P1b, against the rule fixed in the pre-registration before any number was seen.

    `g_j > 1` means the chooser sits closer to the population on axis `j` than the cull does.
    SPLIT is a FAILURE OF THE SENTENCE and not a draw: "concentrated on the fabric axes" is a
    claim about the set, so one fabric axis losing to cost refutes it however well the others do.
    """
    from simulation.settlement_choice import CHOICE_AXES

    gain = {axis: (ks_cull[axis] / ks_chosen[axis]) if ks_chosen[axis] > 0 else float("inf")
            for axis in CHOICE_AXES}
    fabric = [gain[a] for a in FABRIC_AXES]
    cost = gain[COST_AXIS]
    if min(fabric) > cost:
        verdict = "HOLDS"
    elif cost >= max(fabric):
        verdict = "FAILS"
    else:
        verdict = "SPLIT -- P1b as written is false"
    as_named = [gain[a] for a in FABRIC_AXES_AS_NAMED_BY_SECTION_A]
    return {
        "gain_by_axis": {a: round(g, 4) for a, g in gain.items()},
        "fabric_min": round(min(fabric), 4),
        "fabric_max": round(max(fabric), 4),
        "cost": round(cost, 4),
        "P1b": verdict,
        "P1b_on_section_As_named_and_existing_pair": (
            "HOLDS" if min(as_named) > cost else
            "FAILS" if cost >= max(as_named) else "SPLIT -- P1b as written is false"),
        # N4: a FLAT profile would mean "concentrated" has no referent, and P1b would be
        # unfalsifiable rather than true. Reported whatever the verdict is.
        "spread_max_over_min": round(max(gain.values()) / min(gain.values()), 4),
        "worst_axis_cull": max(CHOICE_AXES, key=lambda a: ks_cull[a]),
        "worst_axis_chosen": max(CHOICE_AXES, key=lambda a: ks_chosen[a]),
    }


def _self_check(arms: dict, ks: dict, filed: dict | None = None) -> list[str]:
    """What must reproduce before any per-axis number above is graded. Returns the disagreements.

    `filed` is the SCALARS of the record measured in the live world. Passing None is not "grade
    against the newest" -- it is "there is nothing this world's numbers may be graded against",
    which is one disagreement naming that, never zero.
    """
    from simulation.settlement_choice import CHOICE_AXES

    if filed is None:
        return ["no filed evidence exists for this world"]

    FILED = filed  # noqa: N806 -- the record under grading, named as the legs below read it
    worst = {k: max(ks[k][a] for a in CHOICE_AXES) for k in ("cull", "chosen")}
    out = []
    for name, got, want in (
            ("cull settled", arms["cull"]["settled"], FILED["cull_settled"]),
            ("chosen settled", arms["chosen"]["settled"], FILED["chosen_settled"])):
        if got != want:
            out.append(f"{name}: {got} != filed {want}")
    # EACH LEG IS COMPARED AT THE PRECISION ITS FILED FIGURE WAS WRITTEN DOWN AT. The customer-year
    # totals were filed to one decimal; the KS figures to five. Comparing a full-precision
    # measurement against a rounded record fires on the rounding, and this leg did exactly that on
    # its first run (1195.3895 "!=" 1195.4) beside four real disagreements.
    for name, got, want, dp in (
            ("cull cy", arms["cull"]["committed_cy"], FILED["cull_cy"], 1),
            ("chosen cy", arms["chosen"]["committed_cy"], FILED["chosen_cy"], 1),
            ("worst-axis KS cull", worst["cull"], FILED["worst_ks_cull"], 5),
            ("worst-axis KS chosen", worst["chosen"], FILED["worst_ks_chosen"], 5)):
        if round(float(got), dp) != round(float(want), dp):
            out.append(f"{name}: {round(float(got), dp)} != filed {want}")
    ratio = worst["cull"] / worst["chosen"] if worst["chosen"] else float("inf")
    if abs(ratio - FILED["ratio"]) > 5e-4:
        out.append(f"worst-axis ratio: {ratio:.4f} != filed {FILED['ratio']}")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=int, default=42,
                        help="the seed the filed 1.553x was measured at")
    parser.add_argument("--out", type=pathlib.Path, default=None)
    parser.add_argument("--check", action="store_true",
                        help="exit non-zero if the arms do not reproduce the filed scalars")
    args = parser.parse_args(argv)

    from simulation.settlement_choice import CHOICE_AXES, _fuel_of, demand_vector  # noqa: F401

    candidates, kwargs = capture(args.seed)
    vectors = [demand_vector(p, cy) for _y, p, _d, cy in candidates]
    if any(v is None for v in vectors):
        raise RuntimeError(
            f"{sum(v is None for v in vectors)} of {len(vectors)} candidates have no home on the "
            f"demand axes -- the chooser refuses this list and there is no arm B to compare")

    arms = {
        "cull": _run_arm(candidates, kwargs, cull=True),
        "chosen": _run_arm(candidates, kwargs),
        "chosen_no_year_groups": _run_arm(candidates, kwargs, groups=False),
    }
    ks = {name: _ks_by_axis(vectors, arm) for name, arm in arms.items()}

    record, no_record_because = _filed_for_this_world()
    disagreements = _self_check(arms, ks, record["scalars"] if record else None)
    refusal_cause = no_record_because or (_STALE_ENTRY_CAUSE if disagreements else None)
    payload = {
        "filed_evidence_for_this_world": (
            {k: record[k] for k in ("filed", "base", "source", "world")} if record else None),
        "seed": args.seed,
        "candidates": len(candidates),
        "axes": list(CHOICE_AXES),
        "fabric_axes": list(FABRIC_AXES),
        "cost_axis": COST_AXIS,
        "settled": {k: v["settled"] for k, v in arms.items()},
        "committed_cy": {k: v["committed_cy"] for k, v in arms.items()},
        "selection": {k: v["selection"] for k, v in arms.items()},
        "ks_by_axis": {k: {a: round(d, 5) for a, d in v.items()} for k, v in ks.items()},
        "self_check_disagreements": disagreements,
        "self_check_cause": refusal_cause,
        # THE VERDICT ON §A's PREDICTION, and it stays `None` while the self-check refuses. This is
        # the key a reader may quote as "P1b was graded", so it must be empty exactly when the
        # evidence that could grade it was not measured in the world that ran.
        "grading_against_the_FILED_evidence": (
            None if disagreements else grade(ks["cull"], ks["chosen"])),
        # THE SAME ARITHMETIC, ALWAYS COMPUTED, and never the answer to the same question. When the
        # world matches a filed record these two keys hold identical objects BY CONSTRUCTION, and
        # that is not redundancy: when it does not match, this one is the only one populated, and a
        # reader who quotes it then is quoting a profile rather than a grading.
        #
        # RENAMED 2026-09-16 from `profile_on_THIS_base_which_is_NOT_the_filed_one`. That name was
        # true on 09-15 and became a false sentence the moment this world got its own filed record
        # -- a key asserting a state instead of naming a quantity rots into a lie the first time
        # the state changes, which is this project's own rule about keying to the property.
        "profile_on_THIS_base": grade(ks["cull"], ks["chosen"]),
        "profile_on_THIS_base_pre_repair_arm": grade(ks["cull"], ks["chosen_no_year_groups"]),
    }

    print(json.dumps(payload, indent=2, sort_keys=True))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    if disagreements:
        print("\nSELF-CHECK REFUSED -- nothing is graded against the FILED evidence:",
              file=sys.stderr)
        for d in disagreements:
            print(f"  {d}", file=sys.stderr)
        if refusal_cause:
            print(f"\n{refusal_cause}", file=sys.stderr)
        return 1 if args.check else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
