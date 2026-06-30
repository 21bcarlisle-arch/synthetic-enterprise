"""Renewal Notice Register (Phase DQ).

Standard Licence Condition 22: Before a fixed-term energy contract expires,
the supplier must send a renewal notice between 42 and 49 days before expiry.
The notice must include:
- The expiry date of the current contract
- Details of the tariff the customer will roll onto (usually SVT/deemed)
- The price of the rollover tariff (unit rate + standing charge)
- Information about the customer's right to switch
- Any exit fees that apply to the current contract

Non-compliance with SLC 22 is actively monitored by Ofgem. In 2022-23,
Ofgem issued enforcement actions against several suppliers for:
- Sending notices too late (inside 42 days)
- Incomplete notices (missing rollover tariff detail)
- Failure to flag the option to switch before expiry

Domestic customers: 42-49 days notice window (mandatory).
I&C customers: notice rules may be contract-specific but SLC 22 still applies.

Epistemic: company knows its own notice obligations and can observe which
customers received notices on time.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class NoticeOutcome(str, Enum):
    PENDING = "pending"           # notice not yet due
    SENT_ON_TIME = "sent_on_time" # within 42-49 day window
    SENT_LATE = "sent_late"       # <42 days = SLC 22 breach
    SENT_EARLY = "sent_early"     # >49 days = technically compliant but sub-optimal
    NOT_REQUIRED = "not_required" # customer switched/closed before notice needed
    FAILED = "failed"             # notice not sent = SLC 22 breach


_NOTICE_MIN_DAYS = 42    # SLC 22 minimum (42 days before expiry)
_NOTICE_MAX_DAYS = 49    # SLC 22 maximum (49 days before expiry)


@dataclass(frozen=True)
class RenewalNoticeRecord:
    account_id: str
    contract_expiry_date: dt.date
    rollover_tariff_name: str
    rollover_unit_rate_pence: float
    rollover_standing_charge_pence: float
    exit_fee_gbp: float
    notice_sent_date: Optional[dt.date]   # None = not yet sent
    outcome: NoticeOutcome
    channel: str = "post"                  # post/email/portal

    @property
    def days_before_expiry(self) -> Optional[int]:
        if self.notice_sent_date is None:
            return None
        return (self.contract_expiry_date - self.notice_sent_date).days

    @property
    def is_compliant(self) -> bool:
        if self.outcome == NoticeOutcome.NOT_REQUIRED:
            return True
        return self.outcome in (NoticeOutcome.SENT_ON_TIME, NoticeOutcome.SENT_EARLY)

    @property
    def is_breach(self) -> bool:
        return self.outcome in (NoticeOutcome.SENT_LATE, NoticeOutcome.FAILED)

    def notice_due_window(self) -> tuple:
        earliest = self.contract_expiry_date - dt.timedelta(days=_NOTICE_MAX_DAYS)
        latest = self.contract_expiry_date - dt.timedelta(days=_NOTICE_MIN_DAYS)
        return earliest, latest


def _classify_outcome(
    notice_sent_date: Optional[dt.date],
    contract_expiry_date: dt.date,
) -> NoticeOutcome:
    if notice_sent_date is None:
        return NoticeOutcome.PENDING
    days_before = (contract_expiry_date - notice_sent_date).days
    if days_before < _NOTICE_MIN_DAYS:
        return NoticeOutcome.SENT_LATE
    if days_before > _NOTICE_MAX_DAYS:
        return NoticeOutcome.SENT_EARLY
    return NoticeOutcome.SENT_ON_TIME


class RenewalNoticeRegister:
    """Tracks SLC 22 renewal notice compliance across the portfolio."""

    def __init__(self) -> None:
        self._records: Dict[str, RenewalNoticeRecord] = {}
        self._seq = 0

    def _next_id(self) -> str:
        self._seq += 1
        return f"RN-{self._seq:04d}"

    def register_contract(
        self,
        account_id: str,
        contract_expiry_date: dt.date,
        rollover_tariff_name: str,
        rollover_unit_rate_pence: float,
        rollover_standing_charge_pence: float,
        exit_fee_gbp: float = 0.0,
        channel: str = "post",
    ) -> RenewalNoticeRecord:
        rec = RenewalNoticeRecord(
            account_id=account_id,
            contract_expiry_date=contract_expiry_date,
            rollover_tariff_name=rollover_tariff_name,
            rollover_unit_rate_pence=rollover_unit_rate_pence,
            rollover_standing_charge_pence=rollover_standing_charge_pence,
            exit_fee_gbp=exit_fee_gbp,
            notice_sent_date=None,
            outcome=NoticeOutcome.PENDING,
            channel=channel,
        )
        self._records[account_id] = rec
        return rec

    def record_notice_sent(
        self, account_id: str, sent_date: dt.date
    ) -> RenewalNoticeRecord:
        rec = self._records[account_id]
        outcome = _classify_outcome(sent_date, rec.contract_expiry_date)
        updated = RenewalNoticeRecord(
            account_id=rec.account_id,
            contract_expiry_date=rec.contract_expiry_date,
            rollover_tariff_name=rec.rollover_tariff_name,
            rollover_unit_rate_pence=rec.rollover_unit_rate_pence,
            rollover_standing_charge_pence=rec.rollover_standing_charge_pence,
            exit_fee_gbp=rec.exit_fee_gbp,
            notice_sent_date=sent_date,
            outcome=outcome,
            channel=rec.channel,
        )
        self._records[account_id] = updated
        return updated

    def mark_not_required(self, account_id: str) -> RenewalNoticeRecord:
        rec = self._records[account_id]
        updated = RenewalNoticeRecord(
            account_id=rec.account_id,
            contract_expiry_date=rec.contract_expiry_date,
            rollover_tariff_name=rec.rollover_tariff_name,
            rollover_unit_rate_pence=rec.rollover_unit_rate_pence,
            rollover_standing_charge_pence=rec.rollover_standing_charge_pence,
            exit_fee_gbp=rec.exit_fee_gbp,
            notice_sent_date=None,
            outcome=NoticeOutcome.NOT_REQUIRED,
            channel=rec.channel,
        )
        self._records[account_id] = updated
        return updated

    def mark_failed(self, account_id: str) -> RenewalNoticeRecord:
        rec = self._records[account_id]
        updated = RenewalNoticeRecord(
            account_id=rec.account_id,
            contract_expiry_date=rec.contract_expiry_date,
            rollover_tariff_name=rec.rollover_tariff_name,
            rollover_unit_rate_pence=rec.rollover_unit_rate_pence,
            rollover_standing_charge_pence=rec.rollover_standing_charge_pence,
            exit_fee_gbp=rec.exit_fee_gbp,
            notice_sent_date=None,
            outcome=NoticeOutcome.FAILED,
            channel=rec.channel,
        )
        self._records[account_id] = updated
        return updated

    def get(self, account_id: str) -> Optional[RenewalNoticeRecord]:
        return self._records.get(account_id)

    def pending(self) -> List[RenewalNoticeRecord]:
        return [r for r in self._records.values() if r.outcome == NoticeOutcome.PENDING]

    def breaches(self) -> List[RenewalNoticeRecord]:
        return [r for r in self._records.values() if r.is_breach]

    def due_for_notice(self, as_of: dt.date) -> List[RenewalNoticeRecord]:
        """Contracts where the notice window starts on or before as_of (not yet sent)."""
        result = []
        for r in self._records.values():
            if r.outcome != NoticeOutcome.PENDING:
                continue
            _, latest = r.notice_due_window()
            earliest, _ = r.notice_due_window()
            if earliest <= as_of:
                result.append(r)
        return result

    def overdue_notice(self, as_of: dt.date) -> List[RenewalNoticeRecord]:
        """Contracts where latest notice date has passed (< 42 days to expiry, not sent)."""
        result = []
        for r in self._records.values():
            if r.outcome != NoticeOutcome.PENDING:
                continue
            _, latest = r.notice_due_window()
            if as_of > latest:
                result.append(r)
        return result

    def compliance_rate(self) -> float:
        total = len(self._records)
        if total == 0:
            return 1.0
        compliant = sum(1 for r in self._records.values() if r.is_compliant)
        return compliant / total

    def notice_register_summary(self) -> str:
        total = len(self._records)
        n_breach = len(self.breaches())
        n_pending = len(self.pending())
        return (
            f"Renewal Notice Register (SLC 22): {total} contracts. "
            f"Pending: {n_pending}. Breaches: {n_breach}. "
            f"Window: {_NOTICE_MIN_DAYS}-{_NOTICE_MAX_DAYS} days before expiry."
        )
