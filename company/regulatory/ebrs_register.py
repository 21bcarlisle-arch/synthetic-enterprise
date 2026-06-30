"""Energy Bill Relief Scheme (EBRS) Register.

UK government scheme: October 2022 - March 2023.
Non-domestic customers on fixed-rate contracts above the EBRS baseline
received a per-unit discount applied automatically by their supplier.
Suppliers recovered the subsidy from BEIS/DESNZ via quarterly reconciliation.

Key parameters:
- EBRS electricity baseline: 21.1 p/kWh (wholesale equivalent)
- EBRS gas baseline: 7.5 p/kWh
- Eligible period: 2022-10-01 to 2023-03-31 (6 months)
- Eligible customers: non-domestic only (I&C, SME); residential = separate Energy Price Guarantee
- Maximum subsidy: contract rate minus baseline (supplier caps the discount at this level)
- Domestic equivalent: Energy Price Guarantee (EPG) - separate scheme, separate register
- Total government cost: approximately GBP 5.5B for EBRS

BEIS guidance: www.gov.uk/guidance/energy-bill-relief-scheme
Energy Bills Support Scheme (EBSS): domestic equivalent (GBP 400 credit Oct22-Mar23)

Epistemic: company knows which contracts are above EBRS baseline and what
discount it applied and claimed back from government. It does not see the
simulation forward curve or the reason why prices rose (gas supply disruption).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


_EBRS_START = dt.date(2022, 10, 1)
_EBRS_END = dt.date(2023, 3, 31)
_EBRS_ELECTRICITY_BASELINE_P_KWH = 21.1
_EBRS_GAS_BASELINE_P_KWH = 7.5


class EBRSFuel(str, Enum):
    ELECTRICITY = "electricity"
    GAS = "gas"


class EBRSEligibilityStatus(str, Enum):
    ELIGIBLE = "eligible"
    INELIGIBLE_RESIDENTIAL = "ineligible_residential"
    INELIGIBLE_BELOW_BASELINE = "ineligible_below_baseline"
    INELIGIBLE_OUTSIDE_PERIOD = "ineligible_outside_period"


class RecoveryStatus(str, Enum):
    PENDING = "pending"
    CLAIMED = "claimed"
    PAID_BY_GOVERNMENT = "paid_by_government"
    DISPUTED = "disputed"


def _ebrs_baseline(fuel: EBRSFuel) -> float:
    return _EBRS_ELECTRICITY_BASELINE_P_KWH if fuel == EBRSFuel.ELECTRICITY else _EBRS_GAS_BASELINE_P_KWH


def is_eligible_period(billing_month: dt.date) -> bool:
    """True if this month falls within the EBRS window Oct 2022 - Mar 2023."""
    start = dt.date(billing_month.year, billing_month.month, 1)
    return _EBRS_START <= start <= _EBRS_END


@dataclass(frozen=True)
class EBRSRecord:
    record_id: str
    customer_id: str
    fuel: EBRSFuel
    billing_month: dt.date               # first day of billing month
    contract_unit_rate_p_kwh: float      # customer contract rate
    consumption_kwh: float
    eligibility: EBRSEligibilityStatus
    discount_applied_p_kwh: float        # = max(0, contract_rate - baseline)
    discount_applied_gbp: float          # = discount_p_kwh * consumption / 100
    recovery_status: RecoveryStatus
    claimed_at: Optional[dt.date] = None
    government_ref: Optional[str] = None

    @property
    def is_eligible(self) -> bool:
        return self.eligibility == EBRSEligibilityStatus.ELIGIBLE

    @property
    def is_recovered(self) -> bool:
        return self.recovery_status == RecoveryStatus.PAID_BY_GOVERNMENT

    @property
    def outstanding_recovery_gbp(self) -> float:
        if self.recovery_status == RecoveryStatus.PAID_BY_GOVERNMENT:
            return 0.0
        return self.discount_applied_gbp if self.is_eligible else 0.0


def _assess_eligibility(
    fuel: EBRSFuel,
    contract_unit_rate_p_kwh: float,
    billing_month: dt.date,
    is_domestic: bool,
) -> tuple:
    """Returns (EBRSEligibilityStatus, discount_p_kwh)."""
    if is_domestic:
        return EBRSEligibilityStatus.INELIGIBLE_RESIDENTIAL, 0.0
    if not is_eligible_period(billing_month):
        return EBRSEligibilityStatus.INELIGIBLE_OUTSIDE_PERIOD, 0.0
    baseline = _ebrs_baseline(fuel)
    if contract_unit_rate_p_kwh <= baseline:
        return EBRSEligibilityStatus.INELIGIBLE_BELOW_BASELINE, 0.0
    discount = contract_unit_rate_p_kwh - baseline
    return EBRSEligibilityStatus.ELIGIBLE, discount


class EBRSRegister:
    """Tracks EBRS discount applications and government recovery claims."""

    def __init__(self) -> None:
        self._records: Dict[str, EBRSRecord] = {}
        self._seq = 0

    def _next_id(self) -> str:
        self._seq += 1
        return f"EBRS-{self._seq:05d}"

    def record_billing_month(
        self,
        customer_id: str,
        fuel: EBRSFuel,
        billing_month: dt.date,
        contract_unit_rate_p_kwh: float,
        consumption_kwh: float,
        is_domestic: bool,
    ) -> EBRSRecord:
        rid = self._next_id()
        elig, discount_p_kwh = _assess_eligibility(
            fuel, contract_unit_rate_p_kwh, billing_month, is_domestic,
        )
        discount_gbp = round(discount_p_kwh * consumption_kwh / 100, 2)
        rec = EBRSRecord(
            record_id=rid, customer_id=customer_id, fuel=fuel,
            billing_month=billing_month, contract_unit_rate_p_kwh=contract_unit_rate_p_kwh,
            consumption_kwh=consumption_kwh, eligibility=elig,
            discount_applied_p_kwh=round(discount_p_kwh, 4),
            discount_applied_gbp=discount_gbp,
            recovery_status=RecoveryStatus.PENDING,
        )
        self._records[rid] = rec
        return rec

    def claim_recovery(
        self, record_id: str, claimed_at: dt.date,
        government_ref: Optional[str] = None,
    ) -> EBRSRecord:
        rec = self._records[record_id]
        if not rec.is_eligible:
            raise ValueError(f"{record_id} is not eligible for EBRS recovery")
        updated = EBRSRecord(
            record_id=rec.record_id, customer_id=rec.customer_id, fuel=rec.fuel,
            billing_month=rec.billing_month,
            contract_unit_rate_p_kwh=rec.contract_unit_rate_p_kwh,
            consumption_kwh=rec.consumption_kwh, eligibility=rec.eligibility,
            discount_applied_p_kwh=rec.discount_applied_p_kwh,
            discount_applied_gbp=rec.discount_applied_gbp,
            recovery_status=RecoveryStatus.CLAIMED,
            claimed_at=claimed_at, government_ref=government_ref,
        )
        self._records[record_id] = updated
        return updated

    def mark_paid(self, record_id: str, government_ref: str) -> EBRSRecord:
        rec = self._records[record_id]
        updated = EBRSRecord(
            record_id=rec.record_id, customer_id=rec.customer_id, fuel=rec.fuel,
            billing_month=rec.billing_month,
            contract_unit_rate_p_kwh=rec.contract_unit_rate_p_kwh,
            consumption_kwh=rec.consumption_kwh, eligibility=rec.eligibility,
            discount_applied_p_kwh=rec.discount_applied_p_kwh,
            discount_applied_gbp=rec.discount_applied_gbp,
            recovery_status=RecoveryStatus.PAID_BY_GOVERNMENT,
            claimed_at=rec.claimed_at, government_ref=government_ref,
        )
        self._records[record_id] = updated
        return updated

    # ── Queries ──────────────────────────────────────────────────────────────

    @property
    def eligible_records(self) -> List[EBRSRecord]:
        return [r for r in self._records.values() if r.is_eligible]

    @property
    def total_discount_applied_gbp(self) -> float:
        return sum(r.discount_applied_gbp for r in self.eligible_records)

    @property
    def total_outstanding_recovery_gbp(self) -> float:
        return sum(r.outstanding_recovery_gbp for r in self._records.values())

    @property
    def total_recovered_gbp(self) -> float:
        return sum(r.discount_applied_gbp for r in self.eligible_records
                   if r.is_recovered)

    def records_for_customer(self, customer_id: str) -> List[EBRSRecord]:
        return [r for r in self._records.values() if r.customer_id == customer_id]

    def by_fuel(self) -> Dict[str, float]:
        out: Dict[str, float] = {}
        for r in self.eligible_records:
            key = r.fuel.value
            out[key] = out.get(key, 0.0) + r.discount_applied_gbp
        return out

    def pending_claims(self) -> List[EBRSRecord]:
        return [r for r in self.eligible_records
                if r.recovery_status == RecoveryStatus.PENDING]

    def ebrs_summary(self) -> str:
        total = len(self._records)
        eligible = len(self.eligible_records)
        applied = self.total_discount_applied_gbp
        outstanding = self.total_outstanding_recovery_gbp
        recovered = self.total_recovered_gbp
        by_fuel = self.by_fuel()
        return (
            f"EBRS Register (Oct22-Mar23): {total} billing-month records, {eligible} eligible. "
            f"Total discount applied: GBP{applied:,.2f}. "
            f"Recovered from BEIS: GBP{recovered:,.2f}. Outstanding: GBP{outstanding:,.2f}. "
            f"By fuel: {by_fuel}."
        )
