"""OTC derivative variation margin call tracking (ISDA CSA mechanism).

When a UK energy supplier buys forward contracts OTC (via an ISDA agreement),
any daily mark-to-market loss generates a variation margin call — the counterparty
demands cash collateral equal to the loss on the position.

During 2022, many suppliers failed partly because their forward positions moved
against them (prices rose after buying) — the company was LONG electricity via
hedges that lost value as spot rose, requiring huge daily margin calls that
exhausted liquidity even though the underlying tariff revenue was also rising.

Epistemic constraint: the company tracks its own hedge positions and daily
mark-to-market P&L. It observes margin calls from its counterparties. It does NOT
read the simulation's forward curve internals — it derives MTM from its own
trade blotter against observable market prices.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


class MarginCallStatus(str, Enum):
    PENDING = "pending"
    MET = "met"
    DISPUTED = "disputed"
    DEFAULTED = "defaulted"


class MarginCallDirection(str, Enum):
    CALL = "call"       # Company must pay margin to counterparty
    RETURN = "return"   # Counterparty returns margin to company (position moved in company's favour)


@dataclass(frozen=True)
class VariationMarginCall:
    call_id: str
    call_date: date
    counterparty: str
    notional_mwh: float
    mtm_loss_gbp: float        # Positive = company owes; negative = counterparty owes
    direction: MarginCallDirection
    status: MarginCallStatus
    settled_date: Optional[date] = None

    @property
    def is_call_on_company(self) -> bool:
        return self.direction == MarginCallDirection.CALL

    @property
    def is_settled(self) -> bool:
        return self.status in (MarginCallStatus.MET, MarginCallStatus.DEFAULTED)

    @property
    def is_overdue(self) -> bool:
        """CSA standard: T+1 settlement for variation margin calls."""
        if self.status == MarginCallStatus.PENDING and self.settled_date is None:
            from datetime import date as dt
            delta = (dt.today() - self.call_date).days
            return delta > 1
        return False

    @property
    def cash_impact_gbp(self) -> float:
        """Negative = cash outflow (margin call paid); positive = cash inflow."""
        if self.direction == MarginCallDirection.CALL:
            return -abs(self.mtm_loss_gbp)
        return abs(self.mtm_loss_gbp)


class OTCMarginBook:
    """Tracks all variation margin calls across OTC hedging counterparties."""

    def __init__(self) -> None:
        self._calls: list[VariationMarginCall] = []

    def record_call(
        self,
        call_id: str,
        call_date: date,
        counterparty: str,
        notional_mwh: float,
        mtm_loss_gbp: float,
        direction: MarginCallDirection = MarginCallDirection.CALL,
        status: MarginCallStatus = MarginCallStatus.PENDING,
        settled_date: Optional[date] = None,
    ) -> VariationMarginCall:
        call = VariationMarginCall(
            call_id=call_id,
            call_date=call_date,
            counterparty=counterparty,
            notional_mwh=notional_mwh,
            mtm_loss_gbp=mtm_loss_gbp,
            direction=direction,
            status=status,
            settled_date=settled_date,
        )
        self._calls.append(call)
        return call

    def settle_call(self, call_id: str, settled_date: date) -> Optional[VariationMarginCall]:
        for i, call in enumerate(self._calls):
            if call.call_id == call_id:
                settled = VariationMarginCall(
                    call_id=call.call_id,
                    call_date=call.call_date,
                    counterparty=call.counterparty,
                    notional_mwh=call.notional_mwh,
                    mtm_loss_gbp=call.mtm_loss_gbp,
                    direction=call.direction,
                    status=MarginCallStatus.MET,
                    settled_date=settled_date,
                )
                self._calls[i] = settled
                return settled
        return None

    @property
    def all_calls(self) -> list[VariationMarginCall]:
        return list(self._calls)

    @property
    def pending_calls(self) -> list[VariationMarginCall]:
        return [c for c in self._calls if c.status == MarginCallStatus.PENDING]

    @property
    def overdue_calls(self) -> list[VariationMarginCall]:
        return [c for c in self._calls if c.is_overdue]

    @property
    def total_cash_impact_gbp(self) -> float:
        """Net cash impact: negative = net outflow (margin paid)."""
        return sum(c.cash_impact_gbp for c in self._calls if c.status == MarginCallStatus.MET)

    @property
    def total_pending_outflow_gbp(self) -> float:
        """Pending margin calls the company still owes."""
        return sum(
            abs(c.mtm_loss_gbp)
            for c in self._calls
            if c.status == MarginCallStatus.PENDING and c.direction == MarginCallDirection.CALL
        )

    @property
    def calls_by_counterparty(self) -> dict[str, float]:
        """Total cash impact per counterparty."""
        result: dict[str, float] = {}
        for c in self._calls:
            if c.status == MarginCallStatus.MET:
                result[c.counterparty] = result.get(c.counterparty, 0.0) + c.cash_impact_gbp
        return result

    def calls_for_year(self, year: int) -> list[VariationMarginCall]:
        return [c for c in self._calls if c.call_date.year == year]

    def net_cash_for_year(self, year: int) -> float:
        return sum(
            c.cash_impact_gbp for c in self._calls
            if c.call_date.year == year and c.status == MarginCallStatus.MET
        )

    def margin_book_summary(self) -> str:
        n_total = len(self._calls)
        n_pending = len(self.pending_calls)
        n_overdue = len(self.overdue_calls)
        total_impact = self.total_cash_impact_gbp
        pending_out = self.total_pending_outflow_gbp
        lines = [
            "OTC Margin Book Summary",
            "Total calls: {:d}".format(n_total),
            "Pending: {:d} | Overdue: {:d}".format(n_pending, n_overdue),
            "Net settled cash impact: £{:,.0f}".format(total_impact),
            "Pending outflow: £{:,.0f}".format(pending_out),
        ]
        for cpty, impact in sorted(self.calls_by_counterparty.items()):
            lines.append("  {}: £{:,.0f}".format(cpty, impact))
        return chr(10).join(lines)
