"""Tests for Phase HK: BSC Performance Assurance Register."""
import datetime as dt
import pytest
from company.market.bsc_performance_assurance_register import (
    BSCPerformanceAssuranceRegister,
    PAAgentType,
    PAAssessmentTier,
    PAMetric,
    PAMetricScore,
    PAStatus,
    _METRIC_THRESHOLDS,
    _add_working_days,
)


def _score(metric: PAMetric, pct: float) -> PAMetricScore:
    return PAMetricScore(metric=metric, score_pct=pct, threshold_pct=_METRIC_THRESHOLDS[metric])


def _all_pass() -> tuple:
    return tuple(_score(m, _METRIC_THRESHOLDS[m] + 1.0) for m in PAMetric)


def _one_breach() -> tuple:
    scores = list(_all_pass())
    bad = _score(PAMetric.MISSING_READS, 90.0)
    scores[0] = bad
    return tuple(scores)


def _three_breaches() -> tuple:
    scores = list(_all_pass())
    scores[0] = _score(PAMetric.MISSING_READS, 90.0)
    scores[1] = _score(PAMetric.LATE_DATA_FLOWS, 80.0)
    scores[2] = _score(PAMetric.ERRONEOUS_READS, 95.0)
    return tuple(scores)


DATE = dt.date(2024, 4, 1)


class TestAddWorkingDays:
    def test_skips_weekends(self):
        monday = dt.date(2024, 1, 1)
        assert _add_working_days(monday, 5) == dt.date(2024, 1, 8)

    def test_zero_days(self):
        d = dt.date(2024, 3, 15)
        assert _add_working_days(d, 0) == d


class TestPAMetricScore:
    def test_not_breached(self):
        s = _score(PAMetric.MISSING_READS, 98.0)
        assert not s.is_breached
        assert s.severity == "PASS"

    def test_breached_low(self):
        s = _score(PAMetric.MISSING_READS, 96.0)
        assert s.is_breached
        assert s.severity == "LOW"

    def test_breached_medium(self):
        s = _score(PAMetric.MISSING_READS, 84.0)
        assert s.is_breached
        assert s.severity == "MEDIUM"

    def test_breached_high(self):
        s = _score(PAMetric.MISSING_READS, 40.0)
        assert s.is_breached
        assert s.severity == "HIGH"

    def test_at_threshold_not_breached(self):
        s = _score(PAMetric.LATE_DATA_FLOWS, 95.0)
        assert not s.is_breached

    def test_just_below_threshold_breached(self):
        s = _score(PAMetric.LATE_DATA_FLOWS, 94.9)
        assert s.is_breached



class TestPAAssessmentRecord:
    def _record(self, scores):
        reg = BSCPerformanceAssuranceRegister()
        return reg.record_assessment(
            PAAgentType.DATA_AGGREGATOR, "Test DA", 2024, 1, DATE, scores
        )

    def test_quarter_label(self):
        r = self._record(_all_pass())
        assert r.quarter_label == "Q1/2024"

    def test_tier_standard_zero_breaches(self):
        r = self._record(_all_pass())
        assert r.tier == PAAssessmentTier.STANDARD

    def test_tier_watch_one_breach(self):
        r = self._record(_one_breach())
        assert r.tier == PAAssessmentTier.WATCH

    def test_tier_watch_two_breaches(self):
        scores = list(_all_pass())
        scores[0] = _score(PAMetric.MISSING_READS, 90.0)
        scores[1] = _score(PAMetric.LATE_DATA_FLOWS, 80.0)
        r = self._record(tuple(scores))
        assert r.tier == PAAssessmentTier.WATCH

    def test_tier_formal_action_three_breaches(self):
        r = self._record(_three_breaches())
        assert r.tier == PAAssessmentTier.FORMAL_ACTION

    def test_rap_required_watch(self):
        r = self._record(_one_breach())
        assert r.rap_required is True

    def test_rap_not_required_standard(self):
        r = self._record(_all_pass())
        assert r.rap_required is False
        assert r.rap_due_date is None

    def test_rap_due_date_20wd(self):
        r = self._record(_one_breach())
        expected = _add_working_days(DATE, 20)
        assert r.rap_due_date == expected

    def test_rap_not_overdue_before_deadline(self):
        r = self._record(_one_breach())
        assert not r.is_rap_overdue(DATE)

    def test_rap_overdue_after_deadline(self):
        r = self._record(_one_breach())
        due = r.rap_due_date
        assert r.is_rap_overdue(due + dt.timedelta(days=1))

    def test_rap_not_overdue_when_closed(self):
        reg = BSCPerformanceAssuranceRegister()
        r = reg.record_assessment(PAAgentType.METER_OPERATOR, "MOP1", 2024, 1, DATE, _one_breach())
        reg.submit_assessment(r.assessment_id)
        reg.accept_assessment(r.assessment_id)
        reg.raise_rap(r.assessment_id)
        reg.close_rap(r.assessment_id)
        r2 = reg.assessments_for_agent("MOP1")[0]
        far_future = DATE + dt.timedelta(days=365)
        assert not r2.is_rap_overdue(far_future)

    def test_overall_pass_rate_all_pass(self):
        r = self._record(_all_pass())
        assert r.overall_pass_rate_pct == 100.0

    def test_overall_pass_rate_one_breach(self):
        r = self._record(_one_breach())
        assert r.overall_pass_rate_pct == round(100 * 5/6, 1)

    def test_assessment_summary_contains_key_info(self):
        r = self._record(_all_pass())
        s = r.assessment_summary
        assert "PA-" in s
        assert "Q1/2024" in s
        assert "STANDARD" in s



