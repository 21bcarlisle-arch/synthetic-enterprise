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
import itertools
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
#: Folds in the split that estimates the MAGNITUDE. Three, and the third one is the whole point: two
#: folds can fit and score, but the fold that SELECTS the winner is the fold that holds the maximum,
#: so a figure reported from it is a maximum however honestly the fit was held out.
SPLIT_FOLDS = 3
#: Fewest households a fold may hold and still be scored at all. Matched to `_pair_grid`'s own
#: `min_ids`: a candidate too small to enter the sweep is too small to estimate from.
MIN_FOLD_HOUSEHOLDS = 20

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
#: WHERE EACH OBSERVABLE COMES FROM IN THE COMPANY'S OWN RECORD, and it is not one kind of thing.
#: Declared per field, in view, BEFORE any run, because the difference decides what a low coverage
#: number MEANS -- and reading it wrong is what kept this instrument's pair rung refusing for want
#: of households while the book sat at 164.
#:
#:   `account_state`   the company holds it for every account on supply in every period, whether or
#:                     not anything happened to that account. `simulation/run_phase2b.py` writes it
#:                     to `account_state_log`. Coverage short of the whole book is a DEFECT.
#:   `decision_only`   it exists only where a decision was reached, and for most of them that
#:                     decision is a renewal on a fixed electricity term -- which most of this
#:                     book's households never have. Coverage short of the whole book is the TRUTH
#:                     about the field, and manufacturing a value for an account that never renewed
#:                     would invent the coverage rather than record it.
#:
#: The distinction is the whole point of the record: `company_eac_kwh` at 69 of 164 households was
#: an accounting accident (the company computed it, then only wrote it down at renewals), whereas
#: `discount_pct` at 35 is what a discount IS. One is worth fixing and the other is worth naming.
#: `run_phase2b`'s `account_state_log` comment points AT this table for exactly that reason.
OBSERVABLE_FIELD_SCOPE = {
    "unit_rate_gbp_per_mwh": ("account_state", "what the company charges this account now"),
    "svt_rate_gbp_per_mwh": ("account_state",
                             "the published default-tariff cap on the day, PER FUEL. Read this "
                             "field's coverage against the run that produced it: until 2026-09-06 "
                             "the world wrote it for electricity legs only, so 146-of-164 was a "
                             "missing READ and not the field's own scope"),
    "rate_vs_svt_pct": ("account_state", "the spread between the two above"),
    "company_eac_kwh": ("account_state",
                        "the company's own estimate of annual consumption, from twelve months of "
                        "its own billing -- held continuously, previously written only at renewal"),
    "company_churn_estimate": ("decision_only",
                               "`estimate_renewal_churn` takes an old rate AND a new one, so it "
                               "exists at a renewal and nowhere else"),
    "resentment_score": ("decision_only",
                         "the journey register advances in a renewal window; an account with no "
                         "renewal has no journey to read"),
    "perceived_bill_saving_gbp": ("decision_only",
                                  "a renewal-window quantity: what THIS renewal appears to save "
                                  "against the rate it replaced"),
    "discount_pct": ("decision_only", "an offer artefact -- there is no discount without an offer"),
    "expected_term_margin_gbp": ("decision_only",
                                 "priced at the offer, against the offer's own term"),
    "mean_recent_margin_rate": ("account_state",
                                "the portfolio position the pricing chain reads at every priced "
                                "term, carried by `account_state_log` since 2026-09-06"),
    "portfolio_premium_pct": ("account_state", "likewise, per priced term"),
}
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
    """household -> the company-observable feature vector, averaged over that household's rows.

    Averaged rather than taken at a point because the question is what a supplier could learn about
    a HOUSEHOLD over its life, not at one renewal. A per-renewal view would understate the ceiling
    by throwing away repeat observation, which is the supplier's main advantage.

    KEYED ON THE HOUSEHOLD AND NOT ON `customer_id`, and that is a correction, measured 2026-09-06.
    A run output's `customer_id` is a SUPPLY POINT, and a household's gas leg is registered under its
    electricity point's id plus a suffix -- `C1` and `C1g` are one property. Two of this file's log
    families key on different halves of that: `dynamic_pricing_log` and `rate_decomposition_log`
    write the supply point, while `churn_journey_log`, `churn_basis_risk` and `demand_estimation_log`
    write `household_of(cid)`, which `run_phase2b` calls the billing account. Keying on the raw id
    therefore split one book two ways and the instrument could not join them.

    WHAT IT COST, on run_output_f53c90b85. The instrument reported 213 households; there were 149.
    82 of those 213 rows were gas legs -- 64 the second copy of a dual-fuel household already in the
    book, 18 the only row of a gas-only account -- and every one of the 82 was graded against a
    target drawn by hashing the LEG id. `price_elasticity_for_customer` answers for any string at
    all, so `C1g` came back with 0.5255 while the 1.6043 the world actually gave that household sat
    in a different row. 38% of the target column was noise correctly matched to nothing. The
    full-coverage rung has read `cannot tell` at p=0.85 all along, and this is why: it was never a
    coverage result. Folding the 64 duplicates is what takes 213 to 149; re-keying the other 18 is
    what gives them a truth to be graded against.

    A FIELD ON BOTH LEGS IS AVERAGED OVER THE HOUSEHOLD'S PRICED TERMS, unweighted, so a household
    with thirty electricity terms and five gas ones is mostly its electricity. That is the supplier's
    own margin on that household and it is the quantity the docstring above already claimed to
    return. The alternative -- one row per commodity -- was rejected because the TARGET is a
    household trait: the world draws one price elasticity per property, so a per-leg row has no
    truth to be graded against, which is the defect being fixed and not a second reading of it.
    """
    acc: dict[str, dict[str, list[float]]] = {}
    for value in payload.values():
        if not (isinstance(value, list) and value and isinstance(value[0], dict)):
            continue
        for row in value:
            cid = row.get("customer_id")
            if not cid:
                continue
            bucket = acc.setdefault(_household_key(cid), {})
            for field in OBSERVABLE_FIELDS:
                got = row.get(field)
                if isinstance(got, (int, float)) and not isinstance(got, bool):
                    bucket.setdefault(field, []).append(float(got))
    return {cid: {f: statistics.fmean(v) for f, v in fields.items() if v}
            for cid, fields in acc.items() if fields}


def _household_key(supply_point_id: str) -> str:
    """The household a run output's `customer_id` belongs to. One import site, so the seam this
    instrument was missing is nameable rather than spelled out at three call sites."""
    from simulation.household import household_of

    return household_of(supply_point_id)


def leg_fold_census(payload: dict) -> dict[str, int]:
    """What the household key folded, published so the correction is visible rather than silent.

    A count that goes to zero is the honest reading of a book with no dual-fuel households in it,
    and a count that RISES is the reading of a book that grew them. Neither is an error, so this is
    reported and never asserted on: the control that can fail is `every_graded_row_is_a_household`.
    """
    points: set[str] = set()
    for value in payload.values():
        if not (isinstance(value, list) and value and isinstance(value[0], dict)):
            continue
        for row in value:
            cid = row.get("customer_id")
            if cid:
                points.add(cid)
    households = {_household_key(p) for p in points}
    return {
        "supply_points_in_the_run_output": len(points),
        "households_they_belong_to": len(households),
        "supply_point_legs_folded_into_a_household": len(points) - len(households),
    }


