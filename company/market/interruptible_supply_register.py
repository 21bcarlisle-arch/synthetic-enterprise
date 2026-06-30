"""Interruptible Gas Supply Contract Register.

UK gas suppliers offer I&C customers interruptible (INT) contracts:
- Customer agrees supply can be curtailed during high-demand periods
- In return: lower unit rate vs firm (typically 10-20% discount)
- Notice period: minimum 2 hours (UNC TPD Section X3)
- Annual curtailment cap: typically 30 days per year

Epistemic: contract terms are known to the company. Curtailment
decisions are made by the company or NGT and are observable.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from enum import Enum


class SupplyFirmness(str, Enum):
    FIRM = "firm"
    INTERRUPTIBLE = "interruptible"


class InterruptionReason(str, Enum):
    COLD_WEATHER = "cold_weather"
    NETWORK_CONSTRAINT = "network_constraint"
    NGT_INSTRUCTION = "ngt_instruction"
    SUPPLIER_DISCRETION = "supplier_discretion"


_MAX_ANNUAL_CURTAILMENT_DAYS = 30
_MIN_NOTICE_HOURS = 2
_DISCOUNT_PCT_TYPICAL = 15.0


@dataclass(frozen=True)
class InterruptionEvent:
    event_date: date
    account_id: str
    reason: InterruptionReason
    curtailment_kwh: float
    notice_hours: float

    @property
    def notice_compliant(self) -> bool:
        return self.notice_hours >= _MIN_NOTICE_HOURS


@dataclass(frozen=True)
class InterruptibleContract:
    account_id: str
    start_date: date
    annual_kwh: float
    discount_pct: float = _DISCOUNT_PCT_TYPICAL

    @property
    def saving_vs_firm_gbp_pa(self) -> float:
        return self.annual_kwh * 0.04 * self.discount_pct / 100


class InterruptibleSupplyRegister:
    def __init__(self) -> None:
        self._contracts: dict[str, InterruptibleContract] = {}
        self._events: list[InterruptionEvent] = []

    def register(self, account_id: str, start_date: date, annual_kwh: float, discount_pct: float = _DISCOUNT_PCT_TYPICAL) -> InterruptibleContract:
        contract = InterruptibleContract(account_id=account_id, start_date=start_date, annual_kwh=annual_kwh, discount_pct=discount_pct)
        self._contracts[account_id] = contract
        return contract

    def record_interruption(self, event_date: date, account_id: str, reason: InterruptionReason, curtailment_kwh: float, notice_hours: float) -> InterruptionEvent:
        event = InterruptionEvent(event_date=event_date, account_id=account_id, reason=reason, curtailment_kwh=curtailment_kwh, notice_hours=notice_hours)
        self._events.append(event)
        return event

    @property
    def active_contracts(self) -> list[InterruptibleContract]:
        return list(self._contracts.values())

    @property
    def interruptible_accounts(self) -> list[str]:
        return list(self._contracts.keys())

    def events_for_account(self, account_id: str) -> list[InterruptionEvent]:
        return [e for e in self._events if e.account_id == account_id]

    def annual_curtailment_days(self, account_id: str, year: int) -> int:
        return len({e.event_date for e in self.events_for_account(account_id) if e.event_date.year == year})

    def over_cap_accounts(self, year: int) -> list[str]:
        return [a for a in self._contracts if self.annual_curtailment_days(a, year) > _MAX_ANNUAL_CURTAILMENT_DAYS]

    @property
    def notice_violations(self) -> list[InterruptionEvent]:
        return [e for e in self._events if not e.notice_compliant]

    @property
    def total_portfolio_annual_kwh(self) -> float:
        return sum(c.annual_kwh for c in self._contracts.values())

    def interruptible_summary(self) -> str:
        n, total_kwh = len(self._contracts), self.total_portfolio_annual_kwh
        return (
            "Interruptible Gas Supply Register (UNC)\n"
            "INT contracts: {:d} | Portfolio: {:,.0f} kWh/yr\n"
            "Curtailment events: {:d} | Notice violations: {:d}".format(
                n, total_kwh, len(self._events), len(self.notice_violations))
        )