class TestRegisterMutations:
    def test_record_assigns_sequential_ids(self):
        reg = BSCPerformanceAssuranceRegister()
        r1 = reg.record_assessment(PAAgentType.SUPPLIER, "SUP", 2024, 1, DATE, _all_pass())
        r2 = reg.record_assessment(PAAgentType.SUPPLIER, "SUP", 2024, 2, DATE, _all_pass())
        assert r1.assessment_id == "PA-00001"
        assert r2.assessment_id == "PA-00002"

    def test_record_invalid_quarter_raises(self):
        reg = BSCPerformanceAssuranceRegister()
        with pytest.raises(ValueError):
            reg.record_assessment(PAAgentType.SUPPLIER, "SUP", 2024, 5, DATE, _all_pass())

    def test_submit_open_to_submitted(self):
        reg = BSCPerformanceAssuranceRegister()
        r = reg.record_assessment(PAAgentType.SUPPLIER, "SUP", 2024, 1, DATE, _all_pass())
        r2 = reg.submit_assessment(r.assessment_id)
        assert r2.status == PAStatus.SUBMITTED

    def test_submit_non_open_raises(self):
        reg = BSCPerformanceAssuranceRegister()
        r = reg.record_assessment(PAAgentType.SUPPLIER, "SUP", 2024, 1, DATE, _all_pass())
        reg.submit_assessment(r.assessment_id)
        with pytest.raises(ValueError):
            reg.submit_assessment(r.assessment_id)

    def test_accept_standard_goes_to_accepted(self):
        reg = BSCPerformanceAssuranceRegister()
        r = reg.record_assessment(PAAgentType.SUPPLIER, "SUP", 2024, 1, DATE, _all_pass())
        reg.submit_assessment(r.assessment_id)
        r2 = reg.accept_assessment(r.assessment_id)
        assert r2.status == PAStatus.ACCEPTED

    def test_accept_watch_goes_to_rap_required(self):
        reg = BSCPerformanceAssuranceRegister()
        r = reg.record_assessment(PAAgentType.DATA_AGGREGATOR, "DA", 2024, 1, DATE, _one_breach())
        reg.submit_assessment(r.assessment_id)
        r2 = reg.accept_assessment(r.assessment_id)
        assert r2.status == PAStatus.RAP_REQUIRED

    def test_accept_non_submitted_raises(self):
        reg = BSCPerformanceAssuranceRegister()
        r = reg.record_assessment(PAAgentType.SUPPLIER, "SUP", 2024, 1, DATE, _all_pass())
        with pytest.raises(ValueError):
            reg.accept_assessment(r.assessment_id)

    def test_raise_rap_rap_required_to_in_progress(self):
        reg = BSCPerformanceAssuranceRegister()
        r = reg.record_assessment(PAAgentType.DATA_COLLECTOR, "DC", 2024, 1, DATE, _one_breach())
        reg.submit_assessment(r.assessment_id)
        reg.accept_assessment(r.assessment_id)
        r2 = reg.raise_rap(r.assessment_id)
        assert r2.status == PAStatus.RAP_IN_PROGRESS

    def test_raise_rap_wrong_status_raises(self):
        reg = BSCPerformanceAssuranceRegister()
        r = reg.record_assessment(PAAgentType.SUPPLIER, "SUP", 2024, 1, DATE, _all_pass())
        with pytest.raises(ValueError):
            reg.raise_rap(r.assessment_id)

    def test_close_rap_in_progress_to_closed(self):
        reg = BSCPerformanceAssuranceRegister()
        r = reg.record_assessment(PAAgentType.METER_OPERATOR, "MOP", 2024, 1, DATE, _one_breach())
        reg.submit_assessment(r.assessment_id)
        reg.accept_assessment(r.assessment_id)
        reg.raise_rap(r.assessment_id)
        r2 = reg.close_rap(r.assessment_id)
        assert r2.status == PAStatus.RAP_CLOSED

    def test_close_rap_wrong_status_raises(self):
        reg = BSCPerformanceAssuranceRegister()
        r = reg.record_assessment(PAAgentType.SUPPLIER, "SUP", 2024, 1, DATE, _all_pass())
        with pytest.raises(ValueError):
            reg.close_rap(r.assessment_id)

    def test_get_missing_id_raises(self):
        reg = BSCPerformanceAssuranceRegister()
        with pytest.raises(KeyError):
            reg.submit_assessment("PA-99999")



