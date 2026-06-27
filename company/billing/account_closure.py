"""Account closure process: final bill, deposit, debt referral under Ofgem SLC 21B."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class ClosureReason(str, Enum):
    CUSTOMER_SWITCH = "customer_switch"       # gained by another supplier
    VACANT_PROPERTY = "vacant_property"       # no new occupant yet
    CUSTOMER_DECEASED = "customer_deceased"   # estate settlement
    BUSINESS_CLOSURE = "business_closure"     # SME ceased trading


class ClosureStatus(str, Enum):
    INITIATED = "initiated"
    FINAL_READ_RECEIVED = "final_read_received"
    FINAL_BILL_ISSUED = "final_bill_issued"
    DEPOSIT_RETURNED = "deposit_returned"     # net_balance <= 0: owe customer money
    DEPOSIT_APPLIED = "deposit_applied"       # net_balance > 0: deposit offset debt
    DEBT_REFERRED = "debt_referred"           # outstanding balance sent to collections
    CLOSED = "closed"


_FINAL_BILL_DEADLINE_DAYS = 42  # Ofgem SLC 21B: 6 weeks


@dataclass(frozen=True)
class AccountClosure:
    account_id: str
    supply_point_id: str
    closure_date: dt.date
    reason: ClosureReason
    status: ClosureStatus
    deposit_held_gbp: float
    debt_balance_gbp: float
    final_read_kwh: Optional[float] = None
    final_bill_gbp: Optional[float] = None

    @property
    def net_balance_gbp(self) -> float:
        bill = self.final_bill_gbp or 0.0
        return round(bill + self.debt_balance_gbp - self.deposit_held_gbp, 2)

    @property
    def requires_debt_referral(self) -> bool:
        return (
            self.net_balance_gbp > 0
            and self.status not in (ClosureStatus.DEBT_REFERRED, ClosureStatus.CLOSED)
        )

    def days_since_closure(self, as_of: dt.date) -> int:
        return (as_of - self.closure_date).days

    def is_final_bill_overdue(self, as_of: dt.date) -> bool:
        return (
            self.final_bill_gbp is None
            and self.days_since_closure(as_of) > _FINAL_BILL_DEADLINE_DAYS
        )


def _update(record: AccountClosure, **kwargs) -> AccountClosure:
    fields = {
        "account_id": record.account_id,
        "supply_point_id": record.supply_point_id,
        "closure_date": record.closure_date,
        "reason": record.reason,
        "status": record.status,
        "deposit_held_gbp": record.deposit_held_gbp,
        "debt_balance_gbp": record.debt_balance_gbp,
        "final_read_kwh": record.final_read_kwh,
        "final_bill_gbp": record.final_bill_gbp,
    }
    fields.update(kwargs)
    return AccountClosure(**fields)


class AccountClosureBook:
    """Manages account closure pipeline: switch/vacancy through to settled or debt-referred.

    Real calibration:
    - Ofgem target: final bill within 42 days of supply end (SLC 21B)
    - Final bill delays were #1 switch complaint category in 2022 Ofgem survey
    - Deposit return mandatory within 14 days of final bill (SLC 12)
    - ~8-12% of closures have a net debt balance at final bill
    - Vacant properties: standing charge continues until de-energised or new supplier
    """

    def __init__(self) -> None:
        self._records: Dict[str, AccountClosure] = {}

    def initiate(
        self,
        account_id: str,
        supply_point_id: str,
        reason: ClosureReason,
        closure_date: dt.date,
        deposit_held_gbp: float = 0.0,
        debt_balance_gbp: float = 0.0,
    ) -> AccountClosure:
        record = AccountClosure(
            account_id=account_id,
            supply_point_id=supply_point_id,
            closure_date=closure_date,
            reason=reason,
            status=ClosureStatus.INITIATED,
            deposit_held_gbp=deposit_held_gbp,
            debt_balance_gbp=debt_balance_gbp,
        )
        self._records[account_id] = record
        return record

    def receive_final_read(self, account_id: str, kwh: float) -> AccountClosure:
        r = _update(
            self._records[account_id],
            final_read_kwh=kwh,
            status=ClosureStatus.FINAL_READ_RECEIVED,
        )
        self._records[account_id] = r
        return r

    def issue_final_bill(self, account_id: str, bill_gbp: float) -> AccountClosure:
        r = _update(
            self._records[account_id],
            final_bill_gbp=bill_gbp,
            status=ClosureStatus.FINAL_BILL_ISSUED,
        )
        self._records[account_id] = r
        return r

    def return_deposit(self, account_id: str) -> AccountClosure:
        r = _update(self._records[account_id], status=ClosureStatus.DEPOSIT_RETURNED)
        self._records[account_id] = r
        return r

    def apply_deposit_to_debt(self, account_id: str) -> AccountClosure:
        r = _update(self._records[account_id], status=ClosureStatus.DEPOSIT_APPLIED)
        self._records[account_id] = r
        return r

    def refer_to_debt_collection(self, account_id: str) -> AccountClosure:
        r = _update(self._records[account_id], status=ClosureStatus.DEBT_REFERRED)
        self._records[account_id] = r
        return r

    def close(self, account_id: str) -> AccountClosure:
        r = _update(self._records[account_id], status=ClosureStatus.CLOSED)
        self._records[account_id] = r
        return r

    def active_closures(self) -> List[AccountClosure]:
        return [r for r in self._records.values() if r.status != ClosureStatus.CLOSED]

    def overdue_final_bills(self, as_of: dt.date) -> List[AccountClosure]:
        return [r for r in self._records.values() if r.is_final_bill_overdue(as_of)]

    def deposits_to_return(self) -> List[AccountClosure]:
        return [r for r in self._records.values() if r.status == ClosureStatus.DEPOSIT_RETURNED]

    def debt_referrals(self) -> List[AccountClosure]:
        return [r for r in self._records.values() if r.status == ClosureStatus.DEBT_REFERRED]

    def requiring_debt_referral(self) -> List[AccountClosure]:
        return [r for r in self._records.values() if r.requires_debt_referral]

    def closure_summary(self) -> dict:
        by_status = {s.value: 0 for s in ClosureStatus}
        for r in self._records.values():
            by_status[r.status.value] += 1
        return {
            "total_closures": len(self._records),
            "active": len(self.active_closures()),
            "overdue_final_bills": len(self.overdue_final_bills(dt.date.today())),
            "deposits_to_return": len(self.deposits_to_return()),
            "debt_referrals": len(self.debt_referrals()),
            "requiring_debt_referral": len(self.requiring_debt_referral()),
            "by_status": by_status,
        }
