# Phase 3a Summary — Experience Observability Depth

## What Was Built
- `saas/customer_reaction.py` — new `score_experience_signals()`, three per-customer per-billing-period signals (a "billing period" = one calendar month):
  - `bill_shock_score` = abs(actual_bill - rolling_6_month_avg) / rolling_6_month_avg, triggers above 0.15. Rolling average uses only strictly-prior billing periods (point-in-time safe); `None`/not-triggered until at least one prior period exists.
  - `cumulative_exposure_gbp` — running sum of (actual_cost − actual_bill) across a customer's tenure to date.
  - `expectation_gap_gbp` = actual_bill − (previous_bill × 1.02); `None` for a customer's first billing period.
- `simulation/run_phase3a.py` — runs the Phase 2b dual-fuel simulation, scores all ten customer/commodity legs, and reports bill-shock event counts for 2016 and 2021-2022, broken down by customer, region, and home type.
- `tests/saas/test_customer_reaction.py` — 8 tests covering first-period edge cases, threshold triggering (above/below 0.15), the rolling-window boundary, expectation-gap arithmetic, cumulative exposure accumulation, multi-record-per-month aggregation, and per-customer independence.

## Key Findings
- **2016 (build year) bill shocks are concentrated in London**: C1 (urban_flat, London, electricity) had 6 — by far the most of any leg — and C5 (small_office, London, electricity) had 4. Every gas leg (C1g-C4g) had **zero** 2016 shocks, because gas billing only starts mid-2016 with too little history for the rolling average to swing much, and NBP prices were comparatively flat that year.
- **2021-2022 (crisis years) shocks are an order of magnitude higher across the board** — every leg has 7-20 shocks vs 0-6 in 2016, confirming the crisis was felt as repeated bill shocks, not a single jump.
- **By region**: Manchester (C2 + C6) has the most 2021-22 shocks (39), followed by London and Glasgow (31 each), Cotswolds least (26). 2016 shows the opposite pattern — London dominates (10) while Manchester, Glasgow, Cotswolds are all ≤4.
- **By home type**: tenement_flat (C3/C3g, Glasgow) has the most 2021-22 shocks (31) despite being one of the smaller-consumption profiles — smaller absolute bills make the same £ swing a larger relative shock. small_office (C5, SME) has the fewest 2021-22 shocks (11) — larger absolute bills dampen the relative bill-shock score even though the underlying £ swings are bigger.
- **Profile does differ, but mostly by consumption scale, not location per se**: the home types with the smallest annual consumption (urban_flat, tenement_flat) show the highest relative bill-shock counts during the crisis, because `bill_shock_score` is a *relative* (percentage) measure — small absolute bills amplify percentage swings. Gas legs consistently show fewer crisis shocks than their paired electricity legs (e.g. C1=13 vs C1g=7), consistent with Phase 2b's finding that NBP volatility is lower than SSP's.

## Key Decisions Made
- **Billing period = calendar month**: matches the `monthly_cost_of_capital_gbp` allocation already used throughout `simulation/hedged_settlement.py` and `simulation/gas_settlement.py`, and is the natural unit for "a bill" in UK domestic energy retail.
- **Rolling average window = 6 prior periods, point-in-time safe**: only ever looks backward, consistent with Law 2 (Point-in-Time Blindfold) — a customer's bill-shock perception in month N can only be informed by months 1..N-1.
- **Each customer_id (including gas legs C1g-C4g) scored independently**: dual-fuel customers receive two separate "bills" in this model (one per commodity) rather than a combined bill — flagged below as an open question for whether that matches real billing.
- **`score_dissatisfaction()` left unchanged**: it remains the Phase 0c counter-based seed signal; `score_experience_signals()` is additive, not a replacement.

## Open Questions
- Should dual-fuel customers (C1/C1g etc.) be billed as one combined monthly statement rather than two independent ones? Real UK suppliers typically issue a single dual-fuel bill — this would change `bill_shock_score` and `expectation_gap_gbp` for C1-C4 (their gas and electricity bill shocks could partially offset or compound depending on correlation).
- `cumulative_exposure_gbp` is reported per leg but never surfaced in any portfolio-level report yet — worth wiring into a future treasury/CLV view to show which customers are persistently under- vs over-recovered.
- Real bill-shock perception research suggests thresholds vary by household income/vulnerability — the flat 0.15 threshold is a uniform seed value, not segmented.

## Token Efficiency
- Frontier: `score_experience_signals()`, `run_phase3a.py`, and the test suite — all hand-written (small, schema-adjacent additions to an existing pure module, per the Phase 1d delegation lesson).
- Local: none this session.
- Output: one new pure function (~70 lines), one new orchestration script (~85 lines), 8 new tests, full Phase 2b re-run (8s) used to generate report data.
