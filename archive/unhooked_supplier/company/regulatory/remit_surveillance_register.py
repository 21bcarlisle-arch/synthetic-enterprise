"""REMIT Market Abuse Surveillance Register (Phase GF).

Under REMIT Article 15 (UK REMIT Retained Regulation post-Brexit), energy
market participants must have systems and procedures to detect, investigate,
and report potential market abuse:

  - Insider trading: trading on non-public information (e.g. unannounced
    Ofgem enforcement actions, pre-release NESO system status data)
  - Market manipulation: practices intended to move market prices artificially
    (wash trades, spoofing, layering, front-running)

In the UK, REMIT surveillance is overseen jointly by Ofgem and the FCA.
Suspicious transaction reports (STRs) are submitted to ACER (European) or
directly to Ofgem (UK). The supplier's compliance team must:

  1. Maintain a surveillance log of all flagged trading patterns
  2. Investigate each alert within 10 working days
  3. Escalate to senior compliance officer if evidence of manipulation found
  4. Submit STR to Ofgem within a reasonable timeframe (typically 5 working days
     of decision to report)

Distinct from remit_book.py (Phase DC analogue): that covers mandatory
transaction reporting to ACER/Ofgem (the WHAT of trades). This module
covers internal surveillance (the WHY — pattern detection and investigation).

Epistemic: company monitors its own trading records, counterparty data,
and publicly observable market prices (NBP/EPEX). Insider trading detection
relies on cross-referencing trade timing with public announcements.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class MarketAbuseType(str, Enum):
    INSIDER_TRADING = "insider_trading"
    PRICE_MANIPULATION = "price_manipulation"
    WASH_TRADE = "wash_trade"
    FRONT_RUNNING = "front_running"
    LAYERING_SPOOFING = "layering_spoofing"
    SUSPICIOUS_TIMING = "suspicious_timing"


class SurveillanceAlertStatus(str, Enum):
    OPEN = "open"
    UNDER_INVESTIGATION = "under_investigation"
    ESCALATED = "escalated"             # referred to senior compliance
    CLOSED_NO_ACTION = "closed_no_action"
    STR_SUBMITTED = "str_submitted"     # Suspicious Transaction Report to Ofgem


_STR_REQUIRED_TYPES = frozenset({
    MarketAbuseType.INSIDER_TRADING,
    MarketAbuseType.PRICE_MANIPULATION,
    MarketAbuseType.WASH_TRADE,
})


@dataclass(frozen=True)
class SurveillanceAlertRecord:
    alert_id: str                       # REMIT-SURV-NNNNN
    raised_date: dt.date
    abuse_type: MarketAbuseType
    description: str
    related_trade_ids: tuple            # tuple of trade IDs from trade blotter
    status: SurveillanceAlertStatus = SurveillanceAlertStatus.OPEN
    investigation_notes: Optional[str] = None
    str_submitted_date: Optional[dt.date] = None
    closed_date: Optional[dt.date] = None

    @property
    def is_open(self) -> bool:
        return self.status in (
            SurveillanceAlertStatus.OPEN,
            SurveillanceAlertStatus.UNDER_INVESTIGATION,
            SurveillanceAlertStatus.ESCALATED,
        )

    @property
    def is_escalated(self) -> bool:
        return self.status == SurveillanceAlertStatus.ESCALATED

    @property
    def str_submitted(self) -> bool:
        return self.status == SurveillanceAlertStatus.STR_SUBMITTED

    @property
    def potentially_requires_str(self) -> bool:
        return self.abuse_type in _STR_REQUIRED_TYPES

    def days_open(self, as_of: dt.date) -> int:
        if self.closed_date is not None:
            return (self.closed_date - self.raised_date).days
        return (as_of - self.raised_date).days

    def alert_summary(self) -> str:
        return (
            f"REMIT Alert {self.alert_id} ({self.abuse_type.value}): "
            f"{self.status.value} raised={self.raised_date} "
            f"trades={len(self.related_trade_ids)}"
        )


class REMITSurveillanceRegister:

    def __init__(self) -> None:
        self._records: List[SurveillanceAlertRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return f"REMIT-SURV-{self._counter:05d}"

    def raise_alert(
        self,
        raised_date: dt.date,
        abuse_type: MarketAbuseType,
        description: str,
        related_trade_ids: tuple = (),
    ) -> SurveillanceAlertRecord:
        record = SurveillanceAlertRecord(
            alert_id=self._next_id(),
            raised_date=raised_date,
            abuse_type=abuse_type,
            description=description,
            related_trade_ids=related_trade_ids,
        )
        self._records.append(record)
        return record

    def _update(self, alert_id: str, **kwargs) -> SurveillanceAlertRecord:
        for i, r in enumerate(self._records):
            if r.alert_id == alert_id:
                updated = SurveillanceAlertRecord(
                    alert_id=r.alert_id,
                    raised_date=r.raised_date,
                    abuse_type=r.abuse_type,
                    description=r.description,
                    related_trade_ids=r.related_trade_ids,
                    status=kwargs.get("status", r.status),
                    investigation_notes=kwargs.get("investigation_notes", r.investigation_notes),
                    str_submitted_date=kwargs.get("str_submitted_date", r.str_submitted_date),
                    closed_date=kwargs.get("closed_date", r.closed_date),
                )
                self._records[i] = updated
                return updated
        raise KeyError(f"Surveillance alert {alert_id} not found")

    def commence_investigation(
        self, alert_id: str, notes: str = ""
    ) -> SurveillanceAlertRecord:
        return self._update(
            alert_id,
            status=SurveillanceAlertStatus.UNDER_INVESTIGATION,
            investigation_notes=notes,
        )

    def escalate(self, alert_id: str) -> SurveillanceAlertRecord:
        return self._update(alert_id, status=SurveillanceAlertStatus.ESCALATED)

    def close_no_action(
        self, alert_id: str, closed_date: dt.date
    ) -> SurveillanceAlertRecord:
        return self._update(
            alert_id,
            status=SurveillanceAlertStatus.CLOSED_NO_ACTION,
            closed_date=closed_date,
        )

    def submit_str(
        self, alert_id: str, submitted_date: dt.date
    ) -> SurveillanceAlertRecord:
        return self._update(
            alert_id,
            status=SurveillanceAlertStatus.STR_SUBMITTED,
            str_submitted_date=submitted_date,
        )

    def open_alerts(self) -> List[SurveillanceAlertRecord]:
        return [r for r in self._records if r.is_open]

    def escalated_alerts(self) -> List[SurveillanceAlertRecord]:
        return [r for r in self._records if r.is_escalated]

    def str_submitted_alerts(self) -> List[SurveillanceAlertRecord]:
        return [r for r in self._records if r.str_submitted]

    def by_type(self, abuse_type: MarketAbuseType) -> List[SurveillanceAlertRecord]:
        return [r for r in self._records if r.abuse_type == abuse_type]

    def potential_str_required(self) -> List[SurveillanceAlertRecord]:
        return [r for r in self._records if r.is_open and r.potentially_requires_str]

    def long_open_alerts(
        self, as_of: dt.date, days_threshold: int = 10
    ) -> List[SurveillanceAlertRecord]:
        return [
            r for r in self._records
            if r.is_open and r.days_open(as_of) > days_threshold
        ]

    def surveillance_summary(self, as_of: dt.date) -> str:
        n = len(self._records)
        n_open = len(self.open_alerts())
        n_esc = len(self.escalated_alerts())
        n_str = len(self.str_submitted_alerts())
        n_overdue = len(self.long_open_alerts(as_of))
        return (
            f"REMIT Surveillance Register ({as_of}): {n} alerts "
            f"({n_open} open, {n_esc} escalated, {n_str} STR submitted, "
            f"{n_overdue} open>{10}d)."
        )
