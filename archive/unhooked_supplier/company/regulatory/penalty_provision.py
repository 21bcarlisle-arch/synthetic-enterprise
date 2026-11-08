"""Regulatory Penalty Provision Book (Phase EL).

UK energy regulators (Ofgem) can impose financial penalties for:
- SLC (Standard Licence Condition) breaches
- REMIT market manipulation
- Consumer Duty failures
- Billing and metering non-compliance

Ofgem penalty framework (post-2012 Energy Act):
- Max penalty: 10% of licensable UK revenue for licensable infringements
- Disgorgement of unlawful gains (added on top)
- Redress schemes (separate from penalty; customer compensation)

For accounting purposes, a provision must be raised when:
1. There is a present obligation (formal investigation opened, or SLC breach identified)
2. Outflow is probable (>50% likely to result in penalty)
3. Amount can be reliably estimated (IFRS IAS 37)

This module models the company's internal view of its penalty exposure based on
observable regulatory events: Ofgem correspondence received, investigation notices,
SLC breach self-reports.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class InvestigationStatus(str, Enum):
    MONITORING = "monitoring"         # internal watch, no formal notice
    OFGEM_ENQUIRY = "ofgem_enquiry"   # Ofgem informal enquiry received
    FORMAL_INVESTIGATION = "formal_investigation"  # s.26 Electricity Act notice
    REDRESS_REQUIRED = "redress_required"           # penalty + redress agreed
    CLOSED_NO_ACTION = "closed_no_action"
    PENALTY_PAID = "penalty_paid"


class PenaltyBasis(str, Enum):
    SLC_BREACH = "slc_breach"
    CONSUMER_DUTY = "consumer_duty"
    REMIT_BREACH = "remit_breach"
    BILLING_NON_COMPLIANCE = "billing_non_compliance"
    METERING_NON_COMPLIANCE = "metering_non_compliance"


# Probability weights by investigation status (for IAS 37 provisioning)
_PROBABILITY_BY_STATUS = {
    InvestigationStatus.MONITORING: 0.10,
    InvestigationStatus.OFGEM_ENQUIRY: 0.30,
    InvestigationStatus.FORMAL_INVESTIGATION: 0.65,
    InvestigationStatus.REDRESS_REQUIRED: 0.95,
    InvestigationStatus.CLOSED_NO_ACTION: 0.0,
    InvestigationStatus.PENALTY_PAID: 1.0,
}

# Ofgem public benchmarks (2019-2023 penalty history, £ per case type)
_TYPICAL_PENALTY_BY_BASIS = {
    PenaltyBasis.SLC_BREACH: 500_000.0,
    PenaltyBasis.CONSUMER_DUTY: 750_000.0,
    PenaltyBasis.REMIT_BREACH: 2_000_000.0,
    PenaltyBasis.BILLING_NON_COMPLIANCE: 200_000.0,
    PenaltyBasis.METERING_NON_COMPLIANCE: 150_000.0,
}

_MATERIAL_PROVISION_THRESHOLD_GBP = 50_000.0


@dataclass(frozen=True)
class PenaltyProvisionRecord:
    case_id: str
    basis: PenaltyBasis
    status: InvestigationStatus
    opened_at: dt.date
    estimated_penalty_gbp: float
    redress_estimate_gbp: float = 0.0
    closed_at: Optional[dt.date] = None

    @property
    def probability_of_penalty(self) -> float:
        return _PROBABILITY_BY_STATUS[self.status]

    @property
    def expected_penalty_gbp(self) -> float:
        return self.estimated_penalty_gbp * self.probability_of_penalty

    @property
    def expected_redress_gbp(self) -> float:
        return self.redress_estimate_gbp * self.probability_of_penalty

    @property
    def total_expected_exposure_gbp(self) -> float:
        return self.expected_penalty_gbp + self.expected_redress_gbp

    @property
    def is_active(self) -> bool:
        return self.status not in (
            InvestigationStatus.CLOSED_NO_ACTION,
            InvestigationStatus.PENALTY_PAID,
        )

    @property
    def is_material(self) -> bool:
        return self.total_expected_exposure_gbp >= _MATERIAL_PROVISION_THRESHOLD_GBP

    def provision_summary(self) -> str:
        return (
            "Case " + self.case_id + " (" + self.basis.value + "): "
            "status=" + self.status.value
            + " prob=" + str(round(self.probability_of_penalty * 100)) + "%"
            + " expected=GBP" + str(round(self.total_expected_exposure_gbp))
        )


class RegulatoryPenaltyProvisionBook:

    def __init__(self) -> None:
        self._cases: List[PenaltyProvisionRecord] = []
        self._next_id = 1

    def open_case(
        self,
        basis: PenaltyBasis,
        status: InvestigationStatus,
        opened_at: dt.date,
        estimated_penalty_gbp: Optional[float] = None,
        redress_estimate_gbp: float = 0.0,
    ) -> PenaltyProvisionRecord:
        if estimated_penalty_gbp is None:
            estimated_penalty_gbp = _TYPICAL_PENALTY_BY_BASIS[basis]
        case_id = "REG-" + str(self._next_id).zfill(4)
        self._next_id += 1
        rec = PenaltyProvisionRecord(
            case_id=case_id,
            basis=basis,
            status=status,
            opened_at=opened_at,
            estimated_penalty_gbp=estimated_penalty_gbp,
            redress_estimate_gbp=redress_estimate_gbp,
        )
        self._cases.append(rec)
        return rec

    def update_status(self, case_id: str, new_status: InvestigationStatus,
                      as_of: dt.date) -> Optional[PenaltyProvisionRecord]:
        for i, c in enumerate(self._cases):
            if c.case_id == case_id:
                closed = as_of if new_status in (
                    InvestigationStatus.CLOSED_NO_ACTION,
                    InvestigationStatus.PENALTY_PAID,
                ) else c.closed_at
                updated = PenaltyProvisionRecord(
                    case_id=c.case_id,
                    basis=c.basis,
                    status=new_status,
                    opened_at=c.opened_at,
                    estimated_penalty_gbp=c.estimated_penalty_gbp,
                    redress_estimate_gbp=c.redress_estimate_gbp,
                    closed_at=closed,
                )
                self._cases[i] = updated
                return updated
        return None

    def active_cases(self) -> List[PenaltyProvisionRecord]:
        return [c for c in self._cases if c.is_active]

    def material_cases(self) -> List[PenaltyProvisionRecord]:
        return [c for c in self._cases if c.is_active and c.is_material]

    def formal_investigations(self) -> List[PenaltyProvisionRecord]:
        return [c for c in self._cases
                if c.status == InvestigationStatus.FORMAL_INVESTIGATION]

    def total_provision_gbp(self) -> float:
        return sum(c.total_expected_exposure_gbp for c in self.active_cases())

    def penalty_provision_summary(self, as_of: dt.date) -> str:
        n = len(self.active_cases())
        n_material = len(self.material_cases())
        n_formal = len(self.formal_investigations())
        return (
            "Regulatory Provisions (" + str(as_of) + "): "
            + str(n) + " active cases, "
            + str(n_formal) + " formal investigations, "
            + str(n_material) + " material. "
            "Total provision: GBP" + str(round(self.total_provision_gbp())) + "."
        )
