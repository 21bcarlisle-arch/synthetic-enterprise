"""Statutory Annual Accounts Register (Phase DJ).

UK Companies Act 2006: every registered company must file annual accounts with
Companies House within 9 months of the financial year end (private companies).
Energy suppliers have additional disclosures under the Gas Act 1986 and Electricity
Act 1989 (Licence Conditions).

Key obligations:
- Directors' Report (s414A CA2006)
- Strategic Report (s414C CA2006) — mandatory for medium/large companies
- FRS 102 compliant accounts (small/medium) or IAS/IFRS (public)
- Energy-specific disclosures: SECR (Streamlined Energy & Carbon Reporting, 2019+)
- Confirmation Statement (annual, replaces Annual Return from 2016)
- TCFD (Task Force on Climate-related Financial Disclosures) from 2023+

Filing deadlines:
- Accounts: 9 months after year-end for private companies
- Confirmation Statement: annually, no set deadline but must be filed
- Late filing penalty: £150→£1,500 for private companies (escalating)

Epistemic: company knows its own accounts filing status. Cannot see HMRC/Companies
House internal systems.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class AccountsType(str, Enum):
    MICRO = "micro"                   # < £632k revenue, <10 employees
    SMALL = "small"                   # < £10.2M revenue
    MEDIUM = "medium"                 # < £36M revenue
    LARGE = "large"                   # ≥ £36M revenue


class FilingStatus(str, Enum):
    DRAFT = "draft"
    SIGNED_OFF = "signed_off"         # directors approved
    SUBMITTED = "submitted"           # filed at Companies House
    ACCEPTED = "accepted"             # Companies House accepted
    REJECTED = "rejected"             # errors, must refile
    LATE = "late"                     # past deadline


class DisclosureFlag(str, Enum):
    SECR = "SECR"                     # Streamlined Energy & Carbon Reporting (2019+)
    TCFD = "TCFD"                     # Task Force on Climate-related Financial Disclosures (2023+)
    GENDER_PAY_GAP = "gender_pay_gap" # 250+ employees
    AUDIT_REQUIRED = "audit_required" # medium/large companies


_LATE_PENALTY_GBP = {
    30: 150.0,    # up to 1 month late
    90: 375.0,    # 1-3 months late
    180: 750.0,   # 3-6 months late
    999: 1500.0,  # 6+ months late
}
_FILING_DEADLINE_MONTHS = 9       # CA2006 s442(2)(a) private companies


@dataclass(frozen=True)
class StatutoryAccountsRecord:
    record_id: str
    financial_year_end: dt.date
    accounts_type: AccountsType
    status: FilingStatus
    submitted_date: Optional[dt.date] = None
    accepted_date: Optional[dt.date] = None
    ch_reference: Optional[str] = None     # Companies House reference
    disclosures: tuple = ()
    revenue_gbp: float = 0.0

    @property
    def filing_deadline(self) -> dt.date:
        import calendar
        fy = self.financial_year_end
        m = fy.month + _FILING_DEADLINE_MONTHS
        y = fy.year + (m - 1) // 12
        m = (m - 1) % 12 + 1
        # Clamp day to last day of month (e.g. Dec31+9m = Sep30)
        last_day = calendar.monthrange(y, m)[1]
        return dt.date(y, m, min(fy.day, last_day))

    def is_overdue(self, as_of: dt.date) -> bool:
        if self.status in (FilingStatus.ACCEPTED, FilingStatus.SUBMITTED):
            return False
        return as_of > self.filing_deadline

    def days_overdue(self, as_of: dt.date) -> int:
        if not self.is_overdue(as_of):
            return 0
        return (as_of - self.filing_deadline).days

    def late_penalty_gbp(self, as_of: dt.date) -> float:
        overdue = self.days_overdue(as_of)
        if overdue == 0:
            return 0.0
        for threshold in sorted(_LATE_PENALTY_GBP.keys()):
            if overdue <= threshold:
                return _LATE_PENALTY_GBP[threshold]
        return _LATE_PENALTY_GBP[max(_LATE_PENALTY_GBP.keys())]

    def has_disclosure(self, flag: DisclosureFlag) -> bool:
        return flag in self.disclosures

    @property
    def requires_audit(self) -> bool:
        return self.accounts_type in (AccountsType.MEDIUM, AccountsType.LARGE)

    @property
    def is_filed(self) -> bool:
        return self.status in (FilingStatus.SUBMITTED, FilingStatus.ACCEPTED)


class StatutoryAccountsRegister:
    """Tracks Companies House filing obligations for the energy supplier."""

    def __init__(self) -> None:
        self._records: List[StatutoryAccountsRecord] = []
        self._seq = 0

    def _next_id(self) -> str:
        self._seq += 1
        return f"SA-{self._seq:04d}"

    @staticmethod
    def classify(revenue_gbp: float) -> AccountsType:
        if revenue_gbp < 632_000:
            return AccountsType.MICRO
        if revenue_gbp < 10_200_000:
            return AccountsType.SMALL
        if revenue_gbp < 36_000_000:
            return AccountsType.MEDIUM
        return AccountsType.LARGE

    def record_year(
        self,
        financial_year_end: dt.date,
        revenue_gbp: float,
        status: FilingStatus = FilingStatus.DRAFT,
        submitted_date: Optional[dt.date] = None,
        accepted_date: Optional[dt.date] = None,
        ch_reference: Optional[str] = None,
        disclosures: tuple = (),
    ) -> StatutoryAccountsRecord:
        accounts_type = self.classify(revenue_gbp)
        rec = StatutoryAccountsRecord(
            record_id=self._next_id(),
            financial_year_end=financial_year_end,
            accounts_type=accounts_type,
            status=status,
            submitted_date=submitted_date,
            accepted_date=accepted_date,
            ch_reference=ch_reference,
            disclosures=disclosures,
            revenue_gbp=revenue_gbp,
        )
        self._records.append(rec)
        return rec

    def overdue(self, as_of: dt.date) -> List[StatutoryAccountsRecord]:
        return [r for r in self._records if r.is_overdue(as_of)]

    def total_penalty_exposure_gbp(self, as_of: dt.date) -> float:
        return sum(r.late_penalty_gbp(as_of) for r in self._records)

    def filed(self) -> List[StatutoryAccountsRecord]:
        return [r for r in self._records if r.is_filed]

    def by_status(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for r in self._records:
            out[r.status.value] = out.get(r.status.value, 0) + 1
        return out

    def by_type(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for r in self._records:
            out[r.accounts_type.value] = out.get(r.accounts_type.value, 0) + 1
        return out

    def requiring_audit(self) -> List[StatutoryAccountsRecord]:
        return [r for r in self._records if r.requires_audit]

    def statutory_accounts_summary(self) -> str:
        total = len(self._records)
        filed = len(self.filed())
        now = dt.date.today()
        overdue = len(self.overdue(now))
        penalty = self.total_penalty_exposure_gbp(now)
        return (
            f"Statutory Accounts Register (CA2006/SECR): {total} years, "
            f"{filed} filed, {overdue} overdue. "
            f"Penalty exposure: £{penalty:,.0f}. "
            f"Filing deadline: 9 months after year-end."
        )
