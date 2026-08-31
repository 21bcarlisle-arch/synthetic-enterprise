"""Derive the per-year departure LEVEL anchor: the year's rate is the record's, the mix is ours.

Anchor: `docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json`.
Write-up: `docs/market_research/gb_switching_rate_denominators.md` §8-§11.
Instrument that judges the result: `tools/measure_departure_level.py`.

WHY THIS IS A PER-YEAR TABLE AND NOT A CONSTANT, AND THAT WAS MEASURED RATHER THAN ASSUMED. The
2026-08-30 pass established that no single multiplicative scale on the market term can put the
world inside the published band: the non-market factor product (bill shock x felt price position x
action propensity x dissatisfaction) runs 0.0198 at 2017 to 0.1193 at 2022, a 6x spread whose shape
is unrelated to the record's -- 2022 is the record's TROUGH and carries the LARGEST product. Solving
for the single divisor that would put each year in its own band gives disjoint intervals with an
EMPTY intersection. One scale cannot do it and fitting one would be choosing which years to be
wrong about. See §9 prediction 4 of the write-up for the table.

WHAT THE ANCHOR IS AND IS NOT. It is one number per year, scaling every hazard in
`simulation/departure_risks.build_departure_risks` by the same factor. So it moves the year's
LEVEL and cannot move the reason MIX within the year -- the published record says how many
households left in 2020, the hazards say which ones and why. That separation is the whole point:
`market_departure_rate` states that inside 2016-2025 the level is historical ground truth in the
same sense as 2022 prices, and CLAUDE.md's third wall says the world does not model what the record
already states.

IT IS FITTED ON A CAPTURED RUN AND THEREFORE HAS A FIXED POINT TO REACH, and re-running this tool
IS the iteration. The captured columns are the hazard INPUTS -- bill shock, felt price position,
action propensity, dissatisfaction -- and none of them is a function of the anchor, so a refit on
capture N solves exactly for the population capture N had. What moves is the population itself:
raising the level means more departures, more re-acquisition and a different renewal book the
following year, so the anchor fitted on run N lands run N+1 NEAR the record rather than on it.
Capture, refit, capture again. The acceptance test is not this tool: it is
`tests/architecture/test_switching_rate_commons.py::test_the_worlds_realised_departure_rate_is_inside_the_published_band`,
measured through `tools/measure_departure_level.py` on the committed factor table.

Usage:
    python3 -m tools.fit_year_level_anchor [factor_table.json]
"""
from __future__ import annotations

import collections
import json
import statistics
import sys
from pathlib import Path

from simulation.departure_risks import (
    DECLARED_SENSITIVITY_SCALE,
    DECLARED_SHOCK_WEIGHT,
    build_departure_risks,
    total_departure_probability,
)
from simulation.market_switching_propensity import market_departure_rate
from tools.departure_population import (
    BOOK_BOUND,
    BOOK_DENOMINATOR,
    banner,
    book_level_from_hazards,
    declare,
    load_svt_decisions,
)
from tools.measure_departure_level import COMPARISON_YEARS

PROJECT = Path(__file__).resolve().parent.parent
DEFAULT_TABLE = PROJECT / "docs" / "reports" / "c2_departure_factors.json"


def _mean_probability(rows: list[dict], anchor: float) -> float:
    """Population-mean departure probability for one year at one anchor.

    `retention_offer_retained_fraction` is 1.0 for the same reason `tools/fit_departure_hazards.py`
    holds it there: the quantity being anchored is `realized_churn_probability`, captured BEFORE
    any retention offer, so including the offer would fit a post-intervention level to a
    pre-intervention record.
    """
    return statistics.fmean(
        total_departure_probability(
            build_departure_risks(
                bill_shock_base=r["sim_bill_shock_base"],
                price_response=r["sim_price_response"],
                dissatisfaction_response=r["sim_dissatisfaction_response"],
                market_opportunity=r["sim_market_opportunity"],
                action_propensity=r["sim_action_propensity"],
                retention_offer_retained_fraction=1.0,
                sensitivity_scale=DECLARED_SENSITIVITY_SCALE,
                shock_weight=DECLARED_SHOCK_WEIGHT,
                level_anchor=anchor,
            )
        )
        for r in rows
    )


