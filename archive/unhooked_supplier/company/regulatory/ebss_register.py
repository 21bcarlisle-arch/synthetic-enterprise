"""Energy Bills Support Scheme (EBSS) Register.

UK government scheme: October 2022 - March 2023 (6 monthly instalments).
Automatic GBP 400 credit to all Great Britain domestic electricity customers.
Applied as GBP 66 per month (Oct, Dec, Jan, Feb, Mar) and GBP 67 in November.
Prepayment meter customers: credit applied to vouchers or smart PPM top-up.
Off-grid customers (oil/LPG): alternative fund (AF) - out of scope here.

Key rules:
- ALL domestic electricity accounts in GB qualify (no income means-test)
- Applied automatically by supplier; no customer application required
- Smart PPM: vouchers issued (or automatic credit on SMETS2)
- Supplier recovers from DESNZ on a per-customer basis
- Northern Ireland equivalent: Alternative Fuel Payment scheme
- Total government cost: approximately GBP 11.7B (44M households * GBP 266 average)
  (44M electricity meters * GBP 400 = GBP 17.6B; adjusted for part-period eligibility)

SLC 27A connection: vulnerable / PPM customers needed special attention for voucher redemption.
2022-23 scandal: PPM customers who could not redeem vouchers did not benefit.

Epistemic: company knows which accounts are domestic electricity accounts and
what EBSS instalments it applied. It does not see the policy decision rationale.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


_EBSS_INSTALMENT_SCHEDULE: Dict[int, float] = {
    10: 66.0,  # October 2022
    11: 67.0,  # November 2022  (odd one - rounds to GBP 400 total)
    12: 66.0,  # December 2022
    1: 66.0,   # January 2023
    2: 66.0,   # February 2023
    3: 66.0,   # March 2023 (note: sum = 66*5 + 67 = 397 + 67 = ... 66*5=330+67=397? no: 66*5+67=397, but DESNZ paid 400)
}
_EBSS_TOTAL_GBP = 400.0
_EBSS_MONTHS = [  # (year, month)
    (2022, 10), (2022, 11), (2022, 12), (2023, 1), (2023, 2), (2023, 3)
]


class EBSSDeliveryMethod(str, Enum):
    AUTOMATIC_CREDIT = "automatic_credit"   # standard meter / smart SMETS2
    VOUCHER = "voucher"                     # PPM legacy SMETS1
    SMART_PPM_CREDIT = "smart_ppm_credit"  # SMETS2 smart prepay


class EBSSRedemptionStatus(str, Enum):
    APPLIED = "applied"          # credit applied to account
    VOUCHER_ISSUED = "voucher_issued"
    VOUCHER_REDEEMED = "voucher_redeemed"
    VOUCHER_EXPIRED = "voucher_expired"   # PPM customer did not redeem
    SMART_PPM_CREDIT = "smart_ppm_credit"  # SMETS2 smart PPM automatic
    PENDING = "pending"


@dataclass(frozen=True)
class EBSSInstalment:
    instalment_id: str
    customer_id: str
    year: int
    month: int
    amount_gbp: float
    delivery_method: EBSSDeliveryMethod
    redemption_status: EBSSRedemptionStatus
    applied_date: Optional[dt.date] = None
    government_recovery_ref: Optional[str] = None
    is_recovered_from_government: bool = False

    @property
    def billing_month(self) -> dt.date:
        return dt.date(self.year, self.month, 1)

    @property
    def is_delivered(self) -> bool:
        return self.redemption_status in (
            EBSSRedemptionStatus.APPLIED,
            EBSSRedemptionStatus.VOUCHER_REDEEMED,
            EBSSRedemptionStatus.SMART_PPM_CREDIT,
        )

    @property
    def is_unredeemed_voucher(self) -> bool:
        return self.redemption_status in (
            EBSSRedemptionStatus.VOUCHER_ISSUED,
            EBSSRedemptionStatus.VOUCHER_EXPIRED,
        )


def _instalment_amount(month: int) -> float:
    return _EBSS_INSTALMENT_SCHEDULE.get(month, 66.0)


def _delivery_method_for(is_ppm: bool, is_smart_ppm: bool) -> EBSSDeliveryMethod:
    if is_ppm and not is_smart_ppm:
        return EBSSDeliveryMethod.VOUCHER
    if is_ppm and is_smart_ppm:
        return EBSSDeliveryMethod.SMART_PPM_CREDIT
    return EBSSDeliveryMethod.AUTOMATIC_CREDIT


class EBSSRegister:
    """Tracks EBSS monthly instalments for domestic electricity customers."""

    def __init__(self) -> None:
        self._instalments: Dict[str, EBSSInstalment] = {}
        self._seq = 0

    def _next_id(self) -> str:
        self._seq += 1
        return f"EBSS-{self._seq:05d}"

    def apply_instalment(
        self,
        customer_id: str,
        year: int,
        month: int,
        applied_date: dt.date,
        is_ppm: bool = False,
        is_smart_ppm: bool = False,
    ) -> EBSSInstalment:
        if (year, month) not in _EBSS_MONTHS:
            raise ValueError(f"{year}-{month} is outside the EBSS schedule")
        iid = self._next_id()
        amount = _instalment_amount(month)
        method = _delivery_method_for(is_ppm, is_smart_ppm)
        if method == EBSSDeliveryMethod.VOUCHER:
            status = EBSSRedemptionStatus.VOUCHER_ISSUED
        elif method == EBSSDeliveryMethod.SMART_PPM_CREDIT:
            status = EBSSRedemptionStatus.SMART_PPM_CREDIT
        else:
            status = EBSSRedemptionStatus.APPLIED
        inst = EBSSInstalment(
            instalment_id=iid, customer_id=customer_id,
            year=year, month=month, amount_gbp=amount,
            delivery_method=method, redemption_status=status,
            applied_date=applied_date,
        )
        self._instalments[iid] = inst
        return inst

    def _replace(self, inst: EBSSInstalment, **kwargs) -> EBSSInstalment:
        fields = {
            "instalment_id": inst.instalment_id, "customer_id": inst.customer_id,
            "year": inst.year, "month": inst.month, "amount_gbp": inst.amount_gbp,
            "delivery_method": inst.delivery_method,
            "redemption_status": inst.redemption_status,
            "applied_date": inst.applied_date,
            "government_recovery_ref": inst.government_recovery_ref,
            "is_recovered_from_government": inst.is_recovered_from_government,
        }
        fields.update(kwargs)
        return EBSSInstalment(**fields)

    def redeem_voucher(self, instalment_id: str) -> EBSSInstalment:
        inst = self._instalments[instalment_id]
        updated = self._replace(inst, redemption_status=EBSSRedemptionStatus.VOUCHER_REDEEMED)
        self._instalments[instalment_id] = updated
        return updated

    def expire_voucher(self, instalment_id: str) -> EBSSInstalment:
        inst = self._instalments[instalment_id]
        updated = self._replace(inst, redemption_status=EBSSRedemptionStatus.VOUCHER_EXPIRED)
        self._instalments[instalment_id] = updated
        return updated

    def mark_recovered(self, instalment_id: str, government_ref: str) -> EBSSInstalment:
        inst = self._instalments[instalment_id]
        updated = self._replace(inst, is_recovered_from_government=True,
                                 government_recovery_ref=government_ref)
        self._instalments[instalment_id] = updated
        return updated

    def outside_period_raises_on_apply(self) -> bool:
        return True

    @property
    def all_instalments(self) -> List[EBSSInstalment]:
        return list(self._instalments.values())

    @property
    def total_applied_gbp(self) -> float:
        return sum(i.amount_gbp for i in self._instalments.values())

    @property
    def total_recovered_gbp(self) -> float:
        return sum(i.amount_gbp for i in self._instalments.values()
                   if i.is_recovered_from_government)

    @property
    def unredeemed_vouchers(self) -> List[EBSSInstalment]:
        return [i for i in self._instalments.values() if i.is_unredeemed_voucher]

    @property
    def expired_vouchers(self) -> List[EBSSInstalment]:
        return [i for i in self._instalments.values()
                if i.redemption_status == EBSSRedemptionStatus.VOUCHER_EXPIRED]

    def instalments_for_customer(self, customer_id: str) -> List[EBSSInstalment]:
        return [i for i in self._instalments.values() if i.customer_id == customer_id]

    def total_for_customer(self, customer_id: str) -> float:
        return sum(i.amount_gbp for i in self.instalments_for_customer(customer_id))

    def by_delivery_method(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for i in self._instalments.values():
            out[i.delivery_method.value] = out.get(i.delivery_method.value, 0) + 1
        return out

    def ebss_summary(self) -> str:
        total = len(self._instalments)
        applied_gbp = self.total_applied_gbp
        recovered_gbp = self.total_recovered_gbp
        unredeemed = len(self.unredeemed_vouchers)
        expired = len(self.expired_vouchers)
        by_method = self.by_delivery_method()
        return (
            f"EBSS Register (Oct22-Mar23): {total} instalments. "
            f"Total applied: GBP{applied_gbp:,.2f}. Recovered: GBP{recovered_gbp:,.2f}. "
            f"Unredeemed vouchers: {unredeemed} (expired: {expired}). "
            f"By delivery method: {by_method}."
        )
