"""EAC Drift Assessor -- Phase AB.

After years of life events (EV acquisition, ASHP installation, solar),
the Annual Quantity (AQ) used for tariff pricing at contract signing drifts
from the customer's actual consumption. A real supplier detects this drift
from billing history and reprices at renewal.

Company can observe:
  - Original AQ from contract records (what was quoted at signing)
  - Current billing-derived EAC from meter reads / estimated bills
  - Asset flags from CRM (EV, ASHP, solar registered)

Uses only company-observable data. Epistemic-compliant.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


# Drift thresholds (%) below which we consider consumption stable
_MATERIAL_INCREASE_PCT = 15.0  # +15% or more = likely acquired EV or ASHP
_MATERIAL_DECREASE_PCT = 10.0  # -10% or more = likely installed solar or insulation

# Minimum AQ to avoid divide-by-zero on tiny trial accounts
_MIN_AQ_KWH = 100.0


class DriftDirection(str, Enum):
    INCREASED = "increased"
    DECREASED = "decreased"
    STABLE = "stable"


class RenewalAction(str, Enum):
    REPRICE_UPWARD = "reprice_upward"
    REPRICE_DOWNWARD = "reprice_downward"
    MAINTAIN = "maintain"
    URGENT_REPRICE = "urgent_reprice"


@dataclass(frozen=True)
class EACDriftAssessment:
    """AQ vs actual consumption drift assessment for one customer.

    drift_pct: (current_eac - original_aq) / original_aq * 100
    Positive = consumption increased; negative = decreased.
    """
    account_id: str
    original_aq_kwh: float
    current_eac_kwh: float
    has_ev: bool
    has_ashp: bool
    has_solar: bool

    @property
    def drift_kwh(self) -> float:
        return round(self.current_eac_kwh - self.original_aq_kwh, 1)

    @property
    def drift_pct(self) -> float:
        if self.original_aq_kwh < _MIN_AQ_KWH:
            return 0.0
        return round((self.current_eac_kwh - self.original_aq_kwh) / self.original_aq_kwh * 100.0, 2)

    @property
    def drift_direction(self) -> DriftDirection:
        if self.drift_pct >= _MATERIAL_INCREASE_PCT:
            return DriftDirection.INCREASED
        if self.drift_pct <= -_MATERIAL_DECREASE_PCT:
            return DriftDirection.DECREASED
        return DriftDirection.STABLE

    @property
    def likely_cause(self) -> str:
        if self.drift_direction == DriftDirection.INCREASED:
            if self.has_ev and self.has_ashp:
                return "ev_and_ashp_acquired"
            if self.has_ev:
                return "ev_acquired"
            if self.has_ashp:
                return "ashp_installed"
            return "consumption_uplift_unknown"
        if self.drift_direction == DriftDirection.DECREASED:
            if self.has_solar:
                return "solar_installed"
            return "consumption_reduction_unknown"
        return "stable"

    @property
    def renewal_action(self) -> RenewalAction:
        if self.drift_pct >= 30.0:
            return RenewalAction.URGENT_REPRICE
        if self.drift_direction == DriftDirection.INCREASED:
            return RenewalAction.REPRICE_UPWARD
        if self.drift_direction == DriftDirection.DECREASED:
            return RenewalAction.REPRICE_DOWNWARD
        return RenewalAction.MAINTAIN

    @property
    def is_material(self) -> bool:
        return self.drift_direction != DriftDirection.STABLE


class EACDriftBook:
    """Assesses AQ vs actual EAC drift across the customer portfolio.

    Usage::
        book = EACDriftBook()
        assessment = book.assess(
            account_id="C1",
            original_aq_kwh=3000.0,
            current_eac_kwh=11000.0,
            has_ev=True, has_ashp=False, has_solar=False,
        )
    """

    def __init__(self) -> None:
        self._assessments: list[EACDriftAssessment] = []

    def assess(
        self,
        account_id: str,
        original_aq_kwh: float,
        current_eac_kwh: float,
        has_ev: bool = False,
        has_ashp: bool = False,
        has_solar: bool = False,
    ) -> EACDriftAssessment:
        a = EACDriftAssessment(
            account_id=account_id,
            original_aq_kwh=original_aq_kwh,
            current_eac_kwh=current_eac_kwh,
            has_ev=has_ev,
            has_ashp=has_ashp,
            has_solar=has_solar,
        )
        self._assessments.append(a)
        return a

    @property
    def all_assessments(self) -> list[EACDriftAssessment]:
        return list(self._assessments)

    def significant_increases(self) -> list[EACDriftAssessment]:
        return [a for a in self._assessments if a.drift_direction == DriftDirection.INCREASED]

    def significant_decreases(self) -> list[EACDriftAssessment]:
        return [a for a in self._assessments if a.drift_direction == DriftDirection.DECREASED]

    def renewal_reprice_candidates(self) -> list[EACDriftAssessment]:
        return [a for a in self._assessments if a.renewal_action != RenewalAction.MAINTAIN]

    def urgent_reprice_candidates(self) -> list[EACDriftAssessment]:
        return [a for a in self._assessments if a.renewal_action == RenewalAction.URGENT_REPRICE]

    @property
    def mean_drift_pct(self) -> float:
        if not self._assessments:
            return 0.0
        return round(sum(a.drift_pct for a in self._assessments) / len(self._assessments), 2)

    def drift_summary(self) -> dict:
        return {
            "customers_assessed": len(self._assessments),
            "significant_increases": len(self.significant_increases()),
            "significant_decreases": len(self.significant_decreases()),
            "reprice_candidates": len(self.renewal_reprice_candidates()),
            "urgent_reprice_count": len(self.urgent_reprice_candidates()),
            "mean_drift_pct": self.mean_drift_pct,
        }
