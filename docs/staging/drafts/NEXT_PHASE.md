# NEXT PHASE PROPOSAL: Phase NQ — Churn Model Recalibration via Rate Context

## Problem

Phase NO revealed: 0% recall, all 6 churns missed, F1=0. Root cause diagnosis:
- C3, C4, C5 (estimates 0%): base-rate churn at stable prices — epistemic limit, unpredictable
- C1 (Dec 2021, 3.8%), C2 (Mar 2022, 6.7%): crisis-period churns with YoY comparison neutralised
- C6 (Mar 2024, 24.7%): near-threshold, missed by 5 pts

The crisis-period misses (C1, C2) are fixable: the YoY comparison fails during a sustained crisis
because the reference year (Dec 2020, Mar 2021) was also elevated. The company would observe
this: its own rate vs the average of the previous 24 months (a wider reference window).

The base-rate misses (C3, C4, C5) are epistemic: the company cannot predict lifestyle churns.
However, a real company would ensure minimum 5% floor on all estimates (the Ofgem-published
resi industry base rate).

## What this phase builds

### Part A: Industry base rate floor
company/crm/enriched_churn_estimate.py: add INDUSTRY_BASE_CHURN_RATE = 0.05; ensure
enriched_churn_estimate always returns >= INDUSTRY_BASE_CHURN_RATE. This is defensible
from Ofgem published annual switching statistics.

### Part B: Extended rate reference window
saas/churn_model.py: add extended_reference_mode that compares current bill against the
24-month (rather than 12-month) rolling average. Crisis-year 2021: 12-month ref is already
elevated; 24-month ref reaches back to pre-crisis 2019-2020, showing the full crisis shock.
Controlled by a flag: comparison_mode='yoy_extended'.

### Part C: Wire extended reference in run_phase2b
simulation/run_phase2b.py: pass comparison_mode='yoy_extended' to _enriched_churn_estimate.

### Part D: Tests and report update
~12 tests. Update threshold sensitivity to show F1 improvement with new calibration.

## Why this has real fidelity value
- Real UK suppliers use wider reference windows during crises (Ofgem ECP analysis)
- The INDUSTRY_BASE_CHURN_RATE floor reflects what Ofgem publishes as passive switching baseline
- Recall improvement from 0% to something positive closes the epistemic gap meaningfully
- Without recall improvement, the board section just shows a permanently broken model

## Test targets (~12 tests)
- Base rate floor: estimate never < 0.05 regardless of signals
- Extended window catches crisis: 24-month ref for Dec 2021 shows shock, 12-month doesn't
- Threshold sensitivity shows F1 improvement (optimal F1 > 0.18 current)
- No epistemic violations (company reads its own billing history, not SIM internals)