def fit_year_anchor(rows: list[dict], target: float) -> float:
    """Bisect the year's anchor onto the published rate.

    Monotone by construction: every hazard is increasing in the anchor and `1 - PROD(1-h)` is
    increasing in every hazard, so there is no local solution to land on. Fails closed rather than
    silently returning the bracket end if the target is unreachable -- a year whose factors cannot
    reach its published rate even at the world's churn ceiling is a finding about the mechanism,
    not a number to clamp.
    """
    lo, hi = 0.0, 1.0
    for _ in range(60):
        if _mean_probability(rows, hi) >= target:
            break
        hi *= 2.0
    else:
        raise SystemExit(
            f"unreachable target {target:.4f}: even an anchor of {hi:.1f} leaves the year's mean "
            f"at {_mean_probability(rows, hi):.4f}. Every hazard is clipped at the world's churn "
            f"ceiling, so this says the year's factor population cannot carry the published rate. "
            f"That is a result about the mechanism -- do not clamp it."
        )
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if _mean_probability(rows, mid) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def _book_hazards_by_account(
    renewal_rows: list[dict],
    svt_rows: list[dict],
    anchor: float,
) -> dict[object, list[float]]:
    """One year's per-account hazards at a candidate anchor — renewal RECOMPUTED, SVT AS RECORDED.

    THE ASYMMETRY IS THE DESIGN AND IT IS THE WORLD'S OWN, not a convenience of the fit.
    `departure_risks.build_departure_risks` composes `CAUSE_SVT_INERTIA` as
    `clip(svt_inertia x action_propensity)` with **no** `level_anchor` in it, and the comment there
    gives the reason: `svt_inertia` arrives already carrying units, converted from a published
    ANNUAL drift rate, while the three response risks are dimensionless and it is the anchor that
    gives that family units at all. Anchoring an already-absolute published rate a second time is
    the "normalising a published absolute rate destroys the only level anyone could check" failure
    arriving from the other direction — at an anchor of 4.6 the published 10-20%/yr would reach the
    roll near 65%.

    SO THE ANCHOR'S ONLY LEVER ON THE WHOLE-BOOK LEVEL IS THE RENEWAL ROUTE, and that is what makes
    a per-year floor real rather than theoretical: a year's book level cannot be pushed below what
    the SVT route alone expects, however small the anchor. `book_floor_pct` below is that quantity
    and `fit_year_anchor_on_book` refuses against it rather than clamping.

    The SVT hazard is taken from the row's recorded `realized_churn_probability` rather than
    rebuilt, because rebuilding it would need `svt_inertia_hazard` re-derived from
    `sim_years_on_svt` and `sim_segment_days` — a second implementation of a quantity the capture
    already carries, and the one place a silent divergence between fit and world could hide.
    """
    hazards: dict[object, list[float]] = {}
    for r in renewal_rows:
        account = r.get("customer_id")
        if account is None:
            continue
        hazards.setdefault(account, []).append(
            total_departure_probability(
                build_departure_risks(
                    bill_shock_base=r["sim_bill_shock_base"],
                    price_response=r["sim_price_response"],
                    dissatisfaction_response=r["sim_dissatisfaction_response"],
                    market_opportunity=r["sim_market_opportunity"],
                    action_propensity=r["sim_action_propensity"],
                    retention_offer_retained_fraction=1.0,
                    sensitivity_scale=DECLARED_SENSITIVITY_SCALE,
                    shock_weight=DECLARED_SHOCK_WEIGHT,
                    level_anchor=anchor,
                )
            )
        )
    for r in svt_rows:
        account = r.get("customer_id")
        hazard = r.get("realized_churn_probability")
        if account is None or hazard is None:
            continue
        hazards.setdefault(account, []).append(float(hazard))
    return hazards


def _book_mean_probability(
    renewal_rows: list[dict],
    svt_rows: list[dict],
    anchor: float,
) -> float:
    """The year's whole-book departure level at one anchor, on the account-year denominator.

    Shares `departure_population.book_level_from_hazards` with the band instrument on purpose: the
    quantity being FITTED and the quantity being JUDGED have to be the same one, or the fit lands
    the world somewhere the control does not look.
    """
    return book_level_from_hazards(_book_hazards_by_account(renewal_rows, svt_rows, anchor))


def book_floor_pct(renewal_rows: list[dict], svt_rows: list[dict]) -> float:
    """The lowest whole-book level this year can reach, as a percentage: the anchor driven to zero.

    Not literally zero-able away: at `anchor=0` every renewal hazard collapses but the SVT route
    keeps its own published drift, so this is the SVT route's contribution spread over the year's
    full account denominator. A published band whose HIGH endpoint sits below this floor is
    unreachable by any anchor, and that is a statement about the mechanism rather than a fit to
    clamp.
    """
    return 100.0 * _book_mean_probability(renewal_rows, svt_rows, 0.0)


