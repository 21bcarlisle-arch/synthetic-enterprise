"""Counterparty credit limit management.

Before executing a trade, the trading desk checks whether the new
exposure would breach the credit limit for the counterparty. Credit
limits are set by the risk committee based on:
  - Counterparty credit rating (S&P/Moody's/Fitch)
  - Market participant category (CCGT generator, aggregator, retail, bank)
  - Internal risk appetite

UK energy market counterparties are typically rated or have a credit
support agreement (CSA/ISDA) in place.

Credit utilisation = (current exposure / limit) × 100%.
- GREEN: <70%
- AMBER: 70-90%
- RED: >90% (no new trades unless approved)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


_GREEN_THRESHOLD = 0.70
_AMBER_THRESHOLD = 0.90


@dataclass
class CounterpartyLimit:
    counterparty_id: str
    name: str
    credit_rating: str       # e.g. "BBB+", "A-", "NR" (not rated)
    limit_gbp: float
    category: str = ""      # e.g. "CCGT_generator", "aggregator", "bank", "retail"
    active: bool = True


@dataclass
class CreditCheckResult:
    counterparty_id: str
    current_exposure_gbp: float
    proposed_trade_gbp: float
    limit_gbp: float
    utilisation_pct: float
    status: Literal["GREEN", "AMBER", "RED", "NO_LIMIT"]
    approved: bool
    message: str


class CounterpartyCreditManager:
    """Manages credit limits and pre-trade exposure checks."""

    def __init__(self):
        self._limits: dict[str, CounterpartyLimit] = {}
        self._exposures: dict[str, float] = {}  # current exposure in GBP

    def set_limit(self, limit: CounterpartyLimit) -> None:
        self._limits[limit.counterparty_id] = limit

    def get_limit(self, counterparty_id: str) -> CounterpartyLimit | None:
        return self._limits.get(counterparty_id)

    def update_exposure(self, counterparty_id: str, delta_gbp: float) -> float:
        """Add to (or subtract from) current exposure for a counterparty."""
        current = self._exposures.get(counterparty_id, 0.0)
        self._exposures[counterparty_id] = round(current + delta_gbp, 2)
        return self._exposures[counterparty_id]

    def current_exposure(self, counterparty_id: str) -> float:
        return self._exposures.get(counterparty_id, 0.0)

    def check_trade(self, counterparty_id: str, trade_notional_gbp: float) -> CreditCheckResult:
        limit = self._limits.get(counterparty_id)
        if limit is None:
            return CreditCheckResult(
                counterparty_id, 0.0, trade_notional_gbp, 0.0, 0.0,
                "NO_LIMIT", False, "No credit limit set for counterparty — trade blocked"
            )
        current = self.current_exposure(counterparty_id)
        proposed_total = current + trade_notional_gbp
        util = proposed_total / limit.limit_gbp if limit.limit_gbp > 0 else 1.0

        if util >= _AMBER_THRESHOLD:
            status = "RED"
            approved = False
            msg = f"Breach: {util:.0%} utilisation (limit £{limit.limit_gbp:,.0f})"
        elif util >= _GREEN_THRESHOLD:
            status = "AMBER"
            approved = True
            msg = f"Amber: {util:.0%} utilisation — trade approved with monitoring"
        else:
            status = "GREEN"
            approved = True
            msg = f"Green: {util:.0%} utilisation"

        return CreditCheckResult(
            counterparty_id, current, trade_notional_gbp, limit.limit_gbp,
            round(util * 100, 1), status, approved, msg
        )

    def breached_limits(self) -> list[tuple[str, float, float]]:
        """(counterparty_id, exposure, limit) for all counterparties above RED threshold."""
        result = []
        for cp_id, limit in self._limits.items():
            exp = self.current_exposure(cp_id)
            if limit.limit_gbp > 0 and exp / limit.limit_gbp >= _AMBER_THRESHOLD:
                result.append((cp_id, exp, limit.limit_gbp))
        return result

    def summary(self) -> dict:
        total = len(self._limits)
        active = sum(1 for l in self._limits.values() if l.active)
        breached = len(self.breached_limits())
        return {
            "total_limits": total,
            "active_limits": active,
            "breached": breached,
            "total_exposure_gbp": round(sum(self._exposures.values()), 2),
            "total_limit_gbp": round(sum(l.limit_gbp for l in self._limits.values()), 2),
        }
