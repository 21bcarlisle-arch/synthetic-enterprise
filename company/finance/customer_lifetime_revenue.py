"""Customer Lifetime Revenue Register (Phase FN).

Tracks the cumulative revenue actually received from each customer across
their entire relationship with the company (from onboarding to switch-away).

This is distinct from CLV (forward-looking estimate); this is backward-looking
actuals that tell the true story of each customer relationship.

Revenue categories tracked:
- Unit consumption (electricity + gas)
- Standing charges
- SEG/FIT export payments (negative: company pays customer)
- Late payment charges
- Goodwill credits (negative: company credits customer)
- Reconnection fees

Combined with cost-to-serve, this gives the actual lifetime P&L per customer.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class LifetimeRevenueCategory(str, Enum):
    UNIT_ELECTRICITY = "unit_electricity"
    UNIT_GAS = "unit_gas"
    STANDING_CHARGE_ELECTRICITY = "standing_charge_electricity"
    STANDING_CHARGE_GAS = "standing_charge_gas"
    SEG_PAYMENT = "seg_payment"         # company pays -> negative
    LATE_PAYMENT_CHARGE = "late_payment_charge"
    GOODWILL_CREDIT = "goodwill_credit" # company credits -> negative
    RECONNECTION_FEE = "reconnection_fee"
    DEBT_WRITTEN_OFF = "debt_written_off"  # revenue never received -> negative


@dataclass(frozen=True)
class LifetimeRevenueEntry:
    account_id: str
    category: LifetimeRevenueCategory
    period_start: dt.date
    period_end: dt.date
    amount_gbp: float   # negative = outflow from company

    @property
    def is_outflow(self) -> bool:
        return self.amount_gbp < 0


@dataclass(frozen=True)
class CustomerLifetimeSummary:
    account_id: str
    onboarding_date: dt.date
    switch_away_date: Optional[dt.date]
    total_revenue_gbp: float
    total_outflows_gbp: float
    total_lifetime_cost_to_serve_gbp: float

    @property
    def net_lifetime_contribution_gbp(self) -> float:
        return self.total_revenue_gbp + self.total_outflows_gbp - self.total_lifetime_cost_to_serve_gbp

    @property
    def tenure_years(self) -> float:
        end = self.switch_away_date or dt.date.today()
        return (end - self.onboarding_date).days / 365.25

    @property
    def avg_annual_contribution_gbp(self) -> float:
        if self.tenure_years <= 0:
            return 0.0
        return self.net_lifetime_contribution_gbp / self.tenure_years

    @property
    def is_net_positive(self) -> bool:
        return self.net_lifetime_contribution_gbp > 0

    def lifetime_summary(self) -> str:
        return (
            "CLR " + self.account_id + ": "
            "revenue=GBP" + str(round(self.total_revenue_gbp, 0)) + " "
            "outflows=GBP" + str(round(self.total_outflows_gbp, 0)) + " "
            "net=GBP" + str(round(self.net_lifetime_contribution_gbp, 0)) + " "
            "tenure=" + str(round(self.tenure_years, 1)) + "yr"
        )


class CustomerLifetimeRevenueRegister:

    def __init__(self) -> None:
        self._entries: List[LifetimeRevenueEntry] = []

    def record(self, entry: LifetimeRevenueEntry) -> LifetimeRevenueEntry:
        self._entries.append(entry)
        return entry

    def entries_for_account(self, account_id: str) -> List[LifetimeRevenueEntry]:
        return [e for e in self._entries if e.account_id == account_id]

    def total_revenue_for_account(self, account_id: str) -> float:
        return sum(
            e.amount_gbp for e in self.entries_for_account(account_id)
            if not e.is_outflow
        )

    def total_outflows_for_account(self, account_id: str) -> float:
        return sum(
            e.amount_gbp for e in self.entries_for_account(account_id)
            if e.is_outflow
        )

    def build_summary(
        self,
        account_id: str,
        onboarding_date: dt.date,
        lifetime_cost_to_serve_gbp: float,
        switch_away_date: Optional[dt.date] = None,
    ) -> CustomerLifetimeSummary:
        return CustomerLifetimeSummary(
            account_id=account_id,
            onboarding_date=onboarding_date,
            switch_away_date=switch_away_date,
            total_revenue_gbp=self.total_revenue_for_account(account_id),
            total_outflows_gbp=self.total_outflows_for_account(account_id),
            total_lifetime_cost_to_serve_gbp=lifetime_cost_to_serve_gbp,
        )

    def portfolio_lifetime_revenue_gbp(self) -> float:
        return sum(e.amount_gbp for e in self._entries if not e.is_outflow)

    def portfolio_outflows_gbp(self) -> float:
        return sum(e.amount_gbp for e in self._entries if e.is_outflow)

    def register_summary(self) -> str:
        n = len(set(e.account_id for e in self._entries))
        total_rev = self.portfolio_lifetime_revenue_gbp()
        total_out = self.portfolio_outflows_gbp()
        return (
            "CLR Register: " + str(n) + " customers. "
            "Total revenue: GBP" + str(round(total_rev, 0)) + ". "
            "Total outflows: GBP" + str(round(total_out, 0)) + "."
        )
