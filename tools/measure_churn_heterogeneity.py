"""Rung 3: does the world's churn carry per-customer signal, or is it a level with noise on top?

Canon: `docs/staging/DIRECTOR_CANON_WORLD_VALIDATION_LADDER_2026-08-31.md` §2 rung 3 --
*"Do individual customers within the population make different choices, for hidden reasons of their
own, that aggregate to the average?"* That question had never been measured on any world variable
in this repository. This is the instrument for it, written against churn and deliberately generic
over the factor table so the next variable does not get a second one.

WHAT IT MEASURES, AND WHY IT IS AN ORACLE READING AND NOT A MODEL SCORE. The score is the world's
OWN realised departure probability for each household at each decision -- ground truth, the thing
the company is not allowed to see. So this is the CEILING: no company model, however good, can
discriminate better than the hazard that actually generated the outcome. A company AUC is only
interpretable against it. Reading a company AUC of 0.4653 as "the company is poor" when the ceiling
is 0.62 is the mistake this exists to stop.

WITHIN YEAR, ALWAYS, AND THAT IS THE WHOLE DESIGN. Two of the six factors reaching the hazard
(`sim_level_anchor`, `sim_market_opportunity`) take ONE value per calendar year. Pooling years lets
a reader score those year terms as if they were per-customer signal -- a model that knew only "it
is 2020" would look discriminating. Every AUC here is computed inside a year and pooled by pair
count, so the year terms contribute exactly nothing and what is left is the household.

*Corollary, and it is the load-bearing result:* because AUC is rank-based and the level anchor is a
single per-year multiplier, **the within-year reading is invariant to the anchor.** Measured across
a 20x sweep of a uniform anchor the reading moves 0.6239 -> 0.6248. The canon's diagnosis is that a
top-down aggregate destroys per-customer signal; for THIS variable that mechanism is not operating,
and saying so is worth more than confirming it.

THE NULL IS PART OF THE READING AND IS NEVER OPTIONAL. 79 departures is a small population and an
AUC computed on it wanders. The null here is the same score vector against labels shuffled WITHIN
year, which preserves each year's departure count and the score distribution and destroys only the
pairing. A reading inside its null is reported as "we cannot tell", in those words, per the standing
rule in `tools/inference_claim.py`.

TIES ARE REPORTED BECAUSE THEY ARE THE FAILURE MODE HERE. A factor taking three values across 465
households cannot discriminate no matter how large its hazard is: most pairs are ties and a tie
scores 0.5. `sim_dissatisfaction_response` is 1.0 for 88% of the book. Its AUC of 0.4971 is not
evidence that service does not drive departures -- it is evidence that the variable was discretised
until it could not carry the difference. Those are different findings and only the tie fraction
tells them apart.

THE COMPANY IS GRADED HERE TOO, AND ONLY BECAUSE IT IS THE SAME ROWS (2026-08-31). The ceiling was
measured before the company's belief could be put beside it: 0.6760 and the A/B's 0.4653 came from
different populations and different runs, and two true numbers whose legs are different populations
do not have a difference. So the belief is fed to THIS file's `within_strata_auc` and
`permutation_null` -- same rows, same strata, same seed -- and the readings are split by route,
because the two routes are not the same experiment:

  * the RENEWAL route is partly tautological. `roll_lifecycle_event` seeds `effective_p_retain`
    from the same `build_churn_risk` number it then grades, so that leg measures whether the
    world's adjustment chain preserves the ordering of the base rate it was handed. It is published
    as that, on the surface, not in a footnote. `company_churn_estimate` is the independent leg on
    the same rows and does not feed the roll.
  * the SVT route carries no company belief at all. `build_churn_risk` is indexed on renewal
    anniversaries and `run_phase2b`'s SVT branch consults no company estimate, so the 61% of this
    book's departures that leave by drifting off the standard variable product are invisible to the
    company's churn model. That absence is the finding, and it is stated rather than left as a
    missing column.

No ratio, share or "fraction of the ceiling captured" is emitted unless both legs count one
population AND the belief is independent of the roll -- see `ceiling_vs_belief`, which refuses with
a named cause rather than publishing a capture rate that is the world reading back its own input.

Usage:  python3 -m tools.measure_churn_heterogeneity [factor_table.json] [--permutations N]
                 [--run-output=PATH] [--out=PATH]
"""
from __future__ import annotations

import collections
import json
import math
import random
import statistics
import sys
from pathlib import Path

from tools.inference_claim import CANNOT_TELL

PROJECT = Path(__file__).resolve().parent.parent
#: The two-route capture taken for the ladder assessment. `c2_departure_factors.json` is the older,
#: renewal-only table and is still readable with `whole_book=False`.
DEFAULT_TABLE = PROJECT / "docs" / "reports" / "ladder_churn_factors.json"
#: The finished run the independent company belief is joined from -- see `attach_company_beliefs`,
#: which refuses unless it is the same run that produced the capture.
DEFAULT_RUN_OUTPUT = PROJECT / "docs" / "reports" / "run_output_latest.json"

#: The per-household factors that reach `departure_risks.build_departure_risks`, and the modulators
#: that scale them. Each is checked ALONE and HELD OUT, because those answer different questions: a
#: factor can be the only one that discriminates (bill shock) or can add nothing on top of the rest
#: (dissatisfaction), and a single column cannot show both.
HOUSEHOLD_FACTORS = (
    "sim_bill_shock_base",
    "sim_price_response",
    "sim_dissatisfaction_response",
    "sim_action_propensity",
)

#: Factors that take one value per calendar year. Listed so the report can SAY that they are
#: excluded by construction rather than leaving a reader to notice they are missing.
YEAR_FACTORS = ("sim_level_anchor", "sim_market_opportunity")

#: Population floor, from the table this was written against (465 decisions, 79 departures on
#: 2026-08-31). A scan that finds materially fewer has lost its subject rather than found a better
#: world, and a control built on this must red rather than report a clean-looking AUC on 12 rows.
#: Set at roughly half, so a real change in the book does not trip it and an emptied table does.
MIN_DECISIONS = 200
MIN_DEPARTURES = 30

#: The default permutation count. 2000 puts the 95% interval endpoints on the 50th and 1950th order
#: statistic, which is stable to about +/-0.005 between seeds -- checked, not assumed.
DEFAULT_PERMUTATIONS = 2000

