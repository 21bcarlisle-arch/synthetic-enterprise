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
    ARM B0  `fit_weights` forced to `groups=None` -- the PRE-REPAIR fit, before §B's P3 made the
            year marginal a constraint rather than an axis

**Nothing here re-implements the cull or the chooser.** Settled positions are recovered from the
returned `winners` by OBJECT IDENTITY against the candidate list. A harness that replicated the
selection rule would be measuring its own copy of it, and the copy is what goes stale.

WHAT THE SELF-CHECK IS FOR
--------------------------
`--check` refuses unless the arms reproduce the filed scalars (90/1195.4, 84/1197.0, 1.553x). A
per-axis reading from a harness that cannot reproduce the number it claims to decompose is a
different measurement wearing that number's name, and the disagreement would be the finding.

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

#: The filed scalars this harness must reproduce before any per-axis number it prints is graded.
#: From `SEAT_RESULT_THE_SETTLED_BOOK_IS_CHOSEN_AND_WEIGHTED_2026-09-11.md`, seed 42.
#:
#: **THEY DO NOT REPRODUCE, AND THE CAUSE IS ESTABLISHED RATHER THAN SUSPECTED** (2026-09-15).
#: The filed run's base is `3957ba848`, and `0d86d6dfe` -- "the world's homes are drawn from the
#: fitted joint now" -- is NOT an ancestor of it. It reached this tree through the fork-closing
#: merge `2212d0eed`. So the FUNNEL is identical here (502 candidates, the cull settles the same
#: 90 at the same 1195.3895 cy) and the HOMES are not (105 distinct fabric vectors against the
#: filed 109). A KS over the fabric axes is a statistic about the homes.
#:
#: The refusal is therefore CORRECT and is not a tolerance to be widened. Left in place because
#: what it refuses is real: these numbers cannot be decomposed per axis on this base and called a
#: grading of the prediction they graded.
FILED = {
    "cull_settled": 90,
    #: Filed at ONE DECIMAL, so it is compared at one decimal. Comparing 1195.3895 against a
    #: figure that was rounded before it was written down manufactures a disagreement, and a
    #: refusal that names a non-disagreement beside a real one devalues the real one.
    "cull_cy": 1195.4,
    "chosen_settled": 84,
    "chosen_cy": 1197.0,
    "worst_ks_cull": 0.12798,
    "worst_ks_chosen": 0.08241,
    "ratio": 1.553,
}

#: What a reader of the refusal needs, so the next session does not re-derive the attribution.
REFUSAL_CAUSE = (
    "ESTABLISHED 2026-09-15: the filed scalars were measured at base 3957ba848, which does NOT "
    "contain 0d86d6dfe ('the world's homes are drawn from the fitted joint'). That change reached "
    "this tree through the fork-closing merge 2212d0eed. The funnel is unchanged and the home "
    "stock is not, so the filed KS figures belong to a different world. Do not widen the "
    "tolerances; re-run at 3957ba848 if a verdict against the FILED evidence is what is wanted."
)

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


def _self_check(arms: dict, ks: dict) -> list[str]:
    """What must reproduce before any per-axis number above is graded. Returns the disagreements."""
    from simulation.settlement_choice import CHOICE_AXES

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

    disagreements = _self_check(arms, ks)
    payload = {
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
        "self_check_cause": (REFUSAL_CAUSE if disagreements else None),
        # THE VERDICT ON §A's OWN FILED EVIDENCE, and it stays `None` while the self-check refuses.
        # This is the key a reader may quote as "P1b was graded", so it must be empty exactly when
        # the base the prediction was filed against is not the base that ran.
        "grading_against_the_FILED_evidence": (
            None if disagreements else grade(ks["cull"], ks["chosen"])),
        # THE SAME ARITHMETIC ON TODAY'S BASE, always computed and NEVER the answer to the same
        # question. Reported because the profile is real and informative about the shipped chooser;
        # named this way because a grading of a 09-11 prediction on a 09-15 world is a different
        # claim, and the two collapsing into one key is how the substitution happens.
        "profile_on_THIS_base_which_is_NOT_the_filed_one": grade(ks["cull"], ks["chosen"]),
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
        print(f"\n{REFUSAL_CAUSE}", file=sys.stderr)
        return 1 if args.check else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
