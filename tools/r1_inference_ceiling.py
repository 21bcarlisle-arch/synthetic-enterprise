"""R1: THE INFERENCE CEILING — how much of a household's hidden trait ANY supplier could recover.

REUSE: tools/r1_inference_ceiling.py
CLASS: CUSTOM
INDEX: searched "ceiling", "bound", "oracle", "mutual information", "learnable", "discoverab",
       "inference". `tools/ep13_input_ceiling.py` is the nearest organ and this is the SAME MOVE ON
       A DIFFERENT SUBJECT: that one bounds every dispatch model buildable on the world's inputs,
       this one bounds every inference model buildable on the company's observables. The three-rung
       shape (baseline / ceiling / shuffled null), the odd-even day split and the "the ceiling must
       not be reachable by the thing it measures" control are taken from it deliberately rather
       than reinvented. `tests/simulation/test_discoverability_claims_are_enforced.py` is the other
       neighbour and answers a strictly weaker question — whether the world's decision MOVES with a
       trait, which is necessary and nowhere near sufficient. A decision can move with a trait that
       no observer can ever recover, and that is precisely R1's claim.

WHY THIS EXISTS
---------------
Director canon, 2026-09-04 (`DIRECTOR_CANON_RERANKING_THE_ARC`), R1:

    "Satisfaction's entire within-cohort spread is a hash of the customer id. Price sensitivity is
     structurally unlearnable — the trait reaches the world only where it sets the outcome, so
     mutual information is zero ... Until households genuinely differ for reasons a supplier could
     in principle observe, every comparison returns 'the level is everything' and it is RIGHT —
     there is nothing to select on. The thesis is not unproven; it is untestable."

R1 and R2 are one programme in two halves, and the map already encodes the order: R2's headline
atom `C29_decisions_stop_being_lookup_tables` is blocked ON the R1 atoms, with the reason measured
rather than asserted — "a decision surface widened against a flat world produces a better-
instrumented null ... the choosing is worth -£175".

So the ceiling comes first, on the director's own instruction: *"Take the ceiling measurement before
the build, as you did on EP13."* If the ceiling is at the floor, no amount of R2 — richer dunning,
per-customer acquisition, a wider retention surface — can pay, because there is nothing to condition
on. If it is not at the floor, the ceiling says how much is on the table before a line is written.

THE THREE RUNGS, one process, one split, scored the same way:

    baseline        no inference at all. A supplier that treats every household as the mean.
                    Correlation 0 by construction; carried so the others have a floor to beat.
    input_ceiling   the best possible function of THE COMPANY'S OWN OBSERVABLES. Bounds every
                    inference model buildable on the book — however clever its features, its
                    estimator or its training. This is the number R1's claim is about.
    null_ceiling    the input ceiling refitted against a SHUFFLED target. The rung that makes the
                    other two falsifiable: with the pairing destroyed the fit must collapse, and a
                    gain smaller than this rung's spread is not a gain.

THE TRAP THIS INSTRUMENT IS MOST LIKELY TO FALL INTO, named because it returns the answer the canon
predicts. Ground truth is `price_elasticity_for_customer(customer_id, base_seed)`, and a WRONG SEED
yields a trait unrelated to the one the world used — random labels, a ceiling of zero, and an
apparent confirmation of R1 that is really a measurement of nothing. `live_population.run_base_seed`
exists for exactly this reason and its own docstring says so. So the seed is resolved from the
loaded population, never from a module default, and `control_traits_are_the_worlds` refuses a run
whose recovered traits are degenerate.
"""
from __future__ import annotations

import glob
import json
import math
import os
import random
import statistics
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
OUT_PATH = PROJECT / "docs" / "observability" / "r1_inference_ceiling.json"

#: How many destroyed-pairing draws make the noise floor. The floor is the MAX over draws, because
#: the question the ceiling must answer is how high chance reaches, not where it sits on average.
NULL_DRAWS = 12
#: Fewest households a cell may hold and still be a population rather than a coincidence. At 4
#: per cell this instrument reported a held-out figure ABOVE its own in-sample one -- the signature
#: of a fit reading noise, and the reason this control exists rather than being trusted to judgement.
MIN_HOUSEHOLDS_PER_CELL = 8
#: Fewest distinct predictions a fit must emit to have been a fit at all. Three of eleven observables
#: scored exactly 0.0000 here, and the first guard written for it -- "refuse a feature whose spread
#: is zero" -- fired NEVER, because none of them is constant. They are SKEWED: an outlier sets the
#: upper bin edge and every remaining household falls in the lower bin, so the predictor emits one
#: value, `_corr` divides by a zero deviation and returns a silent 0.0 that reads exactly like
#: "measured, found nothing". The guard has to key on the DEGENERATE FIT, which is the actual
#: failure, not on the constant feature, which was my guess at it.
MIN_DISTINCT_PREDICTIONS = 2

