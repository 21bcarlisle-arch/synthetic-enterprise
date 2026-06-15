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
| 11 | ~~Per-segment (resi electricity / SME electricity / resi gas) aggregated margin trend across years~~ — **Closed 2026-06-15**: `extract_report_data()` now computes `segment_split` per year and `generate_annual_report()` adds a "Segment Margin Trend" table (whole-run, before the per-year sections). | Low | Low | none |
| 12 | Dedicated administration/insolvency incident section, auto-populated if `administration_event` is non-null (currently null for this run, but the report generator should handle it gracefully if a future run trips the threshold). | Low | Low | none |
| 13 | ~~Report-data cache versioning~~ — `save_run_output_json()` already stamps `run_output_latest.json` with `_cache_meta.git_commit`/`generated_at_utc`. **Closed the loop 2026-06-15**: `annual_report.py` now also warns at load time if HEAD has moved since the cache was generated. | Low | Low | 1 |
| 14 | `make report` as a scheduled/automated step (e.g. after each full simulation run completes) so `ANNUAL_REPORT.md` stays current without a manual trigger. | Low | Low | 1 |
| 15 | NTFY digest of the executive summary whenever the annual report is regenerated, so Rich gets the headline figures without opening the file. | Low | Low | 1, 14 |
| 16 | Forward curve realism (`sim/forward_curve.py`): add a tenor-dependent term premium (longer `contract_length_months` carry a higher `risk_factor`, as real forward curves price more uncertainty into far-dated tenors) and a crisis-liquidity premium (extra multiplier when the lookback window's volatility is itself elevated vs. its own trailing distribution — modelling the spread-widening real markets show when everyone wants protection at once). Proposed in response to `docs/staging/Openquestions.md` #2 — **propose-before-build**, see note below. | Medium | Medium-High | none |
| 17 | Cost-to-serve depth (`saas/cost_to_serve.py`): itemise the flat annual overhead into billing/IT, smart-meter operation, and regulatory levy components; add a one-off acquisition cost amortised over expected tenure (from `saas/churn_model.py`); add a variable contact-centre cost driven by `contact_model`'s per-period `contact_probability`; add a debt-collection cost on top of the existing bad-debt provision when an account is overdue (`payment_behaviour`). Proposed in response to `docs/staging/Openquestions.md` #3 — **propose-before-build**, see note below. | Medium | Medium | 2 (contact_model/payment_behaviour already integrated) |

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

## Note on items 16 and 17 (Open Questions #2 and #3)

Both raised in `docs/staging/Openquestions.md` by Rich's strategy advisor.
Investigated; both are credible concerns and the proposed approaches above
are sized to use data/modules that already exist in the codebase
(`churn_model`, `contact_model`, `payment_behaviour`, the existing
sigma/risk_factor machinery in `forward_curve.py`). Neither has been built —
flagged as propose-before-build per the Open Questions instructions, because:

- **#16 (forward curve)** changes the price environment the Phase 5c mandate
  redesign was tuned against. If it materially shifts the
  cost/benefit of hedging across 2016-2025, that's itself a finding (related
  to the "regime-change blindness" risk already called out in CLAUDE.md), not
  just a reporting tweak — worth a full re-run and review before committing
  to specific premium values.
- **#17 (cost-to-serve)** would lower net margin across the whole portfolio
  (possibly materially, given the current model is "a skeleton" per the
  question). The specific £ assumptions for acquisition cost, per-contact
  cost, and debt-collection cost need a sanity check against real supplier
  cost structures before they go into the headline net-margin figures Rich
  reports on.

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
