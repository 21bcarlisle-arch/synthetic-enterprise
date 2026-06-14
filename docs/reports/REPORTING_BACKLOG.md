# Reporting Backlog

Prioritised follow-on items identified while building the Phase 5a annual
report generator (`saas/reporting/annual_report.py`). Items are ordered
roughly by value-to-effort ratio, not strictly by value.

| # | Item | Value | Effort | Depends on |
|---|------|-------|--------|------------|
| 1 | Persist structured Phase 2b/4c run output (`extract_report_data()`'s dict) to JSON at the end of every full simulation run, so `annual_report.py` never needs to re-run the 9.5-year simulation to regenerate. **Currently this is the active blocker for ANNUAL_REPORT.md** — see note below. | High | Low | none |
| 2 | Integrate Phase 4b outputs (CLV, churn risk score, enterprise value, cost-to-serve, home-move win rate from `simulation/run_phase4b_on_phase2b.py`) into the same combined run output / JSON, so the annual report's Customer Book and Pricing & Margin sections can drop their "Not available" placeholders. | High | Medium | 1 |
| 3 | Persist per-wake-up VaR ratio (current vs stressed floor) — `run_phase2b.py` computes `portfolio_var_current`/`portfolio_var_stressed` at each risk-committee check but doesn't return them. Small addition to `committee_wake_ups` entries. | Medium | Low | 1 |
| 4 | Build a chronological portfolio treasury time series (sorted by settlement date/period across all customers) with drawdown-event detection (>10% peak-to-trough), for the Portfolio Health section. | Medium | Medium | 1, 3 |
| 5 | Wire `saas/cost_to_serve.py` into the per-customer net margin calculation so "net margin per customer after cost to serve" and "average/range cost to serve" can be reported. | High | Medium | 2 |
| 6 | Define and implement an "activity-based pricing" flag/policy for net-negative customers (the report can already detect net-negative customers from existing data, but no business-logic flag or remediation policy exists yet). | Medium | Medium | 5, design decision |
| 7 | Define a churn-risk threshold (currently undefined anywhere in the codebase) and surface "# customers above threshold" per year using `saas/churn_model.py`. | Medium | Medium | 2, design decision |
| 8 | Per-year CLV snapshots per customer (currently `saas/clv_model.py` produces point-in-time/lifetime figures only, not a per-year time series). | Medium | Medium | 2 |
| 9 | Design and implement regulatory threshold tracking (no Ofgem-style thresholds — billing accuracy, complaint handling SLAs, etc. — are modelled anywhere yet). This is a net-new business-logic design, not just a reporting gap. | Medium | High | design decision |
| 10 | Hedge-effectiveness analysis section using the newly-exposed `hedge_evolution` (`actual_net` vs `naked_net` per term) — how much did hedging decisions add or cost relative to staying unhedged. | Medium | Medium | none (data exists) |
| 11 | Per-segment (resi electricity / SME electricity / dual-fuel gas) aggregated margin trend across years, for portfolio-strategy review at a coarser grain than per-customer. | Low | Low | none |
| 12 | Dedicated administration/insolvency incident section, auto-populated if `administration_event` is non-null (currently null for this run, but the report generator should handle it gracefully if a future run trips the threshold). | Low | Low | none |
| 13 | Report-data cache versioning — stamp the persisted JSON with the run's git commit hash and timestamp, so a stale cache can't silently be reused after code changes that would alter the figures. | Low | Low | 1 |
| 14 | `make report` as a scheduled/automated step (e.g. after each full simulation run completes) so `ANNUAL_REPORT.md` stays current without a manual trigger. | Low | Low | 1 |
| 15 | NTFY digest of the executive summary whenever the annual report is regenerated, so Rich gets the headline figures without opening the file. | Low | Low | 1, 14 |

## Note on item 1 and ANNUAL_REPORT.md

No structured Phase 2b/4c run output is currently persisted anywhere in the
repo — `run_phase4c_on_phase2b.main()` returns an in-memory dict and prints
summary stats, but nothing is written to disk. `saas/reporting/annual_report.py`
is built and tested against hand-written fixtures (`tests/saas/reporting/`)
and is ready to run, but **ANNUAL_REPORT.md cannot be generated from real data
until a full simulation run's output is captured**.

A weather-effects re-run (`python3 -m simulation.run_phase4c_on_phase2b`,
the same run already in flight for Phase 4c) will be used as the one-time
bootstrap: once it completes, `annual_report.py`'s `--save-json` path will
persist its output, and from then on the report is regenerable without
re-running. This is the only run involved — no additional simulation
execution is being started for Phase 5a specifically.

## What Rich needs to decide

- **Item 2 priority**: should the next phase focus on integrating Phase 4b
  outputs (CLV, churn, enterprise value, cost-to-serve, home-move win rate)
  into the report's data source, so the "Not available" placeholders in
  ANNUAL_REPORT.md can be filled in? This is the single highest-value item
  but touches five existing modules plus the run pipeline.
- **Item 7's churn-risk threshold**: no such threshold exists in the codebase
  today. What level of churn-risk score should count as "at risk" for the
  Customer Book section?
- **Item 9 (regulatory thresholds)**: is modelling Ofgem-style regulatory
  thresholds (billing accuracy, complaint handling SLAs, etc.) in scope for
  the next phase, or should the report continue to mark this section "Not
  available" indefinitely?
- **Item 1's bootstrap run**: confirm it's acceptable for the in-flight
  weather-effects re-run's completion to double as the bootstrap for the
  report-data JSON cache (no extra simulation runs needed beyond that).