#: Fixed so two runs of the same table give the same interval. A null that moves under the reader
#: is a null nobody can quote.
SEED = 20260831


class Unreadable(Exception):
    """The table cannot support a reading. Raised, never swallowed into a number."""


def _label(row: dict) -> int:
    return 1 if row.get("event_type") == "churned" else 0


def auc(scored: list[tuple[float, int]]) -> tuple[float | None, int]:
    """Return `(AUC, pair count)`. Ties score 0.5, which is what makes the tie fraction readable.

    `None` when either class is empty -- a year with no departures has no AUC, and returning 0.5
    for it would be a fabricated reading pooled in at full weight.
    """
    pos = [s for s, y in scored if y == 1]
    neg = [s for s, y in scored if y == 0]
    if not pos or not neg:
        return None, 0
    n = 0.0
    for a in pos:
        for b in neg:
            n += 1.0 if a > b else (0.5 if a == b else 0.0)
    return n / (len(pos) * len(neg)), len(pos) * len(neg)


def by_year(row: dict) -> tuple:
    """Stratify on the calendar year alone. Removes the year terms; leaves the ROUTE in."""
    return (row["market_year"],)


def by_year_and_route(row: dict) -> tuple:
    """Stratify on year AND departure route. The conservative reading, and the default.

    An SVT segment decision runs a mean hazard of 0.037 and a renewal decision 0.211 -- a 5.7x gap
    that is a property of the ROUTE, not of the household. Pooled across routes, a score that knew
    only "this is a renewal" would discriminate, and a reading that let that in would be scoring
    product structure as per-customer signal. Same trap the year stratification exists to close,
    one dimension over.
    """
    return (row["market_year"], row.get("route", "renewal"))


def within_strata_auc(rows: list[dict], score, stratum=by_year_and_route) -> tuple[float | None, int]:
    """Pooled-by-pair-count AUC computed inside each stratum.

    Pooling by pair count rather than averaging the strata is deliberate: a stratum with 3
    departures and one with 14 are not equally informative, and an unweighted mean would let the
    thinnest move the headline as much as the thickest.
    """
    total = 0.0
    pairs = 0
    groups = collections.defaultdict(list)
    for r in rows:
        groups[stratum(r)].append(r)
    for key in sorted(groups):
        a, w = auc([(score(r), _label(r)) for r in groups[key]])
        if a is not None:
            total += a * w
            pairs += w
    if not pairs:
        return None, 0
    return total / pairs, pairs


def within_year_auc(rows: list[dict], score) -> tuple[float | None, int]:
    """Year-only stratification. Kept as the name every caller already uses."""
    return within_strata_auc(rows, score, by_year)


def tie_fraction(rows: list[dict], field: str, stratum=by_year_and_route) -> float:
    """Fraction of within-stratum (departed, stayed) pairs on which `field` is exactly equal.

    This is the ceiling on how much the field could ever contribute: a tied pair scores 0.5 whatever
    the hazard attached to it, so a field tied on 77% of pairs cannot move an AUC further than
    0.115 from 0.5 in either direction.
    """
    tied = 0
    pairs = 0
    groups = collections.defaultdict(list)
    for r in rows:
        groups[stratum(r)].append(r)
    for key in sorted(groups):
        pos = [r[field] for r in groups[key] if _label(r) == 1]
        neg = [r[field] for r in groups[key] if _label(r) == 0]
        for a in pos:
            for b in neg:
                pairs += 1
                if a == b:
                    tied += 1
    return tied / pairs if pairs else float("nan")


