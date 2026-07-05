## Phase QQ COMPLETE -- Decision Loop Remaining Scope (Calibration Fix + Counterfactual Lift)
Last updated: 2026-07-05T13:15:17Z

**Status:** COMPLETE. 15,622 tests passed (fast suite). Epistemic: PASS.

**Phase QQ (PRIORITIES.md P1, closes DECISION_LOOP_AND_EVENT_LEDGER.md):**
- company/crm/churn_model.py: hard 0.95 clamp replaced with an asymptotic saturating curve above
  CHURN_SATURATION_ELBOW=0.90 (identity below it -- every previously-unclamped estimate unchanged);
  distinguishable elevated risk levels no longer collapse to the same false-precision ceiling
- company/analytics/counterfactual_retention.py: compute_counterfactual_lift_by_class() classifies
  every no-offer churn as detection_gate (model problem) or uneconomical_{high,medium,low}
  (economics problem), scored under H3 (effectiveness scales 0.04/discount point); wired into the
  Counterfactual Retention & Threshold Optimisation board section

**PRIORITIES.md P1 (Decision Event Ledger) now fully DONE across Phases QP+QQ.** New P1: PROCESS_NOT_EVENTS.md
acquisition funnel (second in its declared sequence, pre-approved via PREAPPROVE_PROCESS_MODEL.md).

**Prior milestone:** Phase QP (Decision Event Ledger unification) -- docs/claude/phase-history.md.


**Latest simulation results (2016–2025)** — auto-processed (517s / 9 min):
- Net margin: £1,445,257.67 | Gross: £6,467,308.57 | Capital: £51,433
- Treasury: £2,466,636 → £3,911,894 | 38 committee interventions | 1605 bills issued
- Enterprise value: £8,826,938.57 | Net after CTS: £6,360,822
- Retention: 14 offers, 14/14 retained | 6 no-offer churns | 6 total churned accounts