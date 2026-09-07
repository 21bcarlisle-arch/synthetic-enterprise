"""The published GB Capacity Market auction record, one delivery year per row.

Source: `docs/domain_artefact_library/regulatory/capacity_market_auction_results.json`, the
regulation commons. Every figure is one a real GB supplier could read off a published auction
result or an Ofgem annex. Nothing here crosses the wall.

WHY THIS MODULE EXISTS, rather than three copies of a price.

The CM clearing price had THREE homes that disagreed, and the disagreement was invisible to every
control that looked like it covered them:

  * `flexibility_potential.py`        `_CAPACITY_MARKET_GBP_PER_KW_YR = 75.0`  # T-4 auction 2023
  * `capacity_market.py`              `_CM_CLEARING_PRICE_GBP_PER_KW_PER_YEAR[2022] = 75.00`
                                                                              # Crisis year spike
  * `ic_flexibility_revenue.py`       `_CM_DELIVERY_GBP_PER_KW_YR[2023] = 15.97`  (sourced)

75.0 IS A REAL PUBLISHED FIGURE AND BOTH ITS LABELS WERE WRONG. It is the **T-1** clearing price
for **delivery year 2022/23**, which cleared AT THE PRICE CAP on a small volume -- not a T-4, not
2023, and not a "crisis year spike" anybody invented. Ofgem's Annex 9 notes column and Montel's
T-1 auction review agree on it independently. The same delivery year's T-4 was suspended and its
replacement T-3 cleared at GBP6.44/kW, the LOWEST price in the record: so the two numbers the two
homes carried for one delivery year differ by 11.6x, and both are correct, because they are two
different auctions. Conflating T-4 and T-1 is the whole defect, which is why this module keeps
them in separate fields and will not serve "the" CM price for a year.

WHAT THE THIRD HOME WAS DOING. `capacity_market.py` keyed by the year the AUCTION WAS HELD while
its own lookup named its parameter `delivery_year` -- a four-year offset with no comment. Asking
it for delivery year 2023 returned GBP63.00, the price the 2023 auction set for delivery year
2026/27, against GBP15.97 for the year actually asked about. 3.9x, silently.

A HOUSEHOLD CANNOT HOLD A CM AGREEMENT, and that is the substantive finding rather than a
modelling convenience. The minimum Capacity Market Unit is 1 MW (reduced from 2 MW). A whole
flexible house in this book is 3.0-15.4 kW, so the smallest unit that can prequalify is ~80
households. A household reaches the CM only inside an aggregator's DSR CMU, and no publication
states what an aggregator passes through to a member -- those terms are bilateral. So the
domestic leg REFUSES here rather than returning a number, and `DOMESTIC_PARTICIPATION_REFUSAL`
carries the reason to the surface that prints it.

DE-RATING IS A NAMED GAP, NOT A FACTOR OF 1.0. The CM pays on DE-RATED capacity. De-rating
factors are published per auction and per technology class and are duration-dependent for DSR and
storage; this pass did not fetch them. `derating_factor()` therefore returns `None` for every
class, and a caller that multiplies a clearing price by rated power is overstating by the whole
factor. That is the same rated-vs-delivered error the DFS pass settled in
`dfs_published_record.py`, and it is left VISIBLE rather than papered over with a plausible 0.2.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

_COMMONS = (
    Path(__file__).resolve().parents[2]
    / "docs" / "domain_artefact_library" / "regulatory"
    / "capacity_market_auction_results.json"
)

#: Provenances this module will serve as a price. `contested` and `not_applicable` rows carry
#: `None`, and a caller must not read that as zero -- see `clearing_price`.
_ACCEPTED_PROVENANCE = ("primary", "secondary")


@dataclass(frozen=True)
class CapacityMarketYear:
    """One delivery year of the published record. `None` means NOT ESTABLISHED, never zero.

    `delivery_year` is the calendar year the Oct-Sep delivery year opens in: 2022 is DY 2022/23.
    T-4 and T-1 are held apart on purpose; there is no combined field and no average, because
    averaging the two auctions for one delivery year is the arithmetic that produced this
    module's own founding defect.
    """

    delivery_year: int
    t4_gbp_per_kw_year: Optional[float]
    t1_gbp_per_kw_year: Optional[float]
    t4_provenance: str
    t1_provenance: str
    note: str
    source_label: str

    def price(self, auction: str) -> Optional[float]:
        """The clearing price for one auction of this delivery year, or `None`.

        `None` covers three distinct cases the caller may need to tell apart, and `note` carries
        which one this row is: the auction did not run for this delivery year (`not_applicable`),
        two sources disagree and this pass did not reconcile them (`contested`), or the year is
        outside the record.
        """
        if auction == "T-4":
            return self.t4_gbp_per_kw_year
        if auction == "T-1":
            return self.t1_gbp_per_kw_year
        raise ValueError(
            f"unknown auction {auction!r}: the GB Capacity Market runs 'T-4' and 'T-1', and "
            "asking for 'the' CM price without naming one is the conflation this module exists "
            "to prevent"
        )

    def established(self, auction: str) -> bool:
        return self.price(auction) is not None


def _load() -> Dict[int, CapacityMarketYear]:
    """`{delivery_year: row}` from the regulation commons.

    NO FAIL-OPEN PATH (R15). A missing, empty or malformed artefact RAISES at import. Falling
    back to the constants this module replaced, or to a plausible default, is precisely the shape
    that let GBP75/kW run as a household's annual CM revenue: an unavailable record is not a
    licence to invent one.
    """
    if not _COMMONS.exists():
        raise FileNotFoundError(
            f"Capacity Market auction commons missing: {_COMMONS}. The published auction record "
            "is required; there is no invented default."
        )
    raw = json.loads(_COMMONS.read_text())
    entries = raw.get("clearing_prices")
    if not entries:
        raise ValueError(f"CM auction commons carries no clearing_prices: {_COMMONS}")

    record: Dict[int, CapacityMarketYear] = {}
    for row in entries:
        year = row["delivery_year"]
        record[year] = CapacityMarketYear(
            delivery_year=year,
            t4_gbp_per_kw_year=row["t4_gbp_per_kw_year"],
            t1_gbp_per_kw_year=row["t1_gbp_per_kw_year"],
            t4_provenance=row["t4_provenance"],
            t1_provenance=row["t1_provenance"],
            note=row.get("note", ""),
            source_label=row.get("source_label", ""),
        )
        for auction, price, prov in (
            ("T-4", row["t4_gbp_per_kw_year"], row["t4_provenance"]),
            ("T-1", row["t1_gbp_per_kw_year"], row["t1_provenance"]),
        ):
            if price is not None and prov not in _ACCEPTED_PROVENANCE:
                raise ValueError(
                    f"CM commons serves a {auction} price for delivery year {year} under "
                    f"provenance {prov!r}, which is not one this module reads. A figure nobody "
                    "fetched must not be served as the published record."
                )
    if not record:
        raise ValueError(f"CM auction commons produced no rows: {_COMMONS}")
    return record


_RECORD: Dict[int, CapacityMarketYear] = _load()

_PARTICIPATION = json.loads(_COMMONS.read_text())["participation_rules"]

#: The smallest unit that can prequalify for a CM auction, in kW. Reduced from 2 MW; a unit below
#: this cannot hold an agreement in its own right and can only be aggregated into one that can.
#: Origin: cited -- Electricity Capacity (Amendment) Regulations 2020 explanatory note, carried in
#: the commons artefact above.
MINIMUM_CMU_CAPACITY_KW: float = float(_PARTICIPATION["minimum_cmu_capacity_kw"])

FIRST_DELIVERY_YEAR = min(_RECORD)

#: The delivery year a caller gets when it does not name one: the latest with an ESTABLISHED T-4
#: inside the 2016-2025 run window. Not the highest and not the average -- the T-1 for DY 2022/23
#: is 11.6x the T-3 for the same year, so "a" CM price is a question about which auction and which
#: year, and defaulting to either extreme would bias every figure downstream.
LATEST_ESTABLISHED_T4_DELIVERY_YEAR = 2024

#: Why the domestic leg refuses. Written to be PRINTED, not just raised: a refusal that names its
#: reason is how the refusal itself gets found to be wrong.
DOMESTIC_PARTICIPATION_REFUSAL = (
    "a GB domestic household cannot hold a Capacity Market agreement: whole-house flexible load "
    f"is single-digit kW against a {MINIMUM_CMU_CAPACITY_KW:,.0f} kW minimum CMU, so ~80 "
    "households are needed to reach the smallest unit that can prequalify. A household reaches "
    "the CM only inside an aggregator's DSR CMU, and no publication states what an aggregator "
    "passes through to a member -- those terms are bilateral. The published clearing prices do "
    "not on their own support a per-household revenue figure."
)


def delivery_year(delivery_year_start: int) -> Optional[CapacityMarketYear]:
    """The published row, or `None` for a delivery year outside the record."""
    return _RECORD.get(delivery_year_start)


def clearing_price_gbp_per_kw_year(
    delivery_year_start: int, auction: str
) -> Optional[float]:
    """The published clearing price for one auction and one DELIVERY year, or `None`.

    `auction` must be `'T-4'` or `'T-1'`. There is deliberately no default: the two auctions for
    one delivery year differed by 11.6x in DY 2022/23, so a caller that has not decided which one
    it means has not decided what it is computing.

    `None` is NOT zero. It means the auction did not run for that delivery year, or that two
    sources disagree and this pass did not reconcile them, or that the year is outside the
    record -- `delivery_year(y).note` says which.

    THE PRICE IS PER kW OF DE-RATED CAPACITY UNDER AN AWARDED AGREEMENT. Multiplying it by a
    rated power, or by a capacity with no agreement, is not a smaller version of the right
    answer; see `derating_factor` and `DOMESTIC_PARTICIPATION_REFUSAL`.
    """
    row = _RECORD.get(delivery_year_start)
    return row.price(auction) if row else None


def derating_factor(technology_class: str) -> Optional[float]:
    """The published de-rating factor for a technology class -- `None` for every class today.

    AN HONEST GAP, AND IT IS LOAD-BEARING. The CM pays on de-rated capacity; de-rating factors
    are published per auction and per technology class and are duration-dependent for DSR and
    storage. This pass did not fetch them, so there is no factor here to apply and no plausible
    stand-in either. A caller that needs one must fetch the publication and add it to the commons
    artefact, NOT pick a number: a de-rating factor invented to fill this slot would be
    indistinguishable, one week later, from a published one.

    Returning `None` for every argument makes this a refusal rather than a lookup, and the
    argument is kept so that the shape of the fix is obvious to whoever does fetch them.
    """
    return None


def household_revenue_gbp_pa(flex_kw: float) -> Optional[float]:
    """CM revenue for one domestic household: `None`, always, with a named reason.

    This is a REFUSAL, not an unimplemented lookup, and it is the substantive result of the
    2026-09-07 pass rather than a gap in it. See `DOMESTIC_PARTICIPATION_REFUSAL`.

    `flex_kw` is accepted and ignored on purpose: the refusal does not depend on how much flex
    the household has, because no domestic quantity reaches the 1 MW threshold, and a signature
    that took no argument would invite a caller to believe some other function took one.
    """
    return None


def households_per_minimum_cmu(flex_kw: float) -> Optional[float]:
    """How many households of this flex it takes to reach the smallest prequalifying CMU.

    The refusal's arithmetic, exposed so it can be checked and so a surface can print the reason
    with a number in it. `None` for a non-positive flex, which is not a household.
    """
    if flex_kw <= 0:
        return None
    return round(MINIMUM_CMU_CAPACITY_KW / flex_kw, 1)
