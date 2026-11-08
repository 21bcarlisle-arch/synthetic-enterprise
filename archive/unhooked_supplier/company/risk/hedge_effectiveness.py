"""Hedge Effectiveness Assessment: IFRS 9 hedge accounting (80-125% band)."""
from __future__ import annotations
import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class HedgeRelationshipType(str, Enum):
    FAIR_VALUE = "fair_value"
    CASH_FLOW = "cash_flow"


class EffectivenessOutcome(str, Enum):
    HIGHLY_EFFECTIVE = "highly_effective"
    INEFFECTIVE = "ineffective"
    PROSPECTIVE_ONLY = "prospective_only"


_LOWER_BOUND_PCT = 80.0
_UPPER_BOUND_PCT = 125.0


@dataclass(frozen=True)
class EffectivenessTest:
    hedge_id: str
    test_date: dt.date
    relationship_type: HedgeRelationshipType
    hedged_item_fair_value_change_gbp: float
    hedging_instrument_fair_value_change_gbp: float
    is_prospective: bool = False

    @property
    def effectiveness_ratio_pct(self) -> Optional[float]:
        if self.hedged_item_fair_value_change_gbp == 0:
            return None
        ratio = (-self.hedging_instrument_fair_value_change_gbp
                 / self.hedged_item_fair_value_change_gbp) * 100
        return round(ratio, 2)

    @property
    def outcome(self) -> EffectivenessOutcome:
        if self.is_prospective:
            return EffectivenessOutcome.PROSPECTIVE_ONLY
        ratio = self.effectiveness_ratio_pct
        if ratio is None:
            return EffectivenessOutcome.INEFFECTIVE
        if _LOWER_BOUND_PCT <= ratio <= _UPPER_BOUND_PCT:
            return EffectivenessOutcome.HIGHLY_EFFECTIVE
        return EffectivenessOutcome.INEFFECTIVE

    @property
    def is_effective(self) -> bool:
        return self.outcome == EffectivenessOutcome.HIGHLY_EFFECTIVE

    @property
    def ineffectiveness_gbp(self) -> float:
        ratio = self.effectiveness_ratio_pct
        if ratio is None or self.is_prospective:
            return 0.0
        if _LOWER_BOUND_PCT <= ratio <= _UPPER_BOUND_PCT:
            perfect = -self.hedged_item_fair_value_change_gbp
            actual = self.hedging_instrument_fair_value_change_gbp
            return round(actual - perfect, 2)
        return self.hedging_instrument_fair_value_change_gbp


class HedgeEffectivenessBook:
    def __init__(self) -> None:
        self._tests: List[EffectivenessTest] = []

    def record_test(self, test: EffectivenessTest) -> EffectivenessTest:
        self._tests.append(test)
        return test

    def tests_for_hedge(self, hedge_id: str) -> List[EffectivenessTest]:
        return [t for t in self._tests if t.hedge_id == hedge_id]

    def tests_for_period(self, start: dt.date, end: dt.date) -> List[EffectivenessTest]:
        return [t for t in self._tests if start <= t.test_date <= end]

    def failed_tests(self) -> List[EffectivenessTest]:
        return [t for t in self._tests if t.outcome == EffectivenessOutcome.INEFFECTIVE]

    def effective_tests(self) -> List[EffectivenessTest]:
        return [t for t in self._tests if t.outcome == EffectivenessOutcome.HIGHLY_EFFECTIVE]

    def de_designated_hedges(self) -> List[str]:
        return sorted({t.hedge_id for t in self.failed_tests()})

    def total_ineffectiveness_gbp(self, year: Optional[int] = None) -> float:
        tests = [t for t in self._tests if t.test_date.year == year] if year else self._tests
        return round(sum(t.ineffectiveness_gbp for t in tests), 2)

    def effectiveness_summary(self) -> dict:
        total = len(self._tests)
        passed = len(self.effective_tests())
        failed = len(self.failed_tests())
        return {
            "total_tests": total,
            "effective": passed,
            "ineffective": failed,
            "pass_rate_pct": round(passed / total * 100, 1) if total else 0.0,
            "de_designated_hedge_count": len(self.de_designated_hedges()),
            "total_ineffectiveness_gbp": self.total_ineffectiveness_gbp(),
        }
