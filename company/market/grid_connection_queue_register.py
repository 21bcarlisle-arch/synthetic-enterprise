"""Grid Connection Queue Register.

When a customer (typically I&C or distributed generation) needs a new
electricity connection or wants to increase their existing capacity, they
submit an application to the Distribution Network Operator (DNO). The DNO
works through a queue to assess feasibility, issue offers (with cost estimates),
and ultimately energise the connection.

Suppliers track their customers' connection applications to:
  - Anticipate supply start dates
  - Monitor offer acceptance deadlines
  - Coordinate metering for new sites

Ofgem G100/G110 connection offer standards; DNO 5-year queue management plans.
Distinct from agreed_capacity_register.py (DUoS agreed capacity for existing sites).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class ConnectionApplicationType(str, Enum):
    NEW_CONNECTION = "new_connection"
    CAPACITY_INCREASE = "capacity_increase"
    GENERATION_EXPORT = "generation_export"
    EV_CHARGING_HUB = "ev_charging_hub"
    HEAT_NETWORK = "heat_network"


class ConnectionApplicationStatus(str, Enum):
    SUBMITTED = "submitted"
    FEASIBILITY_ACCEPTED = "feasibility_accepted"
    OFFER_ISSUED = "offer_issued"
    OFFER_ACCEPTED = "offer_accepted"
    OFFER_REJECTED = "offer_rejected"
    DESIGN_COMPLETE = "design_complete"
    CONSTRUCTION = "construction"
    ENERGISED = "energised"
    ABANDONED = "abandoned"


_ACTIVE = frozenset({
    ConnectionApplicationStatus.SUBMITTED,
    ConnectionApplicationStatus.FEASIBILITY_ACCEPTED,
    ConnectionApplicationStatus.OFFER_ISSUED,
    ConnectionApplicationStatus.OFFER_ACCEPTED,
    ConnectionApplicationStatus.DESIGN_COMPLETE,
    ConnectionApplicationStatus.CONSTRUCTION,
})

_ACCEPTED_COSTS = frozenset({
    ConnectionApplicationStatus.OFFER_ACCEPTED,
    ConnectionApplicationStatus.DESIGN_COMPLETE,
    ConnectionApplicationStatus.CONSTRUCTION,
    ConnectionApplicationStatus.ENERGISED,
})


@dataclass(frozen=True)
class GridConnectionApplicationRecord:
    reference: str
    account_id: str
    site_address: str
    application_type: ConnectionApplicationType
    requested_capacity_kw: float
    dno_name: str
    submitted_date: dt.date
    status: ConnectionApplicationStatus
    offer_date: Optional[dt.date] = None
    offer_valid_to: Optional[dt.date] = None
    offer_cost_gbp: Optional[float] = None
    energisation_date: Optional[dt.date] = None

    @property
    def is_active(self) -> bool:
        return self.status in _ACTIVE

    @property
    def is_energised(self) -> bool:
        return self.status == ConnectionApplicationStatus.ENERGISED

    def offer_is_live(self, as_of: dt.date) -> bool:
        return (
            self.status == ConnectionApplicationStatus.OFFER_ISSUED
            and self.offer_valid_to is not None
            and as_of <= self.offer_valid_to
        )

    def days_in_queue(self, as_of: dt.date) -> int:
        end = self.energisation_date if self.energisation_date else as_of
        return (end - self.submitted_date).days

    def application_summary(self) -> str:
        parts = [
            f"GCQ {self.reference}: {self.account_id} "
            f"{self.application_type.value} {self.requested_capacity_kw:.0f}kW "
            f"@{self.dno_name} [{self.status.value}]"
        ]
        if self.offer_cost_gbp is not None:
            parts.append(f"offer=GBP{self.offer_cost_gbp:,.0f}")
        return " | ".join(parts)


class GridConnectionQueueRegister:
    """Register of DNO grid connection applications for the company's customers."""

    def __init__(self) -> None:
        self._records: List[GridConnectionApplicationRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return "GCQ-" + str(self._counter).zfill(5)

    def _update(self, reference: str, **kwargs) -> GridConnectionApplicationRecord:
        for i, rec in enumerate(self._records):
            if rec.reference == reference:
                updated = GridConnectionApplicationRecord(**{**rec.__dict__, **kwargs})
                self._records[i] = updated
                return updated
        raise KeyError(f"Application not found: {reference}")

    def _get(self, reference: str) -> GridConnectionApplicationRecord:
        rec = next((r for r in self._records if r.reference == reference), None)
        if rec is None:
            raise KeyError(f"Application not found: {reference}")
        return rec

    def submit_application(
        self,
        account_id: str,
        site_address: str,
        application_type: ConnectionApplicationType,
        requested_capacity_kw: float,
        dno_name: str,
        submitted_date: dt.date,
    ) -> GridConnectionApplicationRecord:
        if requested_capacity_kw <= 0:
            raise ValueError("requested_capacity_kw must be positive")
        rec = GridConnectionApplicationRecord(
            reference=self._next_id(),
            account_id=account_id,
            site_address=site_address,
            application_type=application_type,
            requested_capacity_kw=requested_capacity_kw,
            dno_name=dno_name,
            submitted_date=submitted_date,
            status=ConnectionApplicationStatus.SUBMITTED,
        )
        self._records.append(rec)
        return rec

    def accept_feasibility(self, reference: str) -> GridConnectionApplicationRecord:
        rec = self._get(reference)
        if rec.status != ConnectionApplicationStatus.SUBMITTED:
            raise ValueError(f"Cannot accept feasibility for {rec.status.value} application")
        return self._update(reference, status=ConnectionApplicationStatus.FEASIBILITY_ACCEPTED)

    def issue_offer(
        self,
        reference: str,
        offer_cost_gbp: float,
        offer_date: dt.date,
        offer_valid_to: dt.date,
    ) -> GridConnectionApplicationRecord:
        rec = self._get(reference)
        if rec.status != ConnectionApplicationStatus.FEASIBILITY_ACCEPTED:
            raise ValueError(f"Cannot issue offer for {rec.status.value} application")
        if offer_valid_to <= offer_date:
            raise ValueError("offer_valid_to must be after offer_date")
        if offer_cost_gbp < 0:
            raise ValueError("offer_cost_gbp cannot be negative")
        return self._update(reference, status=ConnectionApplicationStatus.OFFER_ISSUED,
                            offer_cost_gbp=offer_cost_gbp, offer_date=offer_date,
                            offer_valid_to=offer_valid_to)

    def accept_offer(self, reference: str) -> GridConnectionApplicationRecord:
        rec = self._get(reference)
        if rec.status != ConnectionApplicationStatus.OFFER_ISSUED:
            raise ValueError(f"Cannot accept offer for {rec.status.value} application")
        return self._update(reference, status=ConnectionApplicationStatus.OFFER_ACCEPTED)

    def reject_offer(self, reference: str) -> GridConnectionApplicationRecord:
        rec = self._get(reference)
        if rec.status != ConnectionApplicationStatus.OFFER_ISSUED:
            raise ValueError(f"Cannot reject offer for {rec.status.value} application")
        return self._update(reference, status=ConnectionApplicationStatus.OFFER_REJECTED)

    def start_design(self, reference: str) -> GridConnectionApplicationRecord:
        rec = self._get(reference)
        if rec.status != ConnectionApplicationStatus.OFFER_ACCEPTED:
            raise ValueError(f"Cannot start design for {rec.status.value} application")
        return self._update(reference, status=ConnectionApplicationStatus.DESIGN_COMPLETE)

    def start_construction(self, reference: str) -> GridConnectionApplicationRecord:
        rec = self._get(reference)
        if rec.status != ConnectionApplicationStatus.DESIGN_COMPLETE:
            raise ValueError(f"Cannot start construction for {rec.status.value} application")
        return self._update(reference, status=ConnectionApplicationStatus.CONSTRUCTION)

    def energise(self, reference: str, energisation_date: dt.date) -> GridConnectionApplicationRecord:
        rec = self._get(reference)
        if rec.status != ConnectionApplicationStatus.CONSTRUCTION:
            raise ValueError(f"Cannot energise {rec.status.value} application")
        return self._update(reference, status=ConnectionApplicationStatus.ENERGISED,
                            energisation_date=energisation_date)

    def abandon(self, reference: str) -> GridConnectionApplicationRecord:
        rec = self._get(reference)
        if not rec.is_active:
            raise ValueError(f"Cannot abandon {rec.status.value} application")
        return self._update(reference, status=ConnectionApplicationStatus.ABANDONED)

    # ── Queries ──────────────────────────────────────────────────────────────

    @property
    def all_records(self) -> List[GridConnectionApplicationRecord]:
        return list(self._records)

    @property
    def active_applications(self) -> List[GridConnectionApplicationRecord]:
        return [r for r in self._records if r.is_active]

    @property
    def energised_applications(self) -> List[GridConnectionApplicationRecord]:
        return [r for r in self._records if r.is_energised]

    @property
    def abandoned_applications(self) -> List[GridConnectionApplicationRecord]:
        return [r for r in self._records if r.status == ConnectionApplicationStatus.ABANDONED]

    def offers_pending_acceptance(self, as_of: dt.date) -> List[GridConnectionApplicationRecord]:
        return [r for r in self._records if r.offer_is_live(as_of)]

    def offers_expiring_soon(self, as_of: dt.date, days: int = 30) -> List[GridConnectionApplicationRecord]:
        cutoff = as_of + dt.timedelta(days=days)
        return [
            r for r in self._records
            if r.offer_is_live(as_of) and r.offer_valid_to is not None and r.offer_valid_to <= cutoff
        ]

    def by_application_type(self, application_type: ConnectionApplicationType) -> List[GridConnectionApplicationRecord]:
        return [r for r in self._records if r.application_type == application_type]

    def applications_for_account(self, account_id: str) -> List[GridConnectionApplicationRecord]:
        return [r for r in self._records if r.account_id == account_id]

    def applications_for_dno(self, dno_name: str) -> List[GridConnectionApplicationRecord]:
        return [r for r in self._records if r.dno_name == dno_name]

    @property
    def total_committed_cost_gbp(self) -> float:
        return sum(
            r.offer_cost_gbp
            for r in self._records
            if r.status in _ACCEPTED_COSTS and r.offer_cost_gbp is not None
        )

    def queue_summary(self, as_of: dt.date) -> str:
        total = len(self._records)
        active = len(self.active_applications)
        energised = len(self.energised_applications)
        offers = len(self.offers_pending_acceptance(as_of))
        cost = self.total_committed_cost_gbp
        return (
            f"Grid Connection Queue: {total} total | {active} active "
            f"| {energised} energised | {offers} offers live "
            f"| GBP{cost:,.0f} committed cost"
        )
