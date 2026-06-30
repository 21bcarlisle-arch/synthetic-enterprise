"""Wholesale Trading Mandate Register.

UK energy suppliers require board/risk committee-approved trading mandates
that define the scope of wholesale market activities. A mandate specifies:
  - Which instruments may be traded
  - Maximum tenor and notional position limits
  - The authorization level required per trade size
  - The validity period (typically reviewed annually)

This is the authorization layer above individual trades (see trade_blotter.py)
and counterparty credit limits (see credit_limits.py / wholesale_credit_exposure.py).

Common in ISDA/EMIR risk governance frameworks; Ofgem expects evidence of
board-level oversight of commodity trading activities (SLC 4 / Fitness to Trade).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class TradingInstrument(str, Enum):
    PHYSICAL_ELECTRICITY_FORWARD = "physical_electricity_forward"
    PHYSICAL_GAS_FORWARD = "physical_gas_forward"
    ELECTRICITY_FINANCIAL = "electricity_financial"
    GAS_FINANCIAL = "gas_financial"
    ELECTRICITY_OPTION = "electricity_option"
    GAS_OPTION = "gas_option"
    EFA_BLOCK = "efa_block"
    EXCHANGE_TRADED_FUTURE = "exchange_traded_future"


class AuthorizationLevel(str, Enum):
    TRADER_AUTONOMOUS = "trader_autonomous"         # no additional sign-off required
    RISK_MANAGER_APPROVAL = "risk_manager_approval"
    CFO_APPROVAL = "cfo_approval"
    BOARD_APPROVAL = "board_approval"


class MandateStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    SUPERSEDED = "superseded"


_OPEN = frozenset({MandateStatus.DRAFT, MandateStatus.ACTIVE, MandateStatus.SUSPENDED})


@dataclass(frozen=True)
class TradingMandateRecord:
    mandate_id: str
    instrument: TradingInstrument
    max_tenor_days: int
    max_notional_gbp: float
    max_open_position_mwh: float
    authorization_required: AuthorizationLevel
    valid_from: dt.date
    valid_to: dt.date
    status: MandateStatus
    approved_by: Optional[str] = None
    approved_date: Optional[dt.date] = None

    @property
    def is_approved(self) -> bool:
        return self.status in (MandateStatus.ACTIVE, MandateStatus.SUSPENDED)

    def is_active_as_of(self, as_of: dt.date) -> bool:
        return (
            self.status == MandateStatus.ACTIVE
            and self.valid_from <= as_of <= self.valid_to
        )

    def is_expired_as_of(self, as_of: dt.date) -> bool:
        return as_of > self.valid_to

    def days_remaining(self, as_of: dt.date) -> int:
        if self.is_expired_as_of(as_of):
            return 0
        return (self.valid_to - as_of).days

    def mandate_summary(self) -> str:
        return (
            f"Mandate {self.mandate_id}: {self.instrument.value} "
            f"max_tenor={self.max_tenor_days}d "
            f"max_notional=GBP{self.max_notional_gbp:,.0f} "
            f"auth={self.authorization_required.value} "
            f"[{self.status.value}]"
        )


class WholesaleTradingMandateRegister:
    """Register of board-approved wholesale trading mandates."""

    def __init__(self) -> None:
        self._records: List[TradingMandateRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return "MANDATE-" + str(self._counter).zfill(5)

    def _update(self, mandate_id: str, **kwargs) -> TradingMandateRecord:
        for i, rec in enumerate(self._records):
            if rec.mandate_id == mandate_id:
                updated = TradingMandateRecord(**{**rec.__dict__, **kwargs})
                self._records[i] = updated
                return updated
        raise KeyError(f"Mandate not found: {mandate_id}")

    def _get(self, mandate_id: str) -> TradingMandateRecord:
        rec = next((r for r in self._records if r.mandate_id == mandate_id), None)
        if rec is None:
            raise KeyError(f"Mandate not found: {mandate_id}")
        return rec

    def submit_mandate(
        self,
        instrument: TradingInstrument,
        max_tenor_days: int,
        max_notional_gbp: float,
        max_open_position_mwh: float,
        authorization_required: AuthorizationLevel,
        valid_from: dt.date,
        valid_to: dt.date,
    ) -> TradingMandateRecord:
        if valid_to <= valid_from:
            raise ValueError("valid_to must be after valid_from")
        if max_tenor_days <= 0:
            raise ValueError("max_tenor_days must be positive")
        if max_notional_gbp <= 0:
            raise ValueError("max_notional_gbp must be positive")
        if max_open_position_mwh <= 0:
            raise ValueError("max_open_position_mwh must be positive")
        rec = TradingMandateRecord(
            mandate_id=self._next_id(),
            instrument=instrument,
            max_tenor_days=max_tenor_days,
            max_notional_gbp=max_notional_gbp,
            max_open_position_mwh=max_open_position_mwh,
            authorization_required=authorization_required,
            valid_from=valid_from,
            valid_to=valid_to,
            status=MandateStatus.DRAFT,
        )
        self._records.append(rec)
        return rec

    def approve_mandate(
        self, mandate_id: str, approved_by: str, approved_date: dt.date
    ) -> TradingMandateRecord:
        rec = self._get(mandate_id)
        if rec.status != MandateStatus.DRAFT:
            raise ValueError(f"Cannot approve {rec.status.value} mandate")
        return self._update(mandate_id, status=MandateStatus.ACTIVE,
                            approved_by=approved_by, approved_date=approved_date)

    def suspend(self, mandate_id: str) -> TradingMandateRecord:
        rec = self._get(mandate_id)
        if rec.status != MandateStatus.ACTIVE:
            raise ValueError(f"Cannot suspend {rec.status.value} mandate")
        return self._update(mandate_id, status=MandateStatus.SUSPENDED)

    def reinstate(self, mandate_id: str) -> TradingMandateRecord:
        rec = self._get(mandate_id)
        if rec.status != MandateStatus.SUSPENDED:
            raise ValueError(f"Cannot reinstate {rec.status.value} mandate")
        return self._update(mandate_id, status=MandateStatus.ACTIVE)

    def expire(self, mandate_id: str) -> TradingMandateRecord:
        rec = self._get(mandate_id)
        if rec.status not in _OPEN:
            raise ValueError(f"Cannot expire {rec.status.value} mandate")
        return self._update(mandate_id, status=MandateStatus.EXPIRED)

    def supersede(self, mandate_id: str) -> TradingMandateRecord:
        rec = self._get(mandate_id)
        if rec.status not in _OPEN:
            raise ValueError(f"Cannot supersede {rec.status.value} mandate")
        return self._update(mandate_id, status=MandateStatus.SUPERSEDED)

    # ── Queries ──────────────────────────────────────────────────────────────

    @property
    def all_records(self) -> List[TradingMandateRecord]:
        return list(self._records)

    def active_mandates(self, as_of: dt.date) -> List[TradingMandateRecord]:
        return [r for r in self._records if r.is_active_as_of(as_of)]

    def instruments_authorized(self, as_of: dt.date) -> List[TradingInstrument]:
        return list({r.instrument for r in self._records if r.is_active_as_of(as_of)})

    def mandate_for_instrument(
        self, instrument: TradingInstrument, as_of: dt.date
    ) -> Optional[TradingMandateRecord]:
        active = [r for r in self._records
                  if r.instrument == instrument and r.is_active_as_of(as_of)]
        if not active:
            return None
        return max(active, key=lambda r: r.approved_date or dt.date.min)

    def expiring_within(self, as_of: dt.date, days: int = 30) -> List[TradingMandateRecord]:
        cutoff = as_of + dt.timedelta(days=days)
        return [
            r for r in self._records
            if r.is_active_as_of(as_of) and r.valid_to <= cutoff
        ]

    def draft_mandates(self) -> List[TradingMandateRecord]:
        return [r for r in self._records if r.status == MandateStatus.DRAFT]

    def by_instrument(self, instrument: TradingInstrument) -> List[TradingMandateRecord]:
        return [r for r in self._records if r.instrument == instrument]

    def total_authorized_notional_gbp(self, as_of: dt.date) -> float:
        return sum(r.max_notional_gbp for r in self._records if r.is_active_as_of(as_of))

    def mandate_register_summary(self, as_of: dt.date) -> str:
        total = len(self._records)
        active = len(self.active_mandates(as_of))
        draft = len(self.draft_mandates())
        expiring = len(self.expiring_within(as_of, 30))
        total_notional = self.total_authorized_notional_gbp(as_of)
        return (
            f"Trading Mandates: {total} total | {active} active | {draft} draft "
            f"| {expiring} expiring in 30d "
            f"| GBP{total_notional:,.0f} total authorized notional"
        )
