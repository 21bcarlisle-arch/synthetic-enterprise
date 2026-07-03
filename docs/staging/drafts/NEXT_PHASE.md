# NEXT PHASE PROPOSAL: Phase NO — Counterfactual Retention & Threshold Optimisation

## Problem

Phase NJ exposed that the churn model has **0% recall**: all 6 no-offer churns had company
estimates < 30% threshold. The worst: C3, C4, C5 all at 0.0%. The company spent 12
retention offers on customers who renewed anyway (100% FP rate). Phase NK added the board
report section, but it reports the problem — it doesn't fix it.

Root cause breakdown (from last run):
- C3 (Jun 2020): estimate=0%, margin=£585 — stable rates, no shocks, base-rate churn
- C1 (Dec 2021): estimate=3.8%, margin=-£178 — crisis period, company below-threshold
- C2 (Mar 2022): estimate=6.7%, margin=£237 — crisis, below-threshold
- C5 (Dec 2022): estimate=0%, margin=£1,775 — post-crisis, base-rate churn
- C6 (Mar 2024): estimate=24.7%, margin=£2,860 — closest to threshold, missed by 5 pts
- C4 (Sep 2024): estimate=0%, margin=£469 — stable, base-rate churn

## What this phase builds

### Part A: Counterfactual Retention Report (company/analytics/counterfactual_retention.py)
For each no-offer churn, compute:
- `counterfactual_retained`: would the retention modifier (if applied) have prevented churn?
  → Uses the SIM roll + retention_modifier to answer deterministically.
- `value_recovered_gbp`: expected_term_margin if retained.
- `retention_cost_gbp`: cost of making the offer (£50 resi, £200 I&C).
- `net_value_of_offer_gbp`: value_recovered - retention_cost.
- `was_worth_offering`: net_value > 0.

Returns a `CounterfactualRetentionReport` with per-miss detail and aggregate stats.

### Part B: Threshold Sensitivity Analysis (company/analytics/threshold_sensitivity.py)
Compute recall/precision/F1 at each threshold from 0% to 50% (in 5% steps), using the
historical customer_events and retention_log from run output. Return the optimal threshold
(max F1) and the "max recall" threshold (lowest that catches all high-value misses).

### Part C: Board report section (_section_counterfactual_retention)
Add to saas/reporting/annual_report.py:
- "Missed retention opportunities": per-year count + total value at stake.
- "Optimal threshold": current vs. recommended.
- "Sensitivity curve": recall/precision/F1 at each threshold level.
- RAG: RED if >2 high-value misses/year, AMBER if 1-2, GREEN if 0.

### Part D: Threshold update
Update RETENTION_THRESHOLD in company/crm/enriched_churn_estimate.py from 0.30 to the
F1-optimal value computed in Part B. Re-run epistemic verifier.

## Why this closes a real gap
- All 5 hollow gaps: already closed.
- Gap 4 (churn blind miss rate) was "CLOSED" structurally but the recall metric shows 0%.
- This phase makes the churn model self-calibrating: it uses its own performance data
  to adjust the threshold, closing the feedback loop.
- Strategic value: board can see exactly how much revenue was left on the table and
  what threshold change recovers it.

## Files to create / modify
- company/analytics/counterfactual_retention.py (new)
- company/analytics/threshold_sensitivity.py (new)
- saas/reporting/annual_report.py (add _section_counterfactual_retention)
- company/crm/enriched_churn_estimate.py (update RETENTION_THRESHOLD)
- tests/company/test_phase_no_counterfactual_retention.py (new, ~16 tests)

## Test targets (~16 tests)
- counterfactual_retained=True when roll < threshold * (1 - retention_modifier)
- counterfactual_retained=False when roll is very high (even with modifier)
- value_recovered correct given expected_term_margin
- net_value computation
- was_worth_offering False when margin negative
- threshold_sensitivity returns dict with keys 0 to 50
- optimal_threshold maximises F1
- report section present in annual report dict
- RAG = RED with 3 misses
- RAG = GREEN with 0 misses
- threshold update reflected in RETENTION_THRESHOLD
- epistemic: no SIM internal reads
