"""Tests for simulation/acquisition_funnel.py -- PROCESS_NOT_EVENTS.md Section 5.

Uses a local duck-typed fake CreditBureauPort-shaped stub (per the integration note:
tools.credit_bureau_port / tools.credit_adapters are owned by a parallel agent; this
test file does not depend on their specific implementation, only the shape --
.check_credit(applicant_id, segment, seed) -> object with .passed / .score_band).
"""
from __future__ import annotations

from datetime import date

import pytest

import simulation.acquisition_funnel as af
from simulation.acquisition_funnel import (
    FUNNEL_STAGES,
    STAGE_COST_SHARE,
    run_acquisition_funnel,
)


class _FakeCreditResult:
    def __init__(self, passed, score_band="prime"):
        self.passed = passed
        self.score_band = score_band


class _FakeBureau:
    """Always returns the same configured result; records call count."""

    def __init__(self, passed=True, score_band="prime"):
        self.passed = passed
        self.score_band = score_band
        self.calls = 0

    def check_credit(self, applicant_id, segment, seed):
        self.calls += 1
        return _FakeCreditResult(self.passed, self.score_band)


class _ExplodingBureau:
    """Raises if called -- proves the funnel short-circuits before credit_check."""

    def check_credit(self, applicant_id, segment, seed):
        raise AssertionError("credit_bureau.check_credit() should not be called here")


class TestDeterminism:
    def test_same_seed_same_term_start_reproduces_result(self):
        bureau = _FakeBureau(passed=True)
        r1 = run_acquisition_funnel("resi", "seed-A", date(2019, 3, 1), bureau, total_amount_gbp=150.0)
        r2 = run_acquisition_funnel("resi", "seed-A", date(2019, 3, 1), bureau, total_amount_gbp=150.0)
        assert r1.won == r2.won
        assert r1.stage_reached == r2.stage_reached
        assert r1.total_cost_gbp == r2.total_cost_gbp
        assert [s.stage for s in r1.stages] == [s.stage for s in r2.stages]
        assert [s.passed for s in r1.stages] == [s.passed for s in r2.stages]

    def test_different_seed_can_diverge(self):
        bureau = _FakeBureau(passed=True)
        outcomes = {
            run_acquisition_funnel("resi", "seed-%d" % i, date(2019, 3, 1), bureau, total_amount_gbp=150.0).won
            for i in range(50)
        }
        assert outcomes == {True, False}


class TestStageReachedLogic:
    def test_fails_at_application_short_circuits_before_credit_check(self, monkeypatch):
        monkeypatch.setitem(af.QUOTE_TO_APPLICATION, "resi", 0.0)
        bureau = _ExplodingBureau()
        result = run_acquisition_funnel("resi", "seed-1", date(2019, 1, 1), bureau, total_amount_gbp=150.0)
        assert result.stage_reached == "application"
        assert result.won is False
        assert result.credit_bureau_passed is None
        assert result.credit_bureau_score_band is None
        assert [s.stage for s in result.stages] == ["quote", "application"]

    def test_fails_at_credit_check(self, monkeypatch):
        monkeypatch.setitem(af.QUOTE_TO_APPLICATION, "resi", 1.0)
        bureau = _FakeBureau(passed=False, score_band="decline")
        result = run_acquisition_funnel("resi", "seed-2", date(2019, 1, 1), bureau, total_amount_gbp=150.0)
        assert result.stage_reached == "credit_check"
        assert result.won is False
        assert result.credit_bureau_passed is False
        assert result.credit_bureau_score_band == "decline"
        assert [s.stage for s in result.stages] == ["quote", "application", "credit_check"]

    def test_fails_at_onboarding(self, monkeypatch):
        monkeypatch.setitem(af.QUOTE_TO_APPLICATION, "resi", 1.0)
        monkeypatch.setitem(af.CREDIT_CHECK_TO_ONBOARDING, "resi", 0.0)
        bureau = _FakeBureau(passed=True, score_band="prime")
        result = run_acquisition_funnel("resi", "seed-3", date(2019, 1, 1), bureau, total_amount_gbp=150.0)
        assert result.stage_reached == "onboarding"
        assert result.won is False
        assert result.credit_bureau_passed is True
        assert [s.stage for s in result.stages] == ["quote", "application", "credit_check", "onboarding"]

    def test_survives_all_stages_wins(self, monkeypatch):
        monkeypatch.setitem(af.QUOTE_TO_APPLICATION, "resi", 1.0)
        monkeypatch.setitem(af.CREDIT_CHECK_TO_ONBOARDING, "resi", 1.0)
        monkeypatch.setitem(af.ONBOARDING_TO_COOLING_OFF_SURVIVAL["resi"], "pre", 1.0)
        monkeypatch.setitem(af.ONBOARDING_TO_COOLING_OFF_SURVIVAL["resi"], "post", 1.0)
        bureau = _FakeBureau(passed=True, score_band="prime")
        result = run_acquisition_funnel("resi", "seed-4", date(2019, 1, 1), bureau, total_amount_gbp=150.0)
        assert result.stage_reached == "cooling_off"
        assert result.won is True
        assert [s.stage for s in result.stages] == list(FUNNEL_STAGES)
        assert all(s.passed for s in result.stages)


