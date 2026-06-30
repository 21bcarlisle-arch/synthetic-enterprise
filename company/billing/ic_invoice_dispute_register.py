"""I&C Invoice Dispute Register (Phase GE).

Distinct from domestic billing disputes (Phase FC billing_dispute.py):
- No 8-week SLC 18.9 deadline; governed by commercial contract law
- Disputed amounts typically GBP10k-GBP10M; independent meter audit available
- Resolution: supplier review / NICC audit / GEMA arbitration / commercial court
"""
from __future__ import annotations
import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

class ICDisputeType(str, Enum):
    VOLUME = "volume"
    PRICING = "pricing"
    METER_ACCURACY = "meter_accuracy"
    CONTRACT_BREACH = "contract_breach"
    SETTLEMENT_ERROR = "settlement_error"
    PASS_THROUGH = "pass_through"

class ICResolutionMethod(str, Enum):
    SUPPLIER_REVIEW = "supplier_review"
    INDEPENDENT_METER_AUDIT = "independent_meter_audit"
    AGREED_SETTLEMENT = "agreed_settlement"
    GEMA_ARBITRATION = "gema_arbitration"
    COMMERCIAL_COURT = "commercial_court"

class ICDisputeStatus(str, Enum):
    RAISED = "raised"
    UNDER_REVIEW = "under_review"
    AUDIT_COMMISSIONED = "audit_commissioned"
    AGREED_SETTLEMENT = "agreed_settlement"
    RESOLVED = "resolved"
    ESCALATED_GEMA = "escalated_gema"
    ESCALATED_COURT = "escalated_court"
    WITHDRAWN = "withdrawn"

_OPEN = frozenset({ICDisputeStatus.RAISED, ICDisputeStatus.UNDER_REVIEW, ICDisputeStatus.AUDIT_COMMISSIONED})
_ESCALATED = frozenset({ICDisputeStatus.ESCALATED_GEMA, ICDisputeStatus.ESCALATED_COURT})
_TERMINAL = frozenset({ICDisputeStatus.RESOLVED, ICDisputeStatus.WITHDRAWN, ICDisputeStatus.AGREED_SETTLEMENT})

@dataclass(frozen=True)
class ICInvoiceDisputeRecord:
    dispute_id: str
    account_id: str
    raised_date: dt.date
    invoice_ref: str
    disputed_amount_gbp: float
    dispute_type: ICDisputeType
    status: ICDisputeStatus = ICDisputeStatus.RAISED
    resolution_method: Optional[ICResolutionMethod] = None
    resolved_date: Optional[dt.date] = None
    credit_issued_gbp: float = 0.0

    @property
    def is_open(self): return self.status in _OPEN
    @property
    def is_escalated(self): return self.status in _ESCALATED
    @property
    def is_resolved(self): return self.status in _TERMINAL
    @property
    def requires_external_resolution(self):
        return self.status in (ICDisputeStatus.ESCALATED_GEMA, ICDisputeStatus.ESCALATED_COURT, ICDisputeStatus.AUDIT_COMMISSIONED)
    def days_open(self, as_of: dt.date) -> int:
        if self.resolved_date is not None: return (self.resolved_date - self.raised_date).days
        return (as_of - self.raised_date).days
    def dispute_summary(self) -> str:
        return (f"I&C Dispute {self.dispute_id} ({self.dispute_type.value}): "
                f"GBP{self.disputed_amount_gbp:,.2f} [{self.status.value}] acct={self.account_id}")

class ICInvoiceDisputeRegister:
    def __init__(self):
        self._records: List[ICInvoiceDisputeRecord] = []
        self._counter: int = 0
    def _next_id(self):
        self._counter += 1; return f"ICDISP-{self._counter:05d}"
    def raise_dispute(self, account_id, raised_date, invoice_ref, disputed_amount_gbp, dispute_type):
        if disputed_amount_gbp <= 0: raise ValueError(f"disputed_amount_gbp must be positive; got {disputed_amount_gbp}")
        r = ICInvoiceDisputeRecord(dispute_id=self._next_id(), account_id=account_id, raised_date=raised_date,
            invoice_ref=invoice_ref, disputed_amount_gbp=disputed_amount_gbp, dispute_type=dispute_type)
        self._records.append(r); return r
    def _update(self, dispute_id, **kwargs):
        for i, r in enumerate(self._records):
            if r.dispute_id == dispute_id:
                u = ICInvoiceDisputeRecord(dispute_id=r.dispute_id, account_id=r.account_id,
                    raised_date=r.raised_date, invoice_ref=r.invoice_ref,
                    disputed_amount_gbp=r.disputed_amount_gbp, dispute_type=r.dispute_type,
                    status=kwargs.get("status", r.status),
                    resolution_method=kwargs.get("resolution_method", r.resolution_method),
                    resolved_date=kwargs.get("resolved_date", r.resolved_date),
                    credit_issued_gbp=kwargs.get("credit_issued_gbp", r.credit_issued_gbp))
                self._records[i] = u; return u
        raise KeyError(f"I&C dispute {dispute_id} not found")
    def commence_review(self, did): return self._update(did, status=ICDisputeStatus.UNDER_REVIEW)
    def commission_audit(self, did): return self._update(did, status=ICDisputeStatus.AUDIT_COMMISSIONED, resolution_method=ICResolutionMethod.INDEPENDENT_METER_AUDIT)
    def resolve(self, did, resolved_date, resolution_method, credit_issued_gbp=0.0):
        return self._update(did, status=ICDisputeStatus.RESOLVED, resolved_date=resolved_date, resolution_method=resolution_method, credit_issued_gbp=credit_issued_gbp)
    def agree_settlement(self, did, resolved_date, credit_issued_gbp):
        return self._update(did, status=ICDisputeStatus.AGREED_SETTLEMENT, resolved_date=resolved_date, resolution_method=ICResolutionMethod.AGREED_SETTLEMENT, credit_issued_gbp=credit_issued_gbp)
    def escalate_gema(self, did): return self._update(did, status=ICDisputeStatus.ESCALATED_GEMA, resolution_method=ICResolutionMethod.GEMA_ARBITRATION)
    def escalate_court(self, did): return self._update(did, status=ICDisputeStatus.ESCALATED_COURT, resolution_method=ICResolutionMethod.COMMERCIAL_COURT)
    def withdraw(self, did): return self._update(did, status=ICDisputeStatus.WITHDRAWN)
    def open_disputes(self): return [r for r in self._records if r.is_open]
    def escalated_disputes(self): return [r for r in self._records if r.is_escalated]
    def disputes_for_account(self, acct): return [r for r in self._records if r.account_id == acct]
    def by_type(self, t): return [r for r in self._records if r.dispute_type == t]
    def total_disputed_gbp(self): return sum(r.disputed_amount_gbp for r in self._records if r.is_open or r.is_escalated)
    def total_credits_issued_gbp(self): return sum(r.credit_issued_gbp for r in self._records)
    def long_running_disputes(self, as_of, days_threshold=90):
        return [r for r in self._records if (r.is_open or r.is_escalated) and r.days_open(as_of) > days_threshold]
    def dispute_register_summary(self, as_of):
        n=len(self._records); n_open=len(self.open_disputes()); n_esc=len(self.escalated_disputes())
        total=self.total_disputed_gbp(); credits=self.total_credits_issued_gbp()
        return (f"I&C Invoice Dispute Register ({as_of}): {n} disputes ({n_open} open, {n_esc} escalated). Disputed: GBP{total:,.2f}. Credits issued: GBP{credits:,.2f}.")
