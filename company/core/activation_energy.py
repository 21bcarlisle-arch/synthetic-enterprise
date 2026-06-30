"""Activation Energy Model (Phase ED).

CTO Architecture Guidance: "Assign each agent an Activation_Energy variable
representing Status Quo Bias. The perceived utility of an action must
mathematically exceed this barrier to trigger a switch or complaint.
This explains why customers stay even when rationally they should not,
and why they suddenly churn on a minor issue."

The model works as follows:
- Each customer has a personal Activation Energy (AE) set at acquisition
- AE is modulated by: GRI (global reputation multiplier), tenure (inertia builds),
  satisfaction with resolution history (positive ratchet down AE)
- Actions only trigger when Perceived Utility of Action > AE
- PUA = f(bill_saving, friction_stress, emotional_trigger, switching_cost)

UK energy market calibration:
- Typical switching AE: 80-120 points (Status Quo Bias literature: Erta et al., 2013)
- Complaint AE: 30-50 points (lower barrier)
- PPM customer AE: +20 adjustment (higher inertia, often vulnerable)
- Loyal 3+ year customers: +15 inertia adjustment
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ActionType(str, Enum):
    SWITCH_SUPPLIER = "switch_supplier"
    RAISE_COMPLAINT = "raise_complaint"
    REQUEST_TARIFF_REVIEW = "request_tariff_review"
    ESCALATE_TO_OMBUDSMAN = "escalate_to_ombudsman"
    REDUCE_CONSUMPTION = "reduce_consumption"


_BASE_AE: dict = {
    ActionType.SWITCH_SUPPLIER: 100.0,
    ActionType.RAISE_COMPLAINT: 40.0,
    ActionType.REQUEST_TARIFF_REVIEW: 55.0,
    ActionType.ESCALATE_TO_OMBUDSMAN: 70.0,
    ActionType.REDUCE_CONSUMPTION: 30.0,
}

_TENURE_INERTIA_PER_YEAR = 5.0     # +5 AE per year of tenure (Status Quo Bias)
_PPM_AE_UPLIFT = 20.0              # PPM customers have higher inertia
_GOOD_RESOLUTION_AE_REDUCTION = 8.0
_GRI_FLOOR_MODIFIER = -20.0        # crisis GRI reduces AE across portfolio (×0.5 already in GRI)


@dataclass(frozen=True)
class ActivationEnergyProfile:
    account_id: str
    base_ae_switching: float
    tenure_years: float
    is_ppm: bool
    good_resolutions: int = 0
    gri_multiplier: float = 1.0     # from GlobalReputationIndex.activation_energy_multiplier

    @property
    def effective_ae(self, action: ActionType = ActionType.SWITCH_SUPPLIER) -> float:
        base = _BASE_AE[action]
        tenure_bonus = min(self.tenure_years * _TENURE_INERTIA_PER_YEAR, 40.0)
        ppm_bonus = _PPM_AE_UPLIFT if self.is_ppm else 0.0
        resolution_bonus = -self.good_resolutions * _GOOD_RESOLUTION_AE_REDUCTION
        ae_raw = base + tenure_bonus + ppm_bonus + resolution_bonus
        return max(0.0, ae_raw * self.gri_multiplier)

    def switching_ae(self) -> float:
        return self.effective_ae_for(ActionType.SWITCH_SUPPLIER)

    def complaint_ae(self) -> float:
        return self.effective_ae_for(ActionType.RAISE_COMPLAINT)

    def effective_ae_for(self, action: ActionType) -> float:
        base = _BASE_AE[action]
        tenure_bonus = min(self.tenure_years * _TENURE_INERTIA_PER_YEAR, 40.0)
        ppm_bonus = _PPM_AE_UPLIFT if self.is_ppm else 0.0
        resolution_reduction = self.good_resolutions * _GOOD_RESOLUTION_AE_REDUCTION
        ae_raw = base + tenure_bonus + ppm_bonus - resolution_reduction
        return max(0.0, ae_raw * self.gri_multiplier)

    def will_act(self, action: ActionType, perceived_utility: float) -> bool:
        return perceived_utility > self.effective_ae_for(action)


class ActivationEnergyRegister:
    def __init__(self) -> None:
        self._profiles: dict = {}

    def register(self, profile: ActivationEnergyProfile) -> ActivationEnergyProfile:
        self._profiles[profile.account_id] = profile
        return profile

    def get(self, account_id: str) -> Optional[ActivationEnergyProfile]:
        return self._profiles.get(account_id)

    def high_inertia_accounts(self, threshold: float = 120.0) -> list:
        return [
            aid for aid, p in self._profiles.items()
            if p.switching_ae() >= threshold
        ]

    def low_inertia_accounts(self, threshold: float = 80.0) -> list:
        return [
            aid for aid, p in self._profiles.items()
            if p.switching_ae() < threshold
        ]

    def accounts_that_would_switch(self, perceived_bill_saving_gbp: float) -> list:
        return [
            aid for aid, p in self._profiles.items()
            if p.will_act(ActionType.SWITCH_SUPPLIER, perceived_bill_saving_gbp)
        ]

    def ae_summary(self) -> str:
        n = len(self._profiles)
        if n == 0:
            return "Activation Energy Register: no profiles loaded."
        avg_ae = sum(p.switching_ae() for p in self._profiles.values()) / n
        n_low = len(self.low_inertia_accounts())
        return (
            f"Activation Energy Register: {n} customers. "
            f"Avg switching AE: {avg_ae:.1f}. "
            f"Low inertia (<80): {n_low}. "
            f"Tenure inertia: {_TENURE_INERTIA_PER_YEAR:.0f}pts/yr (capped 40pts)."
        )
