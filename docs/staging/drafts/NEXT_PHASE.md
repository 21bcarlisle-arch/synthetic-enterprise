# Phase NH -- Payment Behaviour Score Wired into Company Churn Estimate

## Gap
behaviour_score is always None in every call to enriched_churn_estimate() in
simulation/run_phase2b.py. The three-signal churn model (bill_shock + behaviour + satisfaction)
is only two-signal in practice.

Root cause: PaymentBehaviourAnalytics (Phase MX) was never instantiated in the sim runner.
generate_payment_record() from simulation/payment_timing.py is never called -- only
stress_bad_debt_multiplier is imported (line 85). The company never builds payment history
so _enriched_churn_estimate always receives behaviour_score=None.

Impact: A HIGH-stress customer accumulating DD_FAILED records gets combined_churn_probability
= 0.05 (base) + 0.20 (CRITICAL) = 0.25; with 1 bill shock (+0.05) and low satisfaction (+0.10)
this reaches 0.40, above the 0.30 RETENTION_THRESHOLD. Currently silenced at 0.20.

## What to build

simulation/run_phase2b.py (modify only -- no new files)

New imports:
  from simulation.payment_timing import generate_payment_record
  from company.crm.payment_behaviour_analytics import PaymentBehaviourAnalytics

Instantiation near _company_sat_acc:
  _payment_analytics = PaymentBehaviourAnalytics()
  _payment_rng = random.Random(42 + 7919)
  _payment_month_seen: set[tuple[str, str]] = set()  # (cid, YYYY-MM)

In settlement record loop (after _income_stress, before bad-debt):
  _pm_key = (cid, rec['settlement_date'][:7])
  if _pm_key not in _payment_month_seen:
      _payment_month_seen.add(_pm_key)
      _pm_due = date.fromisoformat(rec['settlement_date'][:7] + '-28')
      _pm_rec = generate_payment_record(cid, _pm_due, rec.get('revenue_gbp', 0.0), _income_stress, _payment_rng)
      _payment_analytics.record_payment(cid, _pm_rec)

At renewal (after _nd_shock_count):
  _nh_behaviour_score = _payment_analytics.get_score(cid)
  # pass behaviour_score=_nh_behaviour_score to _enriched_churn_estimate

## Test plan (16 tests in tests/test_nh_payment_behaviour_wiring.py)

1.  generate_payment_record LOW stress: ON_TIME probability >= 0.90
2.  generate_payment_record HIGH stress: DD_FAILED probability >= 0.30
3.  Analytics all ON_TIME: get_score() == EXCELLENT
4.  Analytics majority DD_FAILED: get_score() == CRITICAL
5.  enriched_churn CRITICAL > enriched_churn None (same other params)
6.  enriched_churn EXCELLENT: no uplift vs behaviour=None baseline
7.  CRITICAL + 1 bill shock + low satisfaction >= 0.30 (crosses RETENTION_THRESHOLD)
8.  POOR score pushes combined above rate-only when rate change is modest
9.  Epistemic: analytics record uses 'result' key (observable), not income_stress directly
10. Multiple customers: independent records; no cross-contamination
11. Monthly accumulation: 12 records after 12 months of a term
12. Score persists across terms: CRITICAL from year 1 still visible at year 3 renewal
13. New customer (no records): get_score() returns None (backward-compatible)
14. at_risk_customers() includes POOR and CRITICAL, excludes FAIR/GOOD/EXCELLENT
15. score_trend() DETERIORATING when second half of window scores worse than first
16. run_phase2b wiring: _enriched_churn_estimate call passes behaviour_score kwarg

## Expected simulation impact

HIGH-stress residential customers (job_loss -> IncomeStress.HIGH) who accumulate 3+
DD_FAILED records reach CRITICAL score. At their next renewal, enriched churn estimate
rises by up to +0.20, crossing RETENTION_THRESHOLD and triggering proactive retention.
LOW-stress and I&C customers unaffected.

## Epistemic check

PASS. Company observes payment outcomes (ON_TIME/LATE/DD_FAILED), not income_stress.
generate_payment_record() uses income_stress to produce the observable record;
the company only reads the output dict. SIM/company barrier preserved.

## Fidelity delta

Company runs a genuine three-signal churn model at every renewal. Phases MX-NF built all
components; Phase NH closes the final wiring gap so the causal chain
income_stress -> DD_FAILED -> BehaviourScore -> enriched churn estimate is live,
not just connected on paper.