def field_provenance(payload: dict) -> dict[str, dict]:
    """Which record carried each observable, how many households it reached, and whether that
    coverage is a DEFECT or a FACT.

    Published rather than asserted on, because the number itself is not the finding: a field at 69
    of 164 is a bookkeeping accident if its scope is `account_state` and the honest truth about the
    field if its scope is `decision_only`. Naming the record it came from is what lets a reader
    check the scope declaration against the world instead of taking it on trust.
    """
    per_field: dict[str, dict[str, set]] = {f: {} for f in OBSERVABLE_FIELDS}
    for record_name, value in payload.items():
        if not (isinstance(value, list) and value and isinstance(value[0], dict)):
            continue
        for row in value:
            cid = row.get("customer_id")
            if not cid:
                continue
            for field in OBSERVABLE_FIELDS:
                got = row.get(field)
                if isinstance(got, (int, float)) and not isinstance(got, bool):
                    per_field[field].setdefault(record_name, set()).add(_household_key(cid))
    out = {}
    for field, records in per_field.items():
        scope, why = OBSERVABLE_FIELD_SCOPE.get(field, ("undeclared", "no scope declared"))
        union: set[str] = set()
        for ids in records.values():
            union |= ids
        out[field] = {
            "scope": scope,
            "why": why,
            "households": len(union),
            "records": {name: len(ids) for name, ids in sorted(records.items())},
        }
    return out


def whole_book_fields(fields) -> list[str]:
    """Of `fields`, the ones the company holds for EVERY account on supply.

    A named function and not an inline comprehension so the partition it draws can be driven by a
    control. The distinction it applies is `OBSERVABLE_FIELD_SCOPE`'s and is declared in this file
    above, before any run: a field whose scope is not `account_state` is one that exists only where
    a decision fired, and a rung built on it can only ever carry the accounts that reached that
    decision -- 69 of 164 on this book, however large the book gets.

    AN UNDECLARED FIELD IS EXCLUDED, which is fail-closed and deliberate: a new observable added to
    `OBSERVABLE_FIELDS` and not to the scope table would otherwise be silently treated as
    whole-book, and the rung would quietly go back to being renewal-shaped with nothing to say so.
    `test_every_observable_declares_a_scope_and_the_declaration_is_a_partition` is what stops that
    exclusion from being how the gap gets lived with.
    """
    return [f for f in fields
            if OBSERVABLE_FIELD_SCOPE.get(f, ("undeclared", ""))[0] == "account_state"]


def true_traits(customer_ids) -> tuple[dict[str, float], int]:
    """The elasticity the WORLD used, resolved at the seed the book was drawn at.

    Never the module default: `live_population.run_base_seed`'s own docstring records that a
    consumer reaching for the default "is correct only for as long as nothing passes base_seed=,
    and it fails silently the day something does".

    AND IT REFUSES A SUPPLY-POINT LEG, because the lookup underneath cannot.
    `price_elasticity_for_customer` is a hash of the id and answers for ANY string -- ask it for
    `NOT_A_REAL_ID` and it returns 1.4223, in range, with the right shape, from nothing. So a gas leg
    `C1g` came back with an elasticity that belongs to no household in the world, and it was
    indistinguishable at every downstream rung from the real one. The world draws ONE elasticity per
    property; an id that is a leg of another household has no truth to be graded against, and the
    only place that can be seen is here, at the point the target column is built.

    NOT a membership test against the drawn book, which is the check I wrote first and deleted: a
    successor registration after a home move (`C3_2`) is a household this run created and the drawn
    book has never heard of, so book membership would refuse a real household and shrink the very
    coverage this measurement is short of. The property is `household_of(cid) == cid`, which is
    true of `C3_2` and false of `C1g` -- it asks whether the id is a household, not whether it is
    one we started with.
    """
    from simulation import live_population
    from simulation.population_draw import price_elasticity_for_customer

    customer_ids = list(customer_ids)
    legs = sorted(c for c in customer_ids if _household_key(c) != c)
    if legs:
        raise SystemExit(
            f"REFUSED: {len(legs)} of {len(customer_ids)} ids to be graded are supply-point legs of "
            f"another household ({', '.join(legs[:5])}). The elasticity lookup would answer for "
            "every one of them -- it hashes the id and has no roster to consult -- and the ceiling "
            "would then be graded against a target column that is part real and part invented, "
            "which reads exactly like a real measurement that found nothing. Key the observables on "
            "`household_of(customer_id)` before calling this.")

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
    fit_i = [i for i in range(len(xs)) if i % 2 == 0]
    score_i = [i for i in range(len(xs)) if i % 2 == 1]
    preds = _cell_predictor(xs, ys, targets, cells, fit_i)

    def scored(idx):
        return _corr(preds(idx), [targets[i] for i in idx])
    if want_distinct:
        return scored(score_i), scored(fit_i), len(set(round(p, 12) for p in preds(score_i)))
    return scored(score_i), scored(fit_i)


def _cell_predictor(xs, ys, targets, cells: int, fit_i):
    """The best cellwise function of (xs, ys) fitted on `fit_i` ALONE. Returns `preds(idx)`.

    EXTRACTED FROM `_cellwise_ceiling`, not newly invented, because the three-way split needs the
    SAME fitted table scored on two different held-out folds. Re-fitting per fold would give two
    different functions, and then the fold that SELECTED a candidate would not be describing the fit
    the estimating fold scores — which is the entire property the three-way split exists to buy.

    Bin edges come from the whole column rather than from the fit fold, which is what this file has
    always done and is kept deliberately: the edges read the FEATURE's range only, never the target,
    so no label crosses the split. Narrowing them to the fit fold would change every existing figure
    for a reason unrelated to the defect being repaired.
    """
    def edges(v):
        lo, hi = min(v), max(v)
        return [lo + (hi - lo) * i / cells for i in range(cells + 1)] if hi > lo else [lo, lo + 1.0]

    ex, ey = edges(xs), edges(ys)

    def cell(x, y):
        bx = min(cells - 1, max(0, sum(1 for e in ex[1:-1] if x >= e)))
        by = min(cells - 1, max(0, sum(1 for e in ey[1:-1] if y >= e)))
        return bx, by

    table: dict[tuple[int, int], list[float]] = {}
    for i in fit_i:
        table.setdefault(cell(xs[i], ys[i]), []).append(targets[i])
    grand = statistics.fmean([targets[i] for i in fit_i]) if fit_i else 0.0
    means = {k: statistics.fmean(v) for k, v in table.items()}

    def preds(idx):
        return [means.get(cell(xs[i], ys[i]), grand) for i in idx]

    return preds


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


def global_folds(ids, folds: int = SPLIT_FOLDS) -> dict[str, int]:
    """household -> fold, assigned ONCE for the whole book.

    GLOBAL is the load-bearing word. Assigning folds inside each candidate would put a household on
    the SELECTING side of one pair and the ESTIMATING side of another; the selection ranges over all
    45 pairs at once, so that household's target would reach the estimate through a candidate it had
    already helped choose. One assignment, honoured by every candidate, is what closes that.

    By POSITION IN THE SORTED ID LIST, never by hashing the id. The target is itself a hash of the
    id (`price_elasticity_for_customer`), so a fold drawn by hashing the same string is a fold that
    can correlate with the very quantity being estimated.
    """
    return {c: i % folds for i, c in enumerate(sorted(ids))}


#: The role assignments the estimate averages over: each fold fits once, selects once and estimates
#: once. Not all six permutations — three is the set in which every fold plays every part exactly
#: once, and the null below has to run the IDENTICAL set or it is grading a different statistic.
SPLIT_ROTATIONS = tuple(r for r in itertools.permutations(range(SPLIT_FOLDS))
                        if all((r[i] - r[0]) % SPLIT_FOLDS == i for i in range(SPLIT_FOLDS)))


