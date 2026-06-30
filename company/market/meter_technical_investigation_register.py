"""Meter Technical Investigation Register — SLC 21A / GS(SS)5 Schedule 3.

When a customer disputes meter accuracy the supplier must commission a formal
test via the incumbent MOP.  Results determine whether rebilling is required
and whether the £150 customer charge (for electricity) applies.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


# Working-day helper (Monday–Friday, no bank-holiday awareness)
def _add_working_days(date: dt.date, days: int) -> dt.date:
    current = date
    added = 0
    while added < days:
        current += dt.timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    return current


class Fuel(str, Enum):
    ELECTRICITY = "electricity"
    GAS = "gas"


class MeterTestType(str, Enum):
    IN_SITU = "in_situ"               # test at customer premises
    REMOVED_TO_LAB = "removed_to_lab" # meter removed and sent to accredited lab
    CERTIFIED_EXCHANGE = "certified_exchange"  # exchange for certified unit; original tested


class MeterTestOutcome(str, Enum):
    WITHIN_TOLERANCE = "within_tolerance"
    OUTSIDE_TOLERANCE = "outside_tolerance"
    INCONCLUSIVE = "inconclusive"


class MTIStatus(str, Enum):
    PENDING = "pending"            # raised, MOP not yet instructed
    COMMISSIONED = "commissioned"  # MOP instructed; awaiting result
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# SLC 21A: 20 working days from commission to outcome
_SLA_WORKING_DAYS = 20

# Customer charge if meter tests within tolerance (electricity only)
# GS(SS)5 Schedule 3: gas customers are not charged
_ELECTRICITY_WITHIN_TOLERANCE_CHARGE_GBP = 150.0

# Accuracy tolerance thresholds (% variance from nominal)
_TOLERANCE_ELECTRICITY_PCT = 2.5
_TOLERANCE_GAS_PCT = 2.0

_OPEN = frozenset({MTIStatus.PENDING, MTIStatus.COMMISSIONED})


@dataclass(frozen=True)
class MTIRecord:
    """A meter technical investigation (MTI) for a single MPAN/MPRN."""

    reference: str
    account_id: str
    mpan_or_mprn: str
    fuel: Fuel
    test_type: MeterTestType
    status: MTIStatus
    commissioned_date: dt.date
    outcome: Optional[MeterTestOutcome] = None
    outcome_date: Optional[dt.date] = None
    # Signed variance: positive = over-reading, negative = under-reading
    accuracy_variance_pct: Optional[float] = None
    customer_charge_gbp: float = 0.0
    # Days of consumption history that must be rebilled if outside tolerance
    rebill_period_days: int = 0

    @property
    def is_open(self) -> bool:
        return self.status in _OPEN

    @property
    def is_completed(self) -> bool:
        return self.status == MTIStatus.COMPLETED

    @property
    def outcome_due_date(self) -> dt.date:
        return _add_working_days(self.commissioned_date, _SLA_WORKING_DAYS)

    def is_overdue(self, as_of: dt.date) -> bool:
        """COMMISSIONED and past the 20-WD outcome SLA."""
        return self.status == MTIStatus.COMMISSIONED and as_of > self.outcome_due_date

    @property
    def is_within_tolerance(self) -> bool:
        if self.outcome != MeterTestOutcome.WITHIN_TOLERANCE:
            return False
        return True

    @property
    def rebill_required(self) -> bool:
        return self.outcome == MeterTestOutcome.OUTSIDE_TOLERANCE

    def mti_summary(self) -> str:
        parts = [
            f"MTI {self.reference}: {self.account_id} {self.fuel.value} "
            f"{self.test_type.value} [{self.status.value}]"
        ]
        if self.outcome:
            parts.append(f"outcome={self.outcome.value}")
        if self.accuracy_variance_pct is not None:
            parts.append(f"variance={self.accuracy_variance_pct:+.2f}%")
        if self.customer_charge_gbp:
            parts.append(f"charge=£{self.customer_charge_gbp:.2f}")
        return " | ".join(parts)


class MeterTechnicalInvestigationRegister:
    """Register of formal meter accuracy investigations commissioned by the supplier."""

    def __init__(self) -> None:
        self._records: List[MTIRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return "MTI-" + str(self._counter).zfill(5)

    def _update(self, reference: str, **kwargs) -> MTIRecord:
        for i, rec in enumerate(self._records):
            if rec.reference == reference:
                updated = MTIRecord(
                    **{**rec.__dict__, **kwargs}
                )
                self._records[i] = updated
                return updated
        raise KeyError(f"MTI reference not found: {reference}")

    def commission_investigation(
        self,
        account_id: str,
        mpan_or_mprn: str,
        fuel: Fuel,
        test_type: MeterTestType,
        commissioned_date: dt.date,
    ) -> MTIRecord:
        """Raise a new MTI and instruct the MOP to commission the test."""
        ref = self._next_id()
        rec = MTIRecord(
            reference=ref,
            account_id=account_id,
            mpan_or_mprn=mpan_or_mprn,
            fuel=fuel,
            test_type=test_type,
            status=MTIStatus.COMMISSIONED,
            commissioned_date=commissioned_date,
        )
        self._records.append(rec)
        return rec

    def record_outcome(
        self,
        reference: str,
        outcome: MeterTestOutcome,
        outcome_date: dt.date,
        accuracy_variance_pct: float,
        rebill_period_days: int = 0,
    ) -> MTIRecord:
        """Record the test result and compute charges / rebill obligation."""
        rec = next((r for r in self._records if r.reference == reference), None)
        if rec is None:
            raise KeyError(f"MTI reference not found: {reference}")
        if rec.status not in _OPEN:
            raise ValueError(f"Cannot record outcome for {rec.status.value} investigation")

        # Electricity within-tolerance: charge the customer £150
        charge = 0.0
        if rec.fuel == Fuel.ELECTRICITY and outcome == MeterTestOutcome.WITHIN_TOLERANCE:
            charge = _ELECTRICITY_WITHIN_TOLERANCE_CHARGE_GBP

        return self._update(
            reference,
            status=MTIStatus.COMPLETED,
            outcome=outcome,
            outcome_date=outcome_date,
            accuracy_variance_pct=accuracy_variance_pct,
            customer_charge_gbp=charge,
            rebill_period_days=rebill_period_days if outcome == MeterTestOutcome.OUTSIDE_TOLERANCE else 0,
        )

    def cancel(self, reference: str) -> MTIRecord:
        rec = next((r for r in self._records if r.reference == reference), None)
        if rec is None:
            raise KeyError(f"MTI reference not found: {reference}")
        if rec.status not in _OPEN:
            raise ValueError(f"Cannot cancel {rec.status.value} investigation")
        return self._update(reference, status=MTIStatus.CANCELLED)

    # ── Queries ──────────────────────────────────────────────────────────────

    @property
    def all_records(self) -> List[MTIRecord]:
        return list(self._records)

    @property
    def open_investigations(self) -> List[MTIRecord]:
        return [r for r in self._records if r.is_open]

    @property
    def completed_investigations(self) -> List[MTIRecord]:
        return [r for r in self._records if r.is_completed]

    @property
    def rebill_required_investigations(self) -> List[MTIRecord]:
        return [r for r in self._records if r.rebill_required]

    def overdue_investigations(self, as_of: dt.date) -> List[MTIRecord]:
        return [r for r in self._records if r.is_overdue(as_of)]

    def investigations_for_account(self, account_id: str) -> List[MTIRecord]:
        return [r for r in self._records if r.account_id == account_id]

    def investigations_for_mpan(self, mpan_or_mprn: str) -> List[MTIRecord]:
        return [r for r in self._records if r.mpan_or_mprn == mpan_or_mprn]

    def by_fuel(self, fuel: Fuel) -> List[MTIRecord]:
        return [r for r in self._records if r.fuel == fuel]

    def by_test_type(self, test_type: MeterTestType) -> List[MTIRecord]:
        return [r for r in self._records if r.test_type == test_type]

    @property
    def total_customer_charges_gbp(self) -> float:
        """Total charges levied on customers for within-tolerance tests."""
        return sum(r.customer_charge_gbp for r in self._records if r.is_completed)

    def accuracy_dispute_rate_pct(self) -> Optional[float]:
        """Percentage of completed tests that found the meter outside tolerance."""
        completed = self.completed_investigations
        if not completed:
            return None
        outside = sum(1 for r in completed if r.outcome == MeterTestOutcome.OUTSIDE_TOLERANCE)
        return round(outside / len(completed) * 100, 2)

    def mti_register_summary(self, as_of: dt.date) -> str:
        total = len(self._records)
        open_count = len(self.open_investigations)
        overdue = len(self.overdue_investigations(as_of))
        rebill = len(self.rebill_required_investigations)
        charges = self.total_customer_charges_gbp
        rate = self.accuracy_dispute_rate_pct()
        rate_str = f"{rate:.1f}%" if rate is not None else "N/A"
        return (
            f"MTI Register: {total} investigations | {open_count} open "
            f"| {overdue} overdue | {rebill} requiring rebill "
            f"| outside-tolerance rate {rate_str} "
            f"| £{charges:,.2f} customer charges"
        )
