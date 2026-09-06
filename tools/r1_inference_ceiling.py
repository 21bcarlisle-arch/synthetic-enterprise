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

AND THE NULL HAS TO CONTAIN THE SEARCH (added 2026-09-06, after the figure had been published for
two days). The pairwise rung scores 45 candidate pairs, ranks them, and reports the winner. A null
drawn for one pair answers "could THIS pair have arisen by chance"; the sweep asks "could the BEST
OF 45 have", and the maximum of 45 noise draws sits far out in the tail of any single one. So the
null re-runs the WHOLE selection -- shuffle the household -> trait assignment across the book,
re-score every pair, keep the winner, 200 times -- and the reported figure is graded against that
distribution. `selection_corrected_null` holds it, and both figures stay in the output because
deleting the flattering one hides that it was ever reported.

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
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
OUT_PATH = PROJECT / "docs" / "observability" / "r1_inference_ceiling.json"

#: How many destroyed-pairing draws make the noise floor. The floor is the MAX over draws, because
#: the question the ceiling must answer is how high chance reaches, not where it sits on average.
NULL_DRAWS = 12
#: Draws of the WHOLE ranked sweep against a shuffled world. Each draw re-runs all 45 pairs and
#: keeps the WINNER, so the distribution is of the quantity actually reported -- a selected maximum
#: -- rather than of one comparison. 200 is set by what it has to resolve: the verdict turns on the
#: 95th percentile and on a p-value against 0.05, and 200 draws put ten of them above that line.
SELECTION_NULL_DRAWS = 200
#: The level a selected maximum has to clear. Named rather than inlined because the whole point of
#: the correction is that the threshold is a decision, made once, in view.
SELECTION_ALPHA = 0.05
#: Fewest households a run output must yield before this instrument will report anything at all.
#: FAIL CLOSED, and learned in this worktree: a linked checkout carries no gitignored run outputs,
#: `newest_run_output` picked a 214-household file's tracked stand-in with ZERO usable rows, and the
#: instrument returned `households: 0, pairs: 0, ceiling +0.0000, clears False` -- which reads
#: exactly like "measured the book, found nothing" and is the opposite claim to "measured nothing".
MIN_HOUSEHOLDS = 40
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


def _sweep_winner(grid, traits: dict[str, float], cells: int) -> float:
    """|held-out| of the candidate THE RANKED SWEEP WOULD REPORT, under this trait assignment.

    The sweep's report is `max(abs(held_out))` over the grid, so that maximum -- not any individual
    candidate's score -- is the statistic whose distribution the verdict needs.
    """
    best = 0.0
    for cand in grid:
        ts = [traits[c] for c in cand["ids"]]
        best = max(best, abs(_cellwise_ceiling(cand["xs"], cand["ys"], ts, cells)[0]))
    return best


def selection_corrected_null(grid, traits: dict[str, float], cells: int,
                             draws: int = SELECTION_NULL_DRAWS) -> dict | None:
    """The null of the SELECTION, not of one comparison.

    THE DEFECT THIS EXISTS TO REPAIR, and it was published under Poesys's name for two days. The
    pairwise sweep scored 45 pairs, ranked them by `abs(held_out)`, reported the winner as the input
    ceiling, and graded that winner against a null drawn FOR THAT PAIR ALONE. Choosing the best of 45
    and comparing it to a one-comparison null is guaranteed to flatter: the maximum of 45 noise draws
    is far out in the tail of any one of them. The signature was in the output the whole time --
    held-out +0.5661 against in-sample +0.1724, a fit scoring three times better on households it
    never saw, which no real fit does.

    THE CORRECTION IS TO RE-RUN THE PROCEDURE, not to adjust the answer. One draw here shuffles the
    household -> trait assignment across the WHOLE book, re-scores every candidate in the grid on the
    shuffled world, and keeps the winner. Two properties of that shape are what make it the same
    procedure, and both were got wrong in earlier nulls in this file:

      - the shuffle is at HOUSEHOLD level and world-wide, so every candidate in a draw sees the SAME
        shuffled world. Shuffling each candidate's target independently would break the correlation
        BETWEEN candidates and understate how high the maximum reaches.
      - the grid is fixed once, before any draw, so candidate eligibility cannot move with the
        target. A sweep whose membership depended on the shuffled target would be a different
        procedure each draw and the distribution would describe none of them.

    Returns the distribution, never a verdict: the caller compares its own observed statistic.
    """
    ids = sorted({c for cand in grid for c in cand["ids"]})
    if not grid or len(ids) < 3:
        return None
    values = [traits[c] for c in ids]
    winners = []
    for draw in range(draws):
        permuted = list(values)
        random.Random(90_000 + draw).shuffle(permuted)
        winners.append(_sweep_winner(grid, dict(zip(ids, permuted)), cells))
    winners.sort()

    def pct(p: float) -> float:
        return winners[max(0, min(len(winners) - 1, math.ceil(p * len(winners)) - 1))]

    return {
        "draws": draws,
        "candidates_per_draw": len(grid),
        "households_shuffled": len(ids),
        "mean": round(statistics.fmean(winners), 4),
        "median": round(pct(0.5), 4),
        "p95": round(pct(0.95), 4),
        "max": round(winners[-1], 4),
        "_winners": winners,
    }


