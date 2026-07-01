import datetime as dt
import pytest
from company.market.bsc_performance_assurance_register import (
    BSCPerformanceAssuranceRegister, PAAgentType, PAMetric, PAMetricScore,
    PAAssessmentTier, PAStatus,
)

DATE = dt.date(2022, 4, 1)


def _scores_all_pass():
    return (
        PAMetricScore(PAMetric.MISSING_READS, 99.0, 97.0),
        PAMetricScore(PAMetric.LATE_DATA_FLOWS, 98.0, 95.0),
    )


def _scores_one_breach():
    return (
        PAMetricScore(PAMetric.MISSING_READS, 95.0, 97.0),
        PAMetricScore(PAMetric.LATE_DATA_FLOWS, 98.0, 95.0),
    )


def _scores_three_breaches():
    return (
        PAMetricScore(PAMetric.MISSING_READS, 90.0, 97.0),
        PAMetricScore(PAMetric.LATE_DATA_FLOWS, 80.0, 95.0),
        PAMetricScore(PAMetric.ERRONEOUS_READS, 90.0, 99.0),
    )


def _reg(scores=None):
    r = BSCPerformanceAssuranceRegister()
    r.record_assessment(PAAgentType.SUPPLIER, "TestDA", 2022, 1, DATE, scores or _scores_all_pass())
    return r


def test_assessment_id_prefix():
    reg = _reg()
    assert reg._records[0].assessment_id.startswith("PA-")


def test_status_default_open():
    reg = _reg()
    assert reg._records[0].status == PAStatus.OPEN


def test_tier_standard_zero_breaches():
    reg = _reg(_scores_all_pass())
    assert reg._records[0].tier == PAAssessmentTier.STANDARD


def test_tier_watch_one_breach():
    reg = _reg(_scores_one_breach())
    assert reg._records[0].tier == PAAssessmentTier.WATCH


def test_tier_formal_action_three_breaches():
    reg = _reg(_scores_three_breaches())
    assert reg._records[0].tier == PAAssessmentTier.FORMAL_ACTION


def test_rap_required_for_watch():
    reg = _reg(_scores_one_breach())
    assert reg._records[0].rap_required is True


def test_rap_not_required_for_standard():
    reg = _reg(_scores_all_pass())
    assert reg._records[0].rap_required is False


def test_submit_assessment_changes_status():
    reg = _reg()
    aid = reg._records[0].assessment_id
    updated = reg.submit_assessment(aid)
    assert updated.status == PAStatus.SUBMITTED


def test_invalid_quarter_raises():
    reg = BSCPerformanceAssuranceRegister()
    with pytest.raises(ValueError):
        reg.record_assessment(PAAgentType.SUPPLIER, "X", 2022, 5, DATE, _scores_all_pass())


def test_rap_due_date_at_least_20_calendar_days():
    reg = _reg(_scores_one_breach())
    r = reg._records[0]
    due = r.rap_due_date
    assert due is not None
    assert (due - DATE).days >= 20
