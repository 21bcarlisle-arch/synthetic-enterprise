from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class ConsumptionRating(str, Enum):
    MUCH_LOWER = 'much_lower'     # bottom 20%
    LOWER = 'lower'               # 20-40%
    SIMILAR = 'similar'           # 40-60%
    HIGHER = 'higher'             # 60-80%
    MUCH_HIGHER = 'much_higher'   # top 20%


@dataclass(frozen=True)
class NeighbourhoodComparison:
    customer_id: str
    postcode_district: str
    property_type: str
    occupant_count: int
    customer_annual_kwh: float
    neighbour_median_kwh: float
    neighbour_efficient_kwh: float
    neighbour_count: int

    @property
    def vs_median_pct(self) -> float:
        if self.neighbour_median_kwh <= 0:
            return 0.0
        return round((self.customer_annual_kwh - self.neighbour_median_kwh)
                     / self.neighbour_median_kwh * 100, 1)

    @property
    def vs_efficient_pct(self) -> float:
        if self.neighbour_efficient_kwh <= 0:
            return 0.0
        return round((self.customer_annual_kwh - self.neighbour_efficient_kwh)
                     / self.neighbour_efficient_kwh * 100, 1)

    @property
    def consumption_rating(self) -> ConsumptionRating:
        pct = self.vs_median_pct
        if pct <= -20:
            return ConsumptionRating.MUCH_LOWER
        if pct <= -5:
            return ConsumptionRating.LOWER
        if pct <= 10:
            return ConsumptionRating.SIMILAR
        if pct <= 30:
            return ConsumptionRating.HIGHER
        return ConsumptionRating.MUCH_HIGHER

    @property
    def potential_saving_kwh(self) -> float:
        return max(0.0, round(self.customer_annual_kwh - self.neighbour_efficient_kwh, 1))

    def summary(self) -> dict:
        return {
            'customer_id': self.customer_id,
            'postcode_district': self.postcode_district,
            'customer_annual_kwh': self.customer_annual_kwh,
            'neighbour_median_kwh': self.neighbour_median_kwh,
            'vs_median_pct': self.vs_median_pct,
            'consumption_rating': self.consumption_rating.value,
            'potential_saving_kwh': self.potential_saving_kwh,
        }


def build_neighbourhood_comparison(
    customer_id: str,
    postcode_district: str,
    property_type: str,
    occupant_count: int,
    customer_annual_kwh: float,
    neighbourhood_sample: List[float],
) -> NeighbourhoodComparison:
    if not neighbourhood_sample:
        raise ValueError('neighbourhood_sample must not be empty')
    sorted_sample = sorted(neighbourhood_sample)
    n = len(sorted_sample)
    median_kwh = sorted_sample[n // 2]
    efficient_kwh = sorted_sample[max(0, n // 5)]
    return NeighbourhoodComparison(
        customer_id=customer_id,
        postcode_district=postcode_district,
        property_type=property_type,
        occupant_count=occupant_count,
        customer_annual_kwh=customer_annual_kwh,
        neighbour_median_kwh=median_kwh,
        neighbour_efficient_kwh=efficient_kwh,
        neighbour_count=n,
    )