class TestCostAccumulation:
    def test_full_win_cost_equals_total_amount(self, monkeypatch):
        monkeypatch.setitem(af.QUOTE_TO_APPLICATION, "resi", 1.0)
        monkeypatch.setitem(af.CREDIT_CHECK_TO_ONBOARDING, "resi", 1.0)
        monkeypatch.setitem(af.ONBOARDING_TO_COOLING_OFF_SURVIVAL["resi"], "pre", 1.0)
        monkeypatch.setitem(af.ONBOARDING_TO_COOLING_OFF_SURVIVAL["resi"], "post", 1.0)
        bureau = _FakeBureau(passed=True)
        result = run_acquisition_funnel("resi", "seed-5", date(2019, 1, 1), bureau, total_amount_gbp=150.0)
        assert result.won is True
        assert result.total_cost_gbp == pytest.approx(150.0, abs=0.01)

    def test_partial_fail_cost_matches_stage_share_sum(self, monkeypatch):
        # Fails AT credit_check (bureau declines) -- cost booked through credit_check
        # inclusive (reaching a stage books its cost, per module docstring), NOT onboarding.
        monkeypatch.setitem(af.QUOTE_TO_APPLICATION, "resi", 1.0)
        bureau = _FakeBureau(passed=False)
        result = run_acquisition_funnel("resi", "seed-6", date(2019, 1, 1), bureau, total_amount_gbp=400.0)
        assert result.stage_reached == "credit_check"
        expected = 400.0 * (
            STAGE_COST_SHARE["quote"] + STAGE_COST_SHARE["application"] + STAGE_COST_SHARE["credit_check"]
        )
        assert result.total_cost_gbp == pytest.approx(expected, abs=0.01)

    def test_reaching_but_failing_onboarding_books_onboarding_share_too(self, monkeypatch):
        # Reaching onboarding (even though it then fails there) books quote+application+
        # credit_check+onboarding shares -- "as the prospect reaches, not necessarily
        # passes, each stage" per module docstring.
        monkeypatch.setitem(af.QUOTE_TO_APPLICATION, "resi", 1.0)
        monkeypatch.setitem(af.CREDIT_CHECK_TO_ONBOARDING, "resi", 0.0)
        bureau = _FakeBureau(passed=True)
        result = run_acquisition_funnel("resi", "seed-6b", date(2019, 1, 1), bureau, total_amount_gbp=400.0)
        assert result.stage_reached == "onboarding"
        expected = 400.0 * (
            STAGE_COST_SHARE["quote"] + STAGE_COST_SHARE["application"]
            + STAGE_COST_SHARE["credit_check"] + STAGE_COST_SHARE["onboarding"]
        )
        assert result.total_cost_gbp == pytest.approx(expected, abs=0.01)

    def test_each_stage_event_cost_increment_matches_share(self, monkeypatch):
        monkeypatch.setitem(af.QUOTE_TO_APPLICATION, "resi", 0.0)
        bureau = _ExplodingBureau()
        result = run_acquisition_funnel("resi", "seed-7", date(2019, 1, 1), bureau, total_amount_gbp=200.0)
        by_stage = {s.stage: s.cost_increment_gbp for s in result.stages}
        assert by_stage["quote"] == pytest.approx(200.0 * STAGE_COST_SHARE["quote"], abs=0.01)
        assert by_stage["application"] == pytest.approx(200.0 * STAGE_COST_SHARE["application"], abs=0.01)

    def test_failed_attempt_costs_less_than_won_attempt(self, monkeypatch):
        monkeypatch.setitem(af.QUOTE_TO_APPLICATION, "resi", 0.0)
        failed = run_acquisition_funnel("resi", "seed-8", date(2019, 1, 1), _ExplodingBureau(), total_amount_gbp=150.0)
        assert failed.total_cost_gbp < 150.0


