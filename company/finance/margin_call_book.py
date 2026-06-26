from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class MarginCallStatus(str, Enum):
    RECEIVED = "received"
    SETTLED = "settled"
    DISPUTED = "disputed"
    DEFAULTED = "defaulted"


@dataclass(frozen=True)
class MarginCallEvent:
    call_id: str
    call_date: str
    counterparty: str
    contract_id: str
    initial_margin_gbp: float
    variation_margin_gbp: float
    settlement_deadline: str
    status: MarginCallStatus = MarginCallStatus.RECEIVED

    @property
    def total_margin_required_gbp(self) -> float:
        return round(self.initial_margin_gbp + self.variation_margin_gbp, 2)

    @property
    def is_settled(self) -> bool:
        return self.status == MarginCallStatus.SETTLED

    @property
    def is_stress_event(self) -> bool:
        return self.variation_margin_gbp > 500_000.0


class MarginCallBook:
    def __init__(self, credit_facility_gbp: float = 5_000_000.0) -> None:
        self._calls: list[MarginCallEvent] = []
        self.credit_facility_gbp = credit_facility_gbp

    def record_call(self, call: MarginCallEvent) -> MarginCallEvent:
        self._calls.append(call)
        return call

    def settle_call(self, call_id: str) -> Optional[MarginCallEvent]:
        for i, c in enumerate(self._calls):
            if c.call_id == call_id and not c.is_settled:
                from dataclasses import replace
                settled = replace(c, status=MarginCallStatus.SETTLED)
                self._calls[i] = settled
                return settled
        return None

    def calls_for_date(self, date: str) -> list[MarginCallEvent]:
        return [c for c in self._calls if c.call_date == date]

    def outstanding_calls(self) -> list[MarginCallEvent]:
        return [c for c in self._calls if not c.is_settled and c.status != MarginCallStatus.DEFAULTED]

    def total_outstanding_gbp(self) -> float:
        return round(sum(c.total_margin_required_gbp for c in self.outstanding_calls()), 2)

    def headroom_gbp(self) -> float:
        return round(self.credit_facility_gbp - self.total_outstanding_gbp(), 2)

    def is_liquidity_stressed(self) -> bool:
        return self.total_outstanding_gbp() > self.credit_facility_gbp * 0.8

    def stress_events(self) -> list[MarginCallEvent]:
        return [c for c in self._calls if c.is_stress_event]

    def margin_call_summary(self) -> dict:
        outstanding = self.outstanding_calls()
        return {
            "total_calls": len(self._calls),
            "outstanding_calls": len(outstanding),
            "total_outstanding_gbp": self.total_outstanding_gbp(),
            "credit_facility_gbp": self.credit_facility_gbp,
            "headroom_gbp": self.headroom_gbp(),
            "is_liquidity_stressed": self.is_liquidity_stressed(),
            "stress_events": len(self.stress_events()),
        }
