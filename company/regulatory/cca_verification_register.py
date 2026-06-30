"""Climate Change Agreement (CCA) Verification Register (Phase GT).

Climate Change Agreements (CCAs) allow eligible I&C customers in energy-
intensive sectors to claim a 90% reduction in Climate Change Levy (CCL).
Suppliers must verify and record CCA eligibility before applying the
reduced rate on invoices.

Regulatory framework:
  Finance Act 2000 s.30 / Climate Change Levy (General) Regulations 2001
  Environment Agency administers CCAs (delegated from HMRC)
  Sectors: chemicals, metals, paper, food & drink, ceramics, glass, etc.
  4-year target periods: if customer misses target, eligibility suspended
  for 2 years (HMRC may claw back incorrectly applied discounts)

CCA discount:
  Standard CCL domestic/small: 20% CCL (i.e. zero reduction)
  CCA eligible I&C (electricity): 90% discount = pay 10% of CCL rate
  CCA eligible I&C (gas): 92% discount = pay 8% of CCL rate
  Discount confirmed by Environment Agency exemption certificates

Supplier obligation:
  1. Obtain exemption certificate copy from customer annually
  2. Record start/expiry date of certificate
  3. Verify against HMRC exemption lookup (manual check)
  4. Apply CCL exemption code on invoice (E for electricity)
  5. If certificate lapses, revert to full CCL immediately

Distinct from: ccl_ledger.py (CCL charge recording), eco_tracker.py (ECO
obligation), ic_invoice_dispute_register.py (invoice disputes).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

_CCL_ELECTRICITY_DISCOUNT_PCT = 90.0
_CCL_GAS_DISCOUNT_PCT = 92.0
_CERTIFICATE_EXPIRY_WARNING_DAYS = 60


class CCASector(str, Enum):
    CHEMICALS = "chemicals"
    METALS = "metals"
    PAPER_PRINTING = "paper_printing"
    FOOD_DRINK = "food_drink"
    CERAMICS = "ceramics"
    GLASS = "glass"
    TEXTILE = "textile"
    RUBBER_PLASTICS = "rubber_plastics"
    FOUNDRIES = "foundries"
    OTHER = "other"


class CCAStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING_RENEWAL = "pending_renewal"


@dataclass(frozen=True)
class CCAVerificationRecord:
    record_id: str
    account_id: str
    mpan: str
    sector: CCASector
    certificate_ref: str
    valid_from: dt.date
    valid_to: dt.date
    status: CCAStatus = CCAStatus.ACTIVE
    suspension_date: Optional[dt.date] = None
    notes: str = ""

    @property
    def is_active(self) -> bool:
        return self.status == CCAStatus.ACTIVE

    def is_valid_as_of(self, as_of: dt.date) -> bool:
        return (self.status == CCAStatus.ACTIVE
                and self.valid_from <= as_of <= self.valid_to)

    def is_expiring_soon(self, as_of: dt.date) -> bool:
        return (self.is_active
                and (self.valid_to - as_of).days <= _CERTIFICATE_EXPIRY_WARNING_DAYS)

    def electricity_ccl_discount_pct(self) -> float:
        return _CCL_ELECTRICITY_DISCOUNT_PCT if self.is_active else 0.0

    def gas_ccl_discount_pct(self) -> float:
        return _CCL_GAS_DISCOUNT_PCT if self.is_active else 0.0

    def cca_summary(self) -> str:
        return (
            "CCA " + self.record_id + " account=" + self.account_id
            + " sector=" + self.sector.value
            + " cert=" + self.certificate_ref
            + " valid=" + str(self.valid_from) + " to " + str(self.valid_to)
            + " [" + self.status.value + "]"
        )


class CCAVerificationRegister:

    def __init__(self) -> None:
        self._records: List[CCAVerificationRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return "CCA-VER-" + str(self._counter).zfill(5)

    def register_certificate(
        self,
        account_id: str,
        mpan: str,
        sector: CCASector,
        certificate_ref: str,
        valid_from: dt.date,
        valid_to: dt.date,
        notes: str = "",
    ) -> CCAVerificationRecord:
        if valid_to <= valid_from:
            raise ValueError("valid_to must be after valid_from")
        record = CCAVerificationRecord(
            record_id=self._next_id(),
            account_id=account_id, mpan=mpan, sector=sector,
            certificate_ref=certificate_ref,
            valid_from=valid_from, valid_to=valid_to, notes=notes,
        )
        self._records.append(record)
        return record

    def _update(self, record_id: str, **kwargs) -> CCAVerificationRecord:
        for i, r in enumerate(self._records):
            if r.record_id == record_id:
                updated = CCAVerificationRecord(
                    record_id=r.record_id, account_id=r.account_id, mpan=r.mpan,
                    sector=r.sector, certificate_ref=r.certificate_ref,
                    valid_from=r.valid_from, valid_to=r.valid_to,
                    status=kwargs.get("status", r.status),
                    suspension_date=kwargs.get("suspension_date", r.suspension_date),
                    notes=kwargs.get("notes", r.notes),
                )
                self._records[i] = updated
                return updated
        raise KeyError("CCA record " + record_id + " not found")

    def suspend(self, record_id: str, suspension_date: dt.date) -> CCAVerificationRecord:
        return self._update(record_id, status=CCAStatus.SUSPENDED,
                            suspension_date=suspension_date)

    def revoke(self, record_id: str) -> CCAVerificationRecord:
        return self._update(record_id, status=CCAStatus.REVOKED)

    def mark_expired(self, record_id: str) -> CCAVerificationRecord:
        return self._update(record_id, status=CCAStatus.EXPIRED)

    def mark_pending_renewal(self, record_id: str) -> CCAVerificationRecord:
        return self._update(record_id, status=CCAStatus.PENDING_RENEWAL)

    def active_certificates(self) -> List[CCAVerificationRecord]:
        return [r for r in self._records if r.is_active]

    def valid_for_account(self, account_id: str, as_of: dt.date) -> Optional[CCAVerificationRecord]:
        candidates = [r for r in self._records if r.account_id == account_id
                      and r.is_valid_as_of(as_of)]
        if not candidates:
            return None
        return max(candidates, key=lambda r: r.valid_to)

    def expiring_soon(self, as_of: dt.date) -> List[CCAVerificationRecord]:
        return [r for r in self._records if r.is_expiring_soon(as_of)]

    def by_sector(self, sector: CCASector) -> List[CCAVerificationRecord]:
        return [r for r in self._records if r.sector == sector]

    def suspended_certificates(self) -> List[CCAVerificationRecord]:
        return [r for r in self._records if r.status == CCAStatus.SUSPENDED]

    def cca_eligible_mpans(self, as_of: dt.date) -> List[str]:
        return list(dict.fromkeys(
            r.mpan for r in self._records if r.is_valid_as_of(as_of)
        ))

    def cca_register_summary(self, as_of: dt.date) -> str:
        n = len(self._records)
        n_active = len(self.active_certificates())
        n_expiring = len(self.expiring_soon(as_of))
        n_suspended = len(self.suspended_certificates())
        return (
            "CCA Verification Register (" + str(as_of) + "): "
            + str(n) + " certificates ("
            + str(n_active) + " active, "
            + str(n_expiring) + " expiring soon, "
            + str(n_suspended) + " suspended)."
        )