class TestCoolingOffRegime:
    def test_resi_post_reform_survival_exceeds_pre_reform(self, monkeypatch):
        monkeypatch.setitem(af.QUOTE_TO_APPLICATION, "resi", 1.0)
        monkeypatch.setitem(af.CREDIT_CHECK_TO_ONBOARDING, "resi", 1.0)
        bureau = _FakeBureau(passed=True)
        n = 500
        pre_wins = sum(
            run_acquisition_funnel(
                "resi", "pre-%d" % i, date(2022, 6, 1), bureau, total_amount_gbp=150.0
            ).won
            for i in range(n)
        )
        post_wins = sum(
            run_acquisition_funnel(
                "resi", "post-%d" % i, date(2022, 8, 1), bureau, total_amount_gbp=150.0
            ).won
            for i in range(n)
        )
        pre_rate = pre_wins / n
        post_rate = post_wins / n
        assert post_rate > pre_rate + 0.05, (
            "expected post-REC survival to exceed pre-REC by >5pp; pre=%s, post=%s" % (pre_rate, post_rate)
        )

    def test_boundary_date_is_post_regime(self):
        assert af._cooling_off_survival_rate("resi", date(2022, 7, 1)) == af.ONBOARDING_TO_COOLING_OFF_SURVIVAL["resi"]["post"]
        assert af._cooling_off_survival_rate("resi", date(2022, 6, 30)) == af.ONBOARDING_TO_COOLING_OFF_SURVIVAL["resi"]["pre"]

    def test_sme_regime_kept_flat(self):
        assert (
            af.ONBOARDING_TO_COOLING_OFF_SURVIVAL["SME"]["pre"]
            == af.ONBOARDING_TO_COOLING_OFF_SURVIVAL["SME"]["post"]
        )
        assert af._cooling_off_survival_rate("SME", date(2022, 6, 1)) == af._cooling_off_survival_rate(
            "SME", date(2022, 8, 1)
        )


