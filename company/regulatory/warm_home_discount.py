from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

_CORE_DISCOUNT: dict[int, float] = {
    2015: 140.0, 2016: 140.0, 2017: 140.0, 2018: 140.0, 2019: 140.0,
    2020: 140.0, 2021: 140.0, 2022: 150.0, 2023: 150.0, 2024: 150.0,
}
_BROADER_DISCOUNT: dict[int, float] = {
    2015: 140.0, 2016: 140.0, 2017: 140.0, 2018: 140.0, 2019: 140.0,
    2020: 140.0, 2021: 140.0, 2022: 150.0, 2023: 150.0, 2024: 150.0,
}


class WHDEligibilityBasis(str, Enum):
    CORE_GROUP = "core_group"
    BROADER_GROUP = "broader_group"


@dataclass(frozen=True)
class WHDRecord:
    account_id: str
    scheme_year: int
    eligibility_basis: WHDEligibilityBasis
    discount_gbp: float
    applied_month: str
    levy_recovered: bool = False

    @property
    def is_core_group(self) -> bool:
        return self.eligibility_basis == WHDEligibilityBasis.CORE_GROUP


class WHDBook:
    def __init__(self) -> None:
        self._records: list[WHDRecord] = []

    def record_discount(
        self,
        account_id: str,
        scheme_year: int,
        eligibility_basis: WHDEligibilityBasis,
        applied_month: str,
    ) -> WHDRecord:
        if eligibility_basis == WHDEligibilityBasis.CORE_GROUP:
            amount = _CORE_DISCOUNT.get(scheme_year, 150.0)
        else:
            amount = _BROADER_DISCOUNT.get(scheme_year, 150.0)
        rec = WHDRecord(
            account_id=account_id,
            scheme_year=scheme_year,
            eligibility_basis=eligibility_basis,
            discount_gbp=amount,
            applied_month=applied_month,
        )
        self._records.append(rec)
        return rec

    def records_for_year(self, scheme_year: int) -> list[WHDRecord]:
        return [r for r in self._records if r.scheme_year == scheme_year]

    def records_for_account(self, account_id: str) -> list[WHDRecord]:
        return [r for r in self._records if r.account_id == account_id]

    def has_received_whd(self, account_id: str, scheme_year: int) -> bool:
        return any(
            r.account_id == account_id and r.scheme_year == scheme_year
            for r in self._records
        )

    def total_discounted_gbp(self, scheme_year: Optional[int] = None) -> float:
        recs = self.records_for_year(scheme_year) if scheme_year else self._records
        return round(sum(r.discount_gbp for r in recs), 2)

    def levy_recoverable_gbp(self) -> float:
        return round(sum(r.discount_gbp for r in self._records if not r.levy_recovered), 2)

    def mark_levy_recovered(self, scheme_year: int) -> int:
        n = 0
        new_list = []
        for r in self._records:
            if r.scheme_year == scheme_year and not r.levy_recovered:
                from dataclasses import replace
                new_list.append(replace(r, levy_recovered=True))
                n += 1
            else:
                new_list.append(r)
        self._records = new_list
        return n

    def core_group_count(self, scheme_year: int) -> int:
        return sum(1 for r in self.records_for_year(scheme_year) if r.is_core_group)

    def broader_group_count(self, scheme_year: int) -> int:
        return sum(1 for r in self.records_for_year(scheme_year) if not r.is_core_group)

    def whd_summary(self, scheme_year: Optional[int] = None) -> dict:
        recs = self.records_for_year(scheme_year) if scheme_year else self._records
        yr_label = scheme_year if scheme_year else "all"
        return {
            "scheme_year": yr_label,
            "total_records": len(recs),
            "total_discounted_gbp": round(sum(r.discount_gbp for r in recs), 2),
            "core_group": sum(1 for r in recs if r.is_core_group),
            "broader_group": sum(1 for r in recs if not r.is_core_group),
            "levy_recoverable_gbp": self.levy_recoverable_gbp(),
        }


def whd_eligible_customers(service_log) -> list[str]:
    """Return customer IDs from the vulnerability register (WHD Broader Group candidates)."""
    flags = service_log.vulnerability_register()
    return list({f.customer_id for f in flags})


def whd_summary(service_log, scheme_year: int) -> dict:
    """Convenience wrapper: WHD summary derived from vulnerability register for a scheme year."""
    eligible = whd_eligible_customers(service_log)
    return {
        "scheme_year": scheme_year,
        "eligible_customers": len(eligible),
        "eligible_ids": eligible,
        "core_group_discount_gbp": _CORE_DISCOUNT.get(scheme_year, 150.0),
        "broader_group_discount_gbp": _BROADER_DISCOUNT.get(scheme_year, 150.0),
        "estimated_total_outlay_gbp": round(len(eligible) * _BROADER_DISCOUNT.get(scheme_year, 150.0), 2),
    }
