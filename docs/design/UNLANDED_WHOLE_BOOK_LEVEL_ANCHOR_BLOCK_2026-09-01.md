# The unlanded whole-book `YEAR_LEVEL_ANCHOR` block, preserved verbatim

**Filed 2026-09-01, delivery seat, from the shared checkout. This document adopts nothing, fits
nothing and decides nothing.** It exists for one reason: at the moment it was written,
`simulation/departure_level_anchor.py` in this checkout was a version that existed **in no commit
and in no reflog**, and therefore one `git checkout <path>` — or one careless `-A` — from being
destroyed with no route back.

Verified before writing, not assumed:

```
$ git log --all --reflog -S'0.364038' -- simulation/departure_level_anchor.py
(no output)
```

`--all` alone would not have settled this: six sibling worktrees share this object store and each
carries a **detached HEAD**, which `--all` does not enumerate. `--reflog` was added for that reason.

**Recovery is byte-exact.** The content below is the whole file as it stood, sha256
`1ece30c41f3cec3c7a91f00e432b55013b4a7a92df82971f6b04034d1f117236`. To restore it, write the fenced block back to
`simulation/departure_level_anchor.py` and check the digest matches.

## What this block is, and what the record got backwards

The finding that first reported this collision —
`docs/staging/WORKER_FINDING_THE_LEVEL_ANCHOR_GUARD_IS_GREEN_AT_HEAD_AND_RED_IN_THE_TREE_THE_WORLD_ACTUALLY_RUNS_FROM_2026-09-01.md`
— read this file as *"old content that HEAD has since superseded"*. **It is the opposite: this is
HEAD's successor.** The correction, with the measured capture chain that establishes the direction,
is appended to that finding. In one line: HEAD's ten-year table was the block the
`ladder_churn_factors.json` capture *ran under*, and this seven-year block is the fit *of* that
capture — so HEAD is the predecessor and this is the next iterate.

**It is preserved, not endorsed.** Landing it as-is composes with the fail-closed guard at
`9fd700366` to raise on 2016 and 2025 term starts, which occur in every capture on disk. That
collision is a real design decision and it belongs to the lane that fitted the block. Preserving the
content is what removes the *deadline* from that decision; it does not take it.

---

```python
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

#: `{calendar year: anchor}`. Fitted by `tools/fit_year_level_anchor.fit_year_anchor_on_book` on the
#: TWO-ROUTE capture `docs/reports/ladder_churn_factors.json` + its `_svt_segment_decisions.json`
#: sibling, at the declared (a_shock, scale) pair, by bisection onto `market_departure_rate(year)`.
#:
#: THE DENOMINATOR IS ACCOUNT-YEARS AND THAT IS THE WHOLE CHANGE HERE. The block this replaced was
#: fitted on `c2_departure_factors.json`, which is a renewal-only capture -- and since C1b a renewal
#: decision is a SELECTED sub-population, the households that took a fixed deal, because an SVT
#: account can leave without ever reaching a renewal roll. Anchoring their mean onto a
#: whole-population published rate fits the world to the households that demonstrably shop. The
#: union combines an account's decisions on both routes within the account (`1 - PROD(1-p)`) and
#: means over ACCOUNTS, not decisions; a mean over decisions reads 3.6-7.5% and inverts the sign of
#: the error in 2022. It is an UPPER bound, per `departure_population.BOOK_BOUND`.
#:
#: THREE YEARS ARE ABSENT ON PURPOSE AND MUST NOT BE INTERPOLATED -- an absence nobody explains and
#: an absence nobody thought about are the same hole in the block itself, and `year_level_anchor`
#: falls back for both. Each refusal is `fit_year_anchor_on_book`'s, printed by the tool, and the
#: fallback is declared where an invented value would not be:
#:
#:   * **2016 and 2025** are outside the declared comparison window 2017-2024. The edge years cannot
#:     carry a fit -- 2016 holds ONE renewal decision in this capture and solves to an anchor near
#:     16 to six decimals, and 2025 is partial.
#:   * **2022 is UNIDENTIFIED, and the fallback does not repair it.** The year has zero renewal
#:     decisions here, so the anchor multiplies nothing: floor equals ceiling and no value of this
#:     constant moves it by a basis point. Independently, its SVT floor is 12.09% against a
#:     published 4.30% -- `build_departure_risks` deliberately does not scale `svt_inertia`, so no
#:     anchor >= 0 brings the book down to the record. Both causes bind; a reader shown only the
#:     first would go looking for renewal decisions, which would not help. Do NOT clamp it and do
#:     not widen the band: it is a result about the mechanism, and it is the subject of
#:     `SEAT_FINDING_THE_DEPARTURE_LEVEL_UNIONED_ONTO_ACCOUNT_YEARS_AND_2022_HAS_NO_LEVER`.
#:
#: THE FIT IS EXACT ON THE RUN IT WAS FITTED TO AND APPROXIMATE ON THE NEXT ONE, which is a
#: property of the thing and not a defect in the fit: raising the level changes the book, so the
#: population the following year is not the one the anchor was solved against. This capture's
#: `sim_level_anchor` column was checked row by row against the block it replaced and matches it in
#: all nine years, so this is one clean capture -> fit step and not a fit against a different run.
#: The iteration is capture -> fit -> capture; the band is what says when it has converged.
YEAR_LEVEL_ANCHOR: dict[int, float] = {
    2017: 4.547299,
    2018: 2.882178,
    2019: 4.803900,
    2020: 6.412007,
    2021: 4.488202,
    2023: 0.364038,
    2024: 3.053619,
}


def year_level_anchor(year: int) -> float:
    """The level anchor for a calendar year.

    UNFITTED IT IS THE REFERENCE YEAR'S, AND THAT IS NOT A SHRUG. Every hazard already carries
    `market_switching_multiplier(year)`, which is the record's own level ratio inside the window and
    the scaled savings curve's outside it -- so the year-to-year LEVEL movement is already accounted
    for by that term, and what this has to supply is the calibration of the factor population to a
    rate, which is a property of the population and not of the year. Taking the reference year's
    value says exactly that. It fails toward the record rather than toward the 3.45x-short world,
    which is the direction a fallback should fail in.

    TWO KINDS OF YEAR REACH THAT FALLBACK NOW, AND ONLY ONE OF THEM IS BENIGN. A synthetic year
    outside 2016-2025 is the case above. But since the whole-book re-fit, 2016, 2022 and 2025 are
    IN the record and still land here, because `fit_year_anchor_on_book` refused them -- and for
    2022 the fallback is not a calibration choice but the absence of any lever at all: its SVT floor
    sits 7.8pp above its published ceiling, so no value returned from this function can put that
    year inside its band. Reading a fallback here as "close enough" would be reading a refusal as an
    answer. The reasons are enumerated beside `YEAR_LEVEL_ANCHOR` and the band control is what
    fails; do not repair it here.
    """
    return YEAR_LEVEL_ANCHOR.get(year, YEAR_LEVEL_ANCHOR[MULTIPLIER_REFERENCE_YEAR])


__all__ = ["YEAR_LEVEL_ANCHOR", "year_level_anchor"]
```
