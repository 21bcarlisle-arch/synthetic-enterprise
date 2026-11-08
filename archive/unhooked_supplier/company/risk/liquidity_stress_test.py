"""Liquidity Stress Test Book — models the combined cash drain from margin calls.

Post-2022, Ofgem requires suppliers to demonstrate that they can survive
a defined stress scenario without breach of their credit support arrangements
or requiring emergency credit from their clearing banks.

Stress scenario elements:
1. Wholesale price shock: +X% increase in market price
2. Volume shock: increased retail demand (heating season)
3. Combined margin drain: IM calls + daily VM settlement (Phase CC/CJ)
4. Credit facility drawdown headroom

Ofgem's Financial Resilience Assessment requires suppliers to demonstrate:
- 12 months of operating liquidity
- Ability to survive a defined wholesale stress event

This module models the 30-day cash waterfall under stress to identify
the minimum cash headroom (liquidation floor).

Epistemic constraint: inputs come from the company's own treasury
position, trade blotter, and observable market data. No SIM internals.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class LiquidityStressOutcome(str, Enum):
    SOLVENT = "solvent"              # Survives stress with positive headroom
    MARGIN_CONSTRAINED = "margin_constrained"   # Survives but below comfort level
    CRITICAL = "critical"            # Barely survives; any further shock fails
    INSOLVENT = "insolvent"          # Cash headroom goes negative


@dataclass(frozen=True)
class StressScenario:
    name: str
    wholesale_price_shock_pct: float   # e.g. +30 = 30% price increase
    volume_shock_pct: float            # e.g. +10 = 10% more demand
    # IM shock: additional margin as % of current total IM posted
    initial_margin_shock_pct: float    # e.g. +200 = tripling of IM
    # Number of stress days (VM settled daily)
    stress_days: int = 30

    @property
    def is_severe(self) -> bool:
        return (
            self.wholesale_price_shock_pct >= 50
            or self.initial_margin_shock_pct >= 150
        )


@dataclass(frozen=True)
class StressTestResult:
    scenario: StressScenario
    starting_cash_gbp: float
    # Outflows under stress
    vm_drain_gbp: float           # Variation margin over stress period
    im_additional_call_gbp: float  # Additional IM required by CCPs
    # Inflows
    retail_revenue_inflow_gbp: float  # Retail customers paying bills
    # Net position
    ending_cash_gbp: float
    outcome: LiquidityStressOutcome
    # Liquidity headroom = ending cash / daily operating cost
    daily_operating_cost_gbp: float

    @property
    def survival_days(self) -> float:
        """How many days of operating cost the ending cash covers."""
        if self.daily_operating_cost_gbp <= 0:
            return float("inf")
        if self.ending_cash_gbp <= 0:
            return 0.0
        return self.ending_cash_gbp / self.daily_operating_cost_gbp

    @property
    def total_cash_drain_gbp(self) -> float:
        return self.vm_drain_gbp + self.im_additional_call_gbp

    @property
    def headroom_pct(self) -> float:
        """Ending cash as % of starting cash. Negative = insolvent."""
        if self.starting_cash_gbp <= 0:
            return 0.0
        return self.ending_cash_gbp / self.starting_cash_gbp * 100


class LiquidityStressTestBook:
    """Runs multiple stress scenarios and produces a liquidity waterfall."""

    # Ofgem FRA comfort thresholds
    _SURVIVAL_DAYS_GREEN = 365
    _SURVIVAL_DAYS_AMBER = 90

    def __init__(
        self,
        starting_cash_gbp: float,
        daily_operating_cost_gbp: float,
        # Per-day VM under normal vs stressed conditions
        normal_daily_vm_gbp: float,
        # Annual retail revenue (used to estimate inflows during stress)
        annual_retail_revenue_gbp: float,
        # Total IM currently posted (Phase CJ)
        total_im_posted_gbp: float,
    ) -> None:
        self._cash = starting_cash_gbp
        self._daily_op = daily_operating_cost_gbp
        self._normal_vm = normal_daily_vm_gbp
        self._retail_revenue = annual_retail_revenue_gbp
        self._im = total_im_posted_gbp
        self._results: list[StressTestResult] = []

    def run_scenario(self, scenario: StressScenario) -> StressTestResult:
        days = scenario.stress_days
        # VM under stress: price shock drives daily mark-to-market losses
        # Each 1% price increase ≈ proportional VM increase
        stressed_daily_vm = self._normal_vm * (1 + scenario.wholesale_price_shock_pct / 100)
        vm_drain = stressed_daily_vm * days

        # Additional IM call from clearing house (% of existing IM)
        im_call = self._im * scenario.initial_margin_shock_pct / 100

        # Retail inflow: customers continue paying; volume shock slightly increases revenue
        daily_retail = self._retail_revenue * (1 + scenario.volume_shock_pct / 100) / 365
        retail_inflow = daily_retail * days

        ending_cash = self._cash - vm_drain - im_call + retail_inflow

        if ending_cash > self._daily_op * self._SURVIVAL_DAYS_GREEN:
            outcome = LiquidityStressOutcome.SOLVENT
        elif ending_cash > self._daily_op * self._SURVIVAL_DAYS_AMBER:
            outcome = LiquidityStressOutcome.MARGIN_CONSTRAINED
        elif ending_cash > 0:
            outcome = LiquidityStressOutcome.CRITICAL
        else:
            outcome = LiquidityStressOutcome.INSOLVENT

        result = StressTestResult(
            scenario=scenario,
            starting_cash_gbp=self._cash,
            vm_drain_gbp=vm_drain,
            im_additional_call_gbp=im_call,
            retail_revenue_inflow_gbp=retail_inflow,
            ending_cash_gbp=ending_cash,
            outcome=outcome,
            daily_operating_cost_gbp=self._daily_op,
        )
        self._results.append(result)
        return result

    def standard_scenarios(self) -> list[StressTestResult]:
        """Run the three standard Ofgem-style stress scenarios."""
        scenarios = [
            StressScenario("mild", wholesale_price_shock_pct=20, volume_shock_pct=5, initial_margin_shock_pct=50),
            StressScenario("moderate", wholesale_price_shock_pct=50, volume_shock_pct=10, initial_margin_shock_pct=100),
            StressScenario("severe_2022", wholesale_price_shock_pct=200, volume_shock_pct=15, initial_margin_shock_pct=200),
        ]
        return [self.run_scenario(s) for s in scenarios]

    @property
    def all_results(self) -> list[StressTestResult]:
        return list(self._results)

    @property
    def worst_outcome(self) -> StressTestResult | None:
        if not self._results:
            return None
        order = {
            LiquidityStressOutcome.INSOLVENT: 3,
            LiquidityStressOutcome.CRITICAL: 2,
            LiquidityStressOutcome.MARGIN_CONSTRAINED: 1,
            LiquidityStressOutcome.SOLVENT: 0,
        }
        # Secondary sort: lowest ending cash is worst within the same severity band
        return max(self._results, key=lambda r: (order[r.outcome], -r.ending_cash_gbp))

    def stress_summary(self) -> str:
        if not self._results:
            return "Liquidity Stress Test Book — no scenarios run"
        worst = self.worst_outcome
        n_insolvent = sum(1 for r in self._results if r.outcome == LiquidityStressOutcome.INSOLVENT)
        lines = [
            "Liquidity Stress Test Book",
            "Scenarios run: {} | Insolvent: {}".format(len(self._results), n_insolvent),
            "Worst: {} ({})".format(worst.scenario.name, worst.outcome.value),
            "Worst ending cash: £{:,.0f} ({:.1f}% of start)".format(
                worst.ending_cash_gbp, worst.headroom_pct
            ),
        ]
        return chr(10).join(lines)
