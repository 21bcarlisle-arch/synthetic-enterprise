"""Wholesale Market Trade Confirmation Register (Phase GR).

After each OTC energy trade, counterparties must exchange signed trade
confirmations within agreed timeframes. Outstanding unconfirmed trades
create operational and credit risk.

Confirmation timelines (EFET/ISDA 2002 Master Agreement):
  Bilateral OTC: counterparties exchange confirmations within 2 business days
  Exchange-cleared: exchange auto-confirms on T+0 or T+1
  Brokered OTC: broker issues matched term sheet on day of trade

Regulatory overlay:
  EMIR Art. 11(1)(a): timely confirmation obligation for OTC derivatives
  FCA SUP 17: MiFID transaction reporting (separate from confirmation)
  REMIT Art. 8: wholesale energy contracts must be reported

Unconfirmed trades beyond threshold attract FCA scrutiny and Ofgem review.
Industry norm: <3% unconfirmed after 5 business days = acceptable.

Distinct from emir_reporting_register.py (regulatory trade repository
reporting) and trade_blotter.py (position recording).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

_BILATERAL_CONFIRMATION_DAYS = 2
_BROKERED_CONFIRMATION_DAYS = 1
_ESCALATION_DAYS = 5


class ConfirmationMethod(str, Enum):
    ELECTRONIC_MATCHING = "electronic_matching"
    SIGNED_CONFIRM = "signed_confirm"
    BROKER_TERM_SHEET = "broker_term_sheet"
    EXCHANGE_AUTO = "exchange_auto"


class ConfirmationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    MATCHED = "matched"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"


_OPEN = frozenset({ConfirmationStatus.PENDING, ConfirmationStatus.SENT})
_TERMINAL = frozenset({ConfirmationStatus.MATCHED, ConfirmationStatus.CANCELLED})


@dataclass(frozen=True)
class TradeConfirmationRecord:
    confirm_id: str
    trade_ref: str
    counterparty_id: str
    trade_date: dt.date
    commodity: str
    notional_mwh: float
    notional_gbp: float
    confirmation_method: ConfirmationMethod
    status: ConfirmationStatus = ConfirmationStatus.PENDING
    sent_date: Optional[dt.date] = None
    matched_date: Optional[dt.date] = None
    dispute_reason: str = ""

    @property
    def confirmation_due(self) -> dt.date:
        if self.confirmation_method == ConfirmationMethod.BROKER_TERM_SHEET:
            return self.trade_date + dt.timedelta(days=_BROKERED_CONFIRMATION_DAYS)
        if self.confirmation_method == ConfirmationMethod.EXCHANGE_AUTO:
            return self.trade_date + dt.timedelta(days=1)
        return self.trade_date + dt.timedelta(days=_BILATERAL_CONFIRMATION_DAYS)

    @property
    def is_open(self) -> bool:
        return self.status in _OPEN

    def is_overdue(self, as_of: dt.date) -> bool:
        return self.is_open and as_of > self.confirmation_due

    def is_long_outstanding(self, as_of: dt.date) -> bool:
        return self.is_open and (as_of - self.trade_date).days > _ESCALATION_DAYS

    def days_outstanding(self, as_of: dt.date) -> int:
        end = self.matched_date if self.matched_date else as_of
        return (end - self.trade_date).days

    def confirmation_summary(self) -> str:
        return (
            "Confirm " + self.confirm_id + " trade=" + self.trade_ref
            + " cpty=" + self.counterparty_id
            + " notional=GBP" + str(round(self.notional_gbp, 0))
            + " [" + self.status.value + "]"
        )


class TradeConfirmationRegister:

    def __init__(self) -> None:
        self._records: List[TradeConfirmationRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return "TC-" + str(self._counter).zfill(6)

    def register_trade(
        self,
        trade_ref: str,
        counterparty_id: str,
        trade_date: dt.date,
        commodity: str,
        notional_mwh: float,
        notional_gbp: float,
        confirmation_method: ConfirmationMethod,
    ) -> TradeConfirmationRecord:
        if notional_mwh < 0 or notional_gbp < 0:
            raise ValueError("notional values must be non-negative")
        record = TradeConfirmationRecord(
            confirm_id=self._next_id(),
            trade_ref=trade_ref, counterparty_id=counterparty_id,
            trade_date=trade_date, commodity=commodity,
            notional_mwh=notional_mwh, notional_gbp=notional_gbp,
            confirmation_method=confirmation_method,
        )
        self._records.append(record)
        return record

    def _update(self, confirm_id: str, **kwargs) -> TradeConfirmationRecord:
        for i, r in enumerate(self._records):
            if r.confirm_id == confirm_id:
                updated = TradeConfirmationRecord(
                    confirm_id=r.confirm_id, trade_ref=r.trade_ref,
                    counterparty_id=r.counterparty_id, trade_date=r.trade_date,
                    commodity=r.commodity, notional_mwh=r.notional_mwh,
                    notional_gbp=r.notional_gbp,
                    confirmation_method=r.confirmation_method,
                    status=kwargs.get("status", r.status),
                    sent_date=kwargs.get("sent_date", r.sent_date),
                    matched_date=kwargs.get("matched_date", r.matched_date),
                    dispute_reason=kwargs.get("dispute_reason", r.dispute_reason),
                )
                self._records[i] = updated
                return updated
        raise KeyError("Confirmation " + confirm_id + " not found")

    def send_confirmation(self, confirm_id: str, sent_date: dt.date) -> TradeConfirmationRecord:
        return self._update(confirm_id, status=ConfirmationStatus.SENT, sent_date=sent_date)

    def match_confirmation(self, confirm_id: str, matched_date: dt.date) -> TradeConfirmationRecord:
        return self._update(confirm_id, status=ConfirmationStatus.MATCHED, matched_date=matched_date)

    def raise_dispute(self, confirm_id: str, dispute_reason: str) -> TradeConfirmationRecord:
        return self._update(confirm_id, status=ConfirmationStatus.DISPUTED,
                            dispute_reason=dispute_reason)

    def cancel(self, confirm_id: str) -> TradeConfirmationRecord:
        return self._update(confirm_id, status=ConfirmationStatus.CANCELLED)

    def pending_confirmations(self) -> List[TradeConfirmationRecord]:
        return [r for r in self._records if r.is_open]

    def overdue_confirmations(self, as_of: dt.date) -> List[TradeConfirmationRecord]:
        return [r for r in self._records if r.is_overdue(as_of)]

    def long_outstanding(self, as_of: dt.date) -> List[TradeConfirmationRecord]:
        return [r for r in self._records if r.is_long_outstanding(as_of)]

    def disputed(self) -> List[TradeConfirmationRecord]:
        return [r for r in self._records if r.status == ConfirmationStatus.DISPUTED]

    def by_counterparty(self, counterparty_id: str) -> List[TradeConfirmationRecord]:
        return [r for r in self._records if r.counterparty_id == counterparty_id]

    def total_pending_notional_gbp(self) -> float:
        return sum(r.notional_gbp for r in self._records if r.is_open)

    def confirmation_rate_pct(self) -> Optional[float]:
        terminal = [r for r in self._records if r.status in _TERMINAL]
        if not self._records:
            return None
        matched = sum(1 for r in terminal if r.status == ConfirmationStatus.MATCHED)
        return round(matched / len(self._records) * 100, 1)

    def confirmation_summary(self, as_of: dt.date) -> str:
        n = len(self._records)
        n_pending = len(self.pending_confirmations())
        n_overdue = len(self.overdue_confirmations(as_of))
        n_disputed = len(self.disputed())
        return (
            "Trade Confirmation Register (" + str(as_of) + "): "
            + str(n) + " trades ("
            + str(n_pending) + " pending, "
            + str(n_overdue) + " overdue, "
            + str(n_disputed) + " disputed)."
        )
