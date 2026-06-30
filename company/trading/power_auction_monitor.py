"""Wholesale Power Auction Monitor (Phase FM).

UK electricity is traded through several mechanisms:
- N2EX Day-Ahead Auction (EPEX Spot): 12:00 noon daily; price cleared at marginal
- N2EX Intraday: continuous trading until gate closure (1h before delivery)
- BM (Balancing Mechanism): NESO dispatches up/down to balance at SBP/SSP
- Bilateral OTC: long-term contracts negotiated directly

From the company's perspective (observable data):
- N2EX day-ahead clearing price (published same day by Epex/Nordpool)
- Settlement period (half-hourly) volumes and clearing prices
- Peak vs off-peak price differentials
- Crisis indicators: prices >£200/MWh

Company uses this data to:
1. Benchmark its forward purchase costs vs spot outturn
2. Detect favourable moments to cover unhedged volume
3. Report to board on spot market conditions

Observability note: all N2EX auction results are published and freely available.
This module represents what a real energy supplier's trading desk would monitor.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class AuctionType(str, Enum):
    DAY_AHEAD = "day_ahead"
    INTRADAY = "intraday"
    SPOT = "spot"           # within-day continuous


class MarketCondition(str, Enum):
    NORMAL = "normal"           # price £40-150/MWh
    ELEVATED = "elevated"       # price £150-250/MWh
    CRISIS = "crisis"           # price >£250/MWh
    NEGATIVE = "negative"       # price <£0 (excess renewables)


_CRISIS_PRICE_THRESHOLD_GBP = 250.0
_ELEVATED_PRICE_THRESHOLD_GBP = 150.0
_NEGATIVE_PRICE_THRESHOLD_GBP = 0.0


@dataclass(frozen=True)
class AuctionResult:
    delivery_date: dt.date
    settlement_period: int       # 1-48 (HH)
    auction_type: AuctionType
    clearing_price_gbp_per_mwh: float
    volume_mwh: float

    @property
    def is_peak(self) -> bool:
        return 14 <= self.settlement_period <= 38   # 07:00-19:00 approx

    @property
    def market_condition(self) -> MarketCondition:
        if self.clearing_price_gbp_per_mwh < _NEGATIVE_PRICE_THRESHOLD_GBP:
            return MarketCondition.NEGATIVE
        if self.clearing_price_gbp_per_mwh >= _CRISIS_PRICE_THRESHOLD_GBP:
            return MarketCondition.CRISIS
        if self.clearing_price_gbp_per_mwh >= _ELEVATED_PRICE_THRESHOLD_GBP:
            return MarketCondition.ELEVATED
        return MarketCondition.NORMAL

    @property
    def is_crisis_price(self) -> bool:
        return self.market_condition == MarketCondition.CRISIS

    @property
    def total_value_gbp(self) -> float:
        return self.volume_mwh * self.clearing_price_gbp_per_mwh

    def result_summary(self) -> str:
        return (
            "Auction " + str(self.delivery_date) + " SP" + str(self.settlement_period) + ": "
            + str(round(self.clearing_price_gbp_per_mwh, 2)) + " GBP/MWh "
            + "[" + self.market_condition.value + "]"
        )


class PowerAuctionMonitor:

    def __init__(self) -> None:
        self._results: List[AuctionResult] = []

    def record(self, result: AuctionResult) -> AuctionResult:
        self._results.append(result)
        return result

    def results_for_date(self, date: dt.date) -> List[AuctionResult]:
        return [r for r in self._results if r.delivery_date == date]

    def daily_avg_price(self, date: dt.date) -> Optional[float]:
        day_results = self.results_for_date(date)
        if not day_results:
            return None
        return sum(r.clearing_price_gbp_per_mwh for r in day_results) / len(day_results)

    def peak_avg_price(self, date: dt.date) -> Optional[float]:
        peak = [r for r in self.results_for_date(date) if r.is_peak]
        if not peak:
            return None
        return sum(r.clearing_price_gbp_per_mwh for r in peak) / len(peak)

    def crisis_results(self) -> List[AuctionResult]:
        return [r for r in self._results if r.is_crisis_price]

    def negative_price_results(self) -> List[AuctionResult]:
        return [r for r in self._results if
                r.market_condition == MarketCondition.NEGATIVE]

    def avg_clearing_price(self) -> float:
        if not self._results:
            return 0.0
        return sum(r.clearing_price_gbp_per_mwh for r in self._results) / len(self._results)

    def max_clearing_price(self) -> float:
        if not self._results:
            return 0.0
        return max(r.clearing_price_gbp_per_mwh for r in self._results)

    def auction_monitor_summary(self) -> str:
        n = len(self._results)
        avg = self.avg_clearing_price()
        n_crisis = len(self.crisis_results())
        n_neg = len(self.negative_price_results())
        return (
            "Power Auction Monitor: " + str(n) + " results. "
            "Avg: " + str(round(avg, 2)) + " GBP/MWh. "
            "Crisis: " + str(n_crisis) + ". "
            "Negative: " + str(n_neg) + "."
        )
