"""PPM Installation Warrant Register (Phase FX).

A magistrates' warrant is how a supplier gains entry to install a prepayment meter for debt where
the customer refuses. 94,201 PPMs were fitted under warrant in 2022, 70% by three suppliers.

The regime, in three eras (read_access_and_theft_duties.md §2.5; debt_and_collections.md, SLC 28B
row and the `ppm_warrant_register.py` finding):
- to 5 Feb 2023: warrants listed and heard as before.
- from 6 Feb 2023: magistrates' listing of PPM warrant applications SUSPENDED; suppliers paused
  involuntary installs. Ofgem's Code of Practice followed on 18 Apr 2023.
- from 8 Nov 2023: SLC 28B in the licence. Involuntary PPM is PERMITTED again, subject to its
  conditions (Debt Trigger: 3 months outstanding and GBP200+ per fuel, not on a plan; 10+ contact
  attempts; a recorded Site Welfare Visit; bans by household type). Suppliers restarted one by one
  from Jan 2024, each on Ofgem's say-so -- a date per supplier, not one this module holds.

Corrected 2026-10-06: this said Ofgem "banned force-fitting (warrants for PPM) from April 2023" and
that suppliers "may only install voluntarily", and flagged every application from 27 Apr 2023 as
"post-ban". There was no ban: listing was suspended in February 2023 and installs resumed under
SLC 28B. An application under SLC 28B is lawful when its conditions are met; only one made in the
suspension window is anomalous.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

#: Magistrates' listing of PPM warrant applications suspended (read_access_and_theft_duties.md
#: §2.5, citing Ofgem's Market compliance review of PPM installations, 3 June 2026).
_WARRANT_LISTING_SUSPENDED_FROM = dt.date(2023, 2, 6)
#: SLC 28B in force (Ofgem PPM licence decision, Sep 2023; debt_and_collections.md SLC 28B row).
_SLC_28B_IN_FORCE_FROM = dt.date(2023, 11, 8)
_VULNERABILITY_CHECK_VALID_DAYS = 28   # check expires if 28 days old at installation
#: SLC 28B Debt Trigger: GBP200 or more PER FUEL (debt_and_collections.md, SLC 28B row). This
#: register holds one debt figure per application, so a dual-fuel account is not split here.
_MIN_DEBT_FOR_WARRANT_GBP = 200.0


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
    LISTING_SUSPENDED = "listing_suspended"   # made 6 Feb - 7 Nov 2023


class WarrantRegime(str, Enum):
    """Which rules an application was made under. Not a ban: see the module docstring."""
    PRE_SUSPENSION = "pre_suspension"         # to 5 Feb 2023
    LISTING_SUSPENDED = "listing_suspended"   # 6 Feb - 7 Nov 2023
    SLC_28B = "slc_28b"                       # from 8 Nov 2023: permitted, with conditions


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
    def regime(self) -> WarrantRegime:
        if self.application_date < _WARRANT_LISTING_SUSPENDED_FROM:
            return WarrantRegime.PRE_SUSPENSION
        if self.application_date < _SLC_28B_IN_FORCE_FROM:
            return WarrantRegime.LISTING_SUSPENDED
        return WarrantRegime.SLC_28B

    @property
    def is_in_suspension_window(self) -> bool:
        return self.regime is WarrantRegime.LISTING_SUSPENDED

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
        return (
            f"Warrant {self.warrant_id} [{self.regime.value}] {self.account_id}: "
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

    def suspension_window_applications(self) -> List[PPMWarrantRecord]:
        return [r for r in self._records if r.is_in_suspension_window]

    def applications_by_regime(self) -> dict[str, int]:
        counts = {g.value: 0 for g in WarrantRegime}
        for r in self._records:
            counts[r.regime.value] += 1
        return counts

    def vulnerability_flagged_warrants(self) -> List[PPMWarrantRecord]:
        return [r for r in self._records if not r.vulnerability_check.assessor_cleared]

    def total_compensation_paid_gbp(self) -> float:
        return sum(r.compensation_paid_gbp for r in self._records)

    def warrant_register_summary(self) -> str:
        n = len(self._records)
        by = self.applications_by_regime()
        n_exec = len(self.executed_warrants())
        n_comp = self.total_compensation_paid_gbp()
        return (
            f"PPM Warrant Register: {n} total ("
            f"{by['pre_suspension']} pre-suspension, {by['listing_suspended']} in the "
            f"listing suspension, {by['slc_28b']} under SLC 28B). "
            f"{n_exec} executed. Compensation paid: £{n_comp:.2f}."
        )
