"""Licence Application and Variation Register.

UK energy suppliers hold licences granted by Ofgem under:
- Gas Act 1986 (gas supply licence)
- Electricity Act 1989 (electricity supply licence)

Licence types:
- Domestic (Tier 1/2 based on customer count)
- Non-domestic (I&C, SME)
- Combined (most suppliers hold all)

Licence variations are needed when:
- Adding new supply categories (e.g., domestic to non-domestic)
- Material changes to business model (new financial arrangements)
- Change of control (ownership change)
- Geographic scope changes

Ofgem may impose Special Conditions (SpC) on individual suppliers
beyond the Standard Licence Conditions (SLC).

Post-2022: Ofgem requires explicit application for licence continuation
when financial resilience deteriorates.

Epistemic: licence status and application outcomes are known to the company.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from enum import Enum


class LicenceType(str, Enum):
    ELECTRICITY_DOMESTIC = "electricity_domestic"
    ELECTRICITY_NON_DOMESTIC = "electricity_non_domestic"
    GAS_DOMESTIC = "gas_domestic"
    GAS_NON_DOMESTIC = "gas_non_domestic"


class LicenceTier(str, Enum):
    TIER_1 = "tier_1"   # <250,000 domestic customers
    TIER_2 = "tier_2"   # >=250,000 domestic customers


class ApplicationStatus(str, Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class VariationReason(str, Enum):
    NEW_CATEGORY = "new_category"
    CHANGE_OF_CONTROL = "change_of_control"
    FINANCIAL_CONDITION = "financial_condition"
    GEOGRAPHIC_EXPANSION = "geographic_expansion"
    SPECIAL_CONDITION = "special_condition"


@dataclass(frozen=True)
class LicenceRecord:
    licence_id: str
    licence_type: LicenceType
    tier: LicenceTier
    grant_date: date
    is_active: bool = True
    special_conditions: tuple[str, ...] = ()

    @property
    def has_special_conditions(self) -> bool:
        return len(self.special_conditions) > 0


@dataclass(frozen=True)
class LicenceApplication:
    application_id: str
    licence_type: LicenceType
    application_date: date
    reason: VariationReason
    status: ApplicationStatus
    decision_date: date | None = None

    @property
    def is_open(self) -> bool:
        return self.status in (ApplicationStatus.PENDING, ApplicationStatus.UNDER_REVIEW)

    @property
    def is_approved(self) -> bool:
        return self.status == ApplicationStatus.APPROVED


class LicenceApplicationRegister:
    """Tracks company's energy supply licences and applications."""

    def __init__(self) -> None:
        self._licences: dict[str, LicenceRecord] = {}
        self._applications: list[LicenceApplication] = []

    def register_licence(self, licence_id: str, licence_type: LicenceType, tier: LicenceTier, grant_date: date, special_conditions: tuple[str, ...] = ()) -> LicenceRecord:
        record = LicenceRecord(licence_id=licence_id, licence_type=licence_type, tier=tier, grant_date=grant_date, special_conditions=special_conditions)
        self._licences[licence_id] = record
        return record

    def submit_application(self, application_id: str, licence_type: LicenceType, application_date: date, reason: VariationReason) -> LicenceApplication:
        appl = LicenceApplication(application_id=application_id, licence_type=licence_type, application_date=application_date, reason=reason, status=ApplicationStatus.PENDING)
        self._applications.append(appl)
        return appl

    def decide(self, application_id: str, approved: bool, decision_date: date) -> LicenceApplication:
        old = next(a for a in self._applications if a.application_id == application_id)
        status = ApplicationStatus.APPROVED if approved else ApplicationStatus.REJECTED
        updated = LicenceApplication(application_id=old.application_id, licence_type=old.licence_type, application_date=old.application_date, reason=old.reason, status=status, decision_date=decision_date)
        self._applications = [updated if a.application_id == application_id else a for a in self._applications]
        return updated

    @property
    def active_licences(self) -> list[LicenceRecord]:
        return [l for l in self._licences.values() if l.is_active]

    @property
    def licences_with_special_conditions(self) -> list[LicenceRecord]:
        return [l for l in self.active_licences if l.has_special_conditions]

    @property
    def open_applications(self) -> list[LicenceApplication]:
        return [a for a in self._applications if a.is_open]

    @property
    def approved_applications(self) -> list[LicenceApplication]:
        return [a for a in self._applications if a.is_approved]

    def licence_summary(self) -> str:
        n_active = len(self.active_licences)
        n_spsc = len(self.licences_with_special_conditions)
        n_open = len(self.open_applications)
        return (
            "Licence Application Register (Ofgem)\n"
            "Active licences: {:d} | With special conditions: {:d}\n"
            "Open applications: {:d}".format(n_active, n_spsc, n_open)
        )
