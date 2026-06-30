"""Phase BB: Risk Committee Decision Ledger tests."""
import pytest
from company.risk.risk_committee_ledger import (
    RiskCommitteeDecisionLedger, CommitteeSession, InterventionTrigger, InterventionOutcome,
)


def _session(date="2022-04-29", trigger=InterventionTrigger.VAR_THRESHOLD,
             treas=3_000_000.0, var_cur=55000.0, var_stress=20000.0,
             customers=None, summary="6 accounts max hedge", post_treas=None):
    return CommitteeSession(
        session_date=date, trigger=trigger,
        treasury_at_session_gbp=treas, portfolio_var_current_gbp=var_cur,
        portfolio_var_stressed_gbp=var_stress,
        customers_adjusted=customers or ["C_IC1", "C_IC2"],
        adjustment_summary=summary, post_session_treasury_gbp=post_treas,
    )


# 1. Record session
def test_record_session():
    ledger = RiskCommitteeDecisionLedger()
    s = ledger.record_session(_session())
    assert s in ledger._sessions


# 2. Sessions for year filter
def test_sessions_for_year():
    ledger = RiskCommitteeDecisionLedger()
    ledger.record_session(_session(date="2022-01-15"))
    ledger.record_session(_session(date="2023-03-10"))
    assert len(ledger.sessions_for_year(2022)) == 1
    assert len(ledger.sessions_for_year(2023)) == 1


# 3. VAR ratio computed correctly
def test_var_ratio():
    s = _session(var_cur=60000.0, var_stress=20000.0)
    assert abs(s.var_ratio - 3.0) < 0.001


# 4. Outcome PENDING when no post_session_treasury
def test_outcome_pending_without_post():
    s = _session(post_treas=None)
    assert s.outcome == InterventionOutcome.PENDING


# 5. Outcome EFFECTIVE when treasury rises >1000
def test_outcome_effective():
    s = _session(treas=3_000_000.0, post_treas=3_050_000.0)
    assert s.outcome == InterventionOutcome.EFFECTIVE


# 6. Outcome COUNTERPRODUCTIVE when treasury falls >1000
def test_outcome_counterproductive():
    s = _session(treas=3_000_000.0, post_treas=2_990_000.0)
    assert s.outcome == InterventionOutcome.COUNTERPRODUCTIVE


# 7. Outcome NEUTRAL for small delta
def test_outcome_neutral():
    s = _session(treas=3_000_000.0, post_treas=3_000_500.0)
    assert s.outcome == InterventionOutcome.NEUTRAL


# 8. treasury_delta_gbp
def test_treasury_delta():
    s = _session(treas=3_000_000.0, post_treas=3_050_000.0)
    assert abs(s.treasury_delta_gbp - 50000.0) < 0.01


# 9. effective_interventions filter
def test_effective_interventions():
    ledger = RiskCommitteeDecisionLedger()
    ledger.record_session(_session(treas=3_000_000.0, post_treas=3_050_000.0))  # effective
    ledger.record_session(_session(post_treas=None))  # pending
    assert len(ledger.effective_interventions()) == 1


# 10. intervention_effectiveness_rate None if all pending
def test_effectiveness_rate_none_if_pending():
    ledger = RiskCommitteeDecisionLedger()
    ledger.record_session(_session(post_treas=None))
    assert ledger.intervention_effectiveness_rate() is None


# 11. intervention_effectiveness_rate percentage
def test_effectiveness_rate_percentage():
    ledger = RiskCommitteeDecisionLedger()
    ledger.record_session(_session(treas=3e6, post_treas=3.05e6))  # effective
    ledger.record_session(_session(treas=3e6, post_treas=2.99e6))  # counterproductive
    # 1 effective out of 2 assessed = 50%
    assert ledger.intervention_effectiveness_rate() == 50.0


# 12. most_active_trigger
def test_most_active_trigger():
    ledger = RiskCommitteeDecisionLedger()
    ledger.record_session(_session(trigger=InterventionTrigger.VAR_THRESHOLD))
    ledger.record_session(_session(trigger=InterventionTrigger.VAR_THRESHOLD))
    ledger.record_session(_session(trigger=InterventionTrigger.PRICE_SPIKE))
    assert ledger.most_active_trigger() == InterventionTrigger.VAR_THRESHOLD


# 13. busiest_year
def test_busiest_year():
    ledger = RiskCommitteeDecisionLedger()
    ledger.record_session(_session(date="2022-01-01"))
    ledger.record_session(_session(date="2022-04-01"))
    ledger.record_session(_session(date="2023-01-01"))
    assert ledger.busiest_year() == 2022


# 14. peak_stressed_var
def test_peak_stressed_var():
    ledger = RiskCommitteeDecisionLedger()
    ledger.record_session(_session(var_stress=20000.0))
    ledger.record_session(_session(var_stress=80000.0))
    assert abs(ledger.peak_stressed_var_gbp() - 80000.0) < 0.01


# 15. governance_summary contains key metrics
def test_governance_summary():
    ledger = RiskCommitteeDecisionLedger()
    ledger.record_session(_session(date="2022-01-01"))
    summary = ledger.governance_summary()
    assert "1 sessions" in summary
    assert "2022" in summary
