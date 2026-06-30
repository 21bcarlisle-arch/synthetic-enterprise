"""Tests for Phase FW: Consumer Duty Annual Board Report Register."""
import datetime as dt
import pytest
from company.compliance.consumer_duty import DutyOutcome, OutcomeRAG
from company.compliance.consumer_duty_board_report import (
    DutyOutcomeSummary,
    ConsumerDutyAnnualReport,
    ConsumerDutyBoardRegister,
    _FIRST_REPORT_YEAR,
)

# ── helpers ──────────────────────────────────────────────────────────────────

def make_summary(
    outcome=DutyOutcome.PRICE_AND_VALUE,
    metric_name="satisfaction_pct",
    actual=85.0,
    target=80.0,
    prior=None,
    remediations=2,
    commitments=3,
):
    return DutyOutcomeSummary(
        outcome=outcome,
        key_metric_name=metric_name,
        key_metric_value=actual,
        target_value=target,
        prior_year_value=prior,
        remediation_count=remediations,
        forward_commitment_count=commitments,
    )


def four_outcomes(rags=None, actuals=None):
    """Build a full set of 4 DutyOutcomeSummary objects."""
    outcomes_list = list(DutyOutcome)
    actuals = actuals or [85.0, 85.0, 85.0, 85.0]
    result = []
    for i, outcome in enumerate(outcomes_list):
        result.append(make_summary(outcome=outcome, actual=actuals[i], target=80.0))
    return tuple(result)


# ── DutyOutcomeSummary ───────────────────────────────────────────────────────

class TestDutyOutcomeSummary:

    def test_rag_green_when_above_target(self):
        s = make_summary(actual=90.0, target=80.0)
        assert s.rag == OutcomeRAG.GREEN

    def test_rag_amber_within_10pct_below_target(self):
        # 80 * 0.90 = 72; actual=75 is >=72 -> AMBER
        s = make_summary(actual=75.0, target=80.0)
        assert s.rag == OutcomeRAG.AMBER

    def test_rag_red_when_well_below_target(self):
        # 80 * 0.90 = 72; actual=60 < 72 -> RED
        s = make_summary(actual=60.0, target=80.0)
        assert s.rag == OutcomeRAG.RED

    def test_is_improving_when_above_prior(self):
        s = make_summary(actual=85.0, prior=80.0)
        assert s.is_improving

    def test_is_improving_false_when_below_prior(self):
        s = make_summary(actual=75.0, prior=80.0)
        assert not s.is_improving

    def test_is_improving_true_when_no_prior(self):
        s = make_summary(actual=70.0, prior=None)
        assert s.is_improving

    def test_improvement_delta_with_prior(self):
        s = make_summary(actual=85.0, prior=80.0)
        assert abs(s.improvement_delta - 5.0) < 1e-9

    def test_improvement_delta_none_without_prior(self):
        s = make_summary(actual=85.0, prior=None)
        assert s.improvement_delta is None

    def test_outcome_summary_contains_key_fields(self):
        s = make_summary(outcome=DutyOutcome.PRICE_AND_VALUE)
        text = s.outcome_summary()
        assert "price_and_value" in text
        assert "85.0" in text

    def test_frozen(self):
        s = make_summary()
        with pytest.raises((AttributeError, TypeError)):
            s.key_metric_value = 99.0


# ── ConsumerDutyAnnualReport ─────────────────────────────────────────────────

