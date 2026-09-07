"""Demand Flexibility Potential Assessor -- Phase AA.

Screens the customer portfolio for demand flexibility potential.
Given company-observable asset data (EV flag, ASHP flag, battery flag),
estimates each customer's flexibility capacity (kW) and potential DSR
revenue if enrolled.

Real UK context: NESO Demand Flexibility Service (DFS) launched Oct 2022. Its rate is NOT a
constant and is not carried here -- `dfs_published_record` holds the published per-winter record and
is the single home for it. The realised rate was £3,316/MWh in 2022/23 under a guaranteed acceptance
price and £241/MWh in 2024/25 once the service had to compete.

THE CAPACITY MARKET LEG IS REFUSED FOR A HOUSEHOLD, and that refusal replaces a £930/household/year
figure. This docstring used to say "Capacity Market participants earn ~£75/kW/yr for committed
flexibility", and `_CAPACITY_MARKET_GBP_PER_KW_YR = 75.0  # T-4 auction 2023` applied it to a
household's RATED asset power. The £75 is real -- it is the **T-1** clearing price for **delivery
year 2022/23**, which cleared at the price cap -- but it is not a T-4, not 2023, not an annual rate
anybody earns for "committed flexibility", and above all not something a household can be paid,
because the minimum Capacity Market Unit is 1 MW and a whole flexible house here is 3.0-15.4 kW.
`capacity_market_published_record` holds the auction record and the refusal's reason.
DNO flexibility auctions (Flex Markets) pay £50-300/MWh depending on location.

All inputs company-observable (asset flags from CRM, kwh from billing).
Epistemic-compliant.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from company.market import capacity_market_published_record, dfs_published_record

# UK calibrated flexibility estimates per asset type
_EV_FLEX_KW = 7.4  # typical 7.4 kW home charger (32A)
_ASHP_FLEX_KW = 3.0  # air source heat pump space heating load
_BATTERY_FLEX_KW = 5.0  # typical 5 kWh/h battery discharge rate
_BATTERY_FLEX_HOURS = 1.5  # usable discharge window (evening peak)

# DSR revenue benchmarks. Neither the DFS rate nor the CM clearing price is here: they are
# published per winter and per delivery year and live in `dfs_published_record` and
# `capacity_market_published_record`. Two copies of one fact is how this book carried a DFS rate
# that was 737x low for three months; THREE copies is how it carried a CM price under two wrong
# labels at once, and neither duplicate gate could see it, because the three homes disagreed about
# the NAME as well as the value.
_DISPATCH_DURATION_HRS = 1.0  # 1-hour events standard


class FlexibilityAssetType(str, Enum):
    EV = "ev"
    ASHP = "ashp"
    BATTERY = "battery"
    EV_AND_BATTERY = "ev_and_battery"


@dataclass(frozen=True)
class FlexibilityEstimate:
    """Flexibility potential for one customer.

    flex_kw: peak demand reduction achievable
    flex_kwh_per_event: energy shifted per dispatch event
    dfs_revenue_gbp_pa: estimated NESO DFS revenue if enrolled
    capacity_market_revenue_gbp_pa: `None`, always -- a household holds no CM agreement
    """
    account_id: str
    asset_type: FlexibilityAssetType
    has_ev: bool
    has_ashp: bool
    has_battery: bool
    flex_kw: float
    flex_kwh_per_event: float
    dfs_revenue_gbp_pa: float
    capacity_market_revenue_gbp_pa: Optional[float]
    dfs_established: bool = True
    """False means the winter is not in the published record, so `dfs_revenue_gbp_pa` is 0.0 for
    want of evidence and NOT because the service paid nothing. 2023/24 is the live case."""
    capacity_market_refusal_reason: Optional[str] = (
        capacity_market_published_record.DOMESTIC_PARTICIPATION_REFUSAL)
    """Why `capacity_market_revenue_gbp_pa` is `None`. A refusal that names its reason is how the
    refusal itself gets found to be wrong, so this is carried to any surface that prints the row
    rather than left as a bare absent value."""

    @property
    def total_annual_revenue_gbp(self) -> float:
        """DFS only, because the CM leg is a refusal.

        THE TWO ZEROS HERE MEAN OPPOSITE THINGS and the flags beside them are what tell them
        apart. A `dfs_revenue_gbp_pa` of 0.0 with `dfs_established=False` means the service ran
        and we cannot say what it paid. The CM leg contributes nothing because a household holds
        no agreement to be paid under -- a structural zero, established rather than unknown.
        """
        cm = self.capacity_market_revenue_gbp_pa or 0.0
        return round(self.dfs_revenue_gbp_pa + cm, 2)

    @property
    def is_dfs_eligible(self) -> bool:
        """Minimum 1 kW and smart meter required (observable via has_ev/battery)."""
        return self.flex_kw >= 1.0

    @property
    def flex_mwh_per_event(self) -> float:
        return round(self.flex_kwh_per_event / 1000.0, 4)


def _classify_asset(has_ev: bool, has_ashp: bool, has_battery: bool) -> FlexibilityAssetType:
    if has_ev and has_battery:
        return FlexibilityAssetType.EV_AND_BATTERY
    if has_ev:
        return FlexibilityAssetType.EV
    if has_battery:
        return FlexibilityAssetType.BATTERY
    return FlexibilityAssetType.ASHP


def _estimate_flex_kw(has_ev: bool, has_ashp: bool, has_battery: bool) -> float:
    total = 0.0
    if has_ev:
        total += _EV_FLEX_KW
    if has_ashp:
        total += _ASHP_FLEX_KW
    if has_battery:
        total += _BATTERY_FLEX_KW
    return round(total, 2)


def _estimate_dfs_revenue(flex_kw: float, winter_start_year: int) -> Optional[float]:
    """DFS revenue for one winter, or None where the published record does not establish it.

    Anchored on what DFS paid PER REGISTERED PARTICIPANT and weighted by this customer's flex against
    the published domestic delivery size -- not on rated asset power at every event. The previous
    form credited a 7.4 kW charger with 7.4 kWh of turn-down 20 times a year; NESO's record says 91%
    of domestic delivery is below 1 kW, and that at best 22.4% of registrants show up to any event.
    """
    return dfs_published_record.revenue_gbp_for_flex_kw(flex_kw, winter_start_year)


def _estimate_capacity_revenue(flex_kw: float) -> Optional[float]:
    """CM revenue for one domestic household: `None`, always, with a reason on the record.

    NOT an unimplemented lookup. A household cannot hold a Capacity Market agreement -- the
    minimum CMU is 1 MW against a whole flexible house of 3.0-15.4 kW, so it takes ~80 of them to
    reach the smallest unit that can prequalify, and what an aggregator passes through to a member
    is bilateral and unpublished. The previous form returned `flex_kw * 75.0`, which credited an
    EV-and-battery household with £930/year of availability payments for an agreement it never
    won, at a price that was a capped T-1 result for delivery year 2022/23 rather than the "T-4
    auction 2023" its comment named.
    """
    return capacity_market_published_record.household_revenue_gbp_pa(flex_kw)


class FlexibilityPotentialBook:
    """Screens portfolio customers for demand flexibility potential.

    Usage::
        book = FlexibilityPotentialBook()
        estimate = book.assess(
            account_id="C1",
            has_ev=True, has_ashp=False, has_battery=True,
        )
    """

    def __init__(self) -> None:
        self._estimates: list[FlexibilityEstimate] = []

    def assess(
        self,
        account_id: str,
        has_ev: bool = False,
        has_ashp: bool = False,
        has_battery: bool = False,
        winter_start_year: int = dfs_published_record.LATEST_ESTABLISHED_WINTER,
    ) -> Optional[FlexibilityEstimate]:
        """Assess one customer's flexibility potential.

        Returns None if customer has no flexible assets.
        """
        if not (has_ev or has_ashp or has_battery):
            return None

        flex_kw = _estimate_flex_kw(has_ev, has_ashp, has_battery)
        flex_kwh = flex_kw * _DISPATCH_DURATION_HRS
        dfs = _estimate_dfs_revenue(flex_kw, winter_start_year)
        estimate = FlexibilityEstimate(
            account_id=account_id,
            asset_type=_classify_asset(has_ev, has_ashp, has_battery),
            has_ev=has_ev,
            has_ashp=has_ashp,
            has_battery=has_battery,
            flex_kw=flex_kw,
            flex_kwh_per_event=flex_kwh,
            dfs_revenue_gbp_pa=(dfs or 0.0),
            dfs_established=(dfs is not None),
            capacity_market_revenue_gbp_pa=_estimate_capacity_revenue(flex_kw),
        )
        self._estimates.append(estimate)
        return estimate

    @property
    def all_estimates(self) -> list[FlexibilityEstimate]:
        return list(self._estimates)

    def dfs_eligible(self) -> list[FlexibilityEstimate]:
        return [e for e in self._estimates if e.is_dfs_eligible]

    def top_by_flex_kw(self, n: int = 5) -> list[FlexibilityEstimate]:
        return sorted(self._estimates, key=lambda e: e.flex_kw, reverse=True)[:n]

    @property
    def total_portfolio_flex_kw(self) -> float:
        return round(sum(e.flex_kw for e in self._estimates), 2)

    @property
    def total_portfolio_revenue_gbp_pa(self) -> float:
        return round(sum(e.total_annual_revenue_gbp for e in self._estimates), 2)

    def by_asset_type(self, asset_type: FlexibilityAssetType) -> list[FlexibilityEstimate]:
        return [e for e in self._estimates if e.asset_type == asset_type]

    def flexibility_summary(self) -> dict:
        eligible = self.dfs_eligible()
        return {
            "customers_assessed": len(self._estimates),
            "dfs_eligible_count": len(eligible),
            "total_flex_kw": self.total_portfolio_flex_kw,
            "total_annual_revenue_gbp": self.total_portfolio_revenue_gbp_pa,
            "ev_customers": len(self.by_asset_type(FlexibilityAssetType.EV)),
            "battery_customers": len(self.by_asset_type(FlexibilityAssetType.BATTERY)),
            "ev_and_battery_customers": len(self.by_asset_type(FlexibilityAssetType.EV_AND_BATTERY)),
        }
