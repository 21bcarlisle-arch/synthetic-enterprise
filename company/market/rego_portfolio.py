"""REGO (Renewable Energy Guarantee of Origin) procurement and retirement.

UK energy suppliers offering "100% renewable" tariffs must hold REGOs
covering all electricity supplied. REGOs are certificates issued by
Ofgem confirming 1 MWh of electricity from a qualifying renewable source.

REGO pricing:
  - 2016-2020: £0.50-£1.50/MWh (abundant supply, low demand)
  - 2021: £2.00/MWh
  - 2022: £5.00-£8.00/MWh (crisis increased renewable tariff demand)
  - 2023-2025: £3.00-£5.00/MWh (normalising)

REGOs are sourced from UK generators (wind, solar, hydro, biomass).
They must be retired in the same compliance year they are used for claims.
Unretired REGOs expire on 31 March (end of the REGO scheme year).

The company cannot see which customers in the simulation have which
tariffs — it only knows its own REGO procurement and consumption.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


_REGO_PRICE_BY_YEAR: dict[int, float] = {
    2016: 0.80, 2017: 0.85, 2018: 0.90, 2019: 1.00, 2020: 1.20,
    2021: 2.00, 2022: 6.50, 2023: 4.00, 2024: 3.50, 2025: 3.20,
}


@dataclass
class RegoPurchase:
    purchase_id: str
    purchase_date: str
    scheme_year: int            # REGO scheme year (April–March)
    mwh: float
    price_per_mwh: float
    generator: str              # e.g. "Humber Wind Farm", "Scottish Hydro"
    technology: Literal["wind_onshore", "wind_offshore", "solar", "hydro", "biomass"]
    retired: bool = False
    retirement_date: str = ""

    @property
    def cost_gbp(self) -> float:
        return round(self.mwh * self.price_per_mwh, 2)


class RegoPortfolio:
    """Company REGO procurement and retirement tracker."""

    def __init__(self):
        self._purchases: list[RegoPurchase] = []

    def buy(self, purchase: RegoPurchase) -> RegoPurchase:
        self._purchases.append(purchase)
        return purchase

    def retire(self, purchase_id: str, retirement_date: str) -> bool:
        p = next((p for p in self._purchases if p.purchase_id == purchase_id), None)
        if p is None:
            return False
        p.retired = True
        p.retirement_date = retirement_date
        return True

    def by_scheme_year(self, year: int) -> list[RegoPurchase]:
        return [p for p in self._purchases if p.scheme_year == year]

    def retired_mwh(self, year: int) -> float:
        return sum(p.mwh for p in self.by_scheme_year(year) if p.retired)

    def available_mwh(self, year: int) -> float:
        return sum(p.mwh for p in self.by_scheme_year(year) if not p.retired)

    def total_cost_gbp(self, year: int) -> float:
        return round(sum(p.cost_gbp for p in self.by_scheme_year(year)), 2)

    def coverage_check(self, year: int, consumption_mwh: float) -> dict:
        """Check if REGOs cover stated renewable consumption."""
        available = self.available_mwh(year) + self.retired_mwh(year)
        shortfall = max(0.0, consumption_mwh - available)
        return {
            "consumption_mwh": consumption_mwh,
            "rego_held_mwh": available,
            "rego_retired_mwh": self.retired_mwh(year),
            "shortfall_mwh": round(shortfall, 2),
            "covered": shortfall == 0.0,
            "coverage_pct": round(100.0 * min(1.0, available / consumption_mwh), 1) if consumption_mwh > 0 else 100.0,
        }

    def by_technology(self, year: int) -> dict[str, float]:
        tech: dict[str, float] = {}
        for p in self.by_scheme_year(year):
            tech[p.technology] = round(tech.get(p.technology, 0.0) + p.mwh, 2)
        return tech

    def summary(self, year: int) -> dict:
        purchases = self.by_scheme_year(year)
        return {
            "scheme_year": year,
            "purchases": len(purchases),
            "total_mwh": round(sum(p.mwh for p in purchases), 2),
            "retired_mwh": self.retired_mwh(year),
            "available_mwh": self.available_mwh(year),
            "total_cost_gbp": self.total_cost_gbp(year),
            "by_technology": self.by_technology(year),
        }


def get_rego_price(year: int) -> float:
    """Published market estimate of REGO price for a given scheme year."""
    return _REGO_PRICE_BY_YEAR.get(year, 3.00)