class TestConsumerDutyAnnualReport:

    def test_report_deadline_is_31_jul_next_year(self):
        report = ConsumerDutyAnnualReport(year=2023, outcomes=four_outcomes())
        assert report.report_deadline == dt.date(2024, 7, 31)

    def test_overall_rag_red_when_any_outcome_red(self):
        outcomes = four_outcomes(actuals=[50.0, 85.0, 85.0, 85.0])  # first RED
        report = ConsumerDutyAnnualReport(year=2023, outcomes=outcomes)
        assert report.overall_rag == OutcomeRAG.RED

    def test_overall_rag_amber_when_any_amber_no_red(self):
        outcomes = four_outcomes(actuals=[75.0, 85.0, 85.0, 85.0])  # first AMBER
        report = ConsumerDutyAnnualReport(year=2023, outcomes=outcomes)
        assert report.overall_rag == OutcomeRAG.AMBER

    def test_overall_rag_green_when_all_green(self):
        report = ConsumerDutyAnnualReport(year=2023, outcomes=four_outcomes())
        assert report.overall_rag == OutcomeRAG.GREEN

    def test_red_outcomes_count(self):
        outcomes = four_outcomes(actuals=[50.0, 50.0, 85.0, 85.0])
        report = ConsumerDutyAnnualReport(year=2023, outcomes=outcomes)
        assert report.red_outcomes_count == 2

    def test_all_outcomes_improving_true(self):
        outcomes = tuple(make_summary(outcome=o, actual=85.0, prior=80.0) for o in DutyOutcome)
        report = ConsumerDutyAnnualReport(year=2024, outcomes=outcomes)
        assert report.all_outcomes_improving

    def test_all_outcomes_improving_false_when_one_declining(self):
        outcomes_list = [make_summary(outcome=o, actual=85.0, prior=80.0) for o in DutyOutcome]
        outcomes_list[0] = make_summary(outcome=list(DutyOutcome)[0], actual=75.0, prior=80.0)
        report = ConsumerDutyAnnualReport(year=2024, outcomes=tuple(outcomes_list))
        assert not report.all_outcomes_improving

    def test_total_remediations(self):
        outcomes = four_outcomes()  # each has remediation_count=2
        report = ConsumerDutyAnnualReport(year=2023, outcomes=outcomes)
        assert report.total_remediations == 8

    def test_get_outcome_found(self):
        report = ConsumerDutyAnnualReport(year=2023, outcomes=four_outcomes())
        o = report.get_outcome(DutyOutcome.PRICE_AND_VALUE)
        assert o is not None and o.outcome == DutyOutcome.PRICE_AND_VALUE

    def test_get_outcome_none_for_missing(self):
        # Pass only one outcome
        report = ConsumerDutyAnnualReport(
            year=2023, outcomes=(make_summary(outcome=DutyOutcome.PRODUCTS_AND_SERVICES),)
        )
        assert report.get_outcome(DutyOutcome.PRICE_AND_VALUE) is None

    def test_is_overdue_as_of_before_deadline(self):
        report = ConsumerDutyAnnualReport(year=2023, outcomes=four_outcomes())
        assert not report.is_overdue_as_of(dt.date(2024, 7, 31))

    def test_is_overdue_as_of_after_deadline_and_unapproved(self):
        report = ConsumerDutyAnnualReport(year=2023, outcomes=four_outcomes())
        assert report.is_overdue_as_of(dt.date(2024, 8, 1))

    def test_is_overdue_false_when_approved(self):
        report = ConsumerDutyAnnualReport(
            year=2023, outcomes=four_outcomes(),
            board_approved=True, approval_date=dt.date(2024, 7, 30)
        )
        assert not report.is_overdue_as_of(dt.date(2025, 1, 1))

    def test_report_summary_contains_year(self):
        report = ConsumerDutyAnnualReport(year=2023, outcomes=four_outcomes())
        assert "2023" in report.report_summary()


# ── ConsumerDutyBoardRegister ─────────────────────────────────────────────────

class TestConsumerDutyBoardRegister:

    def setup_method(self):
        self.reg = ConsumerDutyBoardRegister()

    def test_add_report_stored(self):
        r = self.reg.add_report(2023, four_outcomes())
        assert r.year == 2023

    def test_add_report_pre_first_year_raises(self):
        with pytest.raises(ValueError):
            self.reg.add_report(2022, four_outcomes())

    def test_approve_report(self):
        self.reg.add_report(2023, four_outcomes())
        r = self.reg.approve_report(2023, dt.date(2024, 7, 28))
        assert r.board_approved
        assert r.approval_date == dt.date(2024, 7, 28)

    def test_approve_report_missing_year_raises(self):
        with pytest.raises(KeyError):
            self.reg.approve_report(2023, dt.date(2024, 7, 1))

    def test_report_for_year(self):
        self.reg.add_report(2023, four_outcomes())
        assert self.reg.report_for_year(2023) is not None
        assert self.reg.report_for_year(2022) is None

    def test_unapproved_reports(self):
        self.reg.add_report(2023, four_outcomes())
        self.reg.add_report(2024, four_outcomes())
        self.reg.approve_report(2023, dt.date(2024, 7, 1))
        unapproved = self.reg.unapproved_reports()
        assert len(unapproved) == 1
        assert unapproved[0].year == 2024

    def test_overdue_reports(self):
        self.reg.add_report(2023, four_outcomes())  # deadline Jul 31 2024
        # Before deadline: no overdue
        assert len(self.reg.overdue_reports(dt.date(2024, 7, 31))) == 0
        # After deadline: 1 overdue
        assert len(self.reg.overdue_reports(dt.date(2024, 8, 1))) == 1

    def test_red_years(self):
        self.reg.add_report(2023, four_outcomes(actuals=[50.0, 85.0, 85.0, 85.0]))  # RED
        self.reg.add_report(2024, four_outcomes())  # GREEN
        assert self.reg.red_years() == [2023]

    def test_outcome_trend(self):
        self.reg.add_report(2023, four_outcomes(actuals=[80.0, 85.0, 90.0, 82.0]))
        self.reg.add_report(2024, four_outcomes(actuals=[83.0, 85.0, 90.0, 82.0]))
        trend = self.reg.outcome_trend(DutyOutcome.PRODUCTS_AND_SERVICES)
        assert trend == [(2023, 80.0), (2024, 83.0)]

    def test_all_years_approved_true(self):
        self.reg.add_report(2023, four_outcomes())
        self.reg.approve_report(2023, dt.date(2024, 7, 1))
        assert self.reg.all_years_approved()

    def test_all_years_approved_false(self):
        self.reg.add_report(2023, four_outcomes())
        assert not self.reg.all_years_approved()

    def test_board_register_summary(self):
        self.reg.add_report(2023, four_outcomes())
        self.reg.approve_report(2023, dt.date(2024, 7, 1))
        s = self.reg.board_register_summary(dt.date(2024, 8, 1))
        assert "1 annual reports" in s
        assert "1 approved" in s

    def test_empty_register_summary(self):
        s = self.reg.board_register_summary(dt.date(2024, 1, 1))
        assert "0 annual reports" in s

    def test_first_report_year_constant(self):
        assert _FIRST_REPORT_YEAR == 2023