def _one_rotation(grid, traits: dict[str, float], cells: int, folds_of: dict[str, int],
                  roles: tuple[int, int, int]) -> dict | None:
    """One (fit, select, estimate) assignment: the winner chosen on SELECT, scored on ESTIMATE.

    Returns both the honest estimate and the MATCHED selected maximum — the same fit, but chosen and
    reported on the select and estimate folds TOGETHER, which is what the two-way procedure does.
    Reporting the three-way figure alone would confound two changes: the fit fold shrank from a half
    of the book to a third, AND the selection stopped being reported from. The matched maximum holds
    the fit size fixed, so the difference between the two is the SELECTION and nothing else.
    """
    fit_f, sel_f, est_f = roles
    best_sel, best = 0.0, None
    matched_max = 0.0
    scored = 0
    for cand in grid:
        ids = cand["ids"]
        ts = [traits[c] for c in ids]
        fit_i = [i for i, c in enumerate(ids) if folds_of[c] == fit_f]
        sel_i = [i for i, c in enumerate(ids) if folds_of[c] == sel_f]
        est_i = [i for i, c in enumerate(ids) if folds_of[c] == est_f]
        # `_corr` returns a silent 0.0 under three points, and a 0.0 that means "too few to say"
        # is indistinguishable from one that means "measured, found nothing". Skip instead.
        if len(fit_i) < 1 or len(sel_i) < 3 or len(est_i) < 3:
            continue
        preds = _cell_predictor(cand["xs"], cand["ys"], ts, cells, fit_i)
        sel_score = _corr(preds(sel_i), [ts[i] for i in sel_i])
        est_score = _corr(preds(est_i), [ts[i] for i in est_i])
        both = sel_i + est_i
        matched_max = max(matched_max, abs(_corr(preds(both), [ts[i] for i in both])))
        scored += 1
        if abs(sel_score) > abs(best_sel):
            # SIGN-ALIGNED, NOT ABSOLUTE, and this is the difference between an estimate and another
            # selected maximum. `abs(est_score)` has a positive expectation under pure noise, so
            # taking it would re-introduce exactly the upward bias this function exists to remove.
            # The selection fold already decided which way the fit points; the estimate fold's job
            # is only to agree or disagree with that, so it is scored against that decision.
            best_sel = sel_score
            best = {
                "x": cand["x"], "y": cand["y"], "n": len(ids),
                "select_score": round(sel_score, 4),
                "estimate": round(est_score * (1.0 if sel_score >= 0 else -1.0), 4),
                "fit_households": len(fit_i),
                "select_households": len(sel_i),
                "estimate_households": len(est_i),
            }
    if best is None:
        return None
    return {**best, "roles": list(roles), "candidates_scored": scored,
            "matched_selected_maximum": round(matched_max, 4)}


def three_way_split(grid, traits: dict[str, float], cells: int,
                    folds_of: dict[str, int]) -> dict | None:
    """The magnitude the sweep's selection ACTUALLY delivers, averaged over the rotations.

    THE DEFECT THIS REPAIRS, and it is the one the selection-corrected null does NOT repair. That
    null grades WHETHER the ceiling is real and answers it: p=0.03 on this book. It says nothing
    about HOW BIG. The published figure is `max(abs(held_out))` over 45 candidates ranked on the
    very fold it is then reported from, and the maximum of N noisy estimates overshoots the best
    candidate's true value whether or not the winner is real. Clearing a null does not un-bias a
    maximum; the two are different questions and only one of them had been asked.

    The mean over rotations is still unbiased — a mean of unbiased estimators is one — and it is far
    less noisy than any single split, which matters here because a third of 69 households is 23 and
    one draw of that would tell the reader almost nothing. The SPREAD is published beside it so the
    reader can see how much of the figure is the split.
    """
    if not grid:
        return None
    per = [r for r in (_one_rotation(grid, traits, cells, folds_of, roles)
                       for roles in SPLIT_ROTATIONS) if r]
    if not per:
        return None
    est = [r["estimate"] for r in per]
    matched = [r["matched_selected_maximum"] for r in per]
    return {
        "rotations": len(per),
        "estimate": round(statistics.fmean(est), 4),
        "estimate_range": [round(min(est), 4), round(max(est), 4)],
        "matched_selected_maximum": round(statistics.fmean(matched), 4),
        # WHAT THE SEARCH ITSELF WAS WORTH, at a fit size held fixed so it is attributable. This is
        # the quantity A49 needed and could not read off anything published before now.
        "selection_inflation": round(statistics.fmean(matched) - statistics.fmean(est), 4),
        "fit_households": per[0]["fit_households"],
        "select_households": per[0]["select_households"],
        "estimate_households": per[0]["estimate_households"],
        "winners": [{"x": r["x"], "y": r["y"], "roles": r["roles"],
                     "select_score": r["select_score"], "estimate": r["estimate"]} for r in per],
        # DID THE ROTATIONS EVEN AGREE ON WHAT WON? When they do not, the "winner" of the published
        # sweep is a property of which households happened to be on the ranking side, which is a
        # fact about the split and not about the book.
        "rotations_agree_on_the_winner": len({(r["x"], r["y"]) for r in per}) == 1,
    }


def three_way_null(grid, traits: dict[str, float], cells: int, folds_of: dict[str, int],
                   draws: int = SELECTION_NULL_DRAWS) -> dict | None:
    """The same three-way statistic against shuffled worlds — the estimator's own noise floor.

    Without it a reader cannot tell a small estimate from zero, and "small" is the answer this is
    most likely to return. Runs the IDENTICAL rotation set on the IDENTICAL fixed grid and the
    IDENTICAL global fold assignment: the only thing that moves is the household -> trait pairing.

    Two-sided, because the estimate is SIGNED. `p95` here is a percentile of the signed statistic
    and the verdict uses `abs`, so a real negative estimate is graded as seriously as a positive one
    rather than being scored against a floor it is trivially under.
    """
    ids = sorted({c for cand in grid for c in cand["ids"]})
    if not grid or len(ids) < 3:
        return None
    values = [traits[c] for c in ids]
    draws_out = []
    for draw in range(draws):
        permuted = list(values)
        random.Random(70_000 + draw).shuffle(permuted)
        got = three_way_split(grid, dict(zip(ids, permuted)), cells, folds_of)
        if got:
            draws_out.append(got["estimate"])
    if not draws_out:
        return None
    absolute = sorted(abs(v) for v in draws_out)

    def pct(p: float) -> float:
        return absolute[max(0, min(len(absolute) - 1, math.ceil(p * len(absolute)) - 1))]

    return {"draws": len(draws_out), "mean": round(statistics.fmean(draws_out), 4),
            "abs_median": round(pct(0.5), 4), "abs_p95": round(pct(0.95), 4),
            "abs_max": round(absolute[-1], 4), "_abs": absolute}


def magnitude_verdict(split: dict | None, null: dict | None, cell_count: int) -> dict:
    """The published magnitude: a number with its bound, or a REFUSAL that names its reason.

    FAIL CLOSED AND SAY SO ON THE SURFACE. A49 gates R3 and R4 on this figure, so the one thing that
    must never happen is a number appearing where an under-powered reading was all the book could
    buy. When the fit fold cannot hold populations the estimate is still computed — it is the honest
    direction of travel and suppressing it would hide the size of the correction — but it is
    published under `under_powered_reading` and `estimate` stays `None`. A gate reading `estimate`
    gets `None` and must refuse; a reader gets the number and its reason in the same object.
    """
    if split is None:
        return {"estimate": None, "refused": "no candidate grid to split three ways",
                "under_powered_reading": None}
    # THE CELL COUNT IS THE CALLER'S, because the two rungs do not have the same one: a pair spans
    # `cells * cells` and a single feature spans `cells`, its second axis being a constant. Deriving
    # it here from `cells` alone would divide the full-coverage fit fold by four cells it does not
    # have and refuse a rung that is in fact powered.
    per_cell = split["fit_households"] / cell_count
    powered = per_cell >= MIN_HOUSEHOLDS_PER_CELL and split["estimate_households"] >= MIN_FOLD_HOUSEHOLDS
    reading = split["estimate"]
    out = {
        "households_per_cell_on_the_fit_fold": round(per_cell, 2),
        "fit_fold_holds_populations": bool(per_cell >= MIN_HOUSEHOLDS_PER_CELL),
        "estimate_fold_is_big_enough": bool(split["estimate_households"] >= MIN_FOLD_HOUSEHOLDS),
    }
    if null is not None:
        exceed = sum(1 for w in null["_abs"] if w >= abs(reading))
        out["p_value"] = round((1 + exceed) / (1 + len(null["_abs"])), 4)
        out["bound_abs_p95"] = null["abs_p95"]
        out["exceeds_its_own_noise_floor"] = bool(abs(reading) > null["abs_p95"])
    if powered:
        return {"estimate": reading, "refused": None, "under_powered_reading": None, **out}
    return {
        "estimate": None,
        "under_powered_reading": reading,
        "refused": (
            f"three-way split needs {MIN_HOUSEHOLDS_PER_CELL} households per cell on the fit fold "
            f"and {MIN_FOLD_HOUSEHOLDS} on the estimate fold; this rung gives {per_cell:.2f} per "
            f"cell from a fit fold of {split['fit_households']} and an estimate fold of "
            f"{split['estimate_households']}. The reading beside this refusal is reported because "
            "the direction of travel is evidence; it is not an estimate and must not be gated on."),
        **out,
    }


