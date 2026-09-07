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

A HOUSEHOLD CANNOT HOLD A CM AGREEMENT IN ITS OWN RIGHT, and that half of the refusal survives:
the minimum Capacity Market Unit is 1 MW, and the smallest awarded DSR CMU anywhere in the run
window has a connection capacity of exactly 1.0000 MW, so the threshold binds in practice.

BUT THE OTHER HALF WAS REFUTED BY THE PUBLISHER'S OWN REGISTER (2026-09-07, third pass). This
docstring used to go on: a household reaches the CM only inside an aggregator's DSR CMU, therefore
~80 households per unit, therefore the domestic leg refuses. The Capacity Market Register itself
carries awarded DSR CMUs described by their own operators as "domestic demand turn down" and
"aggregated components less than 30KW", from delivery year 2023 -- 633.5 MW of de-rated capacity by
DY2025 across eight named GB operators including Octopus Energy. Domestic aggregation is not a
hypothetical route; it is an observed and growing one, and a real supplier could read it.

TWO CONSEQUENCES, and the second is the uncomfortable one:

  * **The refusal now stands on ONE ground, not two.** What an aggregator passes through to a
    member household is stated by no publication -- the register publishes capacities and
    component counts, never a payment. That is the whole of it. `DOMESTIC_PARTICIPATION_REFUSAL`
    says so and no longer says the household cannot get there.
  * **The "~80 households" figure was the rated-vs-delivered error, inside the sentence that
    names it.** It is 1,000 kW over a 12.4 kW whole-house RATED flex. The register publishes what
    a domestic component actually contributes to an awarded CMU: 1.1655 kW capacity-weighted, so
    ~858 households. 10.7x, from dividing by rated capacity where the publisher gives contracted
    capacity -- which is the exact defect `derating_factor` was fetched to end, arriving inside
    the refusal that was written to end it. NESO's DFS record agrees independently: 91% of
    domestic delivery is below 1 kW.

`HOUSEHOLDS_PER_MINIMUM_CMU_OBSERVED` carries the register's figure. `households_per_minimum_cmu`
still divides by whatever flex a caller hands it, and its docstring now says which of the two a
caller is asking for.

DE-RATING WAS A NAMED GAP AND IS NOW FILLED FROM THE PUBLISHER (2026-09-07, second pass). The CM
pays on DE-RATED capacity. `derating_factor()` used to return `None` for every class because no
factor had been fetched; the whole published register is now in the commons artefact and it
serves real numbers. Three things that pass learned, each of which can bite a caller:

  * **The factor is keyed to the AUCTION ROUND, not the delivery year.** A T-N auction for
    delivery year Y and the T-1 for delivery year Y-N+1 are one round against one Electricity
    Capacity Report, and carry the IDENTICAL factor -- so T-4[Y] == T-1[Y-3], and the substituted
    T-3[2022] == T-1[2020]. Reading a factor off a delivery year without naming an auction
    reproduces exactly the offset that made `capacity_market.py` the third disagreeing home for
    the price. So `derating_factor` takes an auction and there is no default, for the same reason
    `clearing_price...` has none. (The offset is N-1, not N: a T-4 held in February of year H
    delivers from October H+3. This pass first wrote N and its own control refuted it.)
  * **DSR is NOT duration-split.** One DSR factor per auction; only `Storage` carries duration
    classes. This module's own v1 docstring said de-rating was "duration-dependent for DSR and
    storage", and the publisher's register says that is true of storage alone.
  * **DY 2022/23's T-4 field holds a T-3 price, and the T-3 has a DIFFERENT factor** (0.8614
    against the suspended T-4's 0.8428). Asking for "the T-4 price" and "the T-4 factor" for that
    year would take the price from one auction and the factor from another, silently. That is why
    `derated_price_gbp_per_kw_year` exists: it resolves both through `auction_actually_held`, so
    a price and a factor cannot come from two different auctions.

THE PRIMARY REGISTER WAS REACHED, and it moved two figures nobody was contesting. `emrdeliverybody
.com` returns 404, not the 403 the v1 pass recorded -- the host is retired, not blocking, and the
register lives on the NESO data portal. It settled the two contested years (DY 2023/24 T-1 =
GBP60.00, DY 2025/26 T-4 = GBP30.59) and ALSO corrected DY 2021/22's T-1 from GBP60.00 to
GBP45.00, which was not flagged as contested at all: the two figures had been TRANSPOSED between
two delivery years by one secondary source, and a transposition damages two entries while a
contest flag marks one. See the artefact's `what_the_primary_pass_changed`.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

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
    t4_auction_actually_held: str = "T-4"
    """Which auction the T-4 FIELD's price actually came from. 'T-3' for delivery year 2022/23,
    whose T-4 was suspended and replaced. Load-bearing for de-rating, not a footnote: the two
    auctions carry different published factors, so a caller pairing this year's T-4 price with the
    T-4 de-rating factor would be crossing two auctions."""

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
            t4_auction_actually_held=row.get("t4_auction_actually_held", "T-4"),
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


