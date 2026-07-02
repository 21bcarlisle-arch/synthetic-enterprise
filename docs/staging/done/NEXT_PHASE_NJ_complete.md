# Phase NJ -- Churn Model Calibration Report

## Gap

The company has a three-signal churn model (Phases MX-NH) but no way to measure
how well it performs. The board knows "4/6 departures not forecast" anecdotally —
there is no code that computes this. After Phase NH improved the model, we cannot
quantify the improvement without a formal accuracy report.

A real UK energy supplier treats churn model recall/precision as a board KPI.
Currently we have the raw data (customer_events, retention_log, no_offer_churn_log)
but no post-hoc analysis.

## What to build

company/analytics/churn_accuracy_report.py (new file)

```python
def compute_churn_model_performance(
    customer_events: list[dict],
    retention_log: list[dict],
    no_offer_churn_log: list[dict],
    threshold: float = 0.30,
) -> dict:
    """
    Returns:
        total_churn_events, true_positives, false_positives,
        false_negatives, true_negatives,
        recall, precision, f1_score,
        per_year: {year: {tp, fp, fn, tn, recall, precision}}
    """
```

Logic:
- True Positive (TP): company estimate > threshold AND customer actually churned
  Source: customer_events where event_type=="churned" and company_churn_estimate > threshold
  (these are in retention_log with outcome=="churned_despite_offer")
- False Positive (FP): company estimate > threshold AND customer renewed
  Source: retention_log with outcome=="retained"
- False Negative (FN): company estimate <= threshold AND customer churned
  Source: no_offer_churn_log (all are FN by definition — no offer made means estimate was below threshold)
  Also: customer_events with event_type=="churned" and company_churn_estimate <= threshold
- True Negative (TN): company estimate <= threshold AND customer renewed
  Source: customer_events with event_type=="renewed" and company_churn_estimate <= threshold

Wire into run_phase2b.py at results assembly (end of main()), add
churn_model_performance to output JSON.

## Test plan (16 tests in tests/company/test_churn_accuracy_report.py)

1.  all_tp: all predicted churns actually churn -> recall=1.0, precision=1.0
2.  all_fn: no churns predicted, all churn -> recall=0.0, precision=undefined(0.0)
3.  all_fp: all predicted churn, none churn -> recall=undefined(0.0), precision=0.0
4.  mixed: 2 TP, 1 FP, 1 FN, 3 TN -> recall=2/3, precision=2/3
5.  threshold_boundary: co=0.30 exactly treated as not above threshold (< not <=)
6.  f1_score: matches 2*p*r/(p+r) formula
7.  per_year: two events in 2019, one in 2020 -> separate per-year entries
8.  empty_events: all zeros, recall/precision/f1 = 0.0
9.  no_offer_churns_are_fn: no_offer_churn_log entries count as FN
10. retained_despite_offer_are_tp: retention_log outcome=="retained" are NOT TP
    (they stayed — only "churned_despite_offer" are TP)
11. churned_despite_offer_are_tp: retention_log outcome=="churned_despite_offer" are TP
12. above_threshold_renewed_are_fp: company over-estimated churn for renewals
13. total_churn_events: TP + FN matches total actual churns
14. recall_formula: TP / (TP + FN)
15. precision_formula: TP / (TP + FP), 0.0 if no predictions
16. f1_zero_if_no_predictions: F1 = 0 when precision=0 and recall=0

## Expected simulation impact

At run end, run_output_latest.json will include:
  "churn_model_performance": {
    "total_churn_events": 7,
    "true_positives": 1,   (the one churned_despite_offer from retention_log)
    "false_positives": 25, (25 retained customers who got an offer they didn't need)
    "false_negatives": 6,  (6 no-offer churns — completely missed)
    "true_negatives": N,
    "recall": 0.14,        (1/7 = 14% recall — the model is catching very few churns)
    "precision": 0.038,    (1/26 = 3.8% precision — almost all offers are wasted)
    "f1_score": 0.065,
    "per_year": {...}
  }

These metrics will reveal the baseline and how much Phase NH moves the needle
on future simulation runs.

## Epistemic check

PASS. Company is analysing its OWN records (company estimates, its own offers,
observed churn outcomes). No SIM internals involved. This is internal model
evaluation — exactly what a real supplier's analytics team would do.

## Fidelity delta

The company can now measure its own churn model quality. Board report gains
a "model calibration" section. Quantifies the cost of missed churns (FN) vs
wasted retention spend (FP). Sets baseline before any threshold-tuning work.
