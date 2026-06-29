"""Smart Meter Consumption Reconciliation Book -- Phase Z.

When a customer has a smart meter, the company can compare actual HH reads
against the estimated AQ used for billing. This book records reconciliation
adjustments (credits/debits) and tracks the portfolio exposure.

Real UK context: Suppliers doing 12-monthly bill reconciliation use smart
meter actuals to settle cumulative drift between estimated bills and real usage.
SLC 31A back-billing cap: domestic undercharges older than 12 months are
capped at zero (supplier cannot recover; customer keeps the credit).

All inputs company-observable (estimated AQ from own billing records,
actual reads from DCC/smart meter API). Epistemic-compliant.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Optional


_BACK_BILLING_CAP_DAYS = 365


class ReconciliationType(str, Enum):
    OVERBILLED = "overbilled"
    UNDERBILLED = "underbilled"
    NO_ADJUSTMENT = "no_adjustment"


@dataclass(frozen=True)
class ReconciliationAdjustment:
    """One reconciliation adjustment for a customer billing period.

    Negative credit_debit_gbp means the supplier owes the customer a credit.
    Positive means the customer owes additional charges.
    """
    account_id: str
    period_start: dt.date
    period_end: dt.date
    estimated_kwh: float
    actual_kwh: float
    unit_rate_gbp_per_kwh: float
    reconciliation_type: ReconciliationType
    as_of_date: dt.date
    is_domestic: bool = True

    @property
    def adjustment_kwh(self) -> float:
        return round(self.actual_kwh - self.estimated_kwh, 4)

    @property
    def credit_debit_gbp(self) -> float:
        """Positive = additional charge to customer; negative = credit to customer."""
        return round(self.adjustment_kwh * self.unit_rate_gbp_per_kwh, 2)

    @property
    def is_back_billing_protected(self) -> bool:
        """True if the under-billed period is older than 12 months as of billing date.

        SLC 31A: domestic supplier cannot recover undercharge for energy consumed
        more than 12 months before the billing date.
        """
        if not self.is_domestic:
            return False
        period_age_days = (self.as_of_date - self.period_end).days
        return period_age_days > _BACK_BILLING_CAP_DAYS

    @property
    def recoverable_gbp(self) -> float:
        """Amount the supplier can actually recover.

        If underbilled and back-billing cap applies, supplier cannot recover.
        If overbilled, supplier must always return the credit.
        """
        if self.reconciliation_type == ReconciliationType.NO_ADJUSTMENT:
            return 0.0
        if self.reconciliation_type == ReconciliationType.UNDERBILLED and self.is_back_billing_protected:
            return 0.0
        return self.credit_debit_gbp

    @property
    def is_material(self) -> bool:
        """True when the adjustment exceeds £5 (below which suppliers typically do not bill)."""
        return abs(self.credit_debit_gbp) >= 5.0


def _classify(estimated_kwh: float, actual_kwh: float) -> ReconciliationType:
    diff = actual_kwh - estimated_kwh
    if abs(diff) < 0.01:
        return ReconciliationType.NO_ADJUSTMENT
    return ReconciliationType.UNDERBILLED if diff > 0 else ReconciliationType.OVERBILLED


class SmartMeterReconciliationBook:
    """Records and analyses reconciliation adjustments for smart meter customers.

    Usage::
        book = SmartMeterReconciliationBook()
        adj = book.reconcile(
            account_id="C1",
            period_start=dt.date(2024, 1, 1),
            period_end=dt.date(2024, 12, 31),
            estimated_kwh=3000.0,
            actual_kwh=3400.0,
            unit_rate_gbp_per_kwh=0.285,
            as_of_date=dt.date(2025, 1, 15),
        )
    """

    def __init__(self) -> None:
        self._adjustments: list[ReconciliationAdjustment] = []

    def reconcile(
        self,
        account_id: str,
        period_start: dt.date,
        period_end: dt.date,
        estimated_kwh: float,
        actual_kwh: float,
        unit_rate_gbp_per_kwh: float,
        as_of_date: dt.date,
        is_domestic: bool = True,
    ) -> ReconciliationAdjustment:
        adjustment = ReconciliationAdjustment(
            account_id=account_id,
            period_start=period_start,
            period_end=period_end,
            estimated_kwh=estimated_kwh,
            actual_kwh=actual_kwh,
            unit_rate_gbp_per_kwh=unit_rate_gbp_per_kwh,
            reconciliation_type=_classify(estimated_kwh, actual_kwh),
            as_of_date=as_of_date,
            is_domestic=is_domestic,
        )
        self._adjustments.append(adjustment)
        return adjustment

    def adjustments_for(self, account_id: str) -> list[ReconciliationAdjustment]:
        return [a for a in self._adjustments if a.account_id == account_id]

    def credits_owed_to_customers(self) -> list[ReconciliationAdjustment]:
        """Adjustments where supplier overbilled (owes credit back to customer)."""
        return [a for a in self._adjustments
                if a.reconciliation_type == ReconciliationType.OVERBILLED]

    def charges_owed_by_customers(self) -> list[ReconciliationAdjustment]:
        """Adjustments where customer underbilled (owes additional charge)."""
        return [a for a in self._adjustments
                if a.reconciliation_type == ReconciliationType.UNDERBILLED]

    def back_billing_protected_adjustments(self) -> list[ReconciliationAdjustment]:
        """Undercharges the supplier cannot recover (older than 12 months)."""
        return [a for a in self.charges_owed_by_customers() if a.is_back_billing_protected]

    @property
    def total_credit_exposure_gbp(self) -> float:
        """Total credits supplier must return to customers (positive = liability)."""
        return round(sum(abs(a.credit_debit_gbp) for a in self.credits_owed_to_customers()), 2)

    @property
    def total_recoverable_gbp(self) -> float:
        """Total additional charges supplier can recover from underbilled customers."""
        return round(sum(a.recoverable_gbp for a in self.charges_owed_by_customers()), 2)

    @property
    def total_unrecoverable_gbp(self) -> float:
        """Undercharges that cannot be recovered due to back-billing cap."""
        return round(sum(a.credit_debit_gbp for a in self.back_billing_protected_adjustments()), 2)

    def material_adjustments(self) -> list[ReconciliationAdjustment]:
        return [a for a in self._adjustments if a.is_material]

    def reconciliation_summary(self) -> dict:
        return {
            "total_adjustments": len(self._adjustments),
            "overbilled_count": len(self.credits_owed_to_customers()),
            "underbilled_count": len(self.charges_owed_by_customers()),
            "back_billing_protected_count": len(self.back_billing_protected_adjustments()),
            "total_credit_exposure_gbp": self.total_credit_exposure_gbp,
            "total_recoverable_gbp": self.total_recoverable_gbp,
            "total_unrecoverable_gbp": self.total_unrecoverable_gbp,
            "material_adjustment_count": len(self.material_adjustments()),
        }
