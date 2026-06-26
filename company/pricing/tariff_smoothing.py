from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class SmoothedRateStatus(str, Enum):
    BELOW_COST = "below_cost"
    AT_COST = "at_cost"
    MARGINAL = "marginal"
    PROFITABLE = "profitable"


@dataclass(frozen=True)
class TariffDecision:
    year: int
    commodity: str
    unit_rate_p_per_kwh: float
    wholesale_cost_p_per_kwh: float
    smoothing_reserve_applied_p: float

    @property
    def gross_margin_p_per_kwh(self) -> float:
        return round(self.unit_rate_p_per_kwh - self.wholesale_cost_p_per_kwh, 4)

    @property
    def is_loss_making(self) -> bool:
        return self.gross_margin_p_per_kwh < 0

    @property
    def status(self) -> SmoothedRateStatus:
        gm = self.gross_margin_p_per_kwh
        if gm < 0:
            return SmoothedRateStatus.BELOW_COST
        if gm < 0.1:
            return SmoothedRateStatus.AT_COST
        if gm < 0.5:
            return SmoothedRateStatus.MARGINAL
        return SmoothedRateStatus.PROFITABLE


class TariffSmoothingBook:
    def __init__(self) -> None:
        self._decisions: list[TariffDecision] = []
        self._reserve_p: float = 0.0

    def record_decision(self, decision: TariffDecision) -> TariffDecision:
        self._decisions.append(decision)
        self._reserve_p += decision.smoothing_reserve_applied_p
        return decision

    def decisions_for_commodity(self, commodity: str) -> list[TariffDecision]:
        return [d for d in self._decisions if d.commodity == commodity]

    def decisions_for_year(self, year: int) -> list[TariffDecision]:
        return [d for d in self._decisions if d.year == year]

    def loss_making_years(self, commodity: Optional[str] = None) -> list[TariffDecision]:
        return [d for d in self._decisions if d.is_loss_making
                and (commodity is None or d.commodity == commodity)]

    def max_bill_shock_pct(self, commodity: str) -> float:
        decs = sorted(self.decisions_for_commodity(commodity), key=lambda d: d.year)
        if len(decs) < 2:
            return 0.0
        max_shock = 0.0
        for i in range(1, len(decs)):
            prev_rate = decs[i-1].unit_rate_p_per_kwh
            if prev_rate > 0:
                shock = (decs[i].unit_rate_p_per_kwh - prev_rate) / prev_rate * 100.0
                max_shock = max(max_shock, shock)
        return round(max_shock, 2)

    def smoothing_summary(self) -> dict:
        all_elec = self.decisions_for_commodity("electricity")
        all_gas = self.decisions_for_commodity("gas")
        loss_years_elec = len([d for d in all_elec if d.is_loss_making])
        loss_years_gas = len([d for d in all_gas if d.is_loss_making])
        return {
            "total_decisions": len(self._decisions),
            "cumulative_reserve_p_per_kwh": round(self._reserve_p, 4),
            "loss_making_elec_years": loss_years_elec,
            "loss_making_gas_years": loss_years_gas,
            "max_elec_bill_shock_pct": self.max_bill_shock_pct("electricity"),
            "max_gas_bill_shock_pct": self.max_bill_shock_pct("gas"),
        }
