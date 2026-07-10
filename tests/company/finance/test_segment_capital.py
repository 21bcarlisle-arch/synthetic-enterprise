"""Tests for company/finance/segment_capital.py -- B2_OPEX_TAXONOMY_EXPANSION.md
segment capital-employed + ROCE discipline."""
import pytest

from company.finance.segment_capital import (
    SegmentROCEHistory,
    decision_artefacts_needed,
    segment_capital_employed_gbp,
    segment_roce_pct,
    segments_under_hurdle,
)


class TestSegmentCapitalEmployed:
    def test_combines_working_capital_and_allocated_exposure(self):
        result = segment_capital_employed_gbp(
            segment_working_capital_gbp={"resi": 1000.0, "sme": 500.0},
            segment_revenue_share={"resi": 0.7, "sme": 0.3},
            total_collateral_and_exposure_gbp=10000.0,
        )
        assert result["resi"] == pytest.approx(1000.0 + 7000.0)
        assert result["sme"] == pytest.approx(500.0 + 3000.0)

    def test_segment_present_in_only_one_input_defaults_other_to_zero(self):
        result = segment_capital_employed_gbp(
            segment_working_capital_gbp={"resi": 1000.0},
            segment_revenue_share={"resi": 0.5, "ic": 0.5},
            total_collateral_and_exposure_gbp=1000.0,
        )
        assert result["ic"] == pytest.approx(500.0)


class TestSegmentROCE:
    def test_basic_roce(self):
        result = segment_roce_pct({"resi": 100.0}, {"resi": 1000.0})
        assert result["resi"] == pytest.approx(10.0)

    def test_none_when_capital_employed_zero(self):
        result = segment_roce_pct({"resi": 100.0}, {"resi": 0.0})
        assert result["resi"] is None

    def test_none_when_capital_employed_negative(self):
        result = segment_roce_pct({"resi": 100.0}, {"resi": -50.0})
        assert result["resi"] is None

    def test_missing_profit_defaults_to_zero(self):
        result = segment_roce_pct({}, {"resi": 1000.0})
        assert result["resi"] == 0.0


class TestSegmentsUnderHurdle:
    def test_hurdle_not_set_returns_empty(self):
        result = segments_under_hurdle({"resi": 5.0}, hurdle_pct=None)
        assert result["hurdle_set"] is False
        assert result["under_hurdle"] == []

    def test_hurdle_set_flags_segments_below(self):
        result = segments_under_hurdle({"resi": 5.0, "sme": 15.0}, hurdle_pct=10.0)
        assert result["hurdle_set"] is True
        assert result["under_hurdle"] == ["resi"]

    def test_none_roce_not_flagged_as_under_hurdle(self):
        result = segments_under_hurdle({"resi": None}, hurdle_pct=10.0)
        assert result["under_hurdle"] == []


class TestSegmentROCEHistory:
    def test_consecutive_years_under_hurdle(self):
        history = SegmentROCEHistory()
        history.record("2023", {"resi": 5.0})
        history.record("2024", {"resi": 3.0})
        history.record("2025", {"resi": 4.0})
        streak = history.consecutive_years_under_hurdle(
            "resi", hurdle_pct=10.0, as_of_years=["2023", "2024", "2025"]
        )
        assert streak == 3

    def test_streak_breaks_on_recovery_year(self):
        history = SegmentROCEHistory()
        history.record("2023", {"resi": 5.0})
        history.record("2024", {"resi": 20.0})  # recovered above hurdle
        history.record("2025", {"resi": 3.0})
        streak = history.consecutive_years_under_hurdle(
            "resi", hurdle_pct=10.0, as_of_years=["2023", "2024", "2025"]
        )
        assert streak == 1  # only 2025 counts, streak broken by 2024

    def test_unmeasured_year_breaks_streak(self):
        history = SegmentROCEHistory()
        history.record("2024", {"resi": 3.0})
        # 2025 never recorded for this segment
        streak = history.consecutive_years_under_hurdle(
            "resi", hurdle_pct=10.0, as_of_years=["2024", "2025"]
        )
        assert streak == 0


class TestDecisionArtefacts:
    def test_no_artefacts_when_hurdle_not_set(self):
        history = SegmentROCEHistory()
        history.record("2024", {"resi": 3.0})
        history.record("2025", {"resi": 3.0})
        artefacts = decision_artefacts_needed(
            history, ["resi"], ["2024", "2025"], hurdle_pct=None
        )
        assert artefacts == []

    def test_artefact_created_for_persistent_under_hurdle(self):
        history = SegmentROCEHistory()
        history.record("2024", {"resi": 3.0})
        history.record("2025", {"resi": 4.0})
        artefacts = decision_artefacts_needed(
            history, ["resi"], ["2024", "2025"], hurdle_pct=10.0, min_consecutive_years=2
        )
        assert len(artefacts) == 1
        assert artefacts[0]["segment"] == "resi"
        assert artefacts[0]["years_below_hurdle"] == 2
        assert artefacts[0]["status"] == "AWAITING DIRECTOR/BOARD DECISION"

    def test_no_artefact_for_single_bad_year(self):
        history = SegmentROCEHistory()
        history.record("2024", {"resi": 20.0})
        history.record("2025", {"resi": 3.0})
        artefacts = decision_artefacts_needed(
            history, ["resi"], ["2024", "2025"], hurdle_pct=10.0, min_consecutive_years=2
        )
        assert artefacts == []

    def test_artefact_never_picks_the_decision_itself(self):
        history = SegmentROCEHistory()
        history.record("2024", {"resi": 1.0})
        history.record("2025", {"resi": 1.0})
        artefacts = decision_artefacts_needed(
            history, ["resi"], ["2024", "2025"], hurdle_pct=10.0
        )
        assert "reprice" in artefacts[0]["decision_needed"]
        assert "fix" in artefacts[0]["decision_needed"]
        assert "exit" in artefacts[0]["decision_needed"]
