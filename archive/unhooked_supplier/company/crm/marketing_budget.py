from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class MarketingCategory(str, Enum):
    PRICE_COMPARISON_COMMISSION = 'price_comparison_commission'
    DIGITAL_ADVERTISING = 'digital_advertising'
    TELESALES_COMMISSION = 'telesales_commission'
    BRAND_ADVERTISING = 'brand_advertising'
    PARTNER_COMMISSION = 'partner_commission'
    RETENTION_OUTBOUND = 'retention_outbound'
    REFERRAL_REWARD = 'referral_reward'


@dataclass(frozen=True)
class MarketingSpend:
    category: MarketingCategory
    year: int
    amount_gbp: float
    customers_acquired: int

    @property
    def cost_per_customer_gbp(self) -> float:
        if self.customers_acquired == 0:
            return 0.0
        return round(self.amount_gbp / self.customers_acquired, 2)


@dataclass(frozen=True)
class AnnualMarketingBudget:
    year: int
    budget_gbp: float
    spend_records: tuple

    @property
    def total_spent_gbp(self) -> float:
        return round(sum(s.amount_gbp for s in self.spend_records), 2)

    @property
    def total_customers_acquired(self) -> int:
        return sum(s.customers_acquired for s in self.spend_records)

    @property
    def blended_cac_gbp(self) -> float:
        if self.total_customers_acquired == 0:
            return 0.0
        return round(self.total_spent_gbp / self.total_customers_acquired, 2)

    @property
    def budget_utilisation_pct(self) -> float:
        if self.budget_gbp <= 0:
            return 0.0
        return round(self.total_spent_gbp / self.budget_gbp * 100, 1)

    def summary(self) -> dict:
        by_category: dict = {}
        for s in self.spend_records:
            by_category[s.category.value] = round(
                by_category.get(s.category.value, 0.0) + s.amount_gbp, 2
            )
        return {
            'year': self.year,
            'budget_gbp': self.budget_gbp,
            'total_spent_gbp': self.total_spent_gbp,
            'budget_utilisation_pct': self.budget_utilisation_pct,
            'total_customers_acquired': self.total_customers_acquired,
            'blended_cac_gbp': self.blended_cac_gbp,
            'by_category': by_category,
        }


class MarketingBudgetTracker:
    def __init__(self) -> None:
        self._budgets: Dict[int, float] = {}
        self._spends: List[MarketingSpend] = []

    def set_budget(self, year: int, budget_gbp: float) -> None:
        self._budgets[year] = budget_gbp

    def record_spend(self, category: MarketingCategory, year: int,
                     amount_gbp: float, customers_acquired: int = 0) -> MarketingSpend:
        spend = MarketingSpend(
            category=category, year=year, amount_gbp=amount_gbp,
            customers_acquired=customers_acquired
        )
        self._spends.append(spend)
        return spend

    def annual_budget(self, year: int) -> AnnualMarketingBudget:
        year_spends = [s for s in self._spends if s.year == year]
        return AnnualMarketingBudget(
            year=year,
            budget_gbp=self._budgets.get(year, 0.0),
            spend_records=tuple(year_spends),
        )

    def total_spend_all_years(self) -> float:
        return round(sum(s.amount_gbp for s in self._spends), 2)

    def cac_by_category(self, year: int) -> Dict[str, float]:
        year_spends = [s for s in self._spends if s.year == year]
        result: dict = {}
        for s in year_spends:
            result[s.category.value] = s.cost_per_customer_gbp
        return result
