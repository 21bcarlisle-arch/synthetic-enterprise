"""Commitment / actual / re-forecast tracking for a customer contract (Phase EC).

THIS MODULE IS NOT ABOUT THREE-HORIZON CLV, AND USED TO BE NAMED AS IF IT WERE.
It tracks one account across three points in TIME on a single contract:

    H1  what was COMMITTED at signature      (`H1Commitment`)
    H2  what has ACTUALLY been earned since  (`H2Actuals`)
    H3  what the LATEST re-forecast says     (`H3Forecast`)

That triple is commitment-vs-actual-vs-reforecast — a variance question about one
contract already sold. It is NOT the triple named by `EP1_clv_three_horizon`, whose
horizons are contract-term / tenure-expected / portfolio-cohort — three different
VALUATION BASES for the same customer, all measured from today forward.

The two are answering different questions and the old module name
(`company/core/three_horizon_clv.py`, classes `ThreeHorizonCLVTracker`) claimed the
second while implementing the first. Eight consecutive DISCOVER/FRAME passes on
`EP1_clv_three_horizon` recorded the collision and none resolved it; passes 6, 7 and 8
each pre-committed the same repair — rename this module in the FIRST commit of the draw
that opens EP1, before a line of EP1 code exists — because it had zero non-test
importers and would only get more expensive. This is that commit.

The name `three-horizon CLV` now belongs unambiguously to `EP1_clv_three_horizon`.
`tests/company/core/test_commitment_actual_forecast.py::test_the_three_horizon_clv_name_
does_not_return_to_this_module` is the mechanism that keeps it that way, rather than a
ninth pass re-copying the recommendation forward (MAKE_IT_STICK).
"""
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

# Below this the retention factor is 1 within float noise and the geometric series
# degenerates to a flat sum; see _term_value_gbp.
_UNIT_RETENTION_EPSILON = 1e-12


def _term_value_gbp(
    annual_margin_gbp: float,
    churn_rate: float,
    discount_rate: float,
    term_years: float,
) -> float:
    """Present value of an annual margin earned over a FINITE term.

        sum_{t=1..T} margin * retention^t / (1+d)^t
          = margin * retention * (1 - r^T) / (1 + d - retention),   r = retention / (1+d)

    A contract is worth what it can deliver before it ends, so the term is priced, not
    assumed away. This replaced a perpetuity — the T -> infinity limit of the same
    expression — which was invariant to the term on both horizons and overstated a
    one-year commitment by ~2.9x at margin 100 / churn 0.20 / discount 0.08
    (docs/staging/WORKER_FINDING_THE_CONTRACT_TERM_HORIZON_PRICES_A_TERM_AS_A_PERPETUITY_2026-08-15.md
    — discharged, still in the staging ROOT until its class doc is next rendered, not in `done/`).

    Where retention <= 1 + d the value is bounded above by ``margin * term_years``, the
    undiscounted ceiling of what the term can deliver; equality holds only when
    retention == 1 + d, i.e. churn exactly offsets the discount rate.
    """
    if term_years <= 0:
        return 0.0
    retention = 1.0 - churn_rate
    if retention <= 0:
        # certain churn: nothing survives the first period
        return 0.0
    factor = 1.0 + discount_rate
    if factor <= 0:
        # a rate at or below -100% is not a discount rate; price the term undiscounted
        factor = 1.0
    ratio = retention / factor
    denom = factor - retention
    if abs(denom) < _UNIT_RETENTION_EPSILON:
        # ratio == 1: every period contributes exactly `margin` in present value
        return annual_margin_gbp * term_years
    return annual_margin_gbp * retention * (1.0 - ratio**term_years) / denom

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

    def clv_over_years_gbp(self, term_years: float) -> float:
        """This commitment's value over an arbitrary window — the like-for-like
        baseline an H3 re-forecast of `term_years` remaining must be compared against."""
        return _term_value_gbp(
            self.expected_annual_margin_gbp,
            self.expected_churn_rate,
            self.discount_rate,
            term_years,
        )

    @property
    def h1_clv_gbp(self) -> float:
        return self.clv_over_years_gbp(self.contract_years)

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
        return _term_value_gbp(
            self.updated_annual_margin_gbp,
            self.updated_churn_probability,
            self.discount_rate,
            self.remaining_contract_years,
        )

class CommitmentActualForecastTracker:
    """One account's commitment (H1), running actuals (H2) and latest re-forecast (H3).

    Not a CLV tracker: every figure here is scoped to ONE contract's term. See the module
    docstring for why that distinction is now in the name.
    """

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
        # Like for like: the H3 forecast covers the REMAINING term, so it is scored
        # against what the H1 commitment promised over that same window. Comparing it
        # to the whole-term H1 value would read every account as deteriorating simply
        # because time had passed.
        baseline = h1.clv_over_years_gbp(h3.remaining_contract_years)
        pct = (h3.h3_clv_gbp - baseline) / max(1.0, abs(baseline))
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

    def variance_summary(self) -> str:
        n = len(self._h1)
        n_risk = len(self.at_risk_accounts())
        n_out = len(self.outperforming_accounts())
        return f"Commitment/Actual/Forecast Tracker: {n} accounts. AT_RISK: {n_risk}. OUTPERFORMING: {n_out}. H1=commitment; H2=running P&L; H3=live forecast."
