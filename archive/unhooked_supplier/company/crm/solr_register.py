"""Supplier of Last Resort (SoLR) Register: tracks customer transfers from failed suppliers."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class SoLRStatus(str, Enum):
    TRANSFERRED = "transferred"         # customer received, not yet notified
    NOTIFIED = "notified"               # 5-day notification sent
    CONTRACT_OFFERED = "contract_offered"  # 30-day contract offer sent
    CONTRACT_ACCEPTED = "contract_accepted"
    INTEGRATED = "integrated"           # fully onboarded; SoLR period over


_NOTIFICATION_DEADLINE_DAYS = 5      # calendar days post-transfer
_CONTRACT_OFFER_DEADLINE_DAYS = 30   # calendar days post-transfer
_SOLR_BILLING_DAYS = 90              # SVT rate applies for first 90 days


@dataclass(frozen=True)
class SoLRTransferRecord:
    account_id: str
    original_supplier: str
    transfer_date: dt.date
    credit_balance_claimed_gbp: float   # claim against failed supplier estate
    status: SoLRStatus = SoLRStatus.TRANSFERRED
    notification_date: Optional[dt.date] = None
    contract_offer_date: Optional[dt.date] = None
    contract_accepted_date: Optional[dt.date] = None

    def is_notification_overdue(self, as_of: dt.date) -> bool:
        if self.notification_date is not None:
            return False
        return (as_of - self.transfer_date).days > _NOTIFICATION_DEADLINE_DAYS

    def is_contract_offer_overdue(self, as_of: dt.date) -> bool:
        if self.contract_offer_date is not None:
            return False
        if self.status == SoLRStatus.INTEGRATED:
            return False
        return (as_of - self.transfer_date).days > _CONTRACT_OFFER_DEADLINE_DAYS

    def is_in_solr_billing_period(self, as_of: dt.date) -> bool:
        return (as_of - self.transfer_date).days <= _SOLR_BILLING_DAYS


@dataclass(frozen=True)
class SoLRDesignation:
    designation_date: dt.date
    ofgem_direction_ref: str
    failed_supplier_name: str
    customers_transferred: int


class SoLRRegister:
    """Manages customer transfers from failed suppliers.

    Real calibration:
    - Ofgem SoLR mechanism: when a supplier fails, Ofgem designates another licensed
      supplier to take on customers. SoLR supplier is chosen via tender or standing
      arrangement (Ofgem SoLR process last updated March 2019).
    - 2021-22: 28 supplier failures, ~4M customers transferred via SoLR.
      Bulb: 1.7M customers (too large for SoLR; needed Government Administration).
    - SoLR obligations: notify customers within 5 days; offer new contract within 30 days;
      bill at SVT for first 90 days; honour credit balances (recoverable from Ofgem levy).
    - Credit balance shortfall (when failed supplier estate insufficient): recovered via
      mutualisation charge across all suppliers (added to network charges).
    """

    def __init__(self) -> None:
        self._transfers: List[SoLRTransferRecord] = []
        self._designations: List[SoLRDesignation] = []

    def record_designation(self, designation: SoLRDesignation) -> SoLRDesignation:
        self._designations.append(designation)
        return designation

    def record_transfer(self, record: SoLRTransferRecord) -> SoLRTransferRecord:
        self._transfers.append(record)
        return record

    def _update(self, account_id: str, **kwargs) -> SoLRTransferRecord:
        import dataclasses
        for i, r in enumerate(self._transfers):
            if r.account_id == account_id:
                updated = dataclasses.replace(r, **kwargs)
                self._transfers[i] = updated
                return updated
        raise ValueError(f"No SoLR record for {account_id}")

    def notify(self, account_id: str, notification_date: dt.date) -> SoLRTransferRecord:
        return self._update(account_id, status=SoLRStatus.NOTIFIED,
                            notification_date=notification_date)

    def offer_contract(self, account_id: str, offer_date: dt.date) -> SoLRTransferRecord:
        return self._update(account_id, status=SoLRStatus.CONTRACT_OFFERED,
                            contract_offer_date=offer_date)

    def accept_contract(self, account_id: str, accepted_date: dt.date) -> SoLRTransferRecord:
        return self._update(account_id, status=SoLRStatus.CONTRACT_ACCEPTED,
                            contract_accepted_date=accepted_date)

    def integrate(self, account_id: str) -> SoLRTransferRecord:
        return self._update(account_id, status=SoLRStatus.INTEGRATED)

    def active_transfers(self) -> List[SoLRTransferRecord]:
        return [r for r in self._transfers if r.status != SoLRStatus.INTEGRATED]

    def overdue_notifications(self, as_of: dt.date) -> List[SoLRTransferRecord]:
        return [r for r in self._transfers if r.is_notification_overdue(as_of)]

    def overdue_contract_offers(self, as_of: dt.date) -> List[SoLRTransferRecord]:
        return [r for r in self._transfers if r.is_contract_offer_overdue(as_of)]

    def in_solr_billing_period(self, as_of: dt.date) -> List[SoLRTransferRecord]:
        return [r for r in self._transfers if r.is_in_solr_billing_period(as_of)]

    def total_credit_claimed_gbp(self) -> float:
        return round(sum(r.credit_balance_claimed_gbp for r in self._transfers), 2)

    def transfers_from(self, supplier: str) -> List[SoLRTransferRecord]:
        return [r for r in self._transfers if r.original_supplier == supplier]

    def solr_summary(self) -> dict:
        return {
            "total_transferred": len(self._transfers),
            "active": len(self.active_transfers()),
            "designations": len(self._designations),
            "total_credit_claimed_gbp": self.total_credit_claimed_gbp(),
        }
