"""C10_self_rationing_detection -- company-side SILENT-HARDSHIP detection twin.

THE HARD CASE. The company cannot see the SIM self-rationing state
(`simulation.self_rationing`, W2_8). It never reads it. The hidden "pay-but-
don't-heat" household KEEPS PAYING (a perfect payment record -- the arrears /
collections channel shows NOTHING) but cuts its energy use below plausible
living levels to keep the bill affordable. Arrears vulnerability announces
itself; this does not. The ONLY observable signature is a CONSUMPTION ANOMALY:
a DROP from the household's own established baseline down below the Ofgem TDCV
Low-band floor, with a CLEAN payment record. This detector infers likely self-
rationing from OBSERVABLES ONLY and raises the orphaned
`VulnerabilityFlag.PPM_SELF_DISCONNECTED`, which had no detector today.

THE CONFOUND IT MUST NOT FAIL. A genuinely LOW-NEED household -- a small,
efficient, one-person home -- ALSO sits below the TDCV Low floor with a perfect
payment record. In a single snapshot the two are identical. They differ in one
OBSERVABLE respect: the self-rationer DROPPED to that level from a normal
baseline (a visible change over two meter reads), while the low-need home was
ALWAYS there (no drop). A detector that flags EVERYONE below the floor is naive
-- it would flag every efficient home (a flood of false positives) and, in
spirit, would be reading the floor as if it were the hidden label. So the
signature is the DROP-BELOW-FLOOR, not below-floor alone. This is what separates
rationing from low-need without ever reading the hidden budget or true label.

THE HONEST BLIND SPOT (why this is allowed to be wrong, and where the gap comes
from). The drop signal REQUIRES a trustworthy prior baseline -- a meter read
history. A real UK supplier does not have one for every account: traditional
(non-smart / non-AMR) meters send no regular reads, and a recently-switched
customer brings no history. For those accounts the company sees only "below
floor, no baseline" -- which is EXACTLY what a low-need home looks like too --
so it CANNOT safely raise the flag (doing so on below-floor-alone is the naive
leak above). The silent hardship among the no-baseline population is therefore
structurally invisible. That is a real, externally-anchored detection gap (it
tracks smart-meter coverage), not a modelling shortcut -- and it is the point of
the coupled triad: the harness measures the belief-vs-truth gap this blind spot
produces.

EPISTEMIC WALL (.claude/rules/epistemic-wall-company.md). This module imports
NOTHING from `simulation.*`. Every input is an observable a real supplier holds
in its own systems: two annual meter reads (prior baseline + current), whether a
usable baseline exists at all, the public TDCV floor, the payment/arrears record,
an observable regional weather-normalisation factor. The TDCV Low floor is the
regulation-commons figure sourced DIRECTLY from
`company.compliance.domain_invariants` (the company-side source of truth), not a
re-derived threshold. Thresholds are domain-reasoned, set blind to the SIM's
budget->severity physics (W2_8's `_SEVERITY_RANGE` etc); that independence (R15)
is what makes the measured gap a real measurement and not a tautology.

R12/R13. The drop threshold and floor are affordability/regulation reasoning,
NOT fitted to move any gap number. A near-zero gap would be a red flag to
diagnose (a leak or a coverage assumption that erased the blind spot), never a
success to bank.

C-S1 event-arrival tolerance: `detect` works on whatever observation it is
given -- a missing baseline is simply absent (no opinion on the drop, not a
zero). C-S2: no wall-clock, no unseeded randomness; the same observation always
yields the same result.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from company.compliance.domain_invariants import TDCV_ELEC_LOW, TDCV_GAS_LOW
from company.crm.vulnerability_register import VulnerabilityFlag, VulnerabilityRegister


# ---------------------------------------------------------------------------
# The plausible-living floor -- the Ofgem TDCV Low-band FLOOR (regulation
# commons). SOURCE OF TRUTH: company.compliance.domain_invariants. Consumption
# BELOW this floor is inconsistent with adequately heating a home of that band.
# (W2_8 DUPLICATES these on the SIM side of the wall and drift-guards against
# THIS same source; the company side imports the source directly.)
# ---------------------------------------------------------------------------
TDCV_LOW_FLOOR_KWH: dict[str, float] = {
    "electricity": TDCV_ELEC_LOW.low,   # 1400 kWh/yr
    "gas": TDCV_GAS_LOW.low,            # 5500 kWh/yr
}


# ---------------------------------------------------------------------------
# Detection thresholds -- domain-reasoned, NOT fitted to any SIM parameter.
# ---------------------------------------------------------------------------
# The company's own reading of "what a rationing signature looks like", set by
# supplier-side reasoning and blind to W2_8's hidden severity band. A drop of
# >=20% BEYOND what weather explains is treated as a material, non-seasonal cut.
# (W2_8's true severities sit in ~0.30-0.90; this 0.20 was chosen independently
# -- it is deliberately NOT the SIM's number, preserving R15 independence.)
_MATERIAL_DROP_FRACTION = 0.20


@dataclass(frozen=True)
class SelfRationingObservation:
    """Everything the company can OBSERVE about one account's consumption and
    payment posture over a detection window. Every field is a real supplier-side
    record; none is SIM ground truth.

    `baseline_annual_kwh` is the household's OWN established prior baseline (an
    earlier annual meter read). It is ``None`` when the company has no usable
    history -- a traditional/unread meter or a recently-switched account -- which
    is the real blind spot: without it the drop cannot be seen and the account is
    indistinguishable from a genuinely-low-need home (C-S1: a missing signal is
    absent, never a zero)."""

    customer_id: str
    commodity: str = "electricity"          # "electricity" | "gas"
    # Current metered annual consumption (kWh). The one always-present read.
    observed_annual_kwh: float = 0.0
    # The household's OWN prior baseline (kWh/yr); None if no usable history.
    baseline_annual_kwh: Optional[float] = None
    # Public TDCV Low-band floor; defaults from `commodity` when omitted.
    floor_kwh: Optional[float] = None
    # Payment posture -- the SILENT channel. A self-rationer keeps paying, so a
    # clean record here is EXPECTED, not reassuring. Any arrears means the
    # collections channel (C7 / PAYMENT_DIFFICULTY) already owns the case.
    missed_payments: int = 0
    arrears_open: bool = False
    # Observable regional weather-normalisation factor = expected consumption
    # this period vs baseline purely from weather (HDD ratio recent/baseline).
    # <1 = a milder period (some fall is weather, not rationing); >1 = colder.
    # 1.0 = no adjustment. Lets the detector avoid mistaking a warm year for a
    # cut. It is an OBSERVABLE (the supplier knows regional degree-days).
    weather_normalisation_factor: float = 1.0
    inbound_hardship_contacts: int = 0


@dataclass(frozen=True)
class SelfRationingDetection:
    """The company's BELIEF about one account. `self_rationing_suspected` is the
    binary the detection-gap scores; the rest is audit + support-response
    shaping."""

    customer_id: str
    self_rationing_suspected: bool
    confidence: float                       # 0..1, monotone in signal strength
    signals: dict = field(default_factory=dict)
    vulnerability_flags: tuple = ()

    def to_dict(self) -> dict:
        return {
            "customer_id": self.customer_id,
            "self_rationing_suspected": self.self_rationing_suspected,
            "confidence": round(self.confidence, 4),
            "signals": self.signals,
            "vulnerability_flags": [f.value for f in self.vulnerability_flags],
        }


def _floor_for(obs: SelfRationingObservation) -> float:
    if obs.floor_kwh is not None:
        return obs.floor_kwh
    if obs.commodity not in TDCV_LOW_FLOOR_KWH:
        raise ValueError(
            f"commodity {obs.commodity!r} not one of {tuple(TDCV_LOW_FLOOR_KWH)}"
        )
    return TDCV_LOW_FLOOR_KWH[obs.commodity]


class SelfRationingDetector:
    """Infers likely PAY-BUT-DON'T-HEAT self-rationing from observables, and
    (optionally) writes the resulting support response into the vulnerability
    register (raising PPM_SELF_DISCONNECTED)."""

    def __init__(self, material_drop_fraction: float = _MATERIAL_DROP_FRACTION):
        # Exposed so a reviewer / test can vary it; the default is the
        # domain-reasoned constant, never fitted to a gap.
        self.material_drop_fraction = material_drop_fraction

    def detect(self, obs: SelfRationingObservation) -> SelfRationingDetection:
        floor = _floor_for(obs)
        observed = obs.observed_annual_kwh
        below_floor = observed < floor

        # A clean payment channel is the SILENT-hardship precondition: this flag
        # is for the case the arrears channel cannot see. If arrears are open the
        # collections path owns it -- this detector defers rather than double-flag.
        clean_payment = obs.missed_payments == 0 and not obs.arrears_open

        # -- The drop signal -- the ONE thing that separates a rationer (dropped
        # below floor) from a genuinely-low-need home (always below floor). It
        # needs a usable baseline; without one the drop is unobservable and we do
        # NOT fall back to below-floor-alone (that would flag every efficient
        # home -- the naive leak). Weather-normalise the baseline first so a
        # milder period is not mistaken for a cut.
        has_baseline = obs.baseline_annual_kwh is not None and obs.baseline_annual_kwh > 0
        residual_drop: Optional[float] = None
        material_drop = False
        if has_baseline:
            factor = obs.weather_normalisation_factor
            if factor is None or factor <= 0:
                factor = 1.0
            weather_expected = obs.baseline_annual_kwh * factor
            if weather_expected > 0:
                residual_drop = 1.0 - observed / weather_expected
                material_drop = residual_drop >= self.material_drop_fraction

        suspected = below_floor and material_drop and clean_payment

        signals = {
            "commodity": obs.commodity,
            "observed_annual_kwh": observed,
            "baseline_annual_kwh": obs.baseline_annual_kwh,
            "has_usable_baseline": has_baseline,
            "floor_kwh": floor,
            "below_floor": below_floor,
            "weather_normalisation_factor": obs.weather_normalisation_factor,
            "residual_drop_fraction": (
                None if residual_drop is None else round(residual_drop, 4)
            ),
            "material_drop": material_drop,
            "clean_payment_channel": clean_payment,
            "inbound_hardship_contacts": obs.inbound_hardship_contacts,
            # Why an account BELOW the floor was NOT flagged -- the audit trail
            # that proves the detector is not naive (and names the blind spot).
            "not_flagged_reason": self._not_flagged_reason(
                suspected, below_floor, has_baseline, material_drop, clean_payment
            ),
        }

        # Confidence grows with how deep the residual drop is and how far below
        # the floor -- both observable, both monotone in likely harm. An inbound
        # hardship contact corroborates.
        confidence = 0.0
        if suspected:
            confidence = 0.55
            if residual_drop is not None:
                confidence += min(0.25, max(0.0, residual_drop - self.material_drop_fraction))
            shortfall = (floor - observed) / floor if floor > 0 else 0.0
            confidence += min(0.15, max(0.0, shortfall) * 0.5)
            if obs.inbound_hardship_contacts > 0:
                confidence += 0.10
            confidence = min(confidence, 1.0)

        flags = (VulnerabilityFlag.PPM_SELF_DISCONNECTED,) if suspected else ()
        return SelfRationingDetection(
            customer_id=obs.customer_id,
            self_rationing_suspected=suspected,
            confidence=round(confidence, 4),
            signals=signals,
            vulnerability_flags=flags,
        )

    @staticmethod
    def _not_flagged_reason(
        suspected: bool, below_floor: bool, has_baseline: bool,
        material_drop: bool, clean_payment: bool,
    ) -> Optional[str]:
        if suspected:
            return None
        if not below_floor:
            return "consumption above the plausible-living floor"
        if not has_baseline:
            # The honest blind spot: below floor but no history to see a drop.
            return "below floor but NO usable baseline -- indistinguishable from a low-need home"
        if not material_drop:
            return "below floor but no material drop vs own weather-adjusted baseline (low-need home)"
        if not clean_payment:
            return "arrears open -- owned by the collections channel, not the silent-hardship flag"
        return "not suspected"

    def detect_many(
        self, observations: Sequence[SelfRationingObservation]
    ) -> List[SelfRationingDetection]:
        return [self.detect(o) for o in observations]

    def apply_to_register(
        self,
        register: VulnerabilityRegister,
        result: SelfRationingDetection,
        as_of: dt.date,
    ) -> None:
        """Wire a believed self-rationing case into the real support response:
        register PPM_SELF_DISCONNECTED so the account picks up the required
        actions (offer_emergency_credit, debt_referral) defined in the register.
        A no-detection is a no-op -- an absent signal never clears an existing
        flag (a real supplier does not stand a vulnerability down just because a
        later read looked normal)."""
        if not result.self_rationing_suspected or not result.vulnerability_flags:
            return
        register.register(
            customer_id=result.customer_id,
            flags=list(result.vulnerability_flags),
            recorded_date=as_of,
            notes=(
                "auto-flagged by C10 self-rationing detector "
                f"(confidence={result.confidence:.2f}; consumption drop below "
                "TDCV Low floor with a clean payment record)"
            ),
        )
