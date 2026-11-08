"""Smart home product bundle and ancillary revenue tracker."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class AncillaryProduct(str, Enum):
    BOILER_COVER = 'boiler_cover'
    EV_TARIFF = 'ev_tariff'
    SMART_HOME_CONTROLS = 'smart_home_controls'
    HOME_INSURANCE = 'home_insurance'
    BROADBAND = 'broadband'
    CARBON_OFFSET = 'carbon_offset'
    SOLAR_MONITORING = 'solar_monitoring'


_MONTHLY_REVENUE_GBP = {
    AncillaryProduct.BOILER_COVER: 18.0,
    AncillaryProduct.EV_TARIFF: 0.0,
    AncillaryProduct.SMART_HOME_CONTROLS: 5.0,
    AncillaryProduct.HOME_INSURANCE: 32.0,
    AncillaryProduct.BROADBAND: 28.0,
    AncillaryProduct.CARBON_OFFSET: 3.0,
    AncillaryProduct.SOLAR_MONITORING: 4.0,
}


@dataclass
class ProductSubscription:
    customer_id: str
    product: AncillaryProduct
    start_date: dt.date
    end_date: Optional[dt.date] = None
    monthly_price_gbp: Optional[float] = None

    def __post_init__(self) -> None:
        if self.monthly_price_gbp is None:
            self.monthly_price_gbp = _MONTHLY_REVENUE_GBP[self.product]

    @property
    def is_active(self) -> bool:
        return self.end_date is None

    def annual_revenue_gbp(self, year: int) -> float:
        start = dt.date(year, 1, 1)
        end = dt.date(year, 12, 31)
        eff_start = max(self.start_date, start)
        eff_end = min(self.end_date or end, end)
        if eff_start > eff_end:
            return 0.0
        months = round((eff_end - eff_start).days / 30.4375, 1)
        return round(self.monthly_price_gbp * months, 2)


class AncillaryRevenueTracker:
    def __init__(self) -> None:
        self._subscriptions: List[ProductSubscription] = []

    def subscribe(self, customer_id: str, product: AncillaryProduct,
                   start_date: dt.date, monthly_price_gbp: Optional[float] = None
                   ) -> ProductSubscription:
        sub = ProductSubscription(customer_id=customer_id, product=product,
                                   start_date=start_date, monthly_price_gbp=monthly_price_gbp)
        self._subscriptions.append(sub)
        return sub

    def cancel(self, customer_id: str, product: AncillaryProduct,
                cancel_date: dt.date) -> None:
        for s in self._subscriptions:
            if s.customer_id == customer_id and s.product == product and s.is_active:
                s.end_date = cancel_date
                return

    def active_subscriptions(self, customer_id: str) -> List[ProductSubscription]:
        return [s for s in self._subscriptions
                if s.customer_id == customer_id and s.is_active]

    def products_per_customer(self, customer_id: str) -> int:
        return len(self.active_subscriptions(customer_id))

    def total_annual_revenue_gbp(self, year: int) -> float:
        return round(sum(s.annual_revenue_gbp(year) for s in self._subscriptions), 2)

    def revenue_by_product(self, year: int) -> Dict[str, float]:
        result: Dict[str, float] = {}
        for s in self._subscriptions:
            k = s.product.value
            result[k] = round(result.get(k, 0.0) + s.annual_revenue_gbp(year), 2)
        return result

    def avg_products_per_customer(self) -> Optional[float]:
        customers = set(s.customer_id for s in self._subscriptions if s.is_active)
        if not customers:
            return None
        active_count = {cid: self.products_per_customer(cid) for cid in customers}
        return round(sum(active_count.values()) / len(customers), 2)

    def portfolio_summary(self, year: int) -> dict:
        active_subs = [s for s in self._subscriptions if s.is_active]
        customers = set(s.customer_id for s in active_subs)
        return {
            'year': year,
            'total_active_subscriptions': len(active_subs),
            'unique_customers': len(customers),
            'avg_products_per_customer': self.avg_products_per_customer(),
            'total_annual_revenue_gbp': self.total_annual_revenue_gbp(year),
            'by_product': self.revenue_by_product(year),
        }
