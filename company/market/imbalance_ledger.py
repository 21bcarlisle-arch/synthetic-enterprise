from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ImbalanceDirection(str, Enum):
    LONG = "long"   # bought more than consumed (sold at SBP — usually discount)
    SHORT = "short" # consumed more than bought (bought at SSP — usually premium)
    FLAT = "flat"


@dataclass(frozen=True)
class ImbalanceRecord:
    settlement_date: str
    settlement_period: int  # 1-48
    metered_volume_mwh: float    # actual consumption
    contracted_volume_mwh: float  # position from forwards + intraday
    system_buy_price_gbp_per_mwh: float   # SBP: price to buy shortfall from grid
    system_sell_price_gbp_per_mwh: float  # SSP: price to sell surplus to grid

    @property
    def imbalance_mwh(self) -> float:
        return round(self.contracted_volume_mwh - self.metered_volume_mwh, 4)

    @property
    def direction(self) -> ImbalanceDirection:
        if abs(self.imbalance_mwh) < 0.001:
            return ImbalanceDirection.FLAT
        return ImbalanceDirection.LONG if self.imbalance_mwh > 0 else ImbalanceDirection.SHORT

    @property
    def imbalance_charge_gbp(self) -> float:
        """Positive = receivable (long, SSP). Negative = payable (short, SBP)."""
        if self.direction == ImbalanceDirection.FLAT:
            return 0.0
        if self.direction == ImbalanceDirection.LONG:
            return round(self.imbalance_mwh * self.system_sell_price_gbp_per_mwh, 2)
        # SHORT: cost to buy back shortfall
        return round(self.imbalance_mwh * self.system_buy_price_gbp_per_mwh, 2)

    @property
    def is_crisis_price(self) -> bool:
        return self.system_buy_price_gbp_per_mwh > 500.0

    @property
    def cashout_spread_gbp_per_mwh(self) -> float:
        return round(self.system_buy_price_gbp_per_mwh - self.system_sell_price_gbp_per_mwh, 2)


class ImbalanceLedger:
    def __init__(self) -> None:
        self._records: list[ImbalanceRecord] = []

    def record(self, rec: ImbalanceRecord) -> ImbalanceRecord:
        self._records.append(rec)
        return rec

    def records_for_date(self, date: str) -> list[ImbalanceRecord]:
        return [r for r in self._records if r.settlement_date == date]

    def net_imbalance_cost_gbp(self, date: Optional[str] = None) -> float:
        records = self.records_for_date(date) if date else self._records
        return round(sum(r.imbalance_charge_gbp for r in records), 2)

    def crisis_periods(self) -> list[ImbalanceRecord]:
        return [r for r in self._records if r.is_crisis_price]

    def short_periods(self) -> list[ImbalanceRecord]:
        return [r for r in self._records if r.direction == ImbalanceDirection.SHORT]

    def mean_cashout_spread(self) -> float:
        if not self._records:
            return 0.0
        return round(sum(r.cashout_spread_gbp_per_mwh for r in self._records) / len(self._records), 2)

    def imbalance_summary(self, date: Optional[str] = None) -> dict:
        records = self.records_for_date(date) if date else self._records
        return {
            "total_periods": len(records),
            "net_imbalance_cost_gbp": self.net_imbalance_cost_gbp(date),
            "short_periods": len([r for r in records if r.direction == ImbalanceDirection.SHORT]),
            "crisis_periods": len([r for r in records if r.is_crisis_price]),
            "mean_cashout_spread_gbp_per_mwh": self.mean_cashout_spread(),
        }
