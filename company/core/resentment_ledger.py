"""Customer Resentment Ledger (Phase EA).

The CTO Architecture Guidance mandates the Resentment Ledger as a first-class
Horizon 2 behavioral physics entity:

"Do not model churn solely on immediate bill shocks. Implement a Stock accumulator
— emotional accumulation over time. Minor friction points add to the stock.
When the stock breaches an agent's personal threshold, they churn irreversibly
(future CAC = infinity for that customer)."

The Resentment Ledger models this as:
- Each friction event adds a resentment score to the customer's running total
- The score decays over time (customers forget minor issues)
- When cumulative resentment crosses a personal threshold, churn is triggered
- Once burned, a customer's reacquisition cost is infinite (irreversible)

Friction event types with calibrated scores:
- BILLING_ERROR (£>£50): +15 (high friction)
- PAYMENT_FAILURE (direct debit bounce): +8
- COMPLAINT_UNRESOLVED (>14d): +20
- PRICE_INCREASE (>10%): +12
- OUTAGE (>4h): +10
- CALL_WAIT_LONG (>30min): +6
- BILL_SHOCK (>50% variance): +18
- COMPLAINT_RESOLVED_WELL: -5 (reduces resentment)

Decay rate: -1 point per month (forgetting curve).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class FrictionEventType(str, Enum):
    BILLING_ERROR = "billing_error"
    PAYMENT_FAILURE = "payment_failure"
    COMPLAINT_UNRESOLVED = "complaint_unresolved"
    PRICE_INCREASE = "price_increase"
    OUTAGE = "outage"
    CALL_WAIT_LONG = "call_wait_long"
    BILL_SHOCK = "bill_shock"
    COMPLAINT_RESOLVED_WELL = "complaint_resolved_well"
    SWITCHING_BARRIER = "switching_barrier"


_BASE_FRICTION_SCORES: Dict[FrictionEventType, float] = {
    FrictionEventType.BILLING_ERROR: 15.0,
    FrictionEventType.PAYMENT_FAILURE: 8.0,
    FrictionEventType.COMPLAINT_UNRESOLVED: 20.0,
    FrictionEventType.PRICE_INCREASE: 12.0,
    FrictionEventType.OUTAGE: 10.0,
    FrictionEventType.CALL_WAIT_LONG: 6.0,
    FrictionEventType.BILL_SHOCK: 18.0,
    FrictionEventType.COMPLAINT_RESOLVED_WELL: -5.0,
    FrictionEventType.SWITCHING_BARRIER: 4.0,
}

_DEFAULT_CHURN_THRESHOLD = 50.0     # personal stock threshold above which churn triggers
_MONTHLY_DECAY_RATE = 1.0           # points lost per month (forgetting curve)


@dataclass(frozen=True)
class FrictionEvent:
    event_type: FrictionEventType
    occurred_at: dt.date
    score_delta: float                # +ve = more resentment; -ve = repair
    description: str = ""
    amplifier: float = 1.0           # multiplier for unusually severe instances


@dataclass
class CustomerResentmentState:
    account_id: str
    churn_threshold: float = _DEFAULT_CHURN_THRESHOLD
    _events: List[FrictionEvent] = field(default_factory=list)
    _burned: bool = False             # True = irreversible churn triggered

    @property
    def is_burned(self) -> bool:
        return self._burned

    def current_score(self, as_of: dt.date) -> float:
        """Cumulative resentment score with monthly decay applied."""
        if self._burned:
            return float("inf")
        total = 0.0
        for e in self._events:
            months_ago = (as_of.year - e.occurred_at.year) * 12 + (as_of.month - e.occurred_at.month)
            months_ago = max(0, months_ago)
            delta = e.score_delta * e.amplifier
            if delta > 0:
                decayed = max(0.0, delta - months_ago * _MONTHLY_DECAY_RATE)
                total += decayed
            else:
                total += delta  # repairs don't decay
        return max(0.0, total)

    @property
    def is_at_churn_risk(self) -> bool:
        return self.current_score(dt.date.today()) >= self.churn_threshold * 0.7

    def check_threshold(self, as_of: dt.date) -> bool:
        """Returns True if churn threshold crossed (sets burned)."""
        if self._burned:
            return True
        if self.current_score(as_of) >= self.churn_threshold:
            self._burned = True
            return True
        return False

    def record(self, event: FrictionEvent) -> None:
        self._events.append(event)

    def event_history(self) -> List[FrictionEvent]:
        return list(self._events)


class ResentmentLedger:
    """Portfolio-level resentment tracking. First-class behavioral physics entity."""

    def __init__(self) -> None:
        self._customers: Dict[str, CustomerResentmentState] = {}

    def _get_or_create(self, account_id: str, threshold: float = _DEFAULT_CHURN_THRESHOLD) -> CustomerResentmentState:
        if account_id not in self._customers:
            self._customers[account_id] = CustomerResentmentState(
                account_id=account_id,
                churn_threshold=threshold,
            )
        return self._customers[account_id]

    def record_friction(
        self,
        account_id: str,
        event_type: FrictionEventType,
        occurred_at: dt.date,
        amplifier: float = 1.0,
        description: str = "",
        threshold: float = _DEFAULT_CHURN_THRESHOLD,
    ) -> FrictionEvent:
        base_score = _BASE_FRICTION_SCORES[event_type]
        event = FrictionEvent(
            event_type=event_type,
            occurred_at=occurred_at,
            score_delta=base_score,
            description=description,
            amplifier=amplifier,
        )
        state = self._get_or_create(account_id, threshold)
        state.record(event)
        return event

    def get_state(self, account_id: str) -> Optional[CustomerResentmentState]:
        return self._customers.get(account_id)

    def current_score(self, account_id: str, as_of: dt.date) -> float:
        state = self._customers.get(account_id)
        if state is None:
            return 0.0
        return state.current_score(as_of)

    def check_churn_threshold(self, account_id: str, as_of: dt.date) -> bool:
        state = self._customers.get(account_id)
        if state is None:
            return False
        return state.check_threshold(as_of)

    def burned_accounts(self) -> List[str]:
        return [aid for aid, s in self._customers.items() if s.is_burned]

    def at_risk_accounts(self, as_of: dt.date) -> List[str]:
        return [
            aid for aid, s in self._customers.items()
            if not s.is_burned and s.current_score(as_of) >= s.churn_threshold * 0.7
        ]

    def high_scorers(self, as_of: dt.date, top_n: int = 5) -> List[tuple]:
        scores = [
            (aid, s.current_score(as_of))
            for aid, s in self._customers.items()
            if not s.is_burned
        ]
        return sorted(scores, key=lambda x: x[1], reverse=True)[:top_n]

    def resentment_summary(self, as_of: dt.date) -> str:
        n = len(self._customers)
        n_burned = len(self.burned_accounts())
        n_at_risk = len(self.at_risk_accounts(as_of))
        return (
            f"Resentment Ledger: {n} customers tracked. "
            f"Burned (irrecoverable churn): {n_burned}. "
            f"At risk (>70% threshold): {n_at_risk}. "
            f"Threshold: {_DEFAULT_CHURN_THRESHOLD:.0f}pts; decay {_MONTHLY_DECAY_RATE:.0f}pt/month."
        )
