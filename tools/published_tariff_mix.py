"""The published GB domestic tariff mix, on every population it was published over.

WHY THIS EXISTS AS ONE MODULE AND NOT AS A CONSTANT IN THE TOOL THAT NEEDED IT
------------------------------------------------------------------------------
It already existed three times. `docs/market_research/svt_rates_active_passive_2016_2025.md` §2-3
holds it as prose; `docs/design/DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md` §(b) restates it
as a table; `tools/svt_generated_share_check.PUBLISHED_DOMESTIC_FIXED_SHARE` copied it a third time
as a Python dict. No lane pointed at any of them from
`SEAT_FINDING_THE_LEVEL_IS_CLAMPED_...` which needed exactly this series, and two focus items were
independently about to source it again. That is this repository's VAT shape -- one published
quantity, N implementations, a correction applied to one of them -- and the fix for it is structural.
This module is the one home. `docs/market_research/gb_domestic_default_tariff_share_2016_2025.md`
is its prose write-up and cites it rather than repeating the numbers.

THE CORRECTION THAT MADE THIS WORTH DOING, AND IT IS NOT AN ARITHMETIC ONE
--------------------------------------------------------------------------
**Ofgem's headline default-tariff share EXCLUDES PREPAYMENT CUSTOMERS, all three in-tree copies
dropped that qualifier, and more than 90% of prepayment customers are on a default tariff.** The
2019 State of the Market report says it in one sentence -- *"As of April 2019, 53% of electricity
customer accounts and 51% of gas accounts, **excluding customers on prepayment**, were still on
default tariffs"* -- and separately that PPM was *"4.3 million customers ... around 15% of all
customers in GB"* of whom *"more than 90% ... continue to be on SVTs"*. So the all-domestic share in
2019 is not 53%. It is about 59%.

Which of the two bases is the right comparator for THIS world is **not settled**, and this module
refuses to settle it: `simulation/population_draw.py` gives a household
`payment_method: "direct_debit" | "other"` and models no prepayment meter at all, so the world's
book is neither the published non-PPM population nor the published all-domestic one. Both bases are
therefore carried, per year, and every consumer is made to name which it used. That is not
fastidiousness -- on the non-PPM basis this world's 2018 and 2019 SVT share reads 1.7pp and 2.3pp
ABOVE the published figure, and on the PPM-restored basis it reads 4.3pp and 3.7pp BELOW it. The
verdict for those two years is the basis, not the measurement.

WHAT IS A GAP HERE IS AN EXPLICIT `None`, NOT AN INTERPOLATION
---------------------------------------------------------------
2020 and 2021 have no established figure. The obvious move is to interpolate between 2019 and 2022
and the obvious move is refused: the interval it would span contains the crisis, which is the one
period in the record where the series is known to have moved non-monotonically and fast. A `None`
with a named reason cannot be mistaken for evidence and an interpolated 0.70 can. Consumers get
`None` and must fail closed on it.

ALL OF THIS IS A CHECK AND NONE OF IT IS AN INPUT
--------------------------------------------------
`simulation/svt_product.py` states the rule this module inherits: *"the published year-by-year
fixed/SVT split printed beside the result as a CHECK. Never an input: if the split has to be set to
land in range, the behaviour is wrong and setting it hides that."* Nothing in `simulation/` may
import this module, and `tests/architecture/test_switching_rate_commons.py` holds that as a control.

REUSE
-----
REUSE: tools/published_tariff_mix.py
CLASS: CUSTOM
INDEX: searched "tariff mix", "published share", "svt share", "default tariff", "fixed share",
       "market_research", "commons", "anchor", "band".
       `tools/svt_generated_share_check.PUBLISHED_DOMESTIC_FIXED_SHARE` is the nearest existing row
       and is the thing being REPLACED rather than reused -- it is a bare dict of fixed-share bands
       with the population qualifier dropped, which is the defect above, and it has no second basis
       and no gap representation to extend. That tool now imports from here.
       `simulation/svt_rates.py` is the same SHAPE (a published series keyed by period) and is
       deliberately not extended: it holds a world INPUT that settlement reads, and folding a check
       band into it would put the judge inside the thing being judged, which
       `svt_generated_share_check`'s own docstring forbids in terms.
       `docs/market_research/` is prose and cannot be imported by a control.
"""
from __future__ import annotations

from dataclasses import dataclass

