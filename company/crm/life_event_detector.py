"""C7_life_event_detection -- company-side life-event DETECTION twin.

The company cannot see the SIM life-event stream (`simulation.life_events`,
W2_5). It never reads it. This detector INFERS that a distressing life event
(job loss / serious illness / divorce / retirement / new child) has probably
befallen a customer from OBSERVABLE behaviour ONLY:

    * payment disruption   -- a deterioration in the customer's own payment
                              record (ON_TIME -> LATE / DD_FAILED), the single
                              strongest observable signature of an income shock.
    * consumption shift    -- a sustained rise (a new baby, more time at home
                              after a job loss/retirement) or fall (an occupant
                              leaves after a divorce) in metered kWh.
    * inbound contact      -- the customer telling us they are struggling.
    * metering / MPAN change (a change of tenancy, occupancy change).

It is ALLOWED TO BE WRONG. A real supplier detects some distress late, misses
some entirely (silent hardship), and raises some false alarms (a holiday looks
like a job loss). That imperfection is the point of the coupled triad: the
harness measures the belief-vs-truth GAP between the hidden SIM events and what
this detector recovers from observables (background/gap_metric.py, detection
family). Do NOT "improve" this by giving it more visibility than a real
supplier would have -- that would be an epistemic-wall violation, not a fix.

EPISTEMIC WALL. This module imports NOTHING from `simulation.*`. Its only
inputs are observables that a real supplier holds in its own systems (payment
records, meter reads, contact logs). It wires to the existing company CRM
taxonomy (`company.crm.life_events`) and the vulnerability register
(`company.crm.vulnerability_register`) so a believed event triggers a real
support response (flag vulnerability, offer a payment plan / debt advice).

C-S1 event-arrival tolerance: `detect` works on whatever observation window it
is given -- it never assumes a complete or ordered batch. C-S2: no wall-clock,
no unseeded randomness; the same window always yields the same result.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from company.crm.life_events import LifeEventType
from company.crm.payment_behaviour_analytics import compute_payment_metrics
from company.crm.vulnerability_register import VulnerabilityFlag, VulnerabilityRegister


# ---------------------------------------------------------------------------
# Detection thresholds -- domain-reasoned, NOT fitted to any SIM parameter.
# ---------------------------------------------------------------------------
# These are the company's own imperfect reading of "what a distress signature
# looks like". They are deliberately set by supplier-side reasoning, blind to
# the SIM's income_stress->payment mapping (payment_timing.py) that actually
# produces the records -- that independence is what makes the measured gap real
# rather than a tautology (CLAUDE.md R15).

# A "bad" payment = a missed direct debit or a late payment. `bad_rate` is the
# fraction of records in a window that are bad.
_RECENT_BAD_RATE_TRIGGER = 0.30      # >= ~4 bad in a 12-record year, on its own
_BAD_RATE_DELTA_TRIGGER = 0.20       # a >= 20pt jump vs the customer's baseline
_SEVERE_BAD_RATE = 0.70              # income shock severe enough to read as HIGH

# Consumption is a corroborating / disambiguating signal, not a sole trigger for
# the payment-mediated distress events, but a large shift with a mild payment
# signal is itself suggestive.
_CONSUMPTION_SHIFT_PCT = 0.12        # +/-12% sustained shift is material
_CONSUMPTION_DROP_PCT = -0.12


@dataclass(frozen=True)
class ObservationWindow:
    """Everything the company can OBSERVE about one customer across a detection
    window. Every field is a real supplier-side record; none is SIM ground
    truth. Missing signals are simply absent (C-S1: partial observation is
    normal, never assumed complete)."""

    customer_id: str
    # Payment records as PaymentBehaviourAnalytics holds them: dicts with a
    # "result" of ON_TIME / LATE / DD_FAILED. Baseline = the settled prior
    # period; recent = the window under assessment.
    baseline_payments: Sequence[dict] = field(default_factory=tuple)
    recent_payments: Sequence[dict] = field(default_factory=tuple)
    # Metered consumption (kWh) for the same two periods; 0/None if unknown
    # (e.g. an unread traditional meter -- a real detection blind spot).
    baseline_consumption_kwh: Optional[float] = None
    recent_consumption_kwh: Optional[float] = None
    # Count of inbound contacts flagged as hardship/affordability in the window.
    inbound_hardship_contacts: int = 0
    # A metering / MPAN change occurred (change of tenancy, occupancy change).
    metering_changed: bool = False


@dataclass(frozen=True)
class DetectionResult:
    """The company's BELIEF about one customer. `distress_detected` is the
    binary the detection-gap scores; `inferred_event_type` is the (freely
    fallible) best guess used only to shape the support response."""

    customer_id: str
    distress_detected: bool
    confidence: float                       # 0..1, monotone in signal strength
    inferred_event_type: Optional[LifeEventType]
    signals: dict = field(default_factory=dict)
    vulnerability_flags: tuple = ()

    def to_dict(self) -> dict:
        return {
            "customer_id": self.customer_id,
            "distress_detected": self.distress_detected,
            "confidence": round(self.confidence, 4),
            "inferred_event_type": (
                self.inferred_event_type.value if self.inferred_event_type else None
            ),
            "signals": self.signals,
            "vulnerability_flags": [f.value for f in self.vulnerability_flags],
        }


def _bad_rate(payments: Sequence[dict]) -> Optional[float]:
    """Fraction of records that are LATE or DD_FAILED, or None if the window is
    empty (nothing observed -> no opinion, not a zero)."""
    if not payments:
        return None
    m = compute_payment_metrics(list(payments))
    return m["late_rate"] + m["dd_fail_rate"]


def _consumption_shift_pct(window: ObservationWindow) -> Optional[float]:
    b = window.baseline_consumption_kwh
    r = window.recent_consumption_kwh
    if not b or r is None:
        return None
    return (r - b) / b


class LifeEventDetector:
    """Infers distressing life events from observables and (optionally) writes
    the resulting support response into the vulnerability register."""

    def detect(self, window: ObservationWindow) -> DetectionResult:
        recent_bad = _bad_rate(window.recent_payments)
        baseline_bad = _bad_rate(window.baseline_payments)
        shift = _consumption_shift_pct(window)

        signals: dict = {
            "recent_bad_rate": None if recent_bad is None else round(recent_bad, 4),
            "baseline_bad_rate": None if baseline_bad is None else round(baseline_bad, 4),
            "consumption_shift_pct": None if shift is None else round(shift, 4),
            "inbound_hardship_contacts": window.inbound_hardship_contacts,
            "metering_changed": window.metering_changed,
        }

        # --- Payment-disruption signal (the primary income-shock signature) ---
        payment_signal = False
        bad_delta = None
        if recent_bad is not None:
            if recent_bad >= _RECENT_BAD_RATE_TRIGGER:
                payment_signal = True
            if baseline_bad is not None:
                bad_delta = recent_bad - baseline_bad
                if bad_delta >= _BAD_RATE_DELTA_TRIGGER:
                    payment_signal = True
        signals["bad_rate_delta"] = None if bad_delta is None else round(bad_delta, 4)

        # --- Corroborating signals ---
        consumption_signal = shift is not None and abs(shift) >= _CONSUMPTION_SHIFT_PCT
        contact_signal = window.inbound_hardship_contacts > 0

        # Distress is believed if the payment channel fires, OR a consumption
        # shift is corroborated by the customer reaching out (a real supplier
        # would open a case on that combination even without arrears yet).
        distress = payment_signal or (consumption_signal and contact_signal)

        # Confidence: additive, saturating. Each independent signal raises it.
        confidence = 0.0
        if payment_signal:
            confidence += 0.55
            if recent_bad is not None and recent_bad >= _SEVERE_BAD_RATE:
                confidence += 0.20
        if consumption_signal:
            confidence += 0.20
        if contact_signal:
            confidence += 0.20
        confidence = min(confidence, 1.0)

        inferred = self._infer_event_type(
            distress, recent_bad, shift, window
        ) if distress else None
        flags = self._response_flags(distress, inferred)

        return DetectionResult(
            customer_id=window.customer_id,
            distress_detected=distress,
            confidence=confidence,
            inferred_event_type=inferred,
            signals=signals,
            vulnerability_flags=flags,
        )

    def detect_many(self, windows: Sequence[ObservationWindow]) -> List[DetectionResult]:
        return [self.detect(w) for w in windows]

    @staticmethod
    def _infer_event_type(
        distress: bool,
        recent_bad: Optional[float],
        shift: Optional[float],
        window: ObservationWindow,
    ) -> Optional[LifeEventType]:
        """Best-effort, deliberately fallible disambiguation. Only shapes the
        support response -- the detection gap does not score this."""
        if not distress:
            return None
        # An occupant leaving: consumption falls -> divorce/separation.
        if shift is not None and shift <= _CONSUMPTION_DROP_PCT:
            return LifeEventType.DIVORCE
        # A severe, sustained income shock reads as job loss (could be illness --
        # the two are genuinely hard to separate from payments alone).
        if recent_bad is not None and recent_bad >= _SEVERE_BAD_RATE:
            return LifeEventType.JOB_LOSS
        # Consumption up with a payment strain -> more time at home (job loss).
        if shift is not None and shift >= _CONSUMPTION_SHIFT_PCT:
            return LifeEventType.JOB_LOSS
        return LifeEventType.JOB_LOSS

    @staticmethod
    def _response_flags(
        distress: bool, inferred: Optional[LifeEventType]
    ) -> tuple:
        if not distress:
            return ()
        flags = [VulnerabilityFlag.PAYMENT_DIFFICULTY]
        specific = {
            LifeEventType.JOB_LOSS: VulnerabilityFlag.JOB_LOSS,
            LifeEventType.SERIOUS_ILLNESS: VulnerabilityFlag.SERIOUS_ILLNESS,
        }.get(inferred)
        if specific and specific not in flags:
            flags.append(specific)
        return tuple(flags)

    def apply_to_register(
        self,
        register: VulnerabilityRegister,
        result: DetectionResult,
        as_of: dt.date,
    ) -> None:
        """Wire a believed event into the real support response: register the
        vulnerability flags so the customer picks up the required actions
        (payment plan, debt advice, PSR review) defined in the register. A
        no-detection is a no-op -- the detector never removes an existing flag
        on the strength of an absent signal (a real supplier does not clear a
        vulnerability just because arrears eased)."""
        if not result.distress_detected or not result.vulnerability_flags:
            return
        register.register(
            customer_id=result.customer_id,
            flags=list(result.vulnerability_flags),
            recorded_date=as_of,
            notes=(
                "auto-flagged by C7 life-event detector "
                f"(confidence={result.confidence:.2f}, "
                f"inferred={result.inferred_event_type.value if result.inferred_event_type else 'n/a'})"
            ),
        )
