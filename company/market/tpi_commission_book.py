"""Third-Party Intermediary (TPI) commission tracking for I&C customers.

In the UK I&C energy market, most business customers are acquired through
Third Party Intermediaries (TPIs) — energy brokers, consultants, or
comparison sites. Suppliers pay TPIs commissions (typically £2-25/MWh
depending on contract size, length, and broker tier).

Ofgem has regulated TPI commissions since 2022 (Microbusiness Compliance
Principles, Business Energy Switching and Saving Mandate). Non-domestic
suppliers must disclose commission amounts to customers.

Commission types:
- Upfront: one-off payment at contract signature (acquisition)
- Trail: ongoing per-MWh or per-annum payment through contract term

This module tracks TPI relationships, commission agreements, and payments.
Epistemic constraint: company observes its own commission payables from
contract records — no SIM internals.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TPITier(str, Enum):
    """Ofgem-aligned TPI tier classification."""
    NATIONAL = "national"       # Large national brokers (e.g. Make It Cheaper, Utilitywise)
    REGIONAL = "regional"       # Regional/SME focused brokers
    INDEPENDENT = "independent" # Single-person or micro brokers
    ONLINE = "online"           # Comparison sites


class CommissionType(str, Enum):
    UPFRONT = "upfront"   # Paid once at contract signing
    TRAIL = "trail"       # Ongoing per-MWh or per-term
    HYBRID = "hybrid"     # Partial upfront + ongoing trail


@dataclass(frozen=True)
class TPIAgreement:
    tpi_id: str
    tpi_name: str
    tier: TPITier
    commission_type: CommissionType
    upfront_gbp: float = 0.0
    trail_gbp_per_mwh: float = 0.0
    is_disclosed_to_customer: bool = False
    customer_id: Optional[str] = None
    contract_start_year: Optional[int] = None

    @property
    def annual_trail_gbp(self) -> float:
        """Trail commission paid per year (requires knowing annual consumption)."""
        return 0.0  # Calculated by TPICommissionBook using customer EAC

    @property
    def is_compliant(self) -> bool:
        """Ofgem: all non-domestic TPI commissions must be disclosed."""
        return self.is_disclosed_to_customer


@dataclass(frozen=True)
class TPIPayment:
    payment_id: str
    tpi_id: str
    customer_id: str
    payment_year: int
    commission_type: CommissionType
    amount_gbp: float
    annual_kwh: float = 0.0

    @property
    def rate_gbp_per_mwh(self) -> float:
        if self.annual_kwh <= 0:
            return 0.0
        return self.amount_gbp / (self.annual_kwh / 1000)


class TPICommissionBook:
    """Tracks TPI agreements and commission payments across the I&C portfolio."""

    def __init__(self) -> None:
        self._agreements: dict[str, TPIAgreement] = {}
        self._payments: list[TPIPayment] = []

    def register_tpi(
        self,
        tpi_id: str,
        tpi_name: str,
        tier: TPITier,
        commission_type: CommissionType,
        upfront_gbp: float = 0.0,
        trail_gbp_per_mwh: float = 0.0,
        is_disclosed: bool = False,
        customer_id: Optional[str] = None,
        contract_start_year: Optional[int] = None,
    ) -> TPIAgreement:
        agreement = TPIAgreement(
            tpi_id=tpi_id,
            tpi_name=tpi_name,
            tier=tier,
            commission_type=commission_type,
            upfront_gbp=upfront_gbp,
            trail_gbp_per_mwh=trail_gbp_per_mwh,
            is_disclosed_to_customer=is_disclosed,
            customer_id=customer_id,
            contract_start_year=contract_start_year,
        )
        self._agreements[tpi_id] = agreement
        return agreement

    def record_payment(
        self,
        payment_id: str,
        tpi_id: str,
        customer_id: str,
        payment_year: int,
        commission_type: CommissionType,
        amount_gbp: float,
        annual_kwh: float = 0.0,
    ) -> TPIPayment:
        payment = TPIPayment(
            payment_id=payment_id,
            tpi_id=tpi_id,
            customer_id=customer_id,
            payment_year=payment_year,
            commission_type=commission_type,
            amount_gbp=amount_gbp,
            annual_kwh=annual_kwh,
        )
        self._payments.append(payment)
        return payment

    @property
    def all_agreements(self) -> list[TPIAgreement]:
        return list(self._agreements.values())

    @property
    def non_compliant_agreements(self) -> list[TPIAgreement]:
        return [a for a in self._agreements.values() if not a.is_compliant]

    def payments_for_year(self, year: int) -> list[TPIPayment]:
        return [p for p in self._payments if p.payment_year == year]

    def payments_for_customer(self, customer_id: str) -> list[TPIPayment]:
        return [p for p in self._payments if p.customer_id == customer_id]

    def total_commission_gbp(self) -> float:
        return sum(p.amount_gbp for p in self._payments)

    def total_for_year(self, year: int) -> float:
        return sum(p.amount_gbp for p in self.payments_for_year(year))

    def avg_rate_gbp_per_mwh(self) -> float:
        """Average commission rate across all trail payments with consumption data."""
        trail_payments = [p for p in self._payments
                         if p.commission_type in (CommissionType.TRAIL, CommissionType.HYBRID)
                         and p.annual_kwh > 0]
        if not trail_payments:
            return 0.0
        return sum(p.rate_gbp_per_mwh for p in trail_payments) / len(trail_payments)

    def tpi_summary(self) -> str:
        n_tpis = len(self._agreements)
        n_payments = len(self._payments)
        total = self.total_commission_gbp()
        non_compliant = len(self.non_compliant_agreements)
        avg_rate = self.avg_rate_gbp_per_mwh()
        lines = [
            "TPI Commission Book Summary",
            "TPIs registered: {:d}".format(n_tpis),
            "Total payments: {:d} | Total: £{:,.0f}".format(n_payments, total),
            "Non-disclosed (compliance risk): {:d}".format(non_compliant),
        ]
        if avg_rate > 0:
            lines.append("Avg trail rate: £{:.2f}/MWh".format(avg_rate))
        return chr(10).join(lines)
