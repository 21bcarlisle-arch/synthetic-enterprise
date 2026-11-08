"""Supplier resilience scorecard — Ofgem post-2022 financial fitness assessment.

Following the 28 supplier failures of 2021-22, Ofgem implemented a new
Financial Resilience Assessment (FRA) framework requiring suppliers to
demonstrate resilience across five pillars:

1. Liquidity: At least 12 months of supply costs held as cash or credit facility
2. Hedge Coverage: Adequate forward cover relative to retail commitments
3. Credit Quality: Bad debt rate below threshold
4. Concentration: No single customer > 25% of revenue (I&C risk)
5. Stress Resilience: Portfolio survives a 2x wholesale price shock

This module computes a composite scorecard from observable company data.
It does NOT read simulation internals — all inputs come from the company's
own management accounts, trade blotter, and billing records.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ResiliencePillar(str, Enum):
    LIQUIDITY = "Liquidity"
    HEDGE_COVERAGE = "Hedge Coverage"
    CREDIT_QUALITY = "Credit Quality"
    CONCENTRATION = "Concentration"
    STRESS_RESILIENCE = "Stress Resilience"


class PillarRAG(str, Enum):
    GREEN = "GREEN"
    AMBER = "AMBER"
    RED = "RED"


_LIQUIDITY_GREEN_MONTHS = 12.0
_LIQUIDITY_AMBER_MONTHS = 6.0
_HEDGE_GREEN_PCT = 70.0
_HEDGE_AMBER_PCT = 40.0
_BAD_DEBT_GREEN_PCT = 1.0   # of revenue
_BAD_DEBT_AMBER_PCT = 2.5
_CONC_GREEN_PCT = 20.0      # max single customer % of revenue
_CONC_AMBER_PCT = 35.0
_STRESS_GREEN_COVERAGE = 1.0  # survive 2x price shock without insolvency
_STRESS_AMBER_COVERAGE = 0.5


@dataclass(frozen=True)
class PillarScore:
    pillar: ResiliencePillar
    value: float
    rag: PillarRAG
    description: str
    threshold_green: float
    threshold_amber: float
    unit: str = ""

    @property
    def score_value(self) -> int:
        """Numeric score: GREEN=3, AMBER=2, RED=1."""
        return {PillarRAG.GREEN: 3, PillarRAG.AMBER: 2, PillarRAG.RED: 1}[self.rag]


class SupplierResilienceScorecard:
    """Computes the five-pillar Ofgem resilience scorecard for a given year."""

    def __init__(self) -> None:
        self._scores: list[PillarScore] = []

    def assess_liquidity(
        self, cash_gbp: float, monthly_supply_cost_gbp: float
    ) -> PillarScore:
        """Months of supply cost covered by cash."""
        if monthly_supply_cost_gbp <= 0:
            months = float("inf")
        else:
            months = cash_gbp / monthly_supply_cost_gbp
        rag = (
            PillarRAG.GREEN if months >= _LIQUIDITY_GREEN_MONTHS else
            PillarRAG.AMBER if months >= _LIQUIDITY_AMBER_MONTHS else
            PillarRAG.RED
        )
        score = PillarScore(
            pillar=ResiliencePillar.LIQUIDITY,
            value=round(months, 1),
            rag=rag,
            description="{:.1f} months supply cost covered".format(months),
            threshold_green=_LIQUIDITY_GREEN_MONTHS,
            threshold_amber=_LIQUIDITY_AMBER_MONTHS,
            unit="months",
        )
        self._scores.append(score)
        return score

    def assess_hedge_coverage(self, hedge_fraction_pct: float) -> PillarScore:
        """% of retail commitments covered by forward hedges."""
        rag = (
            PillarRAG.GREEN if hedge_fraction_pct >= _HEDGE_GREEN_PCT else
            PillarRAG.AMBER if hedge_fraction_pct >= _HEDGE_AMBER_PCT else
            PillarRAG.RED
        )
        score = PillarScore(
            pillar=ResiliencePillar.HEDGE_COVERAGE,
            value=hedge_fraction_pct,
            rag=rag,
            description="{:.0f}% of retail exposure hedged".format(hedge_fraction_pct),
            threshold_green=_HEDGE_GREEN_PCT,
            threshold_amber=_HEDGE_AMBER_PCT,
            unit="%",
        )
        self._scores.append(score)
        return score

    def assess_credit_quality(
        self, bad_debt_gbp: float, revenue_gbp: float
    ) -> PillarScore:
        """Bad debt as % of revenue."""
        rate_pct = (bad_debt_gbp / revenue_gbp * 100) if revenue_gbp > 0 else 0.0
        rag = (
            PillarRAG.GREEN if rate_pct <= _BAD_DEBT_GREEN_PCT else
            PillarRAG.AMBER if rate_pct <= _BAD_DEBT_AMBER_PCT else
            PillarRAG.RED
        )
        score = PillarScore(
            pillar=ResiliencePillar.CREDIT_QUALITY,
            value=round(rate_pct, 2),
            rag=rag,
            description="Bad debt {:.2f}% of revenue".format(rate_pct),
            threshold_green=_BAD_DEBT_GREEN_PCT,
            threshold_amber=_BAD_DEBT_AMBER_PCT,
            unit="%",
        )
        self._scores.append(score)
        return score

    def assess_concentration(
        self, max_single_customer_revenue_gbp: float, total_revenue_gbp: float
    ) -> PillarScore:
        """Max single customer revenue as % of total."""
        conc_pct = (max_single_customer_revenue_gbp / total_revenue_gbp * 100) if total_revenue_gbp > 0 else 0.0
        rag = (
            PillarRAG.GREEN if conc_pct <= _CONC_GREEN_PCT else
            PillarRAG.AMBER if conc_pct <= _CONC_AMBER_PCT else
            PillarRAG.RED
        )
        score = PillarScore(
            pillar=ResiliencePillar.CONCENTRATION,
            value=round(conc_pct, 1),
            rag=rag,
            description="Max customer {:.1f}% of revenue".format(conc_pct),
            threshold_green=_CONC_GREEN_PCT,
            threshold_amber=_CONC_AMBER_PCT,
            unit="%",
        )
        self._scores.append(score)
        return score

    def assess_stress_resilience(
        self, net_margin_gbp: float, stressed_net_margin_gbp: float
    ) -> PillarScore:
        """Survival under 2x wholesale price shock (stressed_net > 0 = survive)."""
        coverage = stressed_net_margin_gbp / abs(net_margin_gbp) if net_margin_gbp != 0 else 0.0
        rag = (
            PillarRAG.GREEN if coverage >= _STRESS_GREEN_COVERAGE else
            PillarRAG.AMBER if coverage >= _STRESS_AMBER_COVERAGE else
            PillarRAG.RED
        )
        score = PillarScore(
            pillar=ResiliencePillar.STRESS_RESILIENCE,
            value=round(coverage, 2),
            rag=rag,
            description="Stress coverage {:.2f}x (stressed net £{:,.0f})".format(coverage, stressed_net_margin_gbp),
            threshold_green=_STRESS_GREEN_COVERAGE,
            threshold_amber=_STRESS_AMBER_COVERAGE,
            unit="x",
        )
        self._scores.append(score)
        return score

    @property
    def scores(self) -> list[PillarScore]:
        return list(self._scores)

    @property
    def overall_rag(self) -> PillarRAG:
        if not self._scores:
            return PillarRAG.RED
        if any(s.rag == PillarRAG.RED for s in self._scores):
            return PillarRAG.RED
        if any(s.rag == PillarRAG.AMBER for s in self._scores):
            return PillarRAG.AMBER
        return PillarRAG.GREEN

    @property
    def composite_score(self) -> float:
        """Average pillar score (1-3)."""
        if not self._scores:
            return 0.0
        return sum(s.score_value for s in self._scores) / len(self._scores)

    def red_pillars(self) -> list[PillarScore]:
        return [s for s in self._scores if s.rag == PillarRAG.RED]

    def scorecard_summary(self) -> str:
        lines = [
            "Supplier Resilience Scorecard",
            "Overall RAG: {}".format(self.overall_rag.value),
            "Composite score: {:.1f}/3.0".format(self.composite_score),
        ]
        for s in self._scores:
            lines.append("{}: {} ({}) — {}".format(
                s.pillar.value, s.rag.value, "{:.1f}{}".format(s.value, s.unit), s.description
            ))
        red = self.red_pillars()
        if red:
            lines.append("RED pillars: {}".format(", ".join(p.pillar.value for p in red)))
        return chr(10).join(lines)