def shrunk_toward_the_null(observed: float, null: dict | None) -> dict:
    """The other option on the table: the published maximum, less the null's own median maximum.

    IT IS NOT UNBIASED AND THIS FUNCTION SAYS SO IN ITS OWN PAYLOAD. It assumes the inflation a
    best-of-45 suffers under the alternative equals the inflation it suffers under the null, and
    nothing measured here establishes that — under a real effect the winner is chosen more often on
    signal than on noise, so the true inflation is smaller and this over-corrects. It is published
    because it is cheap, it is the figure a reader would compute themselves from the two numbers
    already on the page, and leaving it uncomputed invites someone to compute it and believe it.
    """
    if null is None:
        return {"value": None, "why_not": "no selection-corrected null to shrink toward"}
    return {
        "value": round(abs(observed) - null["median"], 4),
        "observed": round(abs(observed), 4),
        "null_median_maximum": null["median"],
        "is_unbiased": False,
        "what_it_assumes": (
            "that a best-of-N selection inflates a real effect by as much as it inflates pure "
            "noise. Under a real effect the winner is chosen on signal more often, so the true "
            "inflation is smaller and this figure over-corrects. Reported as a floor on the "
            "magnitude, never as the magnitude."),
    }


def _winner_inverts(best: dict) -> bool:
    """Did the REPORTED pair score better on households it never saw than on its own fit set?

    Kept as a function rather than inlined because three surfaces need the same answer -- the
    control block, the reader's caveat and the printed summary -- and a property computed three
    times is a property that can disagree with itself.
    """
    held = abs(best.get("held_out") or 0.0)
    return bool(held > abs(best.get("in_sample") or 0.0))


def _winner_ratio(best: dict) -> float | None:
    """How far the inversion goes. `None` when the in-sample score is zero: an infinite ratio is
    not a number a reader can hold, and rounding one to a large float would read as measured."""
    ins = abs(best.get("in_sample") or 0.0)
    return round(abs(best.get("held_out") or 0.0) / ins, 2) if ins > 0 else None


def recent_run_outputs(k: int, directory: Path) -> list[Path]:
    """The k most recent run outputs in `directory`, newest first. Never the `latest` alias."""
    runs = [Path(p) for p in glob.glob(str(directory / "run_output_*.json")) if "latest" not in p]
    return sorted(runs, key=os.path.getmtime, reverse=True)[:k]


def verdict_across_runs(paths, cells: int = 2) -> dict | None:
    """Does the published verdict survive being asked of a DIFFERENT DRAW OF THE SAME BOOK?

    WHY THIS RUNG EXISTS. The corrected verdict on the current book clears by +0.0598, a tenth of
    the figure itself, and the finding that landed the correction established by hand on four run
    outputs that it crosses 0.05 on a difference of TWO HOUSEHOLDS in the rung -- p=0.0746 at n=71
    and p=0.0249 at n=69, same population, same base seed. That was the whole reason the finding
    stayed BLOCKING, and it lived only in the finding: the page carried the PREDICTION "a figure
    that clears by a tenth of itself will move with the next draw of the book" while we held the
    OBSERVATION that it already had. A hedge published in place of a measurement we own is the
    weaker claim, and it is the one that rots.

    So the instrument takes the measurement itself. Each path is re-measured end to end -- the full
    ranked sweep and its own 200-draw selection-corrected null -- and the verdicts are counted.

    WHAT IT IS NOT, and this must travel with it or it will be over-read: these are consecutive run
    outputs of the SAME population at the SAME base seed, differing in how far the simulation had
    got and therefore in which households carry both fields of a pair. They are not independent
    books and this is not a bootstrap, so the spread here UNDERSTATES the sampling variability of a
    re-drawn book. What it establishes is narrower and is exactly what a gate needs: whether the
    published verdict is a property of the world or a property of which run output was read.
    """
    per_run = []
    for path in paths:
        try:
            got = measure(cells=cells, run_path=path)
        except SystemExit as refusal:
            # A run output too thin to measure is RECORDED, never skipped: dropping it would make
            # the series look more consistent than the evidence is.
            per_run.append({"run": path.name, "refused": str(refusal)})
            continue
        best, verdict = got.get("best_pair") or {}, got.get("selection_corrected_verdict") or {}
        per_run.append({
            "run": path.name,
            "n": best.get("n"),
            "ceiling": best.get("held_out"),
            "bound_p95": verdict.get("bound_p95"),
            "p_value": verdict.get("p_value"),
            "clears": verdict.get("clears"),
            "full_coverage_clears": got.get(
                "any_full_power_feature_clears_the_selection_corrected_null"),
            "trait_spread": (got.get("controls") or {}).get("trait_spread"),
            # THE WHOLE BOOK, not just the rung. Carried because the rung's household count and the
            # book's move TOGETHER across this window, and without both numbers the change looks
            # attributable to coverage alone when it is not.
            "households_in_book": got.get("households"),
        })
    return _reduce_runs(per_run)


def _reduce_runs(per_run: list[dict]) -> dict | None:
    """The reduction, split from the measurement so a control can grade it without re-measuring.

    Kept separate for one reason: re-running 32 books takes 40 seconds, and a control that costs 40
    seconds is a control that gets marked slow and then skipped. This is the part where the verdict
    is decided, so this is the part that has to be gradeable cheaply.
    """
    graded = [r for r in per_run if r.get("clears") is not None]
    if len(graded) < 2:
        return None
    verdicts = [bool(r["clears"]) for r in graded]
    # THE COUNTS ABOVE DEPEND ON HOW FAR BACK THE WINDOW REACHES, WHICH IS A DIAL. Grouping by the
    # rung's household count does not: it says WHAT the verdict is a function of. On this book the
    # answer is stark -- every run at n=71 reads `cannot tell` and every run at n=69 reads `clears`,
    # with no jitter inside either group. The verdict is a STEP FUNCTION OF COVERAGE, not noise
    # around a threshold, and that is a stronger and more falsifiable statement than a ratio of
    # runs. A regime that contained both verdicts would refute it and would mean something else is
    # moving; this reports the grouping either way rather than asserting the clean case.
    regimes = {}
    for r in graded:
        seen = regimes.setdefault(r["n"], {"households_in_rung": r["n"], "runs": 0,
                                           "verdicts": set(), "ceilings": set(), "p_values": set()})
        seen["runs"] += 1
        seen["verdicts"].add(bool(r["clears"]))
        seen["ceilings"].add(r["ceiling"])
        seen["p_values"].add(r["p_value"])
        seen.setdefault("books", set()).add(r.get("households_in_book"))
    coverage_regimes = [
        {"households_in_rung": k, "runs": v["runs"],
         "verdict": ("clears" if next(iter(v["verdicts"])) else "cannot tell")
                    if len(v["verdicts"]) == 1 else "MIXED",
         "verdict_is_constant_within_this_regime": len(v["verdicts"]) == 1,
         "ceilings": sorted(c for c in v["ceilings"] if c is not None),
         "p_values": sorted(p for p in v["p_values"] if p is not None),
         "households_in_book": sorted(b for b in v["books"] if b is not None)}
        for k, v in sorted(regimes.items(), reverse=True)]
    books_seen = sorted({b for r in coverage_regimes for b in r.get("households_in_book", [])})
    ps = [r["p_value"] for r in graded if r.get("p_value") is not None]
    ns = [r["n"] for r in graded if r.get("n") is not None]
    ceilings = [abs(r["ceiling"]) for r in graded if r.get("ceiling") is not None]
    return {
        "runs_measured": len(graded),
        "runs_refused": sum(1 for r in per_run if r.get("refused")),
        # THE PROPERTY, not today's answer: derived from the per-run verdicts every time, so it
        # goes false the moment the series disagrees and true again if coverage ever settles it.
        "unanimous": all(verdicts) or not any(verdicts),
        "clears_count": sum(1 for v in verdicts if v),
        "cannot_tell_count": sum(1 for v in verdicts if not v),
        "p_value_range": [min(ps), max(ps)] if ps else None,
        "households_range": [min(ns), max(ns)] if ns else None,
        "ceiling_range": [round(min(ceilings), 4), round(max(ceilings), 4)] if ceilings else None,
        "full_coverage_unanimous": len({bool(r.get("full_coverage_clears")) for r in graded}) == 1,
        "same_population": len({r.get("trait_spread") for r in graded}) == 1,
        "coverage_regimes": coverage_regimes,
        # True when every regime is internally consistent AND the regimes disagree with each other:
        # the verdict is then determined by coverage alone, which is the finding worth publishing.
        "verdict_is_a_step_function_of_coverage": bool(
            len(coverage_regimes) > 1
            and all(r["verdict_is_constant_within_this_regime"] for r in coverage_regimes)
            and len({r["verdict"] for r in coverage_regimes}) > 1),
        "window": [graded[-1]["run"], graded[0]["run"]],
        "per_run": per_run,
        # WHETHER THE BOOK MOVED IS A PROPERTY OF THE WINDOW, so it is read off the window rather
        # than asserted. Written as a standing caveat it survived the correction that repealed it:
        # the book only appeared to move because gas legs were being counted as households.
        "what_these_runs_are": (
            "Consecutive run outputs of the same population at the same base seed, differing in "
            "how far the simulation had got, and therefore in which households carry both fields "
            "of a pair. " + (
                "The size of the book moves across this window too, so the two are confounded and "
                "neither can be named as the cause of a verdict change. " if len(books_seen) > 1
                else f"The book is the same {books_seen[0]} households on every one of them, so a "
                     "verdict that changes across this window changes on the RUNG's coverage "
                     "alone. " if books_seen else "")
            + "Not independent books and not a bootstrap: the spread here UNDERSTATES what a "
              "re-drawn book would show."),
    }


