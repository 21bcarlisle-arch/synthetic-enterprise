"""I&C Demand Response Enrollment -- Phase NX.

Large I&C customers can sell interruptible load capacity into the UK Capacity
Market (CM) and NESO Demand Flexibility Service (DFS). Unlike residential
customers (who need EV/ASHP/battery), I&C participants sell process
flexibility (chillers, compressors, HVAC curtailment, interruptible loads).

Eligibility: I&C customers with EAC >= _IC_MIN_EAC_KWH participate via DSR
aggregators who pool sub-threshold loads into CM-eligible units. The minimum Capacity Market Unit
is 1 MW (reduced from 2 MW), and a typical site here is ~35 kW of flex, so aggregation is not an
optimisation but the only route. Aggregators charge a commission (_AGGREGATOR_FEE_PCT) on CM/DFS
revenue. This is what distinguishes the I&C leg from the domestic one, where
`flexibility_potential` REFUSES: an I&C site is a real DSR CMU component with half-hourly metering
behind a real aggregator contract, and a household is not.

CM clearing prices are NOT constants here: they are published per delivery year, per auction, and
read from `capacity_market_published_record`. This module used to carry its own
`_CM_DELIVERY_GBP_PER_KW_YR` table, one of THREE homes for one publication that disagreed with each
other by up to 4.7x.

DE-RATING IS NOW APPLIED, and the gap it closed was this module's largest known overstatement. The
CM pays on DE-RATED capacity; this module used to apply the clearing price to raw `flex_kw`, so its
CM leg was overstated by the whole factor. The published DSR factors are now in the commons and
range 0.7145-0.897 across the record, so the leg was running 12-28% high depending on the year --
NOT 100% high, which is what "overstated by the whole de-rating factor" reads like and is not what
it means. The factor is a multiplier, and the overstatement is `1/f - 1`, not `1`.

An aggregated I&C DSR CMU is class `DSR` in the publisher's register, which carries ONE factor per
auction and is not duration-split; only `Storage` is. So this leg needs no duration model, and a
site's flex duration does not change what the CM pays it per kW.

The price and the factor are taken TOGETHER from `derated_price_gbp_per_kw_year`, never separately.
DY 2022/23 is why: its T-4 was suspended and the price in the T-4 field is really a T-3's, whose
published factor differs (0.8614 against 0.8428). Multiplying this module's own price lookup by
this module's own factor lookup would have crossed two auctions there and said nothing about it.
DFS: launched Oct 2022. Its rate and event count are published per winter and read from
`dfs_published_record` -- they are NOT constants, and they are not duplicated here.

Epistemic: company observes I&C EAC from billing records. No SIM internals read.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from company.market import capacity_market_published_record, dfs_published_record

_IC_LOAD_FACTOR = 0.65           # typical industrial load factor (UK)
_IC_DSR_FRACTION = 0.10          # 10% of peak demand enrolled in DSR/CM
_AGGREGATOR_FEE_PCT = 0.20       # aggregator fee on gross CM/DFS revenue
_IC_MIN_EAC_KWH = 200_000        # minimum 200 MWh/yr for DSR aggregator eligibility

_DFS_LAUNCH_YEAR = dfs_published_record.FIRST_WINTER
_DFS_DURATION_HRS = 1.0          # 1-hour events

#: THIS MODULE'S READING of the published auction record, stated so it can be disagreed with.
#:
#: An aggregated DSR CMU is procured in the BULK auction, so this leg prices at T-4 and never at
#: T-1. The two are different auctions for the same delivery year and differed by 11.6x in DY
#: 2022/23; a leg that took "the" CM price would be choosing between them silently.
#:
#: WHAT THE DELETED TABLE GOT WRONG, beyond being one of three homes. Its 2016 (15.0) and 2017
#: (10.0) entries priced T-4 delivery years that did not exist -- no T-4 had begun delivering, and
#: only transitional DSR auctions ran. Its 2025 entry (18.00) repeated 2024's beside it and
#: matched neither of the two figures published for that auction. Its 2018-2024 entries were
#: right, and they are unchanged by this repair: only the three unestablished years move.
_CM_AUCTION_FOR_IC = "T-4"


@dataclass(frozen=True)
class ICFlexibilityRecord:
    """Realized CM/DFS revenue for one I&C customer in one year."""

    customer_id: str
    year: int
    eac_kwh: float
    peak_demand_kw: float
    flex_kw: float
    cm_price_gbp_per_kw: Optional[float]
    cm_derating_factor: Optional[float]
    """The published DSR de-rating factor actually applied. Carried on the record rather than left
    implicit in the revenue, so a reader can see WHICH factor produced the figure beside it and
    can tell a de-rated leg from a rated one without re-deriving the division."""
    gross_cm_revenue_gbp: float
    gross_dfs_revenue_gbp: float
    aggregator_fee_gbp: float
    net_revenue_gbp: float
    dfs_established: bool = True
    """False means the winter is not in the published record, so the DFS leg is 0.0 for want of
    evidence rather than because the service paid nothing. 2023/24 is the live case."""
    cm_established: bool = True
    """False means the published auction record does not establish a de-rated T-4 price for this
    delivery year, so the CM leg is 0.0 for want of evidence and NOT because the auction paid
    nothing. 2016 and 2017 -- no T-4 delivered into either -- are the only live cases since the
    primary pass settled 2025's contested T-4. It is false if EITHER the price or the de-rating
    factor is missing: a price with no factor is the overstatement this leg was repaired to end,
    so half an answer is refused rather than published."""


def _peak_demand_kw(eac_kwh: float) -> float:
    """Estimate peak demand from annual consumption."""
    return eac_kwh / (8760.0 * _IC_LOAD_FACTOR)


def _flex_kw(peak_kw: float) -> float:
    return round(peak_kw * _IC_DSR_FRACTION, 2)


def _cm_price(year: int) -> Optional[float]:
    """The published T-4 clearing price for this delivery year, or `None`.

    NO FALLBACK. The deleted table ended `.get(year, _CM_DELIVERY_GBP_PER_KW_YR[2025])`, so any
    year outside it silently took 2025's value -- and 2025's value was itself unestablished. A
    lookup whose miss returns a neighbouring year's number cannot report that it missed.
    """
    return capacity_market_published_record.clearing_price_gbp_per_kw_year(
        year, _CM_AUCTION_FOR_IC)


def _cm_derating_factor(year: int) -> Optional[float]:
    """The published DSR de-rating factor for the auction this leg prices at, or `None`."""
    return capacity_market_published_record.derating_factor(
        capacity_market_published_record.DSR_TECHNOLOGY_CLASS, year, _CM_AUCTION_FOR_IC)


def _gross_cm_revenue(flex_kw: float, year: int) -> Optional[float]:
    """Gross CM revenue for one aggregated I&C site in one delivery year, DE-RATED.

    `None` where the published record does not establish a T-4 price for the year: 2016 and 2017,
    because no T-4 delivered into either. Callers must not read that as zero for the same reason
    the DFS leg beside it must not. 2025 used to be a third such year and is not any more -- the
    primary register settled its contested T-4 at GBP30.59.

    `flex_kw` is RATED, and that is correct here: `derated_price_gbp_per_kw_year` returns revenue
    per kW of RATED capacity, having already applied the factor. Applying the factor a second time
    at this call site would de-rate twice, which is the mirror-image error of not de-rating at all
    and would be just as quiet.
    """
    derated = capacity_market_published_record.derated_price_gbp_per_kw_year(
        year, _CM_AUCTION_FOR_IC, capacity_market_published_record.DSR_TECHNOLOGY_CLASS)
    if derated is None:
        return None
    return round(flex_kw * derated, 2)


def _gross_dfs_revenue(flex_kw: float, year: int) -> Optional[float]:
    """Gross DFS revenue for one I&C site in one winter, from the published record.

    None where the winter ran but is not established (2023/24) -- distinct from 0.0, which here means
    the service did not exist yet. An I&C site's rated flex is closer to its delivered flex than a
    household's is (56% of I&C delivery is over 10 kW, against 91% of domestic under 1 kW), so this
    keeps the rated-power form and applies only the published delivery shortfall.
    """
    if year < _DFS_LAUNCH_YEAR:
        return 0.0
    row = dfs_published_record.winter(year)
    rate = dfs_published_record.realised_rate_gbp_per_mwh(year)
    events = dfs_published_record.events(year)
    if row is None or rate is None or events is None or row.delivery_fraction_of_committed is None:
        return None
    flex_mw = flex_kw / 1000.0
    return round(
        flex_mw * _DFS_DURATION_HRS * rate * events * row.delivery_fraction_of_committed, 2)


class ICFlexibilityRevenueBook:
    """Computes realized CM/DFS revenue for enrolled I&C customers.

    Usage::

        book = ICFlexibilityRevenueBook()
        book.compute_year(2023, [("C_IC1", 1_998_631), ("C_IC3", 4_007_250)])
        print(book.total_revenue_all_years())
    """

    def __init__(self) -> None:
        self._records: List[ICFlexibilityRecord] = []

    def compute_year(
        self,
        year: int,
        ic_customers: List[tuple],  # list of (customer_id, eac_kwh)
    ) -> Dict[str, float]:
        """Compute net IC flexibility revenue for all eligible customers in one year."""
        revenue_by_cid: Dict[str, float] = {}

        for cid, eac_kwh in ic_customers:
            if eac_kwh < _IC_MIN_EAC_KWH:
                continue

            peak_kw = _peak_demand_kw(eac_kwh)
            fkw = _flex_kw(peak_kw)
            cm_price = _cm_price(year)
            cm_factor = _cm_derating_factor(year)
            cm = _gross_cm_revenue(fkw, year)
            # Same discipline as the DFS leg below: 0.0 keeps the arithmetic running while
            # `cm_established` carries the reason. "No T-4 delivered that year" and "the record
            # has a price but no factor for this class" both land here, and
            # `capacity_market_published_record.delivery_year(y).note` says which -- they lead to
            # different repairs.
            gross_cm = 0.0 if cm is None else cm
            dfs = _gross_dfs_revenue(fkw, year)
            # None means the winter ran and we cannot say what it paid. Booking 0.0 keeps the
            # arithmetic honest about the CM leg while `dfs_established` carries the reason; the two
            # must stay distinguishable, because "DFS paid nothing" and "we have no primary source
            # for 2023/24" lead to opposite decisions.
            gross_dfs = 0.0 if dfs is None else dfs
            agg_fee = round((gross_cm + gross_dfs) * _AGGREGATOR_FEE_PCT, 2)
            net = round(gross_cm + gross_dfs - agg_fee, 2)

            record = ICFlexibilityRecord(
                customer_id=cid,
                year=year,
                eac_kwh=eac_kwh,
                peak_demand_kw=round(peak_kw, 2),
                flex_kw=fkw,
                cm_price_gbp_per_kw=cm_price,
                cm_derating_factor=cm_factor,
                gross_cm_revenue_gbp=gross_cm,
                gross_dfs_revenue_gbp=gross_dfs,
                aggregator_fee_gbp=agg_fee,
                net_revenue_gbp=net,
                dfs_established=(dfs is not None),
                cm_established=(cm is not None),
            )
            self._records.append(record)
            revenue_by_cid[cid] = net

        return revenue_by_cid

    def records_for_year(self, year: int) -> List[ICFlexibilityRecord]:
        return [r for r in self._records if r.year == year]

    def total_revenue_for_year(self, year: int) -> float:
        return round(sum(r.net_revenue_gbp for r in self._records if r.year == year), 2)

    def total_revenue_all_years(self) -> float:
        return round(sum(r.net_revenue_gbp for r in self._records), 2)

    def flexibility_summary(self) -> dict:
        years_with_revenue = sorted({r.year for r in self._records})
        per_year = {}
        for yr in years_with_revenue:
            yr_recs = self.records_for_year(yr)
            per_year[yr] = {
                "total_net_gbp": self.total_revenue_for_year(yr),
                "enrolled_customers": len(yr_recs),
                "total_flex_kw": round(sum(r.flex_kw for r in yr_recs), 2),
            }
        return {
            "total_ic_flex_revenue_gbp": self.total_revenue_all_years(),
            "enrolled_customer_years": len(self._records),
            "years_with_revenue": years_with_revenue,
            "per_year": per_year,
        }
