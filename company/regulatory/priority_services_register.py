"""Priority Services Register (PSR) — consumer vulnerability tracking.

UK energy suppliers maintain a PSR identifying customers with additional needs.
SLC 26B: maintain PSR, offer ≥1 core service, share with network operators.

PSR eligibility: pensionable age, disability, medical equipment dependency,
child <5, chronic illness, mental health, visual/hearing impairment, language.

UK ~9M households on PSR (~31% domestic). Core services: priority reconnection
(4h domestic), nominee scheme, gas safety check, alternative format,
password scheme, advance interruption notice.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from datetime import date


class PSRCategory(str, Enum):
    PENSIONABLE_AGE = "pensionable_age"
    DISABILITY = "disability"
    MEDICAL_EQUIPMENT = "medical_equipment"
    CHILD_UNDER_5 = "child_under_5"
    CHRONIC_ILLNESS = "chronic_illness"
    MENTAL_HEALTH = "mental_health"
    VISUAL_IMPAIRMENT = "visual_impairment"
    HEARING_IMPAIRMENT = "hearing_impairment"
    LANGUAGE_SUPPORT = "language_support"


class PSRService(str, Enum):
    PRIORITY_RECONNECTION = "priority_reconnection"
    NOMINEE_SCHEME = "nominee_scheme"
    GAS_SAFETY_CHECK = "gas_safety_check"
    ALTERNATIVE_FORMAT = "alternative_format"
    PASSWORD_SCHEME = "password_scheme"
    ADVANCE_INTERRUPTION_NOTICE = "advance_interruption_notice"


@dataclass(frozen=True)
class PSRRecord:
    account_id: str
    categories: tuple[PSRCategory, ...]
    services_enrolled: tuple[PSRService, ...]
    registration_date: date
    review_due_date: date
    shared_with_network: bool = False
    is_active: bool = True

    @property
    def is_electricity_dependent(self) -> bool:
        return PSRCategory.MEDICAL_EQUIPMENT in self.categories

    @property
    def needs_priority_reconnection(self) -> bool:
        return (
            self.is_electricity_dependent
            or PSRCategory.PENSIONABLE_AGE in self.categories
        )

    def is_review_overdue(self, as_of: date) -> bool:
        return as_of > self.review_due_date

    @property
    def has_at_least_one_service(self) -> bool:
        return len(self.services_enrolled) > 0

    @property
    def is_compliant(self) -> bool:
        return self.has_at_least_one_service


class PriorityServicesRegister:
    """Tracks PSR records and monitors SLC 26B compliance."""

    UK_PSR_RATE_PCT = 31.0  # UK benchmark

    def __init__(self) -> None:
        self._records: dict[str, PSRRecord] = {}

    def register(self, record: PSRRecord) -> PSRRecord:
        self._records[record.account_id] = record
        return record

    def get_record(self, account_id: str) -> PSRRecord | None:
        return self._records.get(account_id)

    def deregister(self, account_id: str) -> None:
        record = self._records.get(account_id)
        if record:
            self._records[account_id] = PSRRecord(
                account_id=record.account_id,
                categories=record.categories,
                services_enrolled=record.services_enrolled,
                registration_date=record.registration_date,
                review_due_date=record.review_due_date,
                shared_with_network=record.shared_with_network,
                is_active=False,
            )

    @property
    def active_records(self) -> list[PSRRecord]:
        return [r for r in self._records.values() if r.is_active]

    @property
    def electricity_dependent(self) -> list[PSRRecord]:
        return [r for r in self.active_records if r.is_electricity_dependent]

    @property
    def priority_reconnection_customers(self) -> list[PSRRecord]:
        return [r for r in self.active_records if r.needs_priority_reconnection]

    @property
    def non_compliant_records(self) -> list[PSRRecord]:
        return [r for r in self.active_records if not r.is_compliant]

    @property
    def network_shared_count(self) -> int:
        return sum(1 for r in self.active_records if r.shared_with_network)

    def overdue_reviews(self, as_of: date) -> list[PSRRecord]:
        return [r for r in self.active_records if r.is_review_overdue(as_of)]

    def psr_penetration_pct(self, total_domestic_accounts: int) -> float:
        if total_domestic_accounts == 0:
            return 0.0
        return len(self.active_records) / total_domestic_accounts * 100

    def psr_summary(self, as_of: date) -> str:
        n = len(self.active_records)
        n_elec_dep = len(self.electricity_dependent)
        n_non_compliant = len(self.non_compliant_records)
        n_overdue = len(self.overdue_reviews(as_of))
        lines = [
            "Priority Services Register (SLC 26B)",
            "Active: {:d} | Electricity-dependent: {:d}".format(n, n_elec_dep),
            "Non-compliant (no services): {:d} | Reviews overdue: {:d}".format(
                n_non_compliant, n_overdue
            ),
        ]
        return chr(10).join(lines)
