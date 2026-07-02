Proposed Phase MY -- Payment Behaviour Score into Company Churn Model

Drafted: 2026-07-02T00:30:00Z
Depends on: Phase MX complete
Closes: Gap 4 (Churn Blind Miss Rate) -- Board Risk RED item

Summary

Wire BehaviourScore (built in Phase MX) into the company churn model.
Currently company churn uses only bill shocks (saas/churn_model.py: 5% + 3%/shock).
Payment behaviour is a leading churn indicator that bill shocks miss entirely.

Why now

Gap 4 (Board Risk RED: 4/6 churns not forecast) needs BOTH signals:
  1. Bill shock (existing): customer experienced price pain in trailing 12m
  2. Payment behaviour (MX): customer is struggling to pay -- about to default or leave

What exists (do not re-implement)

- saas/churn_model.py: churn_probability(bill_shock_count) -> float
- company/crm/churn_model.py: company-facing churn model
- After Phase MX: company/crm/payment_behaviour_analytics.py with BehaviourScore enum

Files to create

company/crm/payment_churn_model.py:
  CHURN_UPLIFT_BY_SCORE dict: EXCELLENT=-0.02, GOOD=0.00, FAIR=+0.03, POOR=+0.10, CRITICAL=+0.20
  combined_churn_probability(bill_shock_count, behaviour_score) -> float
    base = churn_probability(bill_shock_count)
    uplift = CHURN_UPLIFT_BY_SCORE.get(behaviour_score, 0.0)
    return min(base + uplift, MAX_CHURN_PROBABILITY)

Tests to create

tests/company/test_phase_my_payment_churn_model.py -- 20 tests:
  base_only_no_score, excellent_suppresses_churn, good_neutral_uplift
  fair_adds_moderate_uplift, poor_adds_significant_uplift, critical_adds_high_uplift
  none_score_equals_base, bill_shocks_still_apply, bill_shocks_plus_poor_stacks
  bill_shocks_plus_critical_stacks, bill_shocks_plus_excellent_reduces, total_capped_at_095
  zero_shocks_excellent_is_low, zero_shocks_critical_is_high
  high_shocks_excellent_still_lower_than_high_shocks_critical
  score_uplift_table_complete, ordering_excellent_lt_good_lt_fair_lt_poor_lt_critical
  integration_payment_analytics_into_combined_probability
  epistemic_combined_uses_observables_only, combined_probability_is_float_in_range

Target: 20 new tests, total ~14,530.

Fidelity delta

Company churn predictions now use TWO observable signals: bill shock (price pain) +
payment behaviour (financial distress). Board Risk RED Churn blind miss rate starts to
close: POOR/CRITICAL scores flag customers likely to default OR churn, enabling retention
intervention before renewal rather than after departure.

Epistemic note

combined_churn_probability takes only: bill_shock_count (observable, billing records) and
BehaviourScore (observable, payment records from Phase MX). No SIM internals accessed.
