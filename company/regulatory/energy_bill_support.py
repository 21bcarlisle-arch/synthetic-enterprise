from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


EBSS_MONTHLY_CREDIT_GBP = 66.67
EBSS_TOTAL_CREDIT_GBP = 400.0
EBSS_ALT_FUEL_CREDIT_GBP = 100.0
EBSS_MONTHS = ["2022-10", "2022-11", "2022-12", "2023-01", "2023-02", "2023-03"]


class EBSSCreditType(str, Enum):
    STANDARD = "standard"
    ALT_FUEL = "alt_fuel"


@dataclass(frozen=True)
class EBSSCredit:
    account_id: str
    credit_month: str
    credit_type: EBSSCreditType
    amount_gbp: float
    claimed_from_govt: bool = False

    @property
    def is_standard(self) -> bool:
        return self.credit_type == EBSSCreditType.STANDARD


class EBSSBook:
    def __init__(self) -> None:
        self._credits: list[EBSSCredit] = []

    def record_credit(
        self,
        account_id: str,
        credit_month: str,
        credit_type: EBSSCreditType = EBSSCreditType.STANDARD,
    ) -> EBSSCredit:
        amount = (
            EBSS_MONTHLY_CREDIT_GBP
            if credit_type == EBSSCreditType.STANDARD
            else EBSS_ALT_FUEL_CREDIT_GBP
        )
        credit = EBSSCredit(
            account_id=account_id,
            credit_month=credit_month,
            credit_type=credit_type,
            amount_gbp=amount,
        )
        self._credits.append(credit)
        return credit

    def credits_for_account(self, account_id: str) -> list[EBSSCredit]:
        return [c for c in self._credits if c.account_id == account_id]

    def credits_for_month(self, month: str) -> list[EBSSCredit]:
        return [c for c in self._credits if c.credit_month == month]

    def total_credited_gbp(self) -> float:
        return round(sum(c.amount_gbp for c in self._credits), 2)

    def total_for_account_gbp(self, account_id: str) -> float:
        return round(sum(c.amount_gbp for c in self.credits_for_account(account_id)), 2)

    def govt_receivable_gbp(self) -> float:
        return round(sum(c.amount_gbp for c in self._credits if not c.claimed_from_govt), 2)

    def mark_claimed(self, month: str) -> int:
        n = 0
        new_list = []
        for c in self._credits:
            if c.credit_month == month and not c.claimed_from_govt:
                from dataclasses import replace
                new_list.append(replace(c, claimed_from_govt=True))
                n += 1
            else:
                new_list.append(c)
        self._credits = new_list
        return n

    def is_scheme_month(self, month: str) -> bool:
        return month in EBSS_MONTHS

    def monthly_summary(self) -> list[dict]:
        by_month: dict[str, float] = {}
        for c in self._credits:
            by_month[c.credit_month] = by_month.get(c.credit_month, 0.0) + c.amount_gbp
        return [
            {"month": m, "total_gbp": round(by_month.get(m, 0.0), 2), "is_ebss_month": m in EBSS_MONTHS}
            for m in sorted(by_month)
        ]

    def ebss_summary(self) -> dict:
        return {
            "total_credits": len(self._credits),
            "total_credited_gbp": self.total_credited_gbp(),
            "govt_receivable_gbp": self.govt_receivable_gbp(),
            "scheme_months": EBSS_MONTHS,
            "standard_credits": sum(1 for c in self._credits if c.is_standard),
            "alt_fuel_credits": sum(1 for c in self._credits if not c.is_standard),
        }