def _load_derating() -> Dict[Tuple[int, str], Dict[str, float]]:
    """`{(delivery_year, auction): {technology_class: factor}}` from the same commons artefact.

    NO FAIL-OPEN PATH, for the same reason as `_load`. A missing de-rating block RAISES rather
    than degrading to "no de-rating", because "no de-rating" is arithmetically identical to a
    factor of 1.0 and that is the exact overstatement this block was fetched to end.
    """
    raw = json.loads(_COMMONS.read_text())
    block = raw.get("derating_factors")
    if not block or not block.get("register"):
        raise ValueError(
            f"CM commons carries no de-rating register: {_COMMONS}. The CM pays on de-rated "
            "capacity; an absent factor is not a factor of 1.0."
        )
    table: Dict[Tuple[int, str], Dict[str, float]] = {}
    for entry in block["register"]:
        table[(entry["delivery_year"], entry["auction"])] = dict(entry["factors"])
    return table


_RECORD: Dict[int, CapacityMarketYear] = _load()
_DERATING: Dict[Tuple[int, str], Dict[str, float]] = _load_derating()

_PARTICIPATION = json.loads(_COMMONS.read_text())["participation_rules"]

#: The technology class an aggregated demand-side response CMU falls in. Named rather than
#: inlined at each call site so that the I&C leg and any future caller cannot drift apart on it,
#: and so a grep for the class finds every consumer.
DSR_TECHNOLOGY_CLASS = "DSR"

#: The smallest unit that can prequalify for a CM auction, in kW. Reduced from 2 MW; a unit below
#: this cannot hold an agreement in its own right and can only be aggregated into one that can.
#: Origin: cited -- Electricity Capacity (Amendment) Regulations 2020 explanatory note, carried in
#: the commons artefact above.
MINIMUM_CMU_CAPACITY_KW: float = float(_PARTICIPATION["minimum_cmu_capacity_kw"])

FIRST_DELIVERY_YEAR = min(_RECORD)

#: The last delivery year inside the 2016-2025 run window, so a caller cannot reach the
#: 2026-2029 rows this artefact carries for diagnostic reasons and read them as history.
RUN_WINDOW_LAST_DELIVERY_YEAR = 2025

#: The latest delivery year with an ESTABLISHED T-4 inside the run window. Not the highest and not
#: the average -- the T-1 for DY 2022/23 is 11.6x the T-3 for the same year, so "a" CM price is a
#: question about which auction and which year, and defaulting to either extreme would bias every
#: figure downstream.
#:
#: DERIVED, NOT PINNED, and it moved the day it was first read. This was the literal `2024` until
#: the primary pass settled DY 2025/26's contested T-4 at GBP30.59, at which point the literal was
#: silently one year stale and nothing could have noticed: a constant keyed to today's answer goes
#: wrong precisely when the record gets BETTER. Computing it means filling a contested year is all
#: it takes to move it.
LATEST_ESTABLISHED_T4_DELIVERY_YEAR = max(
    year for year, row in _RECORD.items()
    if year <= RUN_WINDOW_LAST_DELIVERY_YEAR and row.established("T-4")
)

_SHAPE = json.loads(_COMMONS.read_text())["dsr_cmu_shape"]["measured"]

#: What a domestic component actually contributes to an awarded DSR CMU, capacity-weighted over
#: every domestic-shaped awarded CMU-year in the run window. Origin: observed -- the publisher's
#: own Capacity Market Register, joined CMU-to-Component, carried in the commons artefact above.
#:
#: THIS IS A CONTRACTED CAPACITY, NOT A RATED ONE, and that is the whole point of it. A whole
#: flexible house in `flexibility_potential` is 3.0-15.4 kW of rated asset power; what an
#: aggregator actually puts into a CMU per component is 1.17 kW.
OBSERVED_DOMESTIC_COMPONENT_KW: float = float(_SHAPE["observed_component_scale_kw"])

#: How many domestic components an awarded CMU actually takes, at the scale the register
#: publishes. Replaces the "~80" the refusal used to assert, which divided by rated flex.
HOUSEHOLDS_PER_MINIMUM_CMU_OBSERVED: float = float(_SHAPE["households_per_minimum_cmu_observed"])

#: The first delivery year in which an awarded DSR CMU in the register describes itself as
#: domestic. Before this year the refusal's participation claim was not refutable from the
#: register; from it, the register refutes it.
DOMESTIC_AGGREGATION_FIRST_OBSERVED_DELIVERY_YEAR: int = min(
    row["delivery_year"] for row in _SHAPE["by_delivery_year"])