def _magnitude_sentence(magnitude: dict, full_magnitude: dict, detail: dict | None,
                        observed: float, clears: bool | None = None,
                        book_magnitude: dict | None = None, book_n: int | None = None) -> str:
    """What the reader is owed about HOW BIG, which the verdict above does not answer.

    Every number here is derived from the payload rather than written in. The last version of this
    file's headline carried a literal ("a book of over two hundred") that was wrong the moment the
    count it described was corrected, and this sentence would rot the same way.

    TWO LITERALS IN THIS FUNCTION DID ROT, and both were live on the page for a day (2026-09-07).
    It asserted "So R1's ceiling clears its null on this book" with no access to the verdict, while
    the paragraph it is appended to opened "WE CANNOT TELL" -- one rendered note contradicting
    itself, because the sentence was written on a run where the ceiling cleared and the verdict
    then moved under it. And it closed "What closes it is COVERAGE, not a re-run" after the
    coverage had ARRIVED: `account_state_log` took four observables from 69 households to 164 on
    2026-09-06, and the pair rung still refuses -- not because the book is small but because THIS
    rung's population is set by whichever pair wins, and the winner reaches through a field that
    exists only where a renewal fired. A published cause authored as prose goes stale beside the
    measurement that refutes it, so `clears` and `book_magnitude` are arguments now and the two
    claims are derived rather than remembered.
    """
    est, forced = magnitude.get("estimate"), magnitude.get("under_powered_reading")
    floor, p = magnitude.get("bound_abs_p95"), magnitude.get("p_value")
    if est is not None:
        clear = magnitude.get("exceeds_its_own_noise_floor")
        return (
            f" THE MAGNITUDE IS {est:+.4f}, not {observed:+.4f}. Split three ways — fit on one third "
            f"of the book, choose the winner on a second, score it on a third that neither the fit "
            f"nor the choosing has touched — the figure the selection actually delivers is "
            f"{est:+.4f}"
            + (f", which is {'above' if clear else 'inside'} its own noise floor of {floor:+.4f} "
               f"(p={p})." if floor is not None else ".")
            + " The published figure is the larger because it is a maximum, and a maximum overshoots"
              " whatever it is the maximum of.")
    said = (
        f" AND THE SIZE OF IT IS NOT ESTABLISHED, which is a separate claim from whether it is real."
        f" {observed:+.4f} is the largest of a search ranked on the very fold it is then reported"
        f" from, so it is biased up as an estimate however cleanly it clears a null. De-biasing it"
        f" needs a third fold — fit on one, choose on a second, score on a third — and this rung"
        f" cannot carry one:"
        f" {magnitude.get('households_per_cell_on_the_fit_fold')} households per cell on the fit"
        f" fold against the {MIN_HOUSEHOLDS_PER_CELL} this instrument requires.")
    if forced is not None:
        said += (f" Forced through anyway it reads {forced:+.4f}"
                 + (f", inside a noise floor of {floor:+.4f} (p={p})" if floor is not None else "")
                 + " — the direction of travel, and not an estimate.")
    fe, ff, fp = (full_magnitude.get("estimate"), full_magnitude.get("bound_abs_p95"),
                  full_magnitude.get("p_value"))
    if fe is not None:
        # THE THIRD ROTTED LITERAL IN THIS FUNCTION, and the one that understated R1 rather than
        # overstating it. This read "inside its own noise floor -- indistinguishable from nothing"
        # on EVERY run that had a floor at all, and the full-coverage rung now reads +0.2992 against
        # a floor of +0.1557 at p=0.005: above it, not inside it. The clause is keyed to the
        # instrument's own `exceeds_its_own_noise_floor` verdict now, so it cannot disagree with the
        # figure standing next to it in the same sentence.
        said += (f" The full-coverage rung CAN carry the split, and there the estimate is {fe:+.4f}"
                 + ((f", {'above' if full_magnitude.get('exceeds_its_own_noise_floor') else 'inside'}"
                     f" its own noise floor of {ff:+.4f} (p={fp})"
                     + ("." if full_magnitude.get("exceeds_its_own_noise_floor")
                        else " — indistinguishable from nothing."))
                    if ff is not None else "."))
    if detail:
        said += (
            f" Holding the fit fold at the same size and separating ONLY the choosing from the"
            f" reporting moves the figure from {detail['matched_selected_maximum']:+.4f} to"
            f" {detail['estimate']:+.4f}, so {detail['selection_inflation']:+.4f} of it is the"
            f" search and nothing else — one variable, measured, not inferred.")
        if not detail.get("rotations_agree_on_the_winner"):
            lo, hi = detail["estimate_range"]
            said += (f" The rotations do not even agree on which candidate wins, and their estimates"
                     f" run from {lo:+.4f} to {hi:+.4f}: which pair is 'best' is a fact about who"
                     f" landed on the ranking side of the split.")
    verdict_said = (" So R1's ceiling clears its null on this book and its MAGNITUDE has no"
                    " unbiased estimate here." if clears else
                    " So this rung can neither separate R1's ceiling from chance nor put an"
                    " unbiased size on it." if clears is False else
                    " So this rung has no unbiased estimate of the magnitude.")
    said += verdict_said + (
        f" A49 gates R3 and R4 on this instrument and must read the magnitude field, which is"
        f" null — not {observed:+.4f}.")
    # WHAT CLOSES IT, DERIVED. This used to read "what closes it is COVERAGE, not a re-run", and
    # coverage arrived on 2026-09-06 without closing it -- so the cause was wrong, not merely
    # stale. The pair rung's refusal is about the SELECTED PAIR'S population and not the book's.
    be = (book_magnitude or {}).get("estimate")
    if be is None:
        return said + (" What closes it is COVERAGE on the fields the winning pair reaches, not a"
                       " re-run.")
    bf, bp = book_magnitude.get("bound_abs_p95"), book_magnitude.get("p_value")
    return said + (
        " AND MORE COVERAGE CANNOT CLOSE THIS RUNG, which is the correction to what this sentence"
        " used to say. Its population is not the book's: it is set by whichever pair wins, and the"
        " winner reaches through a field the company holds only where a renewal fired, so the rung"
        " collapses to the renewing subset however large the book grows. The SAME search"
        " restricted to the fields the company holds on every account on supply does carry the"
        " split — on"
        + (f" all {book_n} households" if book_n else " the whole book")
        + f" — and there the magnitude is {be:+.4f}"
        + (f" against its own noise floor of {bf:+.4f} (p={bp})" if bf is not None else "")
        + ". That is a NARROWER claim over a different population, not a better draw of this one,"
          " and it is published beside this rung rather than instead of it.")


