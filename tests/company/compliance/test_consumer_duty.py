import pytest
from company.compliance.consumer_duty import (
    ConsumerDutyRegister, DutyOutcome, OutcomeAssessment, OutcomeRAG
)


def _assessment(outcome=DutyOutcome.PRICE_AND_VALUE, rag=OutcomeRAG.GREEN,
                metric=8.5, date="2023-09-30"):
    return OutcomeAssessment(
        outcome=outcome,
        assessment_date=date,
        rag=rag,
        metric_value=metric,
        metric_name="value_score",
        narrative="Within target",
    )


def test_record_assessment():
    reg = ConsumerDutyRegister()
    a = reg.record_assessment(_assessment())
    assert a.outcome == DutyOutcome.PRICE_AND_VALUE
    assert a.is_compliant is True


def test_is_compliant_amber():
    a = _assessment(rag=OutcomeRAG.AMBER)
    assert a.is_compliant is True


def test_is_compliant_red():
    a = _assessment(rag=OutcomeRAG.RED)
    assert a.is_compliant is False


def test_assessments_for_outcome():
    reg = ConsumerDutyRegister()
    reg.record_assessment(_assessment(outcome=DutyOutcome.PRICE_AND_VALUE))
    reg.record_assessment(_assessment(outcome=DutyOutcome.PRICE_AND_VALUE))
    reg.record_assessment(_assessment(outcome=DutyOutcome.CONSUMER_SUPPORT))
    assert len(reg.assessments_for_outcome(DutyOutcome.PRICE_AND_VALUE)) == 2


def test_latest_for_outcome_picks_most_recent():
    reg = ConsumerDutyRegister()
    reg.record_assessment(_assessment(date="2023-06-30"))
    reg.record_assessment(_assessment(date="2023-09-30"))
    latest = reg.latest_for_outcome(DutyOutcome.PRICE_AND_VALUE)
    assert latest.assessment_date == "2023-09-30"


def test_latest_none_when_empty():
    reg = ConsumerDutyRegister()
    assert reg.latest_for_outcome(DutyOutcome.CONSUMER_SUPPORT) is None


def test_red_outcomes():
    reg = ConsumerDutyRegister()
    reg.record_assessment(_assessment(outcome=DutyOutcome.CONSUMER_SUPPORT, rag=OutcomeRAG.RED))
    reg.record_assessment(_assessment(outcome=DutyOutcome.PRICE_AND_VALUE, rag=OutcomeRAG.GREEN))
    assert len(reg.red_outcomes()) == 1


def test_overall_rag_red_when_any_red():
    reg = ConsumerDutyRegister()
    reg.record_assessment(_assessment(outcome=DutyOutcome.CONSUMER_UNDERSTANDING, rag=OutcomeRAG.RED))
    reg.record_assessment(_assessment(outcome=DutyOutcome.PRICE_AND_VALUE, rag=OutcomeRAG.GREEN))
    assert reg.overall_rag() == OutcomeRAG.RED


def test_overall_rag_green_all_green():
    reg = ConsumerDutyRegister()
    for outcome in DutyOutcome:
        reg.record_assessment(_assessment(outcome=outcome, rag=OutcomeRAG.GREEN))
    assert reg.overall_rag() == OutcomeRAG.GREEN


def test_overall_rag_empty():
    reg = ConsumerDutyRegister()
    assert reg.overall_rag() == OutcomeRAG.GREEN


def test_outcomes_summary_keys():
    reg = ConsumerDutyRegister()
    reg.record_assessment(_assessment(outcome=DutyOutcome.PRICE_AND_VALUE))
    s = reg.outcomes_summary()
    assert "overall_rag" in s
    assert "red_outcomes" in s
    assert "outcomes" in s
    assert DutyOutcome.PRICE_AND_VALUE.value in s["outcomes"]


def test_outcomes_summary_unassessed_outcome_null():
    reg = ConsumerDutyRegister()
    reg.record_assessment(_assessment(outcome=DutyOutcome.PRICE_AND_VALUE))
    s = reg.outcomes_summary()
    support = s["outcomes"][DutyOutcome.CONSUMER_SUPPORT.value]
    assert support["rag"] is None
    assert support["assessments_count"] == 0
