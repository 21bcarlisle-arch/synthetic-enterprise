"""Market Share Estimator — estimates supplier position in each segment.

A UK energy supplier can observe their own portfolio but not competitors'
exact share. They estimate market share using:
1. Their own active account count per segment
2. Published DESNZ/Ofgem aggregate figures for total UK customer counts
   (domestic: ~29M metering points; I&C: ~1.7M)
3. Segment sub-totals (residential, SME, I&C) from published data

Market concentration: the UK retail energy market is highly concentrated.
Post-2022, top 6 suppliers hold >80% domestic market share (Ofgem 2023).
A small supplier with 18 customers is a micro-supplier.

Key metrics:
- National market share (all segments combined)
- Segment market share (domestic / SME / I&C separately)
- Concentration ratio vs big-6 (qualitative)
- Growth rate YoY

Epistemic constraint: the company knows its own portfolio counts.
UK aggregate figures come from published Ofgem/DESNZ annual reports.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class MarketSegment(str, Enum):
    DOMESTIC = "domestic"
    SME = "sme"
    INDUSTRIAL_COMMERCIAL = "industrial_commercial"


# Published UK market sizes (approximate, Ofgem/DESNZ data, ~2022-2023)
_UK_MARKET_SIZE: dict[MarketSegment, int] = {
    MarketSegment.DOMESTIC: 29_000_000,    # ~29M domestic metering points
    MarketSegment.SME: 1_700_000,          # ~1.7M SME electricity accounts
    MarketSegment.INDUSTRIAL_COMMERCIAL: 28_000,  # ~28k large I&C sites
}

_MICRO_SUPPLIER_THRESHOLD = 0.0001   # <0.01% share = micro supplier


@dataclass(frozen=True)
class SegmentShareEstimate:
    segment: MarketSegment
    own_customers: int
    uk_market_total: int
    year: int

    @property
    def market_share_pct(self) -> float:
        if self.uk_market_total == 0:
            return 0.0
        return self.own_customers / self.uk_market_total * 100

    @property
    def is_micro_supplier(self) -> bool:
        return self.market_share_pct < _MICRO_SUPPLIER_THRESHOLD * 100

    @property
    def customers_needed_for_1pct(self) -> int:
        """How many additional customers to reach 1% national share."""
        target = self.uk_market_total * 0.01
        return max(0, round(target - self.own_customers))


@dataclass(frozen=True)
class MarketShareSnapshot:
    year: int
    segment_estimates: tuple[SegmentShareEstimate, ...]

    @property
    def total_own_customers(self) -> int:
        return sum(e.own_customers for e in self.segment_estimates)

    @property
    def total_uk_market(self) -> int:
        return sum(e.uk_market_total for e in self.segment_estimates)

    @property
    def blended_share_pct(self) -> float:
        if self.total_uk_market == 0:
            return 0.0
        return self.total_own_customers / self.total_uk_market * 100

    @property
    def largest_segment(self) -> SegmentShareEstimate:
        return max(self.segment_estimates, key=lambda e: e.market_share_pct)

    def estimate_for_segment(self, segment: MarketSegment) -> SegmentShareEstimate | None:
        return next((e for e in self.segment_estimates if e.segment == segment), None)


class MarketShareEstimator:
    """Tracks estimated market share year by year."""

    def __init__(self) -> None:
        self._snapshots: list[MarketShareSnapshot] = []

    def record_year(
        self,
        year: int,
        own_counts: dict[MarketSegment, int],
        market_overrides: dict[MarketSegment, int] | None = None,
    ) -> MarketShareSnapshot:
        estimates = []
        for seg in MarketSegment:
            own = own_counts.get(seg, 0)
            market = (market_overrides or {}).get(seg, _UK_MARKET_SIZE[seg])
            estimates.append(SegmentShareEstimate(seg, own, market, year))
        snapshot = MarketShareSnapshot(year, tuple(estimates))
        self._snapshots.append(snapshot)
        return snapshot

    def snapshot_for_year(self, year: int) -> MarketShareSnapshot | None:
        return next((s for s in self._snapshots if s.year == year), None)

    @property
    def latest_snapshot(self) -> MarketShareSnapshot | None:
        if not self._snapshots:
            return None
        return max(self._snapshots, key=lambda s: s.year)

    def growth_rate_pct(self, year_a: int, year_b: int) -> float | None:
        """Customer count growth rate from year_a to year_b."""
        s_a = self.snapshot_for_year(year_a)
        s_b = self.snapshot_for_year(year_b)
        if not s_a or not s_b or s_a.total_own_customers == 0:
            return None
        return (s_b.total_own_customers - s_a.total_own_customers) / s_a.total_own_customers * 100

    def share_trend(self) -> dict[int, float]:
        return {s.year: s.blended_share_pct for s in sorted(self._snapshots, key=lambda x: x.year)}

    def market_summary(self) -> str:
        if not self._snapshots:
            return "Market Share Estimator — no data"
        latest = self.latest_snapshot
        ic = latest.estimate_for_segment(MarketSegment.INDUSTRIAL_COMMERCIAL)
        lines = [
            "Market Share Estimator (Ofgem/DESNZ benchmarks)",
            "Year: {} | Total customers: {:,}".format(latest.year, latest.total_own_customers),
            "Blended national share: {:.6f}%".format(latest.blended_share_pct),
            "I&C share: {:.4f}% | Micro-supplier: {}".format(
                ic.market_share_pct if ic else 0,
                latest.largest_segment.is_micro_supplier,
            ),
        ]
        return chr(10).join(lines)
