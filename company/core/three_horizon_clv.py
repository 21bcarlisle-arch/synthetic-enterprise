from __future__ import annotations
import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

class H3Signal(str, Enum):
    OUTPERFORMING = "outperforming"
    ON_TRACK = "on_track"
    DETERIORATING = "deteriorating"
    AT_RISK = "at_risk"

_H3_OUTPERFORM_THRESHOLD = 0.10
_H3_DETERIORATE_THRESHOLD = -0.10
_H3_AT_RISK_THRESHOLD = -0.30

@dataclass(frozen=True)
class H1Commitment:
    account_id: str
    committed_at: dt.date
    contract_start: dt.date
    contract_end: dt.date
    expected_annual_margin_gbp: float
    expected_churn_rate: float
    discount_rate: float = 0.08

    @property
    def contract_years(self) -> float:
        delta = (self.contract_end - self.contract_start).days / 365.25
        return max(0.0, delta)

    @property
    def h1_clv_gbp(self) -> float:
        retention = 1 - self.expected_churn_rate
        denom = 1 + self.discount_rate - retention
        if denom <= 0:
            return self.expected_annual_margin_gbp * self.contract_years
        return self.expected_annual_margin_gbp * retention / denom

@dataclass
class H2Actuals:
    account_id: str
    revenue_events: List[tuple] = field(default_factory=list)
    cost_events: List[tuple] = field(default_factory=list)

    def record_revenue(self, date: dt.date, amount_gbp: float) -> None:
        self.revenue_events.append((date, amount_gbp))

    def record_cost(self, date: dt.date, amount_gbp: float) -> None:
        self.cost_events.append((date, amount_gbp))

    def total_revenue_gbp(self, as_of=None) -> float:
        events = self.revenue_events
        if as_of:
            events = [(d, a) for d, a in events if d <= as_of]
        return sum(a for _, a in events)

    def total_cost_gbp(self, as_of=None) -> float:
        events = self.cost_events
        if as_of:
            events = [(d, a) for d, a in events if d <= as_of]
        return sum(a for _, a in events)

    def h2_margin_gbp(self, as_of=None) -> float:
        return self.total_revenue_gbp(as_of) - self.total_cost_gbp(as_of)

@dataclass(frozen=True)
class H3Forecast:
    account_id: str
    forecast_at: dt.date
    remaining_contract_years: float
    updated_annual_margin_gbp: float
    updated_churn_probability: float
    discount_rate: float = 0.08

    @property
    def h3_clv_gbp(self) -> float:
        retention = 1 - self.updated_churn_probability
        denom = 1 + self.discount_rate - retention
        if denom <= 0:
            return self.updated_annual_margin_gbp * self.remaining_contract_years
        return self.updated_annual_margin_gbp * retention / denom

class ThreeHorizonCLVTracker:
    def __init__(self):
        self._h1: Dict[str, H1Commitment] = {}
        self._h2: Dict[str, H2Actuals] = {}
        self._h3: Dict[str, List[H3Forecast]] = {}

    def commit_h1(self, commitment: H1Commitment) -> H1Commitment:
        self._h1[commitment.account_id] = commitment
        self._h2.setdefault(commitment.account_id, H2Actuals(commitment.account_id))
        return commitment

    def record_revenue(self, account_id, date, amount_gbp):
        self._h2.setdefault(account_id, H2Actuals(account_id)).record_revenue(date, amount_gbp)

    def record_cost(self, account_id, date, amount_gbp):
        self._h2.setdefault(account_id, H2Actuals(account_id)).record_cost(date, amount_gbp)

    def update_h3(self, forecast: H3Forecast) -> H3Forecast:
        self._h3.setdefault(forecast.account_id, []).append(forecast)
        return forecast

    def latest_h3(self, account_id) -> Optional[H3Forecast]:
        fs = self._h3.get(account_id, [])
        return max(fs, key=lambda f: f.forecast_at) if fs else None

    def h1(self, account_id) -> Optional[H1Commitment]:
        return self._h1.get(account_id)

    def h2_margin(self, account_id, as_of=None) -> float:
        h2 = self._h2.get(account_id)
        return h2.h2_margin_gbp(as_of) if h2 else 0.0

    def h1_vs_h2_variance_gbp(self, account_id, as_of) -> Optional[float]:
        h1 = self._h1.get(account_id)
        h2 = self._h2.get(account_id)
        if h1 is None or h2 is None:
            return None
        elapsed_years = (as_of - h1.contract_start).days / 365.25
        expected_so_far = h1.expected_annual_margin_gbp * elapsed_years
        return h2.h2_margin_gbp(as_of) - expected_so_far

    def h3_signal(self, account_id) -> Optional[H3Signal]:
        h1 = self._h1.get(account_id)
        h3 = self.latest_h3(account_id)
        if h1 is None or h3 is None:
            return None
        pct = (h3.h3_clv_gbp - h1.h1_clv_gbp) / max(1.0, abs(h1.h1_clv_gbp))
        if pct > _H3_OUTPERFORM_THRESHOLD:
            return H3Signal.OUTPERFORMING
        if pct < _H3_AT_RISK_THRESHOLD:
            return H3Signal.AT_RISK
        if pct < _H3_DETERIORATE_THRESHOLD:
            return H3Signal.DETERIORATING
        return H3Signal.ON_TRACK

    def at_risk_accounts(self) -> List[str]:
        return [aid for aid in self._h1 if self.h3_signal(aid) == H3Signal.AT_RISK]

    def outperforming_accounts(self) -> List[str]:
        return [aid for aid in self._h1 if self.h3_signal(aid) == H3Signal.OUTPERFORMING]

    def clv_summary(self) -> str:
        n = len(self._h1)
        n_risk = len(self.at_risk_accounts())
        n_out = len(self.outperforming_accounts())
        return f"3-Horizon CLV Tracker: {n} accounts. AT_RISK: {n_risk}. OUTPERFORMING: {n_out}. H1=commitment; H2=running P&L; H3=live forecast."
