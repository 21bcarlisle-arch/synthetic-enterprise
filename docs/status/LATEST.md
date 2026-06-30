# Simulation Status -- LATEST

Last updated: 2026-06-30T02:41:40Z

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

**Latest simulation results (2016–2025)** — auto-processed (763s / 13 min):
- Net margin: £6,239,245.03 | Gross: £6,475,913.39 | Capital: £236,668
- Treasury: £2,466,636 → £3,709,973 | 38 committee interventions | 1531 bills issued
- Enterprise value: £6,037,509.08 | Net after CTS: £6,370,846
- Retention: 18 offers, 17/18 retained | 5 no-offer churns | 6 total churned accounts
