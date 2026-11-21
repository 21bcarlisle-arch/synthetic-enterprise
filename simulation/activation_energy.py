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

WHICH SIDE OF THE WALL (moved from `company/core/` 2026-08-09, KNIFE pass 3,
design B1_behavioural_physics_is_misfiled)
---------------------------------------------------------------------------
Status-quo bias is a property of the CUSTOMER, not of the supplier's model of
the customer — the guidance quoted above literally says "assign each agent an
Activation_Energy variable". Filed company-side it made the SIM reach across the
epistemic wall to read its own physics.

Safe by MEASUREMENT: zero company-side importers before the move, stdlib-only
imports, so the relocation creates no crossing in either direction. Both sides
are walked; see `docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md` §2b for why
a move to an UNWALKED directory would have been laundering, not a cut.

The COMPANY never sees an agent's AE. What it may hold is an estimate of
switching propensity built from observables (tenure, tariff position, contact
history) — an estimate that is allowed to be wrong, which is exactly the gap the
coupled triad measures.
"""
from __future__ import annotations

import datetime as dt
import functools
import json
import statistics
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
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
    media_switching_factor: float = 1.0  # from media_switching_ae_factor; SWITCH_SUPPLIER only

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
        media = self.media_switching_factor if action is ActionType.SWITCH_SUPPLIER else 1.0
        return max(0.0, ae_raw * self.gri_multiplier * media)

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


# ---------------------------------------------------------------------------
# The media term (bill-shock page §7-§8; media page §4a)
# ---------------------------------------------------------------------------
# The world's reading of how far news coverage of household energy prices rose
# above its own background in a week. It is read from a frozen extract of the
# GDELT weekly series, which carries its citation. The company never reads it (W6).
#
# The extract's own data show the moment shapes. A cap has two pulses: its
# announcement and, smaller, its effective date. A supplier SVT change has one,
# the announcement. A supplier failure is a separate event that no price row
# carries. The term measures them and does not assume them.
# `tests/simulation/test_activation_energy_media_term.py` holds those shapes as
# properties of the extract.

MEDIA_EXTRACT_PATH = (
    Path(__file__).resolve().parent.parent
    / "sim" / "data" / "media_coverage_energy_price_weekly_2016_2025.json"
)

# The baseline is the four complete weeks that end one week before the week read.
# This is the weekly form of the method page's day -35 to day -8 window.
_MEDIA_BASELINE_WEEKS = 4
_MEDIA_BASELINE_GAP_WEEKS = 1
_MEDIA_BASELINE_MIN_COMPLETE = 3

# How a unit of excess coverage moves a household's switching hazard, given that
# its own price moves. Measured on 21 Nov 2026 (bill-shock page §8): 59 calm months
# (2016-2020 and Jul 2023 - Dec 2025), whole-market QEP 2.7.1 switching against its
# year and season, regressed on the month's mean weekly media ratio. Slope -0.014,
# bootstrap 95% interval -0.057 to +0.040, Spearman -0.003. The central value is
# set to 0.0 because that is what the fit measured, not as a placeholder.
# The interval is the bound a run that varies this term must stay inside.
MEDIA_SWITCHING_COUPLING = 0.0
MEDIA_SWITCHING_COUPLING_RANGE = (-0.057, 0.040)

# How excess coverage moves contact and complaint. No weekly contact or complaint
# series for GB households is on file, so nothing measures this (bill-shock page §8,
# G6). It stays None, and the term does not reach complaint or contact activation
# energy until a series exists.
MEDIA_CONTACT_COUPLING: Optional[float] = None


class MediaMoment(str, Enum):
    CAP_ANNOUNCEMENT = "cap_announcement"
    CAP_EFFECTIVE = "cap_effective"
    SUPPLIER_ANNOUNCEMENT = "supplier_announcement"
    SUPPLIER_EFFECTIVE = "supplier_effective"
    GUARANTEE_ANNOUNCEMENT = "guarantee_announcement"
    GUARANTEE_EFFECTIVE = "guarantee_effective"
    SUPPLIER_FAILURE = "supplier_failure"


def _week_start(on: dt.date) -> dt.date:
    return on - dt.timedelta(days=on.weekday())


@functools.lru_cache(maxsize=1)
def _media_extract() -> tuple[dict, dict]:
    data = json.loads(MEDIA_EXTRACT_PATH.read_text())
    # A week with no counted day carries no share; it is incomplete, not zero.
    weeks = {
        dt.date.fromisoformat(ws): (float(share or 0.0), bool(complete) and share is not None)
        for ws, share, complete in data["weeks"]
    }
    moments: dict = {}
    for row in data["moments"]:
        day = dt.date.fromisoformat(row["date"])
        moments.setdefault(_week_start(day), []).append(MediaMoment(row["moment"]))
    return weeks, moments


def media_attention_ratio(on: dt.date) -> Optional[float]:
    """Coverage share in the week holding `on`, divided by the mean share of the four
    complete weeks ending one week earlier.

    Returns None, meaning "cannot tell", in three cases: the week is outside the
    series, the week is incomplete at source, or fewer than three of its four
    baseline weeks are complete. An incomplete week is not a zero.
    """
    weeks, _ = _media_extract()
    week = _week_start(on)
    if week not in weeks or not weeks[week][1]:
        return None
    first = week - dt.timedelta(weeks=_MEDIA_BASELINE_WEEKS + _MEDIA_BASELINE_GAP_WEEKS)
    baseline = [
        weeks[w][0]
        for w in (first + dt.timedelta(weeks=i) for i in range(_MEDIA_BASELINE_WEEKS))
        if w in weeks and weeks[w][1]
    ]
    if len(baseline) < _MEDIA_BASELINE_MIN_COMPLETE:
        return None
    background = statistics.mean(baseline)
    if background <= 0.0:
        return None
    return weeks[week][0] / background


def media_moments(on: dt.date) -> tuple:
    """The dated moments in the week holding `on`. An empty tuple is a week with none."""
    _, moments = _media_extract()
    return tuple(moments.get(_week_start(on), ()))


def media_switching_ae_factor(
    on: dt.date,
    own_price_moves: bool,
    coupling: float = MEDIA_SWITCHING_COUPLING,
) -> float:
    """The factor this week's coverage applies to a household's switching
    activation energy.

    The factor depends on the price the household pays, not on a cap headline
    (the Guarantee weeks read 0.7 and 0.9). Coverage reaches a household only when
    its own price moves, or when the week holds a supplier failure, which is news
    about whether its supplier will still exist. Otherwise the factor is 1.0.

    A hazard raised by (1 + c * (r - 1)) is the same as an activation energy divided
    by it. A ratio the world cannot read (None) leaves activation energy unchanged.
    That is the measured central effect, and it holds at any coupling inside the
    measured range.
    """
    failure = MediaMoment.SUPPLIER_FAILURE in media_moments(on)
    if not (own_price_moves or failure):
        return 1.0
    ratio = media_attention_ratio(on)
    if ratio is None:
        return 1.0
    lift = 1.0 + coupling * (ratio - 1.0)
    if lift <= 0.0:
        raise ValueError(
            f"coupling {coupling} at media ratio {ratio:.2f} gives a non-positive hazard lift"
        )
    return 1.0 / lift
