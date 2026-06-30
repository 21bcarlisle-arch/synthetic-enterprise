"""Ofgem Complaint Escalation Register (Phase FB).

When a customer is not satisfied with a supplier's final response, they can
escalate to the Energy Ombudsman (Ombudsman Services Energy).

Key rules (SLC 18.9 + EOS rules):
- Supplier must issue Final Response or 8-week deadlock letter
- Customer has 6 months to refer to Ombudsman after Final Response
- Ombudsman investigates and can order: apology, explanation, remedial action,
  financial award (up to £10,000 domestic, higher commercial)
- Ombudsman decisions are binding on the supplier
- Ombudsman reports data annually to Ofgem (supplier league tables)

Ofgem uses ombudsman uphold rates to identify poor-performing suppliers.
High uphold rate = Ofgem investigation risk.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class OmbudsmanOutcome(str, Enum):
    PENDING = "pending"
    UPHELD = "upheld"               # in customer's favour
    PARTIALLY_UPHELD = "partially_upheld"
    NOT_UPHELD = "not_upheld"       # in supplier's favour
    WITHDRAWN = "withdrawn"         # customer withdrew before decision


class OmbudsmanAwardType(str, Enum):
    FINANCIAL = "financial"
    APOLOGY = "apology"
    EXPLANATION = "explanation"
    REMEDIAL_ACTION = "remedial_action"


_FINAL_RESPONSE_TO_REFERRAL_WINDOW_DAYS = 182   # 6 months
_INVESTIGATION_TARGET_WEEKS = 8
_MAX_FINANCIAL_AWARD_DOMESTIC_GBP = 10_000.0
_HIGH_UPHOLD_RATE_PCT = 50.0   # Ofgem watchlist threshold


@dataclass(frozen=True)
class OmbudsmanAward:
    award_type: OmbudsmanAwardType
    financial_amount_gbp: float = 0.0
    description: str = ""


@dataclass(frozen=True)
class OmbudsmanCase:
    case_reference: str
    account_id: str
    original_ticket_id: str
    referred_at: dt.date
    supplier_final_response_date: dt.date
    outcome: OmbudsmanOutcome = OmbudsmanOutcome.PENDING
    decided_at: Optional[dt.date] = None
    award: Optional[OmbudsmanAward] = None

    @property
    def is_in_window(self) -> bool:
        delta = (self.referred_at - self.supplier_final_response_date).days
        return 0 <= delta <= _FINAL_RESPONSE_TO_REFERRAL_WINDOW_DAYS

    @property
    def is_pending(self) -> bool:
        return self.outcome == OmbudsmanOutcome.PENDING

    @property
    def is_upheld(self) -> bool:
        return self.outcome in (
            OmbudsmanOutcome.UPHELD, OmbudsmanOutcome.PARTIALLY_UPHELD
        )

    @property
    def financial_liability_gbp(self) -> float:
        if self.award and self.award.award_type == OmbudsmanAwardType.FINANCIAL:
            return self.award.financial_amount_gbp
        return 0.0

    def case_summary(self) -> str:
        return (
            "OmbudsmanCase " + self.case_reference + " (" + self.account_id + "): "
            + self.outcome.value
            + (" GBP" + str(round(self.financial_liability_gbp)) if self.financial_liability_gbp else "")
        )


class OmbudsmanRegister:

    def __init__(self) -> None:
        self._cases: List[OmbudsmanCase] = []
        self._next_case = 1

    def register_case(
        self,
        account_id: str,
        ticket_id: str,
        referred_at: dt.date,
        final_response_date: dt.date,
    ) -> OmbudsmanCase:
        ref = "OSE-" + str(self._next_case).zfill(6)
        self._next_case += 1
        case = OmbudsmanCase(
            case_reference=ref,
            account_id=account_id,
            original_ticket_id=ticket_id,
            referred_at=referred_at,
            supplier_final_response_date=final_response_date,
        )
        self._cases.append(case)
        return case

    def record_decision(
        self,
        case_reference: str,
        outcome: OmbudsmanOutcome,
        decided_at: dt.date,
        award: Optional[OmbudsmanAward] = None,
    ) -> Optional[OmbudsmanCase]:
        for i, c in enumerate(self._cases):
            if c.case_reference == case_reference:
                updated = OmbudsmanCase(
                    case_reference=c.case_reference,
                    account_id=c.account_id,
                    original_ticket_id=c.original_ticket_id,
                    referred_at=c.referred_at,
                    supplier_final_response_date=c.supplier_final_response_date,
                    outcome=outcome,
                    decided_at=decided_at,
                    award=award,
                )
                self._cases[i] = updated
                return updated
        return None

    def pending_cases(self) -> List[OmbudsmanCase]:
        return [c for c in self._cases if c.is_pending]

    def upheld_cases(self) -> List[OmbudsmanCase]:
        return [c for c in self._cases if c.is_upheld]

    def decided_cases(self) -> List[OmbudsmanCase]:
        return [c for c in self._cases if not c.is_pending]

    def uphold_rate_pct(self) -> float:
        decided = self.decided_cases()
        if not decided:
            return 0.0
        upheld = [c for c in decided if c.is_upheld]
        return 100.0 * len(upheld) / len(decided)

    def is_high_uphold_rate(self) -> bool:
        return self.uphold_rate_pct() >= _HIGH_UPHOLD_RATE_PCT

    def total_financial_awards_gbp(self) -> float:
        return sum(c.financial_liability_gbp for c in self._cases)

    def ombudsman_summary(self) -> str:
        n = len(self._cases)
        pending = len(self.pending_cases())
        upheld = len(self.upheld_cases())
        rate = self.uphold_rate_pct()
        return (
            "Ombudsman Register: " + str(n) + " cases. "
            "Pending: " + str(pending) + ". "
            "Upheld: " + str(upheld) + " (" + str(round(rate, 1)) + "%). "
            + ("OFGEM_WATCHLIST_RISK. " if self.is_high_uphold_rate() else "")
            + "Total awards: GBP" + str(round(self.total_financial_awards_gbp())) + "."
        )
