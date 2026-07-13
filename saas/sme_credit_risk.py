"""C8_sme_credit_risk -- company-side SME / I&C credit-risk assessment twin.

The company cannot see the SIM business-distress stream
(``simulation.sme_distress``, W2_6). It never reads it. This assessor INFERS a
business customer's credit risk -- and, critically, ATTRIBUTES a late payment to
genuine DISTRESS vs mere late-payment CULTURE -- from OBSERVABLES ONLY:

    * payment pattern    -- the fraction of recent bills paid late / DD-failed,
                            and how that compares to the customer's own baseline
                            (the single strongest observable of cash-flow strain).
    * payment timing     -- how many days late, and whether that is worsening.
    * sector             -- the SIC/sector the supplier already holds; some
                            sectors (construction, hospitality, retail) fail more
                            often. The company's OWN public-knowledge view, set
                            independently of the SIM's hidden hazard multipliers.
    * tenure             -- how long they have been a customer; a long-tenured
                            business that has ALWAYS paid a little late is far more
                            likely a habitual-late-payer than a new distress.
    * consumption        -- a sustained collapse in metered kWh corroborates a
                            business winding down (distress / insolvency).
    * segment            -- SME vs I&C.

THE CONFOUND (the whole point of the atom). A genuinely DISTRESSED business and a
habitual-late-payer (CULTURE) emit the IDENTICAL observable: a late payment. In a
single snapshot they are indistinguishable. The company's ONLY handles are
TEMPORAL (persistence vs onset), SECTORAL, and consumption -- and those handles
are systematically FOOLED by the hardest case: a business that was always late by
habit AND then slides into real distress still just looks "always late", so the
company reads it as CULTURE and misses the distress. That misread is the expensive
error, and it is where the measured belief-vs-truth GAP comes from. This assessor
is ALLOWED TO BE WRONG; disentangling the confound from observables alone is
genuinely hard, which is the coupled triad's point. Do NOT "improve" it by giving
it more visibility than a real supplier holds -- that would be an epistemic-wall
violation, not a fix.

EPISTEMIC WALL. This module imports NOTHING from ``simulation.*`` /  ``sim.*``.
Its inputs are observables a real supplier holds in its own systems (payment
records, the sector on file, tenure, meter reads). Its thresholds are set by
supplier-side credit-risk reasoning, DELIBERATELY BLIND to the SIM's hidden
distress/culture parameters -- that independence is what makes the measured gap
real rather than a tautology (CLAUDE.md R15). It is a pure module: plain
dicts/values in, a dataclass out; no wall-clock, no unseeded randomness (C-S2);
it works on whatever observation window it is given and never assumes a complete
or ordered batch (C-S1).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Company-owned label space. These MIRROR the shape of the hidden SIM answer key
# (simulation.sme_distress.LatePaymentCause) but are defined HERE, independently
# -- the company never imports the SIM enum. They are the company's BELIEF, not
# ground truth.
# ---------------------------------------------------------------------------
class CreditRiskCause(str, Enum):
    """The company's inferred cause of a business's payment behaviour."""
    NONE = "none"            # paying on time -- no credit concern
    CULTURE = "culture"      # believed a habitual late-payer, healthy & solvent
    DISTRESS = "distress"    # believed genuine cash-flow distress
    INSOLVENCY = "insolvency"  # believed ceased / ceasing to trade


#: The 2x2 ABILITY x WILLINGNESS quadrant each cause maps to. This is the space
#: background.gap_metric.classification_gap scores. The CONFOUND lives on the
#: ABILITY axis: CULTURE = (can, wont) -- can pay, pays late by habit; DISTRESS /
#: INSOLVENCY = (cannot, wont) -- genuinely cannot pay. Both are LATE (wont); they
#: differ ONLY on ability, which is exactly where the 8:1 harm asymmetry sits
#: (mistaking real distress for mere habit -> unprovisioned bad debt + heavy-handed
#: collection on a struggling business = the expensive cannot->can error).
_CAUSE_QUADRANT = {
    CreditRiskCause.NONE: ("can", "will"),
    CreditRiskCause.CULTURE: ("can", "wont"),
    CreditRiskCause.DISTRESS: ("cannot", "wont"),
    CreditRiskCause.INSOLVENCY: ("cannot", "wont"),
}


def cause_to_quadrant(cause) -> Tuple[str, str]:
    """Map a cause label (a ``CreditRiskCause``, or the equivalent string from
    the SIM answer key -- 'none'/'culture'/'distress'/'insolvency') to its
    (ability, willingness) quadrant. Defined once so BOTH the company belief and
    the harness's SIM-truth labels project onto the identical 2x2 space without
    the twin ever importing the SIM enum (the harness passes the SIM label's
    STRING value, not the object)."""
    if isinstance(cause, CreditRiskCause):
        return _CAUSE_QUADRANT[cause]
    key = str(getattr(cause, "value", cause)).lower()
    try:
        return _CAUSE_QUADRANT[CreditRiskCause(key)]
    except ValueError as exc:
        raise ValueError(f"unrecognised cause label {cause!r}") from exc


# ---------------------------------------------------------------------------
# Credit-risk thresholds -- domain-reasoned, NOT fitted to any SIM parameter.
# The company's own reading of "what business distress looks like", set blind to
# the SIM's hidden distress-onset / culture-incidence / sector-hazard numbers.
# That independence is what makes the gap a real measurement (R15), and these are
# FROZEN -- never tuned toward a gap number (R12 / R13).
# ---------------------------------------------------------------------------
_MATERIALLY_LATE_RATE = 0.25    # >=25% of recent bills bad -> materially late now
_PERSISTENT_LATE_RATE = 0.25    # baseline ALSO >=25% bad -> habitual, not new
_ONSET_DELTA = 0.25             # >=25pt jump vs baseline -> a deterioration (onset)
_SEVERE_LATE_RATE = 0.60        # this bad -> read as acute, not a mild slip
_INSOLVENCY_CONSUMPTION_DROP = -0.40  # >=40% kWh collapse corroborates wind-down
_LONG_TENURE_YEARS = 3.0        # a track record long enough to read "always late"

#: The company's OWN public-knowledge view of higher-failure sectors. Set from a
#: real credit team's general knowledge (construction, hospitality and retail are
#: widely known to fail more), DELIBERATELY not copied from the SIM's hidden
#: _SECTOR_SHOCK_MULT -- an independent, imperfect reading (R15). The company even
#: uses coarser labels than the SIM may hold.
_COMPANY_HIGH_RISK_SECTORS = frozenset({
    "construction",
    "wholesale_retail",
    "retail",
    "accommodation_food",
    "hospitality",
})

_RISK_SCORE_BY_CAUSE = {
    CreditRiskCause.NONE: 0.05,
    CreditRiskCause.CULTURE: 0.30,
    CreditRiskCause.DISTRESS: 0.75,
    CreditRiskCause.INSOLVENCY: 0.95,
}


@dataclass(frozen=True)
class BusinessObservationWindow:
    """Everything the company can OBSERVE about one business customer across a
    detection window. Every field is a real supplier-side record; none is SIM
    ground truth. Missing signals are simply absent (C-S1: partial observation is
    normal, never assumed complete)."""

    customer_id: str
    segment: str                              # "SME" | "I&C"
    sector: Optional[str] = None              # SIC/sector on file, may be unknown
    tenure_years: Optional[float] = None      # length of the supply relationship
    # Payment records: dicts with "result" in ON_TIME / LATE / DD_FAILED and an
    # optional "days_late". baseline = the settled prior period; recent = the
    # window under assessment.
    baseline_payments: Sequence[dict] = field(default_factory=tuple)
    recent_payments: Sequence[dict] = field(default_factory=tuple)
    # Metered consumption (kWh) for the same two periods; None if unread (a real
    # blind spot -- a traditional-metered SME may not be read for months).
    baseline_consumption_kwh: Optional[float] = None
    recent_consumption_kwh: Optional[float] = None


@dataclass(frozen=True)
class SmeCreditAssessment:
    """The company's BELIEF about one business customer. ``is_late`` is the raw
    observable; ``inferred_cause`` is the fallible distress-vs-culture call the
    classification gap scores; ``quadrant`` projects it onto the 2x2 the shared
    metric reads."""

    customer_id: str
    is_late: bool
    inferred_cause: CreditRiskCause
    risk_score: float                         # 0..1, monotone in believed risk
    ability: str                              # "can" | "cannot"
    willingness: str                          # "will" | "wont"
    signals: dict = field(default_factory=dict)

    @property
    def quadrant(self) -> Tuple[str, str]:
        return (self.ability, self.willingness)

    def to_dict(self) -> dict:
        return {
            "customer_id": self.customer_id,
            "is_late": self.is_late,
            "inferred_cause": self.inferred_cause.value,
            "risk_score": round(self.risk_score, 4),
            "ability": self.ability,
            "willingness": self.willingness,
            "signals": self.signals,
        }


def _bad_rate(payments: Sequence[dict]) -> Optional[float]:
    """Fraction of records that are LATE or DD_FAILED, or None if the window is
    empty (nothing observed -> no opinion, not a zero)."""
    if not payments:
        return None
    bad = sum(1 for r in payments if r.get("result") in ("LATE", "DD_FAILED"))
    return bad / len(payments)


def _avg_days_late(payments: Sequence[dict]) -> Optional[float]:
    vals = [
        float(r.get("days_late", 0) or 0)
        for r in payments
        if r.get("result") in ("LATE", "DD_FAILED")
    ]
    return sum(vals) / len(vals) if vals else None


def _consumption_shift_pct(window: BusinessObservationWindow) -> Optional[float]:
    b = window.baseline_consumption_kwh
    r = window.recent_consumption_kwh
    if not b or r is None:
        return None
    return (r - b) / b


class SmeCreditRiskAssessor:
    """Infers business credit risk and attributes late payment to distress vs
    culture, from observables only. Stateless and deterministic (C-S2)."""

    def assess(self, window: BusinessObservationWindow) -> SmeCreditAssessment:
        recent_bad = _bad_rate(window.recent_payments)
        baseline_bad = _bad_rate(window.baseline_payments)
        shift = _consumption_shift_pct(window)
        sector = (window.sector or "").lower()
        sector_high_risk = sector in _COMPANY_HIGH_RISK_SECTORS
        tenure = window.tenure_years

        signals = {
            "recent_bad_rate": None if recent_bad is None else round(recent_bad, 4),
            "baseline_bad_rate": None if baseline_bad is None else round(baseline_bad, 4),
            "recent_avg_days_late": _avg_days_late(window.recent_payments),
            "consumption_shift_pct": None if shift is None else round(shift, 4),
            "sector": sector or None,
            "sector_high_risk": sector_high_risk,
            "tenure_years": tenure,
        }

        # --- Not materially late now -> no credit concern -------------------
        if recent_bad is None or recent_bad < _MATERIALLY_LATE_RATE:
            return self._result(window.customer_id, False, CreditRiskCause.NONE, signals)

        # --- Insolvency read: acute lateness + a consumption collapse -------
        if (
            recent_bad >= _SEVERE_LATE_RATE
            and shift is not None
            and shift <= _INSOLVENCY_CONSUMPTION_DROP
        ):
            return self._result(
                window.customer_id, True, CreditRiskCause.INSOLVENCY, signals
            )

        # --- Distress vs culture: the confound. Handles are TEMPORAL --------
        persistent = baseline_bad is not None and baseline_bad >= _PERSISTENT_LATE_RATE
        deterioration = (
            baseline_bad is not None and (recent_bad - baseline_bad) >= _ONSET_DELTA
        )
        long_tenure = tenure is not None and tenure >= _LONG_TENURE_YEARS

        if deterioration and not persistent:
            # Clean(ish) baseline that has suddenly worsened -> genuine onset.
            cause = CreditRiskCause.DISTRESS
        elif persistent and not deterioration:
            # Always been a bit late, no worsening -> read as habitual CULTURE.
            # BUT a high-risk sector paying persistently AND severely late is the
            # one case the company leans distress on -- a defensible, error-prone
            # heuristic (it will over-call some healthy high-risk-sector late-payers,
            # and it STILL misses the always-late business that has quietly become
            # distressed: that miss is the expensive cannot->can error, by design).
            if sector_high_risk and recent_bad >= _SEVERE_LATE_RATE and not long_tenure:
                cause = CreditRiskCause.DISTRESS
            else:
                cause = CreditRiskCause.CULTURE
        else:
            # Ambiguous (no baseline to compare, or mixed signals). Fall back on
            # sector + severity; long tenure nudges toward habit.
            if (sector_high_risk or recent_bad >= _SEVERE_LATE_RATE) and not long_tenure:
                cause = CreditRiskCause.DISTRESS
            else:
                cause = CreditRiskCause.CULTURE

        return self._result(window.customer_id, True, cause, signals)

    def assess_many(
        self, windows: Sequence[BusinessObservationWindow]
    ) -> List[SmeCreditAssessment]:
        return [self.assess(w) for w in windows]

    @staticmethod
    def _result(
        customer_id: str, is_late: bool, cause: CreditRiskCause, signals: dict
    ) -> SmeCreditAssessment:
        ability, willingness = cause_to_quadrant(cause)
        return SmeCreditAssessment(
            customer_id=customer_id,
            is_late=is_late,
            inferred_cause=cause,
            risk_score=_RISK_SCORE_BY_CAUSE[cause],
            ability=ability,
            willingness=willingness,
            signals=signals,
        )
