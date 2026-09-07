"""Demand Flexibility Potential Assessor -- Phase AA.

Screens the customer portfolio for demand flexibility potential.
Given company-observable asset data (EV flag, ASHP flag, battery flag),
estimates each customer's flexibility capacity (kW) and potential DSR
revenue if enrolled.

Real UK context: NESO Demand Flexibility Service (DFS) launched Oct 2022. Its rate is NOT a
constant and is not carried here -- `dfs_published_record` holds the published per-winter record and
is the single home for it. The realised rate was £3,316/MWh in 2022/23 under a guaranteed acceptance
price and £241/MWh in 2024/25 once the service had to compete.
Capacity Market participants earn ~£75/kW/yr for committed flexibility.
DNO flexibility auctions (Flex Markets) pay £50-300/MWh depending on location.

All inputs company-observable (asset flags from CRM, kwh from billing).
Epistemic-compliant.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from company.market import dfs_published_record


# UK calibrated flexibility estimates per asset type
_EV_FLEX_KW = 7.4  # typical 7.4 kW home charger (32A)
_ASHP_FLEX_KW = 3.0  # air source heat pump space heating load
_BATTERY_FLEX_KW = 5.0  # typical 5 kWh/h battery discharge rate
_BATTERY_FLEX_HOURS = 1.5  # usable discharge window (evening peak)

# DSR revenue benchmarks (£/kW/yr). The DFS rate and event count are NOT here: they are published
# per winter and live in `dfs_published_record`, because two copies of one fact is how this book
# carried a rate that was 737x low for three months without anything able to notice.
_CAPACITY_MARKET_GBP_PER_KW_YR = 75.0  # T-4 auction 2023
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
    capacity_market_revenue_gbp_pa: capacity market value if contracted
    """
    account_id: str
    asset_type: FlexibilityAssetType
    has_ev: bool
    has_ashp: bool
    has_battery: bool
    flex_kw: float
    flex_kwh_per_event: float
    dfs_revenue_gbp_pa: float
    capacity_market_revenue_gbp_pa: float
    dfs_established: bool = True
    """False means the winter is not in the published record, so `dfs_revenue_gbp_pa` is 0.0 for
    want of evidence and NOT because the service paid nothing. 2023/24 is the live case."""

    @property
    def total_annual_revenue_gbp(self) -> float:
        return round(self.dfs_revenue_gbp_pa + self.capacity_market_revenue_gbp_pa, 2)

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


def _estimate_capacity_revenue(flex_kw: float) -> float:
    return round(flex_kw * _CAPACITY_MARKET_GBP_PER_KW_YR, 2)


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
        estimate = FlexibilityEstimate(
            account_id=account_id,
            asset_type=_classify_asset(has_ev, has_ashp, has_battery),
            has_ev=has_ev,
            has_ashp=has_ashp,
            has_battery=has_battery,
            flex_kw=flex_kw,
            flex_kwh_per_event=flex_kwh,
            dfs_revenue_gbp_pa=(_estimate_dfs_revenue(flex_kw, winter_start_year) or 0.0),
            dfs_established=(
                _estimate_dfs_revenue(flex_kw, winter_start_year) is not None),
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
