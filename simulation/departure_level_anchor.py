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

from simulation.market_switching_propensity import (
    MULTIPLIER_REFERENCE_YEAR,
    _published_departure_rates,
)

#: The years the fit is SCOPED TO, and the third of the three sets this file has to keep apart.
#:
#: THE FITTED TABLE, THE PUBLISHED RECORD AND THE COMPARISON WINDOW ARE THREE DIFFERENT SETS.
#: `9fd700366` fixed a defect in which the fallback's CONDITION was the first and its
#: JUSTIFICATION was the second. It replaced the condition with the record and stopped there --
#: but the fit's own scope is neither: `tools.measure_departure_level.COMPARISON_YEARS` restricts
#: the comparison to 2017-2024 because 2016 carries 1-3 renewal decisions in every capture on disk
#: and 2025 is a partial year, and a three-account year must not weigh as much as a 131-account
#: one. A year the fit never CLAIMED is not a year the fit FAILED to identify, and reading the
#: record's edge years as failures is what turned a scope statement into a crash.
#:
#: Duplicated from `measure_departure_level` rather than imported, because `simulation/` must not
#: acquire a `tools/` edge on its import graph, and held to it by
#: `tests/architecture/test_switching_rate_commons.py::test_the_anchors_fit_window_is_the_window_the_comparison_is_taken_over`.
FIT_COMPARISON_WINDOW = range(2017, 2025)

#: A YEAR WHOSE ANCHOR IS NOT IDENTIFIED APPLIES NO LEVEL CORRECTION, and 1.0 is not a number
#: picked to fill a slot -- it is the IDENTITY of this parameter and `build_departure_risks`'s own
#: default for it, i.e. the arithmetic form of "no calibration is identified". The alternative on
#: offer was the reference year's anchor, and this file's own docstring below already establishes
#: that borrow is wrong on the one year it fires on: 1.98x, on the record's LOWEST year, in the
#: direction that ADDS departures. A borrowed calibration is a claim; the identity is the absence
#: of one, and a reader can tell it from a fit at a glance in the capture's `sim_level_anchor`
#: column -- which is precisely how the last unfitted block was detected at all.
NO_LEVEL_CORRECTION = 1.0

#: `{calendar year: anchor}`, fitted by `tools/fit_year_level_anchor.fit_year_anchor_on_book` on the
#: TWO-ROUTE capture `docs/reports/ladder_churn_factors.json` + its `_svt_segment_decisions.json`
#: sibling, at the declared (a_shock, scale) pair, by bisection onto `market_departure_rate(year)`.
#:
#: THE PROVENANCE IS MEASURED, NOT CITED, because the block this replaced could not be followed.
#: Its docstring named `docs/reports/c2_departure_factors.json` as its fit input; that file was
#: overwritten in place by `b46318106` a day after the block landed, and the artefact carrying the
#: name today RAN UNDER THIS BLOCK. The citation resolved, at HEAD, to a capture produced two steps
#: later by its own successor -- `figures_on_a_superseded_clock`, with a stable path over a moving
#: run. So the direction here was established from the artefacts instead: every capture records the
#: anchor it executed under in its `sim_level_anchor` column, and reading that column across every
#: capture on disk gives ten-year block -> `ladder` capture -> THIS block -> `c2` capture. The
#: retired ten-year table, the side-by-side against this one and why it could not be re-cited are in
#: `docs/design/THE_LEVEL_ANCHOR_COLLISION_ANSWERED_2026-09-02.md`; this block's own byte-exact
#: preservation, taken on 2026-09-01 when it was in no commit, is in
#: `docs/design/UNLANDED_WHOLE_BOOK_LEVEL_ANCHOR_BLOCK_2026-09-01.md`.
#:
#: THOSE WERE ONE CITATION UNTIL 2026-09-02 AND IT POINTED AT THE WRONG DOCUMENT. The single pointer
#: named the `UNLANDED_...` preservation as the home of the retired table. That document holds THIS
#: block -- the live one -- and carries none of the retired table's ten values. So the sentence
#: directly above, which exists to say that the block this replaced could not be followed, sat one
#: line above a citation that could not be followed either: a real, committed, on-origin document
#: that does not contain the thing it is cited for. Note what would NOT have caught it -- a link
#: checker asserting the path resolves passes, because the path does resolve. Held by
#: `tests/simulation/test_departure_risks.py::test_the_document_cited_for_the_retired_table_contains_the_retired_table`,
#: which reads the cited document for the values rather than for its existence.
#:
#: THE DENOMINATOR IS ACCOUNT-YEARS AND THAT IS THE WHOLE CHANGE HERE. The block this replaced was
#: fitted on a renewal-only capture -- and since C1b a renewal decision is a SELECTED
#: sub-population, the households that took a fixed deal, because an SVT account can leave without
#: ever reaching a renewal roll. Anchoring their mean onto a whole-population published rate fits
#: the world to the households that demonstrably shop. The union combines an account's decisions on
#: both routes within the account (`1 - PROD(1-p)`) and means over ACCOUNTS, not decisions; a mean
#: over decisions reads 3.6-7.5% and inverts the sign of the error in 2022. It is an UPPER bound,
#: per `departure_population.BOOK_BOUND`.
#:
#: THREE YEARS ARE ABSENT ON PURPOSE. They are enumerated in `UNFITTED_YEARS` below with a cause
#: each, and they must NOT be interpolated: an absence nobody explains and an absence nobody
#: thought about are the same hole in the block.
#:
#: THE FIT IS EXACT ON THE RUN IT WAS FITTED TO AND APPROXIMATE ON THE NEXT ONE, which is a
#: property of the thing and not a defect in the fit: raising the level changes the book, so the
#: population the following year is not the one the anchor was solved against. The iteration is
#: capture -> fit -> capture; the band is what says when it has converged.
YEAR_LEVEL_ANCHOR: dict[int, float] = {
    2017: 4.547299,
    2018: 2.882178,
    2019: 4.803900,
    2020: 6.412007,
    2021: 4.488202,
    2023: 0.364038,
    2024: 3.053619,
}

