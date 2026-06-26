"""Balancing Mechanism offer/bid log: BM unit positions and dispatch instructions."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict


class BMActionType(str, Enum):
    OFFER = 'offer'  # generator offers to increase output (or demand reduces)
    BID = 'bid'      # generator offers to decrease output (or demand increases)


class BMDispatchStatus(str, Enum):
    SUBMITTED = 'submitted'
    ACCEPTED = 'accepted'
    DISPATCHED = 'dispatched'
    PART_DISPATCHED = 'part_dispatched'
    DECLINED = 'declined'


@dataclass(frozen=True)
class BMOffer:
    bmu_id: str
    settlement_date: dt.date
    settlement_period: int
    action_type: BMActionType
    offered_mw: float
    price_gbp_per_mwh: float
    submission_time: dt.datetime

    @property
    def offered_mwh(self) -> float:
        return round(self.offered_mw * 0.5, 3)

    @property
    def is_expensive(self) -> bool:
        return self.price_gbp_per_mwh > 500.0


@dataclass
class BMDispatch:
    offer: BMOffer
    dispatched_mw: float
    dispatch_time: dt.datetime
    status: BMDispatchStatus = BMDispatchStatus.DISPATCHED

    @property
    def dispatched_mwh(self) -> float:
        return round(self.dispatched_mw * 0.5, 3)

    @property
    def revenue_gbp(self) -> float:
        return round(self.dispatched_mwh * self.offer.price_gbp_per_mwh, 2)

    @property
    def utilisation_pct(self) -> float:
        if self.offer.offered_mw == 0:
            return 0.0
        return round(self.dispatched_mw / self.offer.offered_mw * 100, 1)


class BMUnitLog:
    def __init__(self, bmu_id: str, capacity_mw: float) -> None:
        self.bmu_id = bmu_id
        self.capacity_mw = capacity_mw
        self._offers: List[BMOffer] = []
        self._dispatches: List[BMDispatch] = []

    def submit_offer(self, settlement_date: dt.date, period: int,
                       action_type: BMActionType, offered_mw: float,
                       price_gbp_per_mwh: float,
                       submission_time: dt.datetime) -> BMOffer:
        offer = BMOffer(
            bmu_id=self.bmu_id, settlement_date=settlement_date,
            settlement_period=period, action_type=action_type,
            offered_mw=offered_mw, price_gbp_per_mwh=price_gbp_per_mwh,
            submission_time=submission_time,
        )
        self._offers.append(offer)
        return offer

    def record_dispatch(self, offer: BMOffer, dispatched_mw: float,
                          dispatch_time: dt.datetime) -> BMDispatch:
        status = (
            BMDispatchStatus.PART_DISPATCHED
            if dispatched_mw < offer.offered_mw * 0.99
            else BMDispatchStatus.DISPATCHED
        )
        d = BMDispatch(offer=offer, dispatched_mw=dispatched_mw,
                        dispatch_time=dispatch_time, status=status)
        self._dispatches.append(d)
        return d

    def total_revenue_gbp(self, year: int) -> float:
        return round(sum(
            d.revenue_gbp for d in self._dispatches
            if d.offer.settlement_date.year == year
        ), 2)

    def dispatch_count(self, year: int) -> int:
        return sum(
            1 for d in self._dispatches
            if d.offer.settlement_date.year == year
        )

    def avg_dispatch_price(self, year: int) -> Optional[float]:
        relevant = [d for d in self._dispatches
                     if d.offer.settlement_date.year == year]
        if not relevant:
            return None
        return round(
            sum(d.offer.price_gbp_per_mwh for d in relevant) / len(relevant), 2
        )

    def bm_summary(self, year: int) -> dict:
        return {
            'bmu_id': self.bmu_id,
            'capacity_mw': self.capacity_mw,
            'offers_submitted': len(
                [o for o in self._offers if o.settlement_date.year == year]
            ),
            'dispatches': self.dispatch_count(year),
            'total_revenue_gbp': self.total_revenue_gbp(year),
            'avg_dispatch_price_gbp_per_mwh': self.avg_dispatch_price(year),
        }
