"""Energy Price Guarantee (EPG) Reconciliation Register (Phase GC).

The Energy Price Guarantee (EPG) ran from 1 October 2022 to 30 June 2023,
replacing the Ofgem price cap as the primary domestic energy support mechanism.

Under the EPG:
  - All domestic customers received a guaranteed unit rate and standing charge
    regardless of their tariff: electricity 34p/kWh, gas 10.3p/kWh,
    electricity standing charge 46p/day, gas standing charge 28p/day
  - Suppliers applied the EPG rates to all bills
  - HM Treasury paid suppliers the difference between EPG rates and their
    actual wholesale procurement costs (via the Energy Markets Financing Scheme)

EPG Schedule (announced Nov 2022, extended):
  Oct–Dec 2022: typical household cost £2,500/year (annualised)
  Jan–Mar 2023: £2,500/year (unchanged)
  Apr–Jun 2023: £3,000/year (raised to begin market normalisation)

Suppliers must:
  1. Track EPG-equivalent billing for each domestic account
  2. Record claims submitted to HMRC for cost recovery
  3. Reconcile final settlement against advance payments
  4. Maintain audit trail for 6 years (HM Revenue & Customs)

This is distinct from:
  - EBSS (Energy Bills Support Scheme) — fixed £400 credit (Phase DE)
  - EBRS (Energy Bill Relief Scheme) — non-domestic equivalent (Phase DD)
  - Ofgem Price Cap — regulatory maximum for SVT (ofgem_price_cap.py)

EPG Rates (BEIS published):
  Electricity: 34p/kWh unit, 46p/day standing charge
  Gas:         10.3p/kWh unit, 28p/day standing charge
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

_EPG_START = dt.date(2022, 10, 1)
_EPG_END = dt.date(2023, 6, 30)

# EPG periods: (start, end) → (elec_unit_pence, gas_unit_pence, description)
_EPG_PERIODS: List[Tuple[dt.date, dt.date, float, float, str]] = [
    (dt.date(2022, 10, 1), dt.date(2023, 3, 31), 34.0, 10.3, "£2,500/yr EPG"),
    (dt.date(2023, 4, 1),  dt.date(2023, 6, 30), 34.0, 10.3, "£3,000/yr EPG"),
]

_EPG_ELEC_UNIT_PENCE = 34.0    # p/kWh
_EPG_GAS_UNIT_PENCE = 10.3     # p/kWh
_EPG_ELEC_STANDING_PENCE = 46.0   # p/day
_EPG_GAS_STANDING_PENCE = 28.0    # p/day


def _is_epg_period(billing_month: dt.date) -> bool:
    """True if the billing month falls within the EPG period."""
    month_start = dt.date(billing_month.year, billing_month.month, 1)
    return _EPG_START <= month_start <= _EPG_END


class EPGClaimStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    PART_PAID = "part_paid"
    SETTLED = "settled"
    DISPUTED = "disputed"


@dataclass(frozen=True)
class EPGMonthlyRecord:
    record_id: str                  # EPG-NNNNN
    billing_month: dt.date          # first day of the billing month
    elec_kwh_billed: float
    gas_kwh_billed: float
    elec_actual_pence_per_kwh: float   # supplier\'s actual cost/contracted rate
    gas_actual_pence_per_kwh: float
    domestic_account_count: int
    claim_status: EPGClaimStatus = EPGClaimStatus.DRAFT

    @property
    def is_eligible(self) -> bool:
        return _is_epg_period(self.billing_month)

    @property
    def elec_epg_revenue_gbp(self) -> float:
        return self.elec_kwh_billed * _EPG_ELEC_UNIT_PENCE / 100.0

    @property
    def gas_epg_revenue_gbp(self) -> float:
        return self.gas_kwh_billed * _EPG_GAS_UNIT_PENCE / 100.0

    @property
    def elec_actual_revenue_gbp(self) -> float:
        return self.elec_kwh_billed * self.elec_actual_pence_per_kwh / 100.0

    @property
    def gas_actual_revenue_gbp(self) -> float:
        return self.gas_kwh_billed * self.gas_actual_pence_per_kwh / 100.0

    @property
    def elec_subsidy_gbp(self) -> float:
        """Amount HMT owes supplier for electricity (actual cost - EPG cap)."""
        return max(0.0, self.elec_actual_revenue_gbp - self.elec_epg_revenue_gbp)

    @property
    def gas_subsidy_gbp(self) -> float:
        """Amount HMT owes supplier for gas."""
        return max(0.0, self.gas_actual_revenue_gbp - self.gas_epg_revenue_gbp)

    @property
    def total_subsidy_gbp(self) -> float:
        return self.elec_subsidy_gbp + self.gas_subsidy_gbp

    @property
    def is_settled(self) -> bool:
        return self.claim_status == EPGClaimStatus.SETTLED

    def record_summary(self) -> str:
        month = self.billing_month.strftime("%Y-%m")
        return (
            f"EPG {self.record_id} ({month}): "
            f"subsidy=£{self.total_subsidy_gbp:,.2f} "
            f"[e={self.elec_subsidy_gbp:,.2f}/g={self.gas_subsidy_gbp:,.2f}] "
            f"status={self.claim_status.value}"
        )


class EPGReconciliationRegister:

    def __init__(self) -> None:
        self._records: List[EPGMonthlyRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return f"EPG-{self._counter:05d}"

    def record_month(
        self,
        billing_month: dt.date,
        elec_kwh_billed: float,
        gas_kwh_billed: float,
        elec_actual_pence_per_kwh: float,
        gas_actual_pence_per_kwh: float,
        domestic_account_count: int,
    ) -> EPGMonthlyRecord:
        month_start = dt.date(billing_month.year, billing_month.month, 1)
        if not _is_epg_period(month_start):
            raise ValueError(
                f"billing_month {billing_month} is outside the EPG period "
                f"({_EPG_START} to {_EPG_END})"
            )
        record = EPGMonthlyRecord(
            record_id=self._next_id(),
            billing_month=month_start,
            elec_kwh_billed=elec_kwh_billed,
            gas_kwh_billed=gas_kwh_billed,
            elec_actual_pence_per_kwh=elec_actual_pence_per_kwh,
            gas_actual_pence_per_kwh=gas_actual_pence_per_kwh,
            domestic_account_count=domestic_account_count,
        )
        self._records.append(record)
        return record

    def _update(self, record_id: str, **kwargs) -> EPGMonthlyRecord:
        for i, r in enumerate(self._records):
            if r.record_id == record_id:
                updated = EPGMonthlyRecord(
                    record_id=r.record_id,
                    billing_month=r.billing_month,
                    elec_kwh_billed=r.elec_kwh_billed,
                    gas_kwh_billed=r.gas_kwh_billed,
                    elec_actual_pence_per_kwh=r.elec_actual_pence_per_kwh,
                    gas_actual_pence_per_kwh=r.gas_actual_pence_per_kwh,
                    domestic_account_count=r.domestic_account_count,
                    claim_status=kwargs.get("claim_status", r.claim_status),
                )
                self._records[i] = updated
                return updated
        raise KeyError(f"EPG record {record_id} not found")

    def submit_claim(self, record_id: str) -> EPGMonthlyRecord:
        return self._update(record_id, claim_status=EPGClaimStatus.SUBMITTED)

    def mark_approved(self, record_id: str) -> EPGMonthlyRecord:
        return self._update(record_id, claim_status=EPGClaimStatus.APPROVED)

    def mark_settled(self, record_id: str) -> EPGMonthlyRecord:
        return self._update(record_id, claim_status=EPGClaimStatus.SETTLED)

    def mark_disputed(self, record_id: str) -> EPGMonthlyRecord:
        return self._update(record_id, claim_status=EPGClaimStatus.DISPUTED)

    def records_for_month(self, billing_month: dt.date) -> List[EPGMonthlyRecord]:
        target = dt.date(billing_month.year, billing_month.month, 1)
        return [r for r in self._records if r.billing_month == target]

    def unsettled_records(self) -> List[EPGMonthlyRecord]:
        return [r for r in self._records if not r.is_settled]

    def disputed_records(self) -> List[EPGMonthlyRecord]:
        return [r for r in self._records if r.claim_status == EPGClaimStatus.DISPUTED]

    def total_subsidy_claimed_gbp(self) -> float:
        return sum(r.total_subsidy_gbp for r in self._records)

    def total_subsidy_settled_gbp(self) -> float:
        return sum(r.total_subsidy_gbp for r in self._records if r.is_settled)

    def outstanding_subsidy_gbp(self) -> float:
        return sum(r.total_subsidy_gbp for r in self._records if not r.is_settled
                   and r.claim_status != EPGClaimStatus.DISPUTED)

    def epg_summary(self) -> str:
        n = len(self._records)
        n_settled = sum(1 for r in self._records if r.is_settled)
        total = self.total_subsidy_claimed_gbp()
        settled = self.total_subsidy_settled_gbp()
        return (
            f"EPG Reconciliation Register: {n} monthly records "
            f"({n_settled} settled). "
            f"Total subsidy claimed: £{total:,.2f}. "
            f"Settled: £{settled:,.2f}."
        )