#: Ofgem, State of the Market 2019, §3.56: PPM was 4.3m customers, "around 15% of all customers in
#: GB", as of March 2019. Held as the share used to restore prepayment to the non-PPM series.
PPM_SHARE_OF_DOMESTIC_ACCOUNTS = 0.15

#: Ofgem, State of the Market 2019, §3.60: "More than 90% of prepayment customers continue to be on
#: SVTs." A floor, so restoration using it is a LOWER bound on the all-domestic share -- the
#: direction that understates the gap this world is being measured for.
PPM_SHARE_ON_DEFAULT_TARIFF = 0.90


@dataclass(frozen=True)
class TariffMixRow:
    """One year's published default-tariff share, with the population it was published over.

    `as_published` is the figure exactly as its source states it. `population` says what that
    figure counts, in the source's own terms, and is the field that stops the ratio being taken
    against the wrong denominator. `excludes_prepayment` is machine-readable because the whole
    correction above turns on it.
    """

    as_published: tuple[float, float] | None
    population: str
    source: str
    confidence: str
    excludes_prepayment: bool
    note: str = ""

    def on_basis(self, basis: str) -> tuple[float, float] | None:
        """The share on `as_published` or on `all_domestic`, or None where nothing is established.

        Restoration is `(1 - ppm) * non_ppm + ppm * ppm_on_default` and is applied ONLY to a row
        that excludes prepayment. A row already published over the whole domestic book is returned
        unchanged on both bases rather than restored twice, which is the arithmetic that would
        otherwise silently add six points to the crisis years.
        """
        if basis not in ("as_published", "all_domestic"):
            raise ValueError(f"unknown basis {basis!r}; expected 'as_published' or 'all_domestic'")
        if self.as_published is None:
            return None
        if basis == "as_published" or not self.excludes_prepayment:
            return self.as_published
        return tuple(  # type: ignore[return-value]
            round(
                (1.0 - PPM_SHARE_OF_DOMESTIC_ACCOUNTS) * endpoint
                + PPM_SHARE_OF_DOMESTIC_ACCOUNTS * PPM_SHARE_ON_DEFAULT_TARIFF,
                4,
            )
            for endpoint in self.as_published
        )


