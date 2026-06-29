"""Tariff Segment Profitability Book.

Aggregates CustomerProfitabilityRecord entries by tariff segment to produce a
portfolio-level view of which segments are profitable. Complement to Phase J
(per-customer) and Phase K (cap constraints).

Observable inputs only: revenue/cost breakdowns from billing/CTS data.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# Standard UK retail energy segment labels — matches company/pricing/cost_to_serve.py
SEGMENT_RESI_CREDIT = "residential_credit"
SEGMENT_RESI_PPM = "residential_ppm"
SEGMENT_SME = "sme"
SEGMENT_IC = "i_and_c"
KNOWN_SEGMENTS = {SEGMENT_RESI_CREDIT, SEGMENT_RESI_PPM, SEGMENT_SME, SEGMENT_IC}


@dataclass(frozen=True)
class SegmentProfitabilityRecord:
    """Aggregated annual profitability for one tariff segment."""
    segment: str
    year: int
    account_count: int
    total_revenue_gbp: float
    total_wholesale_cost_gbp: float
    total_levy_cost_gbp: float
    total_operating_cost_gbp: float

    @property
    def total_net_contribution_gbp(self) -> float:
        return round(
            self.total_revenue_gbp
            - self.total_wholesale_cost_gbp
            - self.total_levy_cost_gbp
            - self.total_operating_cost_gbp,
            2,
        )

    @property
    def is_net_negative(self) -> bool:
        return self.total_net_contribution_gbp < 0.0

    @property
    def average_net_contribution_gbp(self) -> float:
        if self.account_count == 0:
            return 0.0
        return round(self.total_net_contribution_gbp / self.account_count, 2)

    @property
    def net_margin_pct(self) -> float:
        if self.total_revenue_gbp == 0:
            return 0.0
        return round(self.total_net_contribution_gbp / self.total_revenue_gbp * 100, 2)

    @property
    def average_revenue_per_account_gbp(self) -> float:
        if self.account_count == 0:
            return 0.0
        return round(self.total_revenue_gbp / self.account_count, 2)


class SegmentProfitabilityBook:
    """Aggregates CustomerProfitabilityRecord data by segment.

    Build segment summaries by calling aggregate() with a list of per-customer
    records and their segment labels.
    """

    def __init__(self) -> None:
        self._records: list[SegmentProfitabilityRecord] = []

    def record(self, rec: SegmentProfitabilityRecord) -> SegmentProfitabilityRecord:
        self._records.append(rec)
        return rec

    def aggregate_from_customers(
        self,
        customer_records: list[dict],
        year: Optional[int] = None,
    ) -> list[SegmentProfitabilityRecord]:
        """Build SegmentProfitabilityRecords from a list of per-customer dicts.

        Each dict: {segment, year, annual_revenue_gbp, annual_wholesale_cost_gbp,
                    annual_levy_cost_gbp, annual_operating_cost_gbp}.

        Returns one SegmentProfitabilityRecord per (segment, year) combination.
        Stores them in self._records.
        """
        filtered = customer_records if year is None else [r for r in customer_records if r.get("year") == year]
        by_seg_year: dict[tuple, dict] = {}
        for rec in filtered:
            seg = rec.get("segment", "unknown")
            yr = rec.get("year", 0)
            key = (seg, yr)
            if key not in by_seg_year:
                by_seg_year[key] = {"count": 0, "rev": 0.0, "whl": 0.0, "levy": 0.0, "op": 0.0}
            by_seg_year[key]["count"] += 1
            by_seg_year[key]["rev"] += rec.get("annual_revenue_gbp", 0.0)
            by_seg_year[key]["whl"] += rec.get("annual_wholesale_cost_gbp", 0.0)
            by_seg_year[key]["levy"] += rec.get("annual_levy_cost_gbp", 0.0)
            by_seg_year[key]["op"] += rec.get("annual_operating_cost_gbp", 0.0)

        results = []
        for (seg, yr), sums in sorted(by_seg_year.items()):
            seg_rec = SegmentProfitabilityRecord(
                segment=seg, year=yr,
                account_count=sums["count"],
                total_revenue_gbp=round(sums["rev"], 2),
                total_wholesale_cost_gbp=round(sums["whl"], 2),
                total_levy_cost_gbp=round(sums["levy"], 2),
                total_operating_cost_gbp=round(sums["op"], 2),
            )
            self._records.append(seg_rec)
            results.append(seg_rec)
        return results

    def latest_for_segment(self, segment: str) -> Optional[SegmentProfitabilityRecord]:
        matches = [r for r in self._records if r.segment == segment]
        return max(matches, key=lambda r: r.year) if matches else None

    def net_negative_segments(self, year: Optional[int] = None) -> list[str]:
        records = self._for_year(year)
        return sorted({r.segment for r in records if r.is_net_negative})

    def most_profitable_segment(self, year: Optional[int] = None) -> Optional[str]:
        records = self._for_year(year)
        if not records:
            return None
        best = max(records, key=lambda r: r.average_net_contribution_gbp)
        return best.segment

    def segment_summary(self, year: Optional[int] = None) -> dict:
        records = self._for_year(year)
        if not records:
            return {"segments_assessed": 0}
        total_net = sum(r.total_net_contribution_gbp for r in records)
        total_rev = sum(r.total_revenue_gbp for r in records)
        return {
            "segments_assessed": len(records),
            "net_negative_segments": self.net_negative_segments(year),
            "total_net_contribution_gbp": round(total_net, 2),
            "portfolio_net_margin_pct": round(total_net / total_rev * 100, 2) if total_rev else 0.0,
        }

    def _for_year(self, year: Optional[int]) -> list[SegmentProfitabilityRecord]:
        if year is None:
            return list(self._records)
        return [r for r in self._records if r.year == year]
