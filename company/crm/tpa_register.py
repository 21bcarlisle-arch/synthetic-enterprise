"""Third Party Authority (TPA) Register: customer-designated account representatives."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class TPAScope(str, Enum):
    VIEW_ONLY = "view_only"             # see bills, usage, account status
    BILLING_MANAGEMENT = "billing_management"  # change payment methods, plans
    FULL_AUTHORITY = "full_authority"    # all actions including tariff switch


class TPARelationship(str, Enum):
    CARER = "carer"
    FAMILY_MEMBER = "family_member"
    ENERGY_ADVISOR = "energy_advisor"    # e.g. Citizens Advice, StepChange
    DEBT_CHARITY = "debt_charity"
    SOLICITOR = "solicitor"
    POWER_OF_ATTORNEY = "power_of_attorney"
    LANDLORD = "landlord"


class TPAStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"    # customer withdrew authority


@dataclass(frozen=True)
class TPARecord:
    account_id: str
    tpa_reference: str
    relationship: TPARelationship
    scope: TPAScope
    granted_date: dt.date
    expiry_date: Optional[dt.date]      # None = indefinite
    tpa_name: str
    contact_email: str = ""
    status: TPAStatus = TPAStatus.ACTIVE

    def is_active(self, as_of: dt.date) -> bool:
        if self.status != TPAStatus.ACTIVE:
            return False
        if self.expiry_date is not None and as_of > self.expiry_date:
            return False
        return True

    def has_billing_access(self, as_of: dt.date) -> bool:
        return self.is_active(as_of) and self.scope in (
            TPAScope.BILLING_MANAGEMENT, TPAScope.FULL_AUTHORITY
        )

    def has_full_authority(self, as_of: dt.date) -> bool:
        return self.is_active(as_of) and self.scope == TPAScope.FULL_AUTHORITY


class TPARegister:
    """Tracks third-party authorities across the customer portfolio.

    Real calibration:
    - Ofgem Consumer Standards / Consumer Duty: suppliers must respect designated TPAs.
    - Citizens Advice Bureau and StepChange are the most common energy TPAs for
      debt management and vulnerable customer support.
    - Power of Attorney (Lasting or Ordinary): legally binding; must be accepted.
    - Landlord authority: common for bill-inclusive tenancies.
    - Ofgem enforcement: refusing to communicate with a designated TPA = SLC breach.
    - Data protection: TPA access must be logged; GDPR Article 6 lawful basis.
    """

    def __init__(self) -> None:
        self._records: List[TPARecord] = []

    def grant_authority(self, record: TPARecord) -> TPARecord:
        self._records.append(record)
        return record

    def _update(self, tpa_reference: str, **kwargs) -> TPARecord:
        import dataclasses
        for i, r in enumerate(self._records):
            if r.tpa_reference == tpa_reference:
                updated = dataclasses.replace(r, **kwargs)
                self._records[i] = updated
                return updated
        raise ValueError(f"TPA not found: {tpa_reference}")

    def revoke(self, tpa_reference: str) -> TPARecord:
        return self._update(tpa_reference, status=TPAStatus.REVOKED)

    def expire(self, tpa_reference: str) -> TPARecord:
        return self._update(tpa_reference, status=TPAStatus.EXPIRED)

    def active_tpas_for_account(self, account_id: str, as_of: dt.date) -> List[TPARecord]:
        return [r for r in self._records
                if r.account_id == account_id and r.is_active(as_of)]

    def all_active_tpas(self, as_of: dt.date) -> List[TPARecord]:
        return [r for r in self._records if r.is_active(as_of)]

    def expiring_soon(self, as_of: dt.date, within_days: int = 30) -> List[TPARecord]:
        cutoff = as_of + dt.timedelta(days=within_days)
        return [r for r in self._records
                if r.is_active(as_of)
                and r.expiry_date is not None
                and r.expiry_date <= cutoff]

    def power_of_attorney_accounts(self, as_of: dt.date) -> List[str]:
        return list({r.account_id for r in self._records
                     if r.is_active(as_of)
                     and r.relationship == TPARelationship.POWER_OF_ATTORNEY})

    def tpa_summary(self, as_of: dt.date) -> dict:
        active = self.all_active_tpas(as_of)
        return {
            "total_records": len(self._records),
            "active": len(active),
            "full_authority": sum(1 for r in active if r.has_full_authority(as_of)),
            "power_of_attorney": len(self.power_of_attorney_accounts(as_of)),
        }
