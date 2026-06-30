"""Market Share Intelligence (Phase EK).

The company tracks its own market position using publicly observable data:
- Ofgem quarterly supply market report (published ~4 weeks after period end)
- Company own customer count (directly observable)
- ONS/DESNZ total domestic/SME supply point counts (publicly published)

Key: the company cannot see competitor volumes directly. It infers relative
market share from its own count vs the total published supply point count.
Ofgem rounds and suppresses data for suppliers <1% share.

This module models:
1. Market share estimation from observable inputs
2. Growth rate calculation (organic vs industry headwinds)
3. Concentration risk (HHI contribution) for regulatory filings
4. Share rank position (top-10, challenger, micro) from observable signals
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class SupplierTier(str, Enum):
    BIG_SIX = "big_six"             # >5% share
    CHALLENGER = "challenger"        # 1-5% share
    MICRO = "micro"                  # <1% share (below Ofgem reporting threshold)


class MarketSegment(str, Enum):
    DOMESTIC = "domestic"
    SME = "sme"
    IC_MHH = "ic_mhh"              # I&C Half-Hourly metered


# ONS total GB domestic supply points ~28.5M (DESNZ 2023)
# SME supply points ~2.5M (Ofgem 2023)
_TOTAL_DOMESTIC_SUPPLY_POINTS = 28_500_000
_TOTAL_SME_SUPPLY_POINTS = 2_500_000

# Ofgem suppresses <1% share in published data
_OFGEM_REPORTING_FLOOR_PCT = 1.0


@dataclass(frozen=True)
class MarketShareSnapshot:
    segment: MarketSegment
    period_end: dt.date
    own_supply_points: int
    total_market_supply_points: int
    prior_period_own: Optional[int] = None

    @property
    def market_share_pct(self) -> float:
        if self.total_market_supply_points == 0:
            return 0.0
        return 100.0 * self.own_supply_points / self.total_market_supply_points

    @property
    def is_above_reporting_floor(self) -> bool:
        return self.market_share_pct >= _OFGEM_REPORTING_FLOOR_PCT

    @property
    def supplier_tier(self) -> SupplierTier:
        pct = self.market_share_pct
        if pct > 5.0:
            return SupplierTier.BIG_SIX
        if pct >= _OFGEM_REPORTING_FLOOR_PCT:
            return SupplierTier.CHALLENGER
        return SupplierTier.MICRO

    @property
    def period_growth_pct(self) -> Optional[float]:
        if self.prior_period_own is None or self.prior_period_own == 0:
            return None
        return 100.0 * (self.own_supply_points - self.prior_period_own) / self.prior_period_own

    @property
    def hhi_contribution(self) -> float:
        return (self.market_share_pct ** 2) / 10000.0

    def snapshot_summary(self) -> str:
        pct_str = str(round(self.market_share_pct, 3)) + "%"
        return (
            "Market share (" + self.segment.value + ", " + str(self.period_end) + "): "
            + str(self.own_supply_points) + " of "
            + str(self.total_market_supply_points) + " = " + pct_str
            + " [" + self.supplier_tier.value + "]."
        )


class MarketShareIntelligenceBook:

    def __init__(self) -> None:
        self._snapshots: List[MarketShareSnapshot] = []

    def record(self, snapshot: MarketShareSnapshot) -> MarketShareSnapshot:
        self._snapshots.append(snapshot)
        return snapshot

    def snapshots_for(self, segment: MarketSegment) -> List[MarketShareSnapshot]:
        return sorted(
            [s for s in self._snapshots if s.segment == segment],
            key=lambda s: s.period_end,
        )

    def latest_for(self, segment: MarketSegment) -> Optional[MarketShareSnapshot]:
        snaps = self.snapshots_for(segment)
        return snaps[-1] if snaps else None

    def share_trend(self, segment: MarketSegment) -> str:
        snaps = self.snapshots_for(segment)
        if len(snaps) < 2:
            return "insufficient_data"
        delta = snaps[-1].market_share_pct - snaps[0].market_share_pct
        if delta > 0.05:
            return "growing"
        if delta < -0.05:
            return "declining"
        return "stable"

    def current_tier(self, segment: MarketSegment) -> Optional[SupplierTier]:
        latest = self.latest_for(segment)
        return latest.supplier_tier if latest else None

    def intelligence_summary(self, segment: MarketSegment) -> str:
        latest = self.latest_for(segment)
        if latest is None:
            return "No market share data for " + segment.value
        trend = self.share_trend(segment)
        return (
            "Market Intelligence (" + segment.value + "): "
            + str(round(latest.market_share_pct, 3)) + "% share ["
            + latest.supplier_tier.value + "], trend=" + trend + "."
        )
