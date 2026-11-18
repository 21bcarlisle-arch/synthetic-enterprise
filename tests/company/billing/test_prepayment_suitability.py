"""The S&RP finding is positive only on a clear, dated conversation, and the gate reads its date.

Defect each leg names: a finding positive without asking (no evidence read as a yes); a 3.7 ground
read as a positive or a "person to decide"; a further-assessment ground found positive by a
machine; an unanswered question passed; a finding that never lapses (28.3); a bare True accepted.
"""
from __future__ import annotations

import datetime as dt

from company.billing.prepayment_suitability import (
    FINDING_LAPSE_DAYS,
    SuitabilityAnswers,
    assess_prepayment_suitability,
)
from company.billing.winter_moratorium import (
    NO_SUITABILITY_FINDING,
    NOT_SUITABLE,
    SAFE_AND_PRACTICABLE,
    SUITABILITY_UNANSWERED,
    EnforcementAction,
    EnforcementCase,
    may_take,
)
from company.regulatory.priority_services_register import ProtectionRecord, PSRCategory

ASKED, ON = dt.date(2024, 3, 1), dt.date(2024, 6, 30)
CLEAR = SuitabilityAnswers(ASKED, **{f: False for f in SuitabilityAnswers.__dataclass_fields__
                                     if f != "asked_on"})


def _with(**kw):
    return SuitabilityAnswers(**{**CLEAR.__dict__, **kw})


def _usable(record, on=ON):
    return record is not None and record.unusable_on(on) is None


def test_the_finding_is_positive_only_when_asked_clear_and_in_date():
    # The permit leg first: a guard that refuses everything fails here.
    positive = assess_prepayment_suitability(ON, answers=CLEAR)
    assert _usable(positive) and positive.kind == SAFE_AND_PRACTICABLE and positive.met
    assert positive.lapses_on == ASKED + dt.timedelta(days=FINDING_LAPSE_DAYS)

    # Never asked, nothing held: no finding at all, not a positive one.
    assert assess_prepayment_suitability(ON) is None

    negatives = {
        "do-not-install category": dict(categories=(PSRCategory.MEDICAL_EQUIPMENT,), answers=CLEAR),
        "further-assessment category": dict(categories=(PSRCategory.MENTAL_HEALTH,), answers=CLEAR),
        "needs code": dict(needs_codes=(33,), answers=CLEAR),
        "over 65": dict(date_of_birth=dt.date(1950, 1, 1), answers=CLEAR),
        "do-not-install answer": dict(answers=_with(child_under_2=True)),
        "further-assessment answer": dict(answers=_with(pregnancy_or_bereavement=True)),
        "unanswered": dict(answers=_with(over_75_without_support=None)),
        "held, never asked": dict(categories=(PSRCategory.CHRONIC_ILLNESS,)),
    }
    for name, kw in negatives.items():
        record = assess_prepayment_suitability(ON, **kw)
        assert record is not None and not record.met and record.evidence, name
        assert not _usable(record), name

    assert any("do-not-install" in e for e in assess_prepayment_suitability(
        ON, categories=(PSRCategory.MEDICAL_EQUIPMENT,)).evidence)
    assert all("person to decide" in e for e in assess_prepayment_suitability(
        ON, categories=(PSRCategory.MENTAL_HEALTH,)).evidence)

    # Dated: asked after the day is not yet known; a year on it has lapsed (SLC 28.3).
    assert assess_prepayment_suitability(ASKED - dt.timedelta(days=1), answers=CLEAR) is None
    assert not _usable(positive, ASKED + dt.timedelta(days=FINDING_LAPSE_DAYS))
    assert _usable(positive, ASKED + dt.timedelta(days=FINDING_LAPSE_DAYS - 1))


def test_the_gate_takes_the_dated_finding_and_names_why_it_refuses():
    def gate(suitability):
        return may_take(EnforcementAction.CONSENT_PPM_OFFER, EnforcementCase(
            account_id="H", as_of=ON, suitability=suitability))

    def srp_refusal(det):
        return [r for c, r in det.refusals if c == "slc_27_6_a_iii_safe_and_practicable"]

    assert srp_refusal(gate(assess_prepayment_suitability(ON, answers=CLEAR))) == []
    assert srp_refusal(gate(None)) == [NO_SUITABILITY_FINDING]
    (bare,) = srp_refusal(gate(True))
    assert bare.startswith(NO_SUITABILITY_FINDING) and "not a dated" in bare
    (negative,) = srp_refusal(gate(assess_prepayment_suitability(ON, answers=_with(child_under_2=True))))
    assert negative.startswith(NOT_SUITABLE) and "child_under_2" in negative
    lapsed = ProtectionRecord(SAFE_AND_PRACTICABLE, ASKED, ASKED + dt.timedelta(days=1))
    (stale,) = srp_refusal(gate(lapsed))
    assert "lapsed" in stale


def test_an_unanswered_conversation_is_refused_as_unanswered_not_as_negative():
    """C32 tenth pass, class 7. The refusal was right but its words were not: a conversation
    whose only bar is unanswered questions printed "finding is negative". Defects: unanswered
    evidence called negative; a real bar beside an unanswered one called merely unanswered."""
    def srp(record):
        det = may_take(EnforcementAction.CONSENT_PPM_OFFER, EnforcementCase(
            account_id="H", as_of=ON, suitability=record))
        return [r for c, r in det.refusals if c == "slc_27_6_a_iii_safe_and_practicable"]

    all_unanswered = SuitabilityAnswers(ASKED)  # asked, every answer None
    (only_unanswered,) = srp(assess_prepayment_suitability(ON, answers=all_unanswered))
    assert only_unanswered.startswith(SUITABILITY_UNANSWERED), only_unanswered
    assert "negative" not in only_unanswered and "over_75_without_support" in only_unanswered

    (mixed,) = srp(assess_prepayment_suitability(
        ON, answers=_with(child_under_2=True, over_75_without_support=None)))
    assert mixed.startswith(NOT_SUITABLE) and "child_under_2" in mixed

    (held,) = srp(assess_prepayment_suitability(
        ON, categories=(PSRCategory.MEDICAL_EQUIPMENT,), answers=_with(over_75_without_support=None)))
    assert held.startswith(NOT_SUITABLE)
