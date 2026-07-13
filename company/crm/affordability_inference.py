"""C6_affordability_inference -- company-side ability-to-pay + book-composition twin.

The company cannot see a customer's household budget (`simulation.household_budget`,
W2_4): income, essential-cost floor, discretionary margin, savings buffer, the
priority-of-debts stack are all HIDDEN SIM ground truth. A real UK energy
supplier does not know these either. It INFERS a customer's affordability from
OBSERVABLES ONLY:

    * payment behaviour  -- on-time / late / direct-debit-failed record, the
                            single strongest observable ability-to-pay signature.
    * arrears            -- an open arrears case and how far it has escalated
                            (first/second notice) -- money that did not arrive.
    * consumption / bill -- metered kWh and the bill it produces; a weak, noisy
                            proxy for household size / property / income.
    * tariff & segment   -- observable account attributes.
    * inbound contact    -- the customer telling us they are struggling.

It produces two beliefs:
  (a) a per-customer AFFORDABILITY BAND (negative / stretched / managing /
      comfortable) -- the company's read of ability to pay;
  (b) a BOOK-COMPOSITION belief -- the distribution of its own book across those
      bands, i.e. "what kind of customers do we think we have".

It is ALLOWED TO BE WRONG, and it will be. Two households in the same band leave
different observable traces (payments are stochastic); a genuinely-cannot-pay
household sitting on savings pays cleanly and looks comfortable; a comfortable
and a merely-managing household both pay on time and are near-indistinguishable
from payments alone. That irrecoverable information loss IS the point: the
coupled-triad harness measures the belief-vs-truth GAP between this inference and
the hidden budget distribution (background/gap_metric.py, belief family / TV
distance). Do NOT "improve" this by giving it visibility a real supplier lacks --
that would be an epistemic-wall violation, not a fix, and it would collapse the
gap by leaking theta rather than by learning.

EPISTEMIC WALL. This module imports NOTHING from `simulation.*`. Its only inputs
are observables a real supplier holds in its own systems. The affordability-band
vocabulary is the COMPANY'S OWN taxonomy (a real supplier defines affordability
tiers for its vulnerability/collections policy); the harness maps the hidden
budget onto the same vocabulary to score the gap, but this module never sees the
budget. Thresholds are domain-reasoned, set blind to the SIM's budget->payment
physics -- that independence (R15) is what makes the measured gap a real
measurement, not a tautology.

R12/R13. The band cut-offs and thresholds below are affordability reasoning. They
are NOT fitted to move any gap number toward a target. A near-zero gap would be a
red flag to diagnose (a leak), never a success to bank.

C-S1 event-arrival tolerance: inference works on whatever observation it is
given -- it never assumes a complete or ordered payment batch; missing signals
are simply absent (no opinion, not a zero). C-S2: no wall-clock, no unseeded
randomness -- the same observation always yields the same band.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Mapping, Optional, Sequence

from company.crm.payment_behaviour_analytics import compute_payment_metrics


class AffordabilityBand(str, Enum):
    """The company's own affordability taxonomy, worst -> best. Ordered so a
    distribution over bands can be compared as a vector (index = _BAND_ORDER)."""

    NEGATIVE = "negative"        # cannot cover essentials; energy competes with food/rent
    STRETCHED = "stretched"      # covers essentials but little slack; a shock tips them over
    MANAGING = "managing"        # comfortable enough to absorb the bill and modest shocks
    COMFORTABLE = "comfortable"  # ample headroom


# Canonical band order (used everywhere a band distribution becomes a vector).
BAND_ORDER: tuple = (
    AffordabilityBand.NEGATIVE,
    AffordabilityBand.STRETCHED,
    AffordabilityBand.MANAGING,
    AffordabilityBand.COMFORTABLE,
)


# ---------------------------------------------------------------------------
# Inference thresholds -- domain-reasoned, NOT fitted to any SIM parameter.
# ---------------------------------------------------------------------------
# The company's own imperfect reading of "what each affordability tier looks
# like from the outside", set by supplier-side reasoning and blind to the SIM's
# hidden budget->income_stress->payment mapping. That independence is the R15
# guarantee the gap is real.

# A "bad" payment = a late payment or a failed direct debit. `bad_rate` is the
# fraction of records in the recent window that are bad.
_SEVERE_BAD_RATE = 0.50          # sustained non-payment -> reads as cannot-pay
_MODERATE_BAD_RATE = 0.15        # intermittent strain -> reads as stretched

# Consumption proxy for wealth. A real supplier has only a very weak read on
# income from metered kWh; this deliberately captures that weakness. Thresholds
# are on annual consumption (kWh) relative to a nominal median.
_MEDIAN_ANNUAL_KWH = 2900.0      # nominal single-fuel median (illustrative, R10)
_HIGH_CONSUMPTION_RATIO = 1.30   # >30% above median -> weak "larger household" signal
_LOW_CONSUMPTION_RATIO = 0.70    # <30% below median -> weak "smaller household" signal


@dataclass(frozen=True)
class AffordabilityObservation:
    """Everything the company can OBSERVE about one customer's ability to pay.
    Every field is a real supplier-side record; none is SIM ground truth. Missing
    signals are simply absent (C-S1: partial observation is normal)."""

    customer_id: str
    segment: str = "resi"
    # Payment records as PaymentBehaviourAnalytics holds them: dicts carrying a
    # "result" of ON_TIME / LATE / DD_FAILED. `recent` is the window under
    # assessment (typically the last 12 months).
    recent_payments: Sequence[dict] = field(default_factory=tuple)
    # An arrears case is open, and how far it escalated (None / "first_notice" /
    # "second_notice" / "default"). Escalation is a strong cannot-pay signal.
    arrears_open: bool = False
    arrears_stage: Optional[str] = None
    arrears_balance_gbp: float = 0.0
    # Metered annual consumption (kWh); None if unread (a real detection blind
    # spot -- a traditional meter never sends a read).
    annual_consumption_kwh: Optional[float] = None
    # The customer's own annual bill (£) and unit rate -- observable.
    annual_bill_gbp: Optional[float] = None
    tariff_unit_rate_gbp_per_mwh: Optional[float] = None
    # Inbound contacts flagged hardship/affordability in the window.
    inbound_hardship_contacts: int = 0


@dataclass(frozen=True)
class AffordabilityAssessment:
    """The company's BELIEF about one customer's ability to pay. `band` is the
    inferred tier the book-composition belief aggregates; `confidence` is monotone
    in signal strength; `signals` records what drove it (audit)."""

    customer_id: str
    band: AffordabilityBand
    confidence: float
    signals: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "customer_id": self.customer_id,
            "band": self.band.value,
            "confidence": round(self.confidence, 4),
            "signals": self.signals,
        }


def _bad_rate(payments: Sequence[dict]) -> Optional[float]:
    """Fraction of records that are LATE or DD_FAILED, or None if the window is
    empty (nothing observed -> no opinion, not a zero)."""
    if not payments:
        return None
    m = compute_payment_metrics(list(payments))
    return m["late_rate"] + m["dd_fail_rate"]


class AffordabilityInference:
    """Infers a per-customer affordability band from observables, and aggregates
    a book-composition belief across a set of customers."""

    def infer_band(self, obs: AffordabilityObservation) -> AffordabilityAssessment:
        bad_rate = _bad_rate(obs.recent_payments)
        signals: dict = {
            "bad_rate": None if bad_rate is None else round(bad_rate, 4),
            "arrears_open": obs.arrears_open,
            "arrears_stage": obs.arrears_stage,
            "inbound_hardship_contacts": obs.inbound_hardship_contacts,
            "annual_consumption_kwh": obs.annual_consumption_kwh,
        }

        # --- Escalated arrears is the strongest cannot-pay signal ----------
        escalated = obs.arrears_open and obs.arrears_stage in (
            "second_notice", "default"
        )

        # --- Payment-behaviour read (primary channel) ---------------------
        # NEGATIVE: sustained non-payment, or escalated arrears, or a moderate
        # payment strain corroborated by the customer telling us they struggle.
        if escalated or (bad_rate is not None and bad_rate >= _SEVERE_BAD_RATE) or (
            bad_rate is not None and bad_rate >= _MODERATE_BAD_RATE
            and obs.inbound_hardship_contacts > 0
        ):
            band = AffordabilityBand.NEGATIVE
            confidence = 0.75 if escalated or (bad_rate or 0) >= _SEVERE_BAD_RATE else 0.6

        # STRETCHED: intermittent strain -- some bad payments, an open (but not
        # yet escalated) arrears case, or a hardship contact without arrears.
        elif (bad_rate is not None and bad_rate >= _MODERATE_BAD_RATE) or (
            obs.arrears_open
        ) or obs.inbound_hardship_contacts > 0:
            band = AffordabilityBand.STRETCHED
            confidence = 0.55

        # Clean payer -> MANAGING or COMFORTABLE. The two are near-indistinguishable
        # from payments alone (both pay on time); the company can only lean on a
        # weak, noisy consumption/bill proxy for "larger/wealthier household". This
        # is exactly where the company is structurally blind (honest gap source).
        else:
            band, confidence = self._clean_payer_band(obs)

        signals["escalated_arrears"] = escalated
        return AffordabilityAssessment(
            customer_id=obs.customer_id, band=band,
            confidence=round(confidence, 4), signals=signals,
        )

    def _clean_payer_band(self, obs: AffordabilityObservation):
        """Disambiguate MANAGING vs COMFORTABLE for a clean payer using only the
        weak consumption proxy. Default is MANAGING -- the company does NOT get to
        assume its clean payers are comfortable, so it systematically under-calls
        COMFORTABLE (a deliberate, honest limitation)."""
        kwh = obs.annual_consumption_kwh
        if kwh is None:
            # No consumption read at all: default to MANAGING, lowest confidence.
            return AffordabilityBand.MANAGING, 0.35
        ratio = kwh / _MEDIAN_ANNUAL_KWH
        if ratio >= _HIGH_CONSUMPTION_RATIO:
            return AffordabilityBand.COMFORTABLE, 0.45   # weak, so low confidence
        return AffordabilityBand.MANAGING, 0.45

    def infer_book(
        self, observations: Sequence[AffordabilityObservation]
    ) -> List[AffordabilityAssessment]:
        """Per-customer inference across the whole book."""
        return [self.infer_band(o) for o in observations]

    def book_composition(
        self, observations: Sequence[AffordabilityObservation]
    ) -> Dict[AffordabilityBand, float]:
        """The company's BELIEF about its own book composition: the fraction of
        customers it infers to sit in each affordability band. Returns a
        distribution (sums to 1) over BAND_ORDER; an empty book yields a uniform
        distribution (no book -> no opinion)."""
        assessments = self.infer_book(observations)
        return composition_of([a.band for a in assessments])


def composition_of(bands: Sequence[AffordabilityBand]) -> Dict[AffordabilityBand, float]:
    """Fraction of `bands` in each band, as a distribution over BAND_ORDER. An
    empty input yields the uniform distribution."""
    n = len(bands)
    if n == 0:
        return {b: 1.0 / len(BAND_ORDER) for b in BAND_ORDER}
    counts = {b: 0 for b in BAND_ORDER}
    for b in bands:
        counts[AffordabilityBand(b)] += 1
    return {b: counts[b] / n for b in BAND_ORDER}


def composition_vector(dist: Mapping[AffordabilityBand, float]) -> List[float]:
    """Turn a band->fraction mapping into a vector in canonical BAND_ORDER, for
    the TV-distance belief gap. Missing bands are treated as 0."""
    return [float(dist.get(b, 0.0)) for b in BAND_ORDER]
