"""Non/partial-payment physics — one engine, segment-parameterised. M2 (D5).

Sits on top of company/billing/account_ledger.py (the model-agnostic event
stream) and drives the collections lifecycle identically for both accounting
models:

  1. AGEING — 30 / 60 / 90+ day buckets over undisputed outstanding. Balance-based
     accounts age their rolling arrears from the oldest unpaid bill; open-item
     accounts age each undisputed open invoice by its own due date. Disputed
     invoices are EXCLUDED from ageing while held (they don't dun, don't accrue
     statutory interest) — the same rule the I&C dispute register already encodes.
  2. DUNNING — segment-specific step sequences (a resi path bounded by Ofgem SLC
     27 ability-to-pay duties; a B2B path that escalates to commercial recovery).
  3. STATUTORY LATE-PAYMENT INTEREST — B2B ONLY, under the Late Payment of
     Commercial Debts (Interest) Act 1998: 8 percentage points above the Bank of
     England base rate, plus fixed compensation (£40/£70/£100 by debt size).
     Residential debt accrues NO statutory interest. Anchors:
     docs/market_research/account_hierarchy_payment_allocation.md.
  4. WRITE-OFFS — dated, reasoned, P&L-visible ledger events (WRITE_OFF_CREDIT),
     never a silent status flip.

Epistemic wall: arrears, dunning steps, statutory interest and write-offs are all
the supplier's own operational actions and published statute. No sim internals.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Sequence

from company.billing.account_ledger import (
    AccountLedger,
    LedgerEvent,
    LedgerEventType,
)
from company.crm.account_hierarchy import Segment


# ---------------------------------------------------------------------------
# 1. Ageing
# ---------------------------------------------------------------------------

AGE_BUCKETS = ("current", "30-60", "60-90", "90+")


def age_bucket(days_overdue: int) -> str:
    """30 / 60 / 90+ day ageing. days_overdue is days PAST the due date."""
    if days_overdue >= 90:
        return "90+"
    if days_overdue >= 60:
        return "60-90"
    if days_overdue >= 30:
        return "30-60"
    return "current"


@dataclass(frozen=True)
class AgedItem:
    reference: str          # invoice_ref (open-item) or account_id (balance-based)
    outstanding_gbp: float
    due_date: dt.date
    days_overdue: int
    disputed: bool = False

    @property
    def bucket(self) -> str:
        return age_bucket(self.days_overdue)


def age_open_items(
    ledger: AccountLedger,
    as_of: dt.date,
    payment_terms_days: int = 14,
    disputed_refs: Sequence[str] = (),
) -> List[AgedItem]:
    """Open-item ageing: one AgedItem per undisputed open invoice, aged from its
    due date (issue_date + payment_terms_days). Disputed invoices are returned
    with disputed=True but callers exclude them from ageing/dunning."""
    alloc = ledger.allocate(disputed_refs=disputed_refs, as_of=as_of)
    items: List[AgedItem] = []
    for oi in alloc.open_items:
        if oi.is_settled:
            continue
        due = oi.issue_date + dt.timedelta(days=payment_terms_days)
        days = (as_of - due).days
        items.append(AgedItem(
            reference=oi.invoice_ref,
            outstanding_gbp=oi.outstanding_gbp,
            due_date=due,
            days_overdue=max(0, days),
            disputed=oi.disputed,
        ))
    return items


def age_balance(
    ledger: AccountLedger,
    as_of: dt.date,
    payment_terms_days: int = 14,
) -> Optional[AgedItem]:
    """Balance-based ageing: the whole positive rolling balance, aged from the
    OLDEST unpaid bill's due date (FIFO — payments reduce the oldest debt first,
    which is what a rolling balance implies). Returns None if not in arrears."""
    bal = ledger.balance(as_of)
    if bal <= 0.005:
        return None
    # oldest bill debit still 'covered' by the outstanding balance
    bill_dates = sorted(
        e.valid_time for e in ledger.events()
        if e.event_type == LedgerEventType.BILL_DEBIT and e.valid_time <= as_of
    )
    oldest = bill_dates[0] if bill_dates else as_of
    due = oldest + dt.timedelta(days=payment_terms_days)
    days = (as_of - due).days
    return AgedItem(
        reference=ledger.account_id,
        outstanding_gbp=round(bal, 2),
        due_date=due,
        days_overdue=max(0, days),
        disputed=False,
    )


def ageing_buckets(items: Sequence[AgedItem]) -> Dict[str, Dict[str, float]]:
    """Aggregate AgedItems into 30/60/90+ buckets, EXCLUDING disputed items."""
    buckets: Dict[str, Dict[str, float]] = {
        b: {"count": 0, "amount_gbp": 0.0} for b in AGE_BUCKETS
    }
    for it in items:
        if it.disputed:
            continue
        b = buckets[it.bucket]
        b["count"] += 1
        b["amount_gbp"] = round(b["amount_gbp"] + it.outstanding_gbp, 2)
    return buckets


# ---------------------------------------------------------------------------
# 2. Dunning (segment-parameterised)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DunningStep:
    trigger_days_overdue: int
    action: str
    channel: str


# Resi/micro-SME: Ofgem SLC 27 (ability-to-pay) shapes the path — reminder,
# then a proactive contact / repayment-plan offer BEFORE any enforcement, and no
# statutory interest. B2B: commercial recovery, faster, interest-bearing.
_DUNNING_PATHS: Dict[Segment, List[DunningStep]] = {
    Segment.RESIDENTIAL: [
        DunningStep(0, "reminder", "email/sms"),
        DunningStep(14, "reminder_2", "letter"),
        DunningStep(28, "repayment_plan_offer", "phone/letter"),   # SLC 27 ability-to-pay
        DunningStep(56, "final_notice", "letter"),
        DunningStep(90, "prepayment_or_debt_agency", "field/agency"),
    ],
    Segment.MICRO_SME: [
        DunningStep(0, "reminder", "email"),
        DunningStep(14, "reminder_2", "email/phone"),
        DunningStep(28, "repayment_plan_offer", "phone"),
        DunningStep(56, "final_notice", "letter"),
        DunningStep(75, "disconnection_warning_or_agency", "letter/agency"),
    ],
    Segment.SME: [
        DunningStep(0, "reminder", "email"),
        DunningStep(7, "statement_of_account", "email"),
        DunningStep(30, "interest_notice", "letter"),               # LPCDA notice
        DunningStep(45, "final_demand", "letter"),
        DunningStep(60, "debt_recovery", "agency/legal"),
    ],
    Segment.IC: [
        DunningStep(0, "reminder", "email/account_manager"),
        DunningStep(7, "interest_notice", "letter"),                # LPCDA notice
        DunningStep(21, "final_demand", "letter/legal"),
        DunningStep(35, "commercial_recovery", "legal"),
    ],
}


def dunning_path(segment: Segment) -> List[DunningStep]:
    return list(_DUNNING_PATHS[segment])


def current_dunning_step(segment: Segment, days_overdue: int) -> Optional[DunningStep]:
    """The furthest dunning step whose trigger has been reached. None if not yet
    overdue enough to dun."""
    step: Optional[DunningStep] = None
    for s in _DUNNING_PATHS[segment]:
        if days_overdue >= s.trigger_days_overdue:
            step = s
        else:
            break
    return step


# ---------------------------------------------------------------------------
# 3. Statutory late-payment interest — B2B ONLY (LPCDA 1998)
# ---------------------------------------------------------------------------

LPCDA_MARGIN = 0.08  # 8 percentage points above BoE base rate


def lpcda_fixed_compensation_gbp(debt_gbp: float) -> float:
    """Fixed sum recoverable under s.5A LPCDA 1998, by debt size band."""
    if debt_gbp < 1000:
        return 40.0
    if debt_gbp < 10000:
        return 70.0
    return 100.0


def statutory_interest_gbp(
    segment: Segment,
    principal_gbp: float,
    days_late: int,
    boe_base_rate: float,
    include_fixed_compensation: bool = True,
) -> float:
    """Late-payment interest under the Late Payment of Commercial Debts (Interest)
    Act 1998. B2B ONLY — residential debt returns 0.0 (no statutory interest on
    domestic energy arrears). Simple interest at (BoE base + 8%) pro-rata by days,
    plus the fixed statutory compensation. days_late/principal <= 0 ⇒ 0.0."""
    if not segment.is_business:
        return 0.0
    if principal_gbp <= 0 or days_late <= 0:
        return 0.0
    annual_rate = boe_base_rate + LPCDA_MARGIN
    interest = principal_gbp * annual_rate * (days_late / 365.0)
    if include_fixed_compensation:
        interest += lpcda_fixed_compensation_gbp(principal_gbp)
    return round(interest, 2)


def build_interest_event(
    account_id: str,
    segment: Segment,
    principal_gbp: float,
    days_late: int,
    boe_base_rate: float,
    as_of: dt.date,
    transaction_time: dt.datetime,
    invoice_ref: Optional[str] = None,
    event_id: Optional[str] = None,
) -> Optional[LedgerEvent]:
    """Produce an INTEREST_DEBIT LedgerEvent for B2B late interest, or None if not
    applicable (residential, or nothing due). The event feeds the SAME ledger."""
    amount = statutory_interest_gbp(segment, principal_gbp, days_late, boe_base_rate)
    if amount <= 0:
        return None
    eid = event_id or f"INT-{account_id}-{invoice_ref or 'BAL'}-{as_of.isoformat()}"
    return LedgerEvent(
        event_id=eid,
        account_id=account_id,
        event_type=LedgerEventType.INTEREST_DEBIT,
        amount_gbp=amount,
        valid_time=as_of,
        transaction_time=transaction_time,
        invoice_ref=invoice_ref,
        reason=(
            f"LPCDA 1998 statutory interest: {days_late}d @ "
            f"{(boe_base_rate + LPCDA_MARGIN) * 100:.2f}% + fixed compensation"
        ),
    )


# ---------------------------------------------------------------------------
# 4. Write-offs — dated, reasoned, P&L-visible
# ---------------------------------------------------------------------------

class WriteOffReason(str, Enum):
    GONE_AWAY = "gone_away"                  # customer untraceable
    INSOLVENCY = "insolvency"                # bankruptcy / liquidation
    DECEASED_NO_ESTATE = "deceased_no_estate"
    UNECONOMIC_TO_PURSUE = "uneconomic_to_pursue"
    STATUTE_BARRED = "statute_barred"        # >6y, Limitation Act 1980
    GOODWILL = "goodwill"


def build_write_off_event(
    account_id: str,
    amount_gbp: float,
    reason: WriteOffReason,
    as_of: dt.date,
    transaction_time: dt.datetime,
    invoice_ref: Optional[str] = None,
    event_id: Optional[str] = None,
    note: str = "",
) -> LedgerEvent:
    """Produce a WRITE_OFF_CREDIT LedgerEvent. A write-off is a P&L expense the
    moment it posts (affects_pnl=True on the event) and is fully audited (dated +
    reasoned) — never a silent status change."""
    if amount_gbp <= 0:
        raise ValueError("write-off amount must be positive")
    eid = event_id or f"WO-{account_id}-{invoice_ref or 'BAL'}-{as_of.isoformat()}"
    detail = f"write-off ({reason.value})" + (f": {note}" if note else "")
    return LedgerEvent(
        event_id=eid,
        account_id=account_id,
        event_type=LedgerEventType.WRITE_OFF_CREDIT,
        amount_gbp=round(amount_gbp, 2),
        valid_time=as_of,
        transaction_time=transaction_time,
        invoice_ref=invoice_ref,
        reason=detail,
    )


# ---------------------------------------------------------------------------
# Account-level collections snapshot
# ---------------------------------------------------------------------------

def collections_snapshot(
    ledger: AccountLedger,
    segment: Segment,
    accounting_model_is_open_item: bool,
    as_of: dt.date,
    payment_terms_days: int = 14,
    disputed_refs: Sequence[str] = (),
) -> dict:
    """One collections view over either accounting model. Returns ageing buckets,
    the current dunning step, and the undisputed overdue total that would bear
    statutory interest (B2B)."""
    if accounting_model_is_open_item:
        items = age_open_items(ledger, as_of, payment_terms_days, disputed_refs)
    else:
        one = age_balance(ledger, as_of, payment_terms_days)
        items = [one] if one is not None else []

    undisputed = [it for it in items if not it.disputed]
    max_overdue = max((it.days_overdue for it in undisputed), default=0)
    total_undisputed_overdue = round(
        sum(it.outstanding_gbp for it in undisputed if it.days_overdue > 0), 2
    )
    step = current_dunning_step(segment, max_overdue)
    return {
        "account_id": ledger.account_id,
        "segment": segment.value,
        "accounting_model": "open_item" if accounting_model_is_open_item else "balance_based",
        "as_of": as_of.isoformat(),
        "ageing": ageing_buckets(items),
        "undisputed_overdue_gbp": total_undisputed_overdue,
        "disputed_excluded_count": sum(1 for it in items if it.disputed),
        "max_days_overdue": max_overdue,
        "dunning_action": step.action if step else None,
        "dunning_channel": step.channel if step else None,
        "interest_bearing": segment.is_business,
    }