def outside_comparison_window(year: int) -> str | None:
    """Why this year may not carry a fitted anchor at all, or `None` if it may.

    REUSES THE WINDOW THIS REPOSITORY HAD ALREADY DECLARED rather than minting a threshold for the
    occasion. `measure_departure_level.COMPARISON_YEARS` exists because the capture's first year
    holds a handful of decisions and its last is partial, and it carries that reason at its own
    definition -- so a reader can check the exemption instead of taking a number on trust. A fresh
    `MIN_RENEWALS_TO_FIT = 5` here would have been exactly the invented constant CLAUDE.md's
    knowledge-first rule is about.

    WHAT IT STOPS, MEASURED. Without it the fit emitted `2016: 15.988769` -- a constant to six
    decimals solved off ONE renewal decision across three accounts -- into a block whose other
    entries are backed by fifty. Nothing in the emitted block would have said which was which.

    IT SITS IN THE DRIVER AND NOT IN `fit_year_anchor_on_book`, deliberately and for two reasons.
    The window is a policy about which years the CAPTURE can report on, not a fact about a year's
    arithmetic, and the fitter should stay a fitter. And it keeps the fitter's signature matching
    `fit_year_anchor` above -- neither takes a year, because neither returns anything keyed to one:
    they return a dimensionless correction factor. `tests/architecture/test_switching_rate_commons`
    discovers every callable of a year in this module as a possible switching-LEVEL reading, and an
    anchor fitter is not one.
    """
    if year in COMPARISON_YEARS:
        return None
    return (
        f"{year} is outside the declared comparison window "
        f"{COMPARISON_YEARS.start}-{COMPARISON_YEARS.stop - 1}, which exists because the edge "
        f"years cannot carry a fit: the capture's first year holds a handful of decisions and its "
        f"last is partial. Fitting one anyway emits a constant to six decimals off a population "
        f"that cannot identify one -- 2016 solves to an anchor near 16 off ONE renewal decision, "
        f"and nothing about the block it lands in would say so"
    )


def fit_year_anchor_on_book(
    renewal_rows: list[dict],
    svt_rows: list[dict],
    target: float,
) -> tuple[float | None, str | None]:
    """`(anchor, None)` fitting the WHOLE BOOK onto the published rate, or `(None, reason)`.

    THE TARGET THAT LIFTS `emission_refusal`'S MINORITY CLAUSE, and it is the thing the C1b finding
    left owed: *"a whole-book departure target that both routes are fitted against together"*. The
    renewal anchor is solved so that the union — every account with a decision on either route,
    combined within the account — lands on `market_departure_rate(year)`. The renewal route no
    longer has the published rate to itself; it contributes whatever the SVT route does not.

    TWO NAMED REFUSALS, AND THEY ARE INDEPENDENT, which is why both are reported rather than the
    first one found. A year can have no renewal population at all (the anchor multiplies nothing,
    so floor equals ceiling and the year is UNIDENTIFIED, not badly fitted), and a year's SVT floor
    can sit above its band whatever the renewal population is. On the 2026-08-31 capture 2022 is
    both at once, and a reader shown only "no renewal decisions" would go looking for renewal
    decisions — which would not help, because the floor binds independently.

    Monotone in the anchor for the same reason `fit_year_anchor` is: every renewal hazard is
    increasing in it, `1 - PROD(1-h)` is increasing in every hazard, and the mean over accounts is
    increasing in each account's annual probability. The SVT term is constant in the anchor, which
    is exactly what makes the floor a floor.
    """
    floor = _book_mean_probability(renewal_rows, svt_rows, 0.0)
    reasons: list[str] = []
    if not renewal_rows:
        reasons.append(
            "this year has NO renewal decisions in the capture, so the anchor multiplies nothing "
            "and the book level is unidentified: floor and ceiling are the same number and no "
            "value of the constant moves it by a basis point"
        )
    if floor > target:
        reasons.append(
            f"the SVT route alone expects {100.0 * floor:.2f}% of the year's accounts to depart, "
            f"against a published target of {100.0 * target:.2f}%. The anchor does not scale "
            f"`svt_inertia`, so no anchor >= 0 brings the whole book down to the record. That is a "
            f"result about the mechanism -- do not clamp it"
        )
    if reasons:
        return None, "; and ".join(reasons)

    lo, hi = 0.0, 1.0
    for _ in range(60):
        if _book_mean_probability(renewal_rows, svt_rows, hi) >= target:
            break
        hi *= 2.0
    else:
        return None, (
            f"unreachable upward: even an anchor of {hi:.1f} leaves the whole book at "
            f"{100.0 * _book_mean_probability(renewal_rows, svt_rows, hi):.2f}% against a target of "
            f"{100.0 * target:.2f}%. Every renewal hazard is clipped at the world's churn ceiling, "
            f"so the year's renewal population cannot carry what the SVT route leaves"
        )
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if _book_mean_probability(renewal_rows, svt_rows, mid) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0, None