def graded_against_selection(observed: float, null: dict | None) -> dict:
    """The verdict, with its p-value, its bound and -- when it refuses -- its reason.

    `(1 + exceedances) / (1 + draws)` rather than `exceedances / draws`: a permutation p-value that
    can return exactly 0 claims a certainty 200 draws cannot buy, and 0 is what would get published.
    """
    if null is None:
        return {"clears": None, "why_no_verdict": "no candidate grid to select over"}
    winners = null["_winners"]
    exceed = sum(1 for w in winners if w >= abs(observed))
    p_value = (1 + exceed) / (1 + len(winners))
    return {
        "observed": round(abs(observed), 4),
        "exceedances": exceed,
        "p_value": round(p_value, 4),
        "alpha": SELECTION_ALPHA,
        "bound_p95": null["p95"],
        "clears": bool(p_value <= SELECTION_ALPHA),
        # HOW MUCH ROOM THE VERDICT HAS, because a boolean at alpha hides everything about how
        # close the call was, and this one is close: the same correction reverses on a book drawn
        # two days earlier. A margin worth a tenth of the figure is not a bound to gate a
        # programme on, and a reader who only gets `clears: true` cannot know that.
        "margin_over_bound": round(abs(observed) - null["p95"], 4),
    }


def _headline(best: dict, pair_verdict: dict, full_verdict: dict, full_n: int,
              pairs: int) -> dict:
    """The sentence a reader gets, composed HERE so the page cannot compose a kinder one.

    "We cannot tell" is a result and it belongs on the surface, not in a footnote -- and it is a
    different claim from "there is nothing there". A refusal published without the bound the sample
    size earns will be read as the second, so the bound travels with it in the same object.
    """
    observed = abs(best.get("held_out", 0.0) or 0.0)
    bound = pair_verdict.get("bound_p95")
    p = pair_verdict.get("p_value")
    clears = pair_verdict.get("clears")
    if clears is None:
        return {"verdict": "unavailable",
                "statement": "There was no sweep to grade, so no ceiling is reported.",
                "what_it_does_not_say": "", "bound_p95": bound, "p_value": p}
    if clears:
        statement = (
            f"The best function of the company's own observables recovers {observed:+.4f} of a "
            f"household's true price sensitivity, and it SURVIVES the correction on this book: "
            f"after re-running the whole best-of-{pairs} selection against {SELECTION_NULL_DRAWS} "
            f"shuffled worlds, chance reached that high in {pair_verdict.get('exceedances')} of "
            f"them (p={p}). It clears by {pair_verdict.get('margin_over_bound'):+.4f} — about a "
            f"tenth of the figure itself — so this is a marginal pass, not a bound.")
    else:
        statement = (
            f"WE CANNOT TELL. The headline figure of {observed:+.4f} is the winner of a "
            f"{pairs}-way search, and when the SAME search is re-run against "
            f"{SELECTION_NULL_DRAWS} shuffled "
            f"worlds -- households' true sensitivities dealt out at random -- the winner reaches "
            f"{bound:+.4f} at the 95th percentile and matched or beat the real figure in "
            f"{pair_verdict.get('exceedances')} of them (p={p}). The measurement cannot separate "
            f"this ceiling from chance, so we report no ceiling.")
    # THE CAVEAT HAS TO BRANCH WITH THE VERDICT. A refusal read as "there is nothing there" and a
    # marginal pass read as "the bound is established" are the same failure from opposite sides,
    # and one sentence cannot carry both. Only what this run MEASURED goes in either branch.
    power = (f"The pair rung carries {best.get('n', 0)} households, and at that size only a "
             f"ceiling above {bound:+.4f} can be told from chance at all -- so a real effect of "
             "moderate size is invisible to this instrument either way. The separate "
             f"full-coverage rung (n={full_n}) reads "
             f"{'clears' if full_verdict.get('clears') else 'cannot tell'} on the same correction, "
             "and the two rungs disagreeing is itself a reason to hold the number loosely.")
    if clears:
        not_said = ("This does not establish a bound. It is a marginal pass on one book, clearing "
                    f"by {pair_verdict.get('margin_over_bound', 0.0):+.4f}, and a figure that "
                    "clears by a tenth of itself will move with the next draw of the book. " + power)
    else:
        not_said = ("This is not a finding that price sensitivity is unlearnable. It is a refusal "
                    "to distinguish, which is a different claim. " + power)
    return {
        "verdict": "clears" if clears else "cannot tell",
        "statement": statement,
        "what_it_does_not_say": not_said,
        "bound_p95": bound,
        "p_value": p,
    }