#: Fields a SUPPLIER COULD SEE. Every one is on the company's own book or its own decision record —
#: consumption it meters, rates it set, arrears it observes, journeys it ran. Nothing here is a
#: simulation internal, and that is the whole discipline of the measurement: a ceiling computed on
#: inputs the company does not have would bound nothing it could ever build.
OBSERVABLE_FIELDS = (
    "unit_rate_gbp_per_mwh", "svt_rate_gbp_per_mwh", "rate_vs_svt_pct",
    "company_eac_kwh", "company_churn_estimate", "resentment_score",
    "perceived_bill_saving_gbp", "discount_pct", "expected_term_margin_gbp",
    "mean_recent_margin_rate", "portfolio_premium_pct",
)
#: Explicitly NOT observable, listed so the exclusion is checkable rather than trusted. Each is the
#: simulation's own hand: what the world rolled, not what the company saw.
GROUND_TRUTH_FIELDS = (
    "churn_probability", "realized_churn_probability", "random_roll",
    "sim_churn_probability", "true_eac_kwh", "market_switching_multiplier",
    "credit_bureau_true_creditworthy", "win_probability",
)


def newest_run_output() -> Path:
    runs = [p for p in glob.glob(str(PROJECT / "docs" / "reports" / "run_output_*.json"))
            if "latest" not in p]
    if not runs:
        raise SystemExit("REFUSED: no run output to measure against.")
    return Path(max(runs, key=os.path.getmtime))


def observable_rows(payload: dict) -> dict[str, dict[str, float]]:
    """customer_id -> the company-observable feature vector, averaged over that customer's rows.

    Averaged rather than taken at a point because the question is what a supplier could learn about
    a HOUSEHOLD over its life, not at one renewal. A per-renewal view would understate the ceiling
    by throwing away repeat observation, which is the supplier's main advantage.
    """
    acc: dict[str, dict[str, list[float]]] = {}
    for value in payload.values():
        if not (isinstance(value, list) and value and isinstance(value[0], dict)):
            continue
        for row in value:
            cid = row.get("customer_id")
            if not cid:
                continue
            bucket = acc.setdefault(cid, {})
            for field in OBSERVABLE_FIELDS:
                got = row.get(field)
                if isinstance(got, (int, float)) and not isinstance(got, bool):
                    bucket.setdefault(field, []).append(float(got))
    return {cid: {f: statistics.fmean(v) for f, v in fields.items() if v}
            for cid, fields in acc.items() if fields}


def true_traits(customer_ids) -> tuple[dict[str, float], int]:
    """The elasticity the WORLD used, resolved at the seed the book was drawn at.

    Never the module default: `live_population.run_base_seed`'s own docstring records that a
    consumer reaching for the default "is correct only for as long as nothing passes base_seed=,
    and it fails silently the day something does".
    """
    from simulation import live_population
    from simulation.population_draw import price_elasticity_for_customer

    live_population.live_population()          # draws the book, which SETS the run seed
    seed = live_population.run_base_seed()
    return {cid: float(price_elasticity_for_customer(cid, seed)) for cid in customer_ids}, seed


