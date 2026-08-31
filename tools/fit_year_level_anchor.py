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
from tools.departure_population import banner, declare

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
    refusal = emission_refusal(decl)
    if refusal is not None:
        print("  REFUSED — no YEAR_LEVEL_ANCHOR block is emitted from this capture.")
        print(f"  Reason: {refusal}")
        print("  The per-year table above is a DIAGNOSTIC on this population and is not the")
        print("  world's level. Lifting this needs a whole-book departure target that both")
        print("  routes are fitted against together — never a widened band, and never this")
        print("  table pasted into simulation/departure_level_anchor.py. See item 1 of")
        print("  docs/staging/WORKER_FINDING_C1B_ADDED_A_DEPARTURE_ROUTE_AND_EVERY_INSTRUMENT"
              "_MEASURING_DEPARTURES_KEPT_READING_THE_OLD_POPULATION_2026-08-31.md.")
        return 1
    print("  YEAR_LEVEL_ANCHOR: dict[int, float] = {")
    for year in sorted(fitted):
        print(f"    {year}: {fitted[year]:.6f},")
    print("  }")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