def _headline(best: dict, pair_verdict: dict, full_verdict: dict, full_n: int,
              pairs: int, stability: dict | None = None,
              magnitude: dict | None = None, full_magnitude: dict | None = None,
              detail: dict | None = None, book_magnitude: dict | None = None,
              book_n: int | None = None) -> dict:
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
    # THE INVERSION TRAVELS WITH THE FIGURE OR IT IS NOT PUBLISHED AT ALL. A reader given
    # "clears, marginally" and not this cannot judge the number, and the whole-population control
    # that names this signature reads green while the published winner shows it.
    if _winner_inverts(best):
        ratio = _winner_ratio(best)
        power += (
            f" And the winning fit scores {abs(best.get('held_out') or 0.0):.4f} on households it "
            f"never saw against {abs(best.get('in_sample') or 0.0):.4f} on the ones it was built "
            f"from" + (f" -- {ratio:.1f} times better out of sample than in it" if ratio else "") +
            ". A fit does not do that; a search over 45 candidates ranked by the out-of-sample "
            "score finds one that does. This is not evidence the ceiling is chance -- the winner "
            "of a shuffled world overshoots its own fit for the same reason -- so the p-value "
            "above stands. It is the one thing that p-value cannot see, and it is why this figure "
            "is reported as the best of a search rather than as a bound.")
    # THE INSTABILITY IS A MEASUREMENT OR IT IS NOTHING (added 2026-09-06). This sentence used to
    # read "a figure that clears by a tenth of itself WILL MOVE with the next draw of the book" --
    # a prediction, published while the record already held the observation that it HAD moved, to
    # the other side of alpha, on a run of the same population two days earlier. A hedge standing in
    # for evidence we own is the weaker claim and the one that goes stale. When the stability rung
    # has run, its count replaces the hedge; when it has not, the hedge is marked as the prediction
    # it is rather than being dressed as a finding.
    if stability and stability.get("runs_measured", 0) >= 2:
        n_lo, n_hi = (stability.get("households_range") or [None, None])
        p_lo, p_hi = (stability.get("p_value_range") or [None, None])
        series = (f"Re-running the whole instrument -- the {pairs}-way sweep and its own "
                  f"{SELECTION_NULL_DRAWS}-draw corrected null -- on "
                  f"{stability['runs_measured']} consecutive run outputs of the SAME population at "
                  f"the same base seed")
        if not stability.get("unanimous"):
            moved = (
                f" AND THE VERDICT IS NOT A PROPERTY OF THE WORLD. {series} returns "
                f"{stability['clears_count']} 'clears' and {stability['cannot_tell_count']} "
                f"'cannot tell'"
                + (f", p from {p_lo} to {p_hi}" if p_lo is not None else "")
                + (f", on rungs of {n_lo} to {n_hi} households" if n_lo is not None else "")
                + ". Those books are consecutive states of one population at one base seed, so the "
                  "published answer moves with the run output the instrument read. A number that "
                  "changes side on that is not a gate, and R3 and R4 must not be gated on it.")
            # THE STRONGER FORM OF THE SAME FACT, when the grouping supports it. "18 of 32 runs
            # cleared" invites the reading that this is noise around a threshold and that more
            # draws would settle it. They would not: the verdict is CONSTANT inside each coverage
            # regime and differs BETWEEN them, so what decides it is two households, deterministically.
            if stability.get("verdict_is_a_step_function_of_coverage"):
                def _leg(r: dict) -> str:
                    # THE WHOLE RANGE, NEVER ITS BEST END. Printing `p_values[0]` here reported
                    # p=0.0249 for a regime holding {0.0249, 0.0299} -- the flattering end of its
                    # own spread, published as if it were the figure.
                    ps = r["p_values"]
                    shown = f"p={ps[0]}" if len(ps) == 1 else f"p from {ps[0]} to {ps[-1]}"
                    cs = r["ceilings"]
                    ceil = (f"ceiling {cs[0]:+.4f}" if len(cs) == 1
                            else f"ceiling {cs[0]:+.4f} to {cs[-1]:+.4f}")
                    return (f"every run at n={r['households_in_rung']} reads '{r['verdict']}' "
                            f"({ceil}, {shown})")
                legs = "; ".join(_leg(r) for r in stability["coverage_regimes"]
                                 if r["ceilings"] and r["p_values"])
                # WHAT MOVED, AND WHAT CANNOT BE ATTRIBUTED. The rung's household count and the
                # BOOK's move together across this window -- 71-in-rung/214-in-book reads one way
                # and 69/213 the other, with nothing in between -- so the two are perfectly
                # confounded and neither can be named as the cause from this evidence. The finding
                # that minted this work said "flips on two households"; that is the rung's share of
                # a change the whole book also underwent, and stating it alone would be attributing
                # a move when more than one thing changed. What survives is the part that bears on
                # a gate, and it needs no attribution at all: the verdict tracks WHICH RUN OUTPUT
                # WAS READ, and the books either side of the step differ by about half a percent.
                books = sorted({b for r in stability["coverage_regimes"]
                                for b in r.get("households_in_book", [])})
                # AND ON 2026-09-06 THE CONFOUND BROKE, which is why this branch is derived and
                # not prose. The 214-against-213 that made the two inseparable was an artefact of
                # the miscount above: keyed on the supply point, the book moved WITH the rung.
                # Keyed on the household it is the same 149 on all 32 runs while the rung still
                # steps 71 -> 69 -- so the cause IS attributable now, and a sentence that went on
                # disclaiming it would be hedging past evidence we hold.
                confound = (
                    f" The books either side of the step differ in the whole book too "
                    f"({books[0]} against {books[-1]} households), not only in the rung, so which "
                    "of the two moved the verdict cannot be attributed from this evidence and is "
                    "not claimed here." if len(books) > 1 else
                    f" The book itself is the same {books[0]} households on every one of them, so "
                    "the rung's coverage is the only thing that moved and it IS the cause."
                    if books else "")
                # THE DENOMINATOR IS DERIVED. It read "a book of over two hundred" while the book
                # was 149 and the instrument was counting gas legs as households -- a literal that
                # was wrong the moment the count it described was corrected.
                gap = (f"{n_hi - n_lo} households" if n_lo is not None and n_hi - n_lo != 1
                       else "one household")
                book = f"a book of {books[0]}" if books else "the book"
                moved += (
                    f" And this is not noise around the line, which would settle with more draws. "
                    f"It is a step: {legs}. There is no scatter inside either group." + confound +
                    f" Either way the published answer is decided by a difference of {gap} in "
                    f"{book}, which is not a quantity a programme can be gated on.")
        else:
            moved = (
                f" {series} returns the same verdict on every one"
                + (f" (p from {p_lo} to {p_hi})" if p_lo is not None else "")
                + ". That is a consistency check, not a bound: these are draws of one book rather "
                  "than independent books, so it cannot widen the claim, only fail to undermine it.")
        power += moved
    if clears:
        hedge = ("" if stability and stability.get("runs_measured", 0) >= 2 else
                 " I expect a figure that clears by a tenth of itself to move with the next draw "
                 "of the book, and that expectation is a prediction rather than a measurement: the "
                 "stability rung has not been run in this tree.")
        not_said = ("This does not establish a bound. It is a marginal pass on one book, clearing "
                    f"by {pair_verdict.get('margin_over_bound', 0.0):+.4f}." + hedge + " " + power)
    else:
        not_said = ("This is not a finding that price sensitivity is unlearnable. It is a refusal "
                    "to distinguish, which is a different claim. " + power)
    # WHETHER AND HOW BIG ARE TWO CLAIMS AND THE PAGE CARRIED ONE OF THEM. A reader given "recovers
    # +0.63, and it survives the correction" reads a magnitude that nothing here established; the
    # correction graded the existence. The sentence goes in `what_it_does_not_say` because that is
    # the field the delivery page renders beside the headline, and a magnitude caveat filed anywhere
    # a reader does not look is a caveat that was not published.
    magnitude_said = ""
    if magnitude is not None:
        magnitude_said = _magnitude_sentence(magnitude, full_magnitude or {}, detail, observed,
                                             clears, book_magnitude, book_n)
        not_said += magnitude_said
    return {
        "verdict": "clears" if clears else "cannot tell",
        "statement": statement,
        "what_it_does_not_say": not_said,
        # LIFTABLE ON ITS OWN, so a surface can render the magnitude claim without having to find it
        # inside a paragraph about something else.
        "on_the_magnitude": magnitude_said.strip() or None,
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


def measure(cells: int = 2, run_path: Path | None = None,
            stability_runs: list[Path] | None = None) -> dict:
    """`stability_runs`, when given, re-measures each of those run outputs end to end and reports
    whether the verdict survives a different draw of the same book. Left None by callers that only
    want the single-book reading -- and by the recursive call inside `verdict_across_runs`, which
    is what stops it descending."""
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

    # THE MAGNITUDE, which is a different question from the verdict above and had no answer until
    # now. `pair_verdict` grades whether +0.63 could be chance; it cannot grade whether +0.63 is the
    # right size, because the figure is the maximum of 45 candidates ranked on the very fold it is
    # reported from. One global fold assignment serves both rungs so a household is on the same side
    # of the split wherever it appears.
    folds_of = global_folds(list(obs))
    pair_split = three_way_split(grid, traits, cells, folds_of)
    pair_magnitude = magnitude_verdict(
        pair_split, three_way_null(grid, traits, cells, folds_of), cells * cells)
    full_split = three_way_split(full_grid, traits, cells, folds_of)
    full_magnitude = magnitude_verdict(
        full_split, three_way_null(full_grid, traits, cells, folds_of), cells)
    # THE PAIR RUNG THE WHOLE BOOK CARRIES, and it is what buys R1 a magnitude at all.
    # The rung above ranks every pair and reports the winner, so ITS household count is set by
    # whichever pair won -- and a pair built on a `decision_only` field collapses it to the renewing
    # subset however large the book is. That is exactly what happens on this book: four observables
    # went from 69 households to 164 when `account_state_log` landed, the book IS 164, and
    # `magnitude_three_way_split` still refuses at 69 because the winner is
    # `perceived_bill_saving_gbp x portfolio_premium_pct` and the first exists only where a renewal
    # window opened. The instrument could not say that. Its refusal read "the book is too small",
    # and the book was never the problem. MORE COVERAGE ON THE OTHER FIELDS CANNOT MOVE IT.
    #
    # THE RESTRICTION IS ON SCOPE AND NOT ON OUTCOME, which is the only thing that keeps this from
    # being a second bite at the search. `OBSERVABLE_FIELD_SCOPE` declares which fields a supplier
    # holds for every account on supply; that declaration is in the source, above, and is not
    # adjustable by what wins. Both rungs are published side by side for the same reason the
    # uncorrected null still is: a rung reported alone is a rung chosen.
    #
    # IT IS A NARROWER CLAIM, NOT A BETTER ONE. It answers "what can be recovered from what the
    # company holds about EVERY account", which is the quantity a book-wide programme can act on.
    # The all-candidate rung answers "what can be recovered about the households that renewed",
    # which is a real question with a smaller population and no route to the rest of the book.
    book_fields = whole_book_fields(shared)
    book_grid = [c for c in grid if c["x"] in book_fields and c["y"] in book_fields]
    book_ranked = [r for r in ranked if r["x"] in book_fields and r["y"] in book_fields]
    book_best = book_ranked[0] if book_ranked else {"held_out": 0.0, "n": 0}
    book_null = selection_corrected_null(book_grid, traits, cells)
    book_verdict = graded_against_selection(book_best.get("held_out", 0.0), book_null)
    # THE SAME `folds_of` as the rungs above, so a household sits on the same side of the split
    # wherever it appears and the three magnitudes are comparable rather than three different draws.
    book_split = three_way_split(book_grid, traits, cells, folds_of)
    book_magnitude = magnitude_verdict(
        book_split, three_way_null(book_grid, traits, cells, folds_of), cells * cells)

    shrunk = shrunk_toward_the_null(best.get("held_out", 0.0), pair_null)

    for block in (pair_null, full_null, book_null):
        if block is not None:
            block.pop("_winners", None)

    stability = verdict_across_runs(stability_runs, cells) if stability_runs else None

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
        # WHAT THE BOOK ACTUALLY IS, beside the count, because `households: 213` was wrong for two
        # days and nothing on the surface could say so. See `observable_rows`.
        "leg_fold_census": leg_fold_census(payload),
        # WHICH RECORD CARRIED EACH OBSERVABLE, AND WHETHER ITS COVERAGE IS A DEFECT OR A FACT.
        # See `field_provenance` and `OBSERVABLE_FIELD_SCOPE`.
        "field_provenance": field_provenance(payload),
        # THE ONE LINE THAT SAYS WHETHER THIS RUN'S BOOK IS ACCOUNT-SHAPED AT ALL. False means the
        # run predates `account_state_log`, or that `extract_report_data` stopped forwarding it --
        # and every account-state field silently falls back to its renewal-only coverage, which
        # reads exactly like a book that got smaller.
        "the_book_carries_an_account_shaped_record": bool(payload.get("account_state_log")),
        # THE SAME PAIR SEARCH, RESTRICTED TO WHAT THE COMPANY HOLDS FOR EVERY ACCOUNT. See the
        # block that builds it: the rung above reports a winner whose household count is set by the
        # pair that won, so a `decision_only` field can win and drag it back to the renewing subset.
        # `magnitude_three_way_split` here is the one that can be powered on this book.
        "whole_book_pair_rung": {
            "fields": book_fields,
            "pairs_scored": len(book_ranked),
            "best_pair": book_best,
            "clears_the_selection_corrected_null": book_verdict.get("clears"),
            "selection_corrected_verdict": book_verdict,
            "selection_corrected_null": book_null,
            "magnitude_three_way_split": book_magnitude,
            "magnitude_three_way_split_detail": book_split,
        },
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
        # THE MAGNITUDE, PUBLISHED SEPARATELY FROM THE VERDICT because they are separate claims and
        # were run together for two days. `estimate` is `None` whenever the rung cannot support one,
        # and A49 must read THAT field: `under_powered_reading` beside it is evidence of direction,
        # not a figure to gate on, and `magnitude_verdict` is where the two are kept apart.
        "magnitude_three_way_split": pair_magnitude,
        "magnitude_three_way_split_full_coverage": full_magnitude,
        "magnitude_three_way_split_detail": pair_split,
        "magnitude_shrunk_toward_the_null": shrunk,
        # WHETHER THE VERDICT SURVIVES A DIFFERENT DRAW OF THE SAME BOOK. `None` when the series was
        # not measured, which is a different claim from "measured, and stable" -- the page has to be
        # able to tell those apart, so the absence is never rendered as agreement.
        "verdict_stability": stability,
        "we_cannot_tell": _headline(best, pair_verdict, full_verdict, full_n, len(ranked),
                                    stability, pair_magnitude, full_magnitude, pair_split,
                                    book_magnitude, book_best.get("n")),
        "controls": {
            # A wrong seed gives random labels and a ceiling of zero -- the answer the canon
            # predicts, from a measurement of nothing.
            "traits_are_the_worlds": bool(spread > 0.0 and len(set(traits.values())) > 2),
            "trait_spread": round(spread, 5),
            # The ceiling must be computed on what the COMPANY sees. If a simulation internal ever
            # reaches this list the bound stops describing anything buildable.
            "no_ground_truth_in_features": not (set(shared) & set(GROUND_TRUTH_FIELDS)),
            # THE UNIT OF ANALYSIS IS THE HOUSEHOLD, which is what the target column is drawn per.
            # False here means a supply-point leg reached the grading and its elasticity was
            # invented by the hash rather than lived by anyone. `true_traits` refuses before this
            # can be read, so a False that ever surfaces means the refusal was routed around.
            "every_graded_row_is_a_household": all(
                _household_key(c) == c for c in obs),
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
            # THE SAME SIGNATURE, KEYED TO THE FIGURE THAT IS ACTUALLY PUBLISHED (added 2026-09-06).
            # The control above asks a POPULATION question and reads green on this book. The page
            # does not carry the population; it carries the WINNER, and on this book the winner
            # scores +0.6127 on households it never saw against +0.1674 on the ones it was built
            # from. The tell the control above is named for was sitting inside the number that
            # control was written to protect, and nothing could see it, because an aggregate is
            # blind to its own selected extreme -- and `abs(held_out)` is exactly the criterion
            # that finds an overshoot.
            #
            # IT IS NOT A SECOND VERDICT AND MUST NEVER BECOME ONE. Under the null the winner
            # overshoots its own fit too, for the same reason it does here: both worlds select on
            # held-out. So this cannot be evidence AGAINST the ceiling, the p-value already
            # contains the selection, and flipping `clears` on it would be keying a control to
            # today's answer. It is reported, on the surface, and it stops there.
            "held_out_exceeds_in_sample_on_the_reported_winner": _winner_inverts(best),
            "reported_winner_held_out_over_in_sample": _winner_ratio(best),
            # DOES THE PUBLISHED VERDICT DESCRIBE THE WORLD OR THE FILE WE HAPPENED TO READ?
            # `None` means unmeasured and must never be read as True: an unrun stability rung and a
            # stable one are different claims, and only one of them earns the word "bound".
            "the_verdict_is_the_same_on_every_draw_measured":
                stability.get("unanimous") if stability else None,
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
    # THE SERIES COMES FROM WHEREVER THE BOOK CAME FROM. `--run` exists because a linked worktree
    # holds no gitignored run outputs; the stability rung needs the SIBLINGS of that file, so it
    # reads the same directory rather than this tree's empty one.
    stability_runs = None
    if "--stability" in argv:
        i = argv.index("--stability")
        k = int(argv[i + 1]) if len(argv) > i + 1 and argv[i + 1].isdigit() else 8
        reports = run_path.parent if run_path else PROJECT / "docs" / "reports"
        stability_runs = recent_run_outputs(k, reports)
        if len(stability_runs) < 2:
            raise SystemExit(
                f"REFUSED: --stability needs at least 2 run outputs and {reports} has "
                f"{len(stability_runs)}. In a linked worktree this is what a missing gitignored "
                "run output looks like -- pass --run <path> in the tree that holds the real ones.")
    result = measure(run_path=run_path, stability_runs=stability_runs)
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
    print("  HOW BIG -- a separate question, and the one the correction above does NOT answer")
    det = result.get("magnitude_three_way_split_detail")
    book = result["whole_book_pair_rung"]
    for label, mag in (("pair rung", result["magnitude_three_way_split"]),
                       ("full coverage", result["magnitude_three_way_split_full_coverage"]),
                       ("whole book", book["magnitude_three_way_split"])):
        est, forced = mag.get("estimate"), mag.get("under_powered_reading")
        shown = (f"{est:+.4f}" if est is not None else
                 (f"REFUSED ({forced:+.4f} under-powered, NOT an estimate)"
                  if forced is not None else "REFUSED"))
        bound = mag.get("bound_abs_p95")
        tail = (f"   vs its own noise floor {bound:+.4f} (p={mag.get('p_value')})"
                if bound is not None else "")
        print(f"    three-way split, {label:<14}: {shown}{tail}")
        print(f"      fit fold holds {mag.get('households_per_cell_on_the_fit_fold')} households"
              f"/cell (needs {MIN_HOUSEHOLDS_PER_CELL}) -- populations: "
              f"{mag.get('fit_fold_holds_populations')}")
        if mag.get("refused"):
            print(f"      REFUSED: {mag['refused']}")
    if det:
        print(f"    the same fit, chosen AND reported on both held-out folds (matched control): "
              f"{det['matched_selected_maximum']:+.4f}")
        print(f"    so the SEARCH alone is worth                             : "
              f"{det['selection_inflation']:+.4f}")
        print(f"    rotations agree on which pair won: {det['rotations_agree_on_the_winner']}   "
              f"estimate across rotations: {det['estimate_range']}")
    # THE RUNG RESTRICTED TO WHAT THE COMPANY HOLDS ON EVERY ACCOUNT, printed beside the one above
    # and never instead of it. The two answer different questions over different populations, and
    # the reason the numbers differ is the population, not the estimator.
    print()
    print(f"  THE SAME SEARCH OVER THE {len(book['fields'])} FIELDS THE WHOLE BOOK CARRIES "
          f"({book['pairs_scored']} pairs)")
    print(f"    fields                                   : {', '.join(book['fields'])}")
    bb = book["best_pair"]
    print(f"    best pair                                : {bb.get('x')} x {bb.get('y')}  "
          f"held-out {bb.get('held_out', 0.0):+.4f}  n={bb.get('n', 0)}")
    print(f"    clears the selection-corrected null      : "
          f"{book['clears_the_selection_corrected_null']}  "
          f"(p={book['selection_corrected_verdict'].get('p_value')})")

    sh = result["magnitude_shrunk_toward_the_null"]
    if sh.get("value") is not None:
        print(f"    shrunk toward the null median instead     : {sh['value']:+.4f}  "
              f"(NOT unbiased -- {sh['observed']:+.4f} less the null's own median "
              f"{sh['null_median_maximum']:+.4f})")
    stab = result.get("verdict_stability")
    if stab:
        print()
        print(f"  THE SAME QUESTION ASKED OF {stab['runs_measured']} DRAWS OF THE SAME BOOK")
        for r in stab["per_run"]:
            if r.get("refused"):
                print(f"    {r['run']}: REFUSED")
                continue
            print(f"    n={r['n']:>4}  ceiling {r['ceiling']:+.4f}  p95 {r['bound_p95']:+.4f}  "
                  f"p={r['p_value']:<7} {'clears' if r['clears'] else 'CANNOT TELL':<12} "
                  f"{r['run']}")
        print(f"    unanimous: {stab['unanimous']}  "
              f"({stab['clears_count']} clears / {stab['cannot_tell_count']} cannot tell)")
    print()
    print(f"  VERDICT: {result['we_cannot_tell']['statement']}")
    print(f"  {result['we_cannot_tell']['what_it_does_not_say']}")
    print()
    print(f"  cells are populations         : {c['cells_are_populations']} "
          f"({c['households_per_cell']} households/cell on the fit side)")
    print(f"  the null ran the same selection: {c['the_null_ran_the_same_selection']}")
    print(f"  held-out beats in-sample on most pairs (the noise tell): "
          f"{c['held_out_exceeds_in_sample_on_most_pairs']}")
    ratio = c.get("reported_winner_held_out_over_in_sample")
    print(f"  ...and ON THE REPORTED WINNER, which is the figure published: "
          f"{c['held_out_exceeds_in_sample_on_the_reported_winner']}"
          + (f"  ({ratio}x better out of sample than in it)" if ratio else ""))
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"\nwrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
