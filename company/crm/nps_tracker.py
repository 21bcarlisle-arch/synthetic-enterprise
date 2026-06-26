from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Dict, List, Optional


class NPSCategory(str):
    pass


PROMOTER_THRESHOLD = 9
PASSIVE_THRESHOLD = 7


def classify_nps(score: int) -> str:
    if score >= PROMOTER_THRESHOLD:
        return 'promoter'
    if score >= PASSIVE_THRESHOLD:
        return 'passive'
    return 'detractor'


@dataclass(frozen=True)
class NPSResponse:
    customer_id: str
    score: int
    surveyed_date: dt.date
    segment: str
    channel: str
    verbatim: str = ''

    @property
    def category(self) -> str:
        return classify_nps(self.score)

    @property
    def is_promoter(self) -> bool:
        return self.score >= PROMOTER_THRESHOLD

    @property
    def is_detractor(self) -> bool:
        return self.score <= 6


def _compute_nps(responses: List[NPSResponse]) -> Optional[float]:
    if not responses:
        return None
    n = len(responses)
    promoters = sum(1 for r in responses if r.is_promoter)
    detractors = sum(1 for r in responses if r.is_detractor)
    return round((promoters - detractors) / n * 100, 1)


class NPSTracker:
    def __init__(self) -> None:
        self._responses: list[NPSResponse] = []

    def record(self, customer_id: str, score: int, surveyed_date: dt.date,
               segment: str, channel: str = 'post_call', verbatim: str = '') -> NPSResponse:
        if not (0 <= score <= 10):
            raise ValueError(f'NPS score must be 0-10, got {score}')
        r = NPSResponse(
            customer_id=customer_id, score=score, surveyed_date=surveyed_date,
            segment=segment, channel=channel, verbatim=verbatim,
        )
        self._responses.append(r)
        return r

    def nps_in_period(self, from_date: dt.date, to_date: dt.date,
                       segment: Optional[str] = None) -> Optional[float]:
        recs = [r for r in self._responses
                if from_date <= r.surveyed_date <= to_date]
        if segment:
            recs = [r for r in recs if r.segment == segment]
        return _compute_nps(recs)

    def monthly_nps(self, year: int) -> Dict[int, Optional[float]]:
        result = {}
        for month in range(1, 13):
            first = dt.date(year, month, 1)
            last_day = 28 if month == 2 else 30 if month in {4, 6, 9, 11} else 31
            last = dt.date(year, month, last_day)
            recs = [r for r in self._responses
                    if first <= r.surveyed_date <= last]
            result[month] = _compute_nps(recs)
        return result

    def by_segment(self, year: int) -> Dict[str, Optional[float]]:
        year_recs = [r for r in self._responses if r.surveyed_date.year == year]
        segments = set(r.segment for r in year_recs)
        return {seg: _compute_nps([r for r in year_recs if r.segment == seg])
                for seg in segments}

    def annual_summary(self, year: int) -> dict:
        year_recs = [r for r in self._responses if r.surveyed_date.year == year]
        nps = _compute_nps(year_recs)
        n = len(year_recs)
        promoters = sum(1 for r in year_recs if r.is_promoter)
        detractors = sum(1 for r in year_recs if r.is_detractor)
        return {
            'year': year,
            'responses': n,
            'nps': nps,
            'promoter_pct': round(promoters / n * 100, 1) if n else None,
            'detractor_pct': round(detractors / n * 100, 1) if n else None,
            'by_segment': self.by_segment(year),
        }
