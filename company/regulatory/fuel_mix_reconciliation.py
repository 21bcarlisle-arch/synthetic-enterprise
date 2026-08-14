"""Reconciliation VIEW over the two published UK grid fuel-mix tables.

WHY THIS EXISTS. The annual report publishes a `Low Carbon %` column twice, for the same years,
under the same metric name, from two independently maintained tables:

* `company/regulatory/carbon_emissions.py::UK_GRID_FUEL_MIX` — 8 buckets, renders the
  **Carbon Emissions Reporting Observatory** (and, via the per-fuel factors, its intensity series).
* `company/billing/fuel_mix.py::_FUEL_MIX_BY_YEAR` — 5 buckets, renders the
  **UK Grid Fuel Mix Disclosure**.

They disagree by up to 3.4pp and the sign of the difference flips across the decade
(`docs/staging/done/WORKER_FINDING_TWO_PUBLISHED_FUEL_MIX_TABLES_DISAGREE_ON_LOW_CARBON_2026-08-14.md`,
archived on discharge — the path moved with it, so this citation is not one of the 66 dead ones).
At most one is right. Choosing which would revalue a published table on the guesser's authority,
with no fetched source to justify it — `EP13_adapter_carbon_intensity` is the atom that sources it
properly, and it is epoch-3 parked. So the finding's *second* discharge is taken here: **the
limitation is stated in the report itself**, where the reader of the two tables is, rather than
only in a finding document they will never see.

THIS MODULE DECLARES NO THIRD SERIES. Every number below is READ from the two owners at call time.
That is the whole design: a disclosure note carrying hardcoded divergence figures would be a third
copy of the same disagreement, decaying silently the first time either table is edited — the exact
shape `tools/grid_intensity_guard.py` exists to prevent. Edit either table and the published
sentence moves with it; make them agree and the note says they agree.

BASIS. The comparison is like-for-like, which is what makes the residue a *data* disagreement
rather than a definitional one: both sides count renewable + nuclear + biomass. The Observatory's
`low_carbon_pct` sums wind/solar/hydro + nuclear + biomass explicitly; the Disclosure's single
`renewable` bucket already includes biomass (2023: 47.8% against the Observatory's 35.0% renewable
+ 10.0% biomass = 45.0%). Neither table is a partial mix — both sum to 100.0% in all ten years.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

#: The two section headings as they are rendered, so the note can point the reader at the other
#: one BY NAME. A cross-reference to "the other table" is not a cross-reference.
OBSERVATORY_SECTION = "Carbon Emissions Reporting Observatory"
DISCLOSURE_SECTION = "UK Grid Fuel Mix Disclosure"

#: Where each side comes from, for the note's provenance clause. Both cite the same publisher and
#: NEITHER carries a vintage — which is itself the reason they are allowed to differ silently.
OBSERVATORY_ORIGIN = "company/regulatory/carbon_emissions.py::UK_GRID_FUEL_MIX (8 buckets)"
DISCLOSURE_ORIGIN = "company/billing/fuel_mix.py::_FUEL_MIX_BY_YEAR (5 buckets)"


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


def sign_flips() -> bool:
    """True when neither table is uniformly the higher one.

    This is the load-bearing distinction and the reason the note cannot say "a definitional
    difference". A constant offset would be one definition stated once; an alternating one is two
    independently maintained series.
    """
    diffs = [r.diff_pp for r in reconcile_low_carbon() if r.diff_pp != 0.0]
    return any(d > 0 for d in diffs) and any(d < 0 for d in diffs)


def divergence_note(section: str) -> str:
    """The disclosure paragraph rendered under `section`'s table, DERIVED from both tables.

    Returns "" when there is nothing to disclose — no overlapping years, or the two tables agree
    everywhere. A note that renders unconditionally would still be there after a reconciliation and
    would then be false, so the absence of a residue must be able to silence it.
    """
    if section not in (OBSERVATORY_SECTION, DISCLOSURE_SECTION):
        raise ValueError(f"unknown section {section!r}")

    worst = worst_divergence()
    if worst is None or worst.abs_diff_pp == 0.0:
        return ""

    other = DISCLOSURE_SECTION if section == OBSERVATORY_SECTION else OBSERVATORY_SECTION
    this_origin = OBSERVATORY_ORIGIN if section == OBSERVATORY_SECTION else DISCLOSURE_ORIGIN
    other_origin = DISCLOSURE_ORIGIN if section == OBSERVATORY_SECTION else OBSERVATORY_ORIGIN
    higher = OBSERVATORY_SECTION if worst.diff_pp > 0 else DISCLOSURE_SECTION

    flip_clause = (
        "and neither section is consistently the higher one across the decade, so this is two "
        "differently-sourced mixes rather than one definitional difference"
        if sign_flips()
        else "in the same direction in every year of disagreement"
    )

    return (
        f"> **Unreconciled with the {other} section.** This report publishes `Low Carbon %` for "
        f"the same years in both sections, from two separately maintained tables — this one from "
        f"{this_origin}, the other from {other_origin}. They differ by up to "
        f"{worst.abs_diff_pp:.1f}pp ({worst.year}: {worst.observatory_pct:.1f}% in the "
        f"{OBSERVATORY_SECTION}, {worst.disclosure_pct:.1f}% in the {DISCLOSURE_SECTION}, the "
        f"{higher} higher), {flip_clause}. Both count renewable + nuclear + biomass, so the "
        f"difference is in the underlying mix and not in the definition; both sum to 100%. "
        f"**At most one of the two is right, and this report does not assert which** — neither "
        f"table carries a publication vintage, and no external source has been fetched to "
        f"adjudicate them. The figures are unchanged rather than silently reconciled to a guess; "
        f"sourcing them is `EP13_adapter_carbon_intensity`. The grid INTENSITY series has a single "
        f"owner and is not affected: it derives from the {OBSERVATORY_SECTION} mix only."
    )