def _pair_grid(obs: dict, shared, min_ids: int = 20) -> list[dict]:
    """Every pair the sweep scores, with its households and columns FIXED BEFORE ANY DRAW."""
    grid = []
    for i, fx in enumerate(shared):
        for fy in shared[i + 1:]:
            ids = [c for c in obs if fx in obs[c] and fy in obs[c]]
            if len(ids) < min_ids:
                continue
            grid.append({"x": fx, "y": fy, "ids": ids,
                         "xs": [obs[c][fx] for c in ids], "ys": [obs[c][fy] for c in ids]})
    return grid


def measure(cells: int = 2, run_path: Path | None = None) -> dict:
    run = run_path or newest_run_output()
    payload = json.loads(run.read_text())
    obs = observable_rows(payload)
    if len(obs) < MIN_HOUSEHOLDS:
        raise SystemExit(
            f"REFUSED: {run.name} yields {len(obs)} households with observable rows, under the "
            f"{MIN_HOUSEHOLDS} this instrument needs. Reporting a ceiling of 0.0 from an empty book "
            "would read as 'measured the book, found nothing', which is the opposite claim. In a "
            "linked worktree this is what a missing gitignored run output looks like -- pass "
            "--run <path> pointing at the tree that holds the real one.")
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
    grid = _pair_grid(obs, shared)
    ranked = []
    for cand in grid:
        ts = [traits[c] for c in cand["ids"]]
        held, insample = _cellwise_ceiling(cand["xs"], cand["ys"], ts, cells)
        # THIS NULL IS THE UNCORRECTED ONE AND IS KEPT ON PURPOSE. It is the SAME fit against a
        # destroyed pairing, drawn NULL_DRAWS times and taken at its worst -- honest for the
        # question "could THIS pair have arisen by chance", and wrong for the question the sweep
        # actually answers, which is "could the BEST OF 45 have". Both are published side by side
        # because deleting the flattering figure hides that it was ever reported; the readable pair
        # is what shows the size of the correction. Two smaller corrections are already inside it: a
        # ROTATION of the target is not a destroyed pairing (it preserves the ordering the features
        # may themselves be ordered by), and a SINGLE draw is one sample, not a floor.
        nulls = []
        for draw in range(NULL_DRAWS):
            shuffled = list(ts)
            random.Random(draw).shuffle(shuffled)
            nulls.append(abs(_cellwise_ceiling(cand["xs"], cand["ys"], shuffled, cells)[0]))
        ranked.append({"x": cand["x"], "y": cand["y"], "n": len(cand["ids"]),
                       "held_out": round(held, 4), "in_sample": round(insample, 4),
                       "null_this_pair_alone": round(max(nulls), 4),
                       "null_mean": round(statistics.fmean(nulls), 4)})
    ranked.sort(key=lambda r: -abs(r["held_out"]))
    best = ranked[0] if ranked else {"held_out": 0.0, "null_this_pair_alone": 0.0, "n": 0}
    null_floor = max((abs(r["null_this_pair_alone"]) for r in ranked), default=0.0)

    # THE CORRECTED NULL: the same choose-the-best-of-N the reported figure survived, run against a
    # shuffled world 200 times. Done for BOTH rungs, because the full-coverage verdict is also a
    # maximum -- `any(...)` over the full-coverage features is a selection over a smaller N, and
    # correcting only the rung that embarrassed us would leave the same defect in the rung that
    # carries the verdict.
    pair_null = selection_corrected_null(grid, traits, cells)
    pair_verdict = graded_against_selection(best.get("held_out", 0.0), pair_null)

    full_grid = [{"x": r["feature"], "y": None,
                  "ids": [c for c in obs if r["feature"] in obs[c]],
                  "xs": [obs[c][r["feature"]] for c in obs if r["feature"] in obs[c]],
                  "ys": [0.0] * sum(1 for c in obs if r["feature"] in obs[c])}
                 for r in at_full_power if not r.get("refused")]
    full_null = selection_corrected_null(full_grid, traits, cells)
    full_observed = max((abs(r["held_out"]) for r in at_full_power
                         if r.get("held_out") is not None), default=0.0)
    full_verdict = graded_against_selection(full_observed, full_null)
    for block in (pair_null, full_null):
        if block is not None:
            block.pop("_winners", None)

    spread = (statistics.pstdev(list(traits.values())) if len(traits) > 1 else 0.0)
    # Half the households are the fit side; they are what the cell means are built from.
    households_per_cell = (best.get("n", 0) / 2) / (cells * cells) if cells else 0.0

    return {
        "run_output": run.name,
        "single_feature_ceilings": single,
        "constant_fields_refused": constant_fields,
        "full_coverage_households": full_n,
        # THE VERDICT. Taken at full coverage only, because that is the only place this book has the
        # power to tell a ceiling from its own noise floor -- and taken against the SELECTION-
        # corrected null, because `any(...)` over the full-coverage features is itself a maximum.
        # The uncorrected per-feature reading is kept beside it under its own name.
        "any_full_power_feature_clears_the_selection_corrected_null": full_verdict.get("clears"),
        "any_full_power_feature_clears_its_own_null_uncorrected":
            bool(any(r["clears"] for r in at_full_power)),
        "full_power_selection": {"observed": round(full_observed, 4), **full_verdict,
                                 "null": full_null},
        "base_seed": seed,
        "households": len(obs),
        "observable_fields_used": shared,
        "cells_per_axis": cells,
        "pairs_scored": len(ranked),
        "best_pair": best,
        "top_pairs": ranked[:8],
        "null_floor_abs_max": round(null_floor, 4),
        # THE HEADLINE, and it is the corrected one. `ceiling_clears_the_null` kept its NAME and
        # changed its MEANING on 2026-09-06, deliberately: every reader and every downstream record
        # asks that field the question "is the ceiling real", and the honest answer to that question
        # is the selection-corrected one. The old computation is kept, under a name that says what
        # it is, so the two are readable together rather than one quietly replacing the other.
        "ceiling_clears_the_null": pair_verdict.get("clears"),
        "ceiling_clears_the_null_uncorrected_per_pair":
            bool(abs(best.get("held_out", 0.0)) > null_floor),
        "selection_corrected_null": pair_null,
        "selection_corrected_verdict": pair_verdict,
        "we_cannot_tell": _headline(best, pair_verdict, full_verdict, full_n, len(ranked)),
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
            # THE SELECTION IS PART OF THE PROCEDURE, so the null has to contain it. False here
            # means the reported figure is a maximum graded against a single comparison.
            "the_null_ran_the_same_selection": bool(
                pair_null is not None
                and pair_null["candidates_per_draw"] == len(ranked)
                and pair_null["draws"] == SELECTION_NULL_DRAWS),
            # A fit cannot honestly score better on households it never saw. When it does, across
            # the board, the rung is reading noise however its null grades it.
            "held_out_exceeds_in_sample_on_most_pairs": bool(
                ranked and sum(1 for r in ranked
                               if abs(r["held_out"]) > abs(r["in_sample"])) > len(ranked) / 2),
        },
    }


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    run_path = None
    if "--run" in argv:
        # A LINKED WORKTREE HAS NO GITIGNORED RUN OUTPUTS, so the tree that holds the real book has
        # to be nameable. Reading a run output from another tree is safe; writing to one is not,
        # and this only ever reads.
        run_path = Path(argv[argv.index("--run") + 1]).expanduser().resolve()
        if not run_path.is_file():
            raise SystemExit(f"REFUSED: --run {run_path} is not a file.")
    result = measure(run_path=run_path)
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
    fp = result["full_power_selection"]
    print(f"\n  AT FULL COVERAGE (n={result['full_coverage_households']})")
    print(f"    uncorrected (each feature vs its own null) : "
          f"{result['any_full_power_feature_clears_its_own_null_uncorrected']}")
    print(f"    selection-corrected (best-of-{(fp.get('null') or {}).get('candidates_per_draw', 0)} "
          f"vs the same selection) : "
          f"{result['any_full_power_feature_clears_the_selection_corrected_null']}"
          f"   (observed {fp.get('observed', 0.0):+.4f}, p95 bound "
          f"{fp.get('bound_p95') if fp.get('bound_p95') is not None else float('nan'):+.4f}, "
          f"p={fp.get('p_value')})")
    print()
    print("  best functions of the company's own observables -> the household's true elasticity")
    for row in result["top_pairs"]:
        print(f"    held-out {row['held_out']:+.4f}  (in-sample {row['in_sample']:+.4f}, "
              f"null-this-pair-alone {row['null_this_pair_alone']:+.4f}, n={row['n']})  "
              f"{row['x']} x {row['y']}")
    print()
    # THE TWO FIGURES SIDE BY SIDE. The uncorrected one is not deleted: printing it beside its
    # correction is the only way a reader can see how much of the headline was the search.
    sel, ver = result["selection_corrected_null"], result["selection_corrected_verdict"]
    print(f"  reported ceiling (best held-out)           : "
          f"{result['best_pair'].get('held_out', 0.0):+.4f}  over {result['pairs_scored']} pairs")
    print("  UNCORRECTED -- graded against ONE pair's null")
    print(f"    null floor (|max| over pairs)            : {result['null_floor_abs_max']:+.4f}")
    print(f"    clears                                   : "
          f"{result['ceiling_clears_the_null_uncorrected_per_pair']}")
    print(f"  CORRECTED -- graded against the SAME best-of-{result['pairs_scored']} selection")
    if sel:
        print(f"    shuffled worlds                          : {sel['draws']}  "
              f"({sel['households_shuffled']} households dealt out at random each time)")
        print(f"    winner of the sweep under chance          : median {sel['median']:+.4f}  "
              f"p95 {sel['p95']:+.4f}  max {sel['max']:+.4f}")
        print(f"    chance matched or beat the real figure    : {ver['exceedances']}/{sel['draws']} "
              f"draws   p={ver['p_value']}  (alpha {ver['alpha']})")
    print(f"    clears                                   : {result['ceiling_clears_the_null']}")
    print()
    print(f"  VERDICT: {result['we_cannot_tell']['statement']}")
    print(f"  {result['we_cannot_tell']['what_it_does_not_say']}")
    print()
    print(f"  cells are populations         : {c['cells_are_populations']} "
          f"({c['households_per_cell']} households/cell on the fit side)")
    print(f"  the null ran the same selection: {c['the_null_ran_the_same_selection']}")
    print(f"  held-out beats in-sample on most pairs (the noise tell): "
          f"{c['held_out_exceeds_in_sample_on_most_pairs']}")
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"\nwrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
