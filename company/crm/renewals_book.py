from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class RenewalOutcome(str, Enum):
    RENEWED = 'renewed'
    LAPSED = 'lapsed'
    SWITCHED_AWAY = 'switched_away'
    MOVED_OUT = 'moved_out'
    DECEASED = 'deceased'


class OfferType(str, Enum):
    SAME_TARIFF = 'same_tariff'
    BETTER_TARIFF = 'better_tariff'
    PRICE_MATCH = 'price_match'
    LOYALTY_DISCOUNT = 'loyalty_discount'
    AUTO_ROLLOVER = 'auto_rollover'


@dataclass(frozen=True)
class RenewalRecord:
    customer_id: str
    segment: str
    term_end_date: dt.date
    outcome: RenewalOutcome
    offer_type: Optional[OfferType]
    offered_rate_ppm: Optional[float]
    new_term_months: Optional[int]
    days_notice_given: int
    was_outbound_contact: bool = False

    @property
    def accepted(self) -> bool:
        return self.outcome == RenewalOutcome.RENEWED


class RenewalsBook:
    def __init__(self) -> None:
        self._records: list[RenewalRecord] = []

    def add(self, customer_id: str, segment: str, term_end_date: dt.date,
            outcome: RenewalOutcome, offer_type: Optional[OfferType] = None,
            offered_rate_ppm: Optional[float] = None,
            new_term_months: Optional[int] = None,
            days_notice_given: int = 42,
            was_outbound_contact: bool = False) -> RenewalRecord:
        r = RenewalRecord(
            customer_id=customer_id, segment=segment, term_end_date=term_end_date,
            outcome=outcome, offer_type=offer_type,
            offered_rate_ppm=offered_rate_ppm, new_term_months=new_term_months,
            days_notice_given=days_notice_given,
            was_outbound_contact=was_outbound_contact,
        )
        self._records.append(r)
        return r

    def renewal_rate(self, year: int, segment: Optional[str] = None) -> Optional[float]:
        recs = [r for r in self._records if r.term_end_date.year == year]
        if segment:
            recs = [r for r in recs if r.segment == segment]
        eligible = [r for r in recs
                    if r.outcome not in {RenewalOutcome.MOVED_OUT, RenewalOutcome.DECEASED}]
        if not eligible:
            return None
        renewed = sum(1 for r in eligible if r.accepted)
        return round(renewed / len(eligible) * 100, 1)

    def lapse_rate(self, year: int, segment: Optional[str] = None) -> Optional[float]:
        rate = self.renewal_rate(year, segment)
        return round(100 - rate, 1) if rate is not None else None

    def outbound_lift(self, year: int) -> Optional[float]:
        recs = [r for r in self._records if r.term_end_date.year == year]
        outbound = [r for r in recs if r.was_outbound_contact]
        inbound = [r for r in recs if not r.was_outbound_contact]
        if not outbound or not inbound:
            return None
        outbound_rate = sum(1 for r in outbound if r.accepted) / len(outbound) * 100
        inbound_rate = sum(1 for r in inbound if r.accepted) / len(inbound) * 100
        return round(outbound_rate - inbound_rate, 1)

    def by_offer_type(self, year: int) -> dict:
        recs = [r for r in self._records if r.term_end_date.year == year and r.offer_type]
        result: dict = {}
        for r in recs:
            key = r.offer_type.value
            if key not in result:
                result[key] = {'total': 0, 'renewed': 0}
            result[key]['total'] += 1
            if r.accepted:
                result[key]['renewed'] += 1
        for v in result.values():
            v['renewal_rate'] = round(v['renewed'] / v['total'] * 100, 1) if v['total'] else 0.0
        return result

    def annual_summary(self, year: int) -> dict:
        recs = [r for r in self._records if r.term_end_date.year == year]
        return {
            'year': year,
            'total_decisions': len(recs),
            'renewal_rate_pct': self.renewal_rate(year),
            'lapse_rate_pct': self.lapse_rate(year),
            'outbound_lift_pct': self.outbound_lift(year),
            'by_offer_type': self.by_offer_type(year),
        }
