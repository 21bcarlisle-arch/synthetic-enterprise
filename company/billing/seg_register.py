"""Smart Export Guarantee (SEG) Register.

The Smart Export Guarantee (SI 2020/1297) replaced the Feed-in Tariff (FiT)
export element from 1 January 2020. Electricity suppliers with >= 150,000
domestic customer accounts are obligated to offer a SEG tariff to eligible
micro-generators (<=5MW installed capacity) who have a smart meter capable of
providing half-hourly export readings.

Key obligations:
  - Must offer at least one SEG tariff (minimum 0p/kWh; must be positive).
  - Export must be metered (SMETS2 required; SMETS1 accepted if DCC-enrolled).
  - Eligible generation types: solar PV, wind, hydro, CHP, anaerobic digestion.
  - Payments made quarterly (standard) or monthly (premium tariff option).

Distinct from:
  - rego_portfolio.py: REGO certificates (wholesale, not customer-facing)
  - green_gas_levy_register.py: GGL levy (gas, not electricity)
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class MicroGenerationType(str, Enum):
    SOLAR_PV = "solar_pv"
    WIND = "wind"
    HYDRO = "hydro"
    COMBINED_HEAT_POWER = "combined_heat_power"
    ANAEROBIC_DIGESTION = "anaerobic_digestion"


class SEGTariffType(str, Enum):
    FIXED = "fixed"
    VARIABLE = "variable"
    TIME_OF_USE = "time_of_use"


class SEGEligibilityStatus(str, Enum):
    PENDING_VERIFICATION = "pending_verification"
    ELIGIBLE = "eligible"
    INELIGIBLE = "ineligible"
    SUSPENDED = "suspended"


class SEGPaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    DISPUTED = "disputed"


_SEG_START_DATE = dt.date(2020, 1, 1)
_MAX_CAPACITY_KW = 5000.0  # 5 MW


@dataclass(frozen=True)
class SEGAccount:
    account_id: str
    export_mpan: str
    generation_type: MicroGenerationType
    installed_capacity_kw: float
    commissioning_date: dt.date
    tariff_rate_pence_per_kwh: float
    tariff_type: SEGTariffType
    eligibility_status: SEGEligibilityStatus
    smets2_verified: bool = True

    @property
    def is_eligible(self) -> bool:
        return self.eligibility_status == SEGEligibilityStatus.ELIGIBLE

    @property
    def is_capacity_compliant(self) -> bool:
        return 0 < self.installed_capacity_kw <= _MAX_CAPACITY_KW

    def annual_estimated_export_gbp(self, annual_export_kwh: float) -> float:
        if not self.is_eligible:
            return 0.0
        return annual_export_kwh * self.tariff_rate_pence_per_kwh / 100.0

    def account_summary(self) -> str:
        return (
            f"SEG {self.account_id}: {self.generation_type.value} "
            f"{self.installed_capacity_kw:.1f}kW "
            f"@{self.tariff_rate_pence_per_kwh:.2f}p/kWh "
            f"[{self.eligibility_status.value}]"
        )


@dataclass(frozen=True)
class SEGPaymentRecord:
    payment_id: str
    account_id: str
    export_mpan: str
    period_start: dt.date
    period_end: dt.date
    export_kwh: float
    payment_gbp: float
    status: SEGPaymentStatus

    @property
    def is_paid(self) -> bool:
        return self.status == SEGPaymentStatus.PAID


class SEGRegister:
    """Register of Smart Export Guarantee accounts and payments."""

    def __init__(self) -> None:
        self._accounts: List[SEGAccount] = []
        self._payments: List[SEGPaymentRecord] = []
        self._account_counter: int = 0
        self._payment_counter: int = 0

    def _next_account_id(self) -> str:
        self._account_counter += 1
        return "SEG-" + str(self._account_counter).zfill(5)

    def _next_payment_id(self) -> str:
        self._payment_counter += 1
        return "SEGPAY-" + str(self._payment_counter).zfill(5)

    def _update_account(self, account_id: str, **kwargs) -> SEGAccount:
        for i, a in enumerate(self._accounts):
            if a.account_id == account_id:
                updated = SEGAccount(**{**a.__dict__, **kwargs})
                self._accounts[i] = updated
                return updated
        raise KeyError(f"SEG account not found: {account_id}")

    def _update_payment(self, payment_id: str, **kwargs) -> SEGPaymentRecord:
        for i, p in enumerate(self._payments):
            if p.payment_id == payment_id:
                updated = SEGPaymentRecord(**{**p.__dict__, **kwargs})
                self._payments[i] = updated
                return updated
        raise KeyError(f"Payment not found: {payment_id}")

    def enrol_account(
        self,
        export_mpan: str,
        generation_type: MicroGenerationType,
        installed_capacity_kw: float,
        commissioning_date: dt.date,
        tariff_rate_pence_per_kwh: float,
        tariff_type: SEGTariffType,
        smets2_verified: bool = True,
    ) -> SEGAccount:
        if commissioning_date < _SEG_START_DATE:
            raise ValueError(f"SEG scheme started {_SEG_START_DATE}; commissioning date too early")
        if installed_capacity_kw <= 0 or installed_capacity_kw > _MAX_CAPACITY_KW:
            raise ValueError(f"installed_capacity_kw must be >0 and <={_MAX_CAPACITY_KW}kW")
        if tariff_rate_pence_per_kwh < 0:
            raise ValueError("tariff_rate_pence_per_kwh cannot be negative")
        account = SEGAccount(
            account_id=self._next_account_id(),
            export_mpan=export_mpan,
            generation_type=generation_type,
            installed_capacity_kw=installed_capacity_kw,
            commissioning_date=commissioning_date,
            tariff_rate_pence_per_kwh=tariff_rate_pence_per_kwh,
            tariff_type=tariff_type,
            eligibility_status=SEGEligibilityStatus.PENDING_VERIFICATION,
            smets2_verified=smets2_verified,
        )
        self._accounts.append(account)
        return account

    def mark_eligible(self, account_id: str) -> SEGAccount:
        a = next((x for x in self._accounts if x.account_id == account_id), None)
        if a is None:
            raise KeyError(f"SEG account not found: {account_id}")
        return self._update_account(account_id, eligibility_status=SEGEligibilityStatus.ELIGIBLE)

    def mark_ineligible(self, account_id: str) -> SEGAccount:
        a = next((x for x in self._accounts if x.account_id == account_id), None)
        if a is None:
            raise KeyError(f"SEG account not found: {account_id}")
        return self._update_account(account_id, eligibility_status=SEGEligibilityStatus.INELIGIBLE)

    def suspend(self, account_id: str) -> SEGAccount:
        a = next((x for x in self._accounts if x.account_id == account_id), None)
        if a is None:
            raise KeyError(f"SEG account not found: {account_id}")
        if a.eligibility_status != SEGEligibilityStatus.ELIGIBLE:
            raise ValueError(f"Cannot suspend {a.eligibility_status.value} account")
        return self._update_account(account_id, eligibility_status=SEGEligibilityStatus.SUSPENDED)

    def record_payment(
        self,
        account_id: str,
        period_start: dt.date,
        period_end: dt.date,
        export_kwh: float,
        tariff_rate_pence_per_kwh: Optional[float] = None,
    ) -> SEGPaymentRecord:
        a = next((x for x in self._accounts if x.account_id == account_id), None)
        if a is None:
            raise KeyError(f"SEG account not found: {account_id}")
        if not a.is_eligible:
            raise ValueError(f"Account {account_id} is not eligible for SEG payments")
        if export_kwh < 0:
            raise ValueError("export_kwh cannot be negative")
        rate = tariff_rate_pence_per_kwh if tariff_rate_pence_per_kwh is not None else a.tariff_rate_pence_per_kwh
        payment_gbp = export_kwh * rate / 100.0
        payment = SEGPaymentRecord(
            payment_id=self._next_payment_id(),
            account_id=account_id,
            export_mpan=a.export_mpan,
            period_start=period_start,
            period_end=period_end,
            export_kwh=export_kwh,
            payment_gbp=payment_gbp,
            status=SEGPaymentStatus.PENDING,
        )
        self._payments.append(payment)
        return payment

    def mark_payment_paid(self, payment_id: str) -> SEGPaymentRecord:
        return self._update_payment(payment_id, status=SEGPaymentStatus.PAID)

    def dispute_payment(self, payment_id: str) -> SEGPaymentRecord:
        return self._update_payment(payment_id, status=SEGPaymentStatus.DISPUTED)

    # ── Queries ──────────────────────────────────────────────────────────────

    @property
    def eligible_accounts(self) -> List[SEGAccount]:
        return [a for a in self._accounts if a.is_eligible]

    @property
    def pending_verification_accounts(self) -> List[SEGAccount]:
        return [a for a in self._accounts if a.eligibility_status == SEGEligibilityStatus.PENDING_VERIFICATION]

    def accounts_by_generation_type(self, gen_type: MicroGenerationType) -> List[SEGAccount]:
        return [a for a in self._accounts if a.generation_type == gen_type]

    @property
    def total_enrolled_capacity_kw(self) -> float:
        return sum(a.installed_capacity_kw for a in self.eligible_accounts)

    def total_export_payments_gbp(self) -> float:
        return sum(p.payment_gbp for p in self._payments if p.is_paid)

    def payments_for_account(self, account_id: str) -> List[SEGPaymentRecord]:
        return [p for p in self._payments if p.account_id == account_id]

    def average_tariff_rate_pence(self) -> Optional[float]:
        eligible = self.eligible_accounts
        if not eligible:
            return None
        return round(sum(a.tariff_rate_pence_per_kwh for a in eligible) / len(eligible), 3)

    def seg_summary(self) -> str:
        total = len(self._accounts)
        eligible = len(self.eligible_accounts)
        pending = len(self.pending_verification_accounts)
        capacity = self.total_enrolled_capacity_kw
        paid = self.total_export_payments_gbp()
        avg_rate = self.average_tariff_rate_pence()
        rate_str = f"{avg_rate:.2f}p/kWh" if avg_rate is not None else "N/A"
        return (
            f"SEG Register: {total} enrolled | {eligible} eligible | {pending} pending "
            f"| {capacity:.1f}kW contracted | GBP{paid:,.2f} paid "
            f"| avg rate {rate_str}"
        )
