"""The year's departure LEVEL is the published record's; the mechanism decides which households.

Record: `docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json`.
Derived by: `tools/fit_year_level_anchor.py`.  Judged by: `tools/measure_departure_level.py`.
Write-up: `docs/market_research/gb_switching_rate_denominators.md` §8-§11.

WHAT THIS IS FOR. `market_departure_rate` made the world's market term a quantity with units again,
and the world still ran 3.45x below the published GB domestic switching record -- because the term
reaches the churn chain as a dimensionless RATIO, normalised to 1.0 at 2024, so correcting what the
ratio is a ratio OF moves the shape across years and cannot move the level at all. The level needs a
term with units in the churn chain itself. This is that term.

WHY IT IS A TABLE AND NOT A CONSTANT, AND THAT WAS MEASURED. `56718a719` established that no single
multiplicative scale reaches the band: the derived 1.99x puts 2022 at 6.0% against a published
2.9-4.3% and 2016 at 29.2% against 17.0-17.6%, while leaving 2020 still low, and the per-year
divisors that would fix each year individually have an EMPTY intersection. A constant would be
choosing which years to be wrong about. The reason is structural rather than a bad fit: the
non-market factor product runs 0.0198 at 2017 to 0.1193 at 2022, a 6x spread whose shape is
unrelated to the record's -- the record's trough year carries the largest product.

WHAT IT IS NOT. It is not a churn dial and it is not the curriculum. It scales every hazard in
`departure_risks.build_departure_risks` by the SAME factor, so it moves the year's LEVEL and cannot
move the reason MIX within that year. The published rate says how many households left in 2020; the
hazards say which ones and why; the company's own price position still moves the total, because the
anchor is a constant and not a renormalisation at roll time. Had it been the latter, the year's
departure count would come out at the record's whatever the company charged -- which is the
"over-pricing has no consequence" defect `churn_position_multiplier` was wired in to remove.

R13, AND THIS IS THE SIDE THAT MATTERS. It is BASELINE, not curriculum: the level is taken from the
published record, an external anchor this tree does not generate, and it was decided blind to
company results. It moves hard AGAINST the company -- the book goes from losing 4.50% per renewal
to losing the record's 15.50%, which is 3.4x more revenue at risk and 3.4x more re-acquisition
spend. A book that loses 4.5% a year is trivially easy to hold, and easy-to-hold flatters us in the
one dimension the thesis is about.

HOW STALE THIS GOES, AND WHAT NOTICES. The values are fitted on a captured run, so a change to the
churn model, the pricing desk or the population draw moves the factor population out from under
them. Nothing here is keyed to today's answer: the control is
`tests/architecture/test_switching_rate_commons.py::test_the_worlds_realised_departure_rate_is_inside_the_published_band`,
which asserts CONTAINMENT in the published band, so a refit that moves a year within its band passes
and drift that takes one outside it fails. When it fails, re-capture and re-fit -- do not widen it.
"""
from __future__ import annotations

from simulation.market_switching_propensity import MULTIPLIER_REFERENCE_YEAR

#: `{calendar year: anchor}`. Fitted by `tools/fit_year_level_anchor.py` on
#: `docs/reports/c2_departure_factors.json` at the declared (a_shock, scale) pair, one number per
#: year, by bisection onto `market_departure_rate(year)`.
#:
#: THE FIT IS EXACT ON THE RUN IT WAS FITTED TO AND APPROXIMATE ON THE NEXT ONE, which is a
#: property of the thing and not a defect in the fit: raising the level changes the book, so the
#: renewal population the following year is not the one the anchor was solved against. The
#: iteration is capture -> fit -> capture; the band is what says when it has converged.
YEAR_LEVEL_ANCHOR: dict[int, float] = {
    2016: 4.597312,
    2017: 4.256902,
    2018: 3.345826,
    2019: 3.228064,
    2020: 4.425742,
    2021: 3.219914,
    2022: 1.524110,
    2023: 2.091517,
    2024: 3.020806,
    2025: 2.118624,
}


def year_level_anchor(year: int) -> float:
    """The level anchor for a calendar year.

    OUTSIDE THE RECORD IT IS THE REFERENCE YEAR'S, AND THAT IS NOT A SHRUG. Every hazard already
    carries `market_switching_multiplier(year)`, which is the record's own level ratio inside the
    window and the scaled savings curve's outside it -- so the year-to-year LEVEL movement for a
    synthetic future is already accounted for by that term, and what this has to supply is the
    calibration of the factor population to a rate, which is a property of the population and not
    of the year. Taking the reference year's value says exactly that. It fails toward the record
    rather than toward the 3.45x-short world, which is the direction a fallback should fail in.
    """
    return YEAR_LEVEL_ANCHOR.get(year, YEAR_LEVEL_ANCHOR[MULTIPLIER_REFERENCE_YEAR])


__all__ = ["YEAR_LEVEL_ANCHOR", "year_level_anchor"]