#: Share of GB DOMESTIC accounts on a default / standard-variable tariff, by calendar year.
#: A band, never a point: every underlying figure is a single-date reading and the year is longer
#: than the reading. Years with no established figure are present with `as_published=None` so that
#: a consumer sees a declared gap rather than a missing key it can `.get(year, something)` past.
DEFAULT_TARIFF_SHARE: dict[int, TariffMixRow] = {
    2016: TariffMixRow(
        as_published=(0.66, 0.74),
        population="Big Six domestic customers; CMA's own population, not all of GB",
        source="CMA Energy Market Investigation final report 2016 ('70%+'); Ofgem SotM 2019 §3.24 "
               "gives 'around 69% in 2015' for customer accounts on default tariffs",
        confidence="M",
        excludes_prepayment=False,
        note="The CMA figure is over the Big Six, who were not the whole market even in 2016, and "
             "the 2015 Ofgem figure does not state whether it excludes prepayment. Banded wide "
             "for both reasons rather than quoted as 70%.",
    ),
    2017: TariffMixRow(
        as_published=(0.57, 0.59),
        population="non-prepayment accounts at the 10 largest suppliers",
        source="Ofgem, 'Standard variable tariffs: latest trends at September 2017' — 57% at "
               "September 2017, 59% at April 2017",
        confidence="H",
        excludes_prepayment=True,
    ),
    2018: TariffMixRow(
        as_published=(0.53, 0.53),
        population="customer accounts at ~25 suppliers (~95% of the market), excluding "
                   "prepayment and excluding Bulb",
        source="Ofgem, State of the Market 2019 §3.24: 'around 69% in 2015 and gradually fell to "
               "53% by April 2018'",
        confidence="H",
        excludes_prepayment=True,
        note="Point reading at April 2018 carried across the year; the series is described as "
             "declining gradually, so a within-year band is not established.",
    ),
    2019: TariffMixRow(
        as_published=(0.51, 0.53),
        population="electricity (53%) and gas (51%) customer accounts, excluding prepayment, "
                   "~25 suppliers ex-Bulb",
        source="Ofgem, State of the Market 2019 §3.24, as of April 2019",
        confidence="H",
        excludes_prepayment=True,
        note="This world's book is electricity, so 53% is the fuel-matched endpoint; the gas "
             "figure is kept as the band's other end rather than dropped, because the two are the "
             "only published spread on this reading.",
    ),
    2020: TariffMixRow(
        as_published=None,
        population="—",
        source="none established",
        confidence="—",
        excludes_prepayment=False,
        note="NOT interpolated between 2019 and 2022. The interval spans the crisis, which is the "
             "one stretch of this record known to have moved fast and non-monotonically, so an "
             "interpolated value would be a manufactured reading in exactly the years the world is "
             "hardest to check. Ofgem's per-supplier data portal series may settle it and has not "
             "been read.",
    ),
    2021: TariffMixRow(
        as_published=None,
        population="—",
        source="none established",
        confidence="—",
        excludes_prepayment=False,
        note="Ofgem's SotM chart 'Electricity share of customers on each tariff type' STARTS at "
             "April 2021 and would settle this, but its values are in an image and are not in the "
             "PDF's text layer. Recorded as a gap with a named route to closing it rather than "
             "read off a chart by eye.",
    ),
    2022: TariffMixRow(
        as_published=(0.80, 0.90),
        population="GB domestic accounts",
        source="Fixed deals withdrawn market-wide as wholesale exceeded the cap; ~29m of ~32m "
               "domestic customers on SVT by April 2023 (svt_rates_active_passive_2016_2025.md §3)",
        confidence="M",
        excludes_prepayment=False,
        note="Structural, not a single published reading. Banded 10pp wide for that reason.",
    ),
    2023: TariffMixRow(
        as_published=(0.80, 0.90),
        population="GB domestic accounts",
        source="~90% on SVT at April 2023; FTCs re-emerged in H2 2023 (Ofgem SotM April 2025 "
               "§'Following the re-emergence of FTCs in the second half of 2023')",
        confidence="M",
        excludes_prepayment=False,
        note="The year straddles the re-emergence, so the true within-year path falls across this "
             "band rather than sitting at a point in it.",
    ),
    2024: TariffMixRow(
        as_published=(0.80, 0.86),
        population="GB domestic electricity customers",
        source="Ofgem, State of the Market January 2026: 'By July 2025, around one-third of "
               "customers were on FTCs, twice the proportion recorded in July of the previous "
               "year' — so ~16-17% on FTCs at July 2024",
        confidence="M",
        excludes_prepayment=False,
        note="DERIVED from an explicit doubling statement against a rounded 'around one-third', "
             "not read off a chart. The band carries the rounding: one-third of 0.32-0.34 halved "
             "is 0.16-0.17 on FTCs, and the remainder is banded slightly wider than that implies "
             "because 'FTC' and 'default' do not exhaust the market in Ofgem's own note (it folds "
             "'non-standard variable/other' into SVT for reporting).",
    ),
    2025: TariffMixRow(
        as_published=(0.64, 0.70),
        population="GB domestic electricity customers",
        source="Ofgem, State of the Market January 2026: around one-third of customers on FTCs at "
               "July 2025",
        confidence="H",
        excludes_prepayment=False,
    ),
}


def default_tariff_share(year: int, basis: str = "all_domestic") -> tuple[float, float] | None:
    """The published default/SVT share band for `year`, or None where none is established.

    `basis` MUST be passed explicitly by any caller that cares which it gets, and the default is
    `all_domestic` deliberately: it is the basis whose denominator matches a whole book, and a
    caller that silently got the non-PPM series would be comparing a world with no prepayment
    concept against a population that had prepayment removed from it.
    """
    row = DEFAULT_TARIFF_SHARE.get(year)
    return None if row is None else row.on_basis(basis)


def fixed_share(year: int, basis: str = "all_domestic") -> tuple[float, float] | None:
    """The complement of the default share, as a band with its endpoints reordered.

    `1 - (lo, hi)` is `(1 - hi, 1 - lo)`, and getting that backwards produces a band whose low
    endpoint exceeds its high one -- which every `lo <= x <= hi` check in this repo would then read
    as "nothing is ever inside", a silent always-fail rather than a crash.
    """
    band = default_tariff_share(year, basis)
    return None if band is None else (round(1.0 - band[1], 4), round(1.0 - band[0], 4))


def years_with_an_established_figure() -> list[int]:
    """The years a check may compare against. Everything else must fail closed and say so."""
    return sorted(y for y, row in DEFAULT_TARIFF_SHARE.items() if row.as_published is not None)