def book_emission_refusal(decl: dict) -> str | None:
    """Why this capture may not hand over a whole-book `YEAR_LEVEL_ANCHOR`, or `None` if it may.

    RE-KEYED TO THE UNION, AND `emission_refusal` ABOVE IS DELIBERATELY LEFT ALONE. That one guards
    the renewal-only fit and its minority clause is still correct there: anchoring a mean over
    renewal decisions onto a whole-population published rate fits the world to the households that
    demonstrably shop. Under a whole-book target a minority renewal route is the EXPECTED state and
    not a defect — refusing on it here would be the refusal refusing the population it asked for.

    So one clause survives and it is the one about observability rather than about proportion: a
    capture that cannot see the SVT route cannot form the union, and fitting anyway would assert
    the thing that is unknown. Per-year reachability is NOT handled here; it is
    `fit_year_anchor_on_book`'s, because it is a fact about a year and not about the capture.
    """
    if not decl["covers_svt_route"]:
        return "this capture cannot form the union. " + decl["warning"]
    return None


def emission_refusal(decl: dict) -> str | None:
    """Why this capture may not hand over a `YEAR_LEVEL_ANCHOR` block, or `None` if it may.

    THE REFUSAL IS THE REPAIR, AND A PRINTED CAVEAT WOULD NOT HAVE BEEN. C1b's author wrote the
    staleness down at the site, named this tool, and predicted exactly what would happen on the
    next capture. It happened. So the debt carries something that FAILS: the per-year diagnostic
    table below still prints, because a measurement withheld is a measurement nobody can argue
    with, but the constant a reader would paste into `simulation/departure_level_anchor.py` does
    not come out of a population that is not the book.

    TWO DISTINCT REFUSALS, because they are two different states and a reader must be able to tell
    them apart:

      * **the capture cannot see the SVT route at all** -- it may or may not be the book, and this
        tool cannot establish which. Fitting anyway would be asserting the thing that is unknown.
      * **the capture CAN see it and the renewal route is a minority** -- measured 2026-08-31 at
        39% of departures. Fitting here is worse than the staleness it appears to cure: the
        households on the standard variable product never reach the renewal roll, so what is left
        is the SELECTED subset who demonstrably shop, and anchoring their mean onto a
        whole-population published rate fits the world to a sub-population.

    What lifts it is item 1 of the finding and is not a wider band: a whole-book departure target
    that both routes are fitted against together.
    """
    if not decl["covers_svt_route"]:
        return (
            "this table's population cannot be established as the book. " + decl["warning"]
        )
    share = decl["share_of_departures_visible"]
    if share is not None and share < 1.0:
        return (
            f"the renewal route carries only {share:.0%} of the departures in this capture "
            f"({decl['departures']}). Anchoring a mean over renewal decisions onto a "
            f"whole-population published switching rate would fit the world to the SELECTED "
            f"subset of households that reach a renewal roll at all."
        )
    return None


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    table_path = Path(args[0]) if args else DEFAULT_TABLE
    all_rows = json.loads(table_path.read_text())
    rows = [r for r in all_rows if r.get("sim_bill_shock_base") is not None]
    by_year: dict[int, list[dict]] = collections.defaultdict(list)
    for r in rows:
        by_year[int(r["event_date"][:4])].append(r)

    decl = declare(table_path, all_rows)
    print(banner(decl))
    print()
    print(f"factor table: {table_path}   ({len(rows)} renewals)")
    print(f"declared pair: a_shock={DECLARED_SHOCK_WEIGHT}  scale={DECLARED_SENSITIVITY_SCALE}")
    print()
    print(f"{'year':>6} {'n':>4} {'record %':>9} {'unanchored %':>13} {'anchor':>9} "
          f"{'achieved %':>11}")
    fitted: dict[int, float] = {}
    for year in sorted(by_year):
        year_rows = by_year[year]
        target = market_departure_rate(year)
        base = 100.0 * _mean_probability(year_rows, 1.0)
        anchor = fit_year_anchor(year_rows, target)
        fitted[year] = anchor
        achieved = 100.0 * _mean_probability(year_rows, anchor)
        print(f"{year:>6} {len(year_rows):>4} {100.0 * target:>9.2f} {base:>13.3f} "
              f"{anchor:>9.4f} {achieved:>11.3f}")
    print()
    print("  THE TABLE ABOVE IS THE RENEWAL-ROUTE DIAGNOSTIC AND IS NOT WHAT GETS EMITTED.")
    print("  It fits each year's renewal decisions alone onto the published rate, which is the")
    print("  reading C1b made a sub-population. The emitted constant comes from the whole-book")
    print("  fit below, on the account-year denominator both routes share.")
    print()
    return _fit_on_the_whole_book(table_path, all_rows, by_year, decl)


