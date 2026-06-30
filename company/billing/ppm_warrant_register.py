"""PPM Installation Warrant Register (Phase FX).

Following the February 2023 British Gas scandal where warrant entries
were used to force-install prepayment meters on vulnerable customers:

- Ofgem launched emergency review Feb 2023
- Voluntary moratorium on forced PPM installations Feb 2023
- Ofgem banned force-fitting (warrants for PPM) from April 2023
- New PPM Code of Practice introduced 2023
- Suppliers who had force-installed PPMs required to compensate

A court warrant (magistrates court application) is required to gain
entry to a property to install a PPM where the customer refuses.
Before applying, suppliers must:
1. Complete SLC 28 4-stage disconnection warning sequence
2. Conduct formal vulnerability assessment
3. Confirm debt exceeds minimum threshold
4. Confirm no winter moratorium applies

Post-April 2023: warrant applications for PPM installation suspended
(Ofgem direction; suppliers may only install voluntarily or with
explicit written customer consent). Emergency metering visits remain
available for safety purposes but not for PPM installation.

This register tracks the pre-ban history and ongoing monitoring
to ensure no recurrence.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

_PPM_FORCE_FIT_BAN_DATE = dt.date(2023, 4, 27)  # Ofgem direction effective date
_VULNERABILITY_CHECK_VALID_DAYS = 28   # check expires if 28 days old at installation
_MIN_DEBT_FOR_WARRANT_GBP = 200.0     # minimum debt before warrant considered


class WarrantStatus(str, Enum):
    APPLIED = "applied"           # application made to magistrates court
    GRANTED = "granted"           # court granted warrant
    REJECTED = "rejected"         # court rejected (typically vulnerability concerns)
    WITHDRAWN = "withdrawn"       # supplier withdrew application
    EXECUTED = "executed"         # warrant used; PPM installed
    REVOKED = "revoked"           # Ofgem or court revoked after the fact


class WarrantRefusalReason(str, Enum):
    VULNERABILITY_IDENTIFIED = "vulnerability_identified"
    INSUFFICIENT_DEBT = "insufficient_debt"
    DISCONNECTION_SEQUENCE_INCOMPLETE = "disconnection_sequence_incomplete"
    WINTER_MORATORIUM = "winter_moratorium"
    POST_BAN = "post_ban"


@dataclass(frozen=True)
class VulnerabilityCheck:
    checked_at: dt.date
    has_psr_flag: bool          # on Priority Services Register
    has_medical_equipment: bool
    has_financial_hardship: bool
    has_children_under_5: bool
    assessor_cleared: bool      # assessor concluded no high-risk vulnerability

    @property
    def is_clear_to_proceed(self) -> bool:
        if not self.assessor_cleared:
            return False
        if self.has_medical_equipment:
            return False
        return True

    @property
    def is_expired(self) -> bool:
        today = dt.date.today()
        return (today - self.checked_at).days > _VULNERABILITY_CHECK_VALID_DAYS

    def is_expired_as_of(self, as_of: dt.date) -> bool:
        return (as_of - self.checked_at).days > _VULNERABILITY_CHECK_VALID_DAYS


@dataclass(frozen=True)
class PPMWarrantRecord:
    warrant_id: str              # WA-NNNNN
    account_id: str
    application_date: dt.date
    debt_at_application_gbp: float
    vulnerability_check: VulnerabilityCheck
    status: WarrantStatus = WarrantStatus.APPLIED
    outcome_date: Optional[dt.date] = None
    refusal_reason: Optional[WarrantRefusalReason] = None
    compensation_paid_gbp: float = 0.0

    @property
    def is_pre_ban(self) -> bool:
        return self.application_date < _PPM_FORCE_FIT_BAN_DATE

    @property
    def is_post_ban(self) -> bool:
        return not self.is_pre_ban

    @property
    def is_active(self) -> bool:
        return self.status in (WarrantStatus.APPLIED, WarrantStatus.GRANTED)

    @property
    def is_executed(self) -> bool:
        return self.status == WarrantStatus.EXECUTED

    @property
    def meets_debt_threshold(self) -> bool:
        return self.debt_at_application_gbp >= _MIN_DEBT_FOR_WARRANT_GBP

    def warrant_summary(self) -> str:
        era = "pre-ban" if self.is_pre_ban else "POST-BAN"
        return (
            f"Warrant {self.warrant_id} [{era}] {self.account_id}: "
            f"debt=£{self.debt_at_application_gbp:.2f} status={self.status.value}"
        )


class PPMWarrantRegister:

    def __init__(self) -> None:
        self._records: List[PPMWarrantRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return f"WA-{self._counter:05d}"

    def apply_for_warrant(
        self,
        account_id: str,
        application_date: dt.date,
        debt_gbp: float,
        vulnerability_check: VulnerabilityCheck,
    ) -> PPMWarrantRecord:
        record = PPMWarrantRecord(
            warrant_id=self._next_id(),
            account_id=account_id,
            application_date=application_date,
            debt_at_application_gbp=debt_gbp,
            vulnerability_check=vulnerability_check,
        )
        self._records.append(record)
        return record

    def update_status(
        self,
        warrant_id: str,
        new_status: WarrantStatus,
        outcome_date: dt.date,
        refusal_reason: Optional[WarrantRefusalReason] = None,
        compensation_gbp: float = 0.0,
    ) -> PPMWarrantRecord:
        for i, r in enumerate(self._records):
            if r.warrant_id == warrant_id:
                updated = PPMWarrantRecord(
                    warrant_id=r.warrant_id,
                    account_id=r.account_id,
                    application_date=r.application_date,
                    debt_at_application_gbp=r.debt_at_application_gbp,
                    vulnerability_check=r.vulnerability_check,
                    status=new_status,
                    outcome_date=outcome_date,
                    refusal_reason=refusal_reason,
                    compensation_paid_gbp=compensation_gbp,
                )
                self._records[i] = updated
                return updated
        raise KeyError(f"Warrant {warrant_id} not found")

    def records_for_account(self, account_id: str) -> List[PPMWarrantRecord]:
        return [r for r in self._records if r.account_id == account_id]

    def active_warrants(self) -> List[PPMWarrantRecord]:
        return [r for r in self._records if r.is_active]

    def granted_warrants(self) -> List[PPMWarrantRecord]:
        return [r for r in self._records if r.status == WarrantStatus.GRANTED]

    def executed_warrants(self) -> List[PPMWarrantRecord]:
        return [r for r in self._records if r.is_executed]

    def rejected_warrants(self) -> List[PPMWarrantRecord]:
        return [r for r in self._records if r.status == WarrantStatus.REJECTED]

    def post_ban_applications(self) -> List[PPMWarrantRecord]:
        return [r for r in self._records if r.is_post_ban]

    def vulnerability_flagged_warrants(self) -> List[PPMWarrantRecord]:
        return [r for r in self._records if not r.vulnerability_check.assessor_cleared]

    def total_compensation_paid_gbp(self) -> float:
        return sum(r.compensation_paid_gbp for r in self._records)

    def warrant_register_summary(self) -> str:
        n = len(self._records)
        n_pre = sum(1 for r in self._records if r.is_pre_ban)
        n_post = len(self.post_ban_applications())
        n_exec = len(self.executed_warrants())
        n_comp = self.total_compensation_paid_gbp()
        return (
            f"PPM Warrant Register: {n} total ({n_pre} pre-ban, {n_post} post-ban). "
            f"{n_exec} executed. Compensation paid: £{n_comp:.2f}. "
            f"Ban date: {_PPM_FORCE_FIT_BAN_DATE}."
        )
