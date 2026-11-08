"""Payment Ledger -- tracks payments with method, outcome, and invoice linkage.

A UK energy supplier maintains a payment ledger separate from the invoice
register. Each payment record carries:
  - Method (DD, PPM, BACS, card, cheque, cash)
  - Outcome (success, failed/returned, pending, reversed)
  - Invoice references (which invoices it settles)

DD failures are a key credit risk metric -- BACS return code R01 means
insufficient funds. PPM customers pre-pay so no payment event is raised
at billing time; their balance is maintained at the meter.

Market-type patterns:
  resi  -- mostly DD (70% UK); PPM ~15%; BACS for larger arrears
  SME   -- BACS or DD; card for occasional top-up
  I&C   -- BACS or CHAPS for high-value settlements
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class PaymentMethodType(str, Enum):
    DIRECT_DEBIT = "direct_debit"
    PREPAYMENT_METER = "prepayment_meter"
    BACS = "bacs"
    CARD = "card"
    CHEQUE = "cheque"
    CASH = "cash"
    CHAPS = "chaps"

    @property
    def is_automated(self) -> bool:
        return self in (PaymentMethodType.DIRECT_DEBIT, PaymentMethodType.PREPAYMENT_METER)

    @property
    def customer_label(self) -> str:
        labels = {
            "direct_debit": "Direct Debit",
            "prepayment_meter": "Prepayment Meter",
            "bacs": "BACS Transfer",
            "card": "Card Payment",
            "cheque": "Cheque",
            "cash": "Cash",
            "chaps": "CHAPS",
        }
        return labels.get(self.value, self.value.replace("_", " ").title())


class PaymentOutcome(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"       # DD returned / card declined
    PENDING = "pending"     # awaiting bank settlement
    REVERSED = "reversed"   # chargeback or DD indemnity claim

    @property
    def is_terminal(self) -> bool:
        return self in (PaymentOutcome.SUCCESS, PaymentOutcome.FAILED, PaymentOutcome.REVERSED)

    @property
    def customer_label(self) -> str:
        labels = {
            "success": "Successful",
            "failed": "Failed",
            "pending": "Pending",
            "reversed": "Reversed",
        }
        return labels.get(self.value, self.value.title())


@dataclass(frozen=True)
class PaymentRecord:
    """A single payment event linked to an account and optionally to invoices."""
    payment_id: str
    account_id: str
    payment_date: str                 # ISO date
    amount_gbp: float
    method: PaymentMethodType
    outcome: PaymentOutcome
    reference: str                    # bank/DD mandate reference
    invoice_numbers: tuple            # invoice numbers this payment covers
    notes: str = ""

    @property
    def is_successful(self) -> bool:
        return self.outcome == PaymentOutcome.SUCCESS

    @property
    def is_failed(self) -> bool:
        return self.outcome == PaymentOutcome.FAILED

    @property
    def is_pending(self) -> bool:
        return self.outcome == PaymentOutcome.PENDING

    @property
    def covers_invoice(self, invoice_number: int) -> bool:
        return invoice_number in self.invoice_numbers


class PaymentLedger:
    """In-memory ledger of payment records for all accounts."""

    def __init__(self) -> None:
        self._records: list[PaymentRecord] = []

    def record(self, rec: PaymentRecord) -> None:
        self._records.append(rec)

    def payments_for_account(self, account_id: str) -> list[PaymentRecord]:
        return [r for r in self._records if r.account_id == account_id]

    def payments_by_date(self, account_id: str) -> list[PaymentRecord]:
        return sorted(
            self.payments_for_account(account_id),
            key=lambda r: r.payment_date,
        )

    def successful_total_gbp(self, account_id: str) -> float:
        return round(sum(
            r.amount_gbp for r in self.payments_for_account(account_id)
            if r.is_successful
        ), 2)

    def failed_payments(self, account_id: str) -> list[PaymentRecord]:
        return [r for r in self.payments_for_account(account_id) if r.is_failed]

    def pending_payments(self, account_id: str) -> list[PaymentRecord]:
        return [r for r in self.payments_for_account(account_id) if r.is_pending]

    def payment_method_breakdown(self, account_id: str) -> dict[str, dict]:
        breakdown: dict[str, dict] = {}
        for r in self.payments_for_account(account_id):
            key = r.method.value
            if key not in breakdown:
                breakdown[key] = {
                    "label": r.method.customer_label,
                    "count": 0,
                    "total_gbp": 0.0,
                    "success": 0,
                    "failed": 0,
                    "pending": 0,
                }
            breakdown[key]["count"] += 1
            breakdown[key]["total_gbp"] = round(
                breakdown[key]["total_gbp"] + r.amount_gbp, 2
            )
            if r.is_successful:
                breakdown[key]["success"] += 1
            elif r.is_failed:
                breakdown[key]["failed"] += 1
            elif r.is_pending:
                breakdown[key]["pending"] += 1
        return breakdown

    def ledger_summary(self, account_id: str, total_billed_gbp: float) -> dict:
        """Account-level ledger summary including balance and method breakdown."""
        paid = self.successful_total_gbp(account_id)
        balance = round(paid - total_billed_gbp, 2)
        recs = self.payments_for_account(account_id)
        return {
            "total_paid_gbp": paid,
            "total_billed_gbp": round(total_billed_gbp, 2),
            "balance_gbp": balance,
            "in_credit": balance > 0,
            "amount_owing_gbp": round(-balance, 2) if balance < 0 else 0.0,
            "payment_count": len(recs),
            "failed_count": len(self.failed_payments(account_id)),
            "pending_count": len(self.pending_payments(account_id)),
            "method_breakdown": self.payment_method_breakdown(account_id),
        }

    def all_accounts(self) -> list[str]:
        return sorted({r.account_id for r in self._records})

    def portfolio_summary(self) -> dict:
        """Portfolio-level payment health metrics."""
        all_recs = self._records
        success = sum(r.amount_gbp for r in all_recs if r.is_successful)
        failed = sum(r.amount_gbp for r in all_recs if r.is_failed)
        pending = sum(r.amount_gbp for r in all_recs if r.is_pending)
        return {
            "total_payment_count": len(all_recs),
            "successful_gbp": round(success, 2),
            "failed_gbp": round(failed, 2),
            "pending_gbp": round(pending, 2),
            "failure_rate_pct": (
                round(len([r for r in all_recs if r.is_failed]) / len(all_recs) * 100, 1)
                if all_recs else 0.0
            ),
            "account_count": len(self.all_accounts()),
        }
