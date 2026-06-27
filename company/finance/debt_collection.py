"""Debt collection process tracker: arrears escalation under Ofgem SLC P14/SoP Regulations."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class DebtStage(str, Enum):
    INITIAL_REMINDER = "initial_reminder"   # 7-day automated letter
    WARNING_LETTER = "warning_letter"       # 14-day notice, potential referral flagged
    PRE_LEGAL = "pre_legal"                 # 28-day final notice before external agency
    DEBT_AGENCY = "debt_agency"             # assigned to collection agency (~65p/\u00a3 recovery)
    LEGAL_ACTION = "legal_action"           # county court judgment or small claims
    WRITE_OFF = "write_off"                 # statute-barred or unrecoverable


_RECOVERY_PROBABILITY: Dict[DebtStage, float] = {
    DebtStage.INITIAL_REMINDER: 0.95,
    DebtStage.WARNING_LETTER: 0.85,
    DebtStage.PRE_LEGAL: 0.70,
    DebtStage.DEBT_AGENCY: 0.65,
    DebtStage.LEGAL_ACTION: 0.40,
    DebtStage.WRITE_OFF: 0.00,
}

_STATUTE_LIMIT_YEARS = 6  # England/Wales (5 in Scotland; using 6 conservatively)


@dataclass(frozen=True)
class DebtRecord:
    account_id: str
    amount_gbp: float
    stage: DebtStage
    stage_date: dt.date
    initial_date: dt.date
    is_vulnerable_customer: bool = False

    def days_in_stage(self, as_of: dt.date) -> int:
        return (as_of - self.stage_date).days

    def is_statute_barred(self, as_of: dt.date) -> bool:
        return (as_of - self.initial_date).days / 365.25 > _STATUTE_LIMIT_YEARS

    @property
    def recovery_probability(self) -> float:
        return _RECOVERY_PROBABILITY[self.stage]

    @property
    def expected_recovery_gbp(self) -> float:
        return round(self.amount_gbp * self.recovery_probability, 2)


class DebtCollectionBook:
    """Tracks escalating debt collection across the portfolio.

    Real calibration:
    - UK average arrears 2022: 380 GBP/customer (Ofgem Retail State of Market)
    - Write-off rate 1.5-2.5% of revenue in crisis years 2022-23
    - Agency recovery rate 60-75p/GBP for energy debts
    - Average days-to-legal: 90-120 from first reminder
    - Ofgem: vulnerable customers must not go to agency without prior welfare check
    """

    def __init__(self) -> None:
        self._records: Dict[str, DebtRecord] = {}

    def record_debt(self, record: DebtRecord) -> DebtRecord:
        self._records[record.account_id] = record
        return record

    def escalate(
        self,
        account_id: str,
        new_stage: DebtStage,
        stage_date: dt.date,
    ) -> DebtRecord:
        existing = self._records[account_id]
        updated = DebtRecord(
            account_id=account_id,
            amount_gbp=existing.amount_gbp,
            stage=new_stage,
            stage_date=stage_date,
            initial_date=existing.initial_date,
            is_vulnerable_customer=existing.is_vulnerable_customer,
        )
        self._records[account_id] = updated
        return updated

    def write_off(self, account_id: str, write_off_date: dt.date) -> DebtRecord:
        return self.escalate(account_id, DebtStage.WRITE_OFF, write_off_date)

    def active_debts(self) -> List[DebtRecord]:
        return [r for r in self._records.values() if r.stage != DebtStage.WRITE_OFF]

    def debts_by_stage(self, stage: DebtStage) -> List[DebtRecord]:
        return [r for r in self._records.values() if r.stage == stage]

    def total_outstanding_gbp(self) -> float:
        return round(sum(r.amount_gbp for r in self.active_debts()), 2)

    def expected_recovery_gbp(self) -> float:
        return round(sum(r.expected_recovery_gbp for r in self.active_debts()), 2)

    def vulnerable_accounts(self) -> List[DebtRecord]:
        return [r for r in self.active_debts() if r.is_vulnerable_customer]

    def statute_barred_check(self, as_of: dt.date) -> List[DebtRecord]:
        return [r for r in self.active_debts() if r.is_statute_barred(as_of)]

    def debt_summary(self) -> dict:
        by_stage = {s.value: len(self.debts_by_stage(s)) for s in DebtStage}
        return {
            "total_accounts": len(self._records),
            "active_accounts": len(self.active_debts()),
            "written_off": len(self.debts_by_stage(DebtStage.WRITE_OFF)),
            "total_outstanding_gbp": self.total_outstanding_gbp(),
            "expected_recovery_gbp": self.expected_recovery_gbp(),
            "vulnerable_accounts": len(self.vulnerable_accounts()),
            "by_stage": by_stage,
        }
