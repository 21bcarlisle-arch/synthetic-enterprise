# Simulation Status — LATEST

Last updated: 2026-06-30T02:13:11Z

## Current state

- **Phase:** AI complete (EAC Drift Snapshot) -- all phases P→AI shipped
- **Tests passing:** 5,266 (all green)
- **Python modules:** 330+
- **Company modules:** 232+
- **Net position (latest sim run):** £1,243,337

## Latest run figures (git 5e2a5dc, 2026-06-30)

| Metric | Value |
|--------|-------|
| Total Revenue | £14,137,721 |
| Gross Margin | £6,462,146 |
| Net Margin | £1,243,337 |
| Enterprise Value | £6,142,209 |
| Administration Event | None |

## Recent build phases (AH→AI)

- **Phase AI:** EAC Drift Snapshot (10 tests). _section_eac_drift_snapshot() in annual_report.py:
  per-customer demand drift (first renewal → latest renewal) from billing-derived EAC estimates.
  Classifies significant/moderate/stable; infers likely cause (EV/ASHP/solar/efficiency).
  Shows notable-drift table + portfolio trend. Uses demand_estimation_log (Phases 23a/25a).
- **Phase AH:** Board Intelligence Pack (12 tests). _section_portfolio_intelligence_pack():
  retention coverage, flex enrollment CAGR, churn peak year, board recommendations.
- **Phase AG:** Flexibility Revenue Annual Report Section (12 tests). CM vs DFS table, pre-DFS years
  labelled, enrolled customer-years, DFS launch note.

→ Full build history: docs/PROJECT_OVERVIEW.md Section 4
