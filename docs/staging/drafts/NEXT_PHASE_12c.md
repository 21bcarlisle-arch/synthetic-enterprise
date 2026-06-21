# Phase 12c: Retention ROI Analysis + Churn Basis Risk P&L Consequence

## What this phase does

**Measure whether the company's retention strategy is net-positive.**

In Phase 12b, the company makes retention offers when its churn estimate > 30%. The outcome is recorded ("retained" or "churned_despite_offer"). Phase 12c answers: is this strategy profitable?

The company's churn estimate is known to be imperfect (Phase 11b: systematically under-estimates during price spikes, over-estimates during stable periods). This creates two failure modes:
1. **False negatives**: company under-estimates churn → no offer made → customer churns (missed retention opportunity)
2. **False positives**: company over-estimates churn → offer made → customer would have renewed anyway (unnecessary discount cost)

## Mechanism

1. Compute per-renewal retention ROI:
   - If retained: saved margin = (full-rate term margin) vs (what we got = discounted rate margin)
     Net benefit = saved churn loss - discount cost
   - If churned despite offer: net loss = discount cost (0 benefit)
   - If no offer made (estimate < threshold): counterfactual — would retention have saved them?

2. Add "Retention ROI" section to annual report:
   - Total offers made / success rate / total cost
   - Net P&L from retention strategy (sum of: saved margins - discount costs)
   - Year-by-year breakdown (crisis years 2021-2022 should show higher offer rates)
   - Comparison: what if we offered to everyone? What if we never offered?

3. Possible extension: adjust RETENTION_THRESHOLD dynamically based on observed ROI
   - This would be the company "learning" from its own retention history

## Deliverables

1. `saas/reporting/annual_report.py`: expand `_section_retention_strategy()` with ROI calculation
   - Per-renewal: cost, benefit (margin saved vs churn loss), net
   - Aggregate: total offers, success rate, net P&L, ROI%
2. `simulation/run_phase2b.py`: pass term margin data into retention_log entries so annual report can compute benefit
3. Annual report "Retention Strategy P&L" section: actual table with ROI figures

## What this unlocks

- Company can assess whether its retention strategy is net-positive
- Basis risk in churn estimation has a quantified P&L consequence (not just tracking)
- Foundation for dynamic threshold tuning (Phase 12d)

## Commit message

"Phase 12c: retention ROI — measure whether company retention strategy is net-positive"
