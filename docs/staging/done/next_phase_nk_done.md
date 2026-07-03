# Phase NK — Churn Model Performance Report

## Problem

Phase NJ (2026-07-02) added compute_churn_model_performance() and wired it into run_phase2b.main()
at line 1809. But extract_report_data() in saas/reporting/annual_report.py does NOT include
"churn_model_performance" in its return dict (lines 558-596). The board KPI — recall/precision/F1 —
is computed every run and silently discarded. The JSON output contains no "churn_model_performance"
key. Phase NJ's board-level model calibration section is completely invisible.

Root cause: omission in extract_report_data return dict (single missing line).

Secondary issue: no annual report section exists to DISPLAY churn model performance, even after
the extraction is fixed. The data would be in the JSON but the report would show nothing.

## Changes

### 1. saas/reporting/annual_report.py — extract_report_data (line ~588)
Add after "demand_estimation_log" line:
    "churn_model_performance": phase2b.get("churn_model_performance", {}),

### 2. saas/reporting/annual_report.py — _section_churn_model_performance(data)
New report section (placed after "Churn Prediction Calibration" section, ~line 1362).
Shows:
- Total churn events, TP, FP, FN, TN
- Recall = TP/(TP+FN): "% of churners detected before departure"
- Precision = TP/(TP+FP): "% of retention offers went to genuine churners"
- F1 score: harmonic mean
- Per-year table: Year | Renewals | TP | FP | FN | TN | Recall | Precision
- Interpretation bullet:
    - recall=0: "Model detected 0% of churners — all departures were surprises"
    - recall=1: "Model detected all churners — full visibility"
    - f1>0.5: "Model is reasonably calibrated"
    - f1<0.2: "Model calibration needs attention (Board Action Required: RED)"
- Notes RAG: recall >= 0.5 = GREEN, 0.3-0.5 = AMBER, < 0.3 = RED
- Wired in generate_annual_report() return list after _section_churn_prediction_calibration()

## Tests (~14 new) — test_phase_nk_churn_model_performance.py
- extract_has_churn_model_performance_key: extract_report_data result dict has "churn_model_performance"
- perf_key_is_dict: churn_model_performance value is a dict
- perf_has_recall: dict has "recall" key
- perf_has_precision: dict has "precision" key
- perf_has_f1_score: dict has "f1_score" key
- perf_has_total_churn_events: dict has "total_churn_events" key
- perf_all_fn_zero_recall: all churns not predicted -> recall=0.0
- perf_all_tp_perfect_recall: all churns predicted -> recall=1.0
- perf_no_fp_precision_one: TP>0 no FP -> precision=1.0
- perf_f1_harmonic_mean: f1 = 2*P*R/(P+R) when both nonzero
- perf_per_year_has_recall: per_year[year] has "recall" key
- section_renders_with_data: _section_churn_model_performance renders markdown when data present
- section_silent_no_data: section returns empty string when churn_model_performance is {}
- section_shows_recall_precision: rendered markdown contains "Recall" and "Precision"

## Expected impact
- Board finally sees recall/precision/F1 on every run (Phase NJ's intent, 2 months late)
- Current expected values: recall=0.33 (2/6 churns predicted), precision=1.0, f1=0.50
  (C5 at 85% and C6 at 26% were above 30% threshold; C2/C3/C1/C4 were blind misses)
- Board can track model quality improving or degrading run-to-run
- RED flag when f1 < 0.2 (churn model is failing to detect departures)

## Known limitation (document in report section)
The SIM's churn_probability for resi/SME customers (29-38%) is driven by SEASONAL bill
variation — all resi customers have 8-11 monthly bill shocks per year from winter/summer
bill cycles. This makes the passive blind miss rate (4/5 no-offer churns) a structural feature:
passive customers churn at ~10% effective rate (after passive_churn_cap) but the 30%
RETENTION_THRESHOLD is calibrated for active renewers. A separate passive loyalty program
would be needed to address this gap (future phase).
