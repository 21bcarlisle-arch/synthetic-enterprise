# Simulation Status -- LATEST

Last updated: 2026-06-30T02:37:32Z

## Current state

- **Phase:** AM complete (Pricing Basis Risk) -- phases P through AM shipped
- **Tests passing:** 5,318 (all green)
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

## Session summary (AH--AM): 6 phases, 84 tests

- **Phase AM:** Pricing Basis Risk (12 tests). year-by-year tariff error; 2023/2025 HIGH OVER-PRICE.
- **Phase AL:** Counterfactual Retention (12 tests). CF value of 4 missed no-offer churns: £3,621.
- **Phase AK:** Churn Root Cause Attribution (14 tests). rate shock + blind misses per departure.
- **Phase AJ:** CRM Risk Triage (14 tests). CRITICAL/HIGH/MEDIUM/LOW bands + company blind spots.
- **Phase AI:** EAC Drift Snapshot (10 tests). per-customer demand drift from billing history.
- **Phase AH:** Board Intelligence Pack (12 tests). retention/flex/churn board synthesis.

-> Full build history: docs/PROJECT_OVERVIEW.md Section 4
