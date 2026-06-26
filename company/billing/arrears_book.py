from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class ArrearsStage(str, Enum):
    CURRENT = 'current'
    DD_FAILED = 'dd_failed'
    FIRST_NOTICE = 'first_notice'
    SECOND_NOTICE = 'second_notice'
    PAYMENT_PLAN_OFFERED = 'payment_plan_offered'
    PAYMENT_PLAN_ACCEPTED = 'payment_plan_accepted'
    PAYMENT_PLAN_DEFAULTED = 'payment_plan_defaulted'
    REFERRED_TO_DEBT = 'referred_to_debt'
    WRITTEN_OFF = 'written_off'
    RESOLVED = 'resolved'


_STAGE_ORDER = [
    ArrearsStage.CURRENT,
    ArrearsStage.DD_FAILED,
    ArrearsStage.FIRST_NOTICE,
    ArrearsStage.SECOND_NOTICE,
    ArrearsStage.PAYMENT_PLAN_OFFERED,
    ArrearsStage.PAYMENT_PLAN_ACCEPTED,
    ArrearsStage.PAYMENT_PLAN_DEFAULTED,
    ArrearsStage.REFERRED_TO_DEBT,
    ArrearsStage.WRITTEN_OFF,
]

_TERMINAL_STAGES = {ArrearsStage.RESOLVED, ArrearsStage.WRITTEN_OFF}


@dataclass
class ArrearsCase:
    case_id: str
    customer_id: str
    arrears_amount_gbp: float
    opened_date: dt.date
    stage: ArrearsStage = ArrearsStage.DD_FAILED
    stage_date: Optional[dt.date] = None
    dd_retry_count: int = 0
    is_vulnerable: bool = False
    resolved_date: Optional[dt.date] = None
    amount_recovered_gbp: float = 0.0

    @property
    def is_open(self) -> bool:
        return self.stage not in _TERMINAL_STAGES

    @property
    def outstanding_gbp(self) -> float:
        return max(0.0, round(self.arrears_amount_gbp - self.amount_recovered_gbp, 2))

    @property
    def days_open(self) -> Optional[int]:
        if self.resolved_date:
            return (self.resolved_date - self.opened_date).days
        return None


class ArrearsBook:
    def __init__(self) -> None:
        self._cases: Dict[str, ArrearsCase] = {}
        self._next_id = 1

    def open_case(self, customer_id: str, arrears_amount_gbp: float,
                  opened_date: dt.date, is_vulnerable: bool = False) -> ArrearsCase:
        case_id = f'ARR-{self._next_id:04d}'
        self._next_id += 1
        case = ArrearsCase(
            case_id=case_id,
            customer_id=customer_id,
            arrears_amount_gbp=arrears_amount_gbp,
            opened_date=opened_date,
            is_vulnerable=is_vulnerable,
        )
        self._cases[case_id] = case
        return case

    def advance_stage(self, case_id: str, new_stage: ArrearsStage,
                      stage_date: dt.date) -> ArrearsCase:
        case = self._cases[case_id]
        if case.stage in _TERMINAL_STAGES:
            raise ValueError(f'Case {case_id} is in terminal stage {case.stage}')
        case.stage = new_stage
        case.stage_date = stage_date
        return case

    def record_recovery(self, case_id: str, amount_gbp: float) -> ArrearsCase:
        case = self._cases[case_id]
        case.amount_recovered_gbp = round(case.amount_recovered_gbp + amount_gbp, 2)
        return case

    def resolve(self, case_id: str, resolved_date: dt.date) -> ArrearsCase:
        case = self._cases[case_id]
        case.stage = ArrearsStage.RESOLVED
        case.resolved_date = resolved_date
        return case

    def write_off(self, case_id: str, write_off_date: dt.date) -> ArrearsCase:
        case = self._cases[case_id]
        case.stage = ArrearsStage.WRITTEN_OFF
        case.resolved_date = write_off_date
        return case

    def open_cases(self) -> List[ArrearsCase]:
        return [c for c in self._cases.values() if c.is_open]

    def cases_for_customer(self, customer_id: str) -> List[ArrearsCase]:
        return [c for c in self._cases.values() if c.customer_id == customer_id]

    def total_arrears_outstanding_gbp(self) -> float:
        return round(sum(c.outstanding_gbp for c in self._cases.values() if c.is_open), 2)

    def cases_at_stage(self, stage: ArrearsStage) -> List[ArrearsCase]:
        return [c for c in self._cases.values() if c.stage == stage]

    def annual_summary(self) -> dict:
        all_c = list(self._cases.values())
        by_stage: dict = {}
        for c in all_c:
            by_stage[c.stage.value] = by_stage.get(c.stage.value, 0) + 1
        written_off = [c for c in all_c if c.stage == ArrearsStage.WRITTEN_OFF]
        return {
            'total_cases': len(all_c),
            'open_cases': len(self.open_cases()),
            'total_outstanding_gbp': self.total_arrears_outstanding_gbp(),
            'total_written_off_gbp': round(sum(c.outstanding_gbp for c in written_off), 2),
            'by_stage': by_stage,
        }
