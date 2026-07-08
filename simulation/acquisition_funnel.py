"""Acquisition funnel -- PROCESS_NOT_EVENTS.md Section 5 / PROCESS_MODEL.md Section 5.

Replaces the single flat win/lose coin flip (saas.growth_mandate.roll_acquisition)
with a real multi-stage funnel with per-stage leakage and per-stage cost.

Per the research doc Section 3, compounding realistic UK stage-conversion rates from
true top-of-funnel awareness would only give ~2% win rate -- 10x below the sim's
existing 20% flat rate. Adopted interpretation: the sim's existing "attempt" already
represents a QUOTE-ISSUED event (mid-funnel), consistent with the GBP150/GBP400
cost-per-attempt looking like quote/application-processing cost, not a
marketing-impression cost. This module does NOT model awareness/consideration as a
lead-volume funnel (scope creep for a sim that tracks individual customer slots, not
marketing impressions); saas.growth_mandate.should_attempt_acquisition() remains the
awareness/consideration gate. This module owns quote onward.

Stage order: quote -> application -> credit_check -> onboarding -> cooling_off.
"quote" is the entry point (attempt == quote issued).

Phase 3 (CORE_FIDELITY_PHASES.md item 5, unhappy-path audit finding #5):
"the funnel is real in outcome but instant in time" -- all 5 stages
previously resolved against a single `term_start` with zero calendar-day
spacing. Each `FunnelStageEvent` now carries a real `stage_date`, walked
forward from `term_start` (the quote-issued date, unchanged entry-point
semantics -- no caller's use of `term_start` itself changes). Stage-to-stage
gaps are provisional short distributions (⚠ not discovery-agent-verified)
except cooling_off, which is a real, hard-anchored constant: the Consumer
Contracts (Information, Cancellation and Additional Charges) Regulations
2013 give a statutory 14-calendar-day cancellation window for off-premises/
distance energy contracts -- `COOLING_OFF_PERIOD_DAYS` below.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import date, timedelta

FUNNEL_STAGES: tuple[str, ...] = (
    "quote",
    "application",
    "credit_check",
    "onboarding",
    "cooling_off",
)

# Section 2 table, row "quote to application": resi 15-30%, SME 20-35% (confidence M/L).
# Picked near the upper-middle of each range -- Section 3 finding: upper-end stage rates
# are needed to reproduce the sim existing ~20%/12% flat win rates under the mid-funnel
# interpretation.
QUOTE_TO_APPLICATION: dict[str, float] = {
    "resi": 0.24,
    "SME": 0.28,
}

# Section 2 table, row "application to credit_check pass": resi 90-97%, SME 80-92%.
# NOT used to gate the credit_check stage itself (delegated entirely to a
# CreditBureauPort adapter, which injects its own noisy signal). Retained only as the
# documented "true" underlying creditworthy-application rate for calibration reference.
APPLICATION_TRUE_CREDITWORTHY_RATE: dict[str, float] = {
    "resi": 0.94,
    "SME": 0.86,
}

# Section 2 table, row "credit_check to onboarding completion": resi 92-98%, SME 90-97%.
CREDIT_CHECK_TO_ONBOARDING: dict[str, float] = {
    "resi": 0.95,
    "SME": 0.93,
}

# Section 2 table, row "onboarding to survives cooling_off (14-day)": resi pre-2022
# 75-88%, post-2022 (REC) 88-96% -- Ofgem Retail Energy Code (REC) reform, live
# 2022-07-01, shortened the objection/win-back window from ~15-17 working days to
# next-working-day (confidence M for the regime fact, L for the specific rates). SME
# 85-95%, kept FLAT: the research doc explicitly finds REC reform is domestic-specific
# (SME off-premises statutory cooling-off is a separate regime, not touched by the
# domestic switching-speed reform).
REC_REFORM_DATE = date(2022, 7, 1)

ONBOARDING_TO_COOLING_OFF_SURVIVAL: dict[str, dict[str, float]] = {
    "resi": {"pre": 0.80, "post": 0.92},
    "SME": {"pre": 0.90, "post": 0.90},
}

# Phase 3 item 5: stage-to-stage calendar-day spacing. Ranges are provisional
# short distributions (⚠ not discovery-agent-verified) except cooling_off,
# a real statutory constant -- see module docstring.
_QUOTE_TO_APPLICATION_DAYS = (1, 14)
_APPLICATION_TO_CREDIT_CHECK_DAYS = (0, 2)
_CREDIT_CHECK_TO_ONBOARDING_DAYS = (1, 5)
COOLING_OFF_PERIOD_DAYS = 14
_STAGE_DAY_RANGE: dict[str, tuple[int, int]] = {
    "quote": (0, 0),
    "application": _QUOTE_TO_APPLICATION_DAYS,
    "credit_check": _APPLICATION_TO_CREDIT_CHECK_DAYS,
    "onboarding": _CREDIT_CHECK_TO_ONBOARDING_DAYS,
    "cooling_off": (COOLING_OFF_PERIOD_DAYS, COOLING_OFF_PERIOD_DAYS),
}

# Section 4 cost-per-stage split -- explicitly labelled an estimate/analogue in the
# research doc (no sourced UK energy-specific CAC stage-cost breakdown found). "quote"
# carries the bulk of committed cost since that is when the existing flat
# GBP150/GBP400 attempt cost is currently spent (mid-funnel entry point). Fractions
# must sum to 1.0 across FUNNEL_STAGES; "cooling_off" itself has no residual cost
# increment (all cost is already booked by the time onboarding completes).
STAGE_COST_SHARE: dict[str, float] = {
    "quote": 0.65,
    "application": 0.10,
    "credit_check": 0.05,
    "onboarding": 0.20,
    "cooling_off": 0.0,
}

assert abs(sum(STAGE_COST_SHARE.values()) - 1.0) < 1e-9
assert tuple(STAGE_COST_SHARE.keys()) == FUNNEL_STAGES


@dataclass
class FunnelStageEvent:
    stage: str
    passed: bool
    cost_increment_gbp: float
    stage_date: str  # ISO date -- real calendar spacing from quote (Phase 3 item 5)


@dataclass
class AcquisitionFunnelResult:
    segment: str
    term_start: str  # ISO date string
    stage_reached: str  # last stage attempted, whether passed or failed
    won: bool  # True iff survived cooling_off
    total_cost_gbp: float
    stages: list[FunnelStageEvent] = field(default_factory=list)
    credit_bureau_score_band: str | None = None  # None if credit_check never reached
    credit_bureau_passed: bool | None = None  # None if credit_check never reached
    # SIM-internal ground truth (tools.credit_bureau_port.CreditCheckResult's third
    # field), retained here for saas/reporting evidence-surface use only (false-decline/
    # false-accept divergence), same pattern as this repo's churn ground-truth retention.
    # None if credit_check never reached, or if the bureau used doesn't expose it.
    # MUST NEVER be read by company/** decision code -- enforced by
    # tests/tools/test_credit_bureau_adapter.py's epistemic guard.
    credit_bureau_true_creditworthy: bool | None = None


def _quote_to_application_rate(segment: str) -> float:
    return QUOTE_TO_APPLICATION.get(segment, QUOTE_TO_APPLICATION["resi"])


def _credit_check_to_onboarding_rate(segment: str) -> float:
    return CREDIT_CHECK_TO_ONBOARDING.get(segment, CREDIT_CHECK_TO_ONBOARDING["resi"])


def _cooling_off_survival_rate(segment: str, term_start: date) -> float:
    rates = ONBOARDING_TO_COOLING_OFF_SURVIVAL.get(
        segment, ONBOARDING_TO_COOLING_OFF_SURVIVAL["resi"]
    )
    regime = "post" if term_start >= REC_REFORM_DATE else "pre"
    return rates[regime]


def _stage_cost_increment(stage: str, total_amount_gbp: float) -> float:
    return round(STAGE_COST_SHARE.get(stage, 0.0) * total_amount_gbp, 2)


def _bernoulli(seed: str, stage_name: str, pass_rate: float) -> bool:
    rng = random.Random(seed + "_" + stage_name)
    return rng.random() <= pass_rate


def _stage_day_offset(seed: str, stage: str) -> int:
    """Calendar days this stage takes AFTER the previous stage (Phase 3
    item 5). cooling_off is a fixed statutory 14 days, not a roll."""
    lo, hi = _STAGE_DAY_RANGE.get(stage, (0, 0))
    if lo == hi:
        return lo
    rng = random.Random(seed + "_" + stage + "_days")
    return rng.randint(lo, hi)


def run_acquisition_funnel(segment, seed, term_start, credit_bureau, total_amount_gbp=None):
    """Run quote -> application -> credit_check -> onboarding -> cooling_off.

    credit_bureau must expose .check_credit(applicant_id, segment, seed) -> result
    where result has .passed (bool) and .score_band (str) attributes -- matches the
    CreditBureauPort Protocol in tools.credit_bureau_port (structural typing only).

    total_amount_gbp is the full committed cost for a WON attempt (mirrors the
    existing flat saas.growth_mandate.COST_PER_ACQUISITION[segment]); defaults to it
    when not supplied.

    Every stage draws from an independent seeded RNG except credit_check, which is
    delegated to credit_bureau. Same seed + term_start always reproduces the same
    result.
    """
    if total_amount_gbp is None:
        from saas.growth_mandate import COST_PER_ACQUISITION
        total_amount_gbp = COST_PER_ACQUISITION.get(segment, COST_PER_ACQUISITION["resi"])

    stages = []
    state = {"cost": 0.0, "band": None, "passed": None, "elapsed_days": 0}
    state["true_creditworthy"] = None

    def _record(stage, passed):
        increment = _stage_cost_increment(stage, total_amount_gbp)
        state["cost"] += increment
        state["elapsed_days"] += _stage_day_offset(seed, stage)
        stage_date = (term_start + timedelta(days=state["elapsed_days"])).isoformat()
        stages.append(FunnelStageEvent(
            stage=stage, passed=passed, cost_increment_gbp=increment, stage_date=stage_date,
        ))

    def _result(stage_reached, won):
        return AcquisitionFunnelResult(
            segment=segment,
            term_start=term_start.isoformat(),
            stage_reached=stage_reached,
            won=won,
            total_cost_gbp=round(state["cost"], 2),
            stages=stages,
            credit_bureau_score_band=state["band"],
            credit_bureau_passed=state["passed"],
            credit_bureau_true_creditworthy=state["true_creditworthy"],
        )

    _record("quote", True)

    passed = _bernoulli(seed, "application", _quote_to_application_rate(segment))
    _record("application", passed)
    if not passed:
        return _result("application", False)

    credit_result = credit_bureau.check_credit(
        applicant_id=seed, segment=segment, seed=seed + "_credit_check"
    )
    state["passed"] = bool(credit_result.passed)
    state["band"] = credit_result.score_band
    state["true_creditworthy"] = getattr(credit_result, "true_creditworthy", None)
    _record("credit_check", state["passed"])
    if not state["passed"]:
        return _result("credit_check", False)

    passed = _bernoulli(seed, "onboarding", _credit_check_to_onboarding_rate(segment))
    _record("onboarding", passed)
    if not passed:
        return _result("onboarding", False)

    passed = _bernoulli(seed, "cooling_off", _cooling_off_survival_rate(segment, term_start))
    _record("cooling_off", passed)
    return _result("cooling_off", passed)