class TestRegisterQueries:
    def _build(self):
        reg = BSCPerformanceAssuranceRegister()
        r1 = reg.record_assessment(PAAgentType.DATA_AGGREGATOR, "DA1", 2024, 1, DATE, _all_pass())
        reg.submit_assessment(r1.assessment_id)
        reg.accept_assessment(r1.assessment_id)
        r2 = reg.record_assessment(PAAgentType.DATA_AGGREGATOR, "DA1", 2024, 2, DATE, _one_breach())
        reg.submit_assessment(r2.assessment_id)
        reg.accept_assessment(r2.assessment_id)
        r3 = reg.record_assessment(PAAgentType.METER_OPERATOR, "MOP1", 2024, 1, DATE, _three_breaches())
        reg.submit_assessment(r3.assessment_id)
        reg.accept_assessment(r3.assessment_id)
        return reg, r1, r2, r3

    def test_assessments_for_agent(self):
        reg, r1, r2, _ = self._build()
        results = reg.assessments_for_agent("DA1")
        assert len(results) == 2

    def test_assessments_for_agent_empty(self):
        reg, *_ = self._build()
        assert reg.assessments_for_agent("UNKNOWN") == []

    def test_current_tier_latest_quarter(self):
        reg, r1, r2, _ = self._build()
        tier = reg.current_tier_for_agent("DA1", DATE)
        assert tier == PAAssessmentTier.WATCH

    def test_current_tier_none_for_unknown_agent(self):
        reg, *_ = self._build()
        assert reg.current_tier_for_agent("NOBODY", DATE) is None

    def test_agents_on_watch(self):
        reg, r1, r2, _ = self._build()
        assert "DA1" in reg.agents_on_watch

    def test_agents_on_formal_action(self):
        reg, r1, r2, r3 = self._build()
        assert "MOP1" in reg.agents_on_formal_action

    def test_agents_on_watch_excludes_closed_rap(self):
        reg = BSCPerformanceAssuranceRegister()
        r = reg.record_assessment(PAAgentType.SUPPLIER, "SUP", 2024, 1, DATE, _one_breach())
        reg.submit_assessment(r.assessment_id)
        reg.accept_assessment(r.assessment_id)
        reg.raise_rap(r.assessment_id)
        reg.close_rap(r.assessment_id)
        assert "SUP" not in reg.agents_on_watch

    def test_overdue_raps(self):
        reg = BSCPerformanceAssuranceRegister()
        r = reg.record_assessment(PAAgentType.DATA_COLLECTOR, "DC", 2024, 1, DATE, _one_breach())
        reg.submit_assessment(r.assessment_id)
        reg.accept_assessment(r.assessment_id)
        due = r.rap_due_date
        assert reg.overdue_raps(due) == []
        assert len(reg.overdue_raps(due + dt.timedelta(days=1))) == 1

    def test_overdue_raps_empty_when_no_raps(self):
        reg = BSCPerformanceAssuranceRegister()
        reg.record_assessment(PAAgentType.SUPPLIER, "SUP", 2024, 1, DATE, _all_pass())
        assert reg.overdue_raps(DATE + dt.timedelta(days=365)) == []

    def test_quarterly_summary(self):
        reg, r1, r2, r3 = self._build()
        s = reg.quarterly_summary(2024, 1)
        assert s["quarter_label"] == "Q1/2024"
        assert s["standard_count"] == 1
        assert s["formal_action_count"] == 1

    def test_quarterly_summary_empty_quarter(self):
        reg = BSCPerformanceAssuranceRegister()
        s = reg.quarterly_summary(2099, 1)
        assert s["total"] == 0

    def test_pa_register_summary_keys(self):
        reg, *_ = self._build()
        s = reg.pa_register_summary
        assert "total_assessments" in s
        assert "agents_on_watch" in s
        assert "agents_on_formal_action" in s

    def test_pa_register_summary_counts(self):
        reg, r1, r2, r3 = self._build()
        s = reg.pa_register_summary
        assert s["total_assessments"] == 3
        assert s["standard_count"] == 1
        assert s["watch_count"] == 1
        assert s["formal_action_count"] == 1

    def test_current_tier_ignores_open_assessments(self):
        reg = BSCPerformanceAssuranceRegister()
        reg.record_assessment(PAAgentType.SUPPLIER, "SUP", 2024, 1, DATE, _one_breach())
        assert reg.current_tier_for_agent("SUP", DATE) is None

    def test_metric_thresholds_all_six_present(self):
        assert len(_METRIC_THRESHOLDS) == 6
        for m in PAMetric:
            assert m in _METRIC_THRESHOLDS

