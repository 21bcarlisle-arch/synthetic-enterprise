"""BSC Credit Assurance Register (Phase FI).

All suppliers operating under the Balancing and Settlement Code (BSC) must
maintain adequate credit cover with Elexon to continue participating in
electricity settlement.

BSC Credit Vetting rules:
- Elexon calculates each supplier's Credit Assessment Price (CAP): max 
  expected exposure over the assessment period
- Suppliers must post credit cover >= their CAP at all times
- Credit instruments accepted: bank guarantee, cash deposit, letter of credit
- If cover falls below CAP: Credit Default Notice (CDN) issued
- 5 working days to cure (restore cover)
- If not cured: suspension from BSC, effectively losing supply licence

Credit exposure drivers:
- Size of portfolio (MWh settled)
- Price volatility (higher during crisis)
- Settlement lag: D+14 (14 working days) for final settlement
- System imbalances (NOP)

Post-2021 crisis: Elexon tightened CAP calculation to include 1-in-20yr VaR.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class CreditInstrumentType(str, Enum):
    BANK_GUARANTEE = "bank_guarantee"
    CASH_DEPOSIT = "cash_deposit"
    LETTER_OF_CREDIT = "letter_of_credit"


class BSCCreditStatus(str, Enum):
    COMPLIANT = "compliant"         # cover >= CAP
    APPROACHING_LIMIT = "approaching_limit"   # cover < 120% CAP
    CREDIT_DEFAULT_NOTICE = "credit_default_notice"  # cover < CAP
    SUSPENDED = "suspended"         # CDN not cured in 5 WD


_CURE_PERIOD_WORKING_DAYS = 5
_APPROACH_THRESHOLD_PCT = 120.0    # warn at 120% to give headroom


@dataclass(frozen=True)
class CreditCoverRecord:
    assessment_date: dt.date
    credit_assessment_price_gbp: float   # CAP: max exposure
    credit_cover_posted_gbp: float       # actual cover provided
    instrument_type: CreditInstrumentType

    @property
    def cover_ratio_pct(self) -> float:
        if self.credit_assessment_price_gbp <= 0:
            return 999.0
        return 100.0 * self.credit_cover_posted_gbp / self.credit_assessment_price_gbp

    @property
    def headroom_gbp(self) -> float:
        return self.credit_cover_posted_gbp - self.credit_assessment_price_gbp

    @property
    def status(self) -> BSCCreditStatus:
        if self.cover_ratio_pct < 100.0:
            return BSCCreditStatus.CREDIT_DEFAULT_NOTICE
        if self.cover_ratio_pct < _APPROACH_THRESHOLD_PCT:
            return BSCCreditStatus.APPROACHING_LIMIT
        return BSCCreditStatus.COMPLIANT

    @property
    def is_compliant(self) -> bool:
        return self.status == BSCCreditStatus.COMPLIANT

    def credit_summary(self) -> str:
        return (
            "BSCCredit " + str(self.assessment_date) + ": "
            "CAP=GBP" + str(round(self.credit_assessment_price_gbp / 1000, 1)) + "k "
            "cover=GBP" + str(round(self.credit_cover_posted_gbp / 1000, 1)) + "k "
            "ratio=" + str(round(self.cover_ratio_pct, 1)) + "% "
            "[" + self.status.value + "]"
        )


class BSCCreditRegister:

    def __init__(self) -> None:
        self._records: List[CreditCoverRecord] = []
        self._cdn_dates: List[dt.date] = []    # CDN issue dates

    def record(self, rec: CreditCoverRecord) -> CreditCoverRecord:
        self._records.append(rec)
        if rec.status == BSCCreditStatus.CREDIT_DEFAULT_NOTICE:
            self._cdn_dates.append(rec.assessment_date)
        return rec

    def latest(self) -> Optional[CreditCoverRecord]:
        if not self._records:
            return None
        return max(self._records, key=lambda r: r.assessment_date)

    def records_in_default(self) -> List[CreditCoverRecord]:
        return [r for r in self._records
                if r.status == BSCCreditStatus.CREDIT_DEFAULT_NOTICE]

    def records_approaching_limit(self) -> List[CreditCoverRecord]:
        return [r for r in self._records
                if r.status == BSCCreditStatus.APPROACHING_LIMIT]

    def is_cdn_overdue(self, as_of: dt.date) -> bool:
        for cdn_date in self._cdn_dates:
            cure_deadline = cdn_date
            days_added = 0
            while days_added < _CURE_PERIOD_WORKING_DAYS:
                cure_deadline += dt.timedelta(days=1)
                if cure_deadline.weekday() < 5:
                    days_added += 1
            latest = self.latest()
            if as_of > cure_deadline and (
                latest is None
                or latest.status == BSCCreditStatus.CREDIT_DEFAULT_NOTICE
            ):
                return True
        return False

    def min_cover_ratio_pct(self) -> float:
        if not self._records:
            return 100.0
        return min(r.cover_ratio_pct for r in self._records)

    def bsc_credit_summary(self, as_of: dt.date) -> str:
        n = len(self._records)
        n_default = len(self.records_in_default())
        overdue = self.is_cdn_overdue(as_of)
        return (
            "BSC Credit Register (" + str(as_of) + "): "
            + str(n) + " assessments. "
            "CDN episodes: " + str(n_default) + ". "
            + ("CDN OVERDUE - SUSPENSION RISK. " if overdue else "")
        )
