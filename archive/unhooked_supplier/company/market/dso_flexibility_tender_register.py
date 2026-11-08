"""DSO Flexibility Tender Register.

Distribution System Operators (DSOs -- DNOs transitioning to the DSO role)
run flexibility tender rounds to manage local network constraints. Suppliers
and aggregators submit bids to provide demand flexibility or storage services
at specific grid supply points.

This covers local distribution-level flexibility procurement, distinct from:
  - dsr_portfolio.py: NESO transmission-level DSR dispatch events
  - flexibility_revenue_book.py: DFS (Demand Flexibility Service) revenue
  - capacity_market_register.py: national Capacity Market auction obligations

Ofgem P2/6 / Open Networks programme / DNO DSO transition framework.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class FlexibilityService(str, Enum):
    PEAK_AVOIDANCE = "peak_avoidance"
    CONSTRAINT_MANAGEMENT = "constraint_management"
    VOLTAGE_SUPPORT = "voltage_support"
    FAULT_RESTORATION = "fault_restoration"
    FREQUENCY_RESPONSE = "frequency_response"


class TenderStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    AWARDED = "awarded"
    CANCELLED = "cancelled"


class BidStatus(str, Enum):
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


_TENDER_OPEN = frozenset({TenderStatus.OPEN, TenderStatus.CLOSED})


@dataclass(frozen=True)
class DSOFlexibilityTenderRecord:
    tender_id: str
    dno_name: str
    service_type: FlexibilityService
    gsp_name: str                        # Grid Supply Point or zone name
    tender_period_start: dt.date
    tender_period_end: dt.date
    capacity_required_mw: float
    status: TenderStatus
    clearing_price_gbp_per_mw: Optional[float] = None  # per year
    award_date: Optional[dt.date] = None
    cancelled_reason: Optional[str] = None

    @property
    def is_open(self) -> bool:
        return self.status in _TENDER_OPEN

    @property
    def is_awarded(self) -> bool:
        return self.status == TenderStatus.AWARDED

    @property
    def contract_length_days(self) -> int:
        return (self.tender_period_end - self.tender_period_start).days

    def tender_summary(self) -> str:
        parts = [
            f"Tender {self.tender_id}: {self.dno_name} {self.service_type.value} "
            f"@{self.gsp_name} {self.capacity_required_mw:.1f}MW [{self.status.value}]"
        ]
        if self.clearing_price_gbp_per_mw is not None:
            parts.append(f"clear=GBP{self.clearing_price_gbp_per_mw:,.0f}/MW/yr")
        return " | ".join(parts)


@dataclass(frozen=True)
class DSOFlexibilityBid:
    bid_id: str
    tender_id: str
    capacity_offered_mw: float
    price_gbp_per_mw_per_year: float
    status: BidStatus
    awarded_capacity_mw: Optional[float] = None

    @property
    def is_accepted(self) -> bool:
        return self.status == BidStatus.ACCEPTED

    @property
    def annual_revenue_gbp(self) -> float:
        if not self.is_accepted or self.awarded_capacity_mw is None:
            return 0.0
        return self.awarded_capacity_mw * self.price_gbp_per_mw_per_year


class DSOFlexibilityTenderRegister:
    """Register of DSO flexibility tender rounds and bids."""

    def __init__(self) -> None:
        self._tenders: List[DSOFlexibilityTenderRecord] = []
        self._bids: List[DSOFlexibilityBid] = []
        self._tender_counter: int = 0
        self._bid_counter: int = 0

    def _next_tender_id(self) -> str:
        self._tender_counter += 1
        return "DSO-TEN-" + str(self._tender_counter).zfill(5)

    def _next_bid_id(self) -> str:
        self._bid_counter += 1
        return "DSO-BID-" + str(self._bid_counter).zfill(5)

    def _update_tender(self, tender_id: str, **kwargs) -> DSOFlexibilityTenderRecord:
        for i, t in enumerate(self._tenders):
            if t.tender_id == tender_id:
                updated = DSOFlexibilityTenderRecord(**{**t.__dict__, **kwargs})
                self._tenders[i] = updated
                return updated
        raise KeyError(f"Tender not found: {tender_id}")

    def _update_bid(self, bid_id: str, **kwargs) -> DSOFlexibilityBid:
        for i, b in enumerate(self._bids):
            if b.bid_id == bid_id:
                updated = DSOFlexibilityBid(**{**b.__dict__, **kwargs})
                self._bids[i] = updated
                return updated
        raise KeyError(f"Bid not found: {bid_id}")

    def create_tender(
        self,
        dno_name: str,
        service_type: FlexibilityService,
        gsp_name: str,
        tender_period_start: dt.date,
        tender_period_end: dt.date,
        capacity_required_mw: float,
    ) -> DSOFlexibilityTenderRecord:
        if tender_period_end <= tender_period_start:
            raise ValueError("tender_period_end must be after tender_period_start")
        if capacity_required_mw <= 0:
            raise ValueError("capacity_required_mw must be positive")
        tender = DSOFlexibilityTenderRecord(
            tender_id=self._next_tender_id(),
            dno_name=dno_name,
            service_type=service_type,
            gsp_name=gsp_name,
            tender_period_start=tender_period_start,
            tender_period_end=tender_period_end,
            capacity_required_mw=capacity_required_mw,
            status=TenderStatus.OPEN,
        )
        self._tenders.append(tender)
        return tender

    def close_tender(self, tender_id: str) -> DSOFlexibilityTenderRecord:
        t = next((x for x in self._tenders if x.tender_id == tender_id), None)
        if t is None:
            raise KeyError(f"Tender not found: {tender_id}")
        if t.status != TenderStatus.OPEN:
            raise ValueError(f"Cannot close {t.status.value} tender")
        return self._update_tender(tender_id, status=TenderStatus.CLOSED)

    def award_tender(
        self, tender_id: str, clearing_price_gbp_per_mw: float, award_date: dt.date
    ) -> DSOFlexibilityTenderRecord:
        t = next((x for x in self._tenders if x.tender_id == tender_id), None)
        if t is None:
            raise KeyError(f"Tender not found: {tender_id}")
        if t.status != TenderStatus.CLOSED:
            raise ValueError(f"Cannot award {t.status.value} tender (must be closed first)")
        if clearing_price_gbp_per_mw < 0:
            raise ValueError("clearing_price_gbp_per_mw cannot be negative")
        return self._update_tender(tender_id, status=TenderStatus.AWARDED,
                                   clearing_price_gbp_per_mw=clearing_price_gbp_per_mw,
                                   award_date=award_date)

    def cancel_tender(self, tender_id: str, reason: str) -> DSOFlexibilityTenderRecord:
        t = next((x for x in self._tenders if x.tender_id == tender_id), None)
        if t is None:
            raise KeyError(f"Tender not found: {tender_id}")
        if t.status not in _TENDER_OPEN:
            raise ValueError(f"Cannot cancel {t.status.value} tender")
        return self._update_tender(tender_id, status=TenderStatus.CANCELLED,
                                   cancelled_reason=reason)

    def submit_bid(
        self,
        tender_id: str,
        capacity_offered_mw: float,
        price_gbp_per_mw_per_year: float,
    ) -> DSOFlexibilityBid:
        t = next((x for x in self._tenders if x.tender_id == tender_id), None)
        if t is None:
            raise KeyError(f"Tender not found: {tender_id}")
        if t.status != TenderStatus.OPEN:
            raise ValueError(f"Cannot bid on {t.status.value} tender")
        if capacity_offered_mw <= 0:
            raise ValueError("capacity_offered_mw must be positive")
        if price_gbp_per_mw_per_year < 0:
            raise ValueError("price cannot be negative")
        bid = DSOFlexibilityBid(
            bid_id=self._next_bid_id(),
            tender_id=tender_id,
            capacity_offered_mw=capacity_offered_mw,
            price_gbp_per_mw_per_year=price_gbp_per_mw_per_year,
            status=BidStatus.SUBMITTED,
        )
        self._bids.append(bid)
        return bid

    def accept_bid(self, bid_id: str, awarded_capacity_mw: float) -> DSOFlexibilityBid:
        b = next((x for x in self._bids if x.bid_id == bid_id), None)
        if b is None:
            raise KeyError(f"Bid not found: {bid_id}")
        if b.status != BidStatus.SUBMITTED:
            raise ValueError(f"Cannot accept {b.status.value} bid")
        if awarded_capacity_mw <= 0:
            raise ValueError("awarded_capacity_mw must be positive")
        return self._update_bid(bid_id, status=BidStatus.ACCEPTED,
                                awarded_capacity_mw=awarded_capacity_mw)

    def reject_bid(self, bid_id: str) -> DSOFlexibilityBid:
        b = next((x for x in self._bids if x.bid_id == bid_id), None)
        if b is None:
            raise KeyError(f"Bid not found: {bid_id}")
        if b.status != BidStatus.SUBMITTED:
            raise ValueError(f"Cannot reject {b.status.value} bid")
        return self._update_bid(bid_id, status=BidStatus.REJECTED)

    def withdraw_bid(self, bid_id: str) -> DSOFlexibilityBid:
        b = next((x for x in self._bids if x.bid_id == bid_id), None)
        if b is None:
            raise KeyError(f"Bid not found: {bid_id}")
        if b.status != BidStatus.SUBMITTED:
            raise ValueError(f"Cannot withdraw {b.status.value} bid")
        return self._update_bid(bid_id, status=BidStatus.WITHDRAWN)

    # ── Queries ──────────────────────────────────────────────────────────────

    @property
    def open_tenders(self) -> List[DSOFlexibilityTenderRecord]:
        return [t for t in self._tenders if t.status == TenderStatus.OPEN]

    @property
    def awarded_tenders(self) -> List[DSOFlexibilityTenderRecord]:
        return [t for t in self._tenders if t.is_awarded]

    def tenders_by_dno(self, dno_name: str) -> List[DSOFlexibilityTenderRecord]:
        return [t for t in self._tenders if t.dno_name == dno_name]

    def tenders_by_service(self, service_type: FlexibilityService) -> List[DSOFlexibilityTenderRecord]:
        return [t for t in self._tenders if t.service_type == service_type]

    def bids_for_tender(self, tender_id: str) -> List[DSOFlexibilityBid]:
        return [b for b in self._bids if b.tender_id == tender_id]

    @property
    def accepted_bids(self) -> List[DSOFlexibilityBid]:
        return [b for b in self._bids if b.is_accepted]

    @property
    def total_contracted_capacity_mw(self) -> float:
        return sum(
            b.awarded_capacity_mw
            for b in self._bids
            if b.is_accepted and b.awarded_capacity_mw is not None
        )

    @property
    def total_annual_flexibility_revenue_gbp(self) -> float:
        return sum(b.annual_revenue_gbp for b in self._bids)

    def dso_tender_summary(self) -> str:
        total_tenders = len(self._tenders)
        open_count = len(self.open_tenders)
        awarded = len(self.awarded_tenders)
        total_bids = len(self._bids)
        accepted = len(self.accepted_bids)
        capacity = self.total_contracted_capacity_mw
        revenue = self.total_annual_flexibility_revenue_gbp
        return (
            f"DSO Tenders: {total_tenders} total | {open_count} open | {awarded} awarded "
            f"| {total_bids} bids ({accepted} accepted) "
            f"| {capacity:.1f}MW contracted "
            f"| GBP{revenue:,.0f}/yr revenue"
        )