def permutation_null(
    rows: list[dict],
    score,
    permutations: int = DEFAULT_PERMUTATIONS,
    stratum=by_year_and_route,
) -> dict:
    """The null distribution of the AUC under labels shuffled WITHIN each stratum.

    Shuffling within the stratum rather than across it is what makes this a null for the HOUSEHOLD
    claim: an across-stratum shuffle would also destroy each stratum's departure count, so beating
    it would only prove that years and routes differ -- which they do, and which nobody is asking
    about.
    """
    rnd = random.Random(SEED)
    scores = {id(r): score(r) for r in rows}
    groups = collections.defaultdict(list)
    for r in rows:
        groups[stratum(r)].append(r)
    draws = []
    for _ in range(permutations):
        total = 0.0
        pairs = 0
        for group in groups.values():
            labels = [_label(r) for r in group]
            rnd.shuffle(labels)
            a, w = auc(list(zip((scores[id(r)] for r in group), labels)))
            if a is not None:
                total += a * w
                pairs += w
        if pairs:
            draws.append(total / pairs)
    if not draws:
        raise Unreadable("no permutation draw produced a pair: every stratum is single-class")
    draws.sort()
    return {
        "low": draws[int(0.025 * len(draws))],
        "high": draws[int(0.975 * len(draws))],
        "median": draws[len(draws) // 2],
        "permutations": len(draws),
    }


def variance_split(rows: list[dict], stratum=by_year_and_route) -> dict:
    """Between-stratum and within-stratum share of the variance of log(realised hazard).

    In logs because every factor enters the hazard multiplicatively, so a log variance decomposes
    the way the model composes. **The between-stratum share is the part of an individual
    household's departure probability that is not about that household at all** -- it is the year
    it happened in and the product it happened on.
    """
    live = [r for r in rows if r["realized_churn_probability"] > 0]
    if len(live) < 2:
        raise Unreadable(f"only {len(live)} rows carry a positive realised hazard")
    lv = [math.log(r["realized_churn_probability"]) for r in live]
    grand = statistics.fmean(lv)
    groups = collections.defaultdict(list)
    for r in live:
        groups[stratum(r)].append(math.log(r["realized_churn_probability"]))
    between = sum(len(v) * (statistics.fmean(v) - grand) ** 2 for v in groups.values()) / len(lv)
    within = sum(sum((x - statistics.fmean(v)) ** 2 for x in v) for v in groups.values()) / len(lv)
    total = between + within
    return {
        "between_strata": between,
        "within_strata": within,
        "total": total,
        "between_strata_share": between / total if total else float("nan"),
        "strata": len(groups),
    }


def _read_list(path: Path) -> list[dict]:
    try:
        rows = json.loads(path.read_text())
    except FileNotFoundError as exc:
        raise Unreadable(f"no factor table at {path}") from exc
    except json.JSONDecodeError as exc:
        raise Unreadable(f"{path} is not readable JSON: {exc}") from exc
    if not isinstance(rows, list):
        raise Unreadable(f"{path} is not a list of decisions")
    return rows


def svt_companion(path: Path) -> Path:
    """The SVT-route file that `capture_departure_factors` writes beside the renewal one."""
    return path.with_name(path.stem + "_svt_segment_decisions.json")


def load(path: Path, *, whole_book: bool = True) -> list[dict]:
    """Read the captured book -- BOTH departure routes -- refusing rather than returning a part.

    FAIL CLOSED, TWICE OVER. A table that cannot be read, or that is too thin, raises. This tool's
    whole output is a claim about whether signal exists; "we could not read the file" must never
    reach a reader looking like "there is no signal".

    THE FLOOR IS ON THE UNION, AND THAT IS THE REPAIR C1b FORCED. The renewal table went from 465
    decisions to 144 when accounts moved onto the standard variable product -- a 69% loss of the
    population the year anchor is fitted on, with no control anywhere able to see it. A floor
    applied to the renewal file alone would now refuse the whole book because one of its two routes
    got smaller, which is the wrong refusal. The floor belongs on the population the reading is
    ABOUT.

    `whole_book=False` reads the renewal route alone. It exists for the routes that legitimately
    have only one file (every capture taken before 2026-08-31), and it is not the default, because
    a reading over a minority of the book that does not say so is exactly what this tool was
    written to stop.
    """
    rows = [dict(r, route=r.get("route", "renewal")) for r in _read_list(path)]
    if whole_book:
        companion = svt_companion(path)
        if companion.exists():
            rows += [dict(r, route=r.get("route", "svt_segment")) for r in _read_list(companion)]
    departures = sum(_label(r) for r in rows)
    if len(rows) < MIN_DECISIONS:
        raise Unreadable(
            f"{len(rows)} decisions is below the population floor of {MIN_DECISIONS}: "
            "the table has lost its subject, and a reading on it would be noise wearing a number"
        )
    if departures < MIN_DEPARTURES:
        raise Unreadable(
            f"{departures} departures is below the floor of {MIN_DEPARTURES}: "
            "no AUC computed on this can be told from chance"
        )
    return rows


def route_coverage(rows: list[dict]) -> dict:
    """Which departure ROUTES this reading can see, said on every run.

    `tools/capture_departure_factors` records the renewal decision by wrapping
    `roll_lifecycle_event`. C1b (`067a00dfd`) added the SVT inertia route, which departs at a
    segment boundary and never reaches a renewal roll -- so from that commit a renewal-only table
    stopped being the book and became a minority of it, silently. **A table with no `svt_inertia`
    cause is not a book in which nobody drifted off SVT; it is a table that cannot see them.**

    Printed rather than kept as a caveat in a document, because the reading is a claim about a
    POPULATION and this names which one. A verdict should be impossible to quote without it.
    """
    causes = collections.Counter(r.get("departure_cause") for r in rows if _label(r) == 1)
    routes = collections.Counter(r.get("route", "renewal") for r in rows)
    departures_by_route = collections.Counter(
        r.get("route", "renewal") for r in rows if _label(r) == 1
    )
    covers_svt = "svt_segment" in routes
    return {
        "causes": dict(causes),
        "routes": dict(routes),
        "departures_by_route": dict(departures_by_route),
        "covers_svt_route": covers_svt,
        "population": (
            "renewal decisions + SVT segment decisions"
            if covers_svt
            else "renewal decisions only"
        ),
    }


#: What each route's hazard is built from. The renewal route composes four household factors
#: through `build_departure_risks`; the SVT route has two, and one of them (`sim_svt_inertia`) is a
#: published annual rate converted to the segment's length rather than a fitted response.
ROUTE_FACTORS = {
    "renewal": HOUSEHOLD_FACTORS,
    "svt_segment": ("sim_svt_inertia", "sim_action_propensity"),
}


#: The company-side beliefs that exist at a renewal decision. TWO, and they are not the same claim
#: -- which is the whole reason this leg is split rather than reported as "the company's AUC".
#:
#: `seeds_the_world_roll` is the field that decides what a reading MEANS, so it travels with the
#: belief rather than living in a caveat a reader may not reach.
#: The ONE belief field that `attach_company_beliefs` supplies from the run output, named rather
#: than left inline — because it is exactly the set that becomes unavailable when the join refuses.
#: Everything else in `COMPANY_BELIEFS` is already on the capture row and is gradable whatever the
#: join does, which is a distinction the first run of
#: `tests/tools/test_the_ceiling_refuses_an_illegal_ratio.py` forced into the open: an over-broad
#: reading of "the join refused" would have marked a belief unavailable that never depended on it.
#: Captures taken from 2026-08-31 record this field directly, so the join — and this constant —
#: retire once no older capture is in use.
JOIN_SUPPLIED_FIELD = "company_churn_estimate"

COMPANY_BELIEFS = (
    {
        "field": "churn_probability",
        "label": "saas.churn_model.build_churn_risk (BASE + k x UPLIFT), logged per renewal",
        "seeds_the_world_roll": True,
        "reading": (
            "`simulation.customer_events.roll_lifecycle_event` seeds the world's "
            "`effective_p_retain` FROM this number and then multiplies it through the passive cap, "
            "the market-year switching multiplier, the price-position multiplier, income stress "
            "and satisfaction. Grading it against the outcome is therefore NOT a forecast against "
            "an unrelated tally: it measures whether the world's own adjustment chain preserves "
            "the ordering of the base rate it was handed. A weaker claim, and the honest one."
        ),
    },
    {
        "field": "company_churn_estimate",
        "field_optional": True,
        "label": "company.crm.churn_model.estimate_churn_probability (rate move, bill stress, tenure)",
        "seeds_the_world_roll": False,
        "reading": (
            "This one does NOT feed the roll -- `roll_lifecycle_event` computes it, stamps it on "
            "the event and never multiplies it into `effective_p_retain`. It is the independent "
            "leg on the renewal route, and the only renewal-route reading that can be compared to "
            "the ceiling without the tautology above."
        ),
    },
)

#: Routes on which the company forms a belief at all. `build_churn_risk` is indexed on RENEWAL
#: ANNIVERSARIES (`saas.churn_model._renewal_periods` walks `acquisition_date + n x 365 days`), so
#: a household drifting off the standard variable product at a segment boundary has no entry in it
#: -- and `run_phase2b`'s SVT branch consults no company belief of any kind, building its hazard
#: with `bill_shock_base=0.0, price_response=0.0, dissatisfaction_response=0.0`.
#:
#: LISTED AS A STRUCTURAL FACT, NOT AS A MISSING COLUMN. "The capture has no belief field on this
#: route" and "the company forms no belief on this route" are different findings, and only naming
#: the second stops the first being read as a data-collection gap someone could close by adding a
#: column. It cannot be closed that way: there is no number to record.
ROUTES_WITH_A_COMPANY_BELIEF = ("renewal",)


def attach_company_beliefs(rows: list[dict], run_output: Path) -> tuple[list[dict], dict]:
    """Join the run's `company_churn_estimate` onto the captured rows, or refuse.

    WHY A JOIN AT ALL, AND WHY IT IS GUARDED THIS HARD. `capture_departure_factors` did not record
    `company_churn_estimate` (it does from this commit; every capture taken before it does not), so
    the independent renewal-route belief lives only on the published run output. Joining two
    artefacts is exactly how this project has published a figure whose legs came from different
    runs, so the join VERIFIES rather than trusts: every captured row must be present, and its
    `realized_churn_probability` must agree to 1e-9 with the event log's. A world that was re-run
    between the capture and the log disagrees on the first hazard and this refuses.

    Returns `(rows, provenance)` unchanged and with `joined=False` when the field is already on the
    capture -- so this becomes dead weight rather than a second code path once captures carry it.
    """
    field = JOIN_SUPPLIED_FIELD
    renewals = [r for r in rows if r.get("route", "renewal") == "renewal"]
    if renewals and all(field in r for r in renewals):
        return rows, {"joined": False, "reason": "the capture already carries the field"}
    try:
        events = json.loads(run_output.read_text()).get("customer_events")
    except FileNotFoundError as exc:
        raise Unreadable(f"no run output at {run_output} to join the independent belief from") from exc
    if not isinstance(events, list) or not events:
        raise Unreadable(f"{run_output} publishes no `customer_events` to join")
    by_key = {(e.get("customer_id"), e.get("event_date")): e for e in events if isinstance(e, dict)}

    missing, disagreed = 0, 0
    joined = []
    for row in rows:
        if row.get("route", "renewal") != "renewal":
            joined.append(row)
            continue
        event = by_key.get((row["customer_id"], row["event_date"]))
        if event is None:
            missing += 1
            joined.append(row)
            continue
        truth = event.get("realized_churn_probability")
        if not isinstance(truth, (int, float)) or abs(truth - row["realized_churn_probability"]) > 1e-9:
            disagreed += 1
            joined.append(row)
            continue
        joined.append(dict(row, **{field: event.get(field)}))
    if missing or disagreed:
        raise Unreadable(
            f"the capture and {run_output} are not the same run: {missing} captured renewals are "
            f"absent from the event log and {disagreed} disagree on `realized_churn_probability`. "
            "A belief joined across runs would be graded against outcomes it never saw."
        )
    return joined, {
        "joined": True,
        "from": str(run_output.relative_to(PROJECT)) if run_output.is_relative_to(PROJECT) else str(run_output),
        "renewals_matched": len(renewals),
        "verified_on": "realized_churn_probability, every row, to 1e-9",
    }


def belief_readings(rows: list[dict], route: str, permutations: int) -> list[dict]:
    """Grade every company belief on ONE route, through the SAME estimator as the ceiling.

    THIS IS THE POINT OF THE WHOLE FUNCTION AND IT IS ONE LINE OF CODE: the belief is fed to
    `within_strata_auc` and `permutation_null` -- the identical stratified estimator, the identical
    within-stratum shuffle, the identical seed, on the identical rows -- as the world's own hazard.
    The published 0.4653 could not be put beside the ceiling because it was a POOLED statistic on a
    different population from a different run, and two true numbers whose legs are different
    populations do not have a difference. Same rows, same strata, same null, or no comparison.

    A route on which the company forms no belief returns a REFUSAL carrying its cause, never an
    empty list and never 0.5. "There is no belief here" and "the belief scored at chance" are
    opposite findings and a reader must not have to tell them apart from a missing row.
    """
    out = []
    for spec in COMPANY_BELIEFS:
        field = spec["field"]
        if route not in ROUTES_WITH_A_COMPANY_BELIEF:
            out.append({
                "belief": spec["label"],
                "field": field,
                "available": False,
                "reason": (
                    f"the company forms no belief on the {route} route. `build_churn_risk` is "
                    "indexed on renewal anniversaries, and `run_phase2b`'s SVT branch builds its "
                    "hazard with bill shock, price response and dissatisfaction all set to 0.0 "
                    "and consults no company estimate. There is no number to grade, and that is "
                    "the finding rather than a gap in the capture."
                ),
                "seeds_the_world_roll": spec["seeds_the_world_roll"],
            })
            continue
        present = [r for r in rows if isinstance(r.get(field), (int, float))]
        if len(present) != len(rows):
            out.append({
                "belief": spec["label"],
                "field": field,
                "available": False,
                "reason": (
                    f"{len(rows) - len(present)} of {len(rows)} decisions on this route carry no "
                    f"`{field}`. Grading the rest would silently change the population out from "
                    "under the ceiling it is being compared with."
                ),
                "seeds_the_world_roll": spec["seeds_the_world_roll"],
            })
            continue
        score = lambda r, f=field: r[f]  # noqa: E731 — passed to the estimator, not called here
        observed, pairs = within_strata_auc(rows, score)
        null = permutation_null(rows, score, permutations)
        out.append({
            "belief": spec["label"],
            "field": field,
            "available": True,
            "seeds_the_world_roll": spec["seeds_the_world_roll"],
            "independent_of_the_outcome": not spec["seeds_the_world_roll"],
            "reading": spec["reading"],
            "decisions": len(rows),
            "departures": sum(_label(r) for r in rows),
            "pairs": pairs,
            "belief_auc": observed,
            "null": null,
            "clears_the_null": observed is not None and observed > null["high"],
            "verdict": (
                "the belief orders who leaves"
                if observed is not None and observed > null["high"]
                else CANNOT_TELL
            ),
            "tie_fraction": tie_fraction(rows, field),
            "distinct_values": len({r[field] for r in rows}),
            "mean_believed": statistics.fmean(r[field] for r in rows),
            "realised_rate": sum(_label(r) for r in rows) / len(rows),
        })
    return out


def ceiling_vs_belief(route_entry: dict) -> dict:
    """Put the ceiling beside each belief on one route, and REFUSE the ratio unless it is legal.

    Three conditions, all required, and the refusal names which one failed:

    * **one population.** The belief and the ceiling must be the same decisions. A "fraction of the
      ceiling captured" whose numerator counts 144 renewals and whose denominator counts 1,410
      decisions across both routes is the exact move this repository has published wrongly before.
    * **independence.** A belief that SEEDS the world's roll and then scores well against it has
      measured the world reading back its own input. Normalising that onto the ceiling would
      publish a tautology as a capture rate, and the number would be quoted long after the sentence
      explaining it was dropped.
    * **the belief clears its own null.** A reading inside its null is `CANNOT_TELL`, and dividing
      a cannot-tell by a ceiling produces a percentage that reads as a finding -- the rank-statistic
      failure this project already has a rule for. On this book `company_churn_estimate` scores
      0.4988 inside `[0.3829, 0.6241]`; the ratio it yields is **-0.5%**, a number with the
      authority of a measurement and the content of noise. It is refused, not rounded to zero.

    `excess_over_chance_captured` is therefore `None` on this book for BOTH beliefs, for different
    reasons, and each is printed beside the reading it refuses. The two AUCs are published side by side with their
    populations named instead -- which is what the direction asked for and what the ladder page
    refused to do without it.
    """
    ceiling = route_entry.get("oracle_auc")
    out = []
    for belief in route_entry.get("company_belief", []):
        if not belief.get("available"):
            out.append({
                "belief": belief["belief"],
                "field": belief["field"],
                "ceiling_auc": ceiling,
                "belief_auc": None,
                "excess_over_chance_captured": None,
                "refused_because": belief["reason"],
            })
            continue
        same_population = belief["decisions"] == route_entry["decisions"]
        independent = belief["independent_of_the_outcome"]
        clears = belief["clears_the_null"]
        reasons = []
        if not same_population:
            reasons.append(
                f"the belief counts {belief['decisions']} decisions and the ceiling "
                f"{route_entry['decisions']}: not one population"
            )
        if not independent:
            reasons.append(
                "the belief seeds the world's own roll, so a captured fraction would be the world "
                "reading back its own input"
            )
        if not clears:
            reasons.append(
                f"the belief reads {belief['belief_auc']:.4f} INSIDE its null "
                f"[{belief['null']['low']:.4f}, {belief['null']['high']:.4f}] — a fraction of the "
                "ceiling computed from a cannot-tell is a percentage that reads as a finding"
            )
        legal = same_population and independent and clears and ceiling is not None and ceiling > 0.5
        out.append({
            "belief": belief["belief"],
            "field": belief["field"],
            "ceiling_auc": ceiling,
            "belief_auc": belief["belief_auc"],
            "one_population": same_population,
            "independent": independent,
            "clears_its_null": clears,
            "excess_over_chance_captured": (
                (belief["belief_auc"] - 0.5) / (ceiling - 0.5) if legal else None
            ),
            "refused_because": None if legal else "; ".join(reasons) or "the ceiling is not above chance",
        })
    return {"route": route_entry.get("route"), "readings": out}


#: The field carrying how long each SVT segment lasted. Exposure, in the survival-analysis sense.
EXPOSURE_FIELD = "sim_segment_days"


def exposure_offset(rows: list[dict], score_with, factors, permutations: int) -> dict:
    """The SVT route's reading with EXPOSURE divided out, and the per-factor table recomputed on it.

    WHY. An SVT segment runs from 1 to 92 days and a longer segment is simply more time in which to
    leave. That is not a hidden reason of anyone's own -- it is the billing calendar -- so any part
    of the route's discrimination it explains must come off before a per-factor figure is quoted as
    heterogeneity. Measured on this book: segment length ALONE scores 0.5868 against a null topping
    out at 0.5866. It clears by 0.0002, sitting on its own boundary: present, small, and real.

    THE OFFSET IS A DIVISION, NOT A STRATIFICATION, AND THAT IS DELIBERATE. `sim_svt_inertia` is a
    published annual rate converted to the segment's length, so the hazard is very nearly linear in
    days; dividing by days is the offset that matches how the quantity was built. Stratifying on
    length instead would cut the 1,266 decisions into 90-odd strata of a handful of rows each and
    the reading would be thin rather than corrected.

    THE PER-FACTOR TABLE IS RECOMPUTED HERE RATHER THAN CAVEATED. A caution recorded beside a table
    is a caution nobody applies; the corrected numbers are the ones a reader meets.
    """
    bad = [r for r in rows if not isinstance(r.get(EXPOSURE_FIELD), (int, float)) or r[EXPOSURE_FIELD] <= 0]
    if bad:
        raise Unreadable(
            f"{len(bad)} SVT decisions carry no positive `{EXPOSURE_FIELD}`: exposure cannot be "
            "offset, and quoting the uncorrected per-factor table instead would be the fail-open"
        )
    per_day = lambda r, **o: score_with(r, **o) / r[EXPOSURE_FIELD]  # noqa: E731 — passed on
    observed, pairs = within_strata_auc(rows, per_day)
    null = permutation_null(rows, per_day, permutations)
    length, _ = within_strata_auc(rows, lambda r: r[EXPOSURE_FIELD])
    length_null = permutation_null(rows, lambda r: r[EXPOSURE_FIELD], permutations)
    return {
        "offset": "hazard divided by segment days, i.e. a per-exposure-day rate",
        "oracle_auc_per_exposure_day": observed,
        "null": null,
        "clears_the_null": observed is not None and observed > null["high"],
        "pairs": pairs,
        "segment_length_alone": length,
        "segment_length_null": length_null,
        "segment_length_clears": length is not None and length > length_null["high"],
        "per_factor": _factor_decomposition(rows, factors, per_day, null, observed),
        "reading": (
            "Per-factor figures on the SVT route are quoted from THIS table, not from the "
            "uncorrected one above. The difference between the two oracle readings is the part of "
            "the route's discrimination that was the billing calendar rather than the household."
        ),
    }


def _supersede_uncorrected_factors(entry: dict, offset_key: str = "exposure_offset") -> None:
    """Stamp the un-offset per-factor table as withdrawn IN the table, not beside it.

    WHY THIS IS NOT A NOTE ELSEWHERE. `exposure_offset` recomputes the table rather than caveating
    it, and its own docstring says a caution recorded beside a table is a caution nobody applies.
    But the un-offset table was still published under the canonical `per_factor` key -- the same key
    that IS the quotable table on the renewal route -- unmarked, and with `inside_null_alone: False`
    on both factors. A reader taking the obvious key got the withdrawn figures wearing a
    clears-its-null flag, which is worse than no flag. On this book that is `sim_action_propensity`
    at 0.6421 (outside its null) versus 0.5067 (inside it), and the withdrawn number is the
    flattering one: it credits the term with what the segment length was doing.

    The measurements are NOT deleted. The uncorrected reading is what makes the size of the
    correction visible, and a figure removed cannot be checked against the one that replaced it.
    """
    reason = (
        "this reading does not carry the exposure offset: on a route where segments run 1-92 days "
        "a longer segment is simply more time in which to leave, so these figures credit the "
        "factors with what the billing calendar was doing"
    )
    entry["per_factor_superseded_by"] = f"{offset_key}.per_factor"
    entry["per_factor_superseded_because"] = reason
    for fd in entry["per_factor"].values():
        fd["superseded_by"] = f"{offset_key}.per_factor"
        fd["superseded_because"] = reason


def _factor_decomposition(rows: list[dict], factors, score_with, null: dict, observed: float) -> dict:
    """ALONE and HELD OUT readings for each factor, plus the tie fraction that bounds both."""
    means = {f: statistics.fmean(r[f] for r in rows) for f in factors}
    out = {}
    for f in factors:
        alone_override = {g: means[g] for g in factors if g != f}
        alone, _ = within_strata_auc(rows, lambda r, o=alone_override: score_with(r, **o))
        held_out, _ = within_strata_auc(rows, lambda r, f=f: score_with(r, **{f: means[f]}))
        out[f] = {
            "alone": alone,
            "held_out": held_out,
            "contribution": None if (observed is None or held_out is None) else observed - held_out,
            "tie_fraction": tie_fraction(rows, f),
            "distinct_values": len({r[f] for r in rows}),
            "inside_null_alone": alone is not None and null["low"] <= alone <= null["high"],
        }
    return out


def report(
    path: Path = DEFAULT_TABLE,
    permutations: int = DEFAULT_PERMUTATIONS,
    run_output: Path = DEFAULT_RUN_OUTPUT,
) -> dict:
    """The whole rung-3 reading for one captured book.

    THE HEADLINE IS STRATIFIED BY YEAR **AND ROUTE**, which is the conservative choice and the
    correct one. An SVT segment decision runs a mean hazard of 0.037 and a renewal decision 0.211;
    pooled, a score that knew only which product a household was on would discriminate, and that is
    product structure rather than the "hidden reasons of their own" rung 3 asks about. The
    year-only figure is reported beside it, labelled, so the size of what is being excluded is
    visible rather than merely asserted.
    """
    from simulation import departure_risks as dr
    from simulation.departure_risks import (
        DECLARED_SENSITIVITY_SCALE,
        DECLARED_SHOCK_WEIGHT,
    )

    rows = load(path)
    # THE BELIEF LEG MAY REFUSE; THE CEILING MUST NOT REFUSE WITH IT (2026-08-31).
    # `attach_company_beliefs` raises when the capture and the run output are not the same run,
    # and that refusal is right -- a belief graded against outcomes it never saw is worthless.
    # But it was allowed to propagate out of `report`, and the ceiling does not depend on the
    # belief at all: the landed rung-3 control calls `report()` with no run output of its own and
    # ERRORED on every leg, tree-wide, blocking every lane. Correct refusal, wrong blast radius --
    # the same class as `project_fail_closed_on_unreadable_input`, arriving from the other side.
    #
    # So the refusal is CAUGHT AND CARRIED rather than swallowed: `company_belief_provenance`
    # holds its cause verbatim, and `belief_readings` then reports every belief as unavailable
    # with the reason attached, because no row carries the field. Nothing reads as chance and
    # nothing reads as absent-without-explanation.
    try:
        rows, belief_provenance = attach_company_beliefs(rows, run_output)
    except Unreadable as exc:
        belief_provenance = {
            "joined": False,
            "refused": str(exc),
            "consequence": (
                "every company-belief reading below is unavailable. The CEILING readings are "
                "unaffected: they are computed from the capture alone and never touch the run "
                "output."
            ),
        }
    realised = lambda r: r["realized_churn_probability"]  # noqa: E731 — one expression, named twice below

    observed, pairs = within_strata_auc(rows, realised)
    null = permutation_null(rows, realised, permutations)
    clears = observed > null["high"]
    year_only, _ = within_year_auc(rows, realised)

    def renewal_hazard(row: dict, **override) -> float:
        risks = dr.build_departure_risks(
            bill_shock_base=override.get("sim_bill_shock_base", row["sim_bill_shock_base"]),
            price_response=override.get("sim_price_response", row["sim_price_response"]),
            dissatisfaction_response=override.get(
                "sim_dissatisfaction_response", row["sim_dissatisfaction_response"]
            ),
            market_opportunity=row["sim_market_opportunity"],
            action_propensity=override.get("sim_action_propensity", row["sim_action_propensity"]),
            sensitivity_scale=DECLARED_SENSITIVITY_SCALE,
            shock_weight=DECLARED_SHOCK_WEIGHT,
            level_anchor=override.get("sim_level_anchor", row["sim_level_anchor"]),
        )
        return dr.total_departure_probability(risks)

    def svt_hazard(row: dict, **override) -> float:
        # `svt_inertia * action_propensity`, and `level_anchor` is deliberately NOT on it —
        # `departure_risks` records why: the inertia hazard already arrives carrying units.
        return dr._clip_hazard(
            override.get("sim_svt_inertia", row["sim_svt_inertia"])
            * override.get("sim_action_propensity", row["sim_action_propensity"])
        )

    per_route = {}
    for route, factors in ROUTE_FACTORS.items():
        sub = [r for r in rows if r.get("route", "renewal") == route]
        if not sub or not any(_label(r) for r in sub):
            # NOT an empty dict quietly omitted: a route with no departures is a fact about the
            # book and belongs on the reading, where the alternative is a silently shorter table.
            per_route[route] = {"decisions": len(sub), "departures": 0, "reading": None}
            continue
        score_with = renewal_hazard if route == "renewal" else svt_hazard
        route_observed, route_pairs = within_strata_auc(sub, score_with)
        route_null = permutation_null(sub, score_with, permutations)
        entry = {
            "decisions": len(sub),
            "departures": sum(_label(r) for r in sub),
            "pairs": route_pairs,
            "oracle_auc": route_observed,
            "null": route_null,
            "clears_the_null": route_observed is not None and route_observed > route_null["high"],
            "per_factor": _factor_decomposition(sub, factors, score_with, route_null, route_observed),
        }
        entry["route"] = route
        # THE COMPANY LEG, ON THE SAME ROWS AND THE SAME STRATA AS THE CEILING DIRECTLY ABOVE IT.
        entry["company_belief"] = belief_readings(sub, route, permutations)
        entry["ceiling_vs_belief"] = ceiling_vs_belief(entry)
        if route == "svt_segment":
            entry["exposure_offset"] = exposure_offset(sub, score_with, factors, permutations)
            # The offset does not replace the table it corrects unless something says so where the
            # table is read. Marked at the point of publication, not in the prose downstream.
            _supersede_uncorrected_factors(entry)
        if route == "renewal":
            # The anchor counterfactual: the same reading with the year's level term flattened to
            # 1.0. It lives here rather than in a one-off script because it is the answer to the
            # canon's own causal claim, and an answer nobody can re-run is an answer nobody can
            # check. Renewal route only — the SVT hazard never carries the anchor.
            entry["oracle_auc_with_level_anchor_flattened"], _ = within_strata_auc(
                sub, lambda r: renewal_hazard(r, sim_level_anchor=1.0)
            )
        per_route[route] = entry

    return {
        "table": str(path.relative_to(PROJECT)) if path.is_relative_to(PROJECT) else str(path),
        "decisions": len(rows),
        "departures": sum(_label(r) for r in rows),
        "pairs": pairs,
        "route_coverage": route_coverage(rows),
        "oracle_auc": observed,
        "oracle_auc_year_only_route_pooled_in": year_only,
        "null": null,
        "clears_the_null": clears,
        "verdict": (
            "the world carries per-customer churn signal" if clears else CANNOT_TELL
        ),
        "variance": variance_split(rows),
        "variance_year_only": variance_split(rows, by_year),
        "per_route": per_route,
        "company_belief_provenance": belief_provenance,
        "departures_on_routes_the_company_has_no_belief_for": {
            "departures": sum(
                d["departures"] for r, d in per_route.items()
                if r not in ROUTES_WITH_A_COMPANY_BELIEF
            ),
            "of_total": sum(_label(r) for r in rows),
            "routes": [r for r in per_route if r not in ROUTES_WITH_A_COMPANY_BELIEF],
        },
        "stratified_by": "calendar year AND departure route",
        "structural_terms_excluded_by_construction": list(YEAR_FACTORS) + ["route"],
    }


def _print(r: dict) -> None:
    cover = r["route_coverage"]
    print(f"subject: {r['table']}")
    print(
        f"population: {cover['population']} — {r['decisions']} decisions, "
        f"{r['departures']} departures, {r['pairs']} within-stratum pairs"
    )
    print(f"  routes: {cover['routes']}   departures by route: {cover['departures_by_route']}")
    if not cover["covers_svt_route"]:
        print(
            "  ⚠ this reading CANNOT SEE the SVT inertia route (C1b). It is the renewal-decision "
            "population only, which is no longer the whole book."
        )
    print()
    print(f"RUNG 3 — per-customer signal, stratified by {r['stratified_by']}")
    n = r["null"]
    print(
        f"  oracle AUC (the world's own hazard) = {r['oracle_auc']:.4f}   "
        f"null 95% = [{n['low']:.4f}, {n['high']:.4f}]  (median {n['median']:.4f}, "
        f"{n['permutations']} within-stratum shuffles)"
    )
    print(f"  verdict: {r['verdict']}")
    print(
        f"  the same reading with the ROUTE pooled back in = "
        f"{r['oracle_auc_year_only_route_pooled_in']:.4f} — the difference is product structure "
        "being scored as per-customer signal, which is why it is excluded"
    )
    v, vy = r["variance"], r["variance_year_only"]
    print(
        f"\n  log-hazard variance: between-stratum {v['between_strata']:.4f} "
        f"({v['between_strata_share']:.1%} of the total, over {v['strata']} year x route strata), "
        f"within-stratum {v['within_strata']:.4f} ({1 - v['between_strata_share']:.1%})"
    )
    print(
        f"  year alone accounts for {vy['between_strata_share']:.1%} — the rest of the "
        "between-stratum share is the route."
    )
    for route, d in r["per_route"].items():
        print(f"\n  ── route: {route} ({d['decisions']} decisions, {d['departures']} departures)")
        if d.get("reading", True) is None or d["departures"] == 0:
            print("     no departures on this route in this capture: no reading is possible")
            continue
        rn = d["null"]
        print(
            f"     oracle AUC = {d['oracle_auc']:.4f}   null 95% = [{rn['low']:.4f}, "
            f"{rn['high']:.4f}]   clears: {d['clears_the_null']}"
        )
        if "oracle_auc_with_level_anchor_flattened" in d:
            print(
                f"     with the LEVEL ANCHOR flattened to 1.0 = "
                f"{d['oracle_auc_with_level_anchor_flattened']:.4f} — the top-down anchor is not "
                "what makes this reading what it is"
            )
        superseded = d.get("per_factor_superseded_by")
        if superseded:
            # The correction is printed further down, in the belief block. Nothing carried it UP to
            # the table it withdraws, so a reader who stopped here met the withdrawn figures with
            # `inside_null_alone: False` beside them and no reason to doubt either.
            print(
                f"     ⚠ SUPERSEDED — DO NOT QUOTE. {d['per_factor_superseded_because']}.\n"
                f"       Quote `{superseded}` (printed below); these are kept only to size the "
                "correction."
            )
        print(
            f"     {'factor':32s} {'ALONE':>7s} {'HELD OUT':>9s} {'CONTRIB':>8s} "
            f"{'TIED PAIRS':>11s} {'VALUES':>7s}"
        )
        for f, fd in d["per_factor"].items():
            flag = "  (alone: inside its null)" if fd["inside_null_alone"] else ""
            if superseded:
                flag = f"  ← SUPERSEDED{flag}"
            print(
                f"     {f:32s} {fd['alone']:7.4f} {fd['held_out']:9.4f} "
                f"{fd['contribution']:+8.4f} {fd['tie_fraction']:11.1%} "
                f"{fd['distinct_values']:7d}{flag}"
            )
    print(
        "\n  ALONE = every other factor on that route frozen at its population mean. HELD OUT = "
        "only this one frozen.\n  A factor tied on most pairs cannot discriminate however large "
        "its hazard is."
    )
    _print_belief(r)


def _print_exposure(e: dict) -> None:
    """The exposure-corrected SVT table, with the uncorrected one explicitly deprecated in place."""
    en = e["null"]
    print(
        f"\n     EXPOSURE OFFSET ({e['offset']}):\n"
        f"       oracle per exposure-day = {e['oracle_auc_per_exposure_day']:.4f}   "
        f"null [{en['low']:.4f}, {en['high']:.4f}]   clears: {e['clears_the_null']}"
    )
    print(
        f"       segment length alone = {e['segment_length_alone']:.4f} against a null "
        f"topping out at {e['segment_length_null']['high']:.4f} "
        f"(clears: {e['segment_length_clears']}) — exposure is present and small"
    )
    print(
        f"       {'factor':30s} {'ALONE':>7s} {'HELD OUT':>9s} {'CONTRIB':>8s} "
        f"{'TIED PAIRS':>11s} {'VALUES':>7s}   ← quote THESE, not the uncorrected table"
    )
    for f, fd in e["per_factor"].items():
        flag = "  (alone: inside its null)" if fd["inside_null_alone"] else ""
        print(
            f"       {f:30s} {fd['alone']:7.4f} {fd['held_out']:9.4f} "
            f"{fd['contribution']:+8.4f} {fd['tie_fraction']:11.1%} "
            f"{fd['distinct_values']:7d}{flag}"
        )
    if all(fd["inside_null_alone"] for fd in e["per_factor"].values()):
        print(
            "       ⚠ with exposure divided out, NEITHER factor alone clears its null while the "
            "composed hazard does:\n         the route's remaining discrimination is in the "
            "product, not in either term, and no single\n         factor from this table may be "
            "quoted as carrying it."
        )


def _print_belief(r: dict) -> None:
    """The company beside the ceiling, per route -- and the refusals in the same place as the reads.

    Printed at the END and in full sentences because this is the comparison the ladder page refused
    to make, and the two things that make it legal (one population, and which belief seeds the
    world's roll) are exactly the two a reader drops when they quote a pair of numbers.
    """
    print("\n" + "=" * 78)
    print("THE COMPANY BESIDE THE CEILING — same rows, same strata, same shuffle")
    print("=" * 78)
    nb = r["departures_on_routes_the_company_has_no_belief_for"]
    for route, d in r["per_route"].items():
        if d.get("departures", 0) == 0:
            continue
        print(f"\n  ── route: {route} ({d['decisions']} decisions, {d['departures']} departures)")
        print(f"     CEILING (the world's own hazard)      {d['oracle_auc']:.4f}")
        beliefs = d.get("company_belief", [])
        if beliefs and not any(b.get("available") for b in beliefs):
            # ONE STATEMENT, NOT ONE PER BELIEF. The cause is the route, not the field, so
            # repeating it per field would read as several separate gaps rather than one absence.
            print(f"     {'NO COMPANY BELIEF EXISTS ON THIS ROUTE':<37s} — nothing to grade")
            print(f"       └ {beliefs[0]['reason']}")
            print(
                f"       └ fields checked and absent: "
                f"{', '.join(b['field'] for b in beliefs)}"
            )
            if "exposure_offset" in d:
                _print_exposure(d["exposure_offset"])
            continue
        for b in beliefs:
            if not b.get("available"):
                print(f"     {b['field']:<37s} NO BELIEF EXISTS")
                print(f"       └ {b['reason']}")
                continue
            bn = b["null"]
            seeds = "SEEDS THE WORLD'S ROLL" if b["seeds_the_world_roll"] else "independent of the roll"
            print(
                f"     {b['field']:<37s} {b['belief_auc']:.4f}   "
                f"null [{bn['low']:.4f}, {bn['high']:.4f}]   {b['verdict']}"
            )
            print(
                f"       └ {seeds}; ties {b['tie_fraction']:.1%}, {b['distinct_values']} distinct "
                f"values, mean believed {b['mean_believed']:.4f} vs realised {b['realised_rate']:.4f}"
            )
        for c in d.get("ceiling_vs_belief", {}).get("readings", []):
            if c["excess_over_chance_captured"] is not None:
                print(
                    f"     fraction of the ceiling's excess captured: "
                    f"{c['excess_over_chance_captured']:.1%} ({c['belief']})"
                )
            else:
                print(f"     NO RATIO PUBLISHED for {c['belief'].split(' (')[0]} — {c['refused_because']}")
        if "exposure_offset" in d:
            _print_exposure(d["exposure_offset"])
    print(
        f"\n  {nb['departures']} of {nb['of_total']} departures "
        f"({nb['departures'] / nb['of_total']:.0%}) happen on {', '.join(nb['routes'])} — a route "
        "the company's churn model does not form a belief about at all."
    )


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    perms = DEFAULT_PERMUTATIONS
    run_output = DEFAULT_RUN_OUTPUT
    out = None
    for a in argv:
        if a.startswith("--permutations="):
            perms = int(a.split("=", 1)[1])
        if a.startswith("--run-output="):
            run_output = Path(a.split("=", 1)[1]).resolve()
        if a.startswith("--out="):
            out = Path(a.split("=", 1)[1]).resolve()
    path = Path(args[0]).resolve() if args else DEFAULT_TABLE
    try:
        result = report(path, perms, run_output)
        _print(result)
        if out is not None:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(result, indent=2) + "\n")
            print(f"\nwrote {out}")
    except Unreadable as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