class TestAcquisitionFunnelPopulationCheck:
    def _make_log(self, segment, year, n_attempts, n_wins):
        entries = []
        for i in range(n_attempts):
            entries.append({
                "segment": segment,
                "term_start": "%d-0%d-01" % (year, (i % 9) + 1),
                "won": i < n_wins,
            })
        return entries

    def test_green_within_benchmark_range(self):
        from tools.population_anchor import _acquisition_funnel_check
        log = self._make_log("resi", 2019, 15, 3)
        result = _acquisition_funnel_check(log)
        assert len(result) == 1
        assert result[0]["rag"] == "GREEN"
        assert result[0]["win_rate_pct"] == 20.0

    def test_amber_within_five_points_of_range(self):
        from tools.population_anchor import _acquisition_funnel_check
        log = self._make_log("resi", 2019, 25, 6)
        result = _acquisition_funnel_check(log)
        assert result[0]["win_rate_pct"] == 24.0
        assert result[0]["rag"] == "AMBER"

    def test_red_far_outside_range(self):
        from tools.population_anchor import _acquisition_funnel_check
        log = self._make_log("resi", 2019, 100, 2)
        result = _acquisition_funnel_check(log)
        assert result[0]["win_rate_pct"] == 2.0
        assert result[0]["rag"] == "RED"

    def test_empty_log_returns_empty_findings(self):
        from tools.population_anchor import _acquisition_funnel_check
        assert _acquisition_funnel_check([]) == []
        assert _acquisition_funnel_check(None) == []

    def test_segments_reported_separately(self):
        from tools.population_anchor import _acquisition_funnel_check
        log = self._make_log("resi", 2020, 20, 4) + self._make_log("SME", 2020, 20, 4)
        result = _acquisition_funnel_check(log)
        segments = {r["segment"] for r in result}
        assert segments == {"resi", "SME"}

    def test_years_reported_separately(self):
        from tools.population_anchor import _acquisition_funnel_check
        log = self._make_log("resi", 2019, 20, 4) + self._make_log("resi", 2020, 20, 4)
        result = _acquisition_funnel_check(log)
        years = {r["year"] for r in result}
        assert years == {2019, 2020}


def test_stage_cost_share_sums_to_one():
    assert abs(sum(STAGE_COST_SHARE.values()) - 1.0) < 1e-9


def test_funnel_stages_order():
    assert FUNNEL_STAGES == ("quote", "application", "credit_check", "onboarding", "cooling_off")


class TestStageCalendarSpacing:
    """Phase 3 item 5 (CORE_FIDELITY_PHASES.md): stage-to-stage calendar-day
    spacing -- previously all 5 stages resolved instantly against a single
    term_start."""

    def test_quote_stage_date_equals_term_start(self):
        result = run_acquisition_funnel(
            "resi", "seedA", date(2020, 1, 1), _FakeBureau(passed=True),
        )
        assert result.stages[0].stage == "quote"
        assert result.stages[0].stage_date == "2020-01-01"

    def test_stage_dates_strictly_non_decreasing(self):
        result = run_acquisition_funnel(
            "resi", "seedB", date(2020, 1, 1), _FakeBureau(passed=True),
        )
        dates = [date.fromisoformat(s.stage_date) for s in result.stages]
        assert dates == sorted(dates)

    def test_cooling_off_stage_is_exactly_14_days_after_onboarding(self):
        # Find a seed that survives to cooling_off (application/onboarding
        # are probabilistic) rather than assuming any single seed does.
        for i in range(50):
            result = run_acquisition_funnel(
                "resi", f"coolseed{i}", date(2020, 1, 1), _FakeBureau(passed=True),
            )
            if result.stage_reached == "cooling_off":
                by_stage = {s.stage: date.fromisoformat(s.stage_date) for s in result.stages}
                assert (by_stage["cooling_off"] - by_stage["onboarding"]).days == af.COOLING_OFF_PERIOD_DAYS
                return
        pytest.fail("no seed reached cooling_off in 50 tries")

    def test_stage_date_deterministic_for_same_seed(self):
        r1 = run_acquisition_funnel("resi", "seedD", date(2021, 6, 1), _FakeBureau(passed=True))
        r2 = run_acquisition_funnel("resi", "seedD", date(2021, 6, 1), _FakeBureau(passed=True))
        assert [s.stage_date for s in r1.stages] == [s.stage_date for s in r2.stages]

    def test_stage_dates_vary_across_seeds(self):
        application_dates = {
            run_acquisition_funnel(
                "resi", f"seed{i}", date(2020, 1, 1), _FakeBureau(passed=True)
            ).stages[1].stage_date
            for i in range(20)
        }
        assert len(application_dates) > 1

    def test_early_dropout_still_carries_stage_dates(self):
        result = run_acquisition_funnel(
            "resi", "seedE", date(2020, 1, 1), _FakeBureau(passed=False),
        )
        assert result.stage_reached == "credit_check"
        assert len(result.stages) == 3
        for stage_event in result.stages:
            date.fromisoformat(stage_event.stage_date)  # doesn't raise
