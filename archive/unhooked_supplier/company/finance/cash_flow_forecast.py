from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class WeeklyCashFlow:
    week_start: dt.date
    customer_receipts_gbp: float
    wholesale_settlements_gbp: float
    network_charges_gbp: float
    policy_levies_gbp: float
    operating_costs_gbp: float
    other_outflows_gbp: float = 0.0

    @property
    def total_inflows_gbp(self) -> float:
        return round(self.customer_receipts_gbp, 2)

    @property
    def total_outflows_gbp(self) -> float:
        return round(
            self.wholesale_settlements_gbp + self.network_charges_gbp
            + self.policy_levies_gbp + self.operating_costs_gbp + self.other_outflows_gbp,
            2,
        )

    @property
    def net_cash_gbp(self) -> float:
        return round(self.total_inflows_gbp - self.total_outflows_gbp, 2)

    @property
    def is_net_positive(self) -> bool:
        return self.net_cash_gbp >= 0


@dataclass(frozen=True)
class CashFlowForecast:
    as_of: dt.date
    opening_cash_gbp: float
    weeks: tuple

    @property
    def closing_cash_gbp(self) -> float:
        total_net = sum(w.net_cash_gbp for w in self.weeks)
        return round(self.opening_cash_gbp + total_net, 2)

    @property
    def minimum_weekly_balance_gbp(self) -> float:
        running = self.opening_cash_gbp
        min_bal = running
        for w in self.weeks:
            running += w.net_cash_gbp
            if running < min_bal:
                min_bal = running
        return round(min_bal, 2)

    @property
    def weeks_to_cash_concern(self) -> Optional[int]:
        running = self.opening_cash_gbp
        for i, w in enumerate(self.weeks):
            running += w.net_cash_gbp
            if running <= 0:
                return i + 1
        return None

    @property
    def is_solvent_throughout(self) -> bool:
        return self.weeks_to_cash_concern is None

    @property
    def total_net_cash_gbp(self) -> float:
        return round(sum(w.net_cash_gbp for w in self.weeks), 2)

    def summary(self) -> dict:
        return {
            'as_of': str(self.as_of),
            'opening_cash_gbp': round(self.opening_cash_gbp, 2),
            'closing_cash_gbp': self.closing_cash_gbp,
            'minimum_weekly_balance_gbp': self.minimum_weekly_balance_gbp,
            'weeks_to_cash_concern': self.weeks_to_cash_concern,
            'is_solvent_throughout': self.is_solvent_throughout,
            'total_net_cash_gbp': self.total_net_cash_gbp,
            'week_count': len(self.weeks),
        }


def build_cash_flow_forecast(
    as_of: dt.date,
    opening_cash_gbp: float,
    weekly_receipts_gbp: float,
    weekly_wholesale_gbp: float,
    weekly_network_gbp: float,
    weekly_policy_gbp: float,
    weekly_opex_gbp: float,
    weeks: int = 13,
    other_outflows_by_week: Optional[List[float]] = None,
) -> CashFlowForecast:
    week_list = []
    for i in range(weeks):
        other = 0.0 if other_outflows_by_week is None else other_outflows_by_week[i]
        week_list.append(
            WeeklyCashFlow(
                week_start=as_of + dt.timedelta(weeks=i),
                customer_receipts_gbp=weekly_receipts_gbp,
                wholesale_settlements_gbp=weekly_wholesale_gbp,
                network_charges_gbp=weekly_network_gbp,
                policy_levies_gbp=weekly_policy_gbp,
                operating_costs_gbp=weekly_opex_gbp,
                other_outflows_gbp=other,
            )
        )
    return CashFlowForecast(as_of=as_of, opening_cash_gbp=opening_cash_gbp, weeks=tuple(week_list))