def _cellwise_ceiling(xs, ys, targets, cells: int, want_distinct: bool = False):
    """(held-out correlation, in-sample correlation) of the best cellwise function of (xs, ys).

    The best possible function of two coordinates IS the per-cell mean of the target, so this needs
    no estimator and cannot be beaten by one. Fit on even-indexed households, scored on odd — a
    household is never in both, so a memorised label cannot score.
    """
    if not xs:
        return (0.0, 0.0, 0) if want_distinct else (0.0, 0.0)
    def edges(v):
        lo, hi = min(v), max(v)
        return [lo + (hi - lo) * i / cells for i in range(cells + 1)] if hi > lo else [lo, lo + 1.0]
    ex, ey = edges(xs), edges(ys)
    def cell(x, y):
        bx = min(cells - 1, max(0, sum(1 for e in ex[1:-1] if x >= e)))
        by = min(cells - 1, max(0, sum(1 for e in ey[1:-1] if y >= e)))
        return bx, by
    fit_i = [i for i in range(len(xs)) if i % 2 == 0]
    score_i = [i for i in range(len(xs)) if i % 2 == 1]
    table: dict[tuple[int, int], list[float]] = {}
    for i in fit_i:
        table.setdefault(cell(xs[i], ys[i]), []).append(targets[i])
    grand = statistics.fmean([targets[i] for i in fit_i]) if fit_i else 0.0
    means = {k: statistics.fmean(v) for k, v in table.items()}

    def preds(idx):
        return [means.get(cell(xs[i], ys[i]), grand) for i in idx]

    def scored(idx):
        return _corr(preds(idx), [targets[i] for i in idx])
    if want_distinct:
        return scored(score_i), scored(fit_i), len(set(round(p, 12) for p in preds(score_i)))
    return scored(score_i), scored(fit_i)


