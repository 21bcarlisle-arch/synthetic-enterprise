"""Portfolio Repricing Action Book — Phase AC.

Connects EAC drift detection (Phase AB) with renewal timing (Phase M) to
produce a prioritised reprice action schedule. When life events (EV, ASHP,
solar) push a customer's actual consumption far from the contracted AQ, the
company should update the tariff at the next renewal to recover margin.

Company can observe:
  - EACDriftAssessment from the billing-derived EAC register (Phase AB)
  - Days until the next contract renewal (company knows its own renewal dates)
  - Current tariff / unit rate (company knows what it is billing)

Uses only company-observable data. Epistemic-compliant.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from company.crm.eac_drift_assessor import EACDriftAssessment, DriftDirection, RenewalAction


# Renewal urgency thresholds (days to renewal)
_IMMINENT_DAYS = 60    # reprice negotiation must start now
_UPCOMING_DAYS = 180   # schedule for next renewal cycle
_LONG_LEAD_DAYS = 365  # flag for planning purposes

# Margin recovery fraction: what the company expects to recover via reprice.
# Conservative — some customers churn rather than accept higher tariff.
_RECOVERY_FRACTION = 0.70


class RepricingPriority(str, Enum):
    CRITICAL = "critical"    # urgent drift + imminent renewal
    HIGH = "high"            # urgent drift but renewal not imminent
    MEDIUM = "medium"        # material drift + upcoming renewal
    MONITOR = "monitor"      # drift detected but renewal far off or stable


@dataclass(frozen=True)
class RepricingAction:
    """Recommended reprice action for one customer account.

    estimated_margin_recovery_gbp_pa assumes the company reprices at renewal
    and retains the customer. A conservative 70% recovery fraction is applied.
    """
    account_id: str
    drift_pct: float
    current_aq_kwh: float
    recommended_aq_kwh: float
    current_tariff_gbp_pa: float
    recommended_tariff_gbp_pa: float
    days_to_renewal: int
    renewal_action: RenewalAction
    priority: RepricingPriority

    @property
    def tariff_delta_gbp_pa(self) -> float:
        return round(self.recommended_tariff_gbp_pa - self.current_tariff_gbp_pa, 2)

    @property
    def estimated_margin_recovery_gbp_pa(self) -> float:
        if self.tariff_delta_gbp_pa <= 0:
            return 0.0
        return round(self.tariff_delta_gbp_pa * _RECOVERY_FRACTION, 2)

    @property
    def is_urgent(self) -> bool:
        return self.priority == RepricingPriority.CRITICAL

    @property
    def is_actionable(self) -> bool:
        return self.priority in (RepricingPriority.CRITICAL, RepricingPriority.HIGH)


def _compute_priority(
    renewal_action: RenewalAction,
    days_to_renewal: int,
    drift_direction: DriftDirection,
) -> RepricingPriority:
    if renewal_action == RenewalAction.MAINTAIN:
        return RepricingPriority.MONITOR
    if renewal_action == RenewalAction.URGENT_REPRICE and days_to_renewal <= _IMMINENT_DAYS:
        return RepricingPriority.CRITICAL
    if renewal_action in (RenewalAction.URGENT_REPRICE, RenewalAction.REPRICE_UPWARD,
                          RenewalAction.REPRICE_DOWNWARD) and days_to_renewal <= _UPCOMING_DAYS:
        return RepricingPriority.HIGH
    if drift_direction != DriftDirection.STABLE:
        return RepricingPriority.MEDIUM
    return RepricingPriority.MONITOR


class PortfolioRepricingBook:
    """Plans and tracks reprice actions across the customer portfolio.

    Usage::
        book = PortfolioRepricingBook()
        action = book.plan_reprice(
            account_id="C1",
            assessment=drift_assessment,
            current_tariff_gbp_pa=900.0,
            days_to_renewal=45,
            unit_rate_p_per_kwh=25.0,
        )
    """

    def __init__(self) -> None:
        self._actions: list[RepricingAction] = []

    def plan_reprice(
        self,
        account_id: str,
        assessment: EACDriftAssessment,
        current_tariff_gbp_pa: float,
        days_to_renewal: int,
        unit_rate_p_per_kwh: float,
        standing_charge_gbp_pa: float = 0.0,
    ) -> RepricingAction:
        """Plan a reprice action for a single customer.

        The recommended AQ is the current billing-derived EAC.
        The recommended tariff is recomputed at the existing unit rate on the
        new AQ — the company adjusts the direct-debit / annual estimate but
        doesn't change the rate itself here (that is the rate card optimiser's job).
        """
        recommended_aq = assessment.current_eac_kwh
        recommended_tariff = round(
            (recommended_aq * unit_rate_p_per_kwh / 100.0) + standing_charge_gbp_pa, 2
        )
        priority = _compute_priority(
            assessment.renewal_action, days_to_renewal, assessment.drift_direction
        )
        action = RepricingAction(
            account_id=account_id,
            drift_pct=assessment.drift_pct,
            current_aq_kwh=assessment.original_aq_kwh,
            recommended_aq_kwh=recommended_aq,
            current_tariff_gbp_pa=current_tariff_gbp_pa,
            recommended_tariff_gbp_pa=recommended_tariff,
            days_to_renewal=days_to_renewal,
            renewal_action=assessment.renewal_action,
            priority=priority,
        )
        self._actions.append(action)
        return action

    @property
    def all_actions(self) -> list[RepricingAction]:
        return list(self._actions)

    def critical_actions(self) -> list[RepricingAction]:
        return [a for a in self._actions if a.priority == RepricingPriority.CRITICAL]

    def actionable_actions(self) -> list[RepricingAction]:
        return [a for a in self._actions if a.is_actionable]

    def by_priority(self, priority: RepricingPriority) -> list[RepricingAction]:
        return [a for a in self._actions if a.priority == priority]

    def total_margin_at_risk_gbp(self) -> float:
        """Sum of unrecovered margin on CRITICAL accounts (not yet repriced)."""
        return round(sum(
            a.tariff_delta_gbp_pa for a in self.critical_actions()
            if a.tariff_delta_gbp_pa > 0
        ), 2)

    def total_expected_recovery_gbp(self) -> float:
        return round(sum(a.estimated_margin_recovery_gbp_pa for a in self._actions), 2)

    def top_n_by_margin_recovery(self, n: int = 5) -> list[RepricingAction]:
        return sorted(self._actions, key=lambda a: a.estimated_margin_recovery_gbp_pa, reverse=True)[:n]

    def portfolio_reprice_summary(self) -> dict:
        return {
            "customers_planned": len(self._actions),
            "critical_count": len(self.critical_actions()),
            "actionable_count": len(self.actionable_actions()),
            "total_margin_at_risk_gbp": self.total_margin_at_risk_gbp(),
            "total_expected_recovery_gbp": self.total_expected_recovery_gbp(),
        }
