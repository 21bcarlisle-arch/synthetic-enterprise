"""Revenue Protection Register.

Revenue protection (RP) is a supplier function that identifies and
quantifies revenue losses due to:
1. Meter tampering (most common): customer bypasses/removes meter
2. Illegal reconnection: customer reconnects after disconnection
3. Meter bypassing: diversion of supply before meter
4. Estimation fraud: manipulating meter reads

In GB, revenue protection is governed by (read_access_and_theft_duties.md §2.2, §3.1):
- SLC 12 and 12A, both fuels: detect, investigate and prevent theft; the 12A.11 investigation
  standards; party to REC Schedule 7 (TRAS, ETTOS, TDIS).
- Electricity Act 1989 Sch 6 para 7 (powers of entry to read, inspect or remove a meter) and
  para 10 (obstruction); Gas Act 1986 Sch 2B para 23 and 28. Entry against the occupier's will
  needs a warrant (Rights of Entry Act 1954 s.1-2).
Corrected 2026-10-06: this cited "Electricity Act 1989 Section 10"; the Act's entry, theft and
meter provisions are Schedules 6 and 7, not s.10. It also cited "GS(SS)5", found in no source
read, and "Gas Safety (Management) Regulations 1996", which no source read ties to revenue
protection; both are dropped.

When RP identifies a case:
1. DNO notified under DCUSA Clause 30.9 (via SLC 12A.3). Deadline: GAP, not read.
2. Assessed volume entered into settlement and billed. SLC 21BA.2(c) lifts the 12-month
   back-billing limit for theft; no licence cap replaces it (the "up to 3 years" this said was
   unsourced). Payment needs evidence of intent or culpable negligence (SLC 12A.11(g)).
3. Dispute process available to customer (SLC 12A.11(h))

Key metric: Revenue at risk (RAR) = lost revenue from confirmed theft cases.

Epistemic: the company knows about identified RP cases and
estimated losses. Underlying theft rate is unknown.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum


class RPCaseType(str, Enum):
    METER_TAMPERING = "meter_tampering"
    ILLEGAL_RECONNECTION = "illegal_reconnection"
    METER_BYPASS = "meter_bypass"
    ESTIMATION_FRAUD = "estimation_fraud"
    SUPPLY_DIVERSION = "supply_diversion"


class RPCaseStatus(str, Enum):
    SUSPECTED = "suspected"
    UNDER_INVESTIGATION = "under_investigation"
    CONFIRMED = "confirmed"
    ESTIMATED_BILL_RAISED = "estimated_bill_raised"
    RECOVERED = "recovered"
    WRITTEN_OFF = "written_off"


#: UNSOURCED, so None. SLC 21BA.2(c) lifts the 12-month cap for theft and sets no other; the
#: 3 years this held has no source (read_access_and_theft_duties.md §2.4).
_MAX_BACKBILL_YEARS: int | None = None


@dataclass(frozen=True)
class RPCase:
    case_id: str
    account_id: str
    case_type: RPCaseType
    discovery_date: date
    status: RPCaseStatus
    estimated_loss_kwh: float
    estimated_loss_gbp: float
    backbill_start_date: date | None = None

    @property
    def is_active(self) -> bool:
        return self.status not in (RPCaseStatus.RECOVERED, RPCaseStatus.WRITTEN_OFF)

    @property
    def is_recoverable(self) -> bool:
        return self.status in (RPCaseStatus.ESTIMATED_BILL_RAISED,)


class RevenueProtectionRegister:
    """Tracks meter tampering and revenue theft cases."""

    def __init__(self) -> None:
        self._cases: list[RPCase] = []

    def open_case(self, case_id: str, account_id: str, case_type: RPCaseType, discovery_date: date, estimated_loss_kwh: float, estimated_loss_gbp: float) -> RPCase:
        case = RPCase(case_id=case_id, account_id=account_id, case_type=case_type, discovery_date=discovery_date, status=RPCaseStatus.SUSPECTED, estimated_loss_kwh=estimated_loss_kwh, estimated_loss_gbp=estimated_loss_gbp)
        self._cases.append(case)
        return case

    def confirm(self, case_id: str, backbill_start_date: date | None = None) -> RPCase:
        old = next(c for c in self._cases if c.case_id == case_id)
        updated = RPCase(case_id=old.case_id, account_id=old.account_id, case_type=old.case_type, discovery_date=old.discovery_date, status=RPCaseStatus.CONFIRMED, estimated_loss_kwh=old.estimated_loss_kwh, estimated_loss_gbp=old.estimated_loss_gbp, backbill_start_date=backbill_start_date)
        self._cases = [updated if c.case_id == case_id else c for c in self._cases]
        return updated

    def raise_estimated_bill(self, case_id: str) -> RPCase:
        return self._update_status(case_id, RPCaseStatus.ESTIMATED_BILL_RAISED)

    def recover(self, case_id: str) -> RPCase:
        return self._update_status(case_id, RPCaseStatus.RECOVERED)

    def write_off(self, case_id: str) -> RPCase:
        return self._update_status(case_id, RPCaseStatus.WRITTEN_OFF)

    def _update_status(self, case_id: str, new_status: RPCaseStatus) -> RPCase:
        old = next(c for c in self._cases if c.case_id == case_id)
        updated = RPCase(case_id=old.case_id, account_id=old.account_id, case_type=old.case_type, discovery_date=old.discovery_date, status=new_status, estimated_loss_kwh=old.estimated_loss_kwh, estimated_loss_gbp=old.estimated_loss_gbp, backbill_start_date=old.backbill_start_date)
        self._cases = [updated if c.case_id == case_id else c for c in self._cases]
        return updated

    @property
    def active_cases(self) -> list[RPCase]:
        return [c for c in self._cases if c.is_active]

    @property
    def confirmed_cases(self) -> list[RPCase]:
        return [c for c in self._cases if c.status == RPCaseStatus.CONFIRMED]

    @property
    def total_estimated_loss_gbp(self) -> float:
        return sum(c.estimated_loss_gbp for c in self.active_cases)

    @property
    def total_estimated_loss_kwh(self) -> float:
        return sum(c.estimated_loss_kwh for c in self.active_cases)

    def cases_by_type(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for c in self._cases:
            k = c.case_type.value
            result[k] = result.get(k, 0) + 1
        return result

    def revenue_protection_summary(self) -> str:
        n_total = len(self._cases)
        n_active = len(self.active_cases)
        return (
            "Revenue Protection Register\n"
            "Total cases: {:d} | Active: {:d}\n"
            "Estimated active loss: £{:,.0f} / {:,.0f} kWh".format(n_total, n_active, self.total_estimated_loss_gbp, self.total_estimated_loss_kwh)
        )
