# Proposed Phase MW -- Income Stress -> Observed Payment Behaviour

**Drafted:** 2026-07-01T19:10:00Z
**4-hour opt-out window expires:** ~2026-07-01T23:10:00Z
**Replaces:** Phase MV proposal (Phase MV already complete)

## Summary

Wire the SIM income_stress state (added in Phase MV) to synthetic payment records
that the company can observe through PaymentBehaviourAnalytics. The canonical Human
Simulation Layer scenario now becomes possible: job_loss fires -> HIGH stress -> late
payment pattern -> company observes deteriorating payment behaviour and must respond.

## Why now

Phase MV added IncomeStress to every household and fires economic events. But
IncomeStress is currently inert -- no downstream effect on simulation output. Without
this wiring the SIM knows a customer is under stress but behaves identically to a
stress-free customer. Phase MW closes this gap.

The canonical scenario becomes testable end-to-end:
1. job_loss fires month 3 (SIM knows, company cannot read)
2. payment_timing.py generates LATE/DD_FAILED records months 4-6 (observable signal)
3. Company PaymentBehaviourAnalytics shows behaviour_score degrading EXCELLENT -> POOR
4. Company debt management responds correctly to observable signals

## Epistemic note

income_stress is SIM ground truth -- the company never reads it directly.
Payment records (due_date, payment_date, result) are observable to the company.
Correlation between stress and payment quality is indirect and noisy. Consistent with
SIM/company barrier.

## Files to create

simulation/payment_timing.py -- new SIM-side module:
  _PAYMENT_DELAY_DAYS: LOW (7,14) days; MODERATE (14,45); HIGH (30,90)
  _DD_FAILURE_PROBABILITY: LOW 0.03, MODERATE 0.12, HIGH 0.35
  generate_payment_record(customer_id, due_date, amount_gbp, income_stress, rng) -> dict
  stress_bad_debt_multiplier(income_stress) -> float: LOW 1.0 / MODERATE 1.5 / HIGH 3.0

## Files to modify

simulation/run_phase2b.py:
  At term close: look up income_stress_at_date(billing_account, term_end_str)
  Multiply get_bad_debt_rate() by stress_bad_debt_multiplier(income_stress)
  Emit payment record dict into run output payment_behaviour_records list

## Files to create (tests)

tests/sim/test_phase_mw_payment_timing.py -- 25 tests:
  LOW_stress_delay_in_7_14_window
  MODERATE_stress_delay_in_14_45_window
  HIGH_stress_delay_in_30_90_window
  LOW_dd_failure_rare (3% rate, seeded 100 -> <=10 failures)
  HIGH_dd_failure_common (35% rate, seeded 100 -> >=20 failures)
  generate_payment_record_fields_present
  dd_failed_has_no_payment_date
  on_time_has_payment_date_not_none
  late_payment_date_after_due_date
  stress_multiplier_LOW_is_1.0
  stress_multiplier_MODERATE_is_1.5
  stress_multiplier_HIGH_is_3.0
  stress_multiplier_None_is_1.0 (I&C/SME no household)
  high_stress_bad_debt_higher_than_low_stress
  payment_records_accumulate
  seeded_rng_deterministic
  income_stress_LOW_mostly_on_time (>=85pct)
  income_stress_HIGH_mostly_not_on_time (>=40pct LATE or worse)
  MODERATE_between_LOW_and_HIGH_on_time_rate
  payment_date_is_date_type
  amount_paid_zero_when_dd_failed
  amount_paid_equals_due_when_not_partial
  two_customers_independent
  sme_customer_None_multiplier
  resi_job_loss_shows_payment_deterioration (integration)

## Target

25 new tests, total ~14,485.

## Fidelity delta

IncomeStress now cascades into observable company-side signals. Financial stress leaves
a footprint in payment records the company can read, classify, and act on. The canonical
HSL scenario (job_loss -> payment slip -> company response) is now end-to-end testable.
Bad debt becomes customer-specific rather than segment-average for the first time.