#: Why the domestic leg refuses. Written to be PRINTED, not just raised: a refusal that names its
#: reason is how the refusal itself gets found to be wrong -- and this one WAS, on this sentence's
#: second reading. It used to carry two grounds and the arithmetic one did not survive contact
#: with the publisher's register. What is left is narrower, and true.
DOMESTIC_PARTICIPATION_REFUSAL = (
    "a GB domestic household cannot hold a Capacity Market agreement in its own right -- the "
    f"minimum CMU is {MINIMUM_CMU_CAPACITY_KW:,.0f} kW and the smallest awarded DSR CMU in the "
    "record sits at exactly that. It CAN reach the Capacity Market inside an aggregator's DSR "
    "CMU, and the register shows that happening from delivery year "
    f"{DOMESTIC_AGGREGATION_FIRST_OBSERVED_DELIVERY_YEAR}: awarded units built from tens of "
    f"thousands of components averaging {OBSERVED_DOMESTIC_COMPONENT_KW:.2f} kW, under operators "
    "including domestic suppliers. What no publication states is what an aggregator PASSES "
    "THROUGH to a member household -- those terms are bilateral. That, and only that, is why "
    "there is no per-household revenue figure here: not that the household cannot get there, but "
    "that nobody publishes what it is paid when it does."
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


def auction_actually_held(delivery_year_start: int, auction: str) -> Optional[str]:
    """Which auction a caller asking for `auction` in this delivery year is really asking about.

    Answers `auction` itself for every year but one: DY 2022/23's T-4 was suspended and replaced
    by a T-3, so `('T-4', 2022)` resolves to `'T-3'`. `None` for a year outside the record.

    This exists because the substitution is INVISIBLE at the price alone. The T-3's price sits in
    the row's `t4` field, so `clearing_price_gbp_per_kw_year(2022, 'T-4')` returns a T-3 number
    and nothing about that number says so. The de-rating factors are published per auction and
    the two disagree (T-3 0.8614, suspended T-4 0.8428), so a caller that took the price from the
    field and the factor from the label would combine two auctions and get an answer that is not
    wrong by a little.
    """
    row = _RECORD.get(delivery_year_start)
    if row is None:
        return None
    if auction == "T-4":
        return row.t4_auction_actually_held
    if auction == "T-1":
        return "T-1"
    raise ValueError(
        f"unknown auction {auction!r}: the GB Capacity Market runs 'T-4' and 'T-1', and asking "
        "for 'the' CM auction without naming one is the conflation this module exists to prevent"
    )


def derating_factor(
    technology_class: str, delivery_year_start: int, auction: str
) -> Optional[float]:
    """The published de-rating factor for one technology class in one auction, or `None`.

    THE FACTOR BELONGS TO AN AUCTION ROUND, NOT A DELIVERY YEAR, so all three arguments are
    required and none has a default. The T-4 for delivery year Y and the T-1 for delivery year
    Y-4 are the same round and carry the identical factor; a signature that let a caller pass a
    year alone would be the four-year offset that made `capacity_market.py` a third disagreeing
    home for the clearing price, arriving again by a different door.

    `None` means the register has no factor for that class in that auction -- a class the
    publisher did not list, or a delivery year outside the record. It is NOT 1.0, and a caller
    that treats it as 1.0 has reinstated the whole overstatement this function was written to
    end. `DSR_TECHNOLOGY_CLASS` is the class an aggregated I&C demand-response CMU falls in, and
    it is not duration-split: only `Storage` is.
    """
    held = auction_actually_held(delivery_year_start, auction)
    if held is None:
        return None
    return _DERATING.get((delivery_year_start, held), {}).get(technology_class)


def derated_price_gbp_per_kw_year(
    delivery_year_start: int, auction: str, technology_class: str
) -> Optional[float]:
    """Revenue per kW of RATED capacity: the clearing price times the de-rating factor.

    THE ONLY SAFE WAY TO SPEND THIS MODULE'S PRICE, and the reason it exists rather than leaving
    callers to multiply. The price and the factor are resolved through the SAME
    `auction_actually_held`, so they cannot come from two different auctions -- which is a live
    hazard exactly once, at DY 2022/23, and would be silent if it happened.

    Returns GBP per kW per year of rated capacity, so a caller may multiply by a site's rated
    flex directly. `None` if either the price or the factor is unestablished, and NOT a partial
    answer using whichever one was found: a price with no factor is the overstatement, and a
    factor with no price is nothing at all.

    An awarded agreement is still assumed by the caller. This function prices capacity that WON;
    it says nothing about whether a given unit did, and `DOMESTIC_PARTICIPATION_REFUSAL` covers
    the population that cannot even bid.
    """
    price = clearing_price_gbp_per_kw_year(delivery_year_start, auction)
    factor = derating_factor(technology_class, delivery_year_start, auction)
    if price is None or factor is None:
        return None
    return round(price * factor, 4)


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

    ASK WHICH FLEX YOU MEAN BEFORE YOU READ THE ANSWER. Handed a household's RATED asset power
    (3.0-15.4 kW here) this returns ~65-333, and that is the arithmetic the old refusal published
    as "~80". Handed what an aggregator actually contracts per component, it returns ~858 --
    `HOUSEHOLDS_PER_MINIMUM_CMU_OBSERVED`, which is what the register says happens. The function
    is right either way; the question it answers is not the same question, and the difference is
    10.7x. Prefer the observed constant for any published figure.

    `None` for a non-positive flex, which is not a household.
    """
    if flex_kw <= 0:
        return None
    return round(MINIMUM_CMU_CAPACITY_KW / flex_kw, 1)
