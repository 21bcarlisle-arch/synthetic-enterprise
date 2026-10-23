from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

EBSS_MONTHLY_CREDIT_GBP = 66.67
EBSS_TOTAL_CREDIT_GBP = 400.0
EBSS_ALT_FUEL_CREDIT_GBP = 100.0
EBSS_MONTHS = ["2022-10", "2022-11", "2022-12", "2023-01", "2023-02", "2023-03"]


#: The published instalments: GBP 66 in October and November 2022, GBP 67 from December to March,
#: adding to the GBP 400 (`docs/market_research/energy_bills_support_scheme_delivery.md`). The
#: even 66.67 above is the register's older figure and is GBP 0.02 off the total.
EBSS_INSTALMENT_GBP = {
    "2022-10": 66.0, "2022-11": 66.0, "2022-12": 67.0,
    "2023-01": 67.0, "2023-02": 67.0, "2023-03": 67.0,
}


def ebss_credit_gbp(segment: str, commodity: str, month: str) -> float:
    """The scheme credit a domestic electricity account carried in `month` ("YYYY-MM"), else 0.

    Paid per domestic electricity account, never on gas and never on non-domestic supply. The
    supplier applied it and reclaimed it from government, so it lowers what the household owes and
    leaves the supplier's charge, and its revenue, where they were. Every amount path that asks what
    a household owes for a month nets it through this one function (the VAT rule's lesson: one
    requirement, one home).

    Every payment route is credited in full. The page's 0.71-0.82 voucher take-up applies only to
    traditional prepayment, which the world cannot tell from smart, and a prepayment statement
    never fails there (`arrears_engine.PREPAYMENT_METHOD`), so the take-up belief moves no failed
    pound. GAP: the unredeemed vouchers, about a fifth of traditional PPM's, are not modelled.
    """
    if segment != "resi" or commodity != "electricity":
        return 0.0
    return EBSS_INSTALMENT_GBP.get(month, 0.0)


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