#: `{year inside the published record with no fitted anchor: WHY}`. This is the half of the
#: partition that makes the guard below liveable, and every entry is a claim an artefact can
#: contradict -- `test_switching_rate_commons` corroborates each against the capture and the record
#: rather than taking it on trust, because a producer that can retire a year by NAMING it refused
#: is the catalogued *refusal names a cause the checker never observed*.
#:
#: THE THREE CAUSES ARE NOT ALIKE AND THE FALLBACKS DIFFER ACCORDINGLY. 2016 and 2025 are outside
#: the comparison window and take the reference year's anchor; 2022 is inside it, is unidentified,
#: and takes `NO_LEVEL_CORRECTION`. A reader shown one cause for all three would go looking for
#: renewal decisions in 2016, which would not help.
UNFITTED_YEARS: dict[int, str] = {
    2016: (
        "2016 is OUTSIDE the comparison window (2017-2024) the fit is scoped to: it carries 1 "
        "renewal decision in `c2` and `ladder` and 3 in `c3`, and solves to an anchor near 16 to "
        "six decimals. An edge year cannot carry a fit and this one was never asked to."
    ),
    2022: (
        "2022 is INSIDE the comparison window and is UNIDENTIFIED. ONE cause binds, and until "
        "2026-09-02 this entry said two did. (i) THE ONE THAT BINDS, and it is CAPTURE-SCOPED: "
        "2022 is 100% crisis-forced-passive (`renewal_engagement.CRISIS_PASSIVE_YEARS`), C1b "
        "routes every passive roll to the SVT segment table, and the `c2`/`ladder`/native capture "
        "family therefore carries ZERO 2022 renewal decisions, so the anchor multiplies nothing "
        "and floor equals ceiling. `c3_shown_price_departure_factors.json` carries 53 renewal rows "
        "in 2022 under the retired ten-year block, so a re-capture CAN close this one. (ii) THE "
        "SECOND CAUSE WAS VOIDED BY THE MARKET TERM AND IS KEPT HERE RATHER THAN DELETED, because "
        "a refusal whose superseded reason is erased takes the evidence that it was ever checked "
        "with it. It read: 'its SVT floor was 12.09% against a published 4.30% ceiling, and "
        "`build_departure_risks` deliberately does not scale `svt_inertia`, so NO anchor >= 0 "
        "brought 2022 to the record.' The middle clause is still true and is not what moved: the "
        "ANCHOR still does not reach `svt_inertia` -- `departure_risks`'s `CAUSE_SVT_INERTIA` line "
        "carries no `level_anchor`. THE FLOOR IS WHAT MOVED. `c628cb37d` gave `svt_inertia_hazard` "
        "a required `market_switching_multiplier`, and recomputed under that hazard its SVT floor "
        "is 2.54% against a published 4.30% ceiling -- BELOW the target, not 7.8pp above it. THAT "
        "FIGURE READ 2.34% UNTIL 2026-09-02 AND ITS CAPTURE WAS NOT COMMITTED: it was re-driven "
        "from `c2_departure_factors.json` paired with an UNTRACKED SVT sibling, which is why the "
        "leg holding it was green in one worktree and red at clean HEAD in every other. It is now "
        "re-driven from `c4_whole_book_departure_factors.json`, the first capture whose two files "
        "describe ONE run with every producer committed. The conclusion is unchanged and was "
        "reached twice independently: a fresh whole-book capture from a clean stem of `19e68169b` "
        "measures 2022's expected departure rate at 2.54% against the same band, and the retired "
        "`ladder` pair re-drives to 2.33%. Every route puts the floor near 2.5%, not near 12%. "
        "THE UNREACHABILITY ARGUMENT THEREFORE INVERTED: 2022 is "
        "now SHORT of the record, which is the direction an anchor exists to close, and the only "
        "thing stopping it is the absent renewal population in (i). The present-tense floor above "
        "is held against a live recomputation by `test_switching_rate_commons.py::test_every_"
        "declared_svt_floor_reproduces_under_the_hazard_the_world_actually_runs`; the past-tense "
        "one is a quotation and is deliberately outside that leg's grammar. Do not clamp it, do "
        "not widen the band, do not interpolate."
    ),
    2025: (
        "2025 is OUTSIDE the comparison window (2017-2024) the fit is scoped to: it is a PARTIAL "
        "year in every capture on disk (15-35 rows against a full year's 49-59), so its realised "
        "rate is not a year's rate and an anchor fitted onto it would be calibrating to a stub."
    ),
}