def _fit_on_the_whole_book(
    table_path: Path,
    all_rows: list[dict],
    renewal_by_year: dict[int, list[dict]],
    decl: dict,
) -> int:
    """Fit and emit `YEAR_LEVEL_ANCHOR` against the whole-book target, or refuse and say why.

    THE YEARS THAT REFUSE ARE PRINTED, NOT DROPPED. A year missing from the emitted block because
    its target is unreachable and a year missing because nobody thought about it look identical in
    the block itself, and `year_level_anchor` falls back to the reference year for both. Naming
    each refusal beside the block is what makes the absence a declaration rather than a gap.
    """
    refusal = book_emission_refusal(decl)
    if refusal is not None:
        print("  REFUSED — no YEAR_LEVEL_ANCHOR block is emitted from this capture.")
        print(f"  Reason: {refusal}")
        print("  Never a widened band, and never the renewal table above pasted into")
        print("  simulation/departure_level_anchor.py.")
        return 1

    svt_rows, _ = load_svt_decisions(table_path)
    svt_by_year: dict[int, list[dict]] = collections.defaultdict(list)
    for r in svt_rows or []:
        svt_by_year[int(str(r["event_date"])[:4])].append(r)

    print(f"  WHOLE-BOOK FIT.  denominator: {BOOK_DENOMINATOR}")
    print(f"  this is an {BOOK_BOUND.upper()} bound on the year's departure rate; the anchor's only")
    print("  lever is the renewal route, because `build_departure_risks` does not scale `svt_inertia`.")
    print()
    print(f"  {'year':>6} {'ren':>4} {'acct':>5} {'record %':>9} {'SVT floor %':>12} "
          f"{'anchor':>9} {'achieved %':>11}   refusal")
    fitted: dict[int, float] = {}
    refused: dict[int, str] = {}
    for year in sorted(set(renewal_by_year) | set(svt_by_year)):
        year_renewals = renewal_by_year.get(year, [])
        year_svt = svt_by_year.get(year, [])
        target = market_departure_rate(year)
        floor = book_floor_pct(year_renewals, year_svt)
        accounts = len(_book_hazards_by_account(year_renewals, year_svt, 1.0))
        why = outside_comparison_window(year)
        anchor = None
        if why is None:
            anchor, why = fit_year_anchor_on_book(year_renewals, year_svt, target)
        if anchor is None:
            refused[year] = why
            print(f"  {year:>6} {len(year_renewals):>4} {accounts:>5} {100.0 * target:>9.2f} "
                  f"{floor:>12.2f} {'—':>9} {'—':>11}   REFUSED")
            continue
        fitted[year] = anchor
        achieved = 100.0 * _book_mean_probability(year_renewals, year_svt, anchor)
        print(f"  {year:>6} {len(year_renewals):>4} {accounts:>5} {100.0 * target:>9.2f} "
              f"{floor:>12.2f} {anchor:>9.4f} {achieved:>11.2f}")
    print()
    for year in sorted(refused):
        print(f"  {year} REFUSED: {refused[year]}.")
    if refused:
        print()
        print("  These years are ABSENT from the block below on purpose and must not be")
        print("  interpolated. `year_level_anchor` already falls back to the reference year, and")
        print("  that fallback is declared where an invented value would not be.")
        print()
    print("  YEAR_LEVEL_ANCHOR: dict[int, float] = {")
    for year in sorted(fitted):
        print(f"    {year}: {fitted[year]:.6f},")
    print("  }")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