def _corr(a, b) -> float:
    if len(a) < 3:
        return 0.0
    ma, mb = statistics.fmean(a), statistics.fmean(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da = math.sqrt(sum((x - ma) ** 2 for x in a))
    db = math.sqrt(sum((y - mb) ** 2 for y in b))
    return 0.0 if da == 0 or db == 0 else num / (da * db)


def score_one_feature(xs, ts, cells: int) -> dict:
    """The ceiling on a SINGLE observable, which is where the power is.

    A pair costs every household missing either field. In this book that is two thirds of it -- 214
    households become 71 -- and at 71 the instrument's own noise floor sits at the level of its best
    result. One feature at full coverage answers a narrower question with enough power to mean it.
    """
    held, insample, distinct = _cellwise_ceiling(xs, [0.0] * len(xs), ts, cells, want_distinct=True)
    if distinct < MIN_DISTINCT_PREDICTIONS:
        return {"n": len(xs), "held_out": None, "in_sample": None, "null": None,
                "clears": False, "refused": "degenerate fit: every household in one cell"}
    nulls = []
    for draw in range(NULL_DRAWS * 2):
        shuffled = list(ts)
        random.Random(draw).shuffle(shuffled)
        nulls.append(abs(_cellwise_ceiling(xs, [0.0] * len(xs), shuffled, cells)[0]))
    return {"n": len(xs), "held_out": round(held, 4), "in_sample": round(insample, 4),
            "null": round(max(nulls), 4), "clears": bool(abs(held) > max(nulls)), "refused": None}


def measure(cells: int = 2) -> dict:
    run = newest_run_output()
    payload = json.loads(run.read_text())
    obs = observable_rows(payload)
    traits, seed = true_traits(list(obs))

    constant_fields, single = [], []
    for f in OBSERVABLE_FIELDS:
        ids = [c for c in obs if f in obs[c]]
        if len(ids) < 40:
            continue
        xs = [obs[c][f] for c in ids]
        row = score_one_feature(xs, [traits[c] for c in ids], cells)
        if row.get("refused"):
            constant_fields.append(f"{f}: {row['refused']}")
        single.append({"feature": f, **row})
    single.sort(key=lambda r: -r["n"])
    full_n = max((r["n"] for r in single), default=0)
    at_full_power = [r for r in single if r["n"] == full_n]

    shared = [f for f in OBSERVABLE_FIELDS
              if sum(1 for c in obs if f in obs[c]) >= max(20, len(obs) // 4)]
    ranked = []
    for i, fx in enumerate(shared):
        for fy in shared[i + 1:]:
            ids = [c for c in obs if fx in obs[c] and fy in obs[c]]
            if len(ids) < 20:
                continue
            xs = [obs[c][fx] for c in ids]
            ys = [obs[c][fy] for c in ids]
            ts = [traits[c] for c in ids]
            held, insample = _cellwise_ceiling(xs, ys, ts, cells)
            # The null is the SAME fit against a destroyed pairing, drawn NULL_DRAWS times and taken
            # at its worst. Two corrections learned by getting both wrong here first: a ROTATION of
            # the target is not a destroyed pairing (it preserves the ordering the features may
            # themselves be ordered by, so it can score by structure rather than by chance), and a
            # SINGLE draw is one sample, not a floor -- the quantity the ceiling has to clear is how
            # high chance REACHES, which only repeated draws can show.
            nulls = []
            for draw in range(NULL_DRAWS):
                shuffled = list(ts)
                random.Random(draw).shuffle(shuffled)
                nulls.append(abs(_cellwise_ceiling(xs, ys, shuffled, cells)[0]))
            ranked.append({"x": fx, "y": fy, "n": len(ids), "held_out": round(held, 4),
                           "in_sample": round(insample, 4), "null": round(max(nulls), 4),
                           "null_mean": round(statistics.fmean(nulls), 4)})
    ranked.sort(key=lambda r: -abs(r["held_out"]))
    best = ranked[0] if ranked else {"held_out": 0.0, "null": 0.0, "n": 0}
    null_floor = max((abs(r["null"]) for r in ranked), default=0.0)
    spread = (statistics.pstdev(list(traits.values())) if len(traits) > 1 else 0.0)
    # Half the households are the fit side; they are what the cell means are built from.
    households_per_cell = (best.get("n", 0) / 2) / (cells * cells) if cells else 0.0

    return {
        "run_output": run.name,
        "single_feature_ceilings": single,
        "constant_fields_refused": constant_fields,
        "full_coverage_households": full_n,
        # THE VERDICT. Taken at full coverage only, because that is the only place this book has the
        # power to tell a ceiling from its own noise floor.
        "any_full_power_feature_clears_the_null": bool(any(r["clears"] for r in at_full_power)),
        "base_seed": seed,
        "households": len(obs),
        "observable_fields_used": shared,
        "cells_per_axis": cells,
        "pairs_scored": len(ranked),
        "best_pair": best,
        "top_pairs": ranked[:8],
        "null_floor_abs_max": round(null_floor, 4),
        "ceiling_clears_the_null": bool(abs(best.get("held_out", 0.0)) > null_floor),
        "controls": {
            # A wrong seed gives random labels and a ceiling of zero -- the answer the canon
            # predicts, from a measurement of nothing.
            "traits_are_the_worlds": bool(spread > 0.0 and len(set(traits.values())) > 2),
            "trait_spread": round(spread, 5),
            # The ceiling must be computed on what the COMPANY sees. If a simulation internal ever
            # reaches this list the bound stops describing anything buildable.
            "no_ground_truth_in_features": not (set(shared) & set(GROUND_TRUTH_FIELDS)),
            "held_out_is_disjoint_from_fit": True,
            # A cell holding a handful of households fits their noise and calls it a function.
            "cells_are_populations": bool(households_per_cell >= MIN_HOUSEHOLDS_PER_CELL),
            "households_per_cell": round(households_per_cell, 1),
        },
    }


def main() -> int:
    result = measure()
    c = result["controls"]
    print(f"run={result['run_output']}  seed={result['base_seed']}  households={result['households']}")
    print(f"observables used: {len(result['observable_fields_used'])}  pairs scored: {result['pairs_scored']}")
    print(f"trait spread (sd): {c['trait_spread']}   traits_are_the_worlds={c['traits_are_the_worlds']}")
    print()
    print("  SINGLE observable -> the household's true elasticity (all households carrying it)")
    for row in result["single_feature_ceilings"]:
        if row.get("refused"):
            print(f"    {row['feature']:<28} n={row['n']:>4}  REFUSED -- {row['refused']}")
            continue
        mark = "CLEARS" if row["clears"] else "noise"
        print(f"    {row['feature']:<28} n={row['n']:>4}  held {row['held_out']:+.4f}  "
              f"in-sample {row['in_sample']:+.4f}  null {row['null']:+.4f}  {mark}")
    print(f"\n  AT FULL COVERAGE (n={result['full_coverage_households']}), anything clears the null: "
          f"{result['any_full_power_feature_clears_the_null']}")
    print()
    print("  best functions of the company's own observables -> the household's true elasticity")
    for row in result["top_pairs"]:
        print(f"    held-out {row['held_out']:+.4f}  (in-sample {row['in_sample']:+.4f}, "
              f"null {row['null']:+.4f}, n={row['n']})  {row['x']} x {row['y']}")
    print()
    print(f"  INPUT CEILING (best held-out) : {result['best_pair'].get('held_out', 0.0):+.4f}")
    print(f"  null floor (|max| over pairs) : {result['null_floor_abs_max']:+.4f}")
    print(f"  ceiling clears the null       : {result['ceiling_clears_the_null']}")
    print(f"  cells are populations         : {c['cells_are_populations']} "
          f"({c['households_per_cell']} households/cell on the fit side)")
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"\nwrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
