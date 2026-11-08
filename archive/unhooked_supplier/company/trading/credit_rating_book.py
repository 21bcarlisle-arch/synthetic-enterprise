"""Supplier credit rating model: wholesale counterparty assessment for trading."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class CreditRating(str, Enum):
    AAA = 'AAA'
    AA = 'AA'
    A = 'A'
    BBB = 'BBB'  # Investment grade floor
    BB = 'BB'    # Sub-investment / speculative
    B = 'B'
    CCC = 'CCC'
    D = 'D'      # Default
    NR = 'NR'    # Not rated


_RATING_SCORE: Dict[CreditRating, int] = {
    CreditRating.AAA: 10, CreditRating.AA: 9, CreditRating.A: 8,
    CreditRating.BBB: 7, CreditRating.BB: 5, CreditRating.B: 3,
    CreditRating.CCC: 1, CreditRating.D: 0, CreditRating.NR: 4,
}


_PROBABILITY_OF_DEFAULT_PCT: Dict[CreditRating, float] = {
    CreditRating.AAA: 0.01, CreditRating.AA: 0.05, CreditRating.A: 0.09,
    CreditRating.BBB: 0.22, CreditRating.BB: 1.1, CreditRating.B: 4.4,
    CreditRating.CCC: 22.0, CreditRating.D: 100.0, CreditRating.NR: 2.0,
}


def is_investment_grade(rating: CreditRating) -> bool:
    return _RATING_SCORE.get(rating, 0) >= 7


@dataclass(frozen=True)
class CounterpartyCreditProfile:
    counterparty_id: str
    name: str
    rating: CreditRating
    rated_by: str
    rating_date: dt.date
    exposure_limit_gbp: float

    @property
    def score(self) -> int:
        return _RATING_SCORE[self.rating]

    @property
    def pd_pct(self) -> float:
        return _PROBABILITY_OF_DEFAULT_PCT[self.rating]

    @property
    def is_investment_grade(self) -> bool:
        return is_investment_grade(self.rating)


@dataclass
class CreditExposure:
    counterparty_id: str
    trade_date: dt.date
    exposure_gbp: float
    trade_type: str


class CreditRatingBook:
    def __init__(self) -> None:
        self._profiles: List[CounterpartyCreditProfile] = []
        self._exposures: List[CreditExposure] = []

    def register(self, counterparty_id: str, name: str, rating: CreditRating,
                   rated_by: str, rating_date: dt.date,
                   exposure_limit_gbp: float) -> CounterpartyCreditProfile:
        p = CounterpartyCreditProfile(
            counterparty_id=counterparty_id, name=name, rating=rating,
            rated_by=rated_by, rating_date=rating_date,
            exposure_limit_gbp=exposure_limit_gbp,
        )
        self._profiles.append(p)
        return p

    def get(self, counterparty_id: str) -> Optional[CounterpartyCreditProfile]:
        return next((p for p in self._profiles
                      if p.counterparty_id == counterparty_id), None)

    def record_exposure(self, counterparty_id: str, trade_date: dt.date,
                          exposure_gbp: float, trade_type: str) -> CreditExposure:
        e = CreditExposure(
            counterparty_id=counterparty_id, trade_date=trade_date,
            exposure_gbp=exposure_gbp, trade_type=trade_type,
        )
        self._exposures.append(e)
        return e

    def total_exposure_gbp(self, counterparty_id: str) -> float:
        return round(sum(e.exposure_gbp for e in self._exposures
                          if e.counterparty_id == counterparty_id), 2)

    def is_within_limit(self, counterparty_id: str, new_exposure_gbp: float) -> bool:
        profile = self.get(counterparty_id)
        if not profile:
            return False
        current = self.total_exposure_gbp(counterparty_id)
        return (current + new_exposure_gbp) <= profile.exposure_limit_gbp

    def sub_investment_grade_counterparties(self) -> List[CounterpartyCreditProfile]:
        return [p for p in self._profiles if not p.is_investment_grade]

    def credit_summary(self) -> dict:
        ig = [p for p in self._profiles if p.is_investment_grade]
        return {
            'total_counterparties': len(self._profiles),
            'investment_grade': len(ig),
            'sub_investment_grade': len(self._profiles) - len(ig),
            'total_exposure_gbp': round(sum(e.exposure_gbp for e in self._exposures), 2),
        }
