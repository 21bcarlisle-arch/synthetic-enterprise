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

Usage:  python3 -m tools.measure_churn_heterogeneity [factor_table.json] [--permutations N]
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


def report(path: Path = DEFAULT_TABLE, permutations: int = DEFAULT_PERMUTATIONS) -> dict:
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
        print(
            f"     {'factor':32s} {'ALONE':>7s} {'HELD OUT':>9s} {'CONTRIB':>8s} "
            f"{'TIED PAIRS':>11s} {'VALUES':>7s}"
        )
        for f, fd in d["per_factor"].items():
            flag = "  (alone: inside its null)" if fd["inside_null_alone"] else ""
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


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    perms = DEFAULT_PERMUTATIONS
    for a in argv:
        if a.startswith("--permutations="):
            perms = int(a.split("=", 1)[1])
    path = Path(args[0]).resolve() if args else DEFAULT_TABLE
    try:
        _print(report(path, perms))
    except Unreadable as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