def year_level_anchor(year: int) -> float:
    """The level anchor for a calendar year.

    OUTSIDE THE RECORD IT IS THE REFERENCE YEAR'S, AND THAT IS NOT A SHRUG. Every hazard already
    carries `market_switching_multiplier(year)`, which is the record's own level ratio inside the
    window and the scaled savings curve's outside it -- so the year-to-year LEVEL movement for a
    synthetic future is already accounted for by that term, and what this has to supply is the
    calibration of the factor population to a rate, which is a property of the population and not
    of the year. Taking the reference year's value says exactly that.

    INSIDE THE RECORD, A MISSING YEAR IS A REFUSAL AND NOT A FALLBACK -- AND UNTIL 2026-09-01 THIS
    BRANCHED ON THE WRONG SET. The condition was `YEAR_LEVEL_ANCHOR.get(year, ...)`, i.e. absence
    from the FITTED TABLE, while the paragraph above justifies the fallback by absence from the
    RECORD. Those are two different sets. They coincide exactly today -- both are 2016-2025 -- which
    is why it went unseen; `market_departure_rate` two files over already branches the right way,
    on `if year in published`.

    THE NATIVE SVT CAPTURE IS THE PROOF THEY COME APART. `9a03f3b44` measured
    `year_level_anchor(2022)` at 3.053619 in a run whose (uncommitted) block was missing 2022,
    against 1.524110 committed. 2022 is squarely INSIDE the record; it silently took the reference
    year's value under an argument written only for synthetic futures, and nothing said so.

    AND THE SENTENCE THAT USED TO END THIS DOCSTRING WAS FALSE ON THE CASE IT FIRED ON. It claimed
    the fallback "fails toward the record rather than toward the 3.45x-short world, which is the
    direction a fallback should fail in". Against each year's own fitted anchor the reference year's
    is 0.657x at 2016 and 1.982x at 2022 -- it overshoots on three of the nine non-reference years
    and undershoots on six, so it has no direction at all. On 2022, the record's LOWEST year at
    4.30%, it nearly doubles the anchor and therefore pushes departures UP, away from the record.
    The old claim holds only against the alternative of no anchor at all, which is not the live
    alternative. It is corrected here rather than deleted so the next reader can see it was made.

    AND "REFUSE OR FALL BACK" WAS A FALSE CHOICE, SETTLED 2026-09-02. The guard above was keyed to
    the RECORD, so the whole-book re-fit -- which honestly identifies seven years of ten -- made the
    accessor raise on 2016, 2022 and 2025 term starts. Those occur in every capture on disk, and
    `year_level_anchor` is on the run's hot path (`customer_events:610`, `run_phase2b:1634/1667/
    1719`), so refusing crashes the world on the record it exists to run. Falling back silently is
    the 1.98x defect above. NEITHER IS THE ANSWER: it is a PARTITION, the shape
    `measure_departure_level.realised_rate_coverage` already uses. A record year is FITTED, or it is
    UNFITTED WITH A DECLARED CAUSE. The guard is unchanged in condition and can still fire -- an
    undeclared gap inside the record still raises -- and what lifts it is a named reason an artefact
    can contradict, never a value.

    So: fitted, return it. Inside the record and undeclared, fail closed and name the reason.
    Inside the record and declared, return the declared value and say so through `anchor_coverage`.
    Outside the record, the reference year's value, unchanged.
    """
    if year in YEAR_LEVEL_ANCHOR:
        return YEAR_LEVEL_ANCHOR[year]
    if year in _published_departure_rates():
        if year not in UNFITTED_YEARS:
            raise ValueError(
                f"no fitted level anchor for {year}, which is INSIDE the published switching "
                f"record ({min(_published_departure_rates())}-"
                f"{max(_published_departure_rates())}), and no declared cause for its absence. "
                "The reference year's anchor is NOT a stand-in: it is fitted to that year's factor "
                "population, and against 2022's own value it runs 1.98x. Either re-fit with "
                "`tools/fit_year_level_anchor.py` and land the block, or declare the year in "
                "`UNFITTED_YEARS` with a cause the capture corroborates -- do not let the fallback "
                "cover a gap inside the record."
            )
        return _unfitted_anchor(year)
    return YEAR_LEVEL_ANCHOR[MULTIPLIER_REFERENCE_YEAR]


