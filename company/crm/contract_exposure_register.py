"""Contract Exposure Register — tracks regulatory supply obligations.

As a licensed UK energy supplier, the company has a regulatory obligation
to supply each customer it has contracted with. The obligation does NOT
automatically end when a fixed-rate contract expires:

1. On contract expiry, customers roll onto SVT (Standard Variable Tariff)
   or Default Tariff Cap rate by operation of licence (SLC 22, 23)
2. The company continues to supply (and bear wholesale price risk) until:
   a. The customer switches to a new supplier
   b. The company agrees to transfer the customer to SoLR (Ph321)
   c. The customer vacates (COT event)
3. For I&C customers, lapse onto "out-of-contract" (OOC) rate

This register tracks:
- Which customers are on fixed contracts vs SVT/OOC
- Days remaining on each contract
- Forward revenue commitment (revenue under contract vs at-risk on SVT)
- Customers approaching contract end (renewal pipeline)

Epistemic constraint: the company knows its own contracts. It does NOT
know the forward wholesale price the SVT customers will cost to serve
after their contract expires.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from enum import Enum


class ContractStatus(str, Enum):
    FIXED_TERM = "fixed_term"         # Fixed unit rate / fixed period
    STANDARD_VARIABLE = "standard_variable"  # SVT after fixed-term expiry
    OUT_OF_CONTRACT = "out_of_contract"       # I&C OOC — supplier may end supply
    DEEMED = "deemed"                  # New occupant / auto-supply (Phase 322)
    PENDING_RENEWAL = "pending_renewal"  # Within 42-day SLC 22 notice window


class ContractSegment(str, Enum):
    DOMESTIC = "domestic"
    SME = "sme"
    INDUSTRIAL_COMMERCIAL = "industrial_commercial"


@dataclass(frozen=True)
class ContractRecord:
    account_id: str
    segment: ContractSegment
    status: ContractStatus
    contract_start: date
    contract_end: date | None      # None = open-ended (SVT)
    annual_kwh: float
    unit_rate_gbp_per_kwh: float
    standing_charge_gbp_per_day: float
    notice_issued: bool = False    # SLC 22 renewal notice sent

    @property
    def is_fixed_term(self) -> bool:
        return self.status == ContractStatus.FIXED_TERM

    @property
    def is_svt(self) -> bool:
        return self.status == ContractStatus.STANDARD_VARIABLE

    @property
    def days_remaining(self) -> int | None:
        """Days until contract end. None for open-ended contracts."""
        if self.contract_end is None:
            return None
        today = date.today()
        return max(0, (self.contract_end - today).days)

    @property
    def is_in_notice_window(self) -> bool:
        """Within SLC 22 42-day renewal notice window."""
        days = self.days_remaining
        return days is not None and 0 < days <= 42

    @property
    def annual_contract_revenue_gbp(self) -> float:
        return (
            self.annual_kwh * self.unit_rate_gbp_per_kwh
            + self.standing_charge_gbp_per_day * 365
        )


class ContractExposureRegister:
    """Tracks all supply contracts and the company's forward obligations."""

    def __init__(self) -> None:
        self._contracts: dict[str, ContractRecord] = {}

    def register_contract(self, record: ContractRecord) -> ContractRecord:
        self._contracts[record.account_id] = record
        return record

    def get_contract(self, account_id: str) -> ContractRecord | None:
        return self._contracts.get(account_id)

    @property
    def all_contracts(self) -> list[ContractRecord]:
        return list(self._contracts.values())

    @property
    def fixed_term_contracts(self) -> list[ContractRecord]:
        return [c for c in self._contracts.values() if c.is_fixed_term]

    @property
    def svt_contracts(self) -> list[ContractRecord]:
        return [c for c in self._contracts.values() if c.is_svt]

    @property
    def in_notice_window(self) -> list[ContractRecord]:
        """Contracts requiring SLC 22 renewal notice to be issued."""
        return [c for c in self._contracts.values() if c.is_in_notice_window]

    @property
    def notice_not_issued(self) -> list[ContractRecord]:
        """Contracts in notice window where notice has not been sent — SLC 22 breach risk."""
        return [c for c in self.in_notice_window if not c.notice_issued]

    @property
    def total_annual_revenue_gbp(self) -> float:
        return sum(c.annual_contract_revenue_gbp for c in self._contracts.values())

    @property
    def fixed_term_revenue_gbp(self) -> float:
        return sum(c.annual_contract_revenue_gbp for c in self.fixed_term_contracts)

    @property
    def svt_revenue_at_risk_gbp(self) -> float:
        """SVT revenue is at-risk — customer may switch at any time."""
        return sum(c.annual_contract_revenue_gbp for c in self.svt_contracts)

    def contracts_by_segment(self, segment: ContractSegment) -> list[ContractRecord]:
        return [c for c in self._contracts.values() if c.segment == segment]

    def exposure_summary(self) -> str:
        n_total = len(self._contracts)
        n_fixed = len(self.fixed_term_contracts)
        n_svt = len(self.svt_contracts)
        n_at_risk_notice = len(self.notice_not_issued)
        lines = [
            "Contract Exposure Register",
            "Total: {:d} | Fixed: {:d} | SVT: {:d}".format(n_total, n_fixed, n_svt),
            "Annual revenue: £{:,.0f} | SVT at-risk: £{:,.0f}".format(
                self.total_annual_revenue_gbp, self.svt_revenue_at_risk_gbp
            ),
            "In notice window: {:d} | Notice not issued: {:d}".format(
                len(self.in_notice_window), n_at_risk_notice
            ),
        ]
        return chr(10).join(lines)
