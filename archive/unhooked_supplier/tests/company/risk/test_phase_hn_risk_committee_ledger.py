"""Tests for Phase HN: Risk Committee Decision Ledger."""
import pytest
from company.risk.risk_committee_ledger import (
    CommitteeSession,
    InterventionOutcome,
    InterventionTrigger,
    RiskCommitteeDecisionLedger,
)


def _session(date="2024-03-15", trigger=InterventionTrigger.VAR_THRESHOLD,
             tsy=500000, var_curr=80000, var_str=100000, post_tsy=None):
    return CommitteeSession(
        session_date=date, trigger=trigger,
        treasury_at_session_gbp=tsy,
        portfolio_var_current_gbp=var_curr,
        portfolio_var_stressed_gbp=var_str,
        customers_adjusted=["C1", "C2"],
        adjustment_summary="2 accounts adjusted",
        post_session_treasury_gbp=post_tsy,
    )


class TestCommitteeSession:
    def test_var_ratio(self):
        s = _session(var_curr=80000, var_str=100000)
        assert s.var_ratio == pytest.approx(0.8)

    def test_var_ratio_zero_stressed(self):
        s = _session(var_str=0)
        assert s.var_ratio is None

    def test_outcome_pending_no_post_treasury(self):
        s = _session(post_tsy=None)
        assert s.outcome == InterventionOutcome.PENDING

    def test_outcome_effective(self):
        s = _session(tsy=500000, post_tsy=505000)
        assert s.outcome == InterventionOutcome.EFFECTIVE

    def test_outcome_neutral(self):
        s = _session(tsy=500000, post_tsy=500500)
        assert s.outcome == InterventionOutcome.NEUTRAL

    def test_outcome_counterproductive(self):
        s = _session(tsy=500000, post_tsy=498000)
        assert s.outcome == InterventionOutcome.COUNTERPRODUCTIVE

    def test_treasury_delta_positive(self):
        s = _session(tsy=500000, post_tsy=503000)
        assert s.treasury_delta_gbp == pytest.approx(3000)

    def test_treasury_delta_none_when_pending(self):
        s = _session(post_tsy=None)
        assert s.treasury_delta_gbp is None


class TestRiskCommitteeDecisionLedger:
    def _build(self):
        led = RiskCommitteeDecisionLedger()
        led.record_session(_session("2022-06-01", InterventionTrigger.PRICE_SPIKE, post_tsy=480000))
        led.record_session(_session("2022-09-01", InterventionTrigger.TREASURY_STRESS, tsy=470000, post_tsy=475000))
        led.record_session(_session("2023-03-01", InterventionTrigger.VAR_THRESHOLD, post_tsy=520000))
        led.record_session(_session("2024-01-01", InterventionTrigger.SCHEDULED_REVIEW, post_tsy=None))
        return led

    def test_sessions_for_year(self):
        led = self._build()
        assert len(led.sessions_for_year(2022)) == 2

    def test_sessions_for_year_empty(self):
        led = self._build()
        assert led.sessions_for_year(2099) == []

    def test_sessions_by_trigger(self):
        led = self._build()
        assert len(led.sessions_by_trigger(InterventionTrigger.VAR_THRESHOLD)) == 1

    def test_effective_interventions(self):
        led = self._build()
        effs = led.effective_interventions()
        assert len(effs) > 0
        assert all(s.outcome == InterventionOutcome.EFFECTIVE for s in effs)

    def test_counterproductive_interventions(self):
        led = self._build()
        count = led.counterproductive_interventions()
        assert any(s.trigger == InterventionTrigger.PRICE_SPIKE for s in count)

    def test_effectiveness_rate(self):
        led = self._build()
        rate = led.intervention_effectiveness_rate()
        assert rate is not None
        assert 0 <= rate <= 100

    def test_effectiveness_rate_none_all_pending(self):
        led = RiskCommitteeDecisionLedger()
        led.record_session(_session(post_tsy=None))
        assert led.intervention_effectiveness_rate() is None

    def test_most_active_trigger(self):
        led = self._build()
        trigger = led.most_active_trigger()
        assert trigger is not None
        assert isinstance(trigger, InterventionTrigger)

    def test_most_active_trigger_empty(self):
        led = RiskCommitteeDecisionLedger()
        assert led.most_active_trigger() is None

    def test_busiest_year(self):
        led = self._build()
        assert led.busiest_year() == 2022

    def test_busiest_year_empty(self):
        led = RiskCommitteeDecisionLedger()
        assert led.busiest_year() is None

    def test_peak_stressed_var(self):
        led = self._build()
        assert led.peak_stressed_var_gbp() == 100000

    def test_peak_stressed_var_empty(self):
        led = RiskCommitteeDecisionLedger()
        assert led.peak_stressed_var_gbp() == 0.0

    def test_governance_summary_not_empty(self):
        led = self._build()
        s = led.governance_summary()
        assert "Risk Committee" in s
        assert "sessions" in s

    def test_governance_summary_empty(self):
        led = RiskCommitteeDecisionLedger()
        assert "No risk committee" in led.governance_summary()

