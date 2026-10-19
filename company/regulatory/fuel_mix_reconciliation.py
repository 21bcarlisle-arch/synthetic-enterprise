"""What the annual report's two `Low Carbon %` columns each measure, stated where they are read.

The report publishes `Low Carbon %` in two sections, for overlapping years, from two tables:

* `company/regulatory/carbon_emissions.py::UK_GRID_FUEL_MIX` renders the **Carbon Emissions
  Reporting Observatory**. Since 2026-10-19 it is the UK GENERATION mix, DUKES 5.6.C, calendar year.
* `company/billing/fuel_mix.py::_FUEL_MIX_BY_YEAR` renders the **UK Grid Fuel Mix Disclosure**.
  Since 2026-10-19 it is DESNZ's FMD UK fuel mix: SUPPLY basis, imports at the European Attribute
  Mix, 1 April to 31 March.

TWO FACTS, NOT ONE. Until 2026-10-19 this module said "at most one is right": both were undated hand
tables up to 3.4pp apart, and choosing one would have revalued a published table on a guess. Both
sources have now been fetched, and DESNZ's own disclosure table says the two differ by construction
(its note 5). So both are right about different things, and the note says what each one is. The
sources, vintages and gap are in
`docs/market_research/two_uk_electricity_fuel_mixes_generation_and_disclosure.md`.

THIS MODULE DECLARES NO THIRD SERIES. Every number in the note is read from the two owners at call
time, so an edit to either table moves the published sentence with it.

BASIS of the comparison: both sides count renewable (bioenergy included) + nuclear. The Observatory
sums wind/solar/hydro + nuclear + biomass. The Disclosure's single `renewable` bucket already
includes biomass.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

#: The two section headings as they are rendered, so the note can point the reader at the other
#: one BY NAME. A cross-reference to "the other table" is not a cross-reference.
OBSERVATORY_SECTION = "Carbon Emissions Reporting Observatory"
DISCLOSURE_SECTION = "UK Grid Fuel Mix Disclosure"

#: Where each side comes from, with its basis and vintage, for the note's provenance clause.
OBSERVATORY_ORIGIN = (
    "the UK generation mix (DESNZ DUKES Table 5.6.C, calendar year, generation only, no imports; "
    "published 30 July 2026)"
)
DISCLOSURE_ORIGIN = (
    "the UK Fuel Mix Disclosure comparison mix (DESNZ Fuel mix disclosure data table, 1 April to "
    "31 March, electricity supplied including imports at the European Attribute Mix; one edition "
    "per period, 2019/20 to 2025/26)"
)


@dataclass(frozen=True)
class LowCarbonDivergence:
    """One year's disagreement. `diff_pp` is Observatory minus Disclosure, signed."""

    year: int
    observatory_pct: float
    disclosure_pct: float

    @property
    def diff_pp(self) -> float:
        return round(self.observatory_pct - self.disclosure_pct, 1)

    @property
    def abs_diff_pp(self) -> float:
        return abs(self.diff_pp)


def reconcile_low_carbon() -> List[LowCarbonDivergence]:
    """Read both published tables and return the per-year `Low Carbon %` divergence.

    Imports are function-local and deliberate: `company.regulatory` importing `company.billing` at
    module scope would make a reporting VIEW into a package-level dependency between two layers
    that have no business depending on each other.
    """
    from company.billing.fuel_mix import _FUEL_MIX_BY_YEAR as _DISCLOSURE
    from company.regulatory.carbon_emissions import UK_GRID_FUEL_MIX as _OBSERVATORY

    rows: List[LowCarbonDivergence] = []
    for year in sorted(set(_OBSERVATORY) & set(_DISCLOSURE)):
        disclosure = _DISCLOSURE[year]
        rows.append(
            LowCarbonDivergence(
                year=year,
                observatory_pct=_OBSERVATORY[year].low_carbon_pct,
                disclosure_pct=round(disclosure["renewable"] + disclosure["nuclear"], 1),
            )
        )
    return rows


def worst_divergence() -> Optional[LowCarbonDivergence]:
    """The year the two tables are furthest apart, or None if they share no years."""
    rows = reconcile_low_carbon()
    if not rows:
        return None
    return max(rows, key=lambda r: r.abs_diff_pp)


def divergence_note(section: str) -> str:
    """The paragraph rendered under `section`'s table, DERIVED from both tables.

    Returns "" only when the two share no years, so there is nothing to compare. When they share
    years the note always renders, because what it says first (two different quantities) is true
    whatever the figures are.
    """
    if section not in (OBSERVATORY_SECTION, DISCLOSURE_SECTION):
        raise ValueError(f"unknown section {section!r}")

    rows = reconcile_low_carbon()
    worst = worst_divergence()
    if worst is None:
        return ""

    other = DISCLOSURE_SECTION if section == OBSERVATORY_SECTION else OBSERVATORY_SECTION
    this_origin = OBSERVATORY_ORIGIN if section == OBSERVATORY_SECTION else DISCLOSURE_ORIGIN
    other_origin = DISCLOSURE_ORIGIN if section == OBSERVATORY_SECTION else OBSERVATORY_ORIGIN
    if worst.abs_diff_pp == 0.0:
        gap = "In the years both cover, they happen to agree."
    else:
        higher = OBSERVATORY_SECTION if worst.diff_pp > 0 else DISCLOSURE_SECTION
        gap = (
            f"Over {rows[0].year}-{rows[-1].year} they differ by up to {worst.abs_diff_pp:.1f}pp "
            f"({worst.year}: {worst.observatory_pct:.1f}% in the {OBSERVATORY_SECTION}, "
            f"{worst.disclosure_pct:.1f}% in the {DISCLOSURE_SECTION}, the {higher} higher)."
        )

    return (
        f"> **Not the same figure as the {other} section.** This section's `Low Carbon %` is "
        f"{this_origin}; the other section's is {other_origin}. Both count renewables (bioenergy "
        f"included) plus nuclear, but they are two different quantities, and DESNZ notes that they "
        f"differ. The disclosure basis adds imports and runs April to March. {gap} The grid "
        f"INTENSITY column is neither mix: it is NESO's published series."
    )