def _unfitted_anchor(year: int) -> float:
    """The declared value for a record year the fit does not carry -- and the case decides it.

    Inside the comparison window the fit CLAIMED the year and could not identify it, so no level
    correction is applied. Outside it the fit never claimed the year, and the reference year's
    anchor carries the same justification it carries for a synthetic future: the year-to-year LEVEL
    movement is already in `market_switching_multiplier(year)`, and what this supplies is the
    calibration of the factor population to a rate -- a property of the population, not of the year.
    """
    if year in FIT_COMPARISON_WINDOW:
        return NO_LEVEL_CORRECTION
    return YEAR_LEVEL_ANCHOR[MULTIPLIER_REFERENCE_YEAR]


def anchor_coverage() -> tuple[dict[int, float], dict[int, tuple[float, str]]]:
    """`({year: fitted anchor}, {year: (declared value, why there is no fit)})`, a PARTITION.

    WHY A SECOND FUNCTION AND NOT A WIDER RETURN. `year_level_anchor` hands back a float and a float
    cannot say whether it was fitted. That is not a hypothetical loss: the previous unfitted block
    was detected ONLY because its three unfitted years all read `3.053619` in a capture's
    `sim_level_anchor` column, which is a coincidence of the fallback and not a disclosure. A
    consumer that publishes a per-year level must be able to ask which years are fits, and every
    record year must appear in exactly one side -- a year that is in NEITHER has left the subject
    silently, which is how an emptied subject reaches a constant PASS.
    """
    record = _published_departure_rates()
    fitted = {y: YEAR_LEVEL_ANCHOR[y] for y in record if y in YEAR_LEVEL_ANCHOR}
    unfitted = {
        y: (_unfitted_anchor(y), UNFITTED_YEARS[y])
        for y in record
        if y not in YEAR_LEVEL_ANCHOR and y in UNFITTED_YEARS
    }
    return fitted, unfitted


__all__ = [
    "FIT_COMPARISON_WINDOW",
    "NO_LEVEL_CORRECTION",
    "UNFITTED_YEARS",
    "YEAR_LEVEL_ANCHOR",
    "anchor_coverage",
    "year_level_anchor",
]
