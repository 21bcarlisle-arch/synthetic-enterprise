"""Feed-in Tariff (FiT) Legacy Register.

The Feed-in Tariff scheme (FIT Regulations 2010 / SI 2010/678) was closed to
new applicants in March 2019. However, existing FiT customers continue to
receive generation and export payments for the remainder of their 20-year
term. Obligated licensees (>250,000 domestic customers) act as FIT licensees
and must pay accredited generators quarterly.

Key FiT rules:
  - Generation tariff: levelised at commissioning date (frozen for 20 years).
  - Export tariff: guaranteed or deemed (50% of generation if no export meter).
  - Meter reads: required quarterly for generation; export meter reads or deemed.
  - Annual uplift: tariffs rise with RPI annually (pre-2014 installs).
  - FiT Levelisation: suppliers recover costs via the FIT Levy on all suppliers.

Distinct from seg_register.py (SEG replaced FiT exports from Jan 2020 for
new applicants; legacy FiT customers have separate rights until term end).

Epistemic: tariff rates frozen at commissioning are known to company records.
Generation reads come from meter data. Export reads from smart meter or deemed.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class FITTechnology(str, Enum):
    SOLAR_PV = "solar_pv"
    WIND = "wind"
    HYDRO = "hydro"
    MICRO_CHP = "micro_chp"
    ANAEROBIC_DIGESTION = "anaerobic_digestion"


class FITPaymentType(str, Enum):
    GENERATION = "generation"
    EXPORT = "export"


class FITPaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    DISPUTED = "disputed"
    RECOVERY_REQUIRED = "recovery_required"  # overpaid


# FiT scheme closed to new applicants
_FIT_SCHEME_CLOSE = dt.date(2019, 3, 31)
# Standard term length in years
_FIT_TERM_YEARS = 20
# Default deemed export fraction (50% of generation if no export meter)
_DEEMED_EXPORT_FRACTION = 0.50


@dataclass(frozen=True)
class FITLegacyRecord:
    account_id: str
    export_mpan: str
    technology: FITTechnology
    installed_capacity_kw: float
    commissioning_date: dt.date
    term_end_date: dt.date                        # commissioning + 20 years
    generation_tariff_pence_per_kwh: float        # frozen at commissioning
    export_tariff_pence_per_kwh: float            # frozen at commissioning
    has_export_meter: bool = True

    @property
    def is_deemed_export(self) -> bool:
        return not self.has_export_meter

    def is_active_as_of(self, as_of: dt.date) -> bool:
        return self.commissioning_date <= as_of <= self.term_end_date

    def is_expired_as_of(self, as_of: dt.date) -> bool:
        return as_of > self.term_end_date

    def years_remaining(self, as_of: dt.date) -> float:
        if self.is_expired_as_of(as_of):
            return 0.0
        return (self.term_end_date - as_of).days / 365.25

    def annual_generation_payment_estimate_gbp(self, annual_generation_kwh: float) -> float:
        return annual_generation_kwh * self.generation_tariff_pence_per_kwh / 100.0

    def fit_summary(self) -> str:
        return (
            f"FiT {self.account_id}: {self.technology.value} "
            f"{self.installed_capacity_kw:.1f}kW "
            f"gen={self.generation_tariff_pence_per_kwh:.2f}p/kWh "
            f"exp={self.export_tariff_pence_per_kwh:.2f}p/kWh "
            f"ends={self.term_end_date}"
        )


@dataclass(frozen=True)
class FITPaymentRecord:
    payment_id: str
    account_id: str
    payment_type: FITPaymentType
    period_start: dt.date
    period_end: dt.date
    units_kwh: float
    payment_gbp: float
    status: FITPaymentStatus

    @property
    def is_paid(self) -> bool:
        return self.status == FITPaymentStatus.PAID


class FITLegacyRegister:
    """Register of legacy Feed-in Tariff customers and their quarterly payments."""

    def __init__(self) -> None:
        self._customers: List[FITLegacyRecord] = []
        self._payments: List[FITPaymentRecord] = []
        self._payment_counter: int = 0

    def _next_payment_id(self) -> str:
        self._payment_counter += 1
        return "FITPAY-" + str(self._payment_counter).zfill(5)

    def _update_payment(self, payment_id: str, **kwargs) -> FITPaymentRecord:
        for i, p in enumerate(self._payments):
            if p.payment_id == payment_id:
                updated = FITPaymentRecord(**{**p.__dict__, **kwargs})
                self._payments[i] = updated
                return updated
        raise KeyError(f"Payment not found: {payment_id}")

    def register_fit_customer(
        self,
        account_id: str,
        export_mpan: str,
        technology: FITTechnology,
        installed_capacity_kw: float,
        commissioning_date: dt.date,
        generation_tariff_pence_per_kwh: float,
        export_tariff_pence_per_kwh: float,
        has_export_meter: bool = True,
    ) -> FITLegacyRecord:
        if commissioning_date > _FIT_SCHEME_CLOSE:
            raise ValueError(
                f"FiT scheme closed to new applicants {_FIT_SCHEME_CLOSE}; "
                f"commissioning {commissioning_date} is invalid"
            )
        if installed_capacity_kw <= 0:
            raise ValueError("installed_capacity_kw must be positive")
        if generation_tariff_pence_per_kwh < 0 or export_tariff_pence_per_kwh < 0:
            raise ValueError("Tariff rates cannot be negative")
        # Term ends 20 years from commissioning (calendar years approximate)
        import datetime
        try:
            term_end = commissioning_date.replace(year=commissioning_date.year + _FIT_TERM_YEARS)
        except ValueError:
            # Feb 29 edge case: use March 1
            term_end = dt.date(commissioning_date.year + _FIT_TERM_YEARS, 3, 1)
        rec = FITLegacyRecord(
            account_id=account_id,
            export_mpan=export_mpan,
            technology=technology,
            installed_capacity_kw=installed_capacity_kw,
            commissioning_date=commissioning_date,
            term_end_date=term_end,
            generation_tariff_pence_per_kwh=generation_tariff_pence_per_kwh,
            export_tariff_pence_per_kwh=export_tariff_pence_per_kwh,
            has_export_meter=has_export_meter,
        )
        self._customers.append(rec)
        return rec

    def record_payment(
        self,
        account_id: str,
        payment_type: FITPaymentType,
        period_start: dt.date,
        period_end: dt.date,
        units_kwh: float,
        rate_override_pence_per_kwh: Optional[float] = None,
    ) -> FITPaymentRecord:
        customer = next((c for c in self._customers if c.account_id == account_id), None)
        if customer is None:
            raise KeyError(f"FiT customer not found: {account_id}")
        if units_kwh < 0:
            raise ValueError("units_kwh cannot be negative")
        if payment_type == FITPaymentType.GENERATION:
            rate = rate_override_pence_per_kwh or customer.generation_tariff_pence_per_kwh
        else:
            rate = rate_override_pence_per_kwh or customer.export_tariff_pence_per_kwh
            # Apply deemed export fraction if no meter
            if customer.is_deemed_export and rate_override_pence_per_kwh is None:
                units_kwh = units_kwh * _DEEMED_EXPORT_FRACTION
        payment_gbp = units_kwh * rate / 100.0
        payment = FITPaymentRecord(
            payment_id=self._next_payment_id(),
            account_id=account_id,
            payment_type=payment_type,
            period_start=period_start,
            period_end=period_end,
            units_kwh=units_kwh,
            payment_gbp=payment_gbp,
            status=FITPaymentStatus.PENDING,
        )
        self._payments.append(payment)
        return payment

    def mark_paid(self, payment_id: str) -> FITPaymentRecord:
        return self._update_payment(payment_id, status=FITPaymentStatus.PAID)

    def dispute_payment(self, payment_id: str) -> FITPaymentRecord:
        return self._update_payment(payment_id, status=FITPaymentStatus.DISPUTED)

    def flag_recovery_required(self, payment_id: str) -> FITPaymentRecord:
        return self._update_payment(payment_id, status=FITPaymentStatus.RECOVERY_REQUIRED)

    # ── Queries ──────────────────────────────────────────────────────────────

    @property
    def all_customers(self) -> List[FITLegacyRecord]:
        return list(self._customers)

    def active_customers(self, as_of: dt.date) -> List[FITLegacyRecord]:
        return [c for c in self._customers if c.is_active_as_of(as_of)]

    def expired_customers(self, as_of: dt.date) -> List[FITLegacyRecord]:
        return [c for c in self._customers if c.is_expired_as_of(as_of)]

    def expiring_within(self, as_of: dt.date, days: int = 365) -> List[FITLegacyRecord]:
        cutoff = as_of + dt.timedelta(days=days)
        return [
            c for c in self._customers
            if c.is_active_as_of(as_of) and c.term_end_date <= cutoff
        ]

    def customers_by_technology(self, technology: FITTechnology) -> List[FITLegacyRecord]:
        return [c for c in self._customers if c.technology == technology]

    def payments_for_account(self, account_id: str) -> List[FITPaymentRecord]:
        return [p for p in self._payments if p.account_id == account_id]

    @property
    def total_generation_payments_paid_gbp(self) -> float:
        return sum(
            p.payment_gbp for p in self._payments
            if p.is_paid and p.payment_type == FITPaymentType.GENERATION
        )

    @property
    def total_export_payments_paid_gbp(self) -> float:
        return sum(
            p.payment_gbp for p in self._payments
            if p.is_paid and p.payment_type == FITPaymentType.EXPORT
        )

    @property
    def total_payments_paid_gbp(self) -> float:
        return sum(p.payment_gbp for p in self._payments if p.is_paid)

    def fit_register_summary(self, as_of: dt.date) -> str:
        total = len(self._customers)
        active = len(self.active_customers(as_of))
        expired = len(self.expired_customers(as_of))
        expiring = len(self.expiring_within(as_of, 365))
        gen_paid = self.total_generation_payments_paid_gbp
        exp_paid = self.total_export_payments_paid_gbp
        return (
            f"FiT Legacy: {total} customers | {active} active | {expired} expired "
            f"| {expiring} expiring within 1yr "
            f"| GBP{gen_paid:,.2f} gen paid | GBP{exp_paid:,.2f} export paid"
        )
